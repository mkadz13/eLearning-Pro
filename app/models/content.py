from datetime import datetime
from app import db
from app.models.enrollment import Enrollment
from app.models.review import Review
from app.models.progress import Progress
from app.models.tag import content_tags
from sqlalchemy import func


class ContentType:
    VIDEO = 'video'
    ARTICLE = 'article'
    COURSE = 'course'
    QUIZ = 'quiz'
    EBOOK = 'ebook'
    PODCAST = 'podcast'


class Content(db.Model):
    """Content model - core learning material"""
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), nullable=False, index=True)
    content_url = db.Column(db.String(500), nullable=True)  # URL to actual content
    thumbnail_url = db.Column(db.String(500), nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)  # For video/audio content
    difficulty_level = db.Column(db.String(20), nullable=True)  # beginner, intermediate, advanced
    language = db.Column(db.String(10), default='en', nullable=False)
    price = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    is_free = db.Column(db.Boolean, default=True, nullable=False)
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    rating_average = db.Column(db.Numeric(3, 2), default=0.00, nullable=False)
    rating_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Foreign keys
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    
    # Metadata
    metadata_json = db.Column(db.JSON, nullable=True)  # Flexible metadata storage
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = db.relationship('Category', backref='content_items')
    enrollments = db.relationship('Enrollment', backref='content', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='content', lazy='dynamic', cascade='all, delete-orphan')
    progress = db.relationship('Progress', backref='content', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=content_tags, backref=db.backref('content_items', lazy='dynamic'))

    def __repr__(self):
        return f'<Content {self.title}>'

    def update_rating(self):
        """Update rating average and count from reviews"""
        rating_data = db.session.query(
            func.avg(Review.rating).label('avg'),
            func.count(Review.id).label('count')
        ).filter_by(content_id=self.id).first()
        
        if rating_data and rating_data.count > 0:
            self.rating_average = float(rating_data.avg) if rating_data.avg else 0.00
            self.rating_count = rating_data.count
        else:
            self.rating_average = 0.00
            self.rating_count = 0
        
        db.session.commit()

    def to_dict(self, include_details=False):
        """Convert content to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content_type': self.content_type,
            'thumbnail_url': self.thumbnail_url,
            'duration_minutes': self.duration_minutes,
            'difficulty_level': self.difficulty_level,
            'language': self.language,
            'price': float(self.price) if self.price else 0.0,
            'is_free': self.is_free,
            'is_published': self.is_published,
            'view_count': self.view_count,
            'rating_average': float(self.rating_average) if self.rating_average else 0.0,
            'rating_count': self.rating_count,
            'instructor': {
                'id': self.instructor.id,
                'username': self.instructor.username,
                'full_name': self.instructor.full_name
            } if self.instructor else None,
            'category': {
                'id': self.category.id,
                'name': self.category.name
            } if self.category else None,
            'tags': [tag.name for tag in self.tags],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_details:
            data['content_url'] = self.content_url
            data['metadata_json'] = self.metadata_json
        
        return data

