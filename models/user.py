from database import get_connection
import hashlib


VALID_ROLES = ('viewer', 'analyst', 'admin')


def create_user(username, password, role='viewer'):
    if role not in VALID_ROLES:
        return None, f"Invalid role. Choose from: {VALID_ROLES}"
    if not username or not password:
        return None, "Username and password are required."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hashed, role))
        conn.commit()
        return cursor.lastrowid, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at FROM users")
    users = cursor.fetchall()
    conn.close()
    return [dict(u) for u in users]


def authenticate_user(username, password):
    user = get_user_by_username(username)
    hashed = hashlib.sha256(password.encode()).hexdigest()
    if user and user['password'] == hashed:
        return user
    return None