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
# In the my-corpus repo you created in the exercises:

# Who touched pivot/BOA1010.tsv and when?
git log --oneline -- pivot/BOA1010.tsv

# What exactly changed in the last commit to that file?
git show HEAD -- pivot/BOA1010.tsv

# How did the file look before your latest edit?
git show HEAD~1:pivot/BOA1010.tsv

# What is different between your branch and main?
git diff main..annotator/BOA1010 -- pivot/BOA1010.tsv
```

→ The commit history **is** the documentation of curatorial decisions. It replaces — and surpasses — manual changelogs.

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

---

*References*

- Pannitto, L. & Mauri, C. (2025). Reuse by design: a pivot-based architecture for the KIParla corpus. *CLARIN*.
- Pannitto et al. (2025). Introducing KIParla Forest. *DepLing / SyntaxFest*.
- Steiner, I. (2017). A DevOps manifesto for speech corpus management. *ESSV*.
- Rosenberg, A. (2012). Rethinking the corpus: moving towards dynamic linguistic resources. *Interspeech*.
- Dumitru et al. (2024). Version control for speech corpora. *KONVENS*.
- Waldon, B. & Schneider, N. (2025). A GitHub-based workflow for annotated resource development. *LAW XIX*.
