import os
from flask import Flask, session, render_template
from app.translations import DEFAULT_LANGUAGE, translations


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

    app.register_blueprint(main_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(projects_bp)

    @app.errorhandler(404)
    def not_found(e):
        lang = session.get('lang', DEFAULT_LANGUAGE)
        return render_template('404.html', translations=translations[lang]), 404

    @app.context_processor
    def inject_language():
        return {'current_lang': session.get('lang', DEFAULT_LANGUAGE)}

    def localize(obj, attr, lang):
        """Return obj[attr_lang], falling back to the English value."""
        return obj.get(f'{attr}_{lang}', obj.get(f'{attr}_en', ''))

    app.jinja_env.globals['localize'] = localize

    return app
