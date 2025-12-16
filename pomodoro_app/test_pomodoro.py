"""
Unit tests for Pomodoro Timer Flask Application
Tests all routes and functionality with authentication
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


@pytest.fixture
def authenticated_client(client):
    """Create an authenticated client"""
    # Login the test user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    return client


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        temp_file_path = tmp_file.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)


class TestIndexRoute:
    """Tests for the index route"""
    
    def test_index_requires_authentication(self, client):
        """Test that index route requires authentication"""
        response = client.get('/')
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_index_returns_200_when_authenticated(self, authenticated_client):
        """Test that authenticated user can access index"""
        response = authenticated_client.get('/')
        assert response.status_code == 200
    
    def test_index_returns_html(self, authenticated_client):
        """Test that index route returns HTML content"""
        response = authenticated_client.get('/')
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


class TestLogSessionRoute:
    """Tests for the /log route"""
    
    def test_log_work_session_success(self, authenticated_client):
        """Test logging a completed work session"""
        data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 1
        }
        
        response = authenticated_client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
        assert 'Session logged successfully' in json_data['message']
    
    def test_log_short_break_session(self, authenticated_client):
        """Test logging a short break session"""
        data = {
            'session_type': 'short_break',
            'action': 'completed',
            'session_number': 2
        }
        
        response = authenticated_client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
    
    def test_log_long_break_session(self, authenticated_client):
        """Test logging a long break session"""
        data = {
            'session_type': 'long_break',
            'action': 'completed',
            'session_number': 4
        }
        
        response = authenticated_client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
    
    def test_log_skipped_session(self, authenticated_client):
        """Test logging a skipped session"""
        data = {
            'session_type': 'work',
            'action': 'skipped',
            'session_number': 3
        }
        
        response = authenticated_client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
    
    def test_log_with_default_values(self, authenticated_client):
        """Test logging with default values when optional fields are missing"""
        data = {}  # Empty data should use defaults
        
        response = authenticated_client.post('/log',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'
    
    def test_log_multiple_sessions(self, authenticated_client):
        """Test logging multiple sessions"""
        sessions = [
            {'session_type': 'work', 'action': 'completed', 'session_number': 1},
            {'session_type': 'short_break', 'action': 'completed', 'session_number': 1},
            {'session_type': 'work', 'action': 'completed', 'session_number': 2},
        ]
        
        for session in sessions:
            response = authenticated_client.post('/log',
                                  data=json.dumps(session),
                                  content_type='application/json')
            assert response.status_code == 200
    
    def test_log_with_invalid_json(self, authenticated_client):
        """Test logging with invalid JSON data"""
        response = authenticated_client.post('/log',
                              data='invalid json',
                              content_type='application/json')
        
        assert response.status_code == 500
        json_data = response.get_json()
        assert json_data['status'] == 'error'
    
    def test_log_without_authentication(self, client):
        """Test that logging requires authentication"""
        data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 1
        }
        
        response = client.post('/log', data=json.dumps(data), content_type='application/json')
        
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]


class TestHistoryRoute:
    """Tests for the /history route"""
    
    def test_history_empty_log(self, authenticated_client):
        """Test retrieving history when no sessions logged"""
        response = authenticated_client.get('/history')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'sessions' in json_data
        assert json_data['sessions'] == []
    
    def test_history_with_sessions(self, authenticated_client):
        """Test retrieving history with logged sessions"""
        # Log some sessions first
        sessions_data = [
            {'session_type': 'work', 'action': 'completed', 'session_number': 1},
            {'session_type': 'short_break', 'action': 'completed', 'session_number': 1},
        ]
        
        for session in sessions_data:
            authenticated_client.post('/log',
                       data=json.dumps(session),
                       content_type='application/json')
        
        # Retrieve history
        response = authenticated_client.get('/history')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'sessions' in json_data
        assert len(json_data['sessions']) == 2
        
        # Verify session data structure
        first_session = json_data['sessions'][0]
        assert 'timestamp' in first_session
        assert 'session_type' in first_session
        assert 'action' in first_session
        assert 'session_number' in first_session
        assert first_session['session_type'] == 'work'
        assert first_session['action'] == 'completed'
    
    def test_history_without_authentication(self, client):
        """Test retrieving history requires authentication"""
        response = client.get('/history')
        
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_history_returns_correct_structure(self, authenticated_client):
        """Test that history returns correct data structure"""
        # Log a session
        session_data = {
            'session_type': 'work',
            'action': 'completed',
            'session_number': 5
        }
        
        authenticated_client.post('/log',
                   data=json.dumps(session_data),
                   content_type='application/json')
        
        # Retrieve history
        response = authenticated_client.get('/history')
        json_data = response.get_json()
        
        assert len(json_data['sessions']) == 1
        session = json_data['sessions'][0]
        
        # Verify all fields are present
        assert session['session_type'] == 'work'
        assert session['action'] == 'completed'
        assert session['session_number'] == 'session_5'
        assert 'timestamp' in session

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
