import os
import smtplib
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename
import base64
from flask_migrate import Migrate


# Initialize the Flask application
app = Flask(__name__)
  
# Set up paths and configurations
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'users.db')  # SQLite database path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications for performance
app.config['SECRET_KEY'] = os.urandom(24)  # Generate a random secret key
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')  # Folder to store uploaded files

# Email configuration for password reset functionality
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Replace with actual email
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Replace with actual app-specific password
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Gmail SMTP server
app.config['MAIL_PORT'] = 587  # SMTP server port

# Initialize extensions
db = SQLAlchemy(app)  # SQLAlchemy for database interactions
bcrypt = Bcrypt(app)  # Bcrypt for password hashing
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])  # Serializer for generating secure tokens
migrate = Migrate(app, db)

# Register a Jinja filter to encode data in base64 format
@app.template_filter('b64encode')
def b64encode_filter(data):
    """Encode binary data into base64 string for rendering images."""
    return base64.b64encode(data).decode('utf-8')

# Define database models
class User(db.Model):
    """Model to store user information."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    uploads = db.relationship('Upload', backref='user', lazy=True)  # Relationship with Uploads table

class Upload(db.Model):
    """Model to store file uploads."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)  # Store file data in binary format
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)  # Automatically add timestamp
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User table

# Helper function to enforce login requirements
def login_required(f):
    """Decorator to restrict access to logged-in users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Define routes
@app.route('/')
def welcome():
    """Render the welcome page."""
    return render_template('welcome.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('register'))

        # Check if user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('register'))

        # Hash the password and save user to the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if 'user_id' in session:
        return redirect(url_for('upload_file'))  # Redirect logged-in users to upload page

    if request.method == 'POST':
        identifier = request.form['username']  # Can be username or email
        password = request.form['password']

        # Check if user exists
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if not user:
            flash('User does not exist. Please register first.', 'danger')
            return redirect(url_for('register'))

        # Validate password
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('upload_file'))
        else:
            flash('Login failed. Check your credentials.', 'danger')

    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset requests."""
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='password-reset-salt')
            link = url_for('reset_password', token=token, _external=True)
            send_email(email, 'Password Reset Request', f'Please click the link to reset your password: {link}')
            flash('Password reset instructions sent to your email.', 'info')
        else:
            flash('Email not found. Please register first.', 'danger')
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset the user's password using a secure token."""
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash('The password reset link has expired.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        user = User.query.filter_by(email=email).first()
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """Handle file uploads."""
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            data = file.read()
            new_upload = Upload(filename=filename, data=data, user_id=session['user_id'])
            db.session.add(new_upload)
            db.session.commit()
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('upload.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Display user uploads on the dashboard."""
    user = User.query.get(session['user_id'])
    uploads = Upload.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', user=user, uploads=uploads)

@app.route('/logout')
def logout():
    """Log out the user and clear the session."""
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('welcome'))

# Helper function to send emails
def send_email(to_email, subject, content):
    """Send an email using SMTP."""
    message = MIMEMultipart()
    message['From'] = app.config['MAIL_USERNAME']
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(content, 'html'))
    try:
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(app.config['MAIL_USERNAME'], to_email, message.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

# Ensure the 'instance' folder exists
os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

# Check if the database file exists, and create it if it doesn't
if not os.path.exists(os.path.join(basedir, 'instance', 'users.db')):
    with app.app_context():
        db.create_all()


# Run the application
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Ensure upload folder exists
    #db.create_all()  # Create database tables if not already created
    app.run(debug=True)  # Enable debug mode for development

