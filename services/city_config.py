#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
城市配置模块
包含目标城市配置和API密钥
"""

import os
from dotenv import load_dotenv

# 确保环境变量已加载
load_dotenv()

# 中央气象署 API Key
CWA_API_KEY = os.getenv("CWA_API_KEY")

# 目标城市配置
CITIES = {
    "台北市": {
        "cwa_id": "臺北市",
        "dataset_id": "F-D0047-061"  # 台北市乡镇预报
    },
    "新北市": {
        "cwa_id": "新北市",
        "dataset_id": "F-D0047-069"  # 新北市乡镇预报
    },
    "桃园市": {
        "cwa_id": "桃園市", 
        "dataset_id": "F-D0047-005"  # 桃园市乡镇预报
    }
}

def get_city_config(city_name):
    """获取城市配置"""
    return CITIES.get(city_name)

def get_all_cities():
    """获取所有城市列表"""
    return list(CITIES.keys())

def get_cwa_api_key():
    """获取CWA API密钥"""
    return CWA_API_KEY 