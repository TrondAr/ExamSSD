from pathlib import Path
import sqlite3

BASIC_DIRECTORY = Path(__file__).resolve().parent
DATABASE = BASIC_DIRECTORY / "user_database.db"

def connect():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

def init_db():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('patient','practitioner','admin')),
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id INTEGER NOT NULL,
            uploaded_by_user_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            storage_name TEXT NOT NULL UNIQUE,
            mime_type TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            sha256_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (uploaded_by_user_id) REFERENCES users(id) ON DELETE SET NULL
        )           
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gp_patient (
            gp_user_id INTEGER NOT NULL,
            patient_user_id INTEGER NOT NULL,
            PRIMARY KEY (gp_user_id, patient_user_id),
            FOREIGN KEY (gp_user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (patient_user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMP,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

def get_user_by_email(email: str):
    email = email.strip().lower()
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(email: str, password_hash: str, role: str ='patient'):
    email = email.strip().lower()
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)', (email, password_hash, role))
    conn.commit()
    conn.close()

def get_user_by_id(user_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_practitioners():
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT id, email FROM users WHERE role = 'practitioner' AND is_active = 1 ORDER BY email")
    rows = cur.fetchall(); conn.close()
    return rows

def add_gp_link(gp_user_id: int, patient_user_id: int):
    conn = connect(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO gp_patient (gp_user_id, patient_user_id) VALUES (?, ?)", (gp_user_id, patient_user_id))
        conn.commit()
    except Exception:        
        pass
    finally:
        conn.close()