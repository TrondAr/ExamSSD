def test_register_and_login_success(client):
   
    client.post("/register", data={
        "email": "drJekyll@example.com",
        "password": "smekkL0bb!123"
    })
    
    r = client.post("/login", data={
        "email": "drJekyll@example.com",
        "password": "smekkL0bb!123"
    }, follow_redirects=True)
    
    assert b"Logged in as" in r.data or b"Dashboard" in r.data
