#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
观测数据获取模块
负责获取中央气象署的观测数据
"""

from .http_client import safe_request
from .city_config import get_cwa_api_key

def fetch_observation_data_for_city(city_name, city_config):
    """获取城市相关的观测数据用于AI辅助判断"""
    observations = {
        "extreme_weather": [],
        "heavy_rainfall": [],
        "climate_anomalies": []
    }
    
    try:
        # 获取气象站观测数据
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"
        params = {
            "Authorization": get_cwa_api_key(),
            "format": "JSON"
        }
        
        resp = safe_request(url, params=params, timeout=15)
        if resp and resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                stations = records.get("Station", [])
                
                # 查找与当前城市相关的观测站
                for station in stations:
                    if isinstance(station, dict):
                        station_name = station.get("StationName", "")
                        geo_info = station.get("GeoInfo", {})
                        county_name = geo_info.get("CountyName", "")
                        
                        # 检查是否与当前城市相关（更宽松的匹配）
                        city_keywords = {
                            "台北市": ["臺北", "台北", "北市"],
                            "新北市": ["新北", "板橋", "三重", "中和", "新莊", "新店"],
                            "桃园市": ["桃園", "桃园", "中壢", "平鎮", "八德"]
                        }
                        
                        # 获取当前城市的关键词
                        keywords = city_keywords.get(city_name, [city_name])
                        
                        # 检查匹配
                        is_related = False
                        for keyword in keywords:
                            if (keyword in station_name or 
                                keyword in county_name or 
                                (county_name and keyword in county_name)):
                                is_related = True
                                break
                        
                        if is_related:
                            
                            # 检查极端天气
                            weather_elements = station.get("WeatherElement", [])
                            for element in weather_elements:
                                if isinstance(element, dict):
                                    element_name = element.get("ElementName", "")
                                    element_value = element.get("ElementValue", "")
                                    
                                    try:
                                        if element_name == "TEMP" and element_value != "-99":
                                            temp = float(element_value)
                                            if temp >= 38 or temp <= 5:
                                                observations["extreme_weather"].append({
                                                    "station": station_name,
                                                    "type": "高温" if temp >= 38 else "低温",
                                                    "value": f"{temp}°C"
                                                })
                                    except ValueError:
                                        continue
                            
                            # 检查降雨数据
                            rainfall_element = station.get("RainfallElement", {})
                            if rainfall_element:
                                now_rainfall = rainfall_element.get("Now", {}).get("Precipitation", "")
                                try:
                                    if now_rainfall and now_rainfall != "-99":
                                        rainfall = float(now_rainfall)
                                        if rainfall >= 50:
                                            observations["heavy_rainfall"].append({
                                                "station": station_name,
                                                "value": f"{rainfall}mm"
                                            })
                                except ValueError:
                                    continue
        

    
    except Exception as e:
        print(f"⚠️ 获取{city_name}观测数据失败: {e}")
    
    return observations 