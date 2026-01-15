from flask import Blueprint, request, jsonify
from app import db
from app.models.content import Content, ContentType
from app.models.user import User
from app.models.tag import Tag
from app.utils.auth import instructor_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, desc

content_bp = Blueprint('content', __name__)


@content_bp.route('', methods=['GET'])
def get_content():
    """Get all content with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    content_type = request.args.get('type', type=str)
    category_id = request.args.get('category_id', type=int)
    instructor_id = request.args.get('instructor_id', type=int)
    is_free = request.args.get('is_free', type=str)
    difficulty = request.args.get('difficulty', type=str)
    language = request.args.get('language', type=str)
    sort_by = request.args.get('sort_by', 'created_at', type=str)  # created_at, rating, views
    
    query = Content.query.filter_by(is_published=True)
    
    # Filters
    if content_type:
        query = query.filter_by(content_type=content_type)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if instructor_id:
        query = query.filter_by(instructor_id=instructor_id)
    if is_free is not None:
        query = query.filter_by(is_free=is_free.lower() == 'true')
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    if language:
        query = query.filter_by(language=language)
    
    # Sorting
    if sort_by == 'rating':
        query = query.order_by(desc(Content.rating_average))
    elif sort_by == 'views':
        query = query.order_by(desc(Content.view_count))
    else:
        query = query.order_by(desc(Content.created_at))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    content_items = pagination.items
    
    return jsonify({
        'content': [item.to_dict() for item in content_items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@content_bp.route('/<int:content_id>', methods=['GET'])
def get_content_by_id(content_id):
    """Get content by ID"""
    content = Content.query.get_or_404(content_id)
    
    # Increment view count
    content.view_count += 1
    db.session.commit()
    
    return jsonify(content.to_dict(include_details=True)), 200


@content_bp.route('', methods=['POST'])
@jwt_required()
@instructor_required
def create_content():
    """Create new content (instructor/admin only)"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('title', 'description', 'content_type')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    instructor_id = get_jwt_identity()
    content_type = data.get('content_type')
    
    # Validate content type
    valid_types = [ContentType.VIDEO, ContentType.ARTICLE, ContentType.COURSE, 
                   ContentType.QUIZ, ContentType.EBOOK, ContentType.PODCAST]
    if content_type not in valid_types:
        return jsonify({'error': 'Invalid content type'}), 400
    
    # Create content
    content = Content(
        title=data.get('title'),
        description=data.get('description'),
        content_type=content_type,
        content_url=data.get('content_url'),
        thumbnail_url=data.get('thumbnail_url'),
        duration_minutes=data.get('duration_minutes'),
        difficulty_level=data.get('difficulty_level'),
        language=data.get('language', 'en'),
        price=data.get('price', 0.00),
        is_free=data.get('is_free', True),
        is_published=data.get('is_published', False),
        instructor_id=instructor_id,
        category_id=data.get('category_id'),
        metadata_json=data.get('metadata_json')
    )
    
    # Handle tags
    if 'tags' in data and isinstance(data['tags'], list):
        tags = []
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name.lower()).first()
            if not tag:
                tag = Tag(name=tag_name.lower(), slug=tag_name.lower().replace(' ', '-'))
                db.session.add(tag)
            tags.append(tag)
        content.tags = tags
    
    db.session.add(content)
    db.session.commit()
    
    return jsonify({
        'message': 'Content created successfully',
        'content': content.to_dict(include_details=True)
    }), 201


@content_bp.route('/<int:content_id>', methods=['PUT'])
@jwt_required()
@instructor_required
def update_content(content_id):
    """Update content (instructor/admin only)"""
    content = Content.query.get_or_404(content_id)
    instructor_id = get_jwt_identity()
    
    # Check ownership or admin
    current_user = User.query.get(instructor_id)
    if content.instructor_id != instructor_id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    updatable_fields = ['title', 'description', 'content_url', 'thumbnail_url', 
                       'duration_minutes', 'difficulty_level', 'language', 'price',
                       'is_free', 'is_published', 'category_id', 'metadata_json']
    
    for field in updatable_fields:
        if field in data:
            setattr(content, field, data[field])
    
    # Update tags
    if 'tags' in data and isinstance(data['tags'], list):
        tags = []
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name.lower()).first()
            if not tag:
                tag = Tag(name=tag_name.lower(), slug=tag_name.lower().replace(' ', '-'))
                db.session.add(tag)
            tags.append(tag)
        content.tags = tags
    
    db.session.commit()
    
    return jsonify({
        'message': 'Content updated successfully',
        'content': content.to_dict(include_details=True)
    }), 200


@content_bp.route('/<int:content_id>', methods=['DELETE'])
@jwt_required()
@instructor_required
def delete_content(content_id):
    """Delete content (instructor/admin only)"""
    content = Content.query.get_or_404(content_id)
    instructor_id = get_jwt_identity()
    
    # Check ownership or admin
    current_user = User.query.get(instructor_id)
    if content.instructor_id != instructor_id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(content)
    db.session.commit()
    
    return jsonify({'message': 'Content deleted successfully'}), 200

