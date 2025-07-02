import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ===== 頁面設定 =====
st.set_page_config(page_title="AI 百家樂預測分析", page_icon="🎰", layout="centered")

# ===== 黑色主題 CSS =====
st.markdown("""
<style>
body, .main {
    background-color: #0f0f0f !important;
    color: #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# ===== 激活碼驗證 =====
PASSWORD = "baccarat2025"
if "access_granted" not in st.session_state:
    input_password = st.text_input("輸入激活碼以使用系統：", type="password")
    if input_password == PASSWORD:
        st.session_state.access_granted = True
        st.success("激活成功，開始使用。")
    else:
        st.stop()

# ===== 初始化狀態 =====
if "history" not in st.session_state:
    st.session_state.history = []
if "wins" not in st.session_state:
    st.session_state.wins = 0
if "games" not in st.session_state:
    st.session_state.games = 0
if "balance" not in st.session_state:
    st.session_state.balance = 1000
if "side_bets" not in st.session_state:
    st.session_state.side_bets = {}

st.title("🎰 AI 百家樂預測系統 黑色極簡版")
st.caption(f"目前金額：${st.session_state.balance}")

# ===== 輸入下注金額 =====
bet_amount = st.number_input("本局下注金額：", min_value=10, max_value=10000, value=100, step=10)

# ===== 模擬預測函數 =====
def get_prediction():
    import random
    return random.choice(["莊", "閒", "和"])

def get_prediction_accuracy():
    if st.session_state.games == 0:
        return 0.0
    return (st.session_state.wins / st.session_state.games) * 100

# ===== 出牌按鈕 =====
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟦 閒", use_container_width=True):
        st.session_state.history.append("P")
        st.session_state.games += 1
with col2:
    if st.button("🟩 和", use_container_width=True):
        st.session_state.history.append("T")
        st.session_state.games += 1
with col3:
    if st.button("🟥 莊", use_container_width=True):
        st.session_state.history.append("B")
        st.session_state.games += 1

st.markdown(f"### 📈 預測建議：**{get_prediction()}**")

# ===== 勝負確認 =====
result = st.radio("本局結果：", ["尚未設定", "勝利", "失敗"])
if result == "勝利":
    st.session_state.wins += 1
    st.session_state.balance += bet_amount
    st.success(f"勝利！金額增加 ${bet_amount}，目前餘額 ${st.session_state.balance}")
elif result == "失敗":
    st.session_state.balance -= bet_amount
    st.error(f"失敗！金額減少 ${bet_amount}，目前餘額 ${st.session_state.balance}")

st.markdown(f"#### 當前勝率：{get_prediction_accuracy():.1f}%")

# ===== 側注按鈕 =====
col4, col5, col6, col7 = st.columns(4)
with col4:
    if st.button("閒對", use_container_width=True):
        st.session_state.side_bets['閒對'] = st.session_state.side_bets.get('閒對', 0) + 1
with col5:
    if st.button("大", use_container_width=True):
        st.session_state.side_bets['大'] = st.session_state.side_bets.get('大', 0) + 1
with col6:
    if st.button("小", use_container_width=True):
        st.session_state.side_bets['小'] = st.session_state.side_bets.get('小', 0) + 1
with col7:
    if st.button("莊對", use_container_width=True):
        st.session_state.side_bets['莊對'] = st.session_state.side_bets.get('莊對', 0) + 1

# ===== 出牌統計圖表 =====
st.divider()
st.subheader("📊 出牌統計")
data = pd.Series(st.session_state.history).value_counts().reindex(["B", "P", "T"], fill_value=0)
st.bar_chart(data)

# ===== 側注統計 =====
if st.session_state.side_bets:
    st.subheader("🎲 側注統計")
    side_data = pd.Series(st.session_state.side_bets)
    st.bar_chart(side_data)

# ===== 重置按鈕 =====
if st.button("🧹 重置資料"):
    st.session_state.history = []
    st.session_state.games = 0
    st.session_state.wins = 0
    st.session_state.balance = 1000
    st.session_state.side_bets = {}
    st.success("已重置所有資料")

st.caption("© 2025 AI 百家樂預測系統 | 黑色極簡安全鎖定版")
