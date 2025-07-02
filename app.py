# ======================================
# 📈 AI 百家樂全自動預測分析系統 強化最終版
# 作者：ChatGPT + 透抽需求客製
# 功能：激活碼 / 自動計算盈虧 / 日累分離統計 / 注碼建議 / 匯出報表
# ======================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import io

# ---------- 激活碼驗證 ---------- #
PASSWORD = "aa17888"
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False
if not st.session_state.access_granted:
    st.title("🔒 請輸入激活碼")
    pw = st.text_input("激活碼 (密碼)", type="password")
    if st.button("確認"):
        if pw == PASSWORD:
            st.session_state.access_granted = True
            st.experimental_rerun()
        else:
            st.error("激活碼錯誤，請重新輸入")
    st.stop()

# ---------- 初始化 ---------- #
def init_state():
    defaults = {
        'history': [],
        'daily_profit': 0,
        'daily_games': 0,
        'daily_wins': 0,
        'total_profit': 0,
        'total_games': 0,
        'total_wins': 0,
        'chip_sets': {'預設籌碼': {'win_amount': 10000, 'lose_amount': 10000}},
        'current_chip_set': '預設籌碼',
        'auto_calc': False,
        'last_reset_date': str(date.today()),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ---------- 每日重置 ---------- #
if st.session_state.last_reset_date != str(date.today()):
    st.session_state.daily_profit = 0
    st.session_state.daily_games = 0
    st.session_state.daily_wins = 0
    st.session_state.last_reset_date = str(date.today())

# ---------- 標題 ---------- #
st.markdown("""
<h1 style='text-align:center; color:#FF6F61;'>🎲 AI 百家樂預測分析 強化版</h1>
<p style='text-align:center; color:gray;'>自動計算｜日累統計｜下注建議｜手機友善</p>
""", unsafe_allow_html=True)

# ---------- 區塊：自動計算選擇 ---------- #
st.checkbox("自動計算盈虧 (輸入本局結果後自動計入盈虧)", key="auto_calc")
st.divider()

# ---------- 區塊：輸入本局結果 ---------- #
st.subheader("🎮 輸入本局結果")
col1, col2, col3 = st.columns(3)
current_chip = st.session_state.chip_sets[st.session_state.current_chip_set]
win_amount = current_chip['win_amount']
lose_amount = current_chip['lose_amount']

def record_result(result):
    st.session_state.history.append({
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'result': result
    })
    st.session_state.daily_games += 1
    st.session_state.total_games += 1
    if st.session_state.auto_calc:
        if result in ["B", "P"]:
            st.session_state.daily_profit += win_amount
            st.session_state.total_profit += win_amount
            st.session_state.daily_wins += 1
            st.session_state.total_wins += 1
        else:
            st.session_state.daily_profit -= lose_amount
            st.session_state.total_profit -= lose_amount

with col1:
    if st.button("🟥 莊 (B)", use_container_width=True):
        record_result("B")
with col2:
    if st.button("🟦 閒 (P)", use_container_width=True):
        record_result("P")
with col3:
    if st.button("🟩 和 (T)", use_container_width=True):
        record_result("T")

st.divider()

# ---------- 區塊：勝負確認 (手動計算用) ---------- #
st.subheader("💰 勝負確認 (手動加減)")
c1, c2 = st.columns(2)
with c1:
    if st.button(f"✅ 勝利 (+{win_amount:,})", use_container_width=True):
        st.session_state.daily_profit += win_amount
        st.session_state.total_profit += win_amount
        st.session_state.daily_wins += 1
        st.session_state.total_wins += 1
with c2:
    if st.button(f"❌ 失敗 (-{lose_amount:,})", use_container_width=True):
        st.session_state.daily_profit -= lose_amount
        st.session_state.total_profit -= lose_amount

if st.button("🧹 清除所有資料", use_container_width=True):
    for k in ['history', 'daily_profit', 'daily_games', 'daily_wins', 'total_profit', 'total_games', 'total_wins']:
        st.session_state[k] = [] if k == 'history' else 0
    st.success("已清除所有資料")

st.divider()

# ---------- 區塊：統計資料 ---------- #
st.subheader("📊 統計資料")
daily_win_rate = (st.session_state.daily_wins / st.session_state.daily_games * 100) if st.session_state.daily_games else 0
total_win_rate = (st.session_state.total_wins / st.session_state.total_games * 100) if st.session_state.total_games else 0

c1, c2 = st.columns(2)
with c1:
    st.info(f"今日｜局數: {st.session_state.daily_games}｜勝場: {st.session_state.daily_wins}｜獲利: {st.session_state.daily_profit:,}｜勝率: {daily_win_rate:.1f}%")
with c2:
    st.success(f"累計｜局數: {st.session_state.total_games}｜勝場: {st.session_state.total_wins}｜獲利: {st.session_state.total_profit:,}｜勝率: {total_win_rate:.1f}%")

# ---------- 區塊：下注建議 ---------- #
st.subheader("🎯 下注建議")
h = [x['result'] for x in st.session_state.history]
if len(h) >= 5:
    last3 = h[-3:]
    if all(x == "B" for x in last3):
        st.info("建議下注：莊 (B)")
    elif all(x == "P" for x in last3):
        st.info("建議下注：閒 (P)")
    else:
        st.info("建議觀望或小注")
else:
    st.info("資料不足，無法給出建議")

# ---------- 區塊：走勢圖 ---------- #
st.subheader("📈 近 30 局走勢圖")
if h:
    mapping = {"B": 1, "P": 0, "T": 0.5}
    data = [mapping[x] for x in h[-30:]]
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(range(1, len(data) + 1), data, marker='o', color="#FF6F61", linewidth=2)
    ax.set_yticks([0, 0.5, 1])
    ax.set_yticklabels(["閒 (0)", "和 (0.5)", "莊 (1)"])
    ax.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig)
else:
    st.info("尚無資料")

st.divider()

# ---------- 區塊：籌碼設定 ---------- #
st.subheader("🎲 籌碼設定 (下拉簡化)")
chip_names = list(st.session_state.chip_sets.keys())
selected_chip = st.selectbox("選擇籌碼組", chip_names, index=chip_names.index(st.session_state.current_chip_set))
st.session_state.current_chip_set = selected_chip

st.write(f"💰 勝利金額: {st.session_state.chip_sets[selected_chip]['win_amount']:,}")
st.write(f"💸 失敗金額: {st.session_state.chip_sets[selected_chip]['lose_amount']:,}")

with st.expander("➕ 新增籌碼組"):
    new_name = st.text_input("名稱", max_chars=20)
    new_win = st.number_input("勝利金額", 1, 1_000_000, 10000, 1000)
    new_lose = st.number_input("失敗金額", 1, 1_000_000, 10000, 1000)
    if st.button("新增"):
        if new_name.strip() and new_name not in st.session_state.chip_sets:
            st.session_state.chip_sets[new_name] = {"win_amount": new_win, "lose_amount": new_lose}
            st.session_state.current_chip_set = new_name
            st.success(f"已新增 {new_name}")
            st.experimental_rerun()

st.divider()

# ---------- 區塊：匯出報表 ---------- #
st.subheader("📤 匯出報表")
if st.button("匯出 CSV 報表"):
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("下載報表", data=csv, file_name="baccarat_report.csv", mime="text/csv")
    else:
        st.warning("目前無資料可匯出")

st.caption("© 2025 AI 百家樂全自動預測分析系統 強化版 | 透抽專用")
