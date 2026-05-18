# git-spoken-corpus-slides

Slides for the summer school lab:
**"Git as a Collaborative Environment for Multilayer Spoken Resource Development"**

Dr. Ludovica Pannitto — Università di Bologna

## Structure

```
slides/
├── index.html       ← presentation renderer (open this in a browser)
├── section1.md      ← Part 1: Why spoken corpora are hard to manage collaboratively
├── section2.md      ← Part 2: Git & GitHub core concepts (coming soon)
├── section3.md      ← Part 3: The spoken corpus case (coming soon)
├── section4.md      ← Part 4: Hands-on walkthrough (coming soon)
└── README.md
```

## How to use

### Locally

Open `index.html` in a browser. The renderer will load the Markdown file directly.

> **Note**: If you open `index.html` via `file://` (double-click), some browsers block
> local `fetch()` calls. Either:
> - Use a local server: `python3 -m http.server 8000` then open `http://localhost:8000`
> - Or use VS Code Live Server / any static server

### Via GitHub Pages

1. Push this repo to GitHub
2. Go to **Settings → Pages → Source: main branch / root**
3. Your slides will be live at `https://<username>.github.io/<repo>/`

## Navigation

| Key              | Action            |
| ---------------- | ----------------- |
| `→` or `Space`   | Next slide        |
| `←`              | Previous slide    |
| `F`              | Toggle fullscreen |
| Swipe left/right | Mobile navigation |

## Adding or editing slides

All content lives in the Markdown files. Each slide is separated by `---` on its own line.

```markdown
## Slide title

Some content here.

---

## Next slide
```

The renderer handles:
- Headings → slide titles
- Bullet lists
- Tables
- Code blocks (with syntax highlighting)
- Blockquotes → styled as pull quotes
- Italic-only paragraphs → styled as attribution/reference lines

## Companion repo

See [`git-spoken-corpus-demo`](https://github.com/your-username/git-spoken-corpus-demo)
for the hands-on annotation workflow demonstrated in Part 4.

## References

- Pannitto, L. & Mauri, C. (2025). Reuse by design: a pivot-based architecture for the KIParla corpus.
- Pannitto et al. (2025). Introducing KIParla Forest. *DepLing / SyntaxFest 2025*.
- Waldon, B. & Schneider, N. (2025). A GitHub-based workflow for annotated resource development. *LAW XIX*.
- Steiner, I. (2017). A DevOps manifesto for speech corpus management. *ESSV*.
