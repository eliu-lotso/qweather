#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预警信息获取模块
负责获取中央气象署的预警信息
"""

from datetime import datetime, timedelta
from .http_client import safe_request
from .city_config import get_cwa_api_key
from .typhoon_fetcher import fetch_cwa_typhoon_info

def fetch_cwa_warnings():
    """获取中央气象署全类型预警信息"""
    warnings = []
    
    print("🔍 获取全台湾所有类型预警信息")
    print("包括：观测、地震海啸、气候、天气特报、数值预报")
    
    # 1. 台风相关预警 (重点检查)
    print("\n🌪️ 获取台风相关预警...")
    typhoon_warnings = fetch_cwa_typhoon_info()
    warnings.extend(typhoon_warnings)
    
    # 2. 地震海啸预警
    print("\n🌊 获取地震海啸预警...")
    
    # 2.1 有感地震报告 (E-A0015-001) - 仅显示最近3天
    try:
        # 计算3天前的时间
        three_days_ago = datetime.now() - timedelta(days=3)
        
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
        params = {
            "Authorization": get_cwa_api_key(),
            "format": "JSON"
        }
        
        resp = safe_request(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                earthquakes = records.get("Earthquake", [])
                
                recent_earthquakes = 0
                
                for earthquake in earthquakes:
                    if isinstance(earthquake, dict):
                        eq_info = earthquake.get("EarthquakeInfo", {})
                        origin_time = eq_info.get("OriginTime", "")
                        
                        # 检查地震时间是否在最近3天内
                        if origin_time:
                            try:
                                # 解析地震发生时间 (格式: 2025-07-16 00:18:09)
                                eq_time = datetime.strptime(origin_time, "%Y-%m-%d %H:%M:%S")
                                
                                # 只处理最近3天内的强地震（规模4.0以上）
                                if eq_time >= three_days_ago:
                                    magnitude = eq_info.get("Magnitude", {}).get("MagnitudeValue", "")
                                    
                                    # 检查是否为强地震（规模4.0以上）
                                    is_strong_earthquake = False
                                    if magnitude:
                                        try:
                                            mag_value = float(magnitude)
                                            if mag_value >= 4.0:
                                                is_strong_earthquake = True
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    if is_strong_earthquake:
                                        eq_no = earthquake.get("EarthquakeNo", "")
                                        report_content = earthquake.get("ReportContent", "")
                                        depth = eq_info.get("Depth", {}).get("DepthValue", "")
                                        epicenter = eq_info.get("Epicenter", {}).get("Location", "")
                                        
                                        warning_text = f"地震编号：{eq_no}"
                                        if origin_time:
                                            warning_text += f"，发生时间：{origin_time}"
                                        if magnitude:
                                            warning_text += f"，规模：{magnitude}"
                                        if depth:
                                            warning_text += f"，深度：{depth}公里"
                                        if epicenter:
                                            warning_text += f"，震央：{epicenter}"
                                        
                                        warnings.append({
                                            "title": "有感地震报告",
                                            "text": warning_text,
                                            "city": epicenter if epicenter else "台湾地区",
                                            "type": "地震预警",
                                            "source": "CWA地震测报",
                                            "magnitude": magnitude,
                                            "depth": depth,
                                            "originTime": origin_time,
                                            "earthquakeTime": eq_time
                                        })
                                        
                                        recent_earthquakes += 1
                                    
                            except ValueError as e:
                                # 时间格式解析失败，跳过该条记录
                                print(f"⚠️ 地震时间格式解析失败: {origin_time}")
                                continue
                
                print(f"✅ 获取到最近3天4.0级以上有感地震：{recent_earthquakes} 条 (总数 {len(earthquakes)} 条)")
        
    except Exception as e:
        print(f"获取有感地震报告失败: {e}")
    
    # 2.2 小区域有感地震报告 (E-A0016-001) - 仅显示最近3天
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001"
        params = {
            "Authorization": get_cwa_api_key(),
            "format": "JSON"
        }
        
        resp = safe_request(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                earthquakes = records.get("Earthquake", [])
                
                recent_small_earthquakes = 0
                
                for earthquake in earthquakes:
                    if isinstance(earthquake, dict):
                        eq_info = earthquake.get("EarthquakeInfo", {})
                        origin_time = eq_info.get("OriginTime", "")
                        
                        # 检查地震时间是否在最近3天内
                        if origin_time:
                            try:
                                # 解析地震发生时间 (格式: 2025-07-30 10:24:21)
                                eq_time = datetime.strptime(origin_time, "%Y-%m-%d %H:%M:%S")
                                
                                # 只处理最近3天内的强地震（规模4.0以上）
                                if eq_time >= three_days_ago:
                                    magnitude = eq_info.get("Magnitude", {}).get("MagnitudeValue", "")
                                    
                                    # 检查是否为强地震（规模4.0以上）
                                    is_strong_earthquake = False
                                    if magnitude:
                                        try:
                                            mag_value = float(magnitude)
                                            if mag_value >= 4.0:
                                                is_strong_earthquake = True
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    if is_strong_earthquake:
                                        eq_no = earthquake.get("EarthquakeNo", "")
                                        epicenter = eq_info.get("Epicenter", {}).get("Location", "")
                                        
                                        warning_text = f"小区域地震编号：{eq_no}"
                                        if origin_time:
                                            warning_text += f"，时间：{origin_time}"
                                        if magnitude:
                                            warning_text += f"，规模：{magnitude}"
                                        if epicenter:
                                            warning_text += f"，震央：{epicenter}"
                                        
                                        warnings.append({
                                            "title": "小区域地震报告",
                                            "text": warning_text,
                                            "city": epicenter if epicenter else "台湾地区",
                                            "type": "地震预警",
                                            "source": "CWA地震测报",
                                            "magnitude": magnitude,
                                            "originTime": origin_time,
                                            "earthquakeTime": eq_time
                                        })
                                        
                                        recent_small_earthquakes += 1
                                    
                            except ValueError as e:
                                # 时间格式解析失败，跳过该条记录
                                print(f"⚠️ 小区域地震时间格式解析失败: {origin_time}")
                                continue
                
                print(f"✅ 获取到最近3天4.0级以上小区域地震：{recent_small_earthquakes} 条 (总数 {len(earthquakes)} 条)")
        
    except Exception as e:
        print(f"获取小区域地震报告失败: {e}")
    
    # 2.3 获取海啸警报和各地区预警 (W-C0033-001)
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0033-001"
        params = {
            "Authorization": get_cwa_api_key(),
            "format": "JSON"
        }
        
        resp = safe_request(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                locations = records.get("location", [])
                
                for location in locations:
                    location_name = location.get("locationName", "")
                    hazard_conditions = location.get("hazardConditions", {})
                    hazards = hazard_conditions.get("hazards", [])
                    
                    for hazard in hazards:
                        if isinstance(hazard, dict):
                            info = hazard.get("info", {})
                            phenomena = info.get("phenomena", "")
                            significance = info.get("significance", "")
                            language = info.get("language", "")
                            
                            valid_time = hazard.get("validTime", {})
                            start_time = valid_time.get("startTime", "")
                            end_time = valid_time.get("endTime", "")
                            
                            if phenomena and significance:
                                warning_text = f"{location_name}发布{phenomena}{significance}"
                                if start_time:
                                    warning_text += f"，生效时间：{start_time}"
                                if end_time:
                                    warning_text += f"，结束时间：{end_time}"
                                
                                warnings.append({
                                    "title": f"{phenomena}{significance}",
                                    "text": warning_text,
                                    "city": location_name,
                                    "type": "官方预警",
                                    "source": "CWA预警系统",
                                    "phenomena": phenomena,
                                    "significance": significance,
                                    "startTime": start_time,
                                    "endTime": end_time
                                })
                
                print(f"✅ 获取到海啸警报/地区预警系统数据，发现 {len([w for w in warnings if w['source'] == 'CWA预警系统'])} 条预警")
        
    except Exception as e:
        print(f"获取海啸警报/地区预警失败: {e}")
    
    # 2.4 获取地震速报和天气特报 (W-C0033-002)
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0033-002"
        params = {
            "Authorization": get_cwa_api_key(),
            "format": "JSON"
        }
        
        resp = safe_request(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                record_list = records.get("record", [])
                
                for record in record_list:
                    if isinstance(record, dict):
                        # 获取数据集信息
                        dataset_info = record.get("datasetInfo", {})
                        dataset_desc = dataset_info.get("datasetDescription", "")
                        issue_time = dataset_info.get("issueTime", "")
                        update_time = dataset_info.get("update", "")
                        valid_time = dataset_info.get("validTime", {})
                        start_time = valid_time.get("startTime", "")
                        end_time = valid_time.get("endTime", "")
                        
                        # 获取内容
                        contents = record.get("contents", {})
                        content = contents.get("content", {})
                        content_text = content.get("contentText", "")
                        
                        # 获取危险条件
                        hazard_conditions = record.get("hazardConditions", {})
                        hazards = hazard_conditions.get("hazards", {})
                        hazard_list = hazards.get("hazard", []) if isinstance(hazards, dict) else []
                        
                        if dataset_desc and content_text:
                            # 主预警信息
                            warnings.append({
                                "title": f"官方{dataset_desc}",
                                "text": content_text.strip(),
                                "city": "相关地区",
                                "type": "官方特报",
                                "source": "CWA特报系统",
                                "issueTime": issue_time,
                                "updateTime": update_time,
                                "startTime": start_time,
                                "endTime": end_time
                            })
                        
                        # 详细危险区域信息
                        for hazard in hazard_list:
                            if isinstance(hazard, dict):
                                info = hazard.get("info", {})
                                phenomena = info.get("phenomena", "")
                                significance = info.get("significance", "")
                                affected_areas = info.get("affectedAreas", {})
                                locations_list = affected_areas.get("location", [])
                                
                                if phenomena and locations_list:
                                    area_names = [loc.get("locationName", "") for loc in locations_list if isinstance(loc, dict)]
                                    if area_names:
                                        warning_text = f"受影响地区：{', '.join(area_names)}"
                                        
                                        warnings.append({
                                            "title": f"{phenomena}{significance}",
                                            "text": warning_text,
                                            "city": ", ".join(area_names),
                                            "type": "区域预警",
                                            "source": "CWA特报系统",
                                            "phenomena": phenomena,
                                            "significance": significance
                                        })
                
                print(f"✅ 获取到地震速报/天气特报数据，发现 {len([w for w in warnings if w['source'] == 'CWA特报系统'])} 条特报")
        
    except Exception as e:
        print(f"获取地震速报/天气特报失败: {e}")
    
    # 3. 观测数据预警
    print("\n📊 获取观测数据预警...")
    
    # 3.1 局属气象站观测资料异常监控 (O-A0002-001)
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"
        params = {
            "Authorization": get_cwa_api_key(),
            "format": "JSON"
        }
        
        resp = safe_request(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                stations = records.get("Station", [])
                
                extreme_weather_count = 0
                
                for station in stations:
                    if isinstance(station, dict):
                        station_name = station.get("StationName", "")
                        obs_time = station.get("ObsTime", "")
                        weather_elements = station.get("WeatherElement", [])
                        
                        # 检查极端天气条件
                        for element in weather_elements:
                            if isinstance(element, dict):
                                element_name = element.get("ElementName", "")
                                element_value = element.get("ElementValue", "")
                                
                                try:
                                    if element_name == "TEMP" and element_value != "-99":
                                        temp = float(element_value)
                                        if temp >= 38:  # 高温预警
                                            warnings.append({
                                                "title": "高温观测预警",
                                                "text": f"{station_name}观测站温度达{temp}°C，请注意防暑",
                                                "city": station_name,
                                                "type": "观测预警",
                                                "source": "CWA观测站",
                                                "temperature": temp,
                                                "obsTime": obs_time
                                            })
                                            extreme_weather_count += 1
                                        elif temp <= 6:  # 低温预警
                                            warnings.append({
                                                "title": "低温观测预警",
                                                "text": f"{station_name}观测站温度降至{temp}°C，请注意保暖",
                                                "city": station_name,
                                                "type": "观测预警",
                                                "source": "CWA观测站",
                                                "temperature": temp,
                                                "obsTime": obs_time
                                            })
                                            extreme_weather_count += 1
                                    
                                    elif element_name == "WDSD" and element_value != "-99":
                                        wind_speed = float(element_value)
                                        if wind_speed >= 15:  # 强风预警
                                            warnings.append({
                                                "title": "强风观测预警",
                                                "text": f"{station_name}观测站风速达{wind_speed}m/s，请注意安全",
                                                "city": station_name,
                                                "type": "观测预警",
                                                "source": "CWA观测站",
                                                "windSpeed": wind_speed,
                                                "obsTime": obs_time
                                            })
                                            extreme_weather_count += 1
                                    
                                    elif element_name == "H_24R" and element_value != "-99":
                                        rainfall = float(element_value)
                                        if rainfall >= 130:  # 大豪雨等级
                                            warnings.append({
                                                "title": "大豪雨观测预警",
                                                "text": f"{station_name}观测站24小时累积雨量达{rainfall}mm，请严防水患",
                                                "city": station_name,
                                                "type": "观测预警",
                                                "source": "CWA观测站",
                                                "rainfall24h": rainfall,
                                                "obsTime": obs_time
                                            })
                                            extreme_weather_count += 1
                                        elif rainfall >= 80:  # 豪雨等级
                                            warnings.append({
                                                "title": "豪雨观测预警",
                                                "text": f"{station_name}观测站24小时累积雨量达{rainfall}mm，请注意防范",
                                                "city": station_name,
                                                "type": "观测预警",
                                                "source": "CWA观测站",
                                                "rainfall24h": rainfall,
                                                "obsTime": obs_time
                                            })
                                            extreme_weather_count += 1
                                
                                except (ValueError, TypeError):
                                    continue
                
                print(f"✅ 检查观测站数据，发现极端天气：{extreme_weather_count} 条")
        
    except Exception as e:
        print(f"获取观测站数据失败: {e}")
    
    # 3.2 雨量站观测资料 (O-A0003-001)
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
        params = {
            "Authorization": get_cwa_api_key(),
            "format": "JSON"
        }
        
        resp = safe_request(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                stations = records.get("Station", [])
                
                heavy_rain_count = 0
                
                for station in stations:
                    if isinstance(station, dict):
                        station_name = station.get("StationName", "")
                        obs_time = station.get("ObsTime", "")
                        weather_elements = station.get("WeatherElement", [])
                        
                        for element in weather_elements:
                            if isinstance(element, dict):
                                element_name = element.get("ElementName", "")
                                element_value = element.get("ElementValue", "")
                                
                                try:
                                    if element_name == "RAIN" and element_value != "-998":
                                        rain_1h = float(element_value)
                                        if rain_1h >= 40:  # 1小时雨量40mm以上
                                            warnings.append({
                                                "title": "短时强降雨预警",
                                                "text": f"{station_name}雨量站1小时降雨达{rain_1h}mm，请立即防范",
                                                "city": station_name,
                                                "type": "观测预警",
                                                "source": "CWA雨量站",
                                                "rainfall1h": rain_1h,
                                                "obsTime": obs_time
                                            })
                                            heavy_rain_count += 1
                                
                                except (ValueError, TypeError):
                                    continue
                
                print(f"✅ 检查雨量站数据，发现强降雨：{heavy_rain_count} 条")
        
    except Exception as e:
        print(f"获取雨量站数据失败: {e}")
    
    # 4. 气候预警
    print("\n🌡️ 获取气候预警...")
    
    # 4.1 气候监测 (C-B0025-001)
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/C-B0025-001"
        params = {
            "Authorization": get_cwa_api_key(),
            "format": "JSON"
        }
        
        resp = safe_request(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                locations = records.get("location", [])
                
                climate_warnings = 0
                
                for location in locations:
                    if isinstance(location, dict):
                        station_info = location.get("station", {})
                        station_name = station_info.get("StationName", "")
                        obs_times = location.get("stationObsTimes", {})
                        obs_stats = location.get("stationObsStatistics", {})
                        
                        # 检查异常气候数据
                        if obs_stats:
                            for period in obs_stats.get("AirTemperature", []):
                                if isinstance(period, dict):
                                    statistics = period.get("Precipitation", [])
                                    for stat in statistics:
                                        if isinstance(stat, dict):
                                            stat_type = stat.get("Precipitation", "")
                                            stat_value = stat.get("PrecipitationValue", "")
                                            
                                            try:
                                                if stat_type == "Monthly" and stat_value:
                                                    value = float(stat_value)
                                                    if value == 0:  # 月降雨量为0
                                                        warnings.append({
                                                            "title": "异常干旱监测",
                                                            "text": f"{station_name}月降雨量为0mm，需关注干旱情况",
                                                            "city": station_name,
                                                            "type": "气候预警",
                                                            "source": "CWA气候监测",
                                                            "precipitationValue": value
                                                        })
                                                        climate_warnings += 1
                                            except (ValueError, TypeError):
                                                continue
                
                print(f"✅ 检查气候监测数据，发现异常：{climate_warnings} 条")
        
    except Exception as e:
        print(f"获取气候监测数据失败: {e}")
    
    # 5. 从乡镇预报中提取预警信息
    try:
        # 获取主要城市的乡镇预报，这些数据更详细
        main_cities = ["臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市"]
        
        for city in main_cities:
            # 根据城市获取对应的乡镇预报API
            city_api_map = {
                "臺北市": "F-D0047-061",
                "新北市": "F-D0047-069", 
                "桃園市": "F-D0047-005",
                "臺中市": "F-D0047-075",
                "臺南市": "F-D0047-079",
                "高雄市": "F-D0047-067"
            }
            
            api_id = city_api_map.get(city)
            if api_id:
                url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{api_id}"
                params = {
                    "Authorization": get_cwa_api_key(),
                    "format": "JSON"
                }
                
                resp = safe_request(url, params=params, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success") == "true":
                        records = data.get("records", {})
                        locations = records.get("locations", [])
                        
                        for location in locations:
                            location_elements = location.get("location", [])
                            
                            for loc in location_elements:
                                weather_elements = loc.get("weatherElement", [])
                                
                                for element in weather_elements:
                                    element_name = element.get("elementName", "")
                                    times = element.get("time", [])
                                    
                                    if times:
                                        time_data = times[0]  # 最新数据
                                        element_value = time_data.get("elementValue", [{}])[0]
                                        
                                        # 检查各种预警条件
                                        if element_name == "天氣現象":
                                            weather_text = element_value.get("Weather", "")
                                            
                                            # 检查危险天气关键词
                                            danger_keywords = [
                                                ("大雨", "大雨特报"),
                                                ("豪雨", "豪雨特报"),
                                                ("大雷雨", "大雷雨即时讯息"),
                                                ("雷雨", "雷雨提醒"),
                                                ("雷陣雨", "雷阵雨提醒"),
                                                ("強風", "陆上强风特报"),
                                                ("颱風", "台风消息"),
                                                ("濃霧", "浓雾警告"),
                                                ("冰雹", "冰雹警告")
                                            ]
                                            
                                            for keyword, alert_type in danger_keywords:
                                                if keyword in weather_text:
                                                    warning_text = f"{city}地区预报有{weather_text}，请注意防范。"
                                                    
                                                    # 避免重复
                                                    if not any(w["city"] == city and keyword in w["text"] for w in warnings):
                                                        warnings.append({
                                                            "title": alert_type,
                                                            "text": warning_text,
                                                            "city": city,
                                                            "type": "天气预警",
                                                            "source": "CWA乡镇预报"
                                                        })
                                                    break
                                        
                                        elif element_name == "3小時降雨機率":
                                            pop_value = element_value.get("ProbabilityOfPrecipitation", "")
                                            try:
                                                pop_int = int(pop_value)
                                                if pop_int >= 80:
                                                    warning_text = f"{city}地区3小时降雨机率达{pop_int}%，请注意防范。"
                                                    
                                                    if not any(w["city"] == city and "降雨机率" in w["text"] for w in warnings):
                                                        warnings.append({
                                                            "title": "高降雨机率预警",
                                                            "text": warning_text,
                                                            "city": city,
                                                            "type": "降雨预警",
                                                            "source": "CWA乡镇预报"
                                                        })
                                            except:
                                                pass
        
        print(f"✅ 完成主要城市预警监控")
        
    except Exception as e:
        print(f"获取乡镇预报预警失败: {e}")
    
    # 6. 从36小时天气预报中提取特殊天气信息（全台湾监控）
    try:
        # 获取全台湾各县市的36小时预报
        all_cities = ["臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", "基隆市", "新竹市", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義市", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"]
        
        for city in all_cities:
            url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
            params = {
                "Authorization": get_cwa_api_key(),
                "format": "JSON",
                "locationName": city
            }
            
            resp = safe_request(url, params=params, timeout=10)
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
                            ("暴風雨", "暴风雨警告"),
                            ("颱風", "台风警告"),
                            ("強風", "强风警告"),
                            ("濃霧", "浓雾警告"),
                            ("冰雹", "冰雹警告")
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
        
        print(f"✅ 完成全台湾天气监控")
        
    except Exception as e:
        print(f"获取全台湾天气预报失败: {e}")
    
    return warnings 