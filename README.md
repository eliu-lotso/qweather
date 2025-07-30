# 台湾天气 RSS 推送工具

📡 基于 [台湾中央气象署开放数据平台](https://opendata.cwa.gov.tw/dist/opendata-swagger.html) 构建的智能天气自动汇总工具，支持台北、新北、桃园天气查询，实时预警监控并生成 RSS 输出

---

## 🔧 功能特性

- ✅ **多城市天气查询**: 台北、新北、桃园当天实况与未来两日天气
- ✅ **智能预警监控**: 台风、地震、暴雨、强风等全类型天气预警
- ✅ **AI智能摘要**: 使用豆包AI自动生成简洁的天气和预警摘要
- ✅ **RSS自动生成**: 生成标准RSS XML文件，支持GitHub Pages发布
- ✅ **手机推送**: 支持BARK推送通知到手机
- ✅ **模块化设计**: 清晰的代码结构，易于维护和扩展

---

## 🏗️ 项目结构

```
.
├── main.py                    # 主入口，负责调度抓取和生成
├── services/                  # 核心服务模块
│   ├── cwa_weather_fetcher.py # 中央气象署天气数据获取协调器
│   ├── weather_fetcher.py     # 城市天气数据获取
│   ├── warning_fetcher.py     # 预警信息获取
│   ├── typhoon_fetcher.py     # 台风信息获取
│   ├── observation_fetcher.py # 观测数据获取
│   ├── summary_builder.py     # AI智能摘要构建
│   ├── doubao_ai.py          # 豆包AI调用接口
│   ├── city_config.py        # 城市配置管理
│   └── http_client.py        # HTTP请求客户端
├── utils/                     # 工具模块
│   ├── rss_writer.py         # RSS XML生成
│   └── notifier.py           # 推送通知
├── docs/                      # 输出文档
│   └── weather.xml           # 生成的RSS文件
├── .env                      # 环境变量配置
└── requirements.txt          # Python依赖
```

---

## 🛠️ 安装依赖

确保使用 Python 3.9+，推荐使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

## 🔑 环境变量配置

请创建 `.env` 文件并填写以下内容：

```dotenv
# 必需配置
CWA_API_KEY=your_cwa_api_key                    # 中央气象署 API Key

# 可选配置
DOUBAO_API_KEY=your_doubao_api_key              # 豆包AI API Key（用于智能摘要）
BARK_KEY=your_bark_key                          # BARK推送Key（用于手机通知）
RSS_FEED_LINK=https://yourname.github.io/qweather/weather.xml  # RSS输出地址
```

### 🔑 API Key 获取方式

- **CWA_API_KEY**: 在[中央气象署开放数据平台](https://opendata.cwa.gov.tw/)注册申请
- **DOUBAO_API_KEY**: 在[火山引擎](https://www.volcengine.com/)申请豆包AI服务
- **BARK_KEY**: 在[BARK](https://github.com/Finb/Bark)应用中获取推送Key

---

### 自动定时运行
项目包含GitHub Actions工作流，可自动定时更新RSS：

1. 在GitHub仓库中启用Actions
2. 配置环境变量（Settings > Secrets and variables > Actions）
3. 工作流将每小时自动运行并更新RSS
---

## 📜 License

MIT License
