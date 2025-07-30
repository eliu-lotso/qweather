#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台湾中央气象署天气数据获取服务
完全替代和风天气API，使用台湾官方气象数据
"""

from .weather_fetcher import fetch_cwa_weather
from .warning_fetcher import fetch_cwa_warnings
from .city_config import CITIES

def fetch_weather_all():
    """获取所有天气数据（完全使用中央气象署API）"""
    result = {}

    # 获取中央气象署天气数据
    for city_name, city_config in CITIES.items():
        try:
            weather_data = fetch_cwa_weather(city_name, city_config)
            result[city_name] = weather_data
        except Exception as e:
            print(f"获取{city_name}天气数据失败: {e}")
            result[city_name] = {
                "hourly": [],
                "weekly": [],
                "now": {}
            }

    # 获取中央气象署预警
    cwa_warnings = fetch_cwa_warnings()
    result["warnings"] = cwa_warnings
    
    # 简化的预警信息输出
    if cwa_warnings:
        print(f"⚠️ 发现 {len(cwa_warnings)} 条天气提醒")
    else:
        print("✅ 当前无特殊天气提醒")
    
    return result