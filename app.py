import streamlit as st

# 頁面設定
st.set_page_config(page_title="AI 百家樂預測分析", page_icon="🎰", layout="centered")

# 激活碼
PASSWORD = "aa17888"
if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

if not st.session_state.access_granted:
    pwd = st.text_input("請輸入激活碼", type="password", placeholder="請輸入激活碼")
    if st.button("確認"):
        if pwd == PASSWORD:
            st.session_state.access_granted = True
            st.experimental_rerun()
        else:
            st.error("激活碼錯誤，請重新輸入")
    st.stop()

# 初始化狀態
def init_state():
    if "history" not in st.session_state:
        st.session_state.history = []  # 歷史局結果（B/P/T）
    if "total_profit" not in st.session_state:
        st.session_state.total_profit = 0
    if "total_games" not in st.session_state:
        st.session_state.total_games = 0
    if "win_games" not in st.session_state:
        st.session_state.win_games = 0
    if "chip_sets" not in st.session_state:
        st.session_state.chip_sets = {
            "預設籌碼": {"win_amount": 100, "lose_amount": 100}
        }
    if "current_chip_set" not in st.session_state:
        st.session_state.current_chip_set = "預設籌碼"
    if "selected_result" not in st.session_state:
        st.session_state.selected_result = None
    if "selected_outcome" not in st.session_state:
        st.session_state.selected_outcome = None
init_state()

INCREMENT = 100
chip_sets = st.session_state.chip_sets
current_chip = chip_sets[st.session_state.current_chip_set]

st.title("🎰 AI 百家樂預測分析")

# --- 本局結果與勝負一次確認 (第一區) ---
st.header("🎮 本局結果與勝負一次確認")

st.markdown("**選擇本局結果（莊、閒、和）：**")
col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    if st.button("🟥 莊 (B)"):
        st.session_state.selected_result = "B"
with col_r2:
    if st.button("🟦 閒 (P)"):
        st.session_state.selected_result = "P"
with col_r3:
    if st.button("🟩 和 (T)"):
        st.session_state.selected_result = "T"

if st.session_state.selected_result:
    st.info(f"已選擇本局結果：{st.session_state.selected_result}")

st.markdown("**選擇本局輸贏狀態：**")
col_o1, col_o2, col_o3 = st.columns(3)
with col_o1:
    if st.button("✅ 勝利"):
        st.session_state.selected_outcome = "win"
with col_o2:
    if st.button("❌ 失敗"):
        st.session_state.selected_outcome = "lose"
with col_o3:
    if st.button("➖ 和局"):
        st.session_state.selected_outcome = "tie"

if st.session_state.selected_outcome:
    txt_map = {"win": "勝利", "lose": "失敗", "tie": "和局"}
    st.info(f"已選擇本局輸贏狀態：{txt_map[st.session_state.selected_outcome]}")

st.markdown("---")

if st.button("提交本局結果"):
    if st.session_state.selected_result is None:
        st.warning("請先選擇本局結果")
    elif st.session_state.selected_outcome is None:
        st.warning("請先選擇本局輸贏狀態")
    else:
        side = st.session_state.selected_result
        outcome = st.session_state.selected_outcome
        st.session_state.history.append(side)
        st.session_state.total_games += 1

        # 自動調整勝敗金額
        if outcome == "win":
            st.session_state.win_games += 1
            st.session_state.total_profit += current_chip["win_amount"]
            # 勝利後勝利金額加，失敗金額微減
            current_chip["win_amount"] = min(100_0000, current_chip["win_amount"] + INCREMENT)
            current_chip["lose_amount"] = max(100, current_chip["lose_amount"] - INCREMENT // 2)
            st.success(f"勝利！累積獲利 +{current_chip['win_amount'] - INCREMENT} 元")
        elif outcome == "lose":
            st.session_state.total_profit -= current_chip["lose_amount"]
            # 失敗後失敗金額加，勝利金額微減
            current_chip["lose_amount"] = min(100_0000, current_chip["lose_amount"] + INCREMENT)
            current_chip["win_amount"] = max(100, current_chip["win_amount"] - INCREMENT // 2)
            st.error(f"失敗！累積損失 -{current_chip['lose_amount'] - INCREMENT} 元")
        else:  # 和局
            st.info("和局，籌碼金額不變")

        # 重置選擇
        st.session_state.selected_result = None
        st.session_state.selected_outcome = None
        st.experimental_rerun()

st.markdown("---")

# --- 統計資料 (第二區) ---
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
    st.info(f"勝率｜莊: {banker / total * 100:.1f}% | 閒: {player / total * 100:.1f}% | 和: {tie / total * 100:.1f}%")
else:
    st.warning("尚無資料，請輸入結果")

win_rate = (st.session_state.win_games / st.session_state.total_games * 100) if st.session_state.total_games else 0
st.success(f"💰 累積獲利: {st.session_state.total_profit:,} 元 | 勝場: {st.session_state.win_games} | 總場: {st.session_state.total_games} | 勝率: {win_rate:.1f}%")

# 三寶路建議
st.markdown("---")
st.subheader("🪄 三寶路建議")
last4 = h[-4:]
suggestion = "資料不足，請先輸入資料"
if len(last4) >= 3:
    if last4.count("T") >= 2:
        suggestion = "近期和局較多，建議觀望"
    elif all(x == "B" for x in last4[-3:]):
        suggestion = "近期連續莊，建議下注【莊】"
    elif all(x == "P" for x in last4[-3:]):
        suggestion = "近期連續閒，建議下注【閒】"
    else:
        suggestion = "無明顯趨勢，建議觀望或小注"
st.info(f"🎯 {suggestion}")

# --- 歷史紀錄 (第三區) ---
st.markdown("---")
st.header("🕒 歷史紀錄")
if h:
    st.text_area("歷史輸入記錄", " ".join(h), height=120, disabled=True)
else:
    st.info("尚無紀錄，請開始輸入資料")

# --- 籌碼管理(最後區) ---
st.markdown("---")
st.header("🎲 籌碼管理")

chip_names = list(chip_sets.keys())
current_name = st.selectbox("選擇籌碼組", chip_names, index=chip_names.index(st.session_state.current_chip_set))
st.session_state.current_chip_set = current_name
current_chip = chip_sets[current_name]

# 勝敗金額顯示，不能手動改，只能看
st.markdown(f"目前勝利金額：**{current_chip['win_amount']:,}** 元（最大 100萬）")
st.markdown(f"目前失敗金額：**{current_chip['lose_amount']:,}** 元（最大 100萬）")

# 清除資料
if st.button("🧹 清除所有資料", use_container_width=True):
    for k in ['history', 'total_profit', 'total_games', 'win_games']:
        st.session_state[k] = [] if k == 'history' else 0
    # 重置籌碼組金額
    for k in chip_sets.keys():
        chip_sets[k] = {"win_amount": 100, "lose_amount": 100}
    st.success("已清除所有資料並重置籌碼")

st.caption("© 2025 AI 百家樂預測分析系統 | 人性化版")
