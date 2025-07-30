import os
from datetime import datetime
from xml.dom import minidom
from dotenv import load_dotenv

# 确保环境变量已加载
load_dotenv()

RSS_PATH = os.path.join("docs", "weather.xml")
FEED_LINK = os.getenv("RSS_FEED_LINK", "https://eliu-lotso.github.io/qweather/weather.xml")  # GitHub Pages 地址
CHANNEL_LINK = FEED_LINK.rsplit("/", 1)[0] + "/"  # 用于 <link> 指向主页


def write_rss(title: str, description: str, forecast_hours: int = 15):
    impl = minidom.getDOMImplementation()
    doc = impl.createDocument(None, "rss", None)
    rss = doc.documentElement
    rss.setAttribute("version", "2.0")
    rss.setAttribute("xmlns:atom", "http://www.w3.org/2005/Atom")

    channel = doc.createElement("channel")
    rss.appendChild(channel)

    def el(tag, text):
        node = doc.createElement(tag)
        node.appendChild(doc.createTextNode(text))
        return node

    # 当前时间（秒级唯一标识）
    now = datetime.utcnow()
    timestamp = now.strftime("%Y%m%dT%H%M%S")
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

    # 构造标题加上汇报范围
    report_range = f"（未来 {forecast_hours} 小时预报）"
    full_title = title + report_range

    # 基本频道信息
    channel.appendChild(el("title", "天气快讯"))
    channel.appendChild(el("link", FEED_LINK))
    channel.appendChild(el("description", "台北新北天气、大雨城市与预警"))

    # Atom 自引用声明
    atom_link = doc.createElement("atom:link")
    atom_link.setAttribute("href", FEED_LINK)
    atom_link.setAttribute("rel", "self")
    atom_link.setAttribute("type", "application/rss+xml")
    channel.appendChild(atom_link)

    # 单条项目
    item = doc.createElement("item")
    item.appendChild(el("title", full_title))
    item.appendChild(el("pubDate", pub_date))

    guid = doc.createElement("guid")
    guid.setAttribute("isPermaLink", "false")
    guid.appendChild(doc.createTextNode(f"weather-{timestamp}"))
    item.appendChild(guid)

    desc = doc.createElement("description")
    # 将换行符转换为HTML <br> 标签，确保在RSS阅读器中正确换行
    html_description = description.replace('\n', '<br>')
    cdata = doc.createCDATASection(html_description)
    desc.appendChild(cdata)
    item.appendChild(desc)

    channel.appendChild(item)

    # 写入文件
    with open(RSS_PATH, "w", encoding="utf-8") as f:
        f.write(doc.toprettyxml(indent="  "))
    print(f"✅ RSS 写入完成：{RSS_PATH}")
