import os
import time
import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv()

KID = os.getenv("QWEATHER_CREDENTIAL_ID")      # 控制台里的 kid
PROJECT_ID = os.getenv("QWEATHER_PROJECT_ID")  # 控制台里的 projectId（sub）
PRIVATE_KEY_PATH = os.getenv("QWEATHER_PRIVATE_KEY_PATH")  # 私钥路径（PEM）

def load_private_key(path: str):
    with open(path, "rb") as f:
        private_bytes = f.read()
        key = serialization.load_pem_private_key(private_bytes, password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise TypeError("私钥类型不是Ed25519，请检查PEM文件。")
        return key

def generate_jwt_token():
    now = int(time.time())
    payload = {
        "sub": PROJECT_ID,
        "iat": now - 30,
        "exp": now + 1800
    }
    headers = {
        "alg": "EdDSA",
        "kid": KID
    }
    
    if not PRIVATE_KEY_PATH:
        raise ValueError("QWEATHER_PRIVATE_KEY_PATH 环境变量未设置")
    private_key = load_private_key(PRIVATE_KEY_PATH)
    token = jwt.encode(
        payload,
        key=private_key,
        algorithm="EdDSA",
        headers=headers
    )
    return token
