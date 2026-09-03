# Portfolio Website

Personal portfolio website built with Flask and Sass.

## Development

### CSS/Sass

This project uses Sass for styling. Source files are in `static/scss/`, compiled CSS goes to `static/css/`.

#### File Structure
```
static/
├── scss/               # Sass source files
│   ├── _variables.scss # Sass variables (colors, sizes, etc.)
│   ├── _mixins.scss    # Reusable mixins
│   ├── _base.scss      # Base styles
│   ├── _layout.scss    # Header & footer
│   ├── _navigation.scss # Navigation & menu
│   ├── _components.scss # Reusable components
│   ├── _projects.scss  # Project section
│   ├── _blog.scss      # Blog styles
│   └── main.scss       # Main file (imports all modules)
└── css/                # Compiled CSS (auto-generated)
```

#### Available Commands

**Build CSS once:**
```bash
npm run sass:build
```

**Watch for changes (auto-compile):**
```bash
npm run sass:watch
```

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

2. Build CSS:
```bash
npm run sass:build
```

3. Run the application:
```bash
python wsgi.py
```

## Static export (GitHub Pages)

The site is exported to plain HTML with [Frozen-Flask](https://frozen-flask.readthedocs.io/)
and served from `https://mpiotro4.github.io/mpiotro-pl/`.

- Polish lives at the root (`/`), English is mirrored under `/en/`.
- Language is chosen by URL prefix (no server session), so both trees are fully static.
- Every URL is prefixed with `/mpiotro-pl/` via `SITE_BASE_URL` in `freeze.py`.

Build locally:
```bash
npm run freeze          # compiles CSS, then runs freeze.py -> build/
```

Preview the build (paths are absolute, so serve it under the sub-path):
```bash
mkdir -p /tmp/preview && ln -sfn "$PWD/build" /tmp/preview/mpiotro-pl
python -m http.server -d /tmp/preview 8000
# open http://localhost:8000/mpiotro-pl/
```

Deployment is automatic: `.github/workflows/deploy-pages.yml` builds and publishes
to GitHub Pages on every push to `master`. Enable it once under
**Settings → Pages → Source → GitHub Actions**.

## Syntax Highlighting

Blog posts support syntax highlighting for code snippets using Prism.js. Supported languages:
- Java
- SQL
- YAML
- Python
- JavaScript
- Bash
- JSON
- CSS/SCSS
- Docker
- Markdown

To use syntax highlighting in blog posts, use fenced code blocks with language specifier:

\`\`\`java
public class Example {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
\`\`\`

## Notes

- **DO NOT** edit files in `static/css/` directly - they are auto-generated
- Edit Sass files in `static/scss/` instead
- Run `npm run sass:build` after making changes
- Use `npm run sass:watch` during development for auto-compilation
