import os
from datetime import datetime
from xml.dom import minidom
from dotenv import load_dotenv

load_dotenv()

RSS_PATH = os.path.join("docs", "weather.xml")
FEED_LINK = os.getenv("RSS_FEED_LINK", "https://example.com/rss.xml")  # GitHub Pages 链接
unique_id = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

def write_rss(title: str, description: str):
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

    channel.appendChild(el("title", "天气快讯"))
    channel.appendChild(el("link", FEED_LINK))
    channel.appendChild(el("description", "台北新北天气、大雨城市与预警"))

    atom_link = doc.createElement("atom:link")
    atom_link.setAttribute("href", FEED_LINK)
    atom_link.setAttribute("rel", "self")
    atom_link.setAttribute("type", "application/rss+xml")
    channel.appendChild(atom_link)

    item = doc.createElement("item")
    item.appendChild(el("title", title))
    item.appendChild(el("pubDate", pub_date))
    item.appendChild(el("guid", f"weather-{unique_id}"))

    desc = doc.createElement("description")
    cdata = doc.createCDATASection(description)
    desc.appendChild(cdata)
    item.appendChild(desc)

    channel.appendChild(item)

    with open(RSS_PATH, "w", encoding="utf-8") as f:
        f.write(doc.toprettyxml(indent="  "))
    print(f"✅ RSS 写入完成：{RSS_PATH}")