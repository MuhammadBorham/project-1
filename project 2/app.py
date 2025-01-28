from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import os





# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@library.com'

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Author model
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    books = db.relationship('Book', backref='author', lazy=True)

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=1)
    borrowed = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    # Relationship to BorrowedBook
    borrowed_by = db.relationship('BorrowedBook', backref='borrowed_book', lazy=True)

# BorrowedBook model
class BorrowedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='borrowed_books')
    book = db.relationship('Book', backref='borrowed_books')

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Utility functions
def send_reset_email(user):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='password-reset')
    reset_url = url_for('reset_password', token=token, _external=True)
    msg = Message('Password Reset Request', recipients=[user.email])
    msg.body = f'To reset your password, visit the following link: {reset_url}'
    mail.send(msg)

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset', max_age=expiration)
    except:
        return None
    return User.query.filter_by(email=email).first()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        email = request.form.get('email', '').strip()
        user_type = request.form.get('user_type', 'normal')
        admin_password = request.form.get('admin_password', '').strip()

        # Validate required fields
        if not first_name or not last_name or not username or not password or not phone_number or not email:
            flash('All fields are required')
            return redirect(url_for('register'))

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))

        # Validate admin registration
        is_admin = user_type == 'admin' and admin_password == os.environ.get('ADMIN_PASSWORD', 'admin123')
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=generate_password_hash(password),
            phone_number=phone_number,
            email=email,
            is_admin=is_admin
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login_input']
        password = request.form['password']

        user = User.query.filter((User.username == login_input) | (User.email == login_input)).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            flash('Password reset instructions have been sent to your email.')
            return redirect(url_for('login'))
        else:
            flash('Email not found.')
    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = verify_reset_token(token)
    if not user:
        flash('Invalid or expired token')
        return redirect(url_for('reset_password_request'))
    if request.method == 'POST':
        password = request.form['password']
        user.password = generate_password_hash(password)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    welcome_message = f"Welcome, {current_user.first_name} {current_user.last_name}!"
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    # Filter books based on search query
    if search_query:
        books = Book.query.join(Author).filter(
            (Book.title.ilike(f'%{search_query}%')) | (Author.name.ilike(f'%{search_query}%'))
        ).paginate(page=page, per_page=10)
    else:
        books = Book.query.paginate(page=page, per_page=10)

    return render_template('dashboard.html', welcome_message=welcome_message, books=books, search_query=search_query)

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    author = Author.query.get(book.author_id)
    return render_template('book_details.html', book=book, author=author)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if not current_user.is_admin:
        flash('You do not have permission to add books')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        quantity = int(request.form['quantity'])
        author_id = request.form.get('author_id')
        new_author_name = request.form.get('new_author_name', '').strip()
        new_author_bio = request.form.get('new_author_bio', '').strip()

        # Validate author selection
        if not author_id and not new_author_name:
            flash('Please select an author or add a new one')
            return redirect(url_for('add_book'))

        # If a new author is provided, create it
        if new_author_name:
            author = Author.query.filter_by(name=new_author_name).first()
            if not author:
                author = Author(name=new_author_name, bio=new_author_bio)
                db.session.add(author)
                db.session.commit()
            author_id = author.id

        # Create new book
        new_book = Book(title=title, description=description, quantity=quantity, author_id=author_id)

        try:
            db.session.add(new_book)
            db.session.commit()
            flash('Book added successfully')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            return redirect(url_for('add_book'))

    # Fetch all authors for the dropdown
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)

@app.route('/add_author', methods=['GET', 'POST'])
@login_required
def add_author():
    if not current_user.is_admin:
        flash('You do not have permission to add authors')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        bio = request.form.get('bio', '')

        # Check if author already exists
        author = Author.query.filter_by(name=name).first()
        if author:
            flash('Author already exists')
            return redirect(url_for('add_author'))

        # Create new author
        new_author = Author(name=name, bio=bio)

        try:
            db.session.add(new_author)
            db.session.commit()
            flash('Author added successfully')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            return redirect(url_for('add_author'))

    return render_template('add_author.html')

@app.route('/author/<int:author_id>')
def author_details(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('author_details.html', author=author)

@app.route('/remove_author/<int:author_id>')
@login_required
def remove_author(author_id):
    if not current_user.is_admin:
        flash('You do not have permission to remove authors')
        return redirect(url_for('dashboard'))

    author = Author.query.get(author_id)
    if author:
        if author.books:
            flash('Cannot remove author with associated books')
        else:
            try:
                db.session.delete(author)
                db.session.commit()
                flash('Author removed successfully')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred. Please try again.')
    else:
        flash('Author not found')

    return redirect(url_for('dashboard'))

@app.route('/remove_book/<int:book_id>')
@login_required
def remove_book(book_id):
    if not current_user.is_admin:
        flash('You do not have permission to remove books')
        return redirect(url_for('dashboard'))

    book = Book.query.get(book_id)
    if book:
        try:
            # Delete all BorrowedBook records associated with this book
            BorrowedBook.query.filter_by(book_id=book.id).delete()

            # Now delete the book
            db.session.delete(book)
            db.session.commit()
            flash('Book removed successfully')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
    else:
        flash('Book not found')

    return redirect(url_for('dashboard'))

@app.route('/borrow_book/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get(book_id)
    if book and book.quantity > book.borrowed:
        try:
            book.borrowed += 1
            borrowed_book = BorrowedBook(user_id=current_user.id, book_id=book.id)
            db.session.add(borrowed_book)
            db.session.commit()
            flash('Book borrowed successfully')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
    else:
        flash('Book is not available')
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/borrowed_books')
@login_required
def borrowed_books():
    if not current_user.is_admin:
        flash('You do not have permission to view this page')
        return redirect(url_for('dashboard'))

    # Fetch all borrowed books with user and book details
    borrowed_books = BorrowedBook.query.join(User).join(Book).all()

    # Group borrowed books by book
    grouped_books = {}
    for borrowed_book in borrowed_books:
        book = borrowed_book.book
        if book not in grouped_books:
            grouped_books[book] = []
        grouped_books[book].append(borrowed_book)

    return render_template('borrowed_books.html', borrowed_books=grouped_books)

@app.route('/return_book/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash('Book not found')
        return redirect(url_for('dashboard'))

    # Allow admins to return any book, or users to return their own books
    if current_user.is_admin:
        borrowed_book = BorrowedBook.query.filter_by(book_id=book.id).first()
    else:
        borrowed_book = BorrowedBook.query.filter_by(book_id=book.id, user_id=current_user.id).first()

    if borrowed_book:
        try:
            book.borrowed -= 1
            db.session.delete(borrowed_book)
            db.session.commit()
            flash('Book returned successfully')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
    else:
        flash('You cannot return this book')

    return redirect(request.referrer or url_for('dashboard'))



# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)