import streamlit as st
import matplotlib.pyplot as plt

# 頁面設定
st.set_page_config(page_title="AI 百家樂預測分析", page_icon="🎰", layout="centered")

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

# --- 初始化 ---
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

# 統計更新函式
def add_history(result):
    st.session_state.history.append(result)
    st.session_state.total_games += 1
    if result == "B":
        st.session_state.count_B += 1
    elif result == "P":
        st.session_state.count_P += 1
    elif result == "T":
        st.session_state.count_T += 1

def update_result(win: bool):
    chip = st.session_state.chip_sets[st.session_state.current_chip_set]
    if win:
        st.session_state.total_profit += chip["win_amount"]
        st.session_state.win_games += 1
    else:
        st.session_state.total_profit -= chip["lose_amount"]

# 重置資料
def reset_all():
    st.session_state.history = []
    st.session_state.total_profit = 0
    st.session_state.total_games = 0
    st.session_state.win_games = 0
    st.session_state.count_B = 0
    st.session_state.count_P = 0
    st.session_state.count_T = 0

# UI - 輸入本局結果
st.markdown("<h1 style='text-align:center; color:#FF6F61;'>🎲 AI 百家樂全自動預測</h1>", unsafe_allow_html=True)
st.divider()

st.subheader("🎮 輸入本局結果")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟥 莊 (B)", use_container_width=True):
        add_history("B")
with col2:
    if st.button("🟦 閒 (P)", use_container_width=True):
        add_history("P")
with col3:
    if st.button("🟩 和 (T)", use_container_width=True):
        add_history("T")
st.divider()

# 勝負確認
current_chip = st.session_state.chip_sets[st.session_state.current_chip_set]
win_amount = current_chip["win_amount"]
lose_amount = current_chip["lose_amount"]

st.subheader("💰 勝負確認")
col1, col2 = st.columns(2)
with col1:
    if st.button(f"✅ 勝利 (+{win_amount:,})", use_container_width=True):
        update_result(True)
with col2:
    if st.button(f"❌ 失敗 (-{lose_amount:,})", use_container_width=True):
        update_result(False)

if st.button("🧹 清除資料", use_container_width=True):
    reset_all()
    st.success("已清除所有資料")
    st.experimental_rerun()
st.divider()

# 下注建議（放統計資料前）
def longest_streak(seq, char):
    max_streak = streak = 0
    for c in seq:
        if c == char:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak

def suggest_bet_combined():
    h = st.session_state.history
    if len(h) < 5:
        return "資料不足，暫無建議"

    total = len(h)
    b = st.session_state.count_B / total
    p = st.session_state.count_P / total
    t = st.session_state.count_T / total

    bs = min(longest_streak(h, "B"), 5)/5
    ps = min(longest_streak(h, "P"), 5)/5
    ts = min(longest_streak(h, "T"), 5)/5

    rev = {"B":0,"P":0,"T":0}
    if total >= 4:
        last4 = h[-4:]
        if all(x=="B" for x in last4): rev["P"]=1
        if all(x=="P" for x in last4): rev["B"]=1

    score = {k: v*0.4 + s*0.4 + rev[k]*0.2 for k,v,s in zip(["B","P","T"], [b,p,t], [bs,ps,ts])}
    top = max(score, key=score.get)
    if score[top]<0.3:
        return "趨勢不明，建議觀望"
    mapping = {"B":"莊 (B)","P":"閒 (P)","T":"和 (T)"}
    return f"建議下注：{mapping[top]} (信心 {score[top]:.2f})"

st.info(f"🎯 {suggest_bet_combined()}")

# 統計資料顯示
def display_stats():
    banker = st.session_state.count_B
    player = st.session_state.count_P
    tie = st.session_state.count_T
    total = st.session_state.total_games
    win_games = st.session_state.win_games
    total_profit = st.session_state.total_profit
    win_rate = (win_games / total * 100) if total else 0

    st.subheader("📊 統計資料")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("莊 (B)", banker)
    col2.metric("閒 (P)", player)
    col3.metric("和 (T)", tie)
    col4.metric("總局數", total)

    if total > 0:
        st.info(f"勝率｜莊: {banker/total*100:.1f}% | 閒: {player/total*100:.1f}% | 和: {tie/total*100:.1f}%")

    st.success(f"💰 獲利: {total_profit:,} 元 | 勝場: {win_games} | 總場: {total} | 勝率: {win_rate:.1f}%")

display_stats()
st.divider()

# 走勢圖
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

# 籌碼設定（放最底）
st.subheader("🎲 籌碼設定 (簡易切換)")
chip_names = list(st.session_state.chip_sets.keys())
selected_chip = st.selectbox("選擇籌碼組", chip_names, index=chip_names.index(st.session_state.current_chip_set))
st.session_state.current_chip_set = selected_chip

st.write(f"💰 勝利金額: {st.session_state.chip_sets[selected_chip]['win_amount']:,} 元")
st.write(f"💸 失敗金額: {st.session_state.chip_sets[selected_chip]['lose_amount']:,} 元")

with st.expander("➕ 新增籌碼組"):
    new_name = st.text_input("名稱", max_chars=20)

    # 建立選項列表，100到1000000，步進100
    amount_options = list(range(100, 1_000_001, 100))

    default_win_index = amount_options.index(100)
    default_lose_index = amount_options.index(100)

    new_win = st.selectbox("勝利金額", amount_options, index=default_win_index)
    new_lose = st.selectbox("失敗金額", amount_options, index=default_lose_index)

    if st.button("新增"):
        if new_name.strip() and new_name not in st.session_state.chip_sets:
            st.session_state.chip_sets[new_name] = {"win_amount": new_win, "lose_amount": new_lose}
            st.session_state.current_chip_set = new_name
            st.success(f"已新增：{new_name}")
            st.experimental_rerun()
        else:
            st.warning("名稱不可空白或重複")

st.caption("© 2025 AI 百家樂全自動預測分析系統 | 手機友善優化版")
