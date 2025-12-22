import os
from pathlib import Path
from flask import Flask, render_template, redirect, url_for, session, request
import markdown
from datetime import datetime
import locale

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

import frontmatter

def format_date(date_obj, lang='en'):
    """Format date according to language"""
    if not date_obj:
        return ''

    # Ensure we have a datetime object
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except (ValueError, TypeError):
            return date_obj

    if not isinstance(date_obj, datetime):
        return str(date_obj)

    # Polish month names
    polish_months = {
        1: 'stycznia', 2: 'lutego', 3: 'marca', 4: 'kwietnia',
        5: 'maja', 6: 'czerwca', 7: 'lipca', 8: 'sierpnia',
        9: 'września', 10: 'października', 11: 'listopada', 12: 'grudnia'
    }

    if lang == 'pl':
        return f"{date_obj.day} {polish_months[date_obj.month]} {date_obj.year}"
    else:
        return date_obj.strftime('%B %d, %Y')

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
        'published': 'Opublikowano',
        'updated': 'Zaktualizowano',
        'author': 'Autor',
        'tags': 'Tagi',
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
        'published': 'Published',
        'updated': 'Updated',
        'author': 'Author',
        'tags': 'Tags',
    }
}


@app.route('/')
def home():
    lang = session.get('lang', 'en')
    return render_template('index.html', lang=lang, translations=translations[lang])

@app.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    # Redirect to the previous page, or home if no referrer
    return redirect(request.referrer or url_for('home'))

from flask import render_template

@app.route('/projects')
def projects():
    lang = session.get('lang', 'en')
    projects = [
        {
            'project_title': {'en': 'Uniklon', 'pl': 'Uniklon'},
            'project_image_url': 'static/images/Uniklon1.JPG',
            'project_description': {'en': 'Description of Project 1', 'pl': 'Opis Projektu 1'}
        },
        {
            'project_title': {'en': 'Lunar Lander', 'pl': 'Lądownik Księżycowy'},
            'project_image_url': 'static/images/Lunar.png',
            'project_description': {'en': 'Description of Project 2', 'pl': 'Opis Projektu 2'}
        },
        {
            'project_title': {'en': 'Nixie clock', 'pl': 'Zegar Nixie'},
            'project_image_url': 'static/images/nixie.jpeg',
            'project_description': {'en': 'Description of Project 3', 'pl': 'Opis Projektu 3'}
        },
        # Add more projects as needed
    ]
    return render_template('projects.html', lang=lang, translations=translations[lang], projects=projects)

@app.route('/cv')
def cv():
    lang = session.get('lang', 'en')
    return render_template('cv.html', lang=lang, translations=translations[lang])

@app.route('/contact')
def contact():
    lang = session.get('lang', 'en')
    return render_template('contact.html', lang=lang, translations=translations[lang])

@app.route('/blog')
def blog():
    lang = session.get('lang', 'pl')
    posts = get_all_posts()

    # Format dates for all posts
    for post in posts:
        post['date_formatted'] = format_date(post.get('date'), lang)
        post['updated_formatted'] = format_date(post.get('updated'), lang) if post.get('updated') else None

    return render_template('blog.html', lang=lang, translations=translations[lang], posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    lang = session.get('lang', 'pl')
    post = get_post_by_slug(slug)
    if not post:
        return render_template('404.html', lang=lang, translations=translations[lang]), 404

    # Format dates for display
    post['date_formatted'] = format_date(post.get('date'), lang)
    post['updated_formatted'] = format_date(post.get('updated'), lang) if post.get('updated') else None

    # Convert markdown content to HTML (use appropriate language)
    content_key = 'content_pl' if lang == 'pl' else 'content_en'
    content_text = post.get(content_key, '')
    html_content = markdown.markdown(
        content_text,
        extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'nl2br'
        ],
        extension_configs={
            'codehilite': {
                'guess_lang': False,
                'use_pygments': False,
                'noclasses': True
            }
        }
    )
    post['html_content'] = html_content

    return render_template('blog_post.html', lang=lang, translations=translations[lang], post=post)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
