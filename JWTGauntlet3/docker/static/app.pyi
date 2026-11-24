import sqlite3

import jwt
from flask import Flask, make_response, render_template, request

app = Flask(__name__, static_folder="static", static_url_path="")

def is_admin(request) -> bool:
    token = request.cookies.get("session")
    if token is None:
        return False

    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        output = []

        try:
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT value FROM keys WHERE kid = '{kid}';
                """)
            output = cursor.fetchall()
            conn.close()
        except:
            return False

        if output == []:
            return False

        data = jwt.decode(token, output[0][0], algorithms=["HS256"])
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

def create_token():
    payload = {"admin": False}
    kid = "12345"
    output = []
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT value FROM keys WHERE kid = '{kid}';
            """)
        output = cursor.fetchall()
        conn.close()
    except:
        return ""

    if output == []:
        raise Exception("Could not find the token's value")

    token = jwt.encode(payload, output[0][0], algorithm="HS256", headers={"kid": kid})
    return token

@app.route("/")
def index():
    # Get products
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, description FROM products;
            """)
        products = cursor.fetchall()
        conn.close()
    except:
        products = [["Error", "Could not read from database"]]

    resp = make_response(
        render_template("index.html", is_admin=is_admin(request), products=products)
    )
    token = request.cookies.get("session")
    if token is None:
        new_token = create_token()
        resp.set_cookie("session", new_token)
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
