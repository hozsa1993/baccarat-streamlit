import streamlit as st
import streamlit.components.v1 as components

# 頁面設定
st.set_page_config(page_title="AI 百家樂預測分析", page_icon="🎰", layout="centered")

# 黑色主題 + 美化 CSS
st.markdown(
    """
    <style>
    body, .main {
        background-color: #0f0f0f !important;
        color: #e0e0e0 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #FF6F61 !important;
        font-weight: 700;
    }
    div.stButton > button {
        background-color: #1f1f1f !important;
        color: #FF6F61 !important;
        border-radius: 12px;
        border: 1px solid #FF6F61;
        font-weight: bold;
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
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    hr {
        border-top: 1px solid #444;
        margin-top: 30px;
        margin-bottom: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# 🎮 本局結果與勝負一次確認
st.header("🎮 本局結果與勝負一次確認")
INCREMENT = 100
chip_set = st.session_state.chip_set

st.markdown(f"""
<b>🎲 當前勝利金額：</b> {chip_set['win_amount']} 元 | 
<b>❌ 當前失敗金額：</b> {chip_set['lose_amount']} 元 <br>
<b>⚙️ 勝負後自動增加：</b> {INCREMENT} 元
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

def record_result(side, outcome, label):
    st.session_state.history.append(side)
    st.session_state.total_games += 1

    if outcome == "win":
        st.session_state.win_games += 1
        st.session_state.total_profit += chip_set['win_amount']
        chip_set['win_amount'] = min(1_000_000, chip_set['win_amount'] + INCREMENT)
        st.success(f"✅ 記錄：{label} 勝 +{chip_set['win_amount'] - INCREMENT} 元 → 新勝利金額 {chip_set['win_amount']} 元")
    else:
        st.session_state.total_profit -= chip_set['lose_amount']
        chip_set['lose_amount'] = min(1_000_000, chip_set['lose_amount'] + INCREMENT)
        st.error(f"❌ 記錄：{label} 負 -{chip_set['lose_amount'] - INCREMENT} 元 → 新失敗金額 {chip_set['lose_amount']} 元")

with col1:
    st.button("🟥 莊 勝", use_container_width=True, on_click=record_result, args=("B", "win", "莊"))
    st.button("🟥 莊 負", use_container_width=True, on_click=record_result, args=("B", "lose", "莊"))
with col2:
    st.button("🟦 閒 勝", use_container_width=True, on_click=record_result, args=("P", "win", "閒"))
    st.button("🟦 閒 負", use_container_width=True, on_click=record_result, args=("P", "lose", "閒"))
with col3:
    st.button("🟩 和 勝", use_container_width=True, on_click=record_result, args=("T", "win", "和"))
    st.button("🟩 和 負", use_container_width=True, on_click=record_result, args=("T", "lose", "和"))

st.markdown("<hr>", unsafe_allow_html=True)

# 📊 統計資料
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

# 🪄 三寶路建議
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

# 🕒 歷史紀錄
st.header("🕒 歷史紀錄")
if h:
    st.text_area("歷史輸入記錄", " ".join(h), height=100)
else:
    st.info("尚無紀錄，請開始輸入資料")

if st.button("🧹 清除所有資料", use_container_width=True):
    for k in ['history', 'total_profit', 'total_games', 'win_games']:
        st.session_state[k] = [] if k == 'history' else 0
    st.session_state.chip_set = {'win_amount': 100, 'lose_amount': 100}
    st.success("已清除所有資料並重置籌碼")

st.markdown("<hr>", unsafe_allow_html=True)

# 🎲 籌碼管理（極簡）
st.header("🎲 籌碼管理（極簡）")
st.markdown(f"""
<b>💰 當前勝利金額：</b> {chip_set['win_amount']} 元<br>
<b>❌ 當前失敗金額：</b> {chip_set['lose_amount']} 元<br>
<b>⚙️ 勝負後自動增加：</b> {INCREMENT} 元（上限 1,000,000）
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 重置金額為 100 元", use_container_width=True):
        chip_set['win_amount'] = 100
        chip_set['lose_amount'] = 100
        st.success("已重置勝利與失敗金額為 100 元")
with col2:
    if st.button("⬆️ 設為 1,000,000 元", use_container_width=True):
        chip_set['win_amount'] = 1_000_000
        chip_set['lose_amount'] = 1_000_000
        st.success("已將金額設為 1,000,000 元")

st.caption("© 2025 AI 百家樂全自動預測分析系統 | 手機友善極速版")
