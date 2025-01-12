import os
import json

# Constants for file paths
BOOKS_FILE = "books.json"
BORROWED_FILE = "borrowed_books.json"
USERS_FILE = "users.json"

# Data Structures
books = []  # List of book dictionaries
borrowed_books = {}  # Book ID mapped to a list of borrower names
users = {}  # Username mapped to user details

# File Handling Functions
def save_data_to_file(file_name, data):
    """Save data to a JSON file."""
    try:
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error saving data to {file_name}: {e}")

def load_data_from_file(file_name, default_data):
    """Load data from a JSON file or return default data if file doesn't exist."""
    try:
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                data = json.load(file)
                if not isinstance(data, type(default_data)):  # Ensure data type consistency
                    return default_data
                return data
        return default_data
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading data from {file_name}: {e}")
        return default_data

# User Management Functions
def sign_up(username, password, other_details, role="user"):
    """Sign up a new user."""
    if username in users:
        print("Error: Username already exists.")
        return False
    try:
        users[username] = {
            "password": password,
            "role": role,
            "other_details": other_details
        }
        save_data_to_file(USERS_FILE, users)
        print("Sign-up successful.")
        return True
    except Exception as e:
        print(f"Error during sign-up: {e}")
        return False

def log_in(username, password):
    """Log in an existing user."""
    try:
        user = users.get(username)
        if not user or user["password"] != password:
            print("Error: Invalid username or password.")
            return None
        print(f"Welcome, {username}! Role: {user['role']}")
        return username, user["role"]
    except KeyError as e:
        print(f"Error during login: {e}")
        return None

def add_admin(username, password, other_details):
    """Add a new admin user."""
    sign_up(username, password, other_details, "admin")

# Book Management Functions
def add_book(book_id, title, author, copies):
    """Add or update a book in the library."""
    try:
        for book in books:
            if book["id"] == book_id:
                book["available_copies"] += copies
                save_data_to_file(BOOKS_FILE, books)
                print("Book updated successfully.")
                return
        books.append({"id": book_id, "title": title, "author": author, "available_copies": copies})
        save_data_to_file(BOOKS_FILE, books)
        print("Book added successfully.")
    except Exception as e:
        print(f"Error adding or updating book: {e}")

def remove_book(book_id):
    """Remove a book from the library."""
    try:
        global books
        books = [book for book in books if book["id"] != book_id]
        save_data_to_file(BOOKS_FILE, books)
        print("Book removed successfully.")
    except Exception as e:
        print(f"Error removing book: {e}")

def search_book(query):
    """Search for books by title or author."""
    try:
        results = [book for book in books if query.lower() in book["title"].lower() or query.lower() in book["author"].lower()]
        if results:
            for book in results:
                print(f"ID: {book['id']}, Title: {book['title']}, Author: {book['author']}, Available: {book['available_copies']}")
        else:
            print("No books found.")
    except Exception as e:
        print(f"Error searching for books: {e}")

# Borrow Management Functions
def borrow_book(book_id, borrower_name):
    """Borrow a book from the library."""
    try:
        for book in books:
            if book["id"] == book_id and book["available_copies"] > 0:
                book["available_copies"] -= 1
                borrowed_books.setdefault(book_id, []).append(borrower_name)
                save_data_to_file(BOOKS_FILE, books)
                save_data_to_file(BORROWED_FILE, borrowed_books)
                print("Book borrowed successfully.")
                return
        print("Error: Book not available.")
    except Exception as e:
        print(f"Error borrowing book: {e}")

def return_book(book_id, borrower_name):
    """Return a borrowed book to the library."""
    try:
        if book_id in borrowed_books and borrower_name in borrowed_books[book_id]:
            borrowed_books[book_id].remove(borrower_name)
            for book in books:
                if book["id"] == book_id:
                    book["available_copies"] += 1
                    break
            save_data_to_file(BOOKS_FILE, books)
            save_data_to_file(BORROWED_FILE, borrowed_books)
            print("Book returned successfully.")
        else:
            print("Error: No record of this book being borrowed by this user.")
    except Exception as e:
        print(f"Error returning book: {e}")

def list_borrowed_books():
    """List all borrowed books and their borrowers."""
    try:
        for book_id, borrowers in borrowed_books.items():
            book = next((b for b in books if b["id"] == book_id), None)
            if book:
                print(f"ID: {book_id}, Title: {book['title']}, Borrowers: {', '.join(borrowers)}")
    except Exception as e:
        print(f"Error listing borrowed books: {e}")

# Utility Functions
def display_menu(role):
    """Display the menu based on user role."""
    menu = {
        "admin": [
            "1. Add Book", "2. Remove Book", "3. Search Book", "4. View Borrowed Books", "5. Add Admin", "6. Log Out"
        ],
        "user": [
            "1. Search Book", "2. Borrow Book", "3. Return Book", "4. Log Out"
        ]
    }
    print(f"\n{'Admin' if role == 'admin' else 'User'} Menu")
    for option in menu.get(role, []):
        print(option)

def get_user_input(prompt):
    """Get input from the user."""
    try:
        return input(prompt).strip()
    except Exception as e:
        print(f"Error getting user input: {e}")
        return ""

# Main Workflow
def main():
    """Main function to run the Library Management System."""
    global books, borrowed_books, users

    # Load data
    books = load_data_from_file(BOOKS_FILE, [])
    borrowed_books = load_data_from_file(BORROWED_FILE, {})
    users = load_data_from_file(USERS_FILE, {})

    current_user = None
    while True:
        try:
            if not current_user:
                print("\nWelcome to the Library Management System")
                print("1. Sign Up")
                print("2. Log In")
                print("3. Exit")

                choice = get_user_input("Enter your choice: ")

                if choice == "1":
                    username = get_user_input("Enter username: ")
                    password = get_user_input("Enter password: ")
                    email = get_user_input("Enter email: ")
                    phone = get_user_input("Enter phone: ")
                    role = get_user_input("Enter role (admin/user): ")
                    sign_up(username, password, {"email": email, "phone": phone}, role)

                elif choice == "2":
                    username = get_user_input("Enter username: ")
                    password = get_user_input("Enter password: ")
                    current_user = log_in(username, password)

                elif choice == "3":
                    print("Exiting the system. Goodbye!")
                    break

                else:
                    print("Invalid choice. Please try again.")
            else:
                username, role = current_user
                display_menu(role)
                choice = get_user_input("Enter your choice: ")

                if role == "admin":
                    if choice == "1":
                        book_id = get_user_input("Enter Book ID: ")
                        title = get_user_input("Enter Book Title: ")
                        author = get_user_input("Enter Book Author: ")
                        copies = int(get_user_input("Enter number of copies: "))
                        add_book(book_id, title, author, copies)
                    elif choice == "2":
                        book_id = get_user_input("Enter Book ID to remove: ")
                        remove_book(book_id)
                    elif choice == "3":
                        query = get_user_input("Enter search query: ")
                        search_book(query)
                    elif choice == "4":
                        list_borrowed_books()
                    elif choice == "5":
                        admin_username = get_user_input("Enter new admin username: ")
                        admin_password = get_user_input("Enter password: ")
                        admin_email = get_user_input("Enter email: ")
                        admin_phone = get_user_input("Enter phone: ")
                        add_admin(admin_username, admin_password, {"email": admin_email, "phone": admin_phone})
                    elif choice == "6":
                        current_user = None
                    else:
                        print("Invalid choice. Please try again.")
                else:
                    if choice == "1":
                        query = get_user_input("Enter search query: ")
                        search_book(query)
                    elif choice == "2":
                        book_id = get_user_input("Enter Book ID to borrow: ")
                        borrow_book(book_id, username)
                    elif choice == "3":
                        book_id = get_user_input("Enter Book ID to return: ")
                        return_book(book_id, username)
                    elif choice == "4":
                        current_user = None
                    else:
                        print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
