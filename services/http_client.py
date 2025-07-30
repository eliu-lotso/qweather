#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络请求客户端模块
提供robust session和safe request功能
"""

import requests
import ssl
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_robust_session():
    """创建一个具有重试机制和SSL配置的requests session"""
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,  # 总重试次数
        backoff_factor=1,  # 重试间隔
        status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的HTTP状态码
        allowed_methods=["HEAD", "GET", "OPTIONS"]  # 允许重试的HTTP方法
    )
    
    # 创建适配器
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # 设置SSL配置
    session.verify = True  # 验证SSL证书
    
    return session

def safe_request(url, params=None, timeout=15, max_retries=2):
    """安全的HTTP请求，带有SSL错误处理和重试机制"""
    session = create_robust_session()
    
    for attempt in range(max_retries + 1):
        try:
            response = session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.SSLError as e:
            print(f"⚠️ SSL错误 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
            if attempt == max_retries:
                # 最后一次尝试：禁用SSL验证
                print("🔓 最后尝试：禁用SSL验证...")
                session.verify = False
                try:
                    response = session.get(url, params=params, timeout=timeout)
                    response.raise_for_status()
                    return response
                except Exception as final_e:
                    raise Exception(f"所有重试均失败，最后错误: {final_e}")
        except requests.exceptions.Timeout as e:
            print(f"⏰ 请求超时 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
            if attempt == max_retries:
                raise
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 连接错误 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
            if attempt == max_retries:
                raise
        except Exception as e:
            print(f"❌ 未知错误 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
            if attempt == max_retries:
                raise
        
        # 重试前等待
        if attempt < max_retries:
            import time
            time.sleep(2 ** attempt)  # 指数退避
    
    session.close() 