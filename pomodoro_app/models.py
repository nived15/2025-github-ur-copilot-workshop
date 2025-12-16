"""
Database models for Pomodoro Timer application
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow())
    
    # Relationship with sessions
    sessions = db.relationship('Session', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Session(db.Model):
    """Session model for storing pomodoro sessions"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow())
    session_type = db.Column(db.String(20), nullable=False)  # work, short_break, long_break
    action = db.Column(db.String(20), nullable=False)  # completed, skipped
    session_number = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<Session {self.session_type} - {self.action} by User {self.user_id}>'
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'session_type': self.session_type,
            'action': self.action,
            'session_number': f'session_{self.session_number}'
        }
