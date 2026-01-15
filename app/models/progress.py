from datetime import datetime
from app import db


class Progress(db.Model):
    """Progress model - tracks user progress through content"""
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False, index=True)
    completion_percentage = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)  # 0.00 to 100.00
    last_position = db.Column(db.Integer, nullable=True)  # Last video position in seconds, etc.
    notes = db.Column(db.Text, nullable=True)
    bookmarked = db.Column(db.Boolean, default=False, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: one progress record per user-content pair
    __table_args__ = (db.UniqueConstraint('user_id', 'content_id', name='unique_user_progress'),)

    def __repr__(self):
        return f'<Progress user_id={self.user_id} content_id={self.content_id} {self.completion_percentage}%>'

    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'completion_percentage': float(self.completion_percentage) if self.completion_percentage else 0.0,
            'last_position': self.last_position,
            'notes': self.notes,
            'bookmarked': self.bookmarked,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

