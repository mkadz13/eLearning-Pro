from flask import Blueprint, request, jsonify
from app import db
from app.models.content import Content
from app.models.tag import Tag
from sqlalchemy import or_, desc

search_bp = Blueprint('search', __name__)


@search_bp.route('', methods=['GET'])
def search():
    """Search content by query, tags, or filters"""
    query = request.args.get('q', '', type=str)
    tags = request.args.get('tags', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Start with published content
    search_query = Content.query.filter_by(is_published=True)
    
    # Text search in title and description
    if query:
        search_query = search_query.filter(
            or_(
                Content.title.ilike(f'%{query}%'),
                Content.description.ilike(f'%{query}%')
            )
        )
    
    # Tag filtering
    if tags:
        tag_list = [tag.strip().lower() for tag in tags.split(',')]
        for tag_name in tag_list:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                search_query = search_query.filter(Content.tags.contains(tag))
    
    # Order by relevance (rating and views)
    search_query = search_query.order_by(
        desc(Content.rating_average),
        desc(Content.view_count)
    )
    
    pagination = search_query.paginate(page=page, per_page=per_page, error_out=False)
    results = pagination.items
    
    return jsonify({
        'query': query,
        'results': [item.to_dict() for item in results],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@search_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """Get search suggestions based on popular content"""
    query = request.args.get('q', '', type=str)
    limit = request.args.get('limit', 10, type=int)
    
    if not query or len(query) < 2:
        return jsonify({'suggestions': []}), 200
    
    # Search in titles
    suggestions = Content.query.filter(
        Content.title.ilike(f'%{query}%'),
        Content.is_published == True
    ).order_by(
        desc(Content.rating_average),
        desc(Content.view_count)
    ).limit(limit).all()
    
    return jsonify({
        'suggestions': [
            {
                'id': item.id,
                'title': item.title,
                'content_type': item.content_type,
                'thumbnail_url': item.thumbnail_url
            }
            for item in suggestions
        ]
    }), 200

