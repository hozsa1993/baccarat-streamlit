# === activation_manager.py ===
import sqlite3
from datetime import datetime
import socket
import uuid

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
            usage_count INTEGER DEFAULT 0,
            bind_ip TEXT,
            bind_hostname TEXT,
            bind_mac TEXT,
            bind_limit INTEGER DEFAULT 1,
            bind_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_current_machine_info():
    ip = socket.gethostbyname(socket.gethostname())
    hostname = socket.gethostname()
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                    for ele in range(0,8*6,8)][::-1])
    return ip, hostname, mac

def validate_code(code):
    ip, hostname, mac = get_current_machine_info()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT is_active, expiry_date, usage_limit, usage_count,
               bind_ip, bind_hostname, bind_mac, bind_limit, bind_count
        FROM activation_codes WHERE code = ?
    """, (code,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "❌ 激活碼不存在"
    (is_active, expiry_date, usage_limit, usage_count,
     bind_ip, bind_hostname, bind_mac, bind_limit, bind_count) = row

    if not is_active:
        conn.close()
        return False, "❌ 激活碼已停用"
    if expiry_date and datetime.now().date() > datetime.strptime(expiry_date, "%Y-%m-%d").date():
        conn.close()
        return False, "❌ 激活碼已過期"
    if usage_count >= usage_limit:
        conn.close()
        return False, "❌ 已達使用次數上限"

    # 綁定檢查
    if bind_ip and bind_ip != ip:
        # 不同IP，檢查是否還可綁定
        if bind_count >= bind_limit:
            conn.close()
            return False, "❌ 已達硬體綁定上限"
        else:
            # 綁定新IP等資訊，並+1綁定計數
            cursor.execute("""
                UPDATE activation_codes SET bind_ip=?, bind_hostname=?, bind_mac=?, bind_count=bind_count+1
                WHERE code=?
            """, (ip, hostname, mac, code))
            conn.commit()
    else:
        # 首次綁定
        if not bind_ip:
            cursor.execute("""
                UPDATE activation_codes SET bind_ip=?, bind_hostname=?, bind_mac=?, bind_count=1
                WHERE code=?
            """, (ip, hostname, mac, code))
            conn.commit()

    cursor.execute("UPDATE activation_codes SET usage_count = usage_count + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    return True, "✅ 激活成功！歡迎使用"

def add_activation_code(code, expiry_date, usage_limit, bind_limit=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO activation_codes 
        (code, expiry_date, usage_limit, bind_limit) VALUES (?, ?, ?, ?)
    """, (code, expiry_date, usage_limit, bind_limit))
    conn.commit()
    conn.close()

def list_activation_codes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code, is_active, expiry_date, usage_limit, usage_count, bind_ip, bind_hostname, bind_mac, bind_limit, bind_count FROM activation_codes")
    rows = cursor.fetchall()
    conn.close()
    return rows

def set_activation_code_active(code, active:bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE activation_codes SET is_active = ? WHERE code = ?", (1 if active else 0, code))
    conn.commit()
    conn.close()

def delete_activation_code(code):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activation_codes WHERE code = ?", (code,))
    conn.commit()
    conn.close()


# === app.py ===
import streamlit as st
import subprocess
import os
from activation_manager import (
    setup_activation_db, validate_code, add_activation_code,
    list_activation_codes, set_activation_code_active, delete_activation_code
)

# 初始化DB與測試碼
setup_activation_db()
add_activation_code("VIP2025", "2025-12-31", 500, bind_limit=2)

# === 管理員密碼，請自行設定強密碼 ===
ADMIN_PASSWORD = "admin2025"

def show_admin_panel():
    st.header("⚙️ 激活碼管理後台")
    codes = list_activation_codes()
    st.write("### 所有激活碼")
    for c in codes:
        code, is_active, expiry_date, usage_limit, usage_count, bind_ip, bind_hostname, bind_mac, bind_limit, bind_count = c
        col1, col2, col3, col4, col5 = st.columns([2,1,2,2,1])
        with col1:
            st.text(code)
        with col2:
            st.text("啟用" if is_active else "停用")
        with col3:
            st.text(f"到期: {expiry_date}\n限用: {usage_limit}\n已用: {usage_count}")
        with col4:
            st.text(f"綁定IP: {bind_ip}\n主機: {bind_hostname}\nMAC: {bind_mac}\n綁定限制: {bind_limit}\n綁定計數: {bind_count}")
        with col5:
            if st.button(f"切換狀態 {code}"):
                set_activation_code_active(code, not is_active)
                st.experimental_rerun()
            if st.button(f"刪除 {code}"):
                delete_activation_code(code)
                st.experimental_rerun()

    st.markdown("---")
    st.write("### 新增激活碼")
    new_code = st.text_input("激活碼名稱(唯一)", max_chars=20, key="new_code")
    new_expiry = st.date_input("過期日期", key="new_expiry")
    new_usage = st.number_input("使用次數上限", min_value=1, max_value=10000, value=100)
    new_bind_limit = st.number_input("硬體綁定限制（幾台裝置）", min_value=1, max_value=10, value=1)

    if st.button("新增激活碼"):
        if new_code.strip():
            add_activation_code(new_code.strip(), new_expiry.strftime("%Y-%m-%d"), new_usage, new_bind_limit)
            st.success(f"新增激活碼：{new_code.strip()}")
            st.experimental_rerun()
        else:
            st.error("激活碼名稱不可空白")

# === 使用者授權驗證 ===
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

menu = ["使用者登入", "管理後台"]
choice = st.sidebar.selectbox("選單", menu)

if choice == "管理後台":
    st.title("🔑 管理員登入")
    admin_pwd = st.text_input("管理員密碼", type="password")
    if st.button("登入"):
        if admin_pwd == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.experimental_rerun()
        else:
            st.error("管理員密碼錯誤")
    if not st.session_state.admin_logged_in:
        st.stop()
    show_admin_panel()
    st.stop()

# 使用者登入流程
if not st.session_state.access_granted:
    st.title("🔒 專屬激活碼驗證")
    code_input = st.text_input("請輸入您的激活碼", type="password")
    if st.button("啟用"):
        valid, message = validate_code(code_input.strip())
        if valid:
            st.session_state.access_granted = True
            st.success(message)
            st.experimental_rerun()
        else:
            st.error(message)
    st.stop()

# 自動爬蟲執行 (首次啟動)
if "crawler_done" not in st.session_state:
    st.info("正在更新最新牌局...")
    try:
        result = subprocess.run(['python', 'baccarat_crawler.py'], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            st.success("✅ 爬蟲執行完成")
        else:
            st.error(f"❌ 爬蟲執行錯誤：{result.stderr}")
    except subprocess.TimeoutExpired:
        st.error("❌ 爬蟲執行超時")
    st.session_state.crawler_done = True

# 主程式區域，請貼入你的完整預測核心、走勢圖、下注建議等功能
st.title("🎲 AI 百家樂全自動預測系統")
st.write("✅ 已完成授權與資料更新，請開始使用。")
st.info("🔹 請將完整預測視覺化及統計邏輯貼入此區，即完成商用部署")
