from pathlib import Path
import frontmatter


def parse_blog_post(filepath):
    """Parse markdown file with front matter and multilingual content"""
    post = frontmatter.load(filepath)

    # Parse multilingual content
    content_pl = ''
    content_en = ''

    if '## PL' in post.content and '## EN' in post.content:
        pl_start = post.content.find('## PL') + len('## PL')
        pl_end = post.content.find('## EN')
        content_pl = post.content[pl_start:pl_end].strip()

        en_start = post.content.find('## EN') + len('## EN')
        content_en = post.content[en_start:].strip()
    else:
        content_pl = post.content
        content_en = post.content

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


def get_all_posts():
    """Get all blog posts sorted by date (newest first)"""
    # Go up two levels from app/services/ to project root
    blog_dir = Path(__file__).parent.parent.parent / 'blog' / 'posts'
    if not blog_dir.exists():
        return []

    posts = []
    for md_file in sorted(blog_dir.glob('*.md'), reverse=True):
        post = parse_blog_post(md_file)
        if post:
            posts.append(post)

    return posts


def get_post_by_slug(slug):
    """Get single blog post by slug"""
    # Go up two levels from app/services/ to project root
    blog_dir = Path(__file__).parent.parent.parent / 'blog' / 'posts'
    filepath = blog_dir / f'{slug}.md'

    if filepath.exists():
        return parse_blog_post(filepath)
    return None
