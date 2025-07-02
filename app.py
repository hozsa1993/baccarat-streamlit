import streamlit as st
import math

# 頁面設定
st.set_page_config(page_title="AI 百家樂預測分析", page_icon="🎰", layout="centered")

# 黑色主題
st.markdown("""
<style>
body, .main {
    background-color: #0f0f0f !important;
    color: #e0e0e0 !important;
}
.stButton>button {
    height: 100px !important;
    font-size: 36px !important;
    border-radius: 12px !important;
}
.stButton>button:hover {
    opacity: 0.85;
}
.metric-label, .metric-value {
    color: #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# --- 激活碼驗證 ---
PASSWORD = "baccarat2025"
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

# 初始化
if 'history' not in st.session_state:
    st.session_state.history = []
if 'total_games' not in st.session_state:
    st.session_state.total_games = 0
if 'win_games' not in st.session_state:
    st.session_state.win_games = 0

# 顯示狀態欄
st.selectbox("策略模式", ["標準策略", "進階策略", "模擬模式"], index=0)
cols = st.columns([1, 1, 1])
cols[0].metric("已輸入牌數", len(st.session_state.history))
cols[1].metric("局數", f"#{st.session_state.total_games}")
acc = (st.session_state.win_games / st.session_state.total_games * 100) if st.session_state.total_games else 0
cols[2].metric("模型準確率", f"{acc:.1f}%")

# 警示文字
st.markdown("<h4 style='text-align:center; color:#FF6F61;'>🔴 預測開始，請按照荷官發牌順序輸入</h4>", unsafe_allow_html=True)

# 大按鈕區塊
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟦 閒", use_container_width=True):
        st.session_state.history.append("P")
        st.session_state.total_games += 1
with col2:
    if st.button("🟩 和", use_container_width=True):
        st.session_state.history.append("T")
        st.session_state.total_games += 1
with col3:
    if st.button("🟥 莊", use_container_width=True):
        st.session_state.history.append("B")
        st.session_state.total_games += 1

# 小按鈕選項
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("閒對", use_container_width=True): pass
with col2:
    if st.button("大", use_container_width=True): pass
with col3:
    if st.button("小", use_container_width=True): pass
with col4:
    if st.button("莊對", use_container_width=True): pass

col5, col6, col7 = st.columns(3)
with col5:
    if st.button("閒龍寶", use_container_width=True): pass
with col6:
    if st.button("幸運六", use_container_width=True): pass
with col7:
    if st.button("莊龍寶", use_container_width=True): pass

# 底部功能
st.divider()
if st.button("🧹 重置資料"):
    st.session_state.history = []
    st.session_state.total_games = 0
    st.session_state.win_games = 0
    st.success("資料已重置")

st.caption("© 2025 AI 百家樂預測系統 | 黑色極簡優化版")

