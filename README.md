# QWeather RSS 推送工具

📡 基于 [和风天气 API (QWeather)](https://dev.qweather.com/) 构建的天气自动汇总脚本，支持台北、新北天气查询，天气预警和穿衣指数，并生成 RSS 输出（适用于 GitHub Pages + Slack 通知）。

---

## 🔧 功能

- ✅ 查询台北、新北当天实况与未来一周天气
- ✅ 获取台湾天气预警（暴雨、台风等）
- ✅ 提取穿衣指数建议
- ✅ 自动生成 RSS XML 文件，可用于 GitHub Pages 发布
- ✅ 使用 JWT 身份认证，安全访问和风 API

---

## 🛡️ 项目结构

```
.
├── main.py                 # 主入口，负责调度抓取和生成
├── services/
│   ├── jwt_auth.py         # 生成 JWT Token
│   ├── weather_fetcher.py  # 请求天气数据
│   ├── summary_builder.py  # 构建天气摘要
│   └── rss_writer.py       # 输出 RSS XML
├── .env                    # 环境变量配置文件（含私钥路径等）
├── weather.xml             # 生成的 RSS 文件
└── requirements.txt
```

---

## 🛠️ 安装依赖

确保使用 Python 3.9+，推荐使用虚拟环境：

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔑 环境变量 `.env` 设置

请创建 `.env` 文件并填写以下内容：

```dotenv
QWEATHER_PROJECT_ID=your_project_id
QWEATHER_CREDENTIAL_ID=your_credential_id
QWEATHER_PRIVATE_KEY_PATH=./private_key.pem  # 私钥文件路径
FEED_LINK=https://yourname.github.io/weather-rss/weather.xml  # RSS 输出地址
```

- `PROJECT_ID` 和 `CREDENTIAL_ID` 可在和风控制台查看
- `PRIVATE_KEY_PATH` 是你的 PEM 私钥文件路径

---

## 🚀 使用方式

```bash
python main.py
```

---

## 🔒 安全建议

- **不要上传 `.env` 和私钥文件到 GitHub**
- 已建议将敏感信息加入 `.gitignore` 保护

---

## 📜 License

MIT
