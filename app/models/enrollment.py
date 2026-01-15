from datetime import datetime
from app import db


class Enrollment(db.Model):
    """Enrollment model - tracks student enrollments in content"""
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False, index=True)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    last_accessed_at = db.Column(db.DateTime, nullable=True)

    # Unique constraint: one enrollment per user-content pair
    __table_args__ = (db.UniqueConstraint('user_id', 'content_id', name='unique_user_content'),)

    def __repr__(self):
        return f'<Enrollment user_id={self.user_id} content_id={self.content_id}>'

    def to_dict(self):
        """Convert enrollment to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_completed': self.is_completed,
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
        }

