# Hands-on: building the workflow

---

## What we will build today

A shared repository for a real excerpt from **BOD2018**, a KIParla recording. Three contributors work simultaneously on different representations of the same data:

```
git-bod2018-demo/
├── eaf/
│   └── BOD2018.eaf            ← Annotator A: ELAN transcription
├── pivot/
│   └── BOD2018.tsv            ← Annotator B: pivot TSV (prosody, overlaps)
├── conllu/
│   └── BOD2018.conllu         ← Annotator C: UD syntactic annotation
├── scripts/
│   ├── validate_tsv.py
│   └── eaf_to_pivot.py
├── .github/workflows/
│   └── validate.yml
└── README.md
```

The goal: merge all three contributions back into a consistent pivot.

---

## The data: BOD2018, TU 138–140

A short exchange between BO118 (interviewer) and BO140 (participant). TU 138 ends, TU 139 and 140 overlap.

**What you hear** (Jefferson notation):

```
BO140 (TU 138): ...zona irnerio così sono più sì anni cinquanta credo.
BO118 (TU 139): [sì] (.) penso di sì.
BO140 (TU 140): [non lo so].
```

`[…]` marks overlap onset/offset. `(.)` is a short pause.

**Three representations of the same three TUs** — each maintained by a different contributor, each seeing only part of the picture.

---

## The three files side by side

**Pivot TSV** (Annotator B):

```
token_id  speaker  tu_id  form    lemma    type        prosody           align          overlaps
139-0     BO118    139    [sì]    sì       linguistic  _                 Begin=539.63   0-2(23)
139-1     BO118    139    (.)     [PAUSE]  shortpause  _                 _              _
139-2     BO118    139    penso   penso    linguistic  _                 _              _
139-3     BO118    139    di      di       linguistic  _                 _              _
139-4     BO118    139    sì.     sì       linguistic  Intonation=Fall   End=540.78     _
140-0     BO140    140    [non    non      linguistic  _                 Begin=539.63   0-3(23)
140-1     BO140    140    lo      lo       linguistic  _                 _              0-2(23)
140-2     BO140    140    so].    so       linguistic  Intonation=Fall   End=540.26     0-2(23)
```

**CoNLL-U** (Annotator C):

```
# sent_id = BOD2018_140
# text = sì penso di sì
# jefferson_text = [sì] (.) penso di sì.
# speaker_id = BO118
1  sì     sì       ADV   _  _                       2  discourse  _  Begin=539.63|PauseAfter=Yes
2  penso  pensare  VERB  _  Mood=Ind|Person=1|...   0  root       _  _
3  di     di       ADP   _  _                       4  case       _  _
4  sì     sì       ADV   _  _                       2  advmod     _  End=540.78|Intonation=Falling
```

---

## The divergence: the pause that disappeared

The pause `(.)` in TU 139 is a **first-class token** in the pivot:

```
139-1  BO118  139  (.)  [PAUSE]  shortpause  _  _  _
```

In the CoNLL-U it is **not a token** — it is encoded as a feature on the preceding word:

```
1  sì  sì  ADV  _  _  2  discourse  _  Begin=539.63|PauseAfter=Yes
```

This is a principled decision: UD trees require every node to be a syntactically analysable unit, and pauses are not. But it means the two files are **not directly comparable line by line**.

When Annotator B and Annotator C open a PR, the manager must:
1. Verify that `PauseAfter=Yes` on token 1 correctly reflects `139-1` in the TSV
2. Ensure no information was lost in the conversion
3. Record the decision in the merge commit message

Git makes this traceable. Without it, the divergence would be invisible.

---

## The pivot TSV format: columns 1–6

Each token is one row. The 12 columns are:

| # | Column | Description |
|---|--------|-------------|
| 1 | `token_id` | Unique token identifier within the conversation — format `TU_ID-TOKEN_INDEX` |
| 2 | `speaker` | Speaker code (e.g. `BO118`) — matches `metadata/participants.tsv` |
| 3 | `tu_id` | Progressive identifier of the Transcription Unit |
| 4 | `span` | Original Jefferson transcription of the token, including all diacritics |
| 5 | `form` | Orthographic form — special symbols stripped; `(.)` → `[PAUSE]`; unintelligible → `x` |
| 6 | `type` | `linguistic` · `shortpause` · `nonverbalbehavior` · `unknown` · `error` |

Tokenization splits on whitespace, prosodic links (`=`), and Italian elision apostrophes.

---

## The pivot TSV format: columns 7–12

| # | Column | Description |
|---|--------|-------------|
| 7 | `jefferson_feats` | `SpaceAfter=No` · `ProsodicLink=Yes` · `Intonation=Falling/Rising/WeaklyRising` · `Interrupted=Yes` · `Truncated=Yes` · `Volume=High/Low` |
| 8 | `align` | `Begin=X.XXX` and/or `End=X.XXX` in seconds — only on first/last token of TU |
| 9 | `prolongations` | Colons encoded as `<char_idx>x<count>` — e.g. `ese::mpio:` → `2x2,6x1` |
| 10 | `pace` | `Fast=START-END` or `Slow=START-END` (zero-based char indices over `form`) |
| 11 | `guesses` | Uncertain spans from round brackets — `START-END` over `form` |
| 12 | `overlaps` | Simultaneous speech — `START-END(GROUP_ID)` — char indices over `form` |

*Pannitto & Mauri (2025) · KIParla tools: github.com/LaboratorioSperimentale/kiparla-tools*

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

1. Go to the shared `git-bod2018-demo` repository
2. Click **Fork** → creates your own copy
3. Explore the structure:
   - `pivot/BOD2018.tsv` — the authoritative TSV (TU 138–140, partially annotated)
   - `conllu/BOD2018.conllu` — the UD annotation (sent_id BOD2018_140 has gaps)
   - `eaf/BOD2018.eaf` — the ELAN source (alignment timestamps to verify)
   - `scripts/validate_tsv.py` — checks schema, delimiter balance, TU coherence

**Assign roles** (one per group of three):
- **Annotator A** → works on `eaf/BOD2018.eaf`: verify and correct alignment timestamps
- **Annotator B** → works on `pivot/BOD2018.tsv`: add missing prosodic features
- **Annotator C** → works on `conllu/BOD2018.conllu`: complete the UD annotation for TU 138

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

## Step 3 (annotator): make your edit

Each annotator works on their assigned file:

**Annotator A** — `eaf/BOD2018.eaf`: check that `Begin=539.63` on TU 139 and `Begin=539.63` on TU 140 are both present and consistent with the overlap marker `0-2(23)` / `0-3(23)` in the TSV.

**Annotator B** — `pivot/BOD2018.tsv`: the `prosody` column on tokens `138-6` (`da::`) and `138-17` (`più::`) is `_` but prolongations are visible. Add the correct values:

```
138-6   BO140  138  da::    da    linguistic  _  _  1x2  _  _  _
```

→ change `_` in the prolongations column to `1x2`.

**Annotator C** — `conllu/BOD2018.conllu`: `sent_id = BOD2018_138_139` is missing the deprel for token 19 (`sì`). It should be `discourse`, head `20`. Add it.

**Important for all:** the pause token `139-1 (.) [PAUSE] shortpause` is in the TSV. Do not add it to the CoNLL-U — record it via `PauseAfter=Yes` on token 1 of `BOD2018_140` instead. This is the expected format divergence.

---

## Step 4 (annotator): commit with a meaningful message

Write a message that documents the decision, not just the change:

**Annotator B example:**
```
Add prolongation features to TU 138 tokens 138-6 and 138-17

138-6 (da::): 1 prolonged syllable, 2 extra.
138-17 (più::): 2 prolonged syllables, 2 extra each.
Values follow KIParla prolongation encoding (NxM = N syllables, M extra).
```

**Annotator C example:**
```
Fix missing deprel for token 19 (sì) in BOD2018_138_139

Was: _ (empty). Should be: discourse, head=20 (anni).
Consistent with treatment of discourse sì in BOD2018_2 and BOD2018_6_7_9_10.
Note: pause (139-1) is not tokenised here — encoded as PauseAfter=Yes on
BOD2018_140 token 1 per KIParla Forest convention.
```

The GitHub Action fires immediately after commit — check the **Actions** tab.

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

## Step 7 (manager): review all three pull requests

Open each PR in turn. For each, check:

- **Files changed** — is the diff minimal and correct?
- **Checks** — did `validate_tsv.py` pass?
- **Commit message** — does it explain the decision?

**The key review moment: the pause divergence.**

When reviewing Annotator C's PR, open `conllu/BOD2018.conllu` and check that `PauseAfter=Yes` appears on `BOD2018_140` token 1. Then open `pivot/BOD2018.tsv` and verify that `139-1` is still there as a `shortpause` token.

Leave a comment on the CoNLL-U line:

> `PauseAfter=Yes` on token 1 (`sì`, KID=139-0) correctly captures
> the pause at TSV token 139-1. The TSV retains the explicit token
> for query and interactional analysis; the CoNLL-U encodes it as
> a feature for syntactic compatibility. Both are correct — the
> formats serve different purposes.

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

## Tour: what the repo looks like after the three merges

```
main branch
├── eaf/BOD2018.eaf          ← A's alignment corrections
├── pivot/BOD2018.tsv        ← B's prolongation features; pause 139-1 intact
├── conllu/BOD2018.conllu    ← C's deprel fix; PauseAfter=Yes on BOD2018_140:1
└── (commit history)
    ├── a3f9c12  "Initial BOD2018 stubs (TU 138–140)"
    ├── 7b2e441  "Verify alignment for TU 139/140 overlap"       ← A
    ├── 9d1f308  "Add prolongation features TU 138 tokens 6, 17" ← B
    ├── 4c8a017  "Fix deprel token 19 in BOD2018_138_139"        ← C
    ├── e2f1c08  "Merge PR #1: alignment (A)"
    ├── f3a9d14  "Merge PR #2: prolongations (B)"
    └── 1b7e305  "Merge PR #3: deprel fix (C)"
```

Three people, three formats, three branches — one consistent, documented, validated corpus state on `main`.

The pause is still in the TSV. The CoNLL-U knows about it via `PauseAfter=Yes`. Both are correct. The PR thread explains why.

---

## Exercise: extend the scenario to TU 141–145

Now continue the annotation on a fresh excerpt.

1. Each group takes a role (A/B/C) for TU 141–145 of BOD2018
2. Create a branch: `annotator-a/tu141`, `annotator-b/tu141`, `annotator-c/tu141`
3. Make your edits to your assigned file
4. Commit with a message that explains each decision
5. Open a PR against `main`
6. Exchange PRs with another group: review their work
7. The manager merges in order: EAF → TSV → CoNLL-U

**Discussion questions while you work:**

- Is there another pause or non-linguistic token in TU 141–145? How is it handled in each format?
- What happens if Annotator B and Annotator C make incompatible decisions about the same token?
- How would the merge process differ if there were 100 annotators working on 2M tokens?

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

## Open questions and next steps

Things we did not cover — threads worth following:

- **Parallel annotation:** two annotators on the same file → branching model for disagreement → inter-annotator agreement computed from PR diffs
- **Integration with annotation tools:**
- **Incremental releases:** `git tag v1.0.0` + Zenodo webhook → automatic DOI on every tag

> "By embracing version control practices and technologies, we can foster more rigorous, collaborative, and sustainable approaches to linguistic annotation."
>
> — Waldon & Schneider (2025)

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
