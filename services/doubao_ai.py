import requests
import os

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

def call_doubao_ai(prompt, model="doubao-seed-1-6-flash-250615", temperature=0.2):
    """
    调用火山引擎豆包大模型进行摘要/合成
    :param prompt: 输入的文本内容
    :param model: 使用的模型名称
    :param temperature: 采样温度
    :return: AI返回的摘要文本
    """
    headers = {
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个专业的气象摘要助手，请将多条天气预警合并为简明、无重复的摘要，相同类型预警只保留一条。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }
    try:
        resp = requests.post(DOUBAO_API_URL, headers=headers, json=data, timeout=20)
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise

# 示例用法
if __name__ == "__main__":
    test_alerts = """
    [台北市] 大雨特报: 台北市未来12小时有大雨，请注意防范。
    [新北市] 大雨特报: 新北市未来12小时有大雨，请注意防范。
    [桃园市] 强风提醒: 桃园市阵风较强，外出注意安全。
    """
    summary = call_doubao_ai(test_alerts)
    print("AI摘要：", summary)
