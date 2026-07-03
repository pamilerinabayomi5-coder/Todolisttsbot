import sqlite3
from datetime import datetime
from config import DATABASE_NAME, logger

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    join_date TEXT NOT NULL
                )
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    telegram_id INTEGER PRIMARY KEY,
                    timezone TEXT DEFAULT 'UTC',
                    notification_pref TEXT DEFAULT 'enabled',
                    date_format TEXT DEFAULT 'YYYY-MM-DD',
                    default_reminder TEXT DEFAULT '09:00',
                    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE
                )
            """)
            
            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'Personal',
                    priority TEXT DEFAULT 'Medium',
                    status TEXT DEFAULT 'Pending',
                    due_date TEXT,
                    reminder_time TEXT,
                    recurrence TEXT DEFAULT 'None',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)

# User Ops
def add_user(telegram_id: int, username: str, first_name: str):
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username, first_name, join_date) VALUES (?, ?, ?, ?)",
            (telegram_id, username, first_name, now)
        )
        cursor.execute(
            "INSERT OR IGNORE INTO settings (telegram_id) VALUES (?)",
            (telegram_id,)
        )
        conn.commit()

def get_user_settings(telegram_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM settings WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()

def update_user_settings(telegram_id: int, key: str, value: str):
    valid_keys = ["timezone", "notification_pref", "date_format", "default_reminder"]
    if key not in valid_keys:
        return
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE settings SET {key} = ? WHERE telegram_id = ?", (value, telegram_id))
        conn.commit()

# Task Ops
def add_task(user_id: int, title: str, description: str, category: str, priority: str, due_date: str, reminder_time: str, recurrence: str) -> int:
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (user_id, title, description, category, priority, status, due_date, reminder_time, recurrence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?, ?, ?, ?)
        """, (user_id, title, description, category, priority, due_date, reminder_time, recurrence, now, now))
        conn.commit()
        return cursor.lastrowid

def get_tasks(user_id: int, status: str = None, category: str = None):
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user_id]
    if status:
        query += " AND status = ?"
        params.append(status)
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY due_date ASC, priority DESC"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

def get_task_by_id(task_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return cursor.fetchone()

def update_task_status(task_id: int, status: str):
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?", (status, now, task_id))
        conn.commit()

def update_task_field(task_id: int, field: str, value: str):
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE tasks SET {field} = ?, updated_at = ? WHERE id = ?", (value, now, task_id))
        conn.commit()

def delete_task(task_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

def get_all_pending_reminders():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE status = 'Pending' AND reminder_time IS NOT NULL AND reminder_time != ''")
        return cursor.fetchall()

def search_tasks_db(user_id: int, query: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND (title LIKE ? OR description LIKE ?)",
            (user_id, f"%{query}%", f"%{query}%")
        )
        return cursor.fetchall()
