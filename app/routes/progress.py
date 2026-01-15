from flask import Blueprint, request, jsonify
from app import db
from app.models.progress import Progress
from app.models.content import Content
from flask_jwt_extended import jwt_required, get_jwt_identity

progress_bp = Blueprint('progress', __name__)


@progress_bp.route('/content/<int:content_id>', methods=['GET'])
@jwt_required()
def get_content_progress(content_id):
    """Get user's progress for specific content"""
    user_id = get_jwt_identity()
    
    progress = Progress.query.filter_by(
        user_id=user_id,
        content_id=content_id
    ).first()
    
    if not progress:
        return jsonify({
            'message': 'No progress found',
            'progress': {
                'completion_percentage': 0.0,
                'bookmarked': False
            }
        }), 200
    
    return jsonify(progress.to_dict()), 200


@progress_bp.route('', methods=['GET'])
@jwt_required()
def get_user_progress():
    """Get all user progress"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    bookmarked_only = request.args.get('bookmarked', type=str)
    
    query = Progress.query.filter_by(user_id=user_id)
    
    if bookmarked_only and bookmarked_only.lower() == 'true':
        query = query.filter_by(bookmarked=True)
    
    pagination = query.order_by(Progress.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    progress_items = pagination.items
    
    return jsonify({
        'progress': [item.to_dict() for item in progress_items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@progress_bp.route('', methods=['POST'])
@jwt_required()
def update_progress():
    """Create or update progress for content"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('content_id'):
        return jsonify({'error': 'content_id required'}), 400
    
    content_id = data.get('content_id')
    Content.query.get_or_404(content_id)  # Ensure content exists
    
    progress = Progress.query.filter_by(
        user_id=user_id,
        content_id=content_id
    ).first()
    
    if not progress:
        progress = Progress(
            user_id=user_id,
            content_id=content_id,
            completion_percentage=data.get('completion_percentage', 0.0),
            last_position=data.get('last_position'),
            notes=data.get('notes'),
            bookmarked=data.get('bookmarked', False)
        )
        db.session.add(progress)
    else:
        if 'completion_percentage' in data:
            progress.completion_percentage = min(max(data['completion_percentage'], 0.0), 100.0)
        if 'last_position' in data:
            progress.last_position = data['last_position']
        if 'notes' in data:
            progress.notes = data['notes']
        if 'bookmarked' in data:
            progress.bookmarked = data['bookmarked']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Progress updated successfully',
        'progress': progress.to_dict()
    }), 200


@progress_bp.route('/content/<int:content_id>/bookmark', methods=['POST'])
@jwt_required()
def toggle_bookmark(content_id):
    """Toggle bookmark for content"""
    user_id = get_jwt_identity()
    
    progress = Progress.query.filter_by(
        user_id=user_id,
        content_id=content_id
    ).first()
    
    if not progress:
        progress = Progress(
            user_id=user_id,
            content_id=content_id,
            bookmarked=True
        )
        db.session.add(progress)
    else:
        progress.bookmarked = not progress.bookmarked
    
    db.session.commit()
    
    return jsonify({
        'message': 'Bookmark toggled successfully',
        'bookmarked': progress.bookmarked
    }), 200

