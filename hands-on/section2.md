# Git & GitHub: core concepts

**Summer School Lab · Part 2 of 4**
Dr. Ludovica Pannitto — Università di Bologna

---

## From the problem to the tool

In Part 1 we established that spoken corpus pipelines suffer from:

- Opacity — decisions are not recorded
- Irreversibility — changes cannot be undone safely
- Bottlenecks — knowledge concentrated in one person
- Static releases — errors persist across versions

**Part 2** introduces the toolbox that addresses all four problems at once.

---

## What is a version control system?

A **Version Control System (VCS)** records changes to a file repository over time.

It allows a team to:

- Track *who* changed *what* and *when*
- Compare any two states of the project
- Revert to any previous state
- Work in parallel without conflicts

> Version control is standard practice in software engineering.
> It is still underused in linguistic annotation — despite the fact that **annotation is a form of collaborative software development**.

---

## Git: the most widely used VCS

**Git** is a distributed version control system. Every contributor has a full copy of the repository history.

Key properties:
- **Free and open source**
- Works entirely on the command line — but has many GUI frontends
- Designed for plain text files → ideal for CoNLL-U, TSV, XML, Markdown
- Does not require a server — repositories live on your machine
- Integrates with hosting platforms: GitHub, GitLab, Codeberg

*Created by Linus Torvalds in 2005 for Linux kernel development*

---

## GitHub: Git with collaboration superpowers

**GitHub** is a web-based hosting service for Git repositories.

Git provides version control. GitHub adds:

| Git (local) | GitHub (web platform) |
|---|---|
| Commit history | Visual diff viewer |
| Branches | Pull requests |
| Merge | Code review interface |
| Tags | Releases |
| Hooks | GitHub Actions (CI/CD) |
| — | Issues (discussion threads) |
| — | Community forks |

*All of this is free for public repositories — including academic projects.*

---

## The five concepts you need

Everything in the Git/GitHub workflow reduces to five ideas:

1. **Repository** — the project and its full history
2. **Commit** — a timestamped snapshot with a message
3. **Branch** — a parallel working copy
4. **Pull request** — a proposal to merge, with review
5. **Action** — an automated script triggered by events

We will map each one to corpus annotation.

---

## Concept 1: Repository

A **repository** (repo) is a directory whose full history of changes is tracked by Git.

```
my-corpus/
├── annotations/
│   ├── BOA1010.conllu
│   └── PSB054.conllu
├── scripts/
│   ├── validate.py
│   └── convert_to_conllu.py
├── metadata/
│   └── speakers.tsv
└── README.md
```

The repo stores:
- All annotation files (every version, forever)
- All processing scripts
- All metadata and documentation
- The complete record of every change ever made

---

## Concept 2: Commit

A **commit** records the state of one or more files at a specific point in time.

```bash
git add annotations/BOA1010.conllu
git commit -m "Add UPOS tags for BOA1010, tokens 1-45"
```

Each commit has:
- A **unique hash** (e.g. `a3f9c12`) — an immutable identifier
- A **message** — the annotation rationale, in plain language
- A **diff** — exactly which lines changed
- **Author** and **timestamp**

→ The commit message *is* the annotation justification. It lives permanently in the history.

---

## What a diff looks like

```diff
# sent_id = BOA1010-003
# text = e quindi studi: pittura?

-1  e      _    _    _    _  0  root  _  _
-2  quindi _    _    _    _  0  root  _  _
+1  e      e    CCONJ _   _  3  cc    _  _
+2  quindi quindi ADV _   _  3  advmod _  _
 3  studi  studiare VERB _  _  0  root  _  _
```

Lines prefixed `-` were removed · lines prefixed `+` were added

→ The diff is a **human-readable record of every annotation decision**

---

## Concept 3: Branch

A **branch** is a parallel instance of the repository.

```
main branch (gold annotations, always valid)
    │
    ├── annotator/BOA1010        ← Maria's working copy
    ├── annotator/PSB054         ← Giulio's working copy
    └── fix/overlap-tokens       ← bug fix in progress
```

Rules:
- `main` is always in a valid, releasable state
- Annotators work on their own branch — **nothing they do affects main**
- When work is ready, it is *proposed* for merging via a pull request

→ Parallel annotation without conflicts

---

## Concept 4: Pull request

A **pull request (PR)** is a proposal to merge a branch into `main`.

It is also a **collaborative space**:

1. Annotator opens a PR: *"I've annotated BOA1010, please review"*
2. Manager sees a visual diff of every changed line
3. Manager (or automated action) checks validation output
4. Discussion happens in threaded comments, **permanently recorded**
5. Manager either approves → merge, or requests changes → annotator revises

> The PR thread is the adjudication record. Every decision, every disagreement, every resolved ambiguity — preserved forever, publicly auditable.

---

## A pull request in practice

```
PR #14 — Annotate BOA1010 tokens 1-45
Opened by: m.rossi · Branch: annotator/BOA1010

  ✓ Validation passed (validate.py)
  ✓ Visualization rendered (BOA1010-tree.pdf)

  Files changed: 1   +47 lines   -3 lines

  ── Review comment (g.bianchi, manager) ──────────────────
  Token 2 "quindi": I'd argue SCONJ not ADV here.
  See guideline §4.2. What do you think?

  ── Reply (m.rossi, annotator) ───────────────────────────
  You're right — checking §4.2. Will fix in next commit.

  [2 commits] [Approved] [Merged into main]
```

---

## Concept 5: GitHub Actions

A **GitHub Action** is a script that runs automatically when a repository event occurs.

```yaml
# .github/workflows/validate.yml
name: Validate CoNLL-U
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/validate.py annotations/
```

Triggered on every commit or PR — no manual steps needed.

---

## Three actions for annotation workflows

| Action | Triggered by | What it does |
|---|---|---|
| **Validate** | Every commit | Checks annotation schema, flags malformed tokens |
| **Visualize** | Every commit | Renders annotation as a readable PDF/SVG |
| **Statistics** | Merge into main | Updates token counts, label distributions, progress |

→ Annotators get *instant feedback* without waiting for a reviewer
→ Reviewers see a *rendered tree*, not raw CoNLL-U
→ Project stats are always *up to date*

---

## The full workflow

```
MANAGER                          ANNOTATOR
──────────────────────────────────────────────────────
Creates stub files on main
  └── BOA1010.conllu (pre-tokenized)
                                 Creates working branch
                                   annotator/BOA1010
                                 Fills in annotations
                                 git commit → Actions fire
                                   ✓ validate
                                   ✓ visualize
                                 Opens pull request
Reviews diff + rendered tree
Leaves comments if needed
                                 Revises (new commits)
Approves → Merge
  └── statistics Action fires
      └── main updated
```

*Waldon & Schneider (2025)*

---

## Already in use: Universal Dependencies

**Universal Dependencies** (UD) is the largest multilingual treebank collection in existence — 100+ languages, maintained by a global community.

UD uses GitHub for:
- Hosting all treebank repositories
- Discussing annotation guidelines (Issues)
- Tracking errors and corrections (Issues + PRs)
- Releasing versioned datasets (GitHub Releases + Zenodo)

> `github.com/UniversalDependencies` — 200+ repositories, thousands of contributors

→ The infrastructure already exists. We are not proposing something new — we are proposing **applying it to spoken corpus work**.

---

## What about the learning curve?

Annotators unfamiliar with Git face a real barrier. Mitigation strategies:

| Challenge | Solution |
|---|---|
| Command line is intimidating | GitHub web editor — edit and commit from the browser |
| Branch/merge concepts unclear | Visual tools: GitHub Desktop, VS Code Git panel |
| YAML for Actions is complex | Manager writes Actions once; annotators never touch them |
| Fear of breaking things | Branches protect `main` — mistakes stay local |

> The goal is not to turn linguists into software engineers.
> The goal is to give annotation projects **the same reliability guarantees** that software projects have.

---

## Part 2 — Summary

- A **repository** stores all files and their complete history
- A **commit** is a timestamped, labelled snapshot — the annotation justification
- A **branch** lets annotators work safely in parallel
- A **pull request** is the adjudication interface — discussion, review, merge
- **Actions** automate validation, visualization, and statistics
- The workflow is already proven at scale in Universal Dependencies
- **Part 3** will re-examine these concepts in the specific context of spoken corpus data: binary audio, GDPR, multilayer formats, and the pivot architecture

---

*References*

- de Marneffe et al. (2021). Universal Dependencies. *Computational Linguistics* 47(2).
- Palmer, M. & Xue, N. (2010). Linguistic annotation. Chapter 10.
- San, N. (2016). Using version control for a reproducible workflow in acoustic phonetics. *SST2016*.
- Steiner, I. (2017). A DevOps manifesto for speech corpus management. *ESSV*.
- Waldon, B. & Schneider, N. (2025). A GitHub-based workflow for annotated resource development. *LAW XIX*.
