import streamlit as st

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

# 警示文字
st.markdown("<h4 style='text-align:center; color:#FF6F61;'>🔴 預測開始，請按荷官發牌順序輸入牌</h4>", unsafe_allow_html=True)

# 大按鈕區塊
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟦 閒", use_container_width=True):
        st.success("已記錄: 閒")
    st.markdown("<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col2:
    if st.button("🟩 和", use_container_width=True):
        st.success("已記錄: 和")
    st.markdown("<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col3:
    if st.button("🟥 莊", use_container_width=True):
        st.success("已記錄: 莊")
    st.markdown("<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)

# 小按鈕第一排
col4, col5, col6, col7 = st.columns(4)
with col4:
    if st.button("閒對", use_container_width=True):
        st.info("已記錄: 閒對")
    st.markdown("<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col5:
    if st.button("大", use_container_width=True):
        st.info("已記錄: 大")
    st.markdown("<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col6:
    if st.button("小", use_container_width=True):
        st.info("已記錄: 小")
    st.markdown("<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col7:
    if st.button("莊對", use_container_width=True):
        st.info("已記錄: 莊對")
    st.markdown("<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)

# 小按鈕第二排
col8, col9, col10 = st.columns(3)
with col8:
    if st.button("閒龍寶", use_container_width=True):
        st.info("已記錄: 閒龍寶")
    st.markdown("<div class='sub-text'>必勝率+0.0%</div>", unsafe_allow_html=True)
with col9:
    if st.button("幸運六", use_cont_
