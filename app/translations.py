from datetime import datetime


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
        'contact': 'Kontakt',
        'my_projects': 'Lista moich projektów.',
        'my_contact': 'Możesz się ze mną skontaktować przez e-mail: mpiotro4@outlook.com.',
        'read_more': 'Czytaj więcej',
        'back_to_blog': 'Powrót do bloga',
        'no_posts': 'Brak postów na blogu.',
        'published': 'Opublikowano',
        'updated': 'Zaktualizowano',
        'author': 'Autor',
        'tags': 'Tagi',
        'page': 'Strona',
        'of': 'z',
        'previous': 'Poprzednia',
        'next': 'Następna',
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
        'contact': 'Contact',
        'my_projects': 'List of my projects.',
        'my_contact': 'You can contact me via email: mpiotro4@outlook.com.',
        'read_more': 'Read more',
        'back_to_blog': 'Back to blog',
        'no_posts': 'No posts yet.',
        'published': 'Published',
        'updated': 'Updated',
        'author': 'Author',
        'tags': 'Tags',
        'page': 'Page',
        'of': 'of',
        'previous': 'Previous',
        'next': 'Next',
    }
}
