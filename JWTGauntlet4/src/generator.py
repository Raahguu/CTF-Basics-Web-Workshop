import base64
import random

import jwt
from cryptography.hazmat.primitives import serialization


def b64_uint(n: int) -> str:
    byte_length = (n.bit_length() + 7) // 8
    return base64.b64encode(n.to_bytes(byte_length, "big")).rstrip(b"=").decode()

def create_token():
    payload = {"admin": True, "aud": "is_admin"}
    secret_key_path = "priv.key"
    with open(secret_key_path, "r") as f:
        key = f.read().strip()

    public_key_path = "pub.key"
    with open(public_key_path, "rb") as f:
        pub_key = serialization.load_pem_public_key(f.read().strip())

    numbers = pub_key.public_numbers()

    N = numbers.n
    e = numbers.e

    kid = str(random.randint(100000, 999999))

    token = jwt.encode(
        payload,
        key,
        algorithm="RS256",
        headers={
            "kid": kid,
            "jwk": {
                "kty": "RSA",
                "e": b64_uint(e),
                "kid": kid,
                "n": b64_uint(N),
            },
        },
    )
    return token
    
if __name__ == "__main__":
    print(create_token())
