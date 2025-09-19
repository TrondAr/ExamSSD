def test_login_sql_injection_attempt_fails(client):    
    client.post("/register", data={
        "email": "frankenstein@example.com",
        "password": "smekkL0bb!123"
    })
    
    payload = "' OR '1'='1"
    r = client.post("/login", data={"email": payload, "password": payload})
    
    assert b"Invalid email or password" in r.data
    assert r.status_code == 200
