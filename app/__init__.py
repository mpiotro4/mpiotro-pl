import os
from flask import Flask, session


def create_app():
    """Application factory pattern"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is not set")
    app.secret_key = secret_key

    # Register blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.blog import blog_bp
    from app.blueprints.projects import projects_bp
    from app.blueprints.contact import contact_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(contact_bp)

    @app.context_processor
    def inject_language():
        return {'current_lang': session.get('lang', 'pl')}

    return app
