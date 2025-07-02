import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ===== 頁面設定 =====
st.set_page_config(page_title="AI 百家樂進階預測系統", page_icon="🎰", layout="centered")

# ===== 黑色主題 CSS =====
st.markdown("""
<style>
body, .main {
    background-color: #0f0f0f !important;
    color: #e0e0e0 !important;
}
.stButton>button {
    height: 80px !important;
    font-size: 30px !important;
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

# ===== 激活碼驗證 =====
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

# ===== 初始化狀態 =====
if "history" not in st.session_state:
    st.session_state.history = []
if "total_games" not in st.session_state:
    st.session_state.total_games = 0
if "win_games" not in st.session_state:
    st.session_state.win_games = 0
if "balance" not in st.session_state:
    st.session_state.balance = 1000
if "bet_amount" not in st.session_state:
    st.session_state.bet_amount = 100
if "strategy" not in st.session_state:
    st.session_state.strategy = "無策略"
if "martingale_step" not in st.session_state:
    st.session_state.martingale_step = 0
if "count_1326" not in st.session_state:
    st.session_state.count_1326 = 0

# ===== 選擇策略 =====
strategy = st.selectbox("選擇下注策略", ["無策略", "1326策略", "馬丁策略", "反馬丁策略"], index=0)
st.session_state.strategy = strategy

# ===== 下注金額設定 =====
if strategy == "無策略":
    bet_amount = st.number_input("本局下注金額", min_value=10, max_value=10000, value=st.session_state.bet_amount, step=10)
    st.session_state.bet_amount = bet_amount
else:
    st.markdown(f"本局下注金額將由【{strategy}】策略自動計算")

# ===== 進階預測函數 =====
def advanced_predict(history, recent_window=6):
    if not history:
        return "無法預測"

    total = len(history)
    count_p = history.count("P")
    count_b = history.count("B")
    count_t = history.count("T")

    # 全局機率
    prob_p = count_p / total
    prob_b = count_b / total
    prob_t = count_t / total

    # 最近幾局趨勢分析
    recent = history[-recent_window:]
    recent_p = recent.count("P")
    recent_b = recent.count("B")
    recent_t = recent.count("T")

    # 趨勢得分（短期偏向）
    trend_score_p = recent_p / recent_window
    trend_score_b = recent_b / recent_window
    trend_score_t = recent_t / recent_window

    # 綜合得分 = 全局機率 * 0.6 + 短期趨勢 * 0.4 (可調)
    score_p = prob_p * 0.6 + trend_score_p * 0.4
    score_b = prob_b * 0.6 + trend_score_b * 0.4
    score_t = prob_t * 0.6 + trend_score_t * 0.4

    scores = {"閒 (P)": score_p, "莊 (B)": score_b, "和 (T)": score_t}
    prediction = max(scores, key=scores.get)
    confidence = scores[prediction] * 100

    return f"{prediction} ({confidence:.1f}%)"

prediction = advanced_predict(st.session_state.history)

# ===== 計算下注金額 =====
def calc_bet_amount(strategy):
    base_bet = 100
    if strategy == "1326策略":
        seq = [1,3,2,6]
        step = st.session_state.count_1326
        amount = seq[step] * base_bet
        return amount
    elif strategy == "馬丁策略":
        step = st.session_state.martingale_step
        return base_bet * (2 ** step)
    elif strategy == "反馬丁策略":
        step = st.session_state.martingale_step
        return base_bet * (2 ** step)
    else:
        return st.session_state.bet_amount

current_bet = calc_bet_amount(strategy)

# ===== 顯示資訊 =====
cols = st.columns(5)
cols[0].metric("已輸入牌數", len(st.session_state.history))
cols[1].metric("局數", f"#{st.session_state.total_games}")
acc = (st.session_state.win_games / st.session_state.total_games * 100) if st.session_state.total_games else 0
cols[2].metric("模型準確率", f"{acc:.1f}%")
cols[3].metric("當前本金", f"${st.session_state.balance}")
cols[4].metric("預測下一局", prediction)

st.markdown(f"### 本局下注金額: ${current_bet}")

st.markdown("<h4 style='text-align:center; color:#FF6F61;'>🔴 點擊以下按鈕輸入本局結果</h4>", unsafe_allow_html=True)

# ===== 輸入本局結果 =====
col1, col2, col3 = st.columns(3)
clicked = None
with col1:
    if st.button("🟦 閒 (P)", use_container_width=True):
        clicked = "P"
with col2:
    if st.button("🟩 和 (T)", use_container_width=True):
        clicked = "T"
with col3:
    if st.button("🟥 莊 (B)", use_container_width=True):
        clicked = "B"

# ===== 更新狀態與勝負判定 =====
def update_after_result(result):
    st.session_state.history.append(result)
    st.session_state.total_games += 1

    # 先扣除下注金額
    st.session_state.balance -= current_bet

    win = False

    # 和局退還本金
    if result == "T":
        st.session_state.balance += current_bet
    else:
        # 判斷勝負：根據預測結果決定下注方
        # 預測格式：閒 (P) (xx.x%)
        predicted_side = prediction.split(" ")[0]  # 取出「閒」「莊」「和」
        # 對應下注方判定
        if predicted_side == "閒" and result == "P":
            win = True
        elif predicted_side == "莊" and result == "B":
            win = True
        else:
            win = False

        if win:
            st.session_state.win_games += 1
            if result == "P":
                st.session_state.balance += current_bet * 2  # 閒贏1倍
            elif result == "B":
                st.session_state.balance += int(current_bet * 1.95)  # 莊贏需扣5%抽水

    # 策略下注更新
    if strategy == "1326策略":
        if win:
            st.session_state.count_1326 = 0
        else:
            st.session_state.count_1326 += 1
            if st.session_state.count_1326 > 3:
                st.session_state.count_1326 = 0
    elif strategy == "馬丁策略":
        if win:
            st.session_state.martingale_step = 0
        else:
            st.session_state.martingale_step += 1
    elif strategy == "反馬丁策略":
        if win:
            st.session_state.martingale_step += 1
        else:
            st.session_state.martingale_step = 0

if clicked:
    update_after_result(clicked)
    st.experimental_rerun()

# ===== 繪製走勢圖 =====
if st.session_state.history:
    st.markdown("### 📈 莊 / 閒 / 和 走勢圖")
    fig, ax = plt.subplots(figsize=(10, 3))
    mapping = {"P": 1, "T": 0, "B": -1}
    y = [mapping[i] for i in st.session_state.history]
    ax.plot(y, marker='o', color='deepskyblue')
    ax.axhline(0, color='white', linestyle='--', linewidth=0.5)
    ax.set_yticks([-1,0,1])
    ax.set_yticklabels(["莊","和","閒"])
    ax.set_xlabel("局數")
    ax.set_title("走勢圖")
    ax.grid(True, alpha=0.2)
    st.pyplot(fig)

# ===== 顯示完整歷史 =====
with st.expander("📜 查看完整輸入歷史"):
    st.write(st.session_state.history)

# ===== 重置按鈕 =====
if st.button("🧹 重置資料"):
    st.session_state.history = []
    st.session_state.total_games = 0
    st.session_state.win_games = 0
    st.session_state.balance = 1000
    st.session_state.martingale_step = 0
    st.session_state.count_1326 = 0
    st.session_state.bet_amount = 100
    st.success("資料已重置")

st.caption("© 2025 AI 百家樂進階預測系統 | 黑色極簡策略版")
