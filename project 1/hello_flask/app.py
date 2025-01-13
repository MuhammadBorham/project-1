from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json

app = Flask(__name__)
app.secret_key = "secret_key_for_flash_messages"

# Book and Library classes (same as before)
class Book:
    def __init__(self, book_id, title, author, is_borrowed=False):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.is_borrowed = is_borrowed

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "is_borrowed": self.is_borrowed
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["book_id"], data["title"], data["author"], data["is_borrowed"])


class Library:
    FILE_PATH = "library_books.json"

    def __init__(self):
        self.books = self.load_books()

    def add_book(self, book):
        if any(b.book_id == book.book_id for b in self.books):
            return False
        self.books.append(book)
        self.save_books()
        return True

    def remove_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id:
                self.books.remove(book)
                self.save_books()
                return True
        return False

    def search_books(self, keyword):
        return [book for book in self.books if keyword.lower() in book.title.lower() or keyword.lower() in book.author.lower()]

    def borrow_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id and not book.is_borrowed:
                book.is_borrowed = True
                self.save_books()
                return True
        return False

    def return_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id and book.is_borrowed:
                book.is_borrowed = False
                self.save_books()
                return True
        return False

    def list_books(self):
        return self.books

    def save_books(self):
        with open(self.FILE_PATH, "w") as file:
            json.dump([book.to_dict() for book in self.books], file)

    def load_books(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, "r") as file:
                data = json.load(file)
                return [Book.from_dict(item) for item in data]
        return []


# Initialize the library
library = Library()

@app.route("/")
def index():
    books = library.list_books()
    return render_template("index.html", books=books)


@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        book_id = request.form["book_id"]
        title = request.form["title"]
        author = request.form["author"]
        if library.add_book(Book(book_id, title, author)):
            flash("Book added successfully!", "success")
        else:
            flash("Book ID already exists. Please use a unique ID.", "danger")
        return redirect(url_for("index"))
    return render_template("add_book.html")


@app.route("/remove/<book_id>")
def remove_book(book_id):
    if library.remove_book(book_id):
        flash("Book removed successfully!", "success")
    else:
        flash("Book not found.", "danger")
    return redirect(url_for("index"))


@app.route("/borrow/<book_id>")
def borrow_book(book_id):
    if library.borrow_book(book_id):
        flash("Book borrowed successfully!", "success")
    else:
        flash("Book not available or already borrowed.", "danger")
    return redirect(url_for("index"))


@app.route("/return/<book_id>")
def return_book(book_id):
    if library.return_book(book_id):
        flash("Book returned successfully!", "success")
    else:
        flash("Book not found or not borrowed.", "danger")
    return redirect(url_for("index"))


@app.route("/search", methods=["GET", "POST"])
def search_books():
    if request.method == "POST":
        keyword = request.form["keyword"]
        books = library.search_books(keyword)
        return render_template("search_results.html", books=books, keyword=keyword)
    return render_template("search.html")


if __name__ == "__main__":
    app.run(debug=True)