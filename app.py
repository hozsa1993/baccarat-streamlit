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
    max_streak = max(b_streak, p_streak, t_streak)
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

    # 翻譯中文
    label_map = {"B": "莊 (B)", "P": "閒 (P)", "T": "和 (T)"}
    return f"綜合建議下注：{label_map[max_key]} (信心分數: {max_score:.2f})"

# 在原本下注建議顯示改成：
sug = suggest_bet_combined()
st.info(f"🎯 {sug}")
