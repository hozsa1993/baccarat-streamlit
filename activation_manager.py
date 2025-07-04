import sqlite3
from datetime import datetime

DB_PATH = "activation_codes.db"

def setup_activation_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activation_codes (
            code TEXT PRIMARY KEY,
            is_active INTEGER DEFAULT 1,
            expiry_date TEXT,
            usage_limit INTEGER DEFAULT 100,
            usage_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def validate_code(code):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT is_active, expiry_date, usage_limit, usage_count FROM activation_codes WHERE code = ?", (code,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "❌ 激活碼不存在"
    is_active, expiry_date, usage_limit, usage_count = row

    if not is_active:
        conn.close()
        return False, "❌ 激活碼已停用"
    if expiry_date and datetime.now().date() > datetime.strptime(expiry_date, "%Y-%m-%d").date():
        conn.close()
        return False, "❌ 激活碼已過期"
    if usage_count >= usage_limit:
        conn.close()
        return False, "❌ 已達使用次數上限"

    cursor.execute("UPDATE activation_codes SET usage_count = usage_count + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    return True, "✅ 激活成功！歡迎使用"

def add_activation_code(code, expiry_date, usage_limit):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO activation_codes (code, expiry_date, usage_limit) VALUES (?, ?, ?)",
        (code, expiry_date, usage_limit)
    )
    conn.commit()
    conn.close()
