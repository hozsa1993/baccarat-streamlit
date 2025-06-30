import streamlit as st

# 頁面設定
st.set_page_config(page_title="AI 百家樂預測分析", page_icon="🎰", layout="centered")

# 美化 CSS
st.markdown("""
<style>
body, .main {
    background-color: #0f0f0f !important;
    color: #e0e0e0 !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
h1, h2, h3, h4 {
    color: #FF6F61 !important;
    font-weight: 700;
}
div.stButton > button {
    background-color: #1f1f1f !important;
    color: #FF6F61 !important;
    border-radius: 12px;
    border: 1px solid #FF6F61;
    font-weight: 700;
    padding: 0.6em 1em;
    transition: 0.3s ease;
}
div.stButton > button:hover {
    background-color: #FF6F61 !important;
    color: #0f0f0f !important;
    transform: scale(1.05);
}
input, textarea, .stTextInput input {
    background-color: #222 !important;
    color: #eee !important;
    border-radius: 8px;
    border: 1px solid #FF6F61 !important;
    padding: 0.5em;
}
div[data-testid="metric-container"] {
    background-color: #222 !important;
    border-radius: 12px;
    padding: 10px;
    margin: 8px 0;
    color: #eee !important;
    border: 1px solid #444;
}
hr {
    border-top: 1px solid #444;
    margin-top: 30px;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# 激活碼驗證
PASSWORD = "aa17888"
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

# 初始化狀態
def init_state():
    defaults = {
        'history': [],
        'total_profit': 0,
        'total_games': 0,
        'win_games': 0,
        'chip_set': {'win_amount': 100, 'lose_amount': 100}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

INCREMENT = 100  # 勝負後自動增加/減少金額

st.header("🎮 本局結果與勝負一次確認")

chip_set = st.session_state.chip_set

# 選擇本局結果
result_option = st.selectbox("選擇本局結果", ["請選擇", "莊 (B)", "閒 (P)", "和 (T)"], index=0)

# 勝負選擇
outcome_option = st.radio("本局輸贏", ["請選擇", "勝利", "失敗"], index=0, horizontal=True)

# 顯示當前勝負金額
st.markdown(f"""
<b>勝利金額：</b> {chip_set['win_amount']} 元 &nbsp;&nbsp;&nbsp;&nbsp;
<b>失敗金額：</b> {chip_set['lose_amount']} 元<br>
<b>勝負金額會自動根據結果調整，每次變動：{INCREMENT} 元 (最大 1,000,000 元)
""", unsafe_allow_html=True)

# 確認按鈕
if st.button("確認本局結果"):
    if result_option == "請選擇" or outcome_option == "請選擇":
        st.warning("請先選擇本局結果與輸贏狀態")
    else:
        side_map = {"莊 (B)": "B", "閒 (P)": "P", "和 (T)": "T"}
        side = side_map[result_option]

        if outcome_option == "勝利":
            st.session_state.history.append(side)
            st.session_state.total_games += 1
            st.session_state.win_games += 1
            st.session_state.total_profit += chip_set['win_amount']

            # 自動調整金額
            chip_set['win_amount'] = min(1_000_000, chip_set['win_amount'] + INCREMENT)
            chip_set['lose_amount'] = max(100, chip_set['lose_amount'] - INCREMENT//2)

            st.success(f"記錄勝利，增加 {chip_set['win_amount'] - INCREMENT} 元勝利金額，失敗金額微降")
        else:
            st.session_state.history.append(side)
            st.session_state.total_games += 1
            st.session_state.total_profit -= chip_set['lose_amount']

            chip_set['lose_amount'] = min(1_000_000, chip_set['lose_amount'] + INCREMENT)
            chip_set['win_amount'] = max(100, chip_set['win_amount'] - INCREMENT//2)

            st.error(f"記錄失敗，扣除 {chip_set['lose_amount'] - INCREMENT} 元失敗金額，勝利金額微降")

        # 自動刷新頁面避免重複提交
        st.experimental_rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# --- 2️⃣ 統計資料 ---
st.header("📊 統計資料")
h = st.session_state.history
banker = h.count("B")
player = h.count("P")
tie = h.count("T")
total = len(h)
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
st.success(f"💰 累積獲利: {st.session_state.total_profit:,} 元 | 勝場: {st.session_state.win_games} | 總場: {st.session_state.total_games} | 勝率: {win_rate:.1f}%")

st.markdown("<hr>", unsafe_allow_html=True)

# --- 3️⃣ 歷史紀錄 + 三寶路建議 ---
st.header("🕒 歷史紀錄")
if h:
    st.text_area("歷史輸入記錄", " ".join(h), height=120, disabled=True)
else:
    st.info("尚無紀錄，請開始輸入資料")

st.markdown("<br>", unsafe_allow_html=True)

st.header("🪄 三寶路建議")
h4 = h[-4:]
suggestion = "資料不足，請先輸入資料"
if len(h4) >= 3:
    if h4.count("T") >= 2:
        suggestion = "近期和局較多，建議觀望"
    elif all(x == "B" for x in h4[-3:]):
        suggestion = "近期連續莊，建議下注【莊】"
    elif all(x == "P" for x in h4[-3:]):
        suggestion = "近期連續閒，建議下注【閒】"
    else:
        suggestion = "無明顯趨勢，建議觀望或小注"
st.info(f"🎯 {suggestion}")

st.markdown("<hr>", unsafe_allow_html=True)

# --- 🎲 籌碼管理（下拉選單） ---
st.header("🎲 籌碼管理（下拉選單）")

win_options = [i for i in range(100, 1_000_001, 1000)]
lose_options = [i for i in range(100, 1_000_001, 1000)]

col1, col2 = st.columns(2)
with col1:
    new_win = st.selectbox(
        "勝利金額",
        options=win_options,
        index=win_options.index(chip_set['win_amount']) if chip_set['win_amount'] in win_options else 0,
        format_func=lambda x: f"{x:,} 元"
    )
with col2:
    new_lose = st.selectbox(
        "失敗金額",
        options=lose_options,
        index=lose_options.index(chip_set['lose_amount']) if chip_set['lose_amount'] in lose_options else 0,
        format_func=lambda x: f"{x:,} 元"
    )

chip_set['win_amount'] = new_win
chip_set['lose_amount'] = new_lose

st.markdown(f"""
當前設定：勝利金額 {chip_set['win_amount']:,} 元，失敗金額 {chip_set['lose_amount']:,} 元。
""")

# --- 清除資料按鈕 ---
st.markdown("<hr>", unsafe_allow_html=True)
if st.button("🧹 清除所有資料", use_container_width=True):
    for k in ['history', 'total_profit', 'total_games', 'win_games']:
        st.session_state[k] = [] if k == 'history' else 0
    st.session_state.chip_set = {'win_amount': 100, 'lose_amount': 100}
    st.success("已清除所有資料並重置籌碼")

st.caption("© 2025 AI 百家樂全自動預測分析系統 | 人性化極速版")
