# Hands-on: building the workflow

---

## What we will build today

Two repositories on GitHub:

```
git-spoken-corpus-demo/          git-spoken-corpus-slides/
├── .github/workflows/           ├── index.html
│   ├── validate.yml             ├── section1.md  …  section4.md
│   └── stats.yml                └── md2slides.py
├── annotations/
│   ├── BOA1010.stub.tsv   ← stub (pre-tokenized, no UPOS)
│   └── PSB054.stub.tsv    ← stub
├── scripts/
│   ├── validate.py
│   └── stats.py
├── guidelines/
│   └── ANNOTATION.md
├── .gitignore
└── README.md
```

By the end of the session you will have gone through a complete annotator→manager cycle on a real spoken Italian excerpt.

---

## Step 0: prerequisites

Before we start, make sure you have:

- A **GitHub account** (free — `github.com/signup`)
- **Git** installed locally (`git --version`)
- A text editor that shows TSV files cleanly (VS Code recommended)

**Alternative: no local setup needed.**
GitHub's web editor lets you edit and commit files directly from the browser. We will use this path as the primary route today.

```bash
# Optional: verify local git
git --version          # should print git version 2.x.x
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
```

---

## Step 1 (manager): fork and inspect the repo

1. Go to `github.com/your-username/git-spoken-corpus-demo`
2. Click **Fork** → creates your own copy
3. Explore the repository structure:
   - `annotations/` — stub TSV files with pre-tokenized spoken Italian
   - `scripts/validate.py` — the validation script
   - `.github/workflows/validate.yml` — the Action that fires on every push
   - `guidelines/ANNOTATION.md` — annotation guidelines

**Read a stub file.**
Open `annotations/BOA1010.stub.tsv`. You will see:

```
token_id  speaker  form    type        lemma  upos
1-1       PSB102   e       linguistic  _      _
1-2       PSB102   quindi  linguistic  _      _
1-3       PSB102   studi   linguistic  _      _
```

`lemma` and `upos` columns are `_` — your job is to fill them in.

---

## Step 2 (annotator): create a working branch

### From the browser (recommended)

1. On the repo page, click the branch dropdown (shows `main`)
2. Type `annotator/BOA1010` → click **Create branch**
3. You are now on your working branch — `main` is untouched

### From the command line

```bash
git clone https://github.com/your-username/git-spoken-corpus-demo
cd git-spoken-corpus-demo
git checkout -b annotator/BOA1010
```

---

## Step 3 (annotator): fill in the stub

Open `annotations/BOA1010.stub.tsv` in the editor and fill in `lemma` and `upos` for each token.

Use [Universal Dependencies UPOS tags](https://universaldependencies.org/u/pos/):

```
token_id  speaker  form    type        lemma   upos
1-1       PSB102   e       linguistic  e       CCONJ
1-2       PSB102   quindi  linguistic  quindi  ADV
1-3       PSB102   studi   linguistic  studiare VERB
1-4       PSB102   pittura linguistic  pittura  NOUN
```

**Tip:** check the guidelines in `guidelines/ANNOTATION.md` before annotating — especially the section on spoken-language specific cases (discourse markers, false starts, filled pauses).

---

## Step 4 (annotator): commit with a meaningful message

### From the browser

1. Scroll to **Commit changes** at the bottom of the editor
2. Write a descriptive commit message:

```
Add UPOS tags for BOA1010 (tokens 1-1 to 1-4)

Token 1-3 (studi): annotated as VERB (studiare), not NOUN.
The form is 2nd person singular present — context confirms
verbal reading (see turn PSB054 preceding).
```

3. Make sure **Commit directly to `annotator/BOA1010`** is selected
4. Click **Commit changes**

The GitHub Action fires immediately — check the **Actions** tab.

---

## Step 5: watch the Action run

After the commit, go to the **Actions** tab on GitHub.

You should see a workflow run called `Validate TSV`:

```
✓  Validate TSV
   Triggered by: push to annotator/BOA1010

   Jobs:
   ✓  validate (2s)
      → Running validate.py on annotations/BOA1010.stub.tsv
      → All 4 tokens: valid UPOS tags ✓
      → No missing lemmas ✓
      → Token IDs sequential ✓
```

If the Action **fails**, read the error output — it tells you exactly which row has the problem.

---

## Step 6 (annotator): open a pull request

1. Go to the repo page → click **Compare & pull request**
   (GitHub shows this banner automatically after a push)
2. Set:
   - **base:** `main`
   - **compare:** `annotator/BOA1010`
3. Write a PR description:

```
Annotate BOA1010 (4 tokens)

UPOS tags added for all tokens. One non-obvious case:
token 1-3 (studi) — annotated VERB not NOUN, see commit
message for reasoning. Please check against §3.2 of the
guidelines.

Checklist:
✓ Validation passed
✓ All lemmas filled
✓ Commit message explains each decision
```

4. Click **Create pull request**

---

## Step 7 (manager): review the pull request

As manager, open the PR. You will see:

- The **Files changed** tab — a diff of every modified line
- The **Checks** section — validation result from the Action
- The **Commits** tab — the full commit history with messages

**Leave a review comment** on a specific line:

> Token 1-2 (`quindi`): ADV is correct here, but note that
> in our corpus `quindi` often functions as a discourse
> connector rather than a pure adverb. See guideline §3.4.
> For now ADV is fine — worth flagging for future discussion.

This comment is **permanently recorded** in the PR thread.

---

## Step 8 (annotator): revise if needed

If the manager requests changes:

1. Go back to `annotations/BOA1010.stub.tsv` on your branch
2. Make the edit
3. Commit again — the Action re-runs automatically
4. Reply to the comment in the PR thread

```
# New commit message
Revise token 1-2: add discourse marker note in misc column

Following reviewer comment (§3.4): kept UPOS=ADV but added
Discourse=Yes in the MISC column to flag the pragmatic use.
```

The PR thread now has **two commits** and a resolved discussion — a complete adjudication record.

---

## Step 9 (manager): approve and merge

Once satisfied:

1. Click **Review changes** → **Approve**
2. Click **Merge pull request** → **Confirm merge**

The `stats` Action fires on merge:

```
✓  Update corpus statistics
   Tokens annotated:   4
   Total in corpus:    4  (0% remaining)
   UPOS distribution:  CCONJ=1  ADV=1  VERB=1  NOUN=1
   → stats/progress.json updated and committed to main
```

The `main` branch now has the approved annotation. Your branch can be deleted.

---

## Tour: what the repo looks like after one full cycle

```
main branch
├── annotations/
│   └── BOA1010.stub.tsv   ← now fully annotated (merged)
├── stats/
│   └── progress.json      ← updated by stats Action
└── (commit history)
    ├── a3f9c12  "Initial stub: BOA1010 (manager)"
    ├── 7b2e441  "Add UPOS tags for BOA1010 (tokens 1-1 to 1-4)"
    ├── 9d1f308  "Revise token 1-2: add discourse marker note"
    └── 4c8a017  "Merge pull request #1: Annotate BOA1010"
```

Every decision is traceable. The PR thread holds the reasoning. The Actions log proves the annotation was validated before merge.

---

## Exercise: annotate PSB054

Now try it yourself with the second stub file.

1. Create branch `annotator/PSB054`
2. Open `annotations/PSB054.stub.tsv`
3. Fill in `lemma` and `upos`
4. Commit with a descriptive message
5. Open a PR against `main`
6. Exchange with a neighbour: review each other's PR
7. Merge

**Discussion questions while you work:**

- Where did the validation Action catch an error?
- What would you add to the guidelines based on what you saw?
- How would you structure the repo for a 2M-token corpus with 10 annotators?

---

## Using the GitHub web editor: zero setup required

Everything we did is possible entirely from the browser:

| Action | How |
|---|---|
| Create a branch | Branch dropdown → type name → Enter |
| Edit a file | Click pencil icon on any file |
| Commit | Scroll to "Commit changes" at bottom of editor |
| Open a PR | "Compare & pull request" banner after push |
| Review a PR | Files changed tab → click `+` on any line |
| Merge | "Merge pull request" button |

No `git clone`, no terminal. Useful for linguists who are new to version control — they can start contributing immediately.

---

## The two repos: how they connect

```
git-spoken-corpus-slides/         git-spoken-corpus-demo/
  ← presentation source              ← live annotation workflow
  ← rendered via GitHub Pages        ← Actions, stubs, validation
  ← md2slides.py builds HTML         ← community can fork + annotate

Both repos link to each other in their README.
The slides explain the demo. The demo instantiates the slides.
```

**Publishing the slides:**

```bash
# In git-spoken-corpus-slides/
python3 md2slides.py          # regenerate index.html from all sections
git add index.html
git commit -m "Rebuild slides after section 4"
git push
# → GitHub Pages serves the updated presentation immediately
```

---

## Open questions and next steps

Things we did not cover — threads worth following:

- **Parallel annotation:** two annotators on the same file → branching model for disagreement → inter-annotator agreement computed from PR diffs
- **Integration with annotation tools:** GitHub Apps API lets ELAN or Inception commit directly to a branch without touching the command line
- **Incremental releases:** `git tag v1.0.0` + Zenodo webhook → automatic DOI on every tag
- **Scaling to speech:** combining Git (text layers) + Zenodo/CLARIN (audio) + GitHub Actions (conversion pipeline) into a single reproducible build

> "By embracing version control practices and technologies, we can foster more rigorous, collaborative, and sustainable approaches to linguistic annotation."
>
> — Waldon & Schneider (2025)

---

## Course summary

| Part | Core idea |
|---|---|
| 1 · Motivation | Spoken corpora are living, multilayer artefacts — current workflows are fragile |
| 2 · Git & GitHub | Five concepts: repo, commit, branch, PR, Action |
| 3 · Spoken data | Pivot format + GDPR + audio strategy = diff-friendly corpus |
| 4 · Hands-on | The full annotator → manager cycle on real spoken Italian data |

**The two repos:**
- `git-spoken-corpus-slides` — these slides, GitHub Pages
- `git-spoken-corpus-demo` — the toy corpus, try it anytime

---

## Thank you

Dr. Ludovica Pannitto
Alma Mater Studiorum — Università di Bologna
`ludovica.pannitto@unibo.it`

*KIParla corpus:* `www.kiparla.it`
*KIParla Forest:* Pannitto et al. (2025), DepLing/SyntaxFest
*GitHub workflow:* Waldon & Schneider (2025), LAW XIX

---

*References*

- Pannitto, L. & Mauri, C. (2025). Reuse by design. *CLARIN*.
- Pannitto et al. (2025). Introducing KIParla Forest. *DepLing / SyntaxFest*.
- Waldon, B. & Schneider, N. (2025). A GitHub-based workflow for annotated resource development. *LAW XIX*.
- Steiner, I. (2017). A DevOps manifesto for speech corpus management. *ESSV*.
- de Marneffe et al. (2021). Universal Dependencies. *Computational Linguistics* 47(2).
