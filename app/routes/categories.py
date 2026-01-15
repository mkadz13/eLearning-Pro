from flask import Blueprint, request, jsonify
from app import db
from app.models.category import Category
from app.utils.auth import admin_required
from flask_jwt_extended import jwt_required
import re

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify({
        'categories': [cat.to_dict() for cat in categories]
    }), 200


@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get category by ID"""
    category = Category.query.get_or_404(category_id)
    return jsonify(category.to_dict()), 200


@categories_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_category():
    """Create new category (admin only)"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Category name required'}), 400
    
    name = data.get('name').strip()
    slug = data.get('slug') or re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    
    # Check if category exists
    if Category.query.filter_by(name=name).first():
        return jsonify({'error': 'Category already exists'}), 409
    
    if Category.query.filter_by(slug=slug).first():
        return jsonify({'error': 'Category slug already exists'}), 409
    
    category = Category(
        name=name,
        slug=slug,
        description=data.get('description'),
        icon_url=data.get('icon_url'),
        parent_id=data.get('parent_id')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'message': 'Category created successfully',
        'category': category.to_dict()
    }), 201


@categories_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(category_id):
    """Update category (admin only)"""
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' in data:
        category.name = data['name'].strip()
    if 'slug' in data:
        category.slug = data['slug']
    if 'description' in data:
        category.description = data['description']
    if 'icon_url' in data:
        category.icon_url = data['icon_url']
    if 'parent_id' in data:
        category.parent_id = data['parent_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Category updated successfully',
        'category': category.to_dict()
    }), 200


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(category_id):
    """Delete category (admin only)"""
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted successfully'}), 200

