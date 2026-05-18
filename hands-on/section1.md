# Git as a Collaborative Environment for Multilayer Spoken Resource Development

**Summer School Lab · Part 1 of 4**
Dr. Ludovica Pannitto — Università di Bologna

---

## Why spoken corpora are hard to manage collaboratively

> "Nothing is, in and of itself, a datum; instead, it is a datum for somebody in some perspective."
>
> — Lehmann (2004), *Data in linguistics*

---

## Human language is first and foremost spoken

- Spoken interaction is **structurally underrepresented** in language resources
- Growing interest in NLP in modelling language *in interaction* — beyond speech
- Interactional phenomena (overlaps, repairs, backchannels, disfluencies) are often treated as marginal or excluded from downstream formats

*Chrupała (2023) · Dobrovoljc (2022) · Linell (2019)*

---

## The multilayer problem

A spoken corpus is not a text. It is a **stratification of interpretive layers**:

```
raw audio
  └── pseudonymized audio          [GDPR pipeline]
        └── Jefferson transcription [ELAN / expert linguist]
              └── orthographic form  [normalization scripts]
                    └── morphosyntax  [POS tagger + manual revision]
                          └── syntax   [UD treebank annotation]
                                └── metadata
```

Each layer: different person · different tool · different time

---

## KIParla: a running example

A large (~2M token) corpus of spontaneous spoken Italian

- Started in **2016**, collaboration between University of Bologna and University of Turin
- Built around **modularity**: new modules added with compatible metadata and transcription conventions
- Data collection → archiving → transcription (Jefferson conventions in ELAN) → revision by a single expert linguist → pseudonymization → release

*Mauri et al. (2019) · Pannitto et al. (2025)*

---

## The current pipeline

```
fieldwork (many people)
    ↓
ELAN transcription  (.eaf XML)
    ↓
expert revision + pseudonymization  (one person)
    ↓
linearized exports  (Jefferson .txt, orthographic .txt, NoSketchEngine .vert)
```

**Problem**: the pipeline is a *one-way street*

---

## What an .eaf file looks like

```xml
<ANNOTATION>
  <ALIGNABLE_ANNOTATION ANNOTATION_ID="a42"
    TIME_SLOT1="ts103" TIME_SLOT2="ts104">
    <ANNOTATION_VALUE>
      e quindi stu[di: pittura?
    </ANNOTATION_VALUE>
  </ALIGNABLE_ANNOTATION>
</ANNOTATION>
```

- Textual XML — readable only through ELAN
- No clear unit descriptions
- Additional annotation layers are **external or tool-dependent**
- Difficult to process at scale with standard NLP pipelines

---

## What goes wrong without version control

| Problem | Consequence |
|---|---|
| Opaque pipeline | Cannot retrace annotation decisions |
| Non-reversible edits | Ad-hoc choices crystallize permanently |
| Single expert bottleneck | Knowledge locked in one person |
| No adjudication trail | Inter-annotator disagreement invisible |
| Static releases | Errors cannot be corrected incrementally |

---

## The standard of practice landscape

Spoken language research is characterised **not by a lack of standards, but by the coexistence of partially incompatible ones**, each optimised for a specific stage of the data lifecycle.

| Format | Strength | Limitation |
|---|---|---|
| ELAN / .eaf | Time alignment, interactional detail | Tool-dependent, hard to diff |
| CHAT | Transcription conventions | Not designed for large-scale annotation |
| TEI-ISO 24624 | Exchange and preservation | Rarely used as working format |
| CoNLL-U | NLP pipelines, UD treebanks | Loses interactional structure |

---

## FAIR data vs FAIR processes

> "Interoperability is not achieved through adherence to formats and standards, but through the **alignment of curatorial practices**."
>
> — Pannitto & Mauri (2025)

- **FAIR** principles (Findable, Accessible, Interoperable, Reusable) are usually applied to *data products*
- But for living corpora, what matters is whether the **process** is FAIR
- A static release can be FAIR; an evolving corpus needs FAIR *workflows*

---

## Corpora as living artefacts

> "Dataset curation increasingly resembles a form of **continuous development**, rather than a linear production pipeline culminating in a static release."
>
> — Pannitto & Mauri (2025)

New data are added · Errors are corrected · Formats evolve · New reuse scenarios emerge

→ This requires **versioning**, **traceability**, and **reversibility** built into the workflow itself

---

## The DevOps analogy

| Software development | Corpus development |
|---|---|
| Codebase | Annotated corpus |
| Feature branch | Annotator's working copy |
| Code review | Annotation adjudication |
| CI/CD pipeline | Validation + format conversion scripts |
| Release tag | Corpus version (e.g. v1.1.0) |
| Issue tracker | Annotation guideline discussion |

*Steiner (2017) — "A DevOps manifesto for speech corpus management"*

---

## What we want

A workflow that is:

- **Transparent** — full record of every annotation decision
- **Efficient** — automated validation and conversion
- **Consistent** — schema enforcement before merge
- **Participatory** — open to community contributions and corrections
- **Reversible** — any change can be traced and undone

→ This is exactly what **Git** and **GitHub** were built for

---

## Part 1 — Summary

- Spoken corpora are multilayer, multi-person, multi-tool artefacts
- Current pipelines are opaque, hard to scale, and difficult to revise
- The challenge is not data formats — it is *curatorial practices*
- We need DevOps-inspired workflows: continuous development, version control, peer review
- **Part 2** will introduce Git and GitHub, and map each concept to corpus work

---

*References*

- Chrupała, G. (2023). Putting natural in natural language processing. *ACL Findings*.
- Dobrovoljc, K. (2022). Spoken language treebanks in Universal Dependencies. *LREC*.
- Lehmann, C. (2004). Data in linguistics. *The Linguistic Review*.
- Linell, P. (2019). The written language bias 40 years after. *Language Sciences*.
- Mauri et al. (2019). KIParla corpus: a new resource for spoken Italian. *CLiC-it*.
- Pannitto, L. & Mauri, C. (2025). Reuse by design: a pivot-based architecture for the KIParla corpus. *CLARIN*.
- Pannitto et al. (2025). Introducing KIParla forest. *DepLing / SyntaxFest*.
- Steiner, I. (2017). A DevOps manifesto for speech corpus management. *ESSV*.
