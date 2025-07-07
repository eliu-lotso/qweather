import os
import requests
from services.jwt_auth import generate_jwt_token
from dotenv import load_dotenv

load_dotenv()

API_HOST = os.getenv("QWEATHER_API_HOST")
CWA_API_KEY = os.getenv("CWA_API_KEY")  # 中央气象署 API Key

# 常规天气：台北、新北、桃园
CITY_IDS = {
    "台北市": "101340101",
    "新北市": "79754",
    "桃园市": "101340102",
}

# CWA 县市对应
CWA_LOCATIONS = ["臺北市", "台北市", "新北市", "桃園市", "桃园市"]

def fetch(endpoint: str, params: dict):
    """获取和风天气数据"""
    jwt_token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept-Encoding": "gzip"
    }
    url = f"https://{API_HOST}/v7/{endpoint}"
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def fetch_cwa_typhoon_info():
    """获取台风相关信息"""
    typhoon_info = []
    
    # 台风消息与警报-热带气旋路径 (主要API)
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0034-005"
        params = {
            "Authorization": CWA_API_KEY,
            "format": "JSON"
        }
        
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                
                # 获取所有热带气旋
                typhoons = records.get("typhoons", {})
                if typhoons:
                    typhoon_list = typhoons.get("typhoon", [])
                    if not isinstance(typhoon_list, list):
                        typhoon_list = [typhoon_list]
                    
                    for typhoon in typhoon_list:
                        if isinstance(typhoon, dict):
                            # 台风基本信息
                            typhoon_name = typhoon.get("typhoonName", {})
                            if isinstance(typhoon_name, dict):
                                tc_name_zh = typhoon_name.get("text", "")
                                tc_name_en = typhoon_name.get("typhoonNameEN", "")
                            else:
                                tc_name_zh = str(typhoon_name)
                                tc_name_en = ""
                            
                            # 当前数据
                            current_data = typhoon.get("analysisData", {})
                            if current_data:
                                # 时间
                                time_info = current_data.get("time", "")
                                
                                # 中心位置
                                center = current_data.get("center", {})
                                lat = center.get("lat", "")
                                lon = center.get("lon", "")
                                
                                # 强度信息
                                scale = current_data.get("scale", {})
                                scale_text = scale.get("text", "") if isinstance(scale, dict) else str(scale)
                                
                                # 移动信息
                                moving = current_data.get("moving", {})
                                direction = moving.get("direction", {})
                                speed = moving.get("speed", {})
                                
                                direction_text = direction.get("text", "") if isinstance(direction, dict) else ""
                                speed_value = speed.get("value", "") if isinstance(speed, dict) else ""
                                speed_unit = speed.get("unit", "km/h") if isinstance(speed, dict) else "km/h"
                                
                                # 风速信息
                                max_wind = current_data.get("maxWind", {})
                                wind_speed = max_wind.get("speed", {})
                                wind_value = wind_speed.get("value", "") if isinstance(wind_speed, dict) else ""
                                wind_unit = wind_speed.get("unit", "m/s") if isinstance(wind_speed, dict) else "m/s"
                                
                                # 气压
                                pressure = current_data.get("pressure", {})
                                pressure_value = pressure.get("value", "") if isinstance(pressure, dict) else ""
                                
                                # 构建警告文本
                                warning_text = f"台风「{tc_name_zh}」"
                                if tc_name_en:
                                    warning_text += f"（{tc_name_en}）"
                                
                                if time_info:
                                    warning_text += f"最新资料时间：{time_info}。"
                                
                                warning_text += f"\n📍 中心位置：北纬{lat}度、东经{lon}度"
                                
                                if scale_text:
                                    warning_text += f"\n🌀 强度：{scale_text}"
                                
                                if direction_text and speed_value:
                                    warning_text += f"\n➡️ 移动：向{direction_text}移动，时速{speed_value}{speed_unit}"
                                
                                if wind_value:
                                    warning_text += f"\n💨 最大风速：{wind_value}{wind_unit}"
                                
                                if pressure_value:
                                    warning_text += f"\n📊 中心气压：{pressure_value}百帕"
                                
                                # 预测路径（如果有）
                                forecast_data = typhoon.get("forecastData", [])
                                if forecast_data and isinstance(forecast_data, list):
                                    warning_text += "\n\n📈 预测路径："
                                    for idx, forecast in enumerate(forecast_data[:3]):  # 只显示前3个预测
                                        if isinstance(forecast, dict):
                                            fc_time = forecast.get("time", "")
                                            fc_center = forecast.get("center", {})
                                            fc_lat = fc_center.get("lat", "")
                                            fc_lon = fc_center.get("lon", "")
                                            if fc_time and fc_lat and fc_lon:
                                                warning_text += f"\n  • {fc_time}: 北纬{fc_lat}°、东经{fc_lon}°"
                                
                                typhoon_info.append({
                                    "title": f"台风路径监测 - {tc_name_zh}",
                                    "text": warning_text,
                                    "city": "全台湾",
                                    "type": "台风路径",
                                    "source": "CWA"
                                })
                                
                                print(f"🌀 发现台风: {tc_name_zh} - {scale_text}")
                                
                                # 判断是否对台湾有威胁
                                try:
                                    lat_float = float(lat)
                                    lon_float = float(lon)
                                    # 台湾大约位于北纬22-26度，东经120-122度
                                    # 如果台风在北纬15-30度，东经115-130度范围内，可能对台湾有影响
                                    if 15 <= lat_float <= 30 and 115 <= lon_float <= 130:
                                        distance_warning = f"⚠️ 注意：台风{tc_name_zh}位于台湾附近海域，请密切关注其动向并做好防台准备。"
                                        typhoon_info.append({
                                            "title": "台风接近警告",
                                            "text": distance_warning,
                                            "city": "台北市、新北市、桃园市",
                                            "type": "台风警告",
                                            "source": "CWA"
                                        })
                                except:
                                    pass
                
                else:
                    print("✅ 当前无活跃台风")
                    
    except Exception as e:
        print(f"获取台风路径失败: {e}")
    
    # 备用：台风警报（如果有官方警报）
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0034-001"
        params = {
            "Authorization": CWA_API_KEY,
            "format": "JSON"
        }
        
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                content = records.get("contents", {}).get("content", "")
                
                if content and "解除" not in content:
                    typhoon_info.append({
                        "title": "台风警报（官方）",
                        "text": content,
                        "city": "台北市、新北市、桃园市",
                        "type": "台风警报",
                        "source": "CWA"
                    })
    except Exception as e:
        print(f"获取官方台风警报失败: {e}")
    
    return typhoon_info

def fetch_cwa_warnings():
    """获取中央气象署天气预警和特殊天气提醒"""
    warnings = []
    
    # 首先获取台风信息
    typhoon_warnings = fetch_cwa_typhoon_info()
    warnings.extend(typhoon_warnings)
    
    # 如果有台风，检查对目标城市的影响
    if typhoon_warnings:
        try:
            # 获取台风期间的详细天气预报
            url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-089"  # 全台湾各县市预报
            params = {
                "Authorization": CWA_API_KEY,
                "format": "JSON",
                "locationName": "台北市,新北市,桃园市,台中市,台南市,高雄市,基隆市,新竹市,嘉义市,新竹县,苗栗县,彰化县,南投县,云林县,嘉义县,屏东县,宜兰县,花莲县,台东县,澎湖县,金门县,连江县"
            }
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success") == "true":
                    records = data.get("records", {})
                    locations = records.get("locations", [])
                    
                    if locations:
                        location_data = locations[0].get("location", [])
                        for location in location_data:
                            loc_name = location.get("locationName", "")
                            weather_elements = location.get("weatherElement", [])
                            
                            # 分析风力和降雨
                            wind_info = None
                            rain_info = None
                            
                            for element in weather_elements:
                                element_name = element.get("elementName", "")
                                if element_name == "Wind":  # 风力
                                    times = element.get("time", [])
                                    if times:
                                        wind_desc = times[0].get("elementValue", [{}])[0].get("measures", {}).get("value", "")
                                        if wind_desc and "級" in wind_desc:
                                            wind_info = wind_desc
                                
                                elif element_name == "PoP12h":  # 12小时降雨机率
                                    times = element.get("time", [])
                                    if times:
                                        rain_prob = times[0].get("elementValue", [{}])[0].get("value", "")
                                        if rain_prob:
                                            rain_info = rain_prob
                            
                            # 生成台风影响预警
                            if wind_info or rain_info:
                                impact_text = f"受台风影响，{loc_name}"
                                if wind_info:
                                    impact_text += f"预计风力达{wind_info}"
                                if rain_info:
                                    try:
                                        if int(rain_info) > 70:
                                            if wind_info:
                                                impact_text += "，"
                                            impact_text += f"降雨机率{rain_info}%"
                                    except:
                                        pass
                                impact_text += "，请做好防台准备。"
                                
                                warnings.append({
                                    "title": "台风影响评估",
                                    "text": impact_text,
                                    "city": loc_name,
                                    "type": "台风影响",
                                    "source": "CWA"
                                })
                                
        except Exception as e:
            print(f"获取台风影响评估失败: {e}")
    
    # 方案1：从36小时天气预报中提取特殊天气信息
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
        params = {
            "Authorization": CWA_API_KEY,
            "format": "JSON",
            "locationName": "台北市,新北市,桃园市,台中市,台南市,高雄市,基隆市,新竹市,嘉义市,新竹县,苗栗县,彰化县,南投县,云林县,嘉义县,屏东县,宜兰县,花莲县,台东县,澎湖县,金门县,连江县"
        }
        
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                locations = records.get("location", [])
                
                for location in locations:
                    location_name = location.get("locationName", "")
                    weather_elements = location.get("weatherElement", [])
                    
                    # 分析天气现象
                    wx_info = {}
                    pop_info = {}
                    
                    for element in weather_elements:
                        element_name = element.get("elementName", "")
                        
                        if element_name == "Wx":  # 天气现象
                            times = element.get("time", [])
                            for idx, time_data in enumerate(times[:2]):  # 只看前两个时段
                                parameter = time_data.get("parameter", {})
                                weather_desc = parameter.get("parameterName", "")
                                wx_info[f"period_{idx}"] = weather_desc
                        
                        elif element_name == "PoP":  # 降雨机率
                            times = element.get("time", [])
                            for idx, time_data in enumerate(times[:2]):
                                parameter = time_data.get("parameter", {})
                                pop_value = parameter.get("parameterName", "0")
                                try:
                                    pop_info[f"period_{idx}"] = int(pop_value)
                                except:
                                    pop_info[f"period_{idx}"] = 0
                    
                    # 检查是否需要发出警告
                    warning_conditions = [
                        ("大雨", "大雨特报"),
                        ("豪雨", "豪雨特报"),
                        ("雷雨", "雷雨提醒"),
                        ("雷陣雨", "雷阵雨提醒"),
                        ("大雷雨", "大雷雨警告"),
                        ("陣雨", "阵雨提醒"),
                        ("暴風雨", "暴风雨警告")
                    ]
                    
                    for period in ["period_0", "period_1"]:
                        if period in wx_info:
                            weather_desc = wx_info[period]
                            pop = pop_info.get(period, 0)
                            
                            # 检查特殊天气关键词
                            for keyword, alert_type in warning_conditions:
                                if keyword in weather_desc:
                                    warning_text = f"{location_name}未来12-24小时内预报有{weather_desc}"
                                    if pop >= 70:
                                        warning_text += f"，降雨机率高达{pop}%"
                                    warning_text += "，请注意防范。"
                                    
                                    # 避免重复
                                    if not any(w["city"] == location_name and keyword in w["text"] for w in warnings):
                                        warnings.append({
                                            "title": alert_type,
                                            "text": warning_text,
                                            "city": location_name,
                                            "type": "天气提醒",
                                            "source": "CWA天气预报"
                                        })
                                    break
                            
                            # 高降雨机率警告（即使没有特殊天气描述）
                            if pop >= 80 and not any(w["city"] == location_name for w in warnings):
                                warnings.append({
                                    "title": "高降雨机率提醒",
                                    "text": f"{location_name}降雨机率达{pop}%，出门请携带雨具。",
                                    "city": location_name,
                                    "type": "降雨提醒",
                                    "source": "CWA天气预报"
                                })
                
                print(f"✅ 成功获取CWA天气预报数据")
                
    except Exception as e:
        print(f"获取36小时天气预报失败: {e}")
    
    # 方案2：尝试获取乡镇预报（更详细的预警信息）
    try:
        # 台北市乡镇预报
        urls = {
            "臺北市": "F-D0047-061",
            "新北市": "F-D0047-069",
            "桃園市": "F-D0047-005"
        }
        
        for city_name, dataset_id in urls.items():
            url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{dataset_id}"
            params = {
                "Authorization": CWA_API_KEY,
                "format": "JSON",
                "elementName": "WeatherDescription"  # 天气综合描述
            }
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success") == "true":
                    records = data.get("records", {})
                    locations = records.get("locations", [])
                    
                    if locations:
                        location = locations[0]
                        location_elements = location.get("location", [])
                        
                        # 分析每个区的天气描述
                        severe_weather_found = False
                        for loc in location_elements[:3]:  # 只看前3个区作为样本
                            loc_name = loc.get("locationName", "")
                            weather_elements = loc.get("weatherElement", [])
                            
                            for element in weather_elements:
                                if element.get("elementName") == "WeatherDescription":
                                    times = element.get("time", [])
                                    if times:
                                        desc = times[0].get("elementValue", [{}])[0].get("value", "")
                                        
                                        # 检查严重天气描述
                                        severe_keywords = ["豪雨", "大雨", "雷雨", "強風", "低溫"]
                                        for keyword in severe_keywords:
                                            if keyword in desc and not severe_weather_found:
                                                warnings.append({
                                                    "title": f"{city_name}{keyword}提醒",
                                                    "text": f"{city_name}部分地区可能出现{keyword}天气，请留意最新天气信息。",
                                                    "city": city_name,
                                                    "type": "区域天气提醒",
                                                    "source": "CWA乡镇预报"
                                                })
                                                severe_weather_found = True
                                                break
                
    except Exception as e:
        print(f"获取乡镇预报失败: {e}")
    
    # 方案3：观测资料异常提醒（实时数据）
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001"
        params = {
            "Authorization": CWA_API_KEY,
            "format": "JSON",
            "locationName": "臺北,板橋,桃園",  # 主要观测站
            "elementName": "TEMP,HUMD,WDSD,H_24R"  # 温度、湿度、风速、24小时雨量
        }
        
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                location_data = records.get("location", [])
                
                for location in location_data:
                    loc_name = location.get("locationName", "")
                    weather_elements = location.get("weatherElement", [])
                    
                    elements_dict = {}
                    for element in weather_elements:
                        element_name = element.get("elementName", "")
                        element_value = element.get("elementValue", "")
                        try:
                            elements_dict[element_name] = float(element_value)
                        except:
                            elements_dict[element_name] = element_value
                    
                    # 检查极端天气条件
                    if "H_24R" in elements_dict and elements_dict["H_24R"] != "-99":
                        rain_24h = elements_dict["H_24R"]
                        if rain_24h > 80:  # 24小时雨量超过80mm
                            warnings.append({
                                "title": "大雨警告",
                                "text": f"{loc_name}观测站24小时累积雨量达{rain_24h}mm，请注意防范水患。",
                                "city": f"{loc_name}地区",
                                "type": "实时观测警告",
                                "source": "CWA观测站"
                            })
                    
                    if "WDSD" in elements_dict:
                        wind_speed = elements_dict["WDSD"]
                        if wind_speed > 10:  # 风速超过10m/s
                            warnings.append({
                                "title": "强风提醒",
                                "text": f"{loc_name}观测站目前风速达{wind_speed}m/s，外出请注意安全。",
                                "city": f"{loc_name}地区",
                                "type": "实时观测提醒",
                                "source": "CWA观测站"
                            })
                
    except Exception as e:
        print(f"获取观测资料失败: {e}")
    
    return warnings

def fetch_weather_all():
    """获取所有天气数据"""
    result = {}

    # 获取和风天气数据
    for city, loc_id in CITY_IDS.items():
        try:
            hourly = fetch("weather/24h", {"location": loc_id})
            weekly = fetch("weather/7d", {"location": loc_id})
            result[city] = {
                "hourly": hourly.get("hourly", []),
                "weekly": weekly.get("daily", [])[1:]
            }
        except Exception as e:
            print(f"获取{city}天气数据失败: {e}")
            result[city] = {
                "hourly": [],
                "weekly": []
            }

    # 获取中央气象署预警
    cwa_warnings = fetch_cwa_warnings()
    result["warnings"] = cwa_warnings
    
    # 打印预警信息供调试
    if cwa_warnings:
        print(f"⚠️ 发现 {len(cwa_warnings)} 条天气提醒")
        
        # 检查是否有台风相关警告
        typhoon_related = [w for w in cwa_warnings if w['type'] in ['台风警报', '热带气旋', '台风影响', '台风路径', '台风警告']]
        if typhoon_related:
            print("🌀 台风相关警告:")
            for warning in typhoon_related:
                print(f"  - [{warning['city']}] {warning['title']}")
        
        # 其他警告
        other_warnings = [w for w in cwa_warnings if w['type'] not in ['台风警报', '热带气旋', '台风影响', '台风路径', '台风警告']]
        if other_warnings:
            print("☔ 其他天气提醒:")
            for warning in other_warnings:
                print(f"  - [{warning['city']}] {warning['title']}")
    else:
        print("✅ 当前无特殊天气提醒")
    
    return result