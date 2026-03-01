from pathlib import Path
import frontmatter

from app.utils import parse_multilingual_content


def parse_project(filepath):
    """Parse markdown file with front matter and multilingual content"""
    post = frontmatter.load(filepath)

    content_pl, content_en = parse_multilingual_content(post.content)

    slug = Path(filepath).stem

    date = post.get('date', '')
    tags = post.get('tags', [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(',')]

    return {
        'slug': slug,
        'title_pl': post.get('title_pl', 'Bez tytułu'),
        'title_en': post.get('title_en', 'No title'),
        'date': date,
        'date_raw': date,
        'tags': tags,
        'description_pl': post.get('description_pl', ''),
        'description_en': post.get('description_en', ''),
        'content_pl': content_pl,
        'content_en': content_en,
        'image': post.get('image', ''),
    }


_cache: dict = {'projects': None, 'mtime': None}


def _projects_dir() -> Path:
    return Path(__file__).parent.parent.parent / 'projects'


def _max_mtime(directory: Path) -> float:
    mtimes = [f.stat().st_mtime for f in directory.glob('*.md')]
    return max(mtimes) if mtimes else 0.0


def get_all_projects() -> list:
    """Get all projects sorted by date (newest first), cached until a file changes."""
    projects_dir = _projects_dir()
    if not projects_dir.exists():
        return []

    mtime = _max_mtime(projects_dir)
    if _cache['projects'] is not None and mtime == _cache['mtime']:
        return _cache['projects']

    projects = [parse_project(f) for f in sorted(projects_dir.glob('*.md'), reverse=True)]
    projects = [p for p in projects if p]

    _cache['projects'] = projects
    _cache['mtime'] = mtime
    return projects


def get_project_by_slug(slug: str) -> dict | None:
    """Get a single project by slug, reusing the in-memory cache."""
    return next((p for p in get_all_projects() if p['slug'] == slug), None)
