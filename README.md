# GitHub Copilot Workshop

This is a sample repository for GitHub Copilot Workshop.

Using the files in this repository, we created a fully functional **Pomodoro Timer Web Application** using Python (Flask), JavaScript, HTML, and CSS.

## 🎯 What is This Project?

A production-ready Pomodoro Timer web application that helps you stay focused and productive using the Pomodoro Technique. The app features:

- 🔐 **User authentication** with registration and login
- 👤 **Personal session tracking** - each user has their own history
- ⏱️ **25-minute work sessions** with short and long breaks
- 📊 **Session tracking** with visual progress indicators
- ⚙️ **Customizable timers** for work and break durations
- 📝 **Automatic database logging** of all sessions
- 🔔 **Browser notifications** when sessions complete
- 📱 **Responsive design** that works on all devices


## 📚 Documentation

- **[Architecture](architecture.md)** - System design and technical architecture
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Detailed development progress and features
- **[Pomodoro App README](pomodoro_app/README.md)** - Application-specific documentation
- **[Development Plan](plan.md)** - Original project plan and requirements
- **[Pomodoro Technique Guide](Pomodoro_Technique.md)** - Learn about the productivity method

## 🚀 Quick Start

### Prerequisites

You need to have `uv` installed for this project.

#### Installing uv

`uv` is an extremely fast Python package and project manager, written in Rust. Install it using one of these methods:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or visit the [official installation guide](https://docs.astral.sh/uv/#installation) for more options.

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/eComindo/2025-github-ur-copilot-workshop.git
   cd 2025-github-ur-copilot-workshop
   ```

2. **Create and activate virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   cd pomodoro_app
   flask init-db
   ```
   
   Or the database will be automatically created when you first run the app.

5. **Set environment variables (optional):**
   ```bash
   export SECRET_KEY='your-secret-key-here'
   export DATABASE_URL='sqlite:///pomodoro.db'  # Default if not set
   ```

6. **Run the application:**
   ```bash
   python app.py
   ```

7. **Open your browser:**
   Navigate to `http://127.0.0.1:5000`

8. **Create your account:**
   - Click "Register here" on the login page
   - Fill in username, email, and password
   - You'll be automatically logged in after registration

### Deactivating Virtual Environment

When you're done working:
```bash
deactivate
```

## 📁 Project Structure

```
2025-github-ur-copilot-workshop/
├── pomodoro_app/           # Main application directory
│   ├── app.py             # Flask backend server
│   ├── models.py          # Database models (User, Session)
│   ├── static/            # CSS and JavaScript files
│   │   ├── style.css      # Application styling
│   │   └── timer.js       # Timer logic and UI interactions
│   ├── templates/         # HTML templates
│   │   ├── index.html     # Main application page
│   │   ├── login.html     # Login page
│   │   └── register.html  # Registration page
│   ├── test_app.py        # Legacy test suite
│   ├── test_pomodoro.py   # Updated test suite with auth
│   ├── test_auth.py       # Authentication tests
│   ├── pomodoro.db        # SQLite database (generated)
│   └── README.md          # App-specific documentation
├── wsgi.py                # WSGI entry point for production
├── startup.txt            # Azure deployment startup command
├── requirements.txt       # Python dependencies
├── architecture.md        # Technical architecture
├── IMPLEMENTATION_SUMMARY.md  # Development summary
└── README.md             # This file
```

## 🔧 Dependencies

The project uses the following Python packages:

- **Flask 3.1.2** - Web framework
- **Flask-SQLAlchemy 3.1.1** - Database ORM
- **Flask-Login 0.6.3** - User session management
- **Flask-Bcrypt 1.0.1** - Password hashing
- **gunicorn 21.2.0** - Production WSGI server
- **requests 2.32.5** - HTTP library for testing
- **pytest 9.0.1** - Testing framework
- **pytest-cov 7.0.0** - Code coverage plugin for pytest
- **pytest-flask 1.3.0** - Flask-specific pytest utilities

## 🌟 Key Features

### Authentication & User Management
- Secure user registration with email validation
- Login with username or email
- Password hashing using bcrypt
- Session-based authentication with Flask-Login
- User-specific session history and data isolation

### Timer Functionality
- Accurate countdown timer with pause/resume
- Automatic transitions between work and break sessions
- Visual progress tracking through 4-session cycles
- Skip to next session option

### User Experience
- Modern, clean interface
- Responsive design for mobile and desktop
- Customizable session durations
- Persistent settings using localStorage
- Browser notifications

### Data Management
- SQLite database for user and session storage
- Automatic session logging to database
- Timestamped entries for all events
- Session history API endpoint (per user)
- Completion vs. skip tracking
- Data isolation between users

## ⚙️ Configuration

### Environment Variables

The application supports the following environment variables:

- `SECRET_KEY` - Secret key for session management (required in production)
  - Default: `'dev-secret-key-change-in-production'`
  - **Important**: Set a strong random key in production
  
- `DATABASE_URL` - Database connection string
  - Default: `'sqlite:///pomodoro.db'`
  - Example: `'postgresql://user:pass@localhost/dbname'` for PostgreSQL
  
- `FLASK_ENV` - Environment mode
  - Values: `'development'` or `'production'`
  - Default: `'production'`

### Database Initialization

The database is automatically created when you first run the application. Alternatively, you can manually initialize it:

```bash
cd pomodoro_app
flask init-db
```

This creates the SQLite database file (`pomodoro.db`) with the following tables:
- **users** - User accounts with authentication credentials
- **sessions** - Pomodoro session history linked to users

### Creating Your First User

After starting the application:
1. Navigate to `http://127.0.0.1:5000`
2. You'll be redirected to the login page
3. Click "Register here"
4. Fill in:
   - Username (unique)
   - Email (unique)
   - Password (minimum 6 characters)
5. Click "Register"
6. You'll be automatically logged in and redirected to the timer

## 🚢 Deployment

The application is deployed on **Azure App Service** using:
- **WSGI server**: Gunicorn
- **Configuration**: See `wsgi.py` and `startup.txt`
- **Environment**: Production-ready Flask configuration

### Testing the Deployed API

```bash
# Check session history
curl http://pomodoro-timer-ecomindo-1763110994.azurewebsites.net/history
```

## 🛠️ Development

### Running Unit Tests

The project includes comprehensive unit tests for all Flask routes, authentication, and functionality. Tests are located in:
- `pomodoro_app/test_pomodoro.py` - Core functionality tests (15 test cases)
- `pomodoro_app/test_auth.py` - Authentication tests (26 test cases)

**Total: 41 test cases** with comprehensive coverage of authentication and session management.

**Run all tests:**
```bash
cd pomodoro_app
pytest test_pomodoro.py test_auth.py -v
```

**Run authentication tests only:**
```bash
cd pomodoro_app
pytest test_auth.py -v
```

**Run core functionality tests:**
```bash
cd pomodoro_app
pytest test_pomodoro.py -v
```

**Run tests with coverage report (terminal):**
```bash
cd pomodoro_app
pytest test_pomodoro.py test_auth.py --cov=app --cov=models --cov-report=term-missing
```

**Run tests with HTML coverage report:**
```bash
cd pomodoro_app
pytest test_pomodoro.py test_auth.py --cov=app --cov=models --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html` that you can open in your browser to see detailed line-by-line coverage.

**Run specific test classes:**
```bash
# Test authentication flows
pytest test_auth.py::TestUserRegistration -v
pytest test_auth.py::TestUserLogin -v

# Test protected endpoints
pytest test_auth.py::TestProtectedEndpoints -v

# Test session isolation
# Test session isolation
pytest test_auth.py::TestSessionHistory -v
```

**Run tests with extra verbose output:**
```bash
pytest test_pomodoro.py test_auth.py -vv
```

### Test Results

All 41 tests pass successfully:
```
======================= 41 passed in 19.43s =======================
```
======================= 41 passed in 19.43s =======================
```

### What's Being Tested

The unit tests cover:

#### Core Functionality (test_pomodoro.py)
- ✅ **Index Route** - Authentication requirements and access control
- ✅ **Session Logging** - All session types with authentication
- ✅ **Session History** - User-specific history retrieval
- ✅ **Protected Endpoints** - Authorization checks

#### Authentication (test_auth.py)
- ✅ **User Registration** - New user creation, duplicate handling, validation
- ✅ **User Login** - Username/email login, password validation
- ✅ **User Logout** - Session termination
- ✅ **Protected Endpoints** - Login requirements for all routes
- ✅ **Session Logging** - Authenticated session creation
- ✅ **Session History** - User-specific data isolation
- ✅ **Database Models** - User and Session model relationships

### Running in Debug Mode

The app runs in debug mode by default during local development:
```bash
python app.py
```

## 🤝 Contributing

This project was built as part of a GitHub Copilot workshop. Feel free to:
- Fork the repository
- Create feature branches
- Submit pull requests
- Open issues for bugs or enhancements

## 📖 Learning Resources

This project demonstrates:
- **Flask web development** with modern Python
- **Frontend-backend integration** using AJAX
- **Session management** and logging
- **Responsive web design** with CSS
- **Production deployment** to Azure
- **Test-driven development** practices

## 📄 License

This project is open source and available for educational purposes.
