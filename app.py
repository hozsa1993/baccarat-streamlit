import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# ===== 頁面設定 =====
st.set_page_config(page_title="AI 百家樂純機器學習預測系統", page_icon="🎰", layout="centered")

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
if "history" not in st.session_state or not isinstance(st.session_state.history, list):
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

# ===== 編碼歷史資料 =====
def encode_result(res):
    mapping = {'P':0, 'B':1, 'T':2}
    return [mapping.get(r, -1) for r in res]

# ===== 建立特徵與標籤 =====
def create_dataset(history, window=3):
    data = encode_result(history)
    X, y = [], []
    for i in range(len(data) - window):
        X.append(data[i:i+window])
        y.append(data[i+window])
    return np.array(X), np.array(y)

# ===== ML 預測 =====
def ml_predict(history, window=3):
    if len(history) < window + 1:
        return "資料不足無法預測"
    X, y = create_dataset(history, window)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    last_seq = np.array(encode_result(history[-window:])).reshape(1, -1)
    pred = model.predict(last_seq)[0]
    mapping = {0:'閒 (P)', 1:'莊 (B)', 2:'和 (T)'}
    return mapping.get(pred, "未知")

ml_prediction = ml_predict(st.session_state.history)

# ===== 策略下注金額計算 =====
def calc_bet_amount(strategy):
    base_bet = st.session_state.bet_amount
    if strategy == "1326策略":
        seq = [1,3,2,6]
        step = st.session_state.count_1326
        if step >= len(seq):
            step = 0
            st.session_state.count_1326 = 0
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
cols[4].metric("機器學習預測下一局", ml_prediction)

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
    st.session_state.balance -= current_bet
    win = False
    if result == "T":
        st.session_state.balance += current_bet
    else:
        predicted_side = ml_prediction.split(" ")[0]
        if predicted_side == "閒" and result == "P":
            win = True
        elif predicted_side == "莊" and result == "B":
            win = True
        else:
            win = False
        if win:
            st.session_state.win_games += 1
            if result == "P":
                st.session_state.balance += current_bet * 2
            elif result == "B":
                st.session_state.balance += int(current_bet * 1.95)
    # 策略下注更新
    if strategy == "1326策略":
        if win:
            st.session_state.count_1326 = 0
        else:
            st.session_state.count_1326 += 1
            if st.session_state.count_1326 >= 4:
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
    try:
        st.text(st.session_state.history)
    except Exception as e:
        st.error(f"顯示歷史錯誤: {e}")
        st.write(str(st.session_state.history))

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

st.caption("© 2025 AI 百家樂純機器學習預測系統 | 黑色極簡策略版")
