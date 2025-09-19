import secrets, hashlib
from database import connect

def _h(raw): return hashlib.sha256(raw.encode()).hexdigest()

def mint_api_token(user_id:int) -> str:
    raw = secrets.token_urlsafe(48)
    conn=connect(); cur=conn.cursor()
    cur.execute("INSERT INTO api_tokens (user_id, token_hash) VALUES (?,?)", (user_id, _h(raw)))
    conn.commit(); conn.close()
    return raw

def get_user_by_bearer(raw:str):
    conn=connect(); cur=conn.cursor()
    cur.execute("SELECT user_id FROM api_tokens WHERE token_hash=? AND is_active=1", (_h(raw),))
    row=cur.fetchone()
    if row:
        cur.execute("UPDATE api_tokens SET last_used_at=CURRENT_TIMESTAMP WHERE token_hash=?", (_h(raw),))
        conn.commit()
    conn.close()
    return row["user_id"] if row else None
