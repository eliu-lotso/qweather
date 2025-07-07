from datetime import datetime
from zoneinfo import ZoneInfo
from services.doubao_ai import call_doubao_ai

def build_summary(data):
    lines = []

    for city, content in data.items():
        if city == "warnings":
            continue

        hourly = content.get("hourly", [])
        block1 = []
        block2 = []
        temp_all = []

        for entry in hourly:
            dt = datetime.fromisoformat(entry["fxTime"]).astimezone(ZoneInfo("Asia/Taipei"))
            hour = dt.hour
            temp = int(entry["temp"])
            temp_all.append(temp)

            if 9 <= hour <= 15:
                block1.append((entry["text"], temp))
            elif 16 <= hour <= 22:
                block2.append((entry["text"], temp))

        def summarize_block(block):
            if not block:
                return "无数据", "?"
            texts = [e[0] for e in block]
            temps = [e[1] for e in block]
            main_text = max(set(texts), key=texts.count)
            return main_text, f"{min(temps)} ~ {max(temps)}℃"

        text1, range1 = summarize_block(block1)
        text2, range2 = summarize_block(block2)
        #full_range = f"{min(temp_all)} ~ {max(temp_all)}℃" if temp_all else "?"
        lines.append(f"【{city}】今日天气简要：09:00~15:00 {text1}（{range1}），16:00~22:00 {text2}（{range2})")
        #lines.append(f"🌡️ 全日气温范围：{full_range}")
        lines.append("")

    for city, content in data.items():
        if city == "warnings":
            continue
        lines.append(f"📅 {city} 一周天气简要：")
        for day in content["weekly"][:2]:
            lines.append(f"- {day['fxDate']}: {day['textDay']} ~ {day['textNight']}")
        lines.append("")

    # ✅ 天气预警
    alerts = data.get("warnings", [])
    if alerts:
        alert_texts = []
        for alert in alerts:
            city = alert.get("city", "未知地区")
            alert_texts.append(f"[{city}] {alert['title']}: {alert['text']}")
        all_alerts_text = "\n".join(alert_texts)
        # 调用豆包AI进行摘要
        try:
            ai_summary = call_doubao_ai(all_alerts_text)
        except Exception as e:
            ai_summary = "AI摘要失败，原始预警如下：\n" + all_alerts_text
        lines.append("⚠️ 当前预警摘要：")
        lines.append(ai_summary)
    else:
        lines.append("✅ 当前无天气预警")

    summary = "\n".join(lines)
    return "天气预报", summary