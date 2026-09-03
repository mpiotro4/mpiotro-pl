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
and served from the custom domain `https://mpiotro.pl/`.

- Polish lives at the root (`/`), English is mirrored under `/en/`.
- Language is chosen by URL prefix (no server session), so both trees are fully static.
- `SITE_BASE_URL` (env, default `https://mpiotro.pl/`) sets link paths and, for a
  non-`github.io` host, makes `freeze.py` emit the `CNAME` file.

Build locally:
```bash
npm run freeze          # compiles CSS, then runs freeze.py -> build/
python -m http.server -d build 8000   # open http://localhost:8000/
```

Deployment is automatic: `.github/workflows/deploy-pages.yml` builds and publishes
to GitHub Pages on every push to `master`. One-time setup:

1. **Settings → Pages → Source → GitHub Actions**
2. **Settings → Pages → Custom domain** → `mpiotro.pl` → wait for the DNS check,
   then tick **Enforce HTTPS**
3. DNS: `A @` → `185.199.108.153` / `.109` / `.110` / `.111`, and
   `CNAME www` → `mpiotro4.github.io.`

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
