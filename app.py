import streamlit as st
import pandas as pd

# 頁面設定
st.set_page_config(page_title="AI 百家樂預測分析", page_icon="🎰", layout="centered")

# 黑色主題 + 自訂 CSS
st.markdown("""
<style>
body, .main {
    background-color: #0f0f0f !important;
    color: #e0e0e0 !important;
}
.big-button {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: #1e1e1e;
    border-radius: 16px;
    padding: 20px;
    margin: 5px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.big-button:hover {
    background-color: #333333;
}
.big-text {
    font-size: 48px;
    font-weight: bold;
    margin: 10px 0 5px 0;
}
.sub-text {
    font-size: 16px;
    opacity: 0.7;
}
.blue {color: #3fa9f5;}
.green {color: #7ed321;}
.red {color: #ff4c4c;}
.yellow {color: #f5a623;}
</style>
""", unsafe_allow_html=True)

# 初始化紀錄與勝率計算
if 'history' not in st.session_state:
    st.session_state.history = []
if 'wins' not in st.session_state:
    st.session_state.wins = 0
if 'games' not in st.session_state:
    st.session_state.games = 0
if 'side_bets' not in st.session_state:
    st.session_state.side_bets = {}

# 頂部提示文字
st.markdown("<h4 style='text-align:center; color:#FF6F61;'>🔴 預測開始，請按荷官發牌順序輸入牌</h4>", unsafe_allow_html=True)

# 模擬預測 (未接模型可先假設準確率隨機或固定)
def get_prediction_accuracy():
    if st.session_state.games == 0:
        return 0.0
    return (st.session_state.wins / st.session_state.games) * 100

# 大按鈕區
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟦 閒", use_container_width=True):
        st.session_state.history.append("P")
        st.session_state.games += 1
    st.markdown(f"<div class='sub-text'>必勝率+{get_prediction_accuracy():.1f}%</div>", unsafe_allow_html=True)
with col2:
    if st.button("🟩 和", use_container_width=True):
        st.session_state.history.append("T")
        st.session_state.games += 1
    st.markdown(f"<div class='sub-text'>必勝率+{get_prediction_accuracy():.1f}%</div>", unsafe_allow_html=True)
with col3:
    if st.button("🟥 莊", use_container_width=True):
        st.session_state.history.append("B")
        st.session_state.games += 1
    st.markdown(f"<div class='sub-text'>必勝率+{get_prediction_accuracy():.1f}%</div>", unsafe_allow_html=True)

# 小按鈕區
col4, col5, col6, col7 = st.columns(4)
with col4:
    if st.button("閒對", use_container_width=True):
        st.session_state.side_bets['閒對'] = st.session_state.side_bets.get('閒對', 0) + 1
    st.markdown(f"<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col5:
    if st.button("大", use_container_width=True):
        st.session_state.side_bets['大'] = st.session_state.side_bets.get('大', 0) + 1
    st.markdown(f"<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col6:
    if st.button("小", use_container_width=True):
        st.session_state.side_bets['小'] = st.session_state.side_bets.get('小', 0) + 1
    st.markdown(f"<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col7:
    if st.button("莊對", use_container_width=True):
        st.session_state.side_bets['莊對'] = st.session_state.side_bets.get('莊對', 0) + 1
    st.markdown(f"<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)

col8, col9, col10 = st.columns(3)
with col8:
    if st.button("閒龍寶", use_container_width=True):
        st.session_state.side_bets['閒龍寶'] = st.session_state.side_bets.get('閒龍寶', 0) + 1
    st.markdown(f"<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col9:
    if st.button("幸運六", use_container_width=True):
        st.session_state.side_bets['幸運六'] = st.session_state.side_bets.get('幸運六', 0) + 1
    st.markdown(f"<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col10:
    if st.button("莊龍寶", use_container_width=True):
        st.session_state.side_bets['莊龍寶'] = st.session_state.side_bets.get('莊龍寶', 0) + 1
    st.markdown(f"<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)

# 顯示統計圖
st.divider()
st.markdown("### ⚡ 出牌統計")
data = pd.DataFrame(pd.Series(st.session_state.history).value_counts(), columns=['次數']).rename_axis('出牌').reset_index()
st.dataframe(data, use_container_width=True)

# 重置按鈕
if st.button("🧹 重置資料"):
    st.session_state.history = []
    st.session_state.games = 0
    st.session_state.wins = 0
    st.session_state.side_bets = {}
    st.success("資料已重置")

st.caption("© 2025 AI 百家樂預測系統 | 黑色極簡版")
