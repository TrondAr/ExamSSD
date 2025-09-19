import io
from database import connect

def _latest_file_id():
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT id FROM files ORDER BY id DESC LIMIT 1")
    row = cur.fetchone(); conn.close()
    return row["id"]

def test_patient_cannot_access_other_patients_file(client):
    # creating 2 patients
    client.post("/register", data={"email":"drJekyll@test.no","password":"smekkL0bb!123"})  # patient 1
    client.post("/register", data={"email":"mrHyde@test.no","password":"smekkL0bb!123"})    # patient 2

    # patient 1 logs in and uploads a file
    client.post("/login", data={"email":"drJekyll@test.no","password":"smekkL0bb!123"})
    client.post("/files/upload", data={
        "file": (io.BytesIO(b"secret data"), "p1.txt")
    }, content_type="multipart/form-data", follow_redirects=True)
    file_id = _latest_file_id()
    client.get("/logout")

    # patient 2 logs in and tries to download patient 1's file
    client.post("/login", data={"email":"mrHyde@test.no","password":"smekkL0bb!123"})
    r = client.get(f"/files/download/{file_id}")
    assert r.status_code == 403
