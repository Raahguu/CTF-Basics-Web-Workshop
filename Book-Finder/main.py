from flask import Flask, request, render_template, make_response
import random

app = Flask(__name__, static_url_path='')

books = {
    "1984":"George Orwell",
    "Hamlet":"William Shakespear",
    "The Odyssey": "Homer",
    "The Iliad": "Homer",
    "War and Peace": "Leo Tolstoy",
    "The Epic of Gilgamesh": "Unknown",
    "Media": "Euripides",
    "Hunger Games": "Suzanne Collins",
    "The Da Vinci Code": "Dan Brown",
    "The Book Thief": "Markus Zusak",
    "The Hobit": "J.R.R. Tolkien",
    "Ender's Game": "Orson Scott Card",
    "To Kill a Mockingbird": "Harper Lee",
    "Ready Player One": "Ernest Cline",
    "The Martian": "Andy Wier",
    "Hail Mary": "Andy Wier",
    "Artemis": "Andy Wier",
    "The Hitchhiker's Guide to The Galaxy": "Douglas Adams",
    "The Lord of the Rings": "J.R.R. Tolkien",
    "The Great Gatsby": "F.Scott Fitzgerald",
}

@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search", "").lower()
    results = []

    for book, author in books.items():
        if search in book.lower() or search in author.lower():
            results.append([book, author])
    
    resp =make_response(render_template("index.html", results=results, search=search, searched=(1 if search else 0)))
    resp.set_cookie("secret", str(random.randint(0, 256)))

    return resp

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=80)