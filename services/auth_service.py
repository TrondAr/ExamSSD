from database import connect
from security import check_password

def verify_password(email: str, password: str) -> bool:    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False    
    return check_password(row['password_hash'], password)
