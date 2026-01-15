from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Import models for Flask-Migrate
    from app.models import User, Content, Category, Enrollment, Review, Progress, Tag

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.content import content_bp
    from app.routes.categories import categories_bp
    from app.routes.enrollments import enrollments_bp
    from app.routes.reviews import reviews_bp
    from app.routes.search import search_bp
    from app.routes.progress import progress_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(content_bp, url_prefix='/api/content')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(enrollments_bp, url_prefix='/api/enrollments')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(progress_bp, url_prefix='/api/progress')

    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Education Platform API is running'}, 200

    @app.route('/')
    def index():
        """Serve the frontend login page"""
        from flask import send_from_directory
        return send_from_directory('frontend', 'index.html')

    @app.route('/dashboard')
    def dashboard():
        """Serve the frontend dashboard"""
        from flask import send_from_directory
        return send_from_directory('frontend', 'dashboard.html')

    return app

