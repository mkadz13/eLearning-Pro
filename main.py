"""
Education Platform API - Main Entry Point
A comprehensive learning content platform with REST APIs, PostgreSQL, and Docker support.
"""

from app import create_app, db
from app.models import User, Content, Category, Tag
from flask_migrate import upgrade
import os

app = create_app()


@app.cli.command('init-db')
def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user
        from app import bcrypt
        from app.models.user import UserRole
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@educationplatform.com',
                password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                full_name='Administrator',
                role=UserRole.ADMIN
            )
            db.session.add(admin)
            print("Created admin user: username='admin', password='admin123'")
        
        # Create sample categories
        categories_data = [
            {'name': 'Programming', 'slug': 'programming', 'description': 'Learn programming languages and frameworks'},
            {'name': 'Data Science', 'slug': 'data-science', 'description': 'Data analysis, machine learning, and AI'},
            {'name': 'Web Development', 'slug': 'web-development', 'description': 'Frontend and backend web technologies'},
            {'name': 'Mobile Development', 'slug': 'mobile-development', 'description': 'iOS and Android app development'},
            {'name': 'Design', 'slug': 'design', 'description': 'UI/UX and graphic design'},
        ]
        
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(**cat_data)
                db.session.add(category)
                print(f"Created category: {cat_data['name']}")
        
        db.session.commit()
        print("Database initialized successfully!")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
