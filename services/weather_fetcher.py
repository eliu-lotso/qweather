import os
import requests
from services.jwt_auth import generate_jwt_token

API_HOST = os.getenv("QWEATHER_API_HOST")

# 常规天气：台北、新北、桃园
CITY_IDS = {
    "台北市": "101340101",
    "新北市": "79754",
    "桃园市": "101340102",
}

# 全台预警城市 ID，可按需增补
ALL_TAIWAN_LOCATION_IDS = {
    "宜兰市": "101340104",
    "台北": "101340101",
    "桃园": "101340102",
    "新竹": "101340103",
    "高雄": "101340201",
    "嘉义市": "101340202",
    "台南市": "101340203",
    "台东市": "101340204",
    "屏东市": "101340205",
    "台中市": "101340401",
    "苗栗市": "101340402",
    "彰化市": "101340403",
    "南投市": "101340404",
    "花莲市": "101340405",
    "新北市": "79754",
    "嘉义县": "34B85",
    "新竹县": "C30C",
    "云林县": "5F767",
    "基隆市": "A9E1",
    "澎湖县": "753A2",
}

def fetch(endpoint: str, params: dict):
    jwt_token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept-Encoding": "gzip"
    }
    url = f"https://{API_HOST}/v7/{endpoint}"
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def fetch_weather_all():
    result = {}

    for city, loc_id in CITY_IDS.items():
        hourly = fetch("weather/24h", {"location": loc_id})
        weekly = fetch("weather/7d", {"location": loc_id})
        result[city] = {
            "hourly": hourly.get("hourly", []),
            "weekly": weekly.get("daily", [])
        }

    # 单独处理全台预警
    all_alerts = []
    for loc_id in ALL_TAIWAN_LOCATION_IDS:
        try:
            warn = fetch("warning/now", {"location": loc_id})
            alerts = warn.get("warning", [])
            all_alerts.extend(alerts)
        except Exception:
            continue

    result["warnings"] = all_alerts
    return result