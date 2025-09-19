def test_xss_input_is_escaped(client):
    payload = "<script>alert(1)</script>"    
    r = client.get(f"/xss/echo?q={payload}")
    body = r.data.decode()
   
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
    assert "<script>" not in body
