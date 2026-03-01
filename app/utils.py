import markdown


_MARKDOWN_EXTENSIONS = [
    'tables',
    'fenced_code',
    'codehilite',
    'nl2br',
    'pymdownx.arithmatex',
]

_MARKDOWN_EXTENSION_CONFIGS = {
    'codehilite': {
        'guess_lang': False,
        'use_pygments': False,
        'noclasses': True,
    },
    'pymdownx.arithmatex': {
        'generic': True,
        'preview': False,
    },
}


def parse_multilingual_content(content: str) -> tuple[str, str]:
    """Split markdown content into Polish and English sections.

    Expects the content to use '## PL' and '## EN' headings as delimiters.
    If neither marker is present, the full content is returned for both languages.
    """
    if '## PL' in content and '## EN' in content:
        pl_start = content.find('## PL') + len('## PL')
        pl_end = content.find('## EN')
        content_pl = content[pl_start:pl_end].strip()

        en_start = content.find('## EN') + len('## EN')
        content_en = content[en_start:].strip()
    else:
        content_pl = content
        content_en = content

    return content_pl, content_en


def render_markdown(text: str) -> str:
    """Convert markdown text to HTML with the project's standard extensions."""
    return markdown.markdown(
        text,
        extensions=_MARKDOWN_EXTENSIONS,
        extension_configs=_MARKDOWN_EXTENSION_CONFIGS,
    )
