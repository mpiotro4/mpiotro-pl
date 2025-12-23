from pathlib import Path
import frontmatter


def parse_project(filepath):
    """Parse markdown file with front matter and multilingual project content"""
    project = frontmatter.load(filepath)

    # Parse multilingual content
    content_pl = ''
    content_en = ''

    if '## PL' in project.content and '## EN' in project.content:
        pl_start = project.content.find('## PL') + len('## PL')
        pl_end = project.content.find('## EN')
        content_pl = project.content[pl_start:pl_end].strip()

        en_start = project.content.find('## EN') + len('## EN')
        content_en = project.content[en_start:].strip()
    else:
        content_pl = project.content
        content_en = project.content

    slug = Path(filepath).stem

    # Get year
    year = project.get('year', '')

    # Get tags and technologies
    tags = project.get('tags', [])
    if isinstance(tags, str):
        # If tags is a string, split by comma
        tags = [tag.strip() for tag in tags.split(',')]

    technologies = project.get('technologies', [])
    if isinstance(technologies, str):
        # If technologies is a string, split by comma
        technologies = [tech.strip() for tech in technologies.split(',')]

    return {
        'slug': slug,
        'title_pl': project.get('title_pl', 'Bez tytułu'),
        'title_en': project.get('title_en', 'No title'),
        'year': year,
        'tags': tags,
        'technologies': technologies,
        'description_pl': project.get('description_pl', ''),
        'description_en': project.get('description_en', ''),
        'image': project.get('image', ''),
        'github': project.get('github', ''),
        'demo': project.get('demo', ''),
        'content_pl': content_pl,
        'content_en': content_en
    }


def get_all_projects():
    """Get all projects sorted by year (newest first)"""
    # Go up two levels from app/services/ to project root
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
    # Go up two levels from app/services/ to project root
    projects_dir = Path(__file__).parent.parent.parent / 'projects'
    filepath = projects_dir / f'{slug}.md'

    if filepath.exists():
        return parse_project(filepath)
    return None


def get_projects_by_year():
    """Get projects grouped by year"""
    projects = get_all_projects()
    projects_by_year = {}

    for project in projects:
        year = project.get('year', 'Unknown')
        if year not in projects_by_year:
            projects_by_year[year] = []
        projects_by_year[year].append(project)

    # Sort years in descending order
    sorted_years = sorted(projects_by_year.keys(), reverse=True)
    return {year: projects_by_year[year] for year in sorted_years}
