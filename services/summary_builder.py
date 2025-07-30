from zoneinfo import ZoneInfo
from datetime import datetime
import re
from services.doubao_ai import call_doubao_ai

def generate_ai_future_weather_summaries(data):
    """使用AI生成智能的未来两日天气总结"""
    summaries = {}
    
    for city, weather_data in data.items():
        if city == "warnings":
            continue
            
        # 提取未来天气数据
        hourly = weather_data.get("hourly", [])
        weekly = weather_data.get("weekly", [])
        
        if not hourly and not weekly:
            summaries[city] = f"🌤️ **{city}未来两日天气**：数据获取中"
            continue
        
        # 构建给AI的数据摘要
        data_summary = f"城市：{city}\n\n"
        
        # 添加观测数据（用于AI辅助判断）
        observations = weather_data.get("observations", {})
        if observations:
            data_summary += "📊 当前观测数据：\n"
            
            # 极端天气观测
            extreme_weather = observations.get("extreme_weather", [])
            if extreme_weather:
                data_summary += "- 极端天气观测：\n"
                for obs in extreme_weather[:3]:  # 最多显示3条
                    data_summary += f"  * {obs['station']}: {obs['type']} {obs['value']}\n"
            
            # 强降雨观测
            heavy_rainfall = observations.get("heavy_rainfall", [])
            if heavy_rainfall:
                data_summary += "- 强降雨观测：\n"
                for obs in heavy_rainfall[:3]:  # 最多显示3条
                    data_summary += f"  * {obs['station']}: {obs['value']}\n"
            
            # 气候异常观测
            climate_anomalies = observations.get("climate_anomalies", [])
            if climate_anomalies:
                data_summary += "- 气候异常观测：\n"
                for obs in climate_anomalies[:3]:  # 最多显示3条
                    data_summary += f"  * {obs['station']}: {obs['value']} ({obs['date']})\n"
            
            data_summary += "\n"
        
        # 添加小时预报信息（未来24小时）
        if hourly:
            data_summary += "未来24小时详细预报：\n"
            for hour in hourly[:6]:  # 前6个小时的详细信息
                data_summary += f"- {hour.get('fxTime', 'N/A')}: {hour.get('text', 'N/A')}"
                if hour.get('temp'):
                    data_summary += f", {hour['temp']}℃"
                if hour.get('tempMax'):
                    data_summary += f", 最高{hour['tempMax']}℃"
                if hour.get('tempMin'):
                    data_summary += f", 最低{hour['tempMin']}℃"
                if hour.get('precip'):
                    data_summary += f", 降雨机率{hour['precip']}%"
                data_summary += "\n"
        
        # 添加日级别总结
        if weekly:
            data_summary += "\n未来两日总结：\n"
            for day in weekly[:2]:
                data_summary += f"- {day.get('fxDate', 'N/A')}: 白天{day.get('textDay', 'N/A')}, 夜间{day.get('textNight', 'N/A')}"
                if day.get('tempMax') and day.get('tempMin'):
                    data_summary += f", {day['tempMin']}~{day['tempMax']}℃"
                if day.get('precip'):
                    data_summary += f", 降雨机率{day['precip']}%"
                data_summary += "\n"
        
        # 精简的AI提示词 - 专门用于未来天气总结（包含观测数据）
        prompt = f"""基于天气数据和观测数据生成极简天气总结：

{data_summary}

要求：
- 格式：🌤️ **{city}未来两日**：[一句话总结]
- 长度：严格控制在30字以内
- 内容：结合观测数据，包含关键天气+温度范围+一个核心提醒
- 风格：简洁实用，如果有观测异常要特别提醒
- 观测数据优先级：极端天气 > 强降雨 > 气候异常

示例：多云转雷雨，27~36℃，明日午后备雨具（观测到强降雨需注意）"""



        try:
            ai_summary = call_doubao_ai(prompt, temperature=0.2)  # 降低温度提高一致性
            summaries[city] = ai_summary.strip()
        except Exception as e:
            print(f"⚠️ {city} AI天气总结生成失败: {e}")
            # AI调用失败时的精简备用格式
            if weekly and len(weekly) >= 2:
                tomorrow = weekly[0]
                day_after = weekly[1] if len(weekly) > 1 else {}
                
                # 提取温度范围
                temps = []
                if tomorrow.get('tempMin'): temps.append(int(tomorrow['tempMin']))
                if tomorrow.get('tempMax'): temps.append(int(tomorrow['tempMax']))
                if day_after.get('tempMin'): temps.append(int(day_after['tempMin']))
                if day_after.get('tempMax'): temps.append(int(day_after['tempMax']))
                
                temp_range = f"{min(temps)}~{max(temps)}℃" if temps else "数据获取中"
                
                # 主要天气现象
                main_weather = tomorrow.get('textDay', '晴')
                if '雷' in main_weather or '雨' in main_weather:
                    reminder = "备雨具"
                elif int(tomorrow.get('tempMax', '0')) >= 35:
                    reminder = "防暑"
                else:
                    reminder = "关注天气"
                
                summaries[city] = f"🌤️ **{city}未来两日**：{main_weather}，{temp_range}，{reminder}"
            else:
                summaries[city] = f"🌤️ **{city}未来两日**：数据获取中"
    
    return summaries

def build_summary(data):
    lines = []

    # 今日天气摘要 - 简化为全天概况
    for city, content in data.items():
        if city == "warnings":
            continue
        
        # 优先从today字段获取数据
        today_data = content.get("today", {})
        if today_data:
            hourly = today_data.get("hourly", [])
            temp_max = today_data.get("tempMax", "")
            temp_min = today_data.get("tempMin", "")
            
            if hourly:
                # 从小时数据中提取主要天气现象
                weather_texts = [entry.get("text", "") for entry in hourly if entry.get("text")]
                main_weather = max(set(weather_texts), key=weather_texts.count) if weather_texts else "晴"
                
                # 构建简化的全天天气摘要
                if temp_max and temp_min:
                    lines.append(f"【{city}】今日天气：{main_weather}，{temp_min} ~ {temp_max}℃")
                else:
                    lines.append(f"【{city}】今日天气：{main_weather}")
            else:
                # 如果没有小时数据，从weekly数据获取
                weekly = content.get("weekly", [])
                if weekly:
                    today_weekly = weekly[0]
                    weather = today_weekly.get("textDay", "晴")
                    temp_max = today_weekly.get("tempMax", "")
                    temp_min = today_weekly.get("tempMin", "")
                    
                    if temp_max and temp_min:
                        lines.append(f"【{city}】今日天气：{weather}，{temp_min} ~ {temp_max}℃")
                    else:
                        lines.append(f"【{city}】今日天气：{weather}")
                else:
                    lines.append(f"【{city}】今日天气：数据获取中")
        else:
            # 兜底：从hourly数据构建
            hourly = content.get("hourly", [])
            if hourly:
                # 提取今日数据
                today_hourly = []
                temp_all = []
                
                for entry in hourly:
                    try:
                        dt = datetime.fromisoformat(entry["fxTime"]).astimezone(ZoneInfo("Asia/Taipei"))
                        if dt.date() == datetime.now(ZoneInfo("Asia/Taipei")).date():
                            today_hourly.append(entry)
                            temp_str = entry.get("temp", "")
                            if temp_str and temp_str.strip():
                                try:
                                    temp_all.append(int(temp_str))
                                except (ValueError, TypeError):
                                    pass
                    except:
                        continue
                
                if today_hourly:
                    weather_texts = [entry.get("text", "") for entry in today_hourly if entry.get("text")]
                    main_weather = max(set(weather_texts), key=weather_texts.count) if weather_texts else "晴"
                    
                    if temp_all:
                        temp_min = min(temp_all)
                        temp_max = max(temp_all)
                        lines.append(f"【{city}】今日天气：{main_weather}，{temp_min} ~ {temp_max}℃")
                    else:
                        lines.append(f"【{city}】今日天气：{main_weather}")
                else:
                    lines.append(f"【{city}】今日天气：数据获取中")
            else:
                lines.append(f"【{city}】今日天气：数据获取中")
        
        lines.append("")

    # AI驱动的未来两日天气总结
    future_summaries = generate_ai_future_weather_summaries(data)
    for city, summary in future_summaries.items():
        lines.append(summary)
        lines.append("")

    # ✅ 天气预警 - 简化显示：只关注市级预警和其他重要区域预警，忽略县级预警
    alerts = data.get("warnings", [])
    if alerts:
        # 分类整理预警信息
        city_alerts = []  # 市级预警（重点关注）
        typhoon_alerts = []  # 台风预警（单独处理）
        other_alerts = []  # 其他重要区域预警
        
        for alert in alerts:
            city = alert.get("city", "未知地区")
            title = alert.get("title", "")
            text = alert.get("text", "")
            alert_type = alert.get("type", "")
            
            # 提取时间信息
            start_time = alert.get("startTime", "")
            end_time = alert.get("endTime", "")
            issue_time = alert.get("issueTime", "")
            
            # 构建带时间信息的预警文本
            time_info = ""
            if start_time or end_time:
                if start_time and end_time:
                    time_info = f"（{start_time}至{end_time}）"
                elif start_time:
                    time_info = f"（生效：{start_time}）"
                elif end_time:
                    time_info = f"（结束：{end_time}）"
            
            alert_with_time = f"[{city}] {title}: {text}{time_info}"
            
            # 台风预警单独处理
            if "台风" in title or "台风" in alert_type:
                typhoon_alerts.append(alert_with_time)
            # 市级预警重点关注
            elif "市" in city and not any(x in city for x in [",", "、", " "]):  # 单独的市
                city_alerts.append(alert_with_time)
            # 忽略县级预警（縣、县）
            elif "縣" in city or "县" in city:
                continue  # 直接跳过县级预警
            # 其他重要区域预警（如官方预警、多区域预警等）
            else:
                other_alerts.append(alert_with_time)
        
        # 构建传递给AI的文本
        alert_texts = []
        
        # 台风预警（已优化过的）
        if typhoon_alerts:
            alert_texts.extend(typhoon_alerts)
        
        # 市级预警（重点关注）
        if city_alerts:
            alert_texts.append("=== 重点市级预警 ===")
            alert_texts.extend(city_alerts)
        
        # 其他重要区域预警（过滤县信息）
        if other_alerts:
            alert_texts.append("=== 其他重要区域预警 ===")
            
            # 对其他区域预警进行县信息过滤
            filtered_other_alerts = []
            for alert in other_alerts:
                # 提取预警信息
                parts = alert.split(": ", 1)
                if len(parts) == 2:
                    header = parts[0]  # [城市] 标题
                    content = parts[1]  # 内容
                    
                    # 过滤内容中的县信息
                    # 移除包含县的句子或短语
                    sentences = re.split(r'[，。；]', content)
                    filtered_sentences = []
                    
                    for sentence in sentences:
                        # 如果句子中包含县，尝试移除县相关部分
                        if '縣' in sentence or '县' in sentence:
                            # 移除县名，但保留其他重要信息
                            # 例如：将"高雄市、屏東縣山區"改为"高雄市山區"
                            sentence = re.sub(r'[^，、]*[縣县][^，、]*[、，]?', '', sentence)
                            sentence = re.sub(r'、+', '、', sentence)  # 清理多余的顿号
                            sentence = re.sub(r'^[、，]+|[、，]+$', '', sentence)  # 清理开头结尾的标点
                        
                        # 如果句子处理后还有内容，就保留
                        if sentence.strip():
                            filtered_sentences.append(sentence.strip())
                    
                    # 重新组合内容
                    if filtered_sentences:
                        filtered_content = '，'.join(filtered_sentences)
                        filtered_alert = f"{header}: {filtered_content}"
                        filtered_other_alerts.append(filtered_alert)
                else:
                    # 如果格式不标准，直接检查是否包含县信息
                    if not ('縣' in alert or '县' in alert):
                        filtered_other_alerts.append(alert)
            
            alert_texts.extend(filtered_other_alerts)
        
        all_alerts_text = "\n".join(alert_texts)
        
        # 调用豆包AI进行摘要，并提供优化指导
        try:
            # 极简预警AI提示词 - 保留重要城市名称和时间信息
            optimized_prompt = f"""对预警信息进行极简摘要：

{all_alerts_text}

要求：
1. **台风信息**：保持现有格式
2. **市级预警**：合并同类预警，保留重要城市名称，如有时间信息需保留
3. **其他区域预警**：合并为1-2句话，保留关键地区名称和时间信息
4. **总体**：总长度控制在150字以内，突出关键信息和时效性

示例格式：
- 台风：台风「XX」对台湾影响较小
- 市级：豪雨特报覆盖台中市、高雄市、台南市（15:05-23:00）；雷雨提醒：台中市、台南市、高雄市有雷雨
- 其他：西南气流影响，新竹市、兰屿、绿岛有强风，山区防坍方"""
            

            
            ai_summary = call_doubao_ai(optimized_prompt)
        except Exception as e:
            ai_summary = "AI摘要失败，原始预警如下：\n" + all_alerts_text
        
        # 获取当前时间作为预警摘要的时间戳
        current_time = datetime.now().strftime('%m月%d日 %H:%M')
        
        lines.append(f"⚠️ 当前预警摘要（{current_time}）：")
        lines.append(ai_summary)
    else:
        lines.append("✅ 当前无天气预警")

    summary = "\n".join(lines)
    return "天气预报", summary