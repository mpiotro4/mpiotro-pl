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


def render_markdown(text: str) -> str:
    """Convert markdown text to HTML with the project's standard extensions."""
    return markdown.markdown(
        text,
        extensions=_MARKDOWN_EXTENSIONS,
        extension_configs=_MARKDOWN_EXTENSION_CONFIGS,
    )
