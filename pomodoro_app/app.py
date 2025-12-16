from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import os
from models import db, User, Session

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///pomodoro.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Ensure log file exists (for backward compatibility)
LOG_FILE = 'pomodoro_log.txt'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return db.session.get(User, int(user_id))

@app.route('/')
@login_required
def index():
    """Serve the main timer page (requires authentication)"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username_or_email = data.get('username') or data.get('email')
        password = data.get('password')
        
        if not username_or_email or not password:
            if request.is_json:
                return jsonify({'status': 'error', 'message': 'Username/email and password are required'}), 400
            return render_template('login.html', error='Username/email and password are required')
        
        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            if request.is_json:
                return jsonify({'status': 'success', 'message': 'Login successful', 'username': user.username})
            return redirect(url_for('index'))
        
        if request.is_json:
            return jsonify({'status': 'error', 'message': 'Invalid username/email or password'}), 401
        return render_template('login.html', error='Invalid username/email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validate input
        if not username or not email or not password:
            if request.is_json:
                return jsonify({'status': 'error', 'message': 'Username, email, and password are required'}), 400
            return render_template('register.html', error='All fields are required')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({'status': 'error', 'message': 'Username already exists'}), 400
            return render_template('register.html', error='Username already exists')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'status': 'error', 'message': 'Email already exists'}), 400
            return render_template('register.html', error='Email already exists')
        
        # Create new user
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=password_hash)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Automatically log in the user
            login_user(new_user)
            
            if request.is_json:
                return jsonify({'status': 'success', 'message': 'Registration successful', 'username': new_user.username})
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'status': 'error', 'message': f'Registration failed: {str(e)}'}), 500
            return render_template('register.html', error=f'Registration failed: {str(e)}')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/log', methods=['POST'])
@login_required
def log_session():
    """Log pomodoro session events (requires authentication)"""
    try:
        data = request.get_json()
        
        # Extract session data
        session_type = data.get('session_type', 'work')  # work, short_break, long_break
        action = data.get('action', 'completed')  # completed, skipped
        session_number = data.get('session_number', 1)
        
        # Create new session in database
        new_session = Session(
            user_id=current_user.id,
            session_type=session_type,
            action=action,
            session_number=session_number
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Session logged successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/history')
@login_required
def get_history():
    """Retrieve session history for authenticated user"""
    try:
        # Get all sessions for the current user
        user_sessions = Session.query.filter_by(user_id=current_user.id).order_by(Session.timestamp).all()
        
        # Convert to dictionary format
        sessions = [session.to_dict() for session in user_sessions]
        
        return jsonify({'sessions': sessions})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print('Database initialized successfully!')

if __name__ == '__main__':
    # Use environment variables for production deployment
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)