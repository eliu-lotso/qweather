import os
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv

# 确保环境变量已加载
load_dotenv()
BARK_KEY = os.getenv("BARK_KEY")

def send_bark(title: str, body: str):
    """通过 BARK 推送一次通知。"""
    if not BARK_KEY:
        return
    url = f"https://api.day.app/{BARK_KEY}/{quote_plus(title)}/{quote_plus(body)}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        print("[Notifier] ✅ BARK 推送成功")
    except Exception as e:
        print(f"[Notifier] ❌ BARK 推送失败：{e}")