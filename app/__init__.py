import os
from flask import Flask


def create_app():
    """Application factory pattern"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

    # Register blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.blog import blog_bp
    from app.blueprints.projects import projects_bp
    from app.blueprints.contact import contact_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(contact_bp)

    return app
