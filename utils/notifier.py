import os
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()
BARK_KEY = os.getenv("BARK_KEY")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")

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


def send_slack(title: str, body: str):
    """通过 Slack Incoming Webhook 推送一次通知。"""
    if not SLACK_WEBHOOK:
        print("[Notifier] No SLACK_WEBHOOK set, skipping.")
        return
    plain_body = body.replace("<br>", "\n")
    payload = {
        "text": f"*{title}*\n{plain_body}",
    }
    try:
        r = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        r.raise_for_status()
        print("[Notifier] ✅ Slack 推送成功")
    except Exception as e:
        print(f"[Notifier] ❌ Slack 推送失败：{e}")
