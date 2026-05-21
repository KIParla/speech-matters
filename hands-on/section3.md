# The KIParla pivot format

---

## Requirements for a Git-friendly pivot format

A format suited to version control in Git must be:

- **Line-oriented** — each line is an atomic unit; diffs are human-readable
- **Tab-separated plain text** — no proprietary tool required to open it
- **One token per line** — one annotation change = one line changed
- **Self-documenting** — column headers describe each layer
- **Column-extensible** — new layers are added without modifying existing data
- **Invertible** — the original representation can be reconstructed from the pivot

> "The format is intentionally designed to support incremental correction and version-controlled maintenance: revisions are localised at the level of token identifiers and propagate deterministically to all derived formats."
>
> — Pannitto & Mauri (2025)

---

## The KIParla pivot format: vertical structure

One token per line. Each column is an annotation layer.

```
token_id  speaker  tu_id  form      lemma     type        prosody          align            overlap
175-0     PKP019   175    eh        eh        linguistic  none             Begin=265.732    _
175-1     PKP019   175    (.)       [PAUSE]   shortpause  none             _                _
175-2     PKP019   175    se        se        linguistic  none             _                _
175-8     PKP019   175    [c~]      c~        linguistic  Interrupted=Yes  _                0-2(41)
175-12    PKP019   175    casotto   casotto   linguistic  none             End=268.952      _
176-0     PKP014   176    [sì       sì        linguistic  none             Begin=267.392    0-2(41)
176-2     PKP014   176    sì]       sì        linguistic  none             End=268.162      0-2(41)
177-0     PKP020   177    >fa       fa        linguistic  none             Begin=268.977    _
177-1     PKP020   177    vedere<   vedere    linguistic  none             End=269.497      _
```

The overlap between TU 175 and TU 176 is encoded via the shared span reference `0-2(41)`. A diff on this file is immediately readable by a linguist.

---

## Why the vertical TSV is diff-friendly

```diff
# Commit: "fix interrupted token 175-8: lemma should preserve tilde"

-175-8  PKP019  175  [c~]  c~   linguistic  Interrupted=Yes  _  0-2(41)
+175-8  PKP019  175  [c~]  c~:  linguistic  Interrupted=Yes  _  0-2(41)
```

- The change affects **exactly one line**
- The reviewer sees **what changed and why** (in the commit message)
- The file history shows **every annotation decision over time**
- The same mechanism works for adding a new layer (new column)

Compare with a `.eaf` XML file: even a small change produces hundreds of unreadable diff lines.

---

## A three-level architecture

The KIParla pivot formalises three explicit levels:

```
Level 1: TU (Transcription Unit)
  └── speaker-attributed segment, temporally anchored
        validation: coherent interval (end > start), non-empty content

Level 2: Span
  └── Jefferson phenomenon extending across a text sequence
        [overlap], °quiet voice°, >fast speech<
        validation: balanced delimiters, anchored to existing tokens

Level 3: Token
  └── lexical or para-verbal unit, locally well-formed
        validation: character inventory, categorical type, prosodic features
```

Each level has **explicit validation criteria** → a GitHub Action can check them automatically on every commit.

---

## Column extensibility: adding a layer without breaking anything

The columnar format allows new annotation layers to be added without modifying the existing structure.

**Example: adding UD syntactic annotation**

Syntactic tokens that require expansion (multiword) are inserted with extended IDs (`254-1a`, `254-1b`) and marked as type `syntactic`. Two additional columns (`lemma`, `upos`) store the UD annotations.

```
# Before: transcription only
token_id  speaker  form    type        jefferson_feats

254-1     PSB102   quindi  linguistic  _

# After: UD layer added as columns
token_id  speaker  form    type        jefferson_feats  lemma   upos
254-1     PSB102   quindi  linguistic  _                quindi  ADV
```

→ Backward compatible: anyone not using the new columns simply ignores them.

---

## The pivot columns: transcription and token structure

| # | Column | Description |
|---|--------|-------------|
| 1 | `token_id` | Unique identifier within the conversation — format `TU_ID-TOKEN_INDEX` |
| 2 | `speaker` | Speaker code (e.g. `BO118`) — matches `metadata/speakers.tsv` |
| 3 | `tu_id` | Progressive identifier of the Transcription Unit |
| 4 | `form` | Jefferson transcription of the token, including all diacritics |
| 5 | `lemma` | Orthographic form — special symbols stripped; `(.)` → `[PAUSE]` |
| 6 | `type` | `linguistic` · `shortpause` · `nonverbalbehavior` · `unknown` · `error` |
| 7 | `jefferson_feats` | `Intonation=` · `Interrupted=Yes` · `Truncated=Yes` · `Volume=` · `SpaceAfter=No` |
| 8 | `align` | `Begin=X.XXX` / `End=X.XXX` in seconds — first/last token of TU only |
| 9 | `prolongations` | Colons encoded as `<char_idx>x<count>` — e.g. `ese::mpio:` → `2x2,6x1` |
| 10 | `pace` | `Fast=START-END` or `Slow=START-END` (char indices over `form`) |
| 11 | `guesses` | Uncertain spans from round brackets — `START-END` over `form` |
| 12 | `overlaps` | Simultaneous speech — `START-END(GROUP_ID)` — char indices over `form` |

*Pannitto & Mauri (2025)*

---

## The divergence: a pause that disappears

The pause `(.)` in TU 139 is a **first-class token** in the pivot:

```
139-1  BO118  139  (.)  [PAUSE]  shortpause  _  _  _  _  _  _
```

In the CoNLL-U it is **not a token** — UD trees require syntactically analysable nodes, and pauses are not. Instead it is encoded as a feature on the adjacent word:

```
1  sì  sì  ADV  _  _  2  discourse  _  Begin=539.63|PauseAfter=Yes
```

This is a principled decision, not an error. But it means the two files are **not directly comparable line by line**. A reviewer checking consistency must know the mapping rule: `shortpause` token in TSV → `PauseAfter=Yes` on the preceding token in CoNLL-U.

At scale — thousands of TUs, multiple pause types, overlapping spans — **this mapping cannot be done by eye**.

---

## Conversion scripts are not optional

The pivot-to-derived format mappings encode decisions about how phenomena are represented in each target format. Those decisions need to be:

- **Explicit** — written down as code, not tribal knowledge
- **Reproducible** — running the script twice on the same input gives the same output
- **Versioned** — the script lives in the repo alongside the data it transforms

```
scripts/
├── eaf_to_pivot.py       # EAF → pivot (timestamps, overlap markers)
├── pivot_to_conllu.py    # pivot → CoNLL-U (pause folding, multiword expansion)
├── pivot_to_vert.py      # pivot → NoSketchEngine vertical
└── validate_tsv.py       # format correctness checks
```

When a correction is made to the pivot, re-running `pivot_to_conllu.py` rebuilds the CoNLL-U with the fix applied — **consistently, automatically, and with no manual patching**. The script is the specification. The Git history of the script is the history of those decisions.

---

## From EAF to pivot: the curation workflow

```
ELAN (.eaf)
    │
    ▼  validation pipeline (Python)
    │   ├── TU validation (temporal coherence)
    │   ├── Span validation (delimiter balancing)
    │   └── Token validation (character inventory, types)
    │
    ▼  pivot format (.tsv)          ← maintained in Git
    │
    ├──► CoNLL-U (.conllu)          ← reproducible derived format
    ├──► re-exported ELAN (.eaf)    ← reproducible derived format
    ├──► NoSketchEngine (.vert)     ← reproducible derived format
    └──► KIParla Forest (treebank)  ← reproducible derived format
```

Derived formats are *regenerated* from the pivot — not maintained separately.

---

## The linguist still works in ELAN

The pivot architecture does not require linguists to abandon their tools.
**ELAN remains the annotation interface** — the pivot is the *storage and versioning* format.

The conversion from EAF to pivot can happen at two points:

```
LINGUIST'S LAPTOP                     SHARED REPOSITORY (GitHub)
─────────────────────────────────     ──────────────────────────────────
Works in ELAN as usual
Saves .eaf locally

Option A — local conversion:
  runs eaf_to_pivot.py
  reviews pivot diff
  git add + git commit + git push  →  pivot arrives already validated

Option B — push and let Actions run:
  git add + git commit + git push  →  Action: eaf_to_pivot.py
                                       Action: validate pivot
                                       Action: commit pivot to repo
```

Both paths produce the same outcome: **the pivot in the shared repo is always the authoritative, validated version**.
Linguists who are comfortable with the command line can run the conversion locally and review the diff before pushing; those who are not can push the EAF and let the Action handle it.

The EAF files can be kept in the repo too — in `eaf/` — for reference and reproducibility, but they are **not** what Git is tracking for annotation changes.

---

## The value of history tracking

With Git, the corpus history is itself a research artefact.

```bash
# Who touched the pivot TSV and when?
git log --oneline -- pivot/BOD2018.tsv
# 18b5167 fix two errors in pivot TSV
# 357d17b Initial commit: BOD2018 exercise stubs (TU 138–145)

# What exactly changed in the last commit to that file?
git show 18b5167 -- pivot/BOD2018.tsv

# When was the POS for 'si' corrected — and why?
git log -S "INTJ" --oneline -- conllu/BOD2018.conllu
# 5c78119 fix POS for si and quindi per KIParla spoken Italian guidelines

```

Any annotation decision is recoverable: who made it, when, and why.

---

## Documentation grounded in the data

A persistent problem in corpus linguistics: documentation claims drift from the actual data.

> "Overlap is encoded with square brackets" — but is it, in every file, in every version?

With Git, documentation can be **derived from and verified against** the history:

```bash
# Auto-generate a dated changelog from commit messages
git log --format="%ad  %s" --date=short -- pivot/
# 2026-05-21  fix two errors in pivot TSV
# 2026-05-21  remove Clitic=Yes from CoNLL-U misc fields
# 2026-05-21  add speaker and conversation metadata for BOD2018
# 2026-05-21  Initial commit: BOD2018 exercise stubs (TU 138–145)

# Who contributed what — for an Acknowledgements section
git shortlog -sn
#     12  Maria Rossi
#      7  Giulio Bianchi
#      3  ellepannitto

# Trace every line of a file back to the commit that introduced it
git blame pivot/BOD2018.tsv
```

A release's README does not need to say "we fixed X in version 1.1" as a free-text claim — it can link to the commit that proves it.

→ The changelog **is** the commit log. The attribution **is** the author list.
Documentation that cannot be falsified by `git log` is not documentation.

---

## Versions and releases: corpora as software

Git supports an explicit release model with *tags*:

```bash
# Create a version
git tag -a v1.1.0 -m "Add ParlaBO module; fix overlap encoding in KIP"
git push origin v1.1.0
```

On GitHub, a tag automatically creates a **Release** with:

- A changelog generated from commits
- A downloadable archive (`.zip`, `.tar.gz`) of the corpus at that version
- A link to Zenodo for a permanent DOI

→ Every corpus version is **citable**, **reproducible**, and **comparable** with previous ones.

## Open questions and next steps

Things we did not cover — threads worth following:

- **Parallel annotation:** two annotators on the same file → branching model for disagreement → inter-annotator agreement computed from PR diffs
- **Integration with annotation tools:**
- **Incremental releases:** `git tag v1.0.0` + Zenodo webhook → automatic DOI on every tag

> "By embracing version control practices and technologies, we can foster more rigorous, collaborative, and sustainable approaches to linguistic annotation."
>
> — Waldon & Schneider (2025)

---

*References*

- [Chrupała, G. (2023). Putting natural in natural language processing. *ACL Findings*.](https://aclanthology.org/2023.findings-acl.495/)
- [de Marneffe et al. (2021). Universal Dependencies. *Computational Linguistics* 47(2).](https://direct.mit.edu/coli/article/47/2/255/98516/Universal-Dependencies)
- [Dobrovoljc, K. (2022). Spoken language treebanks in Universal Dependencies. *LREC*.](https://aclanthology.org/2022.lrec-1.191.pdf)
- [Dumitru et al. (2024). Version control for speech corpora. *KONVENS*.](https://aclanthology.org/2024.konvens-main.30/)
- [Lehmann, C. (2004). Data in linguistics. *The Linguistic Review*.](https://www.degruyterbrill.com/document/doi/10.1515/tlir.2004.21.3-4.175/html)
- [Linell, P. (2019). The written language bias 40 years after. *Language Sciences*.](https://www.sciencedirect.com/science/article/abs/pii/S0388000118303875)
- [Mauri et al. (2019). KIParla corpus: a new resource for spoken Italian. *CLiC-it*.](https://aclanthology.org/2019.clicit-1.37/)
- [Palmer, M. & Xue, N. (2010). Linguistic annotation. Chapter 10.](https://onlinelibrary.wiley.com/doi/10.1002/9781444324044.ch10)
- Pannitto, L. & Mauri, C. (2025). Reuse by design: a pivot-based architecture for the KIParla corpus. *forthcoming*.
- [Pannitto et al. (2025). Introducing KIParla Forest. *DepLing / SyntaxFest*.](https://aclanthology.org/2025.depling-1.5/)
- [Rosenberg, A. (2012). Rethinking the corpus: moving towards dynamic linguistic resources. *Interspeech*.](https://www.researchgate.net/publication/268254153_Rethinking_The_Corpus_Moving_towards_Dynamic_Linguistic_Resources)
- [San, N. (2016). Using version control for a reproducible workflow in acoustic phonetics. *SST2016*.](https://discovery.ucl.ac.uk/id/eprint/10152457/1/SST2016_Proceedings.pdf#page=356)
- [Software Carpentry (2024). *Version Control with Git*. The Carpentries.](https://swcarpentry.github.io/git-novice/)
- [Steiner, I. (2017). A DevOps manifesto for speech corpus management. *ESSV*.](https://www.coli.uni-saarland.de/~steiner/publications/ESSV2017c.pdf)
- [Waldon, B. & Schneider, N. (2025). A GitHub-based workflow for annotated resource development. *LAW XIX*.](https://aclanthology.org/2025.law-1.27.pdf)
- [Zeman, D., Savary, A. & Guillaume, B. (2024). Git Infrastructure. *UniDive Training School*, Chișinău.](https://unidive.lisn.upsaclay.fr/lib/exe/fetch.php?media=meetings:other-events:1st-training-school:unidive_chisinau_3_1_git.pdf)
