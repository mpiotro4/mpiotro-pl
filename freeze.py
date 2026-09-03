"""Freeze the Flask site into a static ``build/`` directory for GitHub Pages.

Usage::

    SECRET_KEY=build-only python freeze.py

Produces a Polish tree at the root and an English mirror under ``/en/``.
The site is served from a sub-path (``/mpiotro-pl/``) on project GitHub Pages,
so every generated URL is prefixed via ``FREEZER_BASE_URL``.
"""
import os
from urllib.parse import urlsplit

from flask_frozen import Freezer

from app import create_app
from app.services.blog_service import get_all_posts
from app.services.project_service import get_all_projects

LANGUAGES = ('pl', 'en')
BASE_URL = os.environ.get('SITE_BASE_URL', 'https://mpiotro4.github.io/mpiotro-pl/')
BASE_PATH = urlsplit(BASE_URL).path or '/'  # e.g. "/mpiotro-pl/"

os.environ.setdefault('SECRET_KEY', 'build-only-not-secret')

app = create_app()
app.config.update(
    FREEZER_DESTINATION=os.path.join(os.path.dirname(__file__), 'build'),
    FREEZER_BASE_URL=BASE_URL,
    FREEZER_REMOVE_EXTRA_FILES=True,
    FREEZER_STATIC_IGNORE=['*.scss', 'scss', '.DS_Store'],
    FREEZER_DESTINATION_IGNORE=['.git*', 'CNAME', '.nojekyll', 'about', 'en/about'],
)

freezer = Freezer(app)


@freezer.register_generator
def site_urls():
    yield 'not_found_page', {}
    for lang in LANGUAGES:
        yield 'main.index', {'lang': lang}
        yield 'blog.index', {'lang': lang}
        yield 'projects.index', {'lang': lang}
        for post in get_all_posts():
            yield 'blog.post', {'lang': lang, 'slug': post['slug']}
        for project in get_all_projects():
            yield 'projects.project', {'lang': lang, 'slug': project['slug']}


def _write(path, content):
    full = os.path.join(app.config['FREEZER_DESTINATION'], path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    mode = 'wb' if isinstance(content, bytes) else 'w'
    with open(full, mode) as fh:
        fh.write(content)


def _redirect_stub(target):
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        f'<link rel="canonical" href="{target}">'
        f'<meta http-equiv="refresh" content="0; url={target}">'
        '<title>Redirecting…</title></head>'
        f'<body><a href="{target}">{target}</a></body></html>'
    )


if __name__ == '__main__':
    freezer.freeze()

    # Disable Jekyll so files/dirs starting with "_" are published as-is.
    _write('.nojekyll', '')

    # Keep the pre-export /about URLs working (they used to be canonical).
    root = BASE_PATH if BASE_PATH.endswith('/') else BASE_PATH + '/'
    _write(os.path.join('about', 'index.html'), _redirect_stub(root))
    _write(os.path.join('en', 'about', 'index.html'), _redirect_stub(root + 'en/'))

    print('Frozen to', app.config['FREEZER_DESTINATION'], 'with base', BASE_URL)
