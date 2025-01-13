import os
import json

# Book and Library classes
class Book:
    def __init__(self, book_id, title, author, quantity, borrowed=0):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.quantity = quantity  # Total quantity of the book
        self.borrowed = borrowed  # Number of borrowed copies

    def available_quantity(self):
        return self.quantity - self.borrowed

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "quantity": self.quantity,
            "borrowed": self.borrowed
        }

    @classmethod
    def from_dict(cls, data): 
        return cls(data["book_id"], data["title"], data["author"], data["quantity"], data["borrowed"])



class Library:
    FILE_PATH = "library_books.json"

    def __init__(self):
        self.books = self.load_books()

    def add_book(self, book):
        for b in self.books:
            if b.book_id == book.book_id:
                b.quantity += book.quantity
                self.save_books()
                return True
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

    def borrow_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id and book.available_quantity() > 0:
                book.borrowed += 1
                self.save_books()
                return True
        return False

    def return_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id and book.borrowed > 0:
                book.borrowed -= 1
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

    def search_and_select_books(self):
        keyword = input("Enter keyword to search: ")
        found_books = [book for book in self.books if keyword.lower() in book.title.lower() or keyword.lower() in book.author.lower()]
        
        if found_books:
            print("\nSearch Results:")
            for index, book in enumerate(found_books, start=1):
                print(f"{index}. ID: {book.book_id}, Title: {book.title}, Author: {book.author}, Total: {book.quantity}, Borrowed: {book.borrowed}, Available: {book.available_quantity()}")
            
            options = [str(i) for i in range(len(found_books) + 1)]
            choice = get_input("\nSelect a book by number (or 0 to cancel): ", options)
            
            if choice == "0":
                print("Search canceled.")
                return
            else:
                selected_book = found_books[int(choice) - 1]
                print(f"\nYou selected: ID: {selected_book.book_id}, Title: {selected_book.title}, Author: {selected_book.author}")
                self.next_action(selected_book)
        else:
            print("\nNo books found matching the keyword.")

    def next_action(self, book):
        options = ["1", "2", "3"]
        while True:
            print("\nWhat would you like to do with this book?")
            print("1. Borrow Book")
            print("2. Return Book")
            print("3. Back to Main Menu")
            
            choice = get_input("Enter your choice: ", options)

            if choice == "1":
                if library.borrow_book(book.book_id):
                    print("Book borrowed successfully.")
                else:
                    print("Book not available or already borrowed. Please try again.")
            elif choice == "2":
                if not book.borrowed:
                    print("This book is not borrowed.")
                else:
                    self.return_book(book.book_id)
                    print("Book returned successfully.")
            elif choice == "3":
                print("Returning to main menu...")
                break


# Initialize library
library = Library()

# Main menu function
def main_menu():
    options = ["1", "2", "3", "4", "5","6","7"]
    while True:
        print("\nLibrary Management System")
        print("1. List Books")
        print("2. Add Book")
        print("3. Remove Book")
        print("4. Search Books")
        print("5. Bowrrow Book")
        print("6. Return Book")
        print("7. Exit")
        
        choice = get_input("Enter your choice: ", options)

        if choice == "1":
            list_books()
        elif choice == "2":
            add_book()
        elif choice == "3":
            remove_book()
        elif choice == "4":
            library.search_and_select_books()
        elif choice == "5" :
            borrow_book()
        elif choice == "6":
            return_book()       
        elif choice == "7":
            print("Exiting the system. Goodbye!")
            break


# Function to list all books
def list_books():
    books = library.list_books()
    if books:
        print("\nList of Books:")
        for book in books:
            status = "Borrowed" if book.borrowed > 0 else "Available"
            print(f"ID: {book.book_id}, Title: {book.title}, Author: {book.author}, Total: {book.quantity}, Borrowed: {book.borrowed}, Available: {book.available_quantity()}, Status: {status}")
    else:
        print("\nNo books available in the library.")


# Function to add a new book
def add_book():
    book_id = input("Enter Book ID: ")
    title = input("Enter Book Title: ")
    author = input("Enter Book Author: ")
    quantity = int(input("Enter Quantity: "))
    if library.add_book(Book(book_id, title, author,quantity)):
        print("Book added successfully.")
    else:
        print("Book ID already exists. Please try again.")


# Function to remove a book
def remove_book():
    book_id = input("Enter Book ID to remove: ")
    
    for book in library.books:
        if book.book_id == book_id:
            print(f"Total copies available: {book.quantity}")
            copies_to_remove = int(input("Enter number of copies to remove: "))
            
            if copies_to_remove > book.quantity:
                print("Error: You cannot remove more copies than currently available.")
                return
            
            book.quantity -= copies_to_remove
            
            if book.quantity == 0:
                library.books.remove(book)
                print("All copies removed. Book deleted from the library.")
            else:
                library.save_books()
                print(f"{copies_to_remove} copies removed. Remaining copies: {book.quantity}")
            
            return
    
    print("Book not found. Please try again.")

def borrow_book():
    book_id = input("Enter Book ID to borrow: ")
    
    for book in library.books:
        if book.book_id == book_id:
            print(f"Total copies available: {book.available_quantity()}")
            copies_to_borrow = int(input("Enter number of copies to borrow: "))
            
            if copies_to_borrow > book.available_quantity():
                print("Error: Not enough copies available to borrow.")
                return
            
            book.borrowed += copies_to_borrow
            library.save_books()
            print(f"{copies_to_borrow} copies borrowed successfully.")
            return
    
    print("Book not found. Please try again.")


def return_book():
    book_id = input("Enter Book ID to return: ")
    
    for book in library.books:
        if book.book_id == book_id:
            print(f"Copies currently borrowed: {book.borrowed}")
            copies_to_return = int(input("Enter number of copies to return: "))
            
            if copies_to_return > book.borrowed:
                print("Error: You cannot return more copies than you have borrowed.")
                return
            
            book.borrowed -= copies_to_return
            library.save_books()
            print(f"{copies_to_return} copies returned successfully.")
            return
    
    print("Book not found. Please try again.")


# Helper function to handle input with validation
def get_input(prompt, valid_options):
    while True:
        user_input = input(prompt)
        if user_input in valid_options:
            return user_input
        print("Invalid input. Please try again.")


# Run the program
if __name__ == "__main__":
    main_menu()
