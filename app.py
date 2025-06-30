import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# 頁面設定
st.set_page_config(page_title="AI 百家樂全自動預測分析", page_icon="🎰", layout="centered")

# 深色主題 CSS
st.markdown(
    """
    <style>
    body, .main {
        background-color: #121212 !important;
        color: #eee !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #FF6F61 !important;
    }
    div.stButton > button {
        border-radius: 8px;
        border: 1px solid #FF6F61;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        filter: brightness(1.2);
    }
    .btn-win > button {
        background-color: #2ecc71 !important;  /* 綠色 */
        color: #121212 !important;
    }
    .btn-lose > button {
        background-color: #e74c3c !important;  /* 紅色 */
        color: #fff !important;
    }
    .btn-clear > button {
        background-color: #f39c12 !important;  /* 橘色 */
        color: #121212 !important;
    }
    input, textarea, .stTextInput>div>input {
        background-color: #222 !important;
        color: #eee !important;
        border: 1px solid #FF6F61 !important;
        border-radius: 6px;
        padding: 6px 10px;
    }
    div[data-testid="metric-container"] {
        background-color: #222 !important;
        border-radius: 8px;
        padding: 10px;
        color: #eee !important;
        font-weight: 600;
    }
    section.block-container {
        padding: 1.5rem 2rem 2rem 2rem;
    }
    .box {
        border: 1px solid #FF6F61;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #1e1e1e;
    }
    table {
        color: #eee;
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        border: 1px solid #FF6F61;
        padding: 8px;
        text-align: center;
    }
    th {
        background-color: #FF6F61;
        color: #121212;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 激活碼驗證 ---
PASSWORD = "aa17888"  # 這裡改成你想要的新密碼

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
            '預設籌碼': {'win_amount': 100, 'lose_amount': 100},
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

# --- 籌碼組管理區 ---
with st.container():
    st.markdown('<div class="box"><h3>🎲 籌碼組管理</h3></div>', unsafe_allow_html=True)

    with st.expander("➕ 新增籌碼組", expanded=False):
        if 'new_chip_name' not in st.session_state:
            st.session_state.new_chip_name = ""
        if 'new_win' not in st.session_state:
            st.session_state.new_win = 100
        if 'new_lose' not in st.session_state:
            st.session_state.new_lose = 100

        new_name = st.text_input("籌碼組名稱", max_chars=20, key="new_chip_name")
        new_win = st.number_input("勝利金額", min_value=1, max_value=1_000_000, value=st.session_state.new_win, step=1000, key="new_win")
        new_lose = st.number_input("失敗金額", min_value=1, max_value=1_000_000, value=st.session_state.new_lose, step=1000, key="new_lose")
        if st.button("新增籌碼組"):
            if new_name.strip() == "":
                st.warning("籌碼組名稱不可為空")
            elif new_name in st.session_state.chip_sets:
                st.warning("此籌碼組名稱已存在")
            else:
                st.session_state.chip_sets[new_name] = {'win_amount': new_win, 'lose_amount': new_lose}
                st.session_state.current_chip_set = new_name
                st.success(f"成功新增籌碼組：{new_name}")
                st.session_state.new_chip_name = ""
                st.session_state.new_win = 100
                st.session_state.new_lose = 100
                st.experimental_rerun()

    chip_names = list(st.session_state.chip_sets.keys())
    current_set = st.selectbox("選擇籌碼組", chip_names, index=chip_names.index(st.session_state.current_chip_set))
    st.session_state.current_chip_set = current_set

    col1, col2 = st.columns(2)
    with col1:
        win_input = st.number_input("勝利金額", min_value=1, max_value=1_000_000,
                                    value=st.session_state.chip_sets[current_set]['win_amount'], step=1000)
    with col2:
        lose_input = st.number_input("失敗金額", min_value=1, max_value=1_000_000,
                                     value=st.session_state.chip_sets[current_set]['lose_amount'], step=1000)

    st.session_state.chip_sets[current_set]['win_amount'] = win_input
    st.session_state.chip_sets[current_set]['lose_amount'] = lose_input

# --- 本局結果＋勝負一次輸入表單 ---
with st.container():
    st.markdown('<div class="box"><h3>🎮 本局結果與勝負一次確認</h3></div>', unsafe_allow_html=True)
    with st.form("round_result_form"):
        col1, col2 = st.columns(2)
        with col1:
            result = st.radio("選擇本局結果", options=["莊 (B)", "閒 (P)", "和 (T)"], horizontal=True)
        with col2:
            outcome = st.radio("勝負結果", options=["勝利", "失敗"], horizontal=True)

        submitted = st.form_submit_button("確認輸入")
        if submitted:
            result_map = {"莊 (B)": "B", "閒 (P)": "P", "和 (T)": "T"}
            res_code = result_map[result]

            st.session_state.history.append(res_code)
            st.session_state.total_games += 1
            if outcome == "勝利":
                st.session_state.win_games += 1
                st.session_state.total_profit += st.session_state.chip_sets[st.session_state.current_chip_set]['win_amount']
                st.success(f"本局結果 {result}，記錄勝利，獲利 +{st.session_state.chip_sets[st.session_state.current_chip_set]['win_amount']:,} 元")
            else:
                st.session_state.total_profit -= st.session_state.chip_sets[st.session_state.current_chip_set]['lose_amount']
                st.success(f"本局結果 {result}，記錄失敗，損失 -{st.session_state.chip_sets[st.session_state.current_chip_set]['lose_amount']:,} 元")

# --- 建議下注 ---
with st.container():
    h = st.session_state.history
    if len(h) >= 3:
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

# --- 清除資料與撤銷上一筆 ---
with st.container():
    st.markdown('<div class="box"><h3>🧹 資料操作</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("🧹 清除所有資料", key="clear_all", help="清除所有歷史和統計資料", type="secondary", use_container_width=True):
            for k in ['history', 'total_profit', 'total_games', 'win_games']:
                st.session_state[k] = [] if k == 'history' else 0
            st.success("所有資料已清除")
    with col2:
        if st.button("↩️ 撤銷上一筆紀錄", key="undo_last", help="撤銷最近一筆輸入的本局結果", type="secondary", use_container_width=True):
            if st.session_state.history:
                last = st.session_state.history.pop()
                st.session_state.total_games -= 1
                # 注意：這裡暫時無法精確撤銷勝敗獲利，需更複雜的資料結構
                st.success(f"已撤銷最後一筆本局結果：{last}")
            else:
                st.info("無歷史紀錄可撤銷")

# --- 統計顯示 ---
with st.container():
    st.markdown('<div class="box"><h3>📊 統計資料</h3></div>', unsafe_allow_html=True)
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
    st.success(f"💰 累積獲利: {st.session_state.total_profit:,} 元 | 勝場數: {st.session_state.win_games} | 總場數: {st.session_state.total_games} | 勝率: {win_rate:.1f}%")

# --- 走勢圖 ---
with st.container():
    st.markdown('<div class="box"><h3>📈 近 30 局走勢圖</h3></div>', unsafe_allow_html=True)
    h = st.session_state.history
    if not h:
        st.warning("無資料可繪製走勢圖")
    else:
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
        st.caption("說明：Y 軸數值代表結果，0=閒，0.5=和，1=莊，方便觀察連續趨勢。")

# --- 歷史紀錄表格 ---
with st.container():
    st.markdown('<div class="box"><h3>🕒 歷史紀錄</h3></div>', unsafe_allow_html=True)
    if st.session_state.history:
        df = pd.DataFrame({
            "局數": list(range(1, len(st.session_state.history) + 1)),
            "結果": st.session_state.history
        })
        df["結果"] = df["結果"].map({"B": "莊", "P": "閒", "T": "和"})
        st.table(df)
    else:
        st.info("尚無紀錄，請開始輸入資料")

st.caption("© 2025 AI 百家樂全自動預測分析系統 | 手機友善優化版")
