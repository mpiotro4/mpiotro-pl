from pathlib import Path
import frontmatter


def parse_project(filepath):
    """Parse markdown file with front matter and multilingual content"""
    post = frontmatter.load(filepath)

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


def get_all_projects():
    """Get all projects sorted by date (newest first)"""
    projects_dir = Path(__file__).parent.parent.parent / 'projects'
    if not projects_dir.exists():
        return []

    projects = []
    for md_file in sorted(projects_dir.glob('*.md'), reverse=True):
        project = parse_project(md_file)
        if project:
            projects.append(project)

    return projects


def get_project_by_slug(slug):
    """Get single project by slug"""
    projects_dir = Path(__file__).parent.parent.parent / 'projects'
    filepath = projects_dir / f'{slug}.md'

    if filepath.exists():
        return parse_project(filepath)
    return None
