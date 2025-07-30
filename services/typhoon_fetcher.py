#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台风信息获取模块
负责获取中央气象署的台风信息
"""

from datetime import datetime
from .http_client import safe_request
from .city_config import get_cwa_api_key

def fetch_cwa_typhoon_info():
    """获取台风相关信息"""
    typhoon_info = []
    
    # 台风消息与警报-热带气旋路径 (主要API)
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0034-005"
        params = {
            "Authorization": get_cwa_api_key(),
            "format": "JSON"
        }
        
        resp = safe_request(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = data.get("records", {})
                
                # 获取所有热带气旋
                tropical_cyclones = records.get("tropicalCyclones", {})
                if tropical_cyclones:
                    typhoon_list = tropical_cyclones.get("tropicalCyclone", [])
                    if not isinstance(typhoon_list, list):
                        typhoon_list = [typhoon_list]
                    
                    for typhoon in typhoon_list:
                        if isinstance(typhoon, dict):
                            # 台风基本信息
                            typhoon_name = typhoon.get("typhoonName", "")
                            tc_name_zh = typhoon_name if typhoon_name else "未知台风"
                            
                            # 获取分析数据 (analysisData)
                            analysis_data = typhoon.get("analysisData", {})
                            if analysis_data:
                                # 获取最新定位数据 (fix)
                                fixes = analysis_data.get("fix", [])
                                if fixes:
                                    # 获取最新的fix数据
                                    latest_fix = fixes[-1] if isinstance(fixes, list) else fixes
                                    
                                    fix_time = latest_fix.get("fixTime", "")
                                    coordinate = latest_fix.get("coordinate", "")
                                    max_wind_speed = latest_fix.get("maxWindSpeed", "")
                                    max_gust_speed = latest_fix.get("maxGustSpeed", "")
                                    pressure = latest_fix.get("pressure", "")
                                    moving_speed = latest_fix.get("movingSpeed", "")
                                    moving_direction = latest_fix.get("movingDirection", "")
                                    
                                    # 解析坐标
                                    lat, lon = "", ""
                                    if coordinate and "," in coordinate:
                                        parts = coordinate.split(",")
                                        if len(parts) == 2:
                                            lon, lat = parts[0].strip(), parts[1].strip()
                                    
                                    # 判断台风等级
                                    try:
                                        wind_val = int(max_wind_speed) if max_wind_speed else 0
                                        if wind_val >= 118:
                                            scale_text = "强台风"
                                        elif wind_val >= 87:
                                            scale_text = "中度台风"
                                        elif wind_val >= 62:
                                            scale_text = "轻度台风"
                                        elif wind_val >= 34:
                                            scale_text = "热带风暴"
                                        else:
                                            scale_text = "热带低压"
                                    except:
                                        scale_text = "热带气旋"
                                    
                                    # 简化台风信息：只显示名字、时间和对台湾的影响
                                    warning_text = f"台风「{tc_name_zh}」"
                                    
                                    if fix_time:
                                        # 格式化时间显示
                                        try:
                                            dt = datetime.fromisoformat(fix_time.replace('+08:00', ''))
                                            formatted_time = dt.strftime('%m月%d日 %H:%M')
                                            warning_text += f"，{formatted_time}最新信息"
                                        except:
                                            warning_text += f"，{fix_time}"
                                    
                                    # 评估对台湾的影响并添加到台风信息中
                                    try:
                                        lat_float = float(lat)
                                        lon_float = float(lon)
                                        # 台湾大约位于北纬22-26度，东经120-122度
                                        if 15 <= lat_float <= 30 and 115 <= lon_float <= 130:
                                            # 计算与台湾的大致距离
                                            taiwan_lat, taiwan_lon = 23.8, 121.0  # 台湾中心位置
                                            distance_lat = abs(lat_float - taiwan_lat)
                                            distance_lon = abs(lon_float - taiwan_lon)
                                            
                                            if distance_lat < 3 and distance_lon < 3:  # 非常接近
                                                impact = "对台湾构成高度威胁"
                                            elif distance_lat < 5 and distance_lon < 5:  # 接近
                                                impact = "对台湾构成中度威胁"
                                            else:  # 需关注
                                                impact = "对台湾构成低度威胁"
                                            
                                            warning_text += f"，{impact}"
                                        else:
                                            warning_text += "，距离台湾较远，影响较小"
                                    except:
                                        warning_text += "，对台湾影响待评估"
                                    
                                    # 不显示预测路径等详细信息
                                    
                                    typhoon_info.append({
                                        "title": f"台风路径监测 - {tc_name_zh}",
                                        "text": warning_text,
                                        "city": "全台湾",
                                        "type": "台风路径",
                                        "source": "CWA",
                                        "typhoonName": tc_name_zh,
                                        "scale": scale_text,
                                        "maxWindSpeed": max_wind_speed,
                                        "pressure": pressure,
                                        "latitude": lat,
                                        "longitude": lon
                                    })
                                    
                                    print(f"🌀 发现台风: {tc_name_zh} - {scale_text}")
                
                else:
                    print("✅ 当前无活跃台风")
    
    except Exception as e:
        print(f"获取台风路径失败: {e}")

    return typhoon_info 