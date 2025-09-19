import uuid, hashlib
from pathlib import Path
from flask import Blueprint, request, render_template, redirect, url_for, session, abort, send_file, current_app
from utils.decorators import requires_role

from database import connect, get_user_by_id

files_bp = Blueprint("files", __name__, url_prefix="/files")

def _user_can_access_file(row, viewer_id, viewer_role) -> bool:
    owner_id = row["owner_user_id"]
    if viewer_role == "admin":
        return True
    if viewer_role == "patient":
        return owner_id == viewer_id
    if viewer_role == "practitioner":
        # Practitioner may access only linked patients' files
        conn = connect(); cur = conn.cursor()
        cur.execute("SELECT 1 FROM gp_patient WHERE gp_user_id=? AND patient_user_id=?", (viewer_id, owner_id))
        ok = cur.fetchone() is not None
        conn.close()
        return ok
    return False

def _allowed_extension(name: str) -> bool:
    allowed = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}
    return Path(name).suffix.lower() in allowed

@files_bp.route("/upload", methods=["GET", "POST"])
@requires_role("patient", "practitioner", "admin")
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        owner_user_id = request.form.get("owner_user_id")  # allow GP upload on behalf of patient
        viewer_id = session["user_id"]
        viewer_role = session["role"]

        if not file or file.filename == "":
            return render_template("upload.html", error="No file selected")

        if viewer_role == "patient":
            # Patient can only upload to self
            owner_user_id = viewer_id
        else:
            # Practitioner/Admin must provide an explicit owner_user_id
            try:
                owner_user_id = int(owner_user_id or 0)
            except:
                return render_template("upload.html", error="owner_user_id required")

        if not _allowed_extension(file.filename):
            return render_template("upload.html", error="File type not allowed")

        #Validate practitioner is actually linked to the patient they’re uploading for
        if viewer_role == "practitioner":
            # Ensure the target patient exists
            if not get_user_by_id(owner_user_id):                        
                return render_template("upload.html", error="Unknown patient")  
            # Ensure linkage exists in gp_patient
            conn = connect(); cur = conn.cursor()                          
            cur.execute(                                                   
                "SELECT 1 FROM gp_patient WHERE gp_user_id=? AND patient_user_id=?", 
                (viewer_id, owner_user_id)
            )
            linked = cur.fetchone() is not None                            
            conn.close()                                                  
            if not linked:                                                 
                return render_template("upload.html", error="You are not linked to this patient") 

        storage_name = str(uuid.uuid4())
        dest = Path(current_app.config["UPLOAD_DIR"]) / storage_name

        h = hashlib.sha256()
        size = 0
        with dest.open("wb") as f:
            chunk = file.stream.read(8192)
            while chunk:
                h.update(chunk)
                size += len(chunk)
                f.write(chunk)
                chunk = file.stream.read(8192)

        if size == 0:
            dest.unlink(missing_ok=True)
            return render_template("upload.html", error="Empty file")

        conn = connect(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO files (owner_user_id, uploaded_by_user_id, original_filename, storage_name, mime_type, size_bytes, sha256_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (owner_user_id, viewer_id, file.filename, storage_name, file.mimetype, size, h.hexdigest()))
        conn.commit(); conn.close()

        return redirect(url_for("files.list_my_files"))

    return render_template("upload.html")


@files_bp.route("/files_list")
@requires_role("patient", "practitioner", "admin")
def list_my_files():
    user_id = session["user_id"]
    role = session["role"]
    conn = connect(); cur = conn.cursor()
    if role == "patient":
        cur.execute("""SELECT * FROM files WHERE owner_user_id=? ORDER BY created_at DESC""", (user_id,))
    elif role == "practitioner":        
        cur.execute("""
            SELECT f.* FROM files f
            JOIN gp_patient gp ON gp.patient_user_id = f.owner_user_id
            WHERE gp.gp_user_id=? ORDER BY f.created_at DESC
        """, (user_id,))
    else:  # admin
        cur.execute("""SELECT * FROM files ORDER BY created_at DESC""")
    rows = cur.fetchall(); conn.close()
    return render_template("files_list.html", files=rows)


@files_bp.route("/download/<int:file_id>")
@requires_role("patient", "practitioner", "admin")
def download(file_id: int):
    viewer_id = session["user_id"]
    role = session["role"]

    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM files WHERE id=?", (file_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        abort(404)

    if not _user_can_access_file(row, viewer_id, role):
        abort(403)

    # Always force download; don't render inline (prevents XSS with HTML files)
    storage_path = Path(current_app.config["UPLOAD_DIR"]) / row["storage_name"]
    if not storage_path.exists():
        abort(404)

    return send_file(
        storage_path,
        as_attachment=True,
        download_name=row["original_filename"],
        mimetype=row["mime_type"],
        max_age=0
    )
