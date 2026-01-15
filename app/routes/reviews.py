from flask import Blueprint, request, jsonify
from app import db
from app.models.review import Review
from app.models.content import Content
from app.models.enrollment import Enrollment
from flask_jwt_extended import jwt_required, get_jwt_identity

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/content/<int:content_id>', methods=['GET'])
def get_content_reviews(content_id):
    """Get reviews for a specific content"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'created_at', type=str)  # created_at, rating, helpful
    
    query = Review.query.filter_by(content_id=content_id)
    
    if sort_by == 'rating':
        query = query.order_by(Review.rating.desc())
    elif sort_by == 'helpful':
        query = query.order_by(Review.helpful_count.desc())
    else:
        query = query.order_by(Review.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    reviews = pagination.items
    
    return jsonify({
        'reviews': [review.to_dict(include_user=True) for review in reviews],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    """Create a review for content"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not all(k in data for k in ('content_id', 'rating')):
        return jsonify({'error': 'content_id and rating required'}), 400
    
    content_id = data.get('content_id')
    rating = data.get('rating')
    
    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    content = Content.query.get_or_404(content_id)
    
    # Check if review already exists
    existing = Review.query.filter_by(user_id=user_id, content_id=content_id).first()
    if existing:
        return jsonify({'error': 'Review already exists'}), 409
    
    # Check if user is enrolled (for verified purchase)
    is_verified = Enrollment.query.filter_by(
        user_id=user_id, 
        content_id=content_id
    ).first() is not None
    
    review = Review(
        user_id=user_id,
        content_id=content_id,
        rating=rating,
        title=data.get('title'),
        comment=data.get('comment'),
        is_verified_purchase=is_verified
    )
    
    db.session.add(review)
    db.session.commit()
    
    # Update content rating
    content.update_rating()
    
    return jsonify({
        'message': 'Review created successfully',
        'review': review.to_dict(include_user=True)
    }), 201


@reviews_bp.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """Update a review"""
    user_id = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'rating' in data:
        rating = data['rating']
        if not (1 <= rating <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        review.rating = rating
    
    if 'title' in data:
        review.title = data['title']
    if 'comment' in data:
        review.comment = data['comment']
    
    db.session.commit()
    
    # Update content rating
    review.content.update_rating()
    
    return jsonify({
        'message': 'Review updated successfully',
        'review': review.to_dict(include_user=True)
    }), 200


@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Delete a review"""
    user_id = get_jwt_identity()
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    content = review.content
    db.session.delete(review)
    db.session.commit()
    
    # Update content rating
    content.update_rating()
    
    return jsonify({'message': 'Review deleted successfully'}), 200


@reviews_bp.route('/<int:review_id>/helpful', methods=['POST'])
@jwt_required()
def mark_helpful(review_id):
    """Mark a review as helpful"""
    review = Review.query.get_or_404(review_id)
    review.helpful_count += 1
    db.session.commit()
    
    return jsonify({
        'message': 'Review marked as helpful',
        'helpful_count': review.helpful_count
    }), 200

