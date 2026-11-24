import base64
import random

import jwt
from cryptography.hazmat.primitives import serialization
from flask import Flask, make_response, render_template, request

app = Flask(__name__, static_folder="static", static_url_path="")

def is_admin(request) -> bool:
    token = request.cookies.get("session")
    if token is None:
        return False

    try:
        header = jwt.get_unverified_header(token)
        jwk = jwt.PyJWK(header["jwk"])
        kid = header["kid"]

        if kid == jwk.key_id:
            key = jwk.key
        else:
            return False

        data = jwt.decode(token, key, algorithms=["RS256"], audience="is_admin")
        return data.get("admin", False)
    except Exception as e:
        return False

def admin_only(f):
    def wrapper():
        if is_admin(request):
            return f()
        else:
            return render_template("403.html", error="Access Denied")

    return wrapper

@app.route("/admin")
@admin_only
def admin_page():
    flag = ""
    with open("flag.txt", "r") as f:
        flag = f.read().strip()
    return flag

def b64_uint(n: int) -> str:
    byte_length = (n.bit_length() + 7) // 8
    return base64.b64encode(n.to_bytes(byte_length, "big")).rstrip(b"=").decode()

def create_token():
    payload = {"admin": False, "aud": "is_admin"}
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

@app.route("/")
def index():
    resp = make_response(render_template("index.html", is_admin=is_admin(request)))
    token = request.cookies.get("session")
    if token is None:
        new_token = create_token()
        resp.set_cookie("session", new_token)
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
