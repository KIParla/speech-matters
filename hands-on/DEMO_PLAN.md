# Demo session plan — `git-spoken-corpus-demo`

> Facilitator guide and preparation checklist for the hands-on component of  
> *"Git as a Collaborative Environment for Multilayer Spoken Resource Development"*  
> Dr. Ludovica Pannitto — Alma Mater Studiorum, Università di Bologna

---

## Overview

The demo repo is a **toy spoken Italian corpus** that instantiates every concept
from the slides on real data. It has two functions running in parallel:

- **Live demo** during Part 2 of the lecture (instructor drives, participants watch)
- **Hands-on exercise** during Part 4 (participants drive on their own fork)

Total active time budgeted in the lecture plan: **20 minutes** (65–85 min of the
90-minute session). The repo is designed so that participants can keep working after
the session ends.

---

## Repo structure to prepare in advance

```
git-spoken-corpus-demo/
│
├── .github/
│   └── workflows/
│       ├── validate.yml      ← fires on every push / PR
│       └── stats.yml         ← fires on merge to main
│
├── annotations/
│   ├── BOA1010.stub.tsv      ← stub: pre-tokenized, lemma/upos empty
│   ├── PSB054.stub.tsv       ← stub: pre-tokenized, lemma/upos empty
│   └── SBCC003.stub.tsv      ← stub: 3-speaker overlap excerpt
│
├── scripts/
│   ├── validate.py           ← checks TSV schema, UPOS inventory, no blanks
│   └── stats.py              ← counts tokens, builds progress.json
│
├── guidelines/
│   └── ANNOTATION.md         ← concise UD UPOS guide + spoken-language notes
│
├── stats/
│   └── progress.json         ← auto-updated by stats Action on every merge
│
├── .gitignore                ← ignores *.wav, *.flac, audio/
└── README.md                 ← explains the repo, links to slides
```

---

## The stub files

Each stub is a valid pivot TSV with `lemma` and `upos` columns filled with `_`.
Content is pre-tokenized, pseudonymized, drawn from real KIParla sentences — short
enough to annotate in under 5 minutes.

### `BOA1010.stub.tsv` — easy

6 tokens, single speaker, no overlap.
The canonical starting file.
Includes one interesting case: `studi` (VERB vs. NOUN ambiguity, resolvable from
conversational context).

### `PSB054.stub.tsv` — intermediate

8 tokens, single speaker, one disfluency (`((sigh))`).
Tests the `nonverbalbehavior` token type: should it receive `INTJ` or remain
unannotated?
This ambiguity is intentional — it feeds the guidelines discussion.

### `SBCC003.stub.tsv` — advanced

10 tokens, two overlapping speakers.
The `jefferson_feats` column is pre-filled with `Volume=High` and
`Intonation=Rising` entries so participants can see the feature system in action.
Used for the advanced exercise or as a take-home task.

---

## The validation script

`scripts/validate.py` — pure Python, no external dependencies, runs in ~1 second.

Checks performed:

1. **TSV schema** — correct number of columns, correct header names, no stray whitespace
2. **Token ID format** — `\d+-\d+` pattern, sequential within each TU block
3. **UPOS inventory** — only valid UD UPOS tags permitted (or `_` for stub tokens)
4. **Lemma/UPOS coherence** — if `upos` is filled, `lemma` must not be `_`
5. **Type consistency** — `nonverbalbehavior` tokens must not carry syntactic UPOS tags

Exit codes: `0` on success, `1` on failure with a human-readable message naming the
exact row and column.

---

## The GitHub Actions

### `validate.yml`

- **Trigger:** every `push` and `pull_request` to any branch
- **What it does:** runs `validate.py` on all changed TSV files
- **Output:** surfaced in the Actions tab and as a PR status check
- **Runtime:** ~5 seconds

### `stats.yml`

- **Trigger:** `push` to `main` only (i.e. after a merge)
- **What it does:** runs `stats.py`, counts annotated vs. stub tokens, writes
  `stats/progress.json`, commits the result back to `main`
- **Runtime:** ~3 seconds

---

## The annotation guidelines

`guidelines/ANNOTATION.md` — ~2 pages, purpose-built for this exercise.

Contents:

- The 17 UD UPOS tags with a one-line description each
- Four spoken-language specific notes:
  - Discourse markers (`quindi`, `cioè`, `allora`) — ADV or SCONJ?
  - Filled pauses (`mh`, `eh`) — INTJ
  - Truncated words (`stu-`) — annotate the base form, flag with `Truncated=Yes`
  - Non-verbal behaviours (`((sigh))`) — `nonverbalbehavior` type, no UPOS
- Commit message convention: *what happened* + *why* (one sentence minimum for
  non-obvious choices)

The guidelines document is itself version-controlled.
Participants can open a GitHub Issue to propose changes — demonstrating the Issue
tracker as a living annotation forum.

---

## Session flow (20 minutes in the room)

### Phase 1 — Guided demo (instructor drives, ~8 min)

The repo is already set up before the session. Show, live on screen:

| Step | Action | Teaching point |
|------|--------|---------------|
| 1 | Open the repo on GitHub, walk through the directory tree | Repo as the unit of curation |
| 2 | Create branch `annotator/BOA1010` from the branch dropdown | Branches protect `main` |
| 3 | Open `BOA1010.stub.tsv` in the GitHub web editor, fill 3–4 tokens | No terminal needed |
| 4 | Commit with a message explaining the `studi` VERB choice | Commit = annotation rationale |
| 5 | Switch to the Actions tab, watch `validate.yml` run (~5s) | Automation fires on every commit |
| 6 | Open a pull request, show diff view and check status | PR = adjudication interface |
| 7 | Leave an inline review comment as manager | Discussion thread is permanent |
| 8 | Approve and merge, watch `stats.yml` update `progress.json` | Stats always up to date |

The full cycle takes 6–7 minutes at a relaxed pace.
Pause at steps 5 and 7 to let participants read the screen.

### Phase 2 — Parallel exercise (participants drive, ~12 min)

Participants work in **pairs**. Within each pair:

- **Person A** forks the repo, creates branch `annotator/PSB054`, annotates,
  commits, opens a PR
- **Person B** reviews Person A's PR, leaves at least one inline comment, then
  approves or requests changes

Swap roles for `SBCC003` if time allows; otherwise use it as a take-home exercise.

**Common friction points to watch for:**

- First-time GitHub users confused by the branch dropdown
  → point to the web editor path (no terminal required)
- UPOS uncertainty on `((sigh))`
  → good live moment to demonstrate opening a GitHub Issue on the guidelines
- Action failing due to wrong column count
  → demonstrate reading the error log, finding the offending row

### Debrief (3 min, immediately after)

Three questions for a quick round-table:

1. What did the validation Action catch that you would not have noticed yourself?
2. What would you change in the annotation guidelines based on what you annotated?
3. If this were a real 2M-token corpus with 10 annotators, what would you structure differently?

---

## Pre-session checklist

- [ ] Create `git-spoken-corpus-demo` on your GitHub account — make it **public**
- [ ] Push the directory structure above: stubs, scripts, Actions, guidelines
- [ ] Test the happy path: push a commit, verify `validate.yml` fires and passes
- [ ] Test the error path: set a token's UPOS to an invalid tag, verify the Action
      catches it and names the right row
- [ ] Enable GitHub Pages on `git-spoken-corpus-slides` — presentation live at a
      URL you can share
- [ ] Prepare a shortlink or QR code for both repos (e.g. `bit.ly/kiparla-demo`)
- [ ] Test the GitHub web editor on a phone — verify it works for participants
      without a laptop
- [ ] Open one pre-seeded Issue on the demo repo:
      *"Should `quindi` be ADV or SCONJ? See §3.4 of guidelines"*
      — gives participants a live example of the Issue tracker as a guidelines forum

---

## What participants take away

By the end of the 20 minutes, every participant has on their own GitHub account:

- A **fork** of a real version-controlled spoken corpus
- At least one **branch** with their own annotation commits
- At least one **PR** — either opened or reviewed
- Direct experience of a GitHub Action **passing** and (likely) **failing**
- A **peer-review comment thread** they wrote or received

The repo persists after the summer school. Participants can continue annotating,
open Issues, and use it as a template for their own projects.

---

## Relationship between the two repos

| | `git-spoken-corpus-slides` | `git-spoken-corpus-demo` |
|---|---|---|
| **Role** | Explains the concepts | Instantiates the concepts |
| **Access** | Served via GitHub Pages | Forked and worked on live |
| **Cross-link** | README → demo repo | README → slides (Part 4, Step 1) |
| **Key script** | `md2slides.py` rebuilds HTML | `validate.py` runs in Actions |

The demo repo's README includes a direct link to the relevant section of the
presentation so participants can follow along without switching browser tabs.

---

## References

- Pannitto, L. & Mauri, C. (2025). Reuse by design: a pivot-based architecture for
  the KIParla corpus. *CLARIN*.
- Waldon, B. & Schneider, N. (2025). A GitHub-based workflow for annotated resource
  development. *LAW XIX*.
- de Marneffe et al. (2021). Universal Dependencies. *Computational Linguistics* 47(2).
- Steiner, I. (2017). A DevOps manifesto for speech corpus management. *ESSV*.
