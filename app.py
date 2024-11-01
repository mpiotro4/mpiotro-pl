import os

from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

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
        'cv': 'CV',
        'contact': 'Kontakt',
        'my_projects': 'Lista moich projektów.',
        'my_cv': 'Moje CV.',
        'my_contact': 'Możesz się ze mną skontaktować przez e-mail: mpiotro4@outlook.com.',
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
        'cv': 'CV',
        'contact': 'Contact',
        'my_projects': 'List of my projects.',
        'my_cv': 'My CV.',
        'my_contact': 'You can contact me via email: mpiotro4@outlook.com.',
    }
}


@app.route('/')
def home():
    lang = session.get('lang', 'en')
    return render_template('index.html', lang=lang, translations=translations[lang])

@app.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    return redirect(url_for('home'))

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
