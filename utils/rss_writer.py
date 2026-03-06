import os
from datetime import datetime
from xml.dom import minidom
from xml.etree import ElementTree
from dotenv import load_dotenv

load_dotenv()

RSS_PATH = os.path.join("docs", "weather.xml")
FEED_LINK = os.getenv("RSS_FEED_LINK", "https://eliu-lotso.github.io/tw-weather/weather.xml")
MAX_ITEMS = 20


def _load_existing_items() -> list[ElementTree.Element]:
    """Load existing <item> elements from the current weather.xml."""
    if not os.path.exists(RSS_PATH):
        return []
    try:
        tree = ElementTree.parse(RSS_PATH)
        return list(tree.iter("item"))
    except Exception:
        return []


def _et_to_minidom(doc: minidom.Document, et_elem: ElementTree.Element) -> minidom.Element:
    """Convert an ElementTree <item> element to a minidom element."""
    item = doc.createElement(et_elem.tag)
    for child in et_elem:
        child_node = doc.createElement(child.tag)
        for attr_name, attr_val in child.attrib.items():
            child_node.setAttribute(attr_name, attr_val)
        if child.text:
            if child.tag == "description":
                child_node.appendChild(doc.createCDATASection(child.text))
            else:
                child_node.appendChild(doc.createTextNode(child.text))
        item.appendChild(child_node)
    return item


def write_rss(title: str, description: str, forecast_hours: int = 15):
    now = datetime.utcnow()
    timestamp = now.strftime("%Y%m%dT%H%M%S")
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

    report_range = f"（未来 {forecast_hours} 小时预报）"
    full_title = title + report_range

    html_description = description.replace('\n', '<br>')

    old_items = _load_existing_items()

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
    channel.appendChild(el("lastBuildDate", pub_date))

    atom_link = doc.createElement("atom:link")
    atom_link.setAttribute("href", FEED_LINK)
    atom_link.setAttribute("rel", "self")
    atom_link.setAttribute("type", "application/rss+xml")
    channel.appendChild(atom_link)

    new_item = doc.createElement("item")
    new_item.appendChild(el("title", full_title))
    new_item.appendChild(el("pubDate", pub_date))

    guid = doc.createElement("guid")
    guid.setAttribute("isPermaLink", "false")
    guid.appendChild(doc.createTextNode(f"weather-{timestamp}"))
    new_item.appendChild(guid)

    desc = doc.createElement("description")
    cdata = doc.createCDATASection(html_description)
    desc.appendChild(cdata)
    new_item.appendChild(desc)

    channel.appendChild(new_item)

    for old in old_items[:MAX_ITEMS - 1]:
        imported = doc.importNode(_et_to_minidom(doc, old), True)
        channel.appendChild(imported)

    with open(RSS_PATH, "w", encoding="utf-8") as f:
        f.write(doc.toprettyxml(indent="  "))
    print(f"✅ RSS 写入完成：{RSS_PATH}（共 {min(len(old_items) + 1, MAX_ITEMS)} 条）")
