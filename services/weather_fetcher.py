import os
import requests
from services.jwt_auth import generate_jwt_token

# ✅ 从 .env 获取你的专属 API Host，例如 abc123.qweatherapi.com
API_HOST = os.getenv("QWEATHER_API_HOST")  # 添加到 .env 文件中
CITY_IDS = {
    "台北市": "101340101",
    "新北市": "101191107",
    "桃园市": "101340102"
}

def fetch(endpoint: str, params: dict):
    jwt_token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept-Encoding": "gzip"
    }
    url = f"https://{API_HOST}/v7/{endpoint}"  # ✅ 使用你的专属域名
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def fetch_indices(city_name, location_id):
    # type=3 是穿衣指数，1 天内预报
    data = fetch("indices/1d", {"location": location_id, "type": 3})
    indices = data.get("daily", [])
    if indices:
        return indices[0].get("category", ""), indices[0].get("text", "")
    return "", ""

def fetch_weather_all():
    result = {}

    for city, loc_id in CITY_IDS.items():
        hourly = fetch("weather/24h", {"location": loc_id})
        week = fetch("weather/7d", {"location": loc_id})
        category, advice = fetch_indices(city, loc_id)
        result[city] = {
            "hourly": hourly.get("hourly", {}),
            "weekly": week.get("daily", []),
            "clothing": {
                "category": category,
                "advice": advice
            }
        }

    warnings = fetch("warning/now", {"location": "101340101"})
    result["warnings"] = warnings.get("warning", [])
    return result