def build_summary(data):
    lines = []

    for city, content in data.items():
        if city == "warnings":
            continue
        now = content["now"]
        forecast = content["weekly"][0]  # 当天预报

        desc = now.get("text", "")
        temp_min = forecast.get("tempMin", "?")
        temp_max = forecast.get("tempMax", "?")
        lines.append(f"【{city}】{desc}，{temp_min} ~ {temp_max}℃")

    lines.append("")

    # 一周天气摘要（简写）
    for city, content in data.items():
        if city == "warnings":
            continue
        lines.append(f"📅 {city} 一周天气简要：")
        for day in content["weekly"][:3]:
            lines.append(f"- {day['fxDate']}: {day['textDay']} ~ {day['textNight']}")

    lines.append("")

    lines.append("👕 穿衣建议：")
    for city, content in data.items():
        if city == "warnings":
            continue
        clothing = content.get("clothing", {})
        lines.append(f"- {city}：{clothing.get('category', '')}，{clothing.get('advice', '')}")

    # 天气预警
    alerts = data.get("warnings", [])
    if alerts:
        lines.append("⚠️ 当前预警：")
        for alert in alerts:
            lines.append(f"- {alert['title']}: {alert['text']}")
    else:
        lines.append("✅ 当前无天气预警")

    summary = "\n".join(lines)
    return "天气更新（自动生成）", summary