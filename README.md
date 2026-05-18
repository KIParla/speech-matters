# Speech Matters — 2nd Edition

Materials for the **Speech Matters** summer school (2nd edition),
hosted at Villa del Grumello, Como, Italy.

> [spma.lakecomoschool.org](https://spma.lakecomoschool.org/program/)

---

## Lab: Git as a Collaborative Environment for Multilayer Spoken Resource Development

**Instructor:** Dr. Ludovica Pannitto — Alma Mater Studiorum, Università di Bologna

This lab introduces automation, reproducibility, and collaborative workflows for spoken corpus development, using NLP resources, UD-compliant formats, and GitOps methodologies.

### Session structure

The 90-minute session combines a lecture with a hands-on component:

| Part | Content |
|------|---------|
| Part 1 | Why spoken corpora are hard to manage collaboratively |
| Part 2 | Git & GitHub core concepts — live demo on a toy corpus |
| Part 3 | The spoken corpus case: pivot formats, layered annotation |
| Part 4 | Hands-on walkthrough — participants fork, annotate, open PRs |

### What participants do

Working in pairs, participants fork a toy spoken Italian corpus, annotate stub TSV files following UD UPOS guidelines, commit their changes, open pull requests, and review each other's work — while a GitHub Actions workflow validates every commit automatically.

---

## Repository contents

```
speech-matters/
├── hands-on/           ← slides and demo plan for the lab
│   ├── index.html      ← presentation renderer (open in browser)
│   ├── section1.md     ← Part 1: collaborative challenges
│   ├── section2.md     ← Part 2: Git & GitHub concepts
│   ├── section3.md     ← Part 3: spoken corpus case
│   ├── section4.md     ← Part 4: hands-on walkthrough
│   ├── md2slides.py    ← rebuilds index.html from Markdown sections
│   ├── DEMO_PLAN.md    ← facilitator guide and pre-session checklist
│   └── README.md       ← how to view and edit the slides
└── layers-of-cooperation/   ← (forthcoming)
```

### Viewing the slides

```bash
cd hands-on
python3 -m http.server 8000
# then open http://localhost:8000
```

Or push to GitHub and enable Pages (**Settings → Pages → Source: main**).

---

## References

- Pannitto, L. & Mauri, C. (2025). Reuse by design: a pivot-based architecture for the KIParla corpus. *forthcoming*.
- Pannitto et al. (2025). Introducing KIParla Forest. *DepLing / SyntaxFest 2025*.
- Waldon, B. & Schneider, N. (2025). A GitHub-based workflow for annotated resource development. *LAW XIX*.
- de Marneffe et al. (2021). Universal Dependencies. *Computational Linguistics* 47(2).
- Steiner, I. (2017). A DevOps manifesto for speech corpus management. *ESSV*.
