from flask import Blueprint, request, jsonify
from app import db
from app.models.enrollment import Enrollment
from app.models.content import Content
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

enrollments_bp = Blueprint('enrollments', __name__)


@enrollments_bp.route('', methods=['GET'])
@jwt_required()
def get_enrollments():
    """Get user's enrollments"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_completed = request.args.get('is_completed', type=str)
    
    query = Enrollment.query.filter_by(user_id=user_id)
    
    if is_completed is not None:
        query = query.filter_by(is_completed=is_completed.lower() == 'true')
    
    pagination = query.order_by(Enrollment.enrolled_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    enrollments = pagination.items
    
    return jsonify({
        'enrollments': [enrollment.to_dict() for enrollment in enrollments],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@enrollments_bp.route('', methods=['POST'])
@jwt_required()
def create_enrollment():
    """Enroll in content"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('content_id'):
        return jsonify({'error': 'content_id required'}), 400
    
    content_id = data.get('content_id')
    content = Content.query.get_or_404(content_id)
    
    # Check if already enrolled
    existing = Enrollment.query.filter_by(user_id=user_id, content_id=content_id).first()
    if existing:
        return jsonify({
            'message': 'Already enrolled',
            'enrollment': existing.to_dict()
        }), 200
    
    # Check if content is published
    if not content.is_published:
        return jsonify({'error': 'Content is not published'}), 400
    
    enrollment = Enrollment(
        user_id=user_id,
        content_id=content_id
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify({
        'message': 'Enrolled successfully',
        'enrollment': enrollment.to_dict()
    }), 201


@enrollments_bp.route('/<int:enrollment_id>', methods=['PUT'])
@jwt_required()
def update_enrollment(enrollment_id):
    """Update enrollment (mark as completed)"""
    user_id = get_jwt_identity()
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    if enrollment.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if data.get('is_completed'):
        enrollment.is_completed = True
        enrollment.completed_at = datetime.utcnow()
    
    if 'last_accessed_at' in data:
        enrollment.last_accessed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Enrollment updated successfully',
        'enrollment': enrollment.to_dict()
    }), 200


@enrollments_bp.route('/<int:enrollment_id>', methods=['DELETE'])
@jwt_required()
def delete_enrollment(enrollment_id):
    """Unenroll from content"""
    user_id = get_jwt_identity()
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    if enrollment.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(enrollment)
    db.session.commit()
    
    return jsonify({'message': 'Unenrolled successfully'}), 200

