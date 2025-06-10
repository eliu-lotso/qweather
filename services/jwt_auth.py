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

def load_private_key(path: str) -> Ed25519PrivateKey:
    with open(path, "rb") as f:
        private_bytes = f.read()
        return serialization.load_pem_private_key(private_bytes, password=None)

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
    

    private_key = load_private_key(PRIVATE_KEY_PATH)
    token = jwt.encode(
        payload,
        key=private_key,
        algorithm="EdDSA",
        headers=headers
    )
    return token
