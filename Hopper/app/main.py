from flask import Flask, request, render_template, make_response, redirect
import sqlite3
from hashlib import sha256

app = Flask(__name__, static_url_path='')

global SECRET_LOGIN_TOKEN
SECRET_LOGIN_TOKEN = 'PizzaPizza123'

def is_logged_in(request):
	user =  request.cookies.get("user")
	global SECRET_LOGIN_TOKEN
	if sha256(f"ubuntu:ubuntu:{SECRET_LOGIN_TOKEN}".encode('utf-8')).hexdigest() == user: return True
	return False
    

@app.route("/", methods=["GET"])
def index():
	user = request.cookies.get("user")
	return render_template("index.html", logged_in=bool(user), user_id="3")

@app.route("/login", methods=["GET", "POST"])
def login():
	user = request.cookies.get("user")
	if request.method == "POST":
		username = request.form.get("username", "")
		password =request.form.get("password", "")
	
		if username == "ubuntu" == password:
			resp = make_response(redirect("/"))
			global SECRET_LOGIN_TOKEN
			resp.set_cookie("user", sha256(f"ubuntu:ubuntu:{SECRET_LOGIN_TOKEN}".encode('utf-8')).hexdigest())
			return resp
		else:
			return render_template("login.html", error="Invalid credentials", logged_in=bool(user))

	return render_template("login.html", error=None, logged_in=bool(user))
    
@app.route("/note/<int:noteID>", methods=["GET"])
def viewUser(noteID):
	if not is_logged_in(request): return make_response(redirect("/login"))
	try: 
		noteID = int(noteID)
		with open("notes/" + str(noteID)) as f:
			return render_template("note.html", text=f.read(), noteID=noteID)
	except: return render_template("note.html", text=f"Error: {str(noteID)} is not a valid note ID", noteID=noteID)
	

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=80)
