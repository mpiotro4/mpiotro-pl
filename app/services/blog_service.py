from pathlib import Path
import frontmatter

from app.utils import date_sort_key, parse_multilingual_content


def parse_blog_post(filepath):
    """Parse markdown file with front matter and multilingual content"""
    post = frontmatter.load(filepath)

    # Parse multilingual content
    content_pl, content_en = parse_multilingual_content(post.content)

    slug = Path(filepath).stem

    # Get dates - frontmatter should parse them as datetime objects
    date = post.get('date', '')
    updated = post.get('updated', None)

    # Get author and tags
    author = post.get('author', '')
    tags = post.get('tags', [])
    if isinstance(tags, str):
        # If tags is a string, split by comma
        tags = [tag.strip() for tag in tags.split(',')]

    return {
        'slug': slug,
        'title_pl': post.get('title_pl', 'Bez tytułu'),
        'title_en': post.get('title_en', 'No title'),
        'date': date,
        'date_raw': date,  # Keep raw datetime for sorting
        'updated': updated,
        'updated_raw': updated,
        'author': author,
        'tags': tags,
        'description_pl': post.get('description_pl', ''),
        'description_en': post.get('description_en', ''),
        'content_pl': content_pl,
        'content_en': content_en
    }


_cache: dict = {'posts': None, 'mtime': None}


def _blog_dir() -> Path:
    return Path(__file__).parent.parent.parent / 'blog' / 'posts'


def _max_mtime(directory: Path) -> float:
    mtimes = [f.stat().st_mtime for f in directory.glob('*.md')]
    return max(mtimes) if mtimes else 0.0


def get_all_posts() -> list:
    """Get all blog posts sorted by date (newest first), cached until a file changes."""
    blog_dir = _blog_dir()
    if not blog_dir.exists():
        return []

    mtime = _max_mtime(blog_dir)
    if _cache['posts'] is not None and mtime == _cache['mtime']:
        return _cache['posts']

    posts = [parse_blog_post(f) for f in blog_dir.glob('*.md')]
    posts = [p for p in posts if p]
    posts.sort(key=date_sort_key, reverse=True)

    _cache['posts'] = posts
    _cache['mtime'] = mtime
    return posts


def get_post_by_slug(slug: str) -> dict | None:
    """Get a single blog post by slug, reusing the in-memory cache."""
    return next((p for p in get_all_posts() if p['slug'] == slug), None)
