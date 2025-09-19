from database import connect

conn = connect()
cur = conn.cursor()
for row in cur.execute("SELECT id, email, role, is_active, created_at, updated_at FROM users"):
    print(dict(row))
conn.close()
