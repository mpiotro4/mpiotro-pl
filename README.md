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
python app.py
```

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
