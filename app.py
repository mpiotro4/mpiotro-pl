import os
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, session

# Try to import markdown, fallback to simple converter if not available
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Blog helper functions
def parse_blog_post(filepath):
    """Parse markdown file with front matter and multilingual content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by --- to separate front matter from content
    parts = content.split('---')
    if len(parts) < 3:
        return None

    front_matter = parts[1].strip()
    post_content = '---'.join(parts[2:]).strip()  # Rejoin in case content has ---

    # Parse front matter
    metadata = {}
    for line in front_matter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

    # Parse multilingual content (split by ## PL and ## EN)
    content_pl = ''
    content_en = ''

    if '## PL' in post_content and '## EN' in post_content:
        # Extract Polish content
        pl_start = post_content.find('## PL') + len('## PL')
        pl_end = post_content.find('## EN')
        content_pl = post_content[pl_start:pl_end].strip()

        # Extract English content
        en_start = post_content.find('## EN') + len('## EN')
        content_en = post_content[en_start:].strip()
    else:
        # Fallback: use same content for both languages
        content_pl = post_content
        content_en = post_content

    # Create slug from filename
    filename = Path(filepath).stem
    slug = filename

    return {
        'slug': slug,
        'title_pl': metadata.get('title_pl', 'Bez tytułu'),
        'title_en': metadata.get('title_en', 'No title'),
        'date': metadata.get('date', ''),
        'description_pl': metadata.get('description_pl', ''),
        'description_en': metadata.get('description_en', ''),
        'content_pl': content_pl,
        'content_en': content_en
    }

def get_all_posts():
    """Get all blog posts sorted by date (newest first)"""
    blog_dir = Path(__file__).parent / 'blog' / 'posts'
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
    blog_dir = Path(__file__).parent / 'blog' / 'posts'
    filepath = blog_dir / f'{slug}.md'

    if filepath.exists():
        return parse_blog_post(filepath)
    return None

# Markdown to HTML converter
def markdown_to_html(text):
    """Convert markdown to HTML using markdown library or simple fallback"""
    if HAS_MARKDOWN:
        return markdown.markdown(text, extensions=['tables', 'fenced_code'])
    else:
        # Fallback simple converter if markdown library is not available
        lines = text.split('\n')
        html = []

        for line in lines:
            if line.startswith('## '):
                html.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('# '):
                html.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('- '):
                html.append(f'<li>{line[2:]}</li>')
            elif line.startswith('**') and line.endswith('**'):
                html.append(f'<strong>{line[2:-2]}</strong>')
            elif line.strip() == '':
                html.append('<br>')
            else:
                html.append(f'<p>{line}</p>')

        return '\n'.join(html)

translations = {
    'pl': {
        'title': 'Marcin Piotrowski - strona domowa',
        'about_me': 'O mnie',
        'about_me_content': 'Posiadam ponad 3 lata komercyjnego doświadczenia w wytwarzaniu oprogramowania z czego '
                            'dwa lata w języku Java. Większość czasu spędziłem nad pracą w dużych projektach '
                            'dotyczących ceł i podatków dla duńskiego sektora publicznego. Posiadałem szeroki zakres '
                            'obowiązków, od tworzenia testów automatycznych, implementacji nowych funkcjonalności i '
                            'wdrożeń po przygotowywanie kontraktów. Ukończyłem studia magisterskie z informatyki na '
                            'wydziale elektroniki i technik informacyjnych politechniki warszawskiej.',
        'projects': 'Projekty',
        'blog': 'Blog',
        'cv': 'CV',
        'contact': 'Kontakt',
        'my_projects': 'Lista moich projektów.',
        'my_blog': 'Czytaj moje wpisy na blogu.',
        'my_cv': 'Moje CV.',
        'my_contact': 'Możesz się ze mną skontaktować przez e-mail: mpiotro4@outlook.com.',
        'read_more': 'Czytaj więcej',
        'back_to_blog': 'Powrót do bloga',
        'no_posts': 'Brak postów na blogu.',
    },
    'en': {
        'title': 'Marcin Piotrowski - homepage',
        'about_me': 'About Me',
        'about_me_content': "I have over three years of commercial experience in software development, including two "
                            "years in Java. I spent most of my time working on large projects related to customs and "
                            "taxes for the Danish public sector. I had a wide range of responsibilities, "
                            "from creating automated tests and implementing new features to deployments and preparing "
                            "contracts. I hold a master's degree in computer science from the Faculty of Electronics "
                            "and Information Technology at the Warsaw University of Technology.",
        'projects': 'Projects',
        'blog': 'Blog',
        'cv': 'CV',
        'contact': 'Contact',
        'my_projects': 'List of my projects.',
        'my_blog': 'Read my blog posts.',
        'my_cv': 'My CV.',
        'my_contact': 'You can contact me via email: mpiotro4@outlook.com.',
        'read_more': 'Read more',
        'back_to_blog': 'Back to blog',
        'no_posts': 'No posts yet.',
    }
}


@app.route('/')
def home():
    lang = session.get('lang', 'en')  # Domyślnie język polski
    return render_template('index.html', lang=lang, translations=translations[lang])

@app.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    return redirect(url_for('home'))

@app.route('/projekty')
def projekty():
    lang = session.get('lang', 'pl')
    return render_template('projects.html', lang=lang, translations=translations[lang])

@app.route('/cv')
def cv():
    lang = session.get('lang', 'pl')
    return render_template('cv.html', lang=lang, translations=translations[lang])

@app.route('/kontakt')
def kontakt():
    lang = session.get('lang', 'pl')
    return render_template('contact.html', lang=lang, translations=translations[lang])

@app.route('/blog')
def blog():
    lang = session.get('lang', 'pl')
    posts = get_all_posts()
    return render_template('blog.html', lang=lang, translations=translations[lang], posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    lang = session.get('lang', 'pl')
    post = get_post_by_slug(slug)
    if not post:
        return render_template('404.html', lang=lang, translations=translations[lang]), 404

    # Convert markdown content to HTML (use appropriate language)
    content_key = 'content_pl' if lang == 'pl' else 'content_en'
    content_text = post.get(content_key, '')
    html_content = markdown_to_html(content_text)
    post['html_content'] = html_content

    return render_template('blog_post.html', lang=lang, translations=translations[lang], post=post)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
