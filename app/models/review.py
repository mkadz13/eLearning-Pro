from datetime import datetime
from app import db
from sqlalchemy import CheckConstraint


class Review(db.Model):
    """Review model - user reviews and ratings for content"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    is_verified_purchase = db.Column(db.Boolean, default=False, nullable=False)
    helpful_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: one review per user-content pair
    __table_args__ = (
        db.UniqueConstraint('user_id', 'content_id', name='unique_user_review'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range')
    )

    def __repr__(self):
        return f'<Review {self.id} rating={self.rating}>'

    def to_dict(self, include_user=False):
        """Convert review to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'is_verified_purchase': self.is_verified_purchase,
            'helpful_count': self.helpful_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'full_name': self.user.full_name,
                'avatar_url': self.user.avatar_url
            } if self.user else None
        
        return data

