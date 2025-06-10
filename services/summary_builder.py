from datetime import datetime
from zoneinfo import ZoneInfo

def build_summary(data):
    lines = []

    for city, content in data.items():
        if city == "warnings":
            continue

        # 取出24小时数据
        hourly = content.get("hourly", [])

        # 用于两段时间过滤
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
            # 取最常出现的天气状态
            main_text = max(set(texts), key=texts.count)
            return main_text, f"{min(temps)} ~ {max(temps)}℃"

        text1, range1 = summarize_block(block1)
        text2, range2 = summarize_block(block2)
        full_range = f"{min(temp_all)} ~ {max(temp_all)}℃" if temp_all else "?"

        lines.append(f"【{city}】今日天气简要：")
        lines.append(f"09:00 ~ 15:00：{text1}，{range1}")
        lines.append(f"16:00 ~ 22:00：{text2}，{range2}")
        lines.append(f"🌡️ 全日气温范围：{full_range}")
        lines.append("")
    # 一周天气摘要
    for city, content in data.items():
        if city == "warnings":
            continue
        lines.append(f"📅 {city} 一周天气简要：")
        for day in content["weekly"][:3]:
            lines.append(f"- {day['fxDate']}: {day['textDay']} ~ {day['textNight']}")
        lines.append("")

    # 穿衣建议
    lines.append("👕 穿衣建议：")
    for city, content in data.items():
        if city == "warnings":
            continue
        clothing = content.get("clothing", {})
        lines.append(f"- {city}：{clothing.get('category', '')}，{clothing.get('advice', '')}")

    # 加入天气预警
    alerts = data.get("warnings", [])
    if alerts:
        lines.append("⚠️ 当前预警：")
        for alert in alerts:
            lines.append(f"- {alert['title']}: {alert['text']}")
    else:
        lines.append("✅ 当前无天气预警")

    summary = "\n".join(lines)
    return "天气更新（自动生成）", summary