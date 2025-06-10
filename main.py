from services.weather_fetcher import fetch_weather_all
from services.summary_builder import build_summary
from utils.rss_writer import write_rss
from utils.notifier import send_bark
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    try:
        data = fetch_weather_all()
        _, summary = build_summary(data)

        now = datetime.now(ZoneInfo("Asia/Taipei"))
        title = f"今日天气（{now.strftime('%Y-%m-%d %H:%M')}）"

        write_rss(title, summary)
        send_bark(title, summary)
        print("✅ RSS 已生成")
    except Exception as e:
        err_msg = f"❌ 生成失败：{e}"
        send_bark("❌ RSS 生成失败", str(e))
        print(err_msg)