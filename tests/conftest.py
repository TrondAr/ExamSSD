import pytest
from app import app, init_db
import database
from pathlib import Path
from security import hash_password
from database import create_user, get_user_by_email, connect

@pytest.fixture(scope="function")
def client(tmp_path):
    
    db_path = Path(database.DATABASE)
    if db_path.exists():
        db_path.unlink()
    init_db()

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["UPLOAD_DIR"] = str(tmp_path / "uploads")
    (tmp_path / "uploads").mkdir(parents=True, exist_ok=True)

    with app.test_client() as c:
       
        def create_patient(email="p@example.com", password="StrongPass!123"):
           
            return c.post("/register", data={"email": email, "password": password})

        def create_practitioner_direct(email="gp@example.com", password="StrongPass!123"):
            
            pw_hash = hash_password(password)
            create_user(email, pw_hash, role="practitioner")
            return get_user_by_email(email)

        def create_admin_direct(email="admin@example.com", password="AdminPass!123"):
            pw_hash = hash_password(password)
            create_user(email, pw_hash, role="admin")
            return get_user_by_email(email)

        def link_gp_patient(gp_id, patient_id):
            conn = connect(); cur = conn.cursor()
            cur.execute("INSERT INTO gp_patient (gp_user_id, patient_user_id) VALUES (?,?)", (gp_id, patient_id))
            conn.commit(); conn.close()
        
        c.create_patient = create_patient
        c.create_practitioner_direct = create_practitioner_direct
        c.create_admin_direct = create_admin_direct
        c.link_gp_patient = link_gp_patient

        yield c
