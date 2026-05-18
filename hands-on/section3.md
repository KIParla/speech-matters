# Git e i corpora parlati: il caso specifico

**Summer School Lab · Part 3 of 4**
Dr. Ludovica Pannitto — Università di Bologna

---

## Da Part 2 a Part 3

In Part 2 abbiamo visto come Git e GitHub funzionano in astratto.

**Part 3** affronta il problema concreto: applicare queste pratiche a corpora del parlato, che pongono sfide specifiche che i treebank di testo scritto non hanno.

- File audio binari e di grandi dimensioni
- Vincoli GDPR sulla diffusione dei dati
- Formati parzialmente incompatibili tra strumenti diversi
- Annotazioni stratificate che non possono essere separate

La soluzione è progettare il formato dei dati affinché sia *diff-friendly* fin dall'inizio.

---

## Il problema dei file audio in Git

Git è ottimizzato per file di testo a righe brevi. I file audio sono:

- **Binari** — nessun diff leggibile è possibile
- **Grandi** — decine o centinaia di MB per conversazione
- **Quasi immutabili** — registrati una volta, raramente modificati

> "Speech data is (a) inefficient to store and transfer with SCM operations, and (b) meaningless to compare at the binary level."
>
> — Steiner (2017)

→ I file audio **non vanno tracciati in Git** direttamente

---

## Strategie per i file audio

| Approccio | Come funziona | Quando usarlo |
|---|---|---|
| **Git LFS** | Puntatori in repo, file in storage separato | Audio accessibili via GitHub |
| **git-annex** | Traccia hash, recupera da remoti multipli | Archivi distribuiti |
| **Storage esterno** | Audio su server/CLARIN, URL in metadata | Corpus già depositato |
| **Esclusione da `.gitignore`** | Audio non tracciati, solo testo in repo | Sviluppo locale |

**Raccomandazione pratica per corpora linguistici:**

```
# .gitignore
audio/raw/
audio/pseudonymized/
*.wav
*.flac
*.mp4
```

Il repo traccia gli *script di pseudonimizzazione* e la *documentazione del processo*, non i file audio stessi.

---

## GDPR: cosa può stare in un repo pubblico

I dati del parlato spontaneo contengono informazioni personali identificabili (PII).

```
audio/raw/BOA1010.wav          ← MAI in repo pubblico
audio/pseudonymized/BOA1010.wav ← accesso controllato
transcriptions/BOA1010.eaf     ← richiede revisione
pivot/BOA1010.tsv              ← richiede pseudonimizzazione
metadata/speakers.tsv          ← NO nomi, solo codici
```

**Cosa può stare nel repo pubblico:**
- Trascrizioni *dopo* pseudonimizzazione completa
- Script del pipeline di pseudonimizzazione
- Metadati anonimi (codici parlante, durata, tipo di testo)
- Schemi di annotazione, linee guida, documentazione
- GitHub Actions per validazione e conversione

**Repo privato → repo pubblico** è il modello di rilascio: si lavora in privato, si pubblica la versione pseudonimizzata.

---

## Il layering problem e la necessità di un pivot

I formati esistenti sono ottimizzati per fasi diverse del ciclo di vita:

```
ELAN / .eaf      → allineamento temporale, analisi interazionale
                   ma: XML monolitico, difficile da diff
CHAT             → convenzioni di trascrizione
                   ma: non progettato per annotazione NLP su larga scala
TEI-ISO 24624    → scambio e preservazione
                   ma: raramente usato come formato operativo
CoNLL-U          → pipeline NLP, treebank UD
                   ma: perde struttura interazionale
```

Nessuno di questi formati è adatto come **rappresentazione di lavoro mantenuta in Git**.

→ Serve un *pivot format* che soddisfi contemporaneamente tutti i requisiti

---

## Requisiti di un formato pivot per Git

Un formato adatto a essere versioned in Git deve essere:

- **Line-oriented** — ogni riga è un'unità atomica, i diff sono leggibili
- **Tab-separated plain text** — nessun tool proprietario per aprirlo
- **Un token per riga** — una modifica di annotazione = una riga cambiata
- **Auto-documentante** — le intestazioni descrivono ogni colonna
- **Estensibile per colonne** — nuovi layer si aggiungono senza modificare l'esistente
- **Invertibile** — dalla rappresentazione pivot si può ricostruire l'originale

> "The format is intentionally designed to support incremental correction and version-controlled maintenance: revisions are localised at the level of token identifiers and propagate deterministically to all derived formats."
>
> — Pannitto & Mauri (2025)

---

## Il formato pivot di KIParla: struttura verticale

Un token per riga. Ogni colonna è un layer di annotazione.

```
token_id  speaker  tu_id  span          form      type        jefferson_feats       align              lemma    upos
1-1       PSB102   1      ah            ah        linguistic                        AlignBegin=5.12    ah       INTJ
1-2       PSB102   1      no            no        linguistic                        _                  no       ADV
1-3       PSB102   1      no:           no        linguistic  Intonation=Rising     _                  no       ADV
1-4       PSB102   1      [no]          no        linguistic  _                     AlignEnd=6.08      no       ADV
2-1       PSB054   2      [e]           e         linguistic                        AlignBegin=5.95    e        CCONJ
2-2       PSB054   2      quindi        quindi    linguistic                        _                  quindi   ADV
```

Un diff su questo file è immediatamente leggibile da un linguista.

---

## Perché il TSV verticale è diff-friendly

```diff
# Correzione del lemma per token 1-3

-1-3  PSB102  1  no:  no  linguistic  Intonation=Rising  _  no    ADV
+1-3  PSB102  1  no:  no  linguistic  Intonation=Rising  _  no:   ADV
```

- La modifica riguarda **esattamente una riga**
- Il revisore vede **cosa è cambiato e perché** (nel messaggio di commit)
- La storia del file mostra **tutte le decisioni di annotazione nel tempo**
- Lo stesso meccanismo funziona per aggiungere un nuovo layer (nuova colonna)

Confrontate con un `.eaf` XML: anche una piccola modifica produce centinaia di righe di diff illeggibili.

---

## Architettura a tre livelli

Il pivot KIParla formalizza tre livelli espliciti:

```
Livello 1: TU (Transcription Unit)
  └── segmento attribuito a un parlante, ancorato temporalmente
        validazione: intervallo coerente (end > start), contenuto non vuoto

Livello 2: Span
  └── fenomeno Jefferson che si estende su sequenze di testo
        [sovrapposizione], °volume basso°, >velocità alta<
        validazione: delimitatori bilanciati, ancorati a token esistenti

Livello 3: Token
  └── unità lessicale o para-verbale, localmente ben formata
        validazione: inventario caratteri, tipo categorico, feature prosodiche
```

Ogni livello ha **criteri di validazione espliciti** → GitHub Action di validazione li controlla automaticamente ad ogni commit.

---

## Estensibilità per colonne: aggiungere un layer senza rompere nulla

Il formato a colonne permette di aggiungere nuovi layer di annotazione senza modificare la struttura esistente.

**Esempio: aggiunta di annotazione sintattica UD**

I token sintattici che richiedono espansione (multiword) vengono inseriti con ID estesi (`254-1a`, `254-1b`) e marcati come tipo `syntactic`. Due colonne aggiuntive (`lemma`, `upos`) memorizzano le annotazioni UD.

```
# Prima: solo trascrizione
token_id  speaker  form    type        jefferson_feats
254-1     PSB102   quindi  linguistic  _

# Dopo: layer UD aggiunto come colonne
token_id  speaker  form    type        jefferson_feats  lemma   upos
254-1     PSB102   quindi  linguistic  _                quindi  ADV
```

→ Backward compatible: chi non usa le nuove colonne le ignora semplicemente.

---

## Dall'EAF al pivot: il workflow di curatela

```
ELAN (.eaf)
    │
    ▼  pipeline di validazione (Python)
    │   ├── validazione TU (coerenza temporale)
    │   ├── validazione Span (bilanciamento delimitatori)
    │   └── validazione Token (inventario caratteri, tipi)
    │
    ▼  formato pivot (.tsv)          ← mantenuto in Git
    │
    ├──► CoNLL-U (.conllu)           ← derivato riproducibile
    ├──► ELAN riesportato (.eaf)     ← derivato riproducibile
    ├──► NoSketchEngine (.vert)      ← derivato riproducibile
    └──► KIParla Forest (treebank)   ← derivato riproducibile
```

I formati derivati vengono *rigenerati* dal pivot — non mantenuti separatamente.

---

## Cosa va in Git e cosa no: riepilogo

| Artefatto | In Git? | Note |
|---|---|---|
| Pivot TSV pseudonimizzato | ✓ sì | Cuore del repo |
| Script di validazione | ✓ sì | Parte del pipeline |
| Script di conversione | ✓ sì | Genera i derivati |
| GitHub Actions (YAML) | ✓ sì | Automazione CI |
| Linee guida di annotazione | ✓ sì | Documentazione viva |
| Metadati anonimi | ✓ sì | Codici parlante, durata |
| File audio (.wav, .flac) | ✗ no | Git LFS o storage esterno |
| EAF originali non pseudonimizzati | ✗ no | Repo privato o archivio CLARIN |
| Nomi, indirizzi, dati personali | ✗ mai | Vincolo GDPR |

---

## Il valore del tracciamento della storia

Con Git, la storia del corpus è un artefatto di ricerca in sé.

```bash
# Chi ha modificato il token 254-1 e quando?
git log --all -S "254-1" -- pivot/BOA1010.tsv

# Come era annotato questo token sei mesi fa?
git show HEAD~180:pivot/BOA1010.tsv | grep "^254-1"

# Quali token sono stati corretti dopo la prima release?
git diff v1.0.0..v1.1.0 -- pivot/
```

→ La storia dei commit **è** la documentazione delle decisioni curatoriali. Sostituisce (e supera) i changelog manuali.

---

## Versioni e rilasci: corpora come software

Git supporta un modello di rilascio esplicito con *tag*:

```bash
# Creare una versione
git tag -a v1.1.0 -m "Add ParlaBO module; fix overlap encoding in KIP"
git push origin v1.1.0
```

Su GitHub, un tag crea automaticamente una **Release** con:
- Changelog generato dai commit
- Archivio scaricabile (`.zip`, `.tar.gz`) del corpus a quella versione
- Collegamento a Zenodo per DOI permanente

→ Ogni versione del corpus è **citabile**, **riproducibile** e **confrontabile** con le precedenti.

---

## Part 3 — Riepilogo

- I file audio **non appartengono** a Git direttamente: usare Git LFS, storage esterno, o `.gitignore`
- I vincoli GDPR definiscono una netta separazione tra repo privato (dati grezzi) e repo pubblico (dati pseudonimizzati)
- Il **formato pivot TSV verticale** è la chiave: un token per riga, diff leggibili, estensibile per colonne
- L'architettura a tre livelli (TU → Span → Token) permette validazione automatica a ogni commit
- I formati derivati (CoNLL-U, ELAN, NoSketchEngine) si rigenerano dal pivot — non si mantengono separatamente
- La storia Git **è** la documentazione delle decisioni curatoriali
- **Part 4** metterà in pratica tutto questo con un demo su un repo reale

---

*Riferimenti*

- Pannitto, L. & Mauri, C. (2025). Reuse by design: a pivot-based architecture for the KIParla corpus. *CLARIN*.
- Pannitto et al. (2025). Introducing KIParla Forest. *DepLing / SyntaxFest*.
- Steiner, I. (2017). A DevOps manifesto for speech corpus management. *ESSV*.
- Rosenberg, A. (2012). Rethinking the corpus: moving towards dynamic linguistic resources. *Interspeech*.
- Dumitru et al. (2024). Version control for speech corpora. *KONVENS*.
- Waldon, B. & Schneider, N. (2025). A GitHub-based workflow for annotated resource development. *LAW XIX*.
