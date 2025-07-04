import streamlit as st
import matplotlib.pyplot as plt
import math
import sqlite3
import os

# --- 激活碼設定 ---
PASSWORD = "aa17888"
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

if not st.session_state.access_granted:
    st.markdown("<h1 style='text-align:center; color:#FF6F61;'>請輸入激活碼以使用系統</h1>", unsafe_allow_html=True)
    password_input = st.text_input("激活碼 (密碼)", type="password")
    if st.button("確認"):
        if password_input == PASSWORD:
            st.session_state.access_granted = True
            st.experimental_rerun()
        else:
            st.error("激活碼錯誤，請重新輸入")
    st.stop()

# --- 自動初始化資料庫與資料表 ---
def init_db(db_path="baccarat_history.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS baccarat_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        result TEXT NOT NULL CHECK (result IN ('B', 'P', 'T')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

# --- 從 SQLite 讀取歷史牌局 ---
def load_history_from_db(db_path="baccarat_history.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT result FROM baccarat_results ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        history = [r[0] for r in rows if r[0] in ("B", "P", "T")]
        return history
    except Exception as e:
        st.warning(f"讀取資料庫失敗：{e}")
        return []

# --- 新增資料進 SQLite ---
def insert_result(result, db_path="baccarat_history.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO baccarat_results (result) VALUES (?)", (result,))
    conn.commit()
    conn.close()

# --- 初始化狀態 ---
def init_state():
    defaults = {
        'history': [],
        'total_profit': 0,
        'total_games': 0,
        'win_games': 0,
        'count_B': 0,
        'count_P': 0,
        'count_T': 0,
        'chip_sets': {'預設籌碼': {'win_amount': 100, 'lose_amount': 100}},
        'current_chip_set': '預設籌碼',
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

db_history = load_history_from_db()
if db_history and db_history != st.session_state.history:
    st.session_state.history = db_history

# --- 預測計算 ---
def longest_streak(seq, char):
    max_streak = streak = 0
    for c in seq:
        if c == char:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak

def weighted_prob(history, target, window=10):
    if len(history) == 0:
        return 0
    recent = history[-window:]
    weights = list(range(1, len(recent) + 1))
    total_weight = sum(weights)
    weighted_count = sum(w for h, w in zip(recent, weights) if h == target)
    return weighted_count / total_weight

def streak_score(streak, max_streak=7):
    if streak == 0:
        return 0
    return (math.exp(streak) - 1) / (math.exp(max_streak) - 1)

def reversal_score(history, target, window=6):
    if len(history) < window:
        return 0
    recent = history[-window:]
    count_target = recent.count(target)
    if count_target >= window - 1:
        return 1
    return 0

def suggest_bet_advanced():
    h = st.session_state.history
    if len(h) < 5:
        return "資料不足，暫無建議"

    b_prob = weighted_prob(h, "B")
    p_prob = weighted_prob(h, "P")
    t_prob = weighted_prob(h, "T")

    b_streak = streak_score(longest_streak(h, "B"))
    p_streak = streak_score(longest_streak(h, "P"))
    t_streak = streak_score(longest_streak(h, "T"))

    b_rev = reversal_score(h, "B")
    p_rev = reversal_score(h, "P")
    t_rev = reversal_score(h, "T")

    w_prob, w_streak, w_rev = 0.5, 0.3, 0.2

    scores = {
        "B": b_prob * w_prob + b_streak * w_streak + b_rev * w_rev,
        "P": p_prob * w_prob + p_streak * w_streak + p_rev * w_rev,
        "T": t_prob * w_prob + t_streak * w_streak + t_rev * w_rev,
    }

    top = max(scores, key=scores.get)
    if scores[top] < 0.3:
        return "趨勢不明，建議觀望"

    mapping = {"B": "莊 (B)", "P": "閒 (P)", "T": "和 (T)"}
    return f"建議下注：{mapping[top]} (信心 {scores[top]:.2f})"

# --- UI ---
st.markdown("<h1 style='text-align:center; color:#FF6F61;'>🎲 AI 百家樂全自動預測</h1>", unsafe_allow_html=True)
st.divider()

st.subheader("🎯 下注建議")
st.info(suggest_bet_advanced())
st.divider()

# --- 輸入本局結果 ---
st.subheader("🎮 輸入本局結果")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟥 莊 (B)", use_container_width=True):
        st.session_state.history.append("B")
        st.session_state.total_games += 1
        st.session_state.count_B += 1
        insert_result("B")
with col2:
    if st.button("🟦 閒 (P)", use_container_width=True):
        st.session_state.history.append("P")
        st.session_state.total_games += 1
        st.session_state.count_P += 1
        insert_result("P")
with col3:
    if st.button("🟩 和 (T)", use_container_width=True):
        st.session_state.history.append("T")
        st.session_state.total_games += 1
        st.session_state.count_T += 1
        insert_result("T")
st.divider()

# --- 勝負確認 ---
current_chip = st.session_state.chip_sets[st.session_state.current_chip_set]
win_amount = current_chip["win_amount"]
lose_amount = current_chip["lose_amount"]

st.subheader("💰 勝負確認")
col1, col2 = st.columns(2)
with col1:
    if st.button(f"✅ 勝利 (+{win_amount:,})", use_container_width=True):
        st.session_state.total_profit += win_amount
        st.session_state.win_games += 1
with col2:
    if st.button(f"❌ 失敗 (-{lose_amount:,})", use_container_width=True):
        st.session_state.total_profit -= lose_amount

if st.button("🧹 清除資料", use_container_width=True):
    st.session_state.history = []
    st.session_state.total_profit = 0
    st.session_state.total_games = 0
    st.session_state.win_games = 0
    st.session_state.count_B = 0
    st.session_state.count_P = 0
    st.session_state.count_T = 0
    conn = sqlite3.connect("baccarat_history.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM baccarat_results")
    conn.commit()
    conn.close()
    st.success("已清除所有資料")
    st.experimental_rerun()
st.divider()

# --- 統計資料 ---
st.subheader("📊 統計資料")
total = st.session_state.total_games
win_games = st.session_state.win_games
total_profit = st.session_state.total_profit
win_rate = (win_games / total * 100) if total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("莊 (B)", st.session_state.count_B)
col2.metric("閒 (P)", st.session_state.count_P)
col3.metric("和 (T)", st.session_state.count_T)
col4.metric("總局數", total)

if total > 0:
    st.info(f"勝率｜莊: {st.session_state.count_B/total*100:.1f}% | 閒: {st.session_state.count_P/total*100:.1f}% | 和: {st.session_state.count_T/total*100:.1f}%")

st.success(f"💰 獲利: {total_profit:,} 元 | 勝場: {win_games} | 總場: {total} | 勝率: {win_rate:.1f}%")
st.divider()

# --- 走勢圖 ---
def plot_trend():
    h = st.session_state.history
    if not h:
        st.info("尚無資料")
        return
    mapping = {"B": 1, "P": 0, "T": 0.5}
    data = [mapping[x] for x in h[-30:]]
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(range(1, len(data)+1), data, marker='o', color="#FF6F61", linewidth=2)
    ax.set_title("近30局走勢")
    ax.set_xlabel("局數")
    ax.set_yticks([0, 0.5, 1])
    ax.set_yticklabels(["閒", "和", "莊"])
    ax.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig)

plot_trend()
st.divider()

# --- 籌碼設定 ---
st.subheader("🎲 籌碼設定 (簡易切換)")
chip_names = list(st.session_state.chip_sets.keys())
selected_chip = st.selectbox("選擇籌碼組", chip_names, index=chip_names.index(st.session_state.current_chip_set))
st.session_state.current_chip_set = selected_chip

st.write(f"💰 勝利金額: {st.session_state.chip_sets[selected_chip]['win_amount']:,} 元")
st.write(f"💸 失敗金額: {st.session_state.chip_sets[selected_chip]['lose_amount']:,} 元")

with st.expander("➕ 新增籌碼組"):
    new_name = st.text_input("名稱", max_chars=20)
    amount_options = list(range(100, 1_000_001, 100))
    default_index = amount_options.index(100)
    new_win = st.selectbox("勝利金額", amount_options, index=default_index)
    new_lose = st.selectbox("失敗金額", amount_options, index=default_index)

    if st.button("新增"):
        if new_name.strip() and new_name not in st.session_state.chip_sets:
            st.session_state.chip_sets[new_name] = {"win_amount": new_win, "lose_amount": new_lose}
            st.session_state.current_chip_set = new_name
            st.success(f"已新增：{new_name}")
            st.experimental_rerun()
        else:
            st.warning("名稱不可空白或重複")

st.caption("© 2025 AI 百家樂全自動預測分析系統 | 手機友善優化版")
