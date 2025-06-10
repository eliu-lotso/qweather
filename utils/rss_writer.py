import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from xml.sax.saxutils import escape
import os
from dotenv import load_dotenv
from datetime import datetime
unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
load_dotenv()
RSS_PATH = os.path.join("docs", "weather.xml")
FEED_LINK = os.getenv("RSS_FEED_LINK", "https://example.com/rss.xml")  # 设置默认值避免空值

def write_rss(title: str, description: str, pub_date: str):
    impl = minidom.getDOMImplementation()
    doc = impl.createDocument(None, "rss", None)
    rss = doc.documentElement
    rss.setAttribute("version", "2.0")

    channel = doc.createElement("channel")
    rss.appendChild(channel)

    def el(tag, text):
        node = doc.createElement(tag)
        node.appendChild(doc.createTextNode(text))
        return node

    channel.appendChild(el("title", "天气快讯"))
    channel.appendChild(el("link", os.getenv("RSS_FEED_LINK", "https://example.com")))
    channel.appendChild(el("description", "台北新北天气、大雨城市与预警"))

    item = doc.createElement("item")
    item.appendChild(el("title", title))
    item.appendChild(el("pubDate", pub_date))
    item.appendChild(el("guid", f"weather-{pub_date[:16].replace(':', '').replace(',', '')}"))

    # 正确添加 CDATA 内容
    desc = doc.createElement("description")
    cdata = doc.createCDATASection(description)
    desc.appendChild(cdata)
    item.appendChild(desc)

    channel.appendChild(item)

    with open("docs/weather.xml", "w", encoding="utf-8") as f:
        f.write(doc.toprettyxml(indent="  "))