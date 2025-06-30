import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# 頁面設定
st.set_page_config(page_title="AI 百家樂全自動預測分析", page_icon="🎰", layout="centered")

st.markdown("""
<h1 style="text-align:center; color:#FF6F61;">🎲 AI 百家樂全自動預測分析</h1>
<p style="text-align:center; color:gray;">實時記錄、勝率分析、自動走勢提示與下注建議</p>
""", unsafe_allow_html=True)

# 初始化狀態
def init_state():
    defaults = {'history': [], 'total_profit': 0, 'total_games': 0, 'win_games': 0}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
st.divider()

# 輸入區塊
st.markdown("### 🎮 輸入本局結果")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟥 莊 (B)", use_container_width=True):
        st.session_state.history.append("B")
        st.session_state.total_games += 1
with col2:
    if st.button("🟦 閒 (P)", use_container_width=True):
        st.session_state.history.append("P")
        st.session_state.total_games += 1
with col3:
    if st.button("🟩 和 (T)", use_container_width=True):
        st.session_state.history.append("T")
        st.session_state.total_games += 1

st.markdown("### 💰 勝負確認")
col4, col5 = st.columns(2)
with col4:
    if st.button("✅ 確認勝利 (+10,000)", use_container_width=True):
        st.session_state.total_profit += 10000
        st.session_state.win_games += 1
with col5:
    if st.button("❌ 確認失敗 (-10,000)", use_container_width=True):
        st.session_state.total_profit -= 10000

if st.button("🧹 清除所有資料", use_container_width=True):
    for k in ['history', 'total_profit', 'total_games', 'win_games']:
        st.session_state[k] = [] if k == 'history' else 0
    st.success("所有資料已清除")

st.divider()

# 顯示統計
def display_stats():
    h = st.session_state.history
    banker = h.count("B")
    player = h.count("P")
    tie = h.count("T")
    total = len(h)

    st.subheader("📊 統計資料")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("莊 (B)", banker)
    col2.metric("閒 (P)", player)
    col3.metric("和 (T)", tie)
    col4.metric("總局數", total)

    if total > 0:
        st.info(f"勝率｜莊: {banker/total*100:.1f}% | 閒: {player/total*100:.1f}% | 和: {tie/total*100:.1f}%")
    else:
        st.warning("尚無資料，請輸入結果")

    win_rate = (st.session_state.win_games / st.session_state.total_games * 100) if st.session_state.total_games else 0
    st.success(f"💰 累積獲利: {st.session_state.total_profit:,} 元 | 勝場數: {st.session_state.win_games} | 總場數: {st.session_state.total_games} | 勝率: {win_rate:.1f}%")

    if total >= 3:
        last3 = h[-3:]
        if all(x == "B" for x in last3):
            sug = "建議下注：莊 (B)"
        elif all(x == "P" for x in last3):
            sug = "建議下注：閒 (P)"
        else:
            sug = "建議下注：觀望或依直覺"
    else:
        sug = "資料不足，暫無下注建議"
    st.info(f"🎯 {sug}")

display_stats()
st.divider()

# 繪製走勢圖
def plot_trend():
    h = st.session_state.history
    if not h:
        st.warning("無資料可繪製走勢圖")
        return
    mapping = {"B": 1, "P": 0, "T": 0.5}
    data = [mapping[x] for x in h[-30:]]
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(range(1, len(data)+1), data, marker='o', color="#FF6F61", linestyle='-', linewidth=2)
    ax.set_title("近 30 局莊閒和走勢圖", fontsize=14)
    ax.set_xlabel("局數")
    ax.set_ylabel("結果")
    ax.set_yticks([0, 0.5, 1])
    ax.set_yticklabels(["閒 (0)", "和 (0.5)", "莊 (1)"])
    ax.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig)

plot_trend()

st.divider()

# 歷史紀錄
with st.expander("🕒 歷史紀錄 (點此展開/收合)"):
    if st.session_state.history:
        st.text_area("歷史輸入記錄", " ".join(st.session_state.history), height=120)
    else:
        st.info("尚無紀錄，請開始輸入資料")

st.caption("© 2025 AI 百家樂全自動預測分析系統 | 手機友善優化版")
