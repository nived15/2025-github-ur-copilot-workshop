"""
Unit tests for Pomodoro Timer authentication and user management
"""
import pytest
import json
import os
import tempfile
from app import app, db
from models import User, Session


@pytest.fixture
def client():
    """Create a test client with a temporary database"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        # Drop all tables and recreate to ensure clean state
        db.drop_all()
        db.create_all()
        
        # Create a test user
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt(app)
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(test_user)
        db.session.commit()
    
    with app.test_client() as client:
        yield client
    
    # Cleanup
    with app.app_context():
        db.session.remove()
        db.drop_all()
    os.close(db_fd)
    os.unlink(db_path)


class TestUserRegistration:
    """Tests for user registration"""
    
    def test_register_page_loads(self, client):
        """Test that registration page loads"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data or b'register' in response.data
    
    def test_register_new_user_success(self, client):
        """Test successful user registration"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify user was created
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
    
    def test_register_duplicate_username(self, client):
        """Test registration with existing username"""
        response = client.post('/register', data={
            'username': 'testuser',  # Already exists
            'email': 'another@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Username already exists' in response.data or b'already exists' in response.data
    
    def test_register_duplicate_email(self, client):
        """Test registration with existing email"""
        response = client.post('/register', data={
            'username': 'anotheruser',
            'email': 'test@example.com',  # Already exists
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Email already exists' in response.data or b'already exists' in response.data
    
    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post('/register', data={
            'username': 'incomplete',
            'email': ''
        })
        
        assert response.status_code == 200
        assert b'required' in response.data.lower() or b'error' in response.data.lower()
    
    def test_register_api_endpoint(self, client):
        """Test registration via JSON API"""
        response = client.post('/register',
                               data=json.dumps({
                                   'username': 'apiuser',
                                   'email': 'api@example.com',
                                   'password': 'apipassword123'
                               }),
                               content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert 'apiuser' in json_data['username']


class TestUserLogin:
    """Tests for user login"""
    
    def test_login_page_loads(self, client):
        """Test that login page loads"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
    
    def test_login_with_username_success(self, client):
        """Test successful login with username"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to index page
        assert b'Pomodoro Timer' in response.data
    
    def test_login_with_email_success(self, client):
        """Test successful login with email"""
        response = client.post('/login', data={
            'username': 'test@example.com',  # Can use email in username field
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_invalid_password(self, client):
        """Test login with invalid password"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'invalid' in response.data
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'invalid' in response.data
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post('/login', data={
            'username': 'testuser'
        })
        
        assert response.status_code == 200
        assert b'required' in response.data.lower() or b'error' in response.data.lower()
    
    def test_login_api_endpoint(self, client):
        """Test login via JSON API"""
        response = client.post('/login',
                               data=json.dumps({
                                   'username': 'testuser',
                                   'password': 'password123'
                               }),
                               content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'


class TestUserLogout:
    """Tests for user logout"""
    
    def test_logout_redirects_to_login(self, client):
        """Test that logout redirects to login page"""
        # First login
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data


class TestProtectedEndpoints:
    """Tests for protected endpoints requiring authentication"""
    
    def test_index_requires_login(self, client):
        """Test that index page requires login"""
        response = client.get('/')
        # Should redirect to login
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_log_requires_login(self, client):
        """Test that /log endpoint requires login"""
        response = client.post('/log',
                               data=json.dumps({
                                   'session_type': 'work',
                                   'action': 'completed',
                                   'session_number': 1
                               }),
                               content_type='application/json')
        
        # Should return 401 or redirect
        assert response.status_code in [302, 401]
    
    def test_history_requires_login(self, client):
        """Test that /history endpoint requires login"""
        response = client.get('/history')
        # Should return 401 or redirect
        assert response.status_code in [302, 401]
    
    def test_index_accessible_after_login(self, client):
        """Test that index page is accessible after login"""
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Access index
        response = client.get('/')
        assert response.status_code == 200
        assert b'Pomodoro Timer' in response.data


class TestSessionLogging:
    """Tests for session logging with authentication"""
    
    def test_log_session_authenticated(self, client):
        """Test logging a session when authenticated"""
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Log a session
        response = client.post('/log',
                               data=json.dumps({
                                   'session_type': 'work',
                                   'action': 'completed',
                                   'session_number': 1
                               }),
                               content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        
        # Verify session was created in database
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            sessions = Session.query.filter_by(user_id=user.id).all()
            assert len(sessions) > 0
            assert sessions[-1].session_type == 'work'
    
    def test_log_multiple_sessions(self, client):
        """Test logging multiple sessions"""
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Log multiple sessions
        session_data = [
            {'session_type': 'work', 'action': 'completed', 'session_number': 1},
            {'session_type': 'short_break', 'action': 'completed', 'session_number': 1},
            {'session_type': 'work', 'action': 'skipped', 'session_number': 2}
        ]
        
        for data in session_data:
            response = client.post('/log',
                                   data=json.dumps(data),
                                   content_type='application/json')
            assert response.status_code == 200


class TestSessionHistory:
    """Tests for session history per user"""
    
    def test_get_history_authenticated(self, client):
        """Test getting history when authenticated"""
        # Login
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Log some sessions
        client.post('/log',
                    data=json.dumps({
                        'session_type': 'work',
                        'action': 'completed',
                        'session_number': 1
                    }),
                    content_type='application/json')
        
        # Get history
        response = client.get('/history')
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'sessions' in json_data
        assert len(json_data['sessions']) > 0
    
    def test_history_isolation_between_users(self, client):
        """Test that users only see their own sessions"""
        # Create a second user and login
        with app.app_context():
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(app)
            user2 = User(
                username='testuser2',
                email='test2@example.com',
                password_hash=bcrypt.generate_password_hash('password123').decode('utf-8')
            )
            db.session.add(user2)
            db.session.commit()
        
        # Login as first user and log a session
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        client.post('/log',
                    data=json.dumps({
                        'session_type': 'work',
                        'action': 'completed',
                        'session_number': 1
                    }),
                    content_type='application/json')
        
        # Logout
        client.get('/logout')
        
        # Login as second user
        client.post('/login', data={
            'username': 'testuser2',
            'password': 'password123'
        })
        
        # Get history - should be empty
        response = client.get('/history')
        json_data = response.get_json()
        assert len(json_data['sessions']) == 0
    
    def test_history_returns_correct_format(self, client):
        """Test that history returns correct data format"""
        # Login and log a session
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        client.post('/log',
                    data=json.dumps({
                        'session_type': 'work',
                        'action': 'completed',
                        'session_number': 5
                    }),
                    content_type='application/json')
        
        # Get history
        response = client.get('/history')
        json_data = response.get_json()
        
        assert len(json_data['sessions']) > 0
        session = json_data['sessions'][-1]
        
        # Verify structure
        assert 'timestamp' in session
        assert 'session_type' in session
        assert 'action' in session
        assert 'session_number' in session
        assert session['session_type'] == 'work'
        assert session['action'] == 'completed'


class TestDatabaseModels:
    """Tests for database models"""
    
    def test_user_creation(self, client):
        """Test User model creation"""
        with app.app_context():
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(app)
            
            user = User(
                username='modeltest',
                email='model@test.com',
                password_hash=bcrypt.generate_password_hash('test123').decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            
            # Query back
            found_user = User.query.filter_by(username='modeltest').first()
            assert found_user is not None
            assert found_user.email == 'model@test.com'
    
    def test_session_creation(self, client):
        """Test Session model creation"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            session = Session(
                user_id=user.id,
                session_type='work',
                action='completed',
                session_number=1
            )
            db.session.add(session)
            db.session.commit()
            
            # Query back
            found_session = Session.query.filter_by(user_id=user.id).first()
            assert found_session is not None
            assert found_session.session_type == 'work'
    
    def test_user_session_relationship(self, client):
        """Test relationship between User and Session"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # Create sessions
            for i in range(3):
                session = Session(
                    user_id=user.id,
                    session_type='work',
                    action='completed',
                    session_number=i+1
                )
                db.session.add(session)
            db.session.commit()
            
            # Access via relationship
            user = User.query.filter_by(username='testuser').first()
            assert len(user.sessions) >= 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
