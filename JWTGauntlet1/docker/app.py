import jwt  # Using PyJWT 2.3.0
from flask import Flask, make_response, render_template, request

app = Flask(__name__, static_folder="static", static_url_path="")


def is_admin(request) -> bool:
    token = request.cookies.get("session")
    if token is None:
        return False

    try:
        with open("pub.key", "r") as f:
            key = f.read().strip()
    except:
        return False

    try:
        header = jwt.get_unverified_header(token)
        alg = header["alg"]

        data = jwt.decode(token, key, algorithms=[alg])
        return data.get("admin", False)
    except:
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


@app.route("/pub")
def publish_public_key():
    try:
        with open("pub.key") as f:
            key = f.read().strip()
        return key
    except:
        return render_template("403.html", error="Cannot find public key")


def create_token():
    payload = {"admin": False}
    with open("priv.key", "r") as f:
        key = f.read().strip()
    token = jwt.encode(payload, key, algorithm="ES256")
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
