import secrets, hashlib, datetime
from database import connect, get_user_by_email
from security import hash_password

TOKEN_BYTES = 48               # number of random bytes for token
EXP_MINUTES = 15               # token expiry time in minutes

def _now_utc():
    return datetime.datetime.utcnow()

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def create_reset_for_email(email: str) -> str | None:
    """Create a reset token for existing email. Returns the *raw* token (show once when requested) or None if user not found."""
    user = get_user_by_email(email)
    if not user:
        return None  
    raw = secrets.token_urlsafe(TOKEN_BYTES)
    token_hash = _sha256(raw)
    expires_at = (_now_utc() + datetime.timedelta(minutes=EXP_MINUTES)).isoformat(" ")
    conn = connect(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO password_resets (user_id, token_hash, expires_at) VALUES (?, ?, ?)",
        (user["id"], token_hash, expires_at)
    )
    conn.commit(); conn.close()
    return raw

def lookup_valid_token(raw_token: str):
    """Return row with id & user_id if token is valid (exists, unexpired, unused)."""
    token_hash = _sha256(raw_token)
    conn = connect(); cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, expires_at, used_at
        FROM password_resets
        WHERE token_hash = ?
    """, (token_hash,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    
    if row["used_at"] is not None:
        return None
    
    expires = datetime.datetime.fromisoformat(row["expires_at"])
    if _now_utc() > expires:
        return None
    return row

def consume_token(reset_id: int):
    conn = connect(); cur = conn.cursor()
    cur.execute("UPDATE password_resets SET used_at = CURRENT_TIMESTAMP WHERE id = ?", (reset_id,))
    conn.commit(); conn.close()

def set_new_password(user_id: int, new_password: str):    
    new_hash = hash_password(new_password)
    conn = connect(); cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_hash, user_id))
    conn.commit(); conn.close()
