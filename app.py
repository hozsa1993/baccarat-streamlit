import streamlit as st
import matplotlib.pyplot as plt

# 頁面設定
st.set_page_config(page_title="AI 百家樂全自動預測分析", page_icon="🎰", layout="centered")

# --- 激活碼驗證 ---
PASSWORD = "baccarat2025"  # 你可以改成自己想要的密碼

if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

if not st.session_state.access_granted:
    st.markdown("<h1 style='text-align:center; color:#FF6F61;'>請輸入激活碼以使用系統</h1>", unsafe_allow_html=True)
    password_input = st.text_input("激活碼 (密碼)", type="password", placeholder="請輸入激活碼")
    if st.button("確認"):
        if password_input == PASSWORD:
            st.session_state.access_granted = True
            st.experimental_rerun()
        else:
            st.error("激活碼錯誤，請重新輸入")
    st.stop()

# --- 初始化狀態 ---
def init_state():
    defaults = {
        'history': [],
        'total_profit': 0,
        'total_games': 0,
        'win_games': 0,
        'chip_sets': {
            '預設籌碼': {'win_amount': 10000, 'lose_amount': 10000},
        },
        'current_chip_set': '預設籌碼',
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

st.markdown("""
<h1 style="text-align:center; color:#FF6F61;">🎲 AI 百家樂全自動預測分析</h1>
<p style="text-align:center; color:gray;">實時記錄、勝率分析、自動走勢提示與下注建議</p>
""", unsafe_allow_html=True)
st.divider()

# --- 籌碼組設定區 ---
st.markdown("### 🎲 多組籌碼設定與切換")

# 新增籌碼組
with st.expander("新增籌碼組"):
    new_name = st.text_input("籌碼組名稱", max_chars=20, placeholder="輸入新籌碼組名稱")
    new_win = st.number_input("勝利金額", min_value=1, max_value=1_000_000, value=10000, step=1000, key="new_win")
    new_lose = st.number_input("失敗金額", min_value=1, max_value=1_000_000, value=10000, step=1000, key="new_lose")
    if st.button("新增籌碼組"):
        if new_name.strip() == "":
            st.warning("籌碼組名稱不可為空")
        elif new_name in st.session_state.chip_sets:
            st.warning("此籌碼組名稱已存在")
        else:
            st.session_state.chip_sets[new_name] = {'win_amount': new_win, 'lose_amount': new_lose}
            st.session_state.current_chip_set = new_name  # 新增後自動切換
            st.success(f"成功新增籌碼組：{new_name}")
            st.experimental_rerun()

# 籌碼組切換
chip_names = list(st.session_state.chip_sets.keys())
current_set = st.selectbox("選擇籌碼組", chip_names, index=chip_names.index(st.session_state.current_chip_set))
st.session_state.current_chip_set = current_set

# 顯示及調整目前籌碼組金額
col1, col2 = st.columns(2)
with col1:
    win_input = st.number_input("勝利金額", min_value=1, max_value=1_000_000,
                                value=st.session_state.chip_sets[current_set]['win_amount'], step=1000)
with col2:
    lose_input = st.number_input("失敗金額", min_value=1, max_value=1_000_000,
                                 value=st.session_state.chip_sets[current_set]['lose_amount'], step=1000)

st.session_state.chip_sets[current_set]['win_amount'] = win_input
st.session_state.chip_sets[current_set]['lose_amount'] = lose_input

st.divider()

# --- 本局結果輸入 ---
st.markdown("### 🎮 輸入本局結果")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟥 莊 (B)", use_container_width=True):
        st.session_state.history.append("B")
        st.session_state.total_games += 1
        st.success("已加入莊局結果")
with col2:
    if st.button("🟦 閒 (P)", use_container_width=True):
        st.session_state.history.append("P")
        st.session_state.total_games += 1
        st.success("已加入閒局結果")
with col3:
    if st.button("🟩 和 (T)", use_container_width=True):
        st.session_state.history.append("T")
        st.session_state.total_games += 1
        st.success("已加入和局結果")

# --- 勝負確認 ---
st.markdown("### 💰 勝負確認")
col4, col5 = st.columns(2)
with col4:
    if st.button(f"✅ 確認勝利 (+{win_input:,})", use_container_width=True):
        if len(st.session_state.history) == 0:
            st.warning("請先輸入本局結果再確認勝負")
        else:
            st.session_state.total_profit += win_input
            st.session_state.win_games += 1
            st.success(f"已記錄勝利，增加 {win_input:,} 元")
with col5:
    if st.button(f"❌ 確認失敗 (-{lose_input:,})", use_container_width=True):
        if len(st.session_state.history) == 0:
            st.warning("請先輸入本局結果再確認勝負")
        else:
            st.session_state.total_profit -= lose_input
            st.success(f"已記錄失敗，扣除 {lose_input:,} 元")

if st.button("🧹 清除所有資料", use_container_width=True):
    for k in ['history', 'total_profit', 'total_games', 'win_games']:
        st.session_state[k] = [] if k == 'history' else 0
    st.success("所有資料已清除")

st.divider()

# --- 統計顯示 ---
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

    # 強化版下注建議（綜合多策略加權）
    sug = suggest_bet_combined()
    st.info(f"🎯 {sug}")

# 強化版下注建議演算法
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
        return "資料不足，暫無下注建議"

    total = len(h)
    banker_count = h.count("B")
    player_count = h.count("P")
    tie_count = h.count("T")

    # 歷史頻率比重 (0.4)
    total_float = float(total)
    freq_scores = {
        "B": banker_count / total_float,
        "P": player_count / total_float,
        "T": tie_count / total_float,
    }

    # 連續趨勢比重 (0.4)
    b_streak = longest_streak(h, "B")
    p_streak = longest_streak(h, "P")
    t_streak = longest_streak(h, "T")
    # 正規化連續長度（假設最大 5）
    streak_scores = {
        "B": min(b_streak, 5) / 5,
        "P": min(p_streak, 5) / 5,
        "T": min(t_streak, 5) / 5,
    }

    # 反轉策略比重 (0.2)
    reversal_scores = {"B":0, "P":0, "T":0}
    if total >= 4:
        last4 = h[-4:]
        if all(x == "B" for x in last4):
            reversal_scores["P"] = 1  # 建議下注閒
        elif all(x == "P" for x in last4):
            reversal_scores["B"] = 1  # 建議下注莊

    # 加權計算總分
    weights = {"freq": 0.4, "streak": 0.4, "reversal": 0.2}
    combined_scores = {}
    for k in ["B", "P", "T"]:
        combined_scores[k] = (
            freq_scores.get(k,0)*weights["freq"] +
            streak_scores.get(k,0)*weights["streak"] +
            reversal_scores.get(k,0)*weights["reversal"]
        )

    # 找出最高分下注建議
    max_key = max(combined_scores, key=combined_scores.get)
    max_score = combined_scores[max_key]

    if max_score < 0.3:
        return "趨勢不明，建議觀望"

    label_map = {"B": "莊 (B)", "P": "閒 (P)", "T": "和 (T)"}
    return f"綜合建議下注：{label_map[max_key]} (信心分數: {max_score:.2f})"

display_stats()
st.divider()

# --- 走勢圖 ---
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

# --- 歷史紀錄 ---
with st.expander("🕒 歷史紀錄 (點此展開/收合)"):
    if st.session_state.history:
        st.text_area("歷史輸入記錄", " ".join(st.session_state.history), height=120)
    else:
        st.info("尚無紀錄，請開始輸入資料")

st.caption("© 2025 AI 百家樂全自動預測分析系統 | 手機友善優化版")
