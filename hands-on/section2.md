# Git & GitHub: core concepts

---

## Before we start: forming groups

1. Everyone stands up
2. *"If you have used Git before — even once — move to the left side of the room. If not, stay right."*
3. *"Now within each half: if you speak Italian, move to the front. Otherwise, the back."*
4. Count heads in each quadrant; divide by target group size (4–5)
5. Take one person from each quadrant in turn to fill each group
6. Once in groups, assign roles by counting off: **1 = Manager · 2 = Annotators**

One rule: the Git-experienced person **explains, does not type**. Others drive the keyboard.

---

## From the problem to the tool

So: often spoken corpus pipelines suffer from

- Opacity — decisions are not recorded > because it takes a lot of time to track things!
- Irreversibility — changes cannot be undone safely > how should we propagate changes to all artifacts? Better not to change anything...
- Bottlenecks — knowledge concentrated in one person > the PI often is the only one aware of the entire ecosystem
- Static releases — no clear relation between releases

---

## We have all seen this

```
BOA1010_final.eaf
BOA1010_final_revised.eaf
BOA1010_final_revised_2.eaf
BOA1010_FINAL_USE_THIS_ONE.eaf
BOA1010_FINAL_USE_THIS_ONE_v2_corrected.eaf
BOA1010_FINAL_USE_THIS_ONE_v2_corrected_LP.eaf
```

- Which is the authoritative version?
- Who made the `_corrected` changes, and why?
- Do you know exactly what changed from `BOA1010_FINAL_USE_THIS_ONE.eaf` to `BOA1010_FINAL_USE_THIS_ONE_v2_corrected.eaf`?
- What happens when two annotators work on different copies?

*Software Carpentry (2024)*

---

## What is a version control system?

A **Version Control System (VCS)** records changes to a file repository over time.

Instead of keeping multiple copies of a file, it stores a **base version** and a **sequence of changes**:

```
BOA1010 [base — initial transcription]
    │  commit a3f9c12  "initial ELAN transcription"
    ↓
BOA1010 + Δ1
    │  commit b7e2a41  "add UPOS tags tokens 1–20"
    ↓
BOA1010 + Δ1 + Δ2
    │  commit c1d8f33  "fix overlap annotation token 14"
    ↓
BOA1010 + Δ1 + Δ2 + Δ3          ← current state
```

Any past version is reconstructible. Any change can be undone.
The **commit message is the rationale**, stored permanently alongside the change.

> "Version control is like an unlimited undo — and it also allows many people to work in parallel."
>
> — *Software Carpentry, Version Control with Git (2024)*

It allows a team to:

- Track *who* changed *what* and *when*
- Compare any two states of the project
- Revert to any previous state
- Work in parallel without conflicts

Version control is standard practice in software engineering.
It is still underused in linguistic annotation, despite the fact that **annotation is a form of collaborative software development**.

---

## Why not just use Track Changes?

The closest familiar tool is *Track Changes* in word processors. It fails for annotation work because:

| Limitation                        | Consequence for annotation                                         |
| --------------------------------- | ------------------------------------------------------------------ |
| History is **lost on acceptance** | Authorship and rationale vanish once changes are merged            |
| No **parallel branches**          | Collaborators must work sequentially or merge manually             |
| **Not plain-text friendly**       | Does not work with CoNLL-U, TSV, XML — the formats we actually use |
| No **programmatic access**        | You cannot run a validation script or trigger a conversion         |
| No **conflict detection**         | Two people editing the same span silently overwrite each other     |

> Track Changes is designed for a document that reaches a final state.
> A corpus is never final — it is a living artefact.

*Software Carpentry (2024)*

---

## Git: the most widely used VCS

**Git** is a distributed version control system.
Every contributor has a full copy of the repository history.

Key properties:

- **Free and open source**
- Works entirely on the command line — but has many GUI frontends
- Designed for plain text files → ideal for CoNLL-U, TSV, XML, Markdown
- Does not (necessarily) require a server — repositories live on your machine
- Integrates with hosting platforms: GitHub, GitLab, own server

*Created by Linus Torvalds in 2005 for Linux kernel development*

**GitHub** is a web-based hosting service for Git repositories.

---

## The five concepts you need -- and we'll go over during this tutorial

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
├── eaf/                        ← original ELAN transcriptions
│   ├── BOA1010.eaf
│   └── PSB054.eaf
├── pivot/                      ← maintained TSV representation
│   ├── BOA1010.tsv
│   └── PSB054.tsv
├── derived/                    ← formats generated from the pivot
│   ├── conllu/
│   │   ├── BOA1010.conllu
│   │   └── PSB054.conllu
│   ├── vert/
│   │   └── corpus.vert
│   └── jefferson/
│       └── BOA1010.txt
├── scripts/                    ← validation and conversion
│   ├── validate.py
│   ├── eaf_to_pivot.py
│   └── pivot_to_conllu.py
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

## Exercise 1 — Create your first repository

```bash
# 1. Create a project folder and enter it
mkdir my-corpus && cd my-corpus

# 2. Initialise a Git repository
git init

# 3. Check what Git sees
git status

# 4. Create and open a README file in VSCode
touch README.md
code README.md
# Add a line: "# My corpus", then save

# 5. Check status again — notice README is now "untracked"
git status
```

**What to observe:**

- `git init` creates a hidden `.git/` folder — that is the entire history database
- `git status` reports which files Git knows about and which it does not
- An untracked file exists on disk but is invisible to Git until you `git add` it

---

## Local and remote repositories

In a distributed VCS, every collaborator has a **full copy** of the repository.
Git distinguishes two kinds:

- **Remote repo** — hosted on a server (GitHub, GitLab, institutional server); the shared reference point for the team
- **Local repo** — on your personal machine; where you actually do your work

The three operations that connect them:

```
git clone <url>   # copy the remote repo to your machine — done once
git pull          # fetch the latest commits from remote into your local repo
git push          # send your local commits up to the remote
```

```
remote repo (GitHub)
      │  clone ↓        ↑ push / ↓ pull
      ├── Maria's local repo    (annotates BOA1010)
      └── Giulio's local repo   (annotates PSB054)
```

Each annotator works locally and commits at their own pace.
Changes reach the shared remote only via an explicit `push`.

*Zeman, Savary & Guillaume (2024)*

---

## Exercise 2 — Stage and commit

Continuing from Exercise 1:

```bash
# 1. Stage the README
git add README.md

# 2. Check status — README is now "staged"
git status

# 3. Make your first commit
git commit -m "Initial commit: add README"

# 4. View the commit log
git log --oneline

# 5. Edit the README, then check what Git sees
code README.md
# Add a line: "Spontaneous spoken Italian corpus", then save
git status
git diff README.md
```

**What to observe:**

- `git diff` shows exactly which lines changed before you stage them
- `git log` shows the commit hash, author, timestamp, and message
- After committing, the working directory is "clean" again

---

## Troubleshooting: "Please tell me who you are"

If `git commit` fails with an error like:

```
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"
```

Git needs to know who is making the commit. Run these **once** on your machine:

```bash
git config --global user.email "your.email@example.com"
git config --global user.name "Your Name"
```

Use your real name and the email linked to your GitHub account.
After that, retry `git commit`.

---

## How a diff summarizes what changed

In Exercise 2 you opened `README.md` in VSCode and added a second line, then ran:

```bash
git diff README.md
```

Your README started as a single line:

```
# My corpus
```

After saving the file it has a second line:

```
# My corpus
Spontaneous spoken Italian corpus
```

`git diff README.md` collapses that to:

```diff
@@ -1 +1,2 @@
 # My corpus
+Spontaneous spoken Italian corpus
```

Lines with `+` were added. Unchanged context lines (no prefix) anchor the change in the file.
The `@@` header tells you the line numbers: the old file had 1 line starting at line 1; the new version has 2 lines.

---

## The four states of a file

Every file in a Git repository is in one of four states:

```
[untracked]                         not known to Git
     │  git add
     ▼
[staged]         change selected, ready to be included in the next commit
     │  git commit
     ▼
[committed / unmodified]            safely stored in the Git database
     │  edit file
     ▼
[modified]       file changed on disk, but change not yet staged
     │  git add
     ▼
[staged] → ...
```

Three areas a file moves through:

| Area              | Location               | Role                           |
| ----------------- | ---------------------- | ------------------------------ |
| Working directory | `project/`             | where you edit                 |
| Staging area      | `project/.git/index`   | what goes into the next commit |
| Git database      | `project/.git/objects` | permanent history              |

The staging step lets you commit **some** changes from your working directory while leaving others for a later commit — useful when one session touches multiple annotation files but only one is ready for review.

*Zeman, Savary & Guillaume (2024)*

---

## Concept 2: Commit

A **commit** records the state of one or more files at a specific point in time.

```bash
git add annotations/BOA1010.conllu
git commit -m "Add UPOS tags for BOA1010, tokens 1-45"
```

Each commit has:

- A **unique hash** (e.g. `a3f9c12`) — a 40-character hexadecimal checksum calculated from the contents of all tracked files; Git shortens it to the first 6–7 characters for display
- A **message** — the annotation rationale, in plain language
- A **diff** — exactly which lines changed
- **Author** and **timestamp**

→ The commit message *is* the annotation justification. It lives permanently in the history.

---

## What a diff looks like

From `speech-matters-demo`: an annotator fills in the missing dependency head and relation for token 19 (`sì`) in sentence `BOD2018_138_139`.

```diff
 18  più   più   ADV   _  _  20  advmod    _  KID=138-17|Prolonged=Yes
-19  sì    sì    ADV   _  _  _   _         _  Clitic=Yes|KID=138-18
+19  sì    sì    ADV   _  _  20  discourse _  Clitic=Yes|KID=138-18
 20  anni  anno  NOUN  _  _  0   root      _  KID=138-19
```

Column 7 is the head token; column 8 is the syntactic relation.
The commit message explains *why*: `"sì at 138-18 is a discourse marker attached to root anni (20)"`.

→ The diff + message together are a **permanent, auditable annotation decision**

---

## Exercise 2b — Push your repository to GitHub

Before exploring an existing repo, let's put your own work on GitHub.

**Step 1 — Create a new repository on GitHub**

1. Go to [github.com](https://github.com) and log in
2. Click **+** → **New repository**
3. Name it `my-corpus`; leave it **empty** (no README, no .gitignore)
4. Click **Create repository**

**Step 2 — Connect your local repo and push**

```bash
# Add GitHub as the remote (paste the URL from the GitHub page)
git remote add origin https://github.com/<your-username>/my-corpus.git

# Rename the default branch to "main" (if not already)
git branch -M main

# Push your commits
git push -u origin main
```

After pushing, refresh the GitHub page — your `README.md` and commit history should be visible.

---

## Exercise 3 — Fork, clone, and explore a richer history

This exercise uses **speech-matters-demo**, a pre-built repository with several commits already in it.

**Step 1 — Fork and clone**

1. Go to `github.com/KIParla/speech-matters-demo`
2. Click **Fork** (top-right) — this creates your own copy on GitHub
3. Clone your fork to your machine:

```bash
git clone https://github.com/<your-username>/speech-matters-demo.git
cd speech-matters-demo
```

**Step 2 — Inspect the history**

```bash
# 1. View the full commit history
git log --oneline

# 2. See exactly what changed in a specific commit
#    (use the hash of "add speaker and conversation metadata for BOD2018")
git show <hash>

# 3. Travel back to an earlier state of the whole repository
git checkout <earlier-hash>    # HEAD is now "detached"
ls                             # the working directory reflects that past state

# 4. Come back to the present
git checkout main
git status                     # should be clean
```

**What to observe:**

- `git log --oneline` gives you a compact timeline of every decision in the project
- `git show <hash>` displays the full diff for any past commit — message, author, and changed lines
- `git checkout <hash>` moves the entire working directory to that past state ("detached HEAD")
- `git checkout main` brings you back — Git does not forget anything

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

---

## Exercise 4 — Create and switch branches

```bash
# 1. Create a new branch for annotation work
git checkout -b annotator/BOA1010

# 2. Check which branch you are on
git branch

# 3. Make a change on this branch — create and open a new file in VSCode
mkdir -p pivot

# Add a header line: token_id	speaker	form  (tab-separated), then save
git add pivot/BOA1010.tsv
git commit -m "Add BOA1010 pivot stub"

# 4. Switch back to main — the file you just added is not here
git checkout main
ls pivot/

# 5. Switch back to your branch — the file reappears
git checkout annotator/BOA1010
ls pivot/
```

**What to observe:**

- `git branch` shows all branches; the current one is marked with `*`
- Switching branches changes the working directory — files appear and disappear
- `main` is unaffected by anything you do on your branch

---

## When two people edit the same file: conflicts

A **conflict** occurs when two collaborators modify the **same lines** of the same file independently,
and one tries to push after the other has already done so.

```
Maria pushes commit 1  →  remote updated
Giulio tries to push commit 2  →  REJECTED: remote has commits Giulio doesn't have
    Giulio must first: git pull
    Git attempts automatic merge
    If the same lines were changed by both: CONFLICT — must be resolved manually
```

What a conflict looks like inside the file:

```diff
<<<<<<< HEAD  (Giulio's version)
1  e  e  CCONJ  _  _  3  cc    _  _
=======
1  e  e  PART   _  _  3  mark  _  _
>>>>>>> origin/main  (Maria's version)
```

Giulio must choose one version (or write a combined one), remove the conflict markers, and commit.

**How the branch workflow prevents this**: annotators work on **separate branches**, usually on **separate files**. Conflicts only arise if two people touch the same token in the same file — which the branch + pull-request model makes rare and detectable before merge.

*Zeman, Savary & Guillaume (2024)*

---

## Concept 4: Pull request

A **pull request (PR)** is a proposal to merge a branch into `main`.

It is also a **collaborative space**:

1. Annotator opens a PR: *"I've annotated BOA1010, please review"*
2. Manager sees a visual diff of every changed line
3. Manager (or automated action) checks validation output
4. Discussion happens in threaded comments, **permanently recorded**
5. Manager either approves → merge, or requests changes → annotator revises

> The PR thread is the adjudication record.
> Every decision, every disagreement, every resolved ambiguity — preserved forever, publicly auditable.

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

## Exercise 5 — Push and open a pull request on GitHub

```bash
# 1. Push your branch to GitHub
git push -u origin annotator/BOA1010
```

Then in the browser:

1. Go to your repository on GitHub
2. Click **"Compare & pull request"** (GitHub shows this automatically after a push)
3. Write a title: `"Add BOA1010 pivot stub"`
4. In the description, explain what you did and why
5. Click **"Create pull request"**
6. Browse the **Files changed** tab — this is what a reviewer sees
7. Leave a comment on a specific line (click the `+` that appears on hover)
8. Merge the PR into `main`

**What to observe:**

- The diff view shows exactly which lines were added or changed
- Comments are anchored to specific lines and preserved forever
- After merge, `main` contains your changes and the branch can be deleted

---

## No terminal required: the GitHub web editor

Everything in Exercises 3–5 is possible entirely from the browser — no `git clone`, no terminal.

| Action          | How                                                      |
| --------------- | -------------------------------------------------------- |
| Fork a repo     | Click **Fork** on any GitHub repo page                   |
| Create a branch | Branch dropdown → type name → **Create branch**          |
| Edit a file     | Click the pencil icon on any file                        |
| Commit          | Scroll to "Commit changes" at the bottom of the editor   |
| Open a PR       | Click **Compare & pull request** after pushing           |
| Review a PR     | **Files changed** tab → click `+` on any line to comment |
| Merge           | Click **Merge pull request**                             |

Useful for annotators who are new to version control — they can start contributing immediately without any local setup.

---

## Three actions for annotation workflows

| Action         | Triggered by    | What it does                                        |
| -------------- | --------------- | --------------------------------------------------- |
| **Validate**   | Every commit    | Checks annotation schema, flags malformed tokens    |
| **Visualize**  | Every commit    | Renders annotation as a readable PDF/SVG            |
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

---

## Monitoring the project: Issues and permalinks

Beyond commits and pull requests, GitHub provides two tools for tracking *what is happening and why*:

**Issues** — a structured discussion thread attached to the repository:

- Report an annotation error found after merge
- Raise a guideline ambiguity ("should overlap marker go on PKP019 or PKP014?")
- Track a decision to its resolution, with full comment history
- Link an issue to the commit or PR that fixed it — closes automatically on merge

**Permalinks** — a permanent URL pointing to a specific line or commit:

- `github.com/.../BOA1010.conllu#L42` → links to token 42 in the current file
- `github.com/.../blob/<commit-hash>/BOA1010.conllu#L42` → links to that line *as it was at that exact commit*

Together they make the project **auditable**: every annotation decision has a discussion thread; every discussion thread can point to the exact line of data it concerns; every line of data can be traced back to the commit that introduced it.

---

## What about the learning curve?

Annotators unfamiliar with Git face a real barrier. Mitigation strategies:

| Challenge                     | Solution                                                 |
| ----------------------------- | -------------------------------------------------------- |
| Command line is intimidating  | GitHub web editor — edit and commit from the browser     |
| Branch/merge concepts unclear | Visual tools: GitHub Desktop, VS Code Git panel          |
| YAML for Actions is complex   | Manager writes Actions once; annotators never touch them |
| Fear of breaking things       | Branches protect `main` — mistakes stay local            |

> The goal is not to turn linguists into software engineers.
> The goal is to give annotation projects **the same reliability guarantees** that software projects have.

