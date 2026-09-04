import os
import re
from flask import Flask, g, render_template, request, url_for
from app.translations import DEFAULT_LANGUAGE, translations

# Absolute /static/... references hardcoded in markdown content, so they can be
# routed through url_for() (and pick up any deployment path prefix).
_STATIC_REF_RE = re.compile(r'(src|href)="/static/([^"]+)"')

# Endpoints that come in an English (root) and a Polish (/pl/...) variant.
# Their url_for() calls automatically keep the current language prefix.
LANG_AWARE_ENDPOINTS = {
    'main.index',
    'blog.index',
    'blog.post',
    'projects.index',
    'projects.project',
}


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

    @app.url_value_preprocessor
    def pull_lang(endpoint, values):
        """Expose the language chosen by the matched route as g.lang."""
        g.lang = (values or {}).get('lang', DEFAULT_LANGUAGE)

    @app.url_defaults
    def add_lang(endpoint, values):
        """Keep the active language when building URLs for language-aware endpoints."""
        if 'lang' in values or endpoint not in LANG_AWARE_ENDPOINTS:
            return
        values['lang'] = g.get('lang', DEFAULT_LANGUAGE)

    @app.errorhandler(404)
    def not_found(e):
        lang = 'pl' if request.path.startswith('/pl/') else DEFAULT_LANGUAGE
        g.lang = lang
        return render_template('404.html', translations=translations[lang]), 404

    @app.route('/404.html')
    def not_found_page():
        """Static 404 page frozen for GitHub Pages."""
        return render_template('404.html', translations=translations[DEFAULT_LANGUAGE])

    def _alt_lang_url(lang):
        """URL of the current page in the other language."""
        target = 'en' if lang == 'pl' else 'pl'
        if request.endpoint in LANG_AWARE_ENDPOINTS:
            view_args = {k: v for k, v in (request.view_args or {}).items() if k != 'lang'}
            return url_for(request.endpoint, lang=target, **view_args)
        return url_for('main.index', lang=target)

    @app.context_processor
    def inject_language():
        lang = g.get('lang', DEFAULT_LANGUAGE)
        return {
            'current_lang': lang,
            'alt_lang': 'en' if lang == 'pl' else 'pl',
            'alt_lang_url': _alt_lang_url(lang),
        }

    def localize(obj, attr, lang):
        """Return obj[attr_lang], falling back to the English value."""
        return obj.get(f'{attr}_{lang}', obj.get(f'{attr}_en', ''))

    app.jinja_env.globals['localize'] = localize

    @app.template_filter('resolve_static')
    def resolve_static(html):
        """Route absolute /static/... links in rendered markdown through url_for."""
        return _STATIC_REF_RE.sub(
            lambda m: f'{m.group(1)}="{url_for("static", filename=m.group(2))}"',
            html or '',
        )

    @app.template_filter('static_url')
    def static_url(path):
        """Route a hardcoded /static/... path (e.g. frontmatter 'image') through url_for."""
        if path and path.startswith('/static/'):
            return url_for('static', filename=path[len('/static/'):])
        return path

    return app
