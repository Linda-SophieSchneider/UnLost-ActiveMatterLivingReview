# Protocol: Literature review for the UnLost project

Status: **DRAFT 2026-11-23, not frozen, not registered.** Freeze = `amlr freeze` manifest +
tag `protocol-v1` (+ optional OSF Registries entry), both before the first screening decision.
Amendments after freezing are new, dated entries in the amendment log; earlier text is never
edited in place.

Derived from the Active Matter Living Review pipeline (Maier et al., 2026), whose procedures
this protocol keeps; scope, search blocks, prompts and data items are UnLost-specific.

Reporting standard: PRISMA 2020 (Page et al., BMJ 2021;372:n71), checklist mapping in
`prisma_checklist.md`. Living-review conventions follow Elliott et al. (2017).

## 1. Rationale (PRISMA 3)

UnLost aims to recover, read and study carbonised and damaged papyri, above all the Herculaneum
papyri, without opening them. This review is deliberately narrow: papyri that are read, Greek
letters that are identified, everything on the Herculaneum papyri, and virtual unwrapping.

## 2. Objectives (PRISMA 4)

- O1. Map which imaging techniques have been applied to rolled, sealed or carbonised papyri and
  documents, at what resolution and on which objects.
- O2. Establish which methods exist for virtual unwrapping, ink detection, and the reading of
  characters and letters on papyri, and how they were validated.
- O3. Collect what is known about the Herculaneum papyri (chemistry, scripts, editions, library)
  and about writers and scripts of Greek papyri.
- O4. Identify available datasets, ground truth and open code.
- O5. Identify gaps that the UnLost work packages can address.

## 3. Eligibility criteria (PRISMA 5)

Operationalised in `PICO.md`.

## 4. Information sources (PRISMA 6)

| Source | Interface | Role |
|---|---|---|
| OpenAlex | REST `api.openalex.org/works`, `title_and_abstract.search` | primary |
| SemOpenAlex | SPARQL `semopenalex.org/sparql` | fallback for metadata and citation lookups; not a separate search source |
| Crossref | REST `api.crossref.org/works`, `query.bibliographic` | primary; no Boolean search, so one relevance query (top 100) per OBJECT-METHOD pair and phrase, then the same Boolean logic applied locally to title + abstract |
| arXiv | `export.arxiv.org/api/query`, field `all:` | primary; `all:` also matches authors and comments, because the title-and-abstract form of the query exceeds arXiv's URL length limit |
| bioRxiv | Europe PMC preprint index | primary |
| PubMed | NCBI E-utilities | primary |
| IEEE Xplore | Command Search (web), Abstract field | primary; two queries within IEEE's limits (`amlr.search.render_ieee`), exported as CSV |
| HAL | `api.archives-ouvertes.fr/search` | primary |
| NASA ADS | `api.adsabs.harvard.edu/v1` | primary |
| Citation chasing | OpenAlex references/cited-by of included studies and of excluded reviews | supplementary |
| Hand-search | Cronache Ercolanesi, Zeitschrift fuer Papyrologie und Epigraphik, ICDAR and ICFHR proceedings, Vesuvius Challenge open reports | supplementary |
| Author's collection | Obsidian paper collection `01 - Research/UnLost/Paper`, used as the known-item set | validation |

Date coverage: database inception to the run date. Language: see `PICO.md` I5.

## 5. Search strategy (PRISMA 7)

Concept blocks live in `search_strategies/concepts.yml`; the logic is
`(OBJECT AND METHOD) OR COMPOSITE-PHRASES`. `amlr search` renders the per-source syntax and
writes one dated file per source and run (`search_strategies/<source>-<YYYY-MM-DD>.txt`) with
the exact query string, run timestamp, record count, and SHA-256 of the raw payload.

Sensitivity check: known-item recall on `search_strategies/seed_set.yml` (`amlr
search-validate`); every seed paper must be retrieved by at least one primary source before
freezing. Peer review of the search: PRESS 2015 checklist by a second person before freezing.

## 6. Selection process (PRISMA 8)

- Deduplication: DOI canonicalization, then normalized-title Jaccard ≥ 0.9 (`amlr.dedup`);
  merged records keep all source IDs.
- Reviewers: a panel of three large language models served on the NHR@FAU LLM gateway
  (`https://hub.nhr.fau.de/api/llmgw/v1`, OpenAI-compatible):

  | Reviewer | Gateway model ID |
  |---|---|
  | R1 | `gpt-oss-120b` |
  | R2 | `GaleneAI/Magistral-Small-2509-FP8-Dynamic` |
  | R3 | `deepseek-ai/DeepSeek-V4-Flash-0731` |

  All three were listed by the gateway on 2026-11-23 and are the package defaults.

- Independence: each model screens every record in a fresh context, without access to the
  other models' votes. Instructions are the frozen screening prompt
  (`protocol/screening_prompt.md`, SHA-256 pinned at freezing), temperature 0.
- Output per vote: include/exclude, one exclusion code (E1–E5, `PICO.md`), confidence, and a
  ≤ 40-word rationale. Every vote is stored with reviewer, gateway-reported model string,
  prompt SHA-256, timestamp, and the raw response (`data/screening/*-votes.jsonl`).
- Decision rule (both stages): a record is included when ≥ 2 of 3 reviewers vote include.
  The exclusion reason is the majority code, or the highest-precedence code if all three
  differ. Title/abstract: records without an abstract proceed to full text unless all three
  reviewers exclude on the title.
- Vote sequencing: R1 and R2 vote on every record; R3 votes only where its vote can change
  the outcome — R1 and R2 disagree, both exclude a record without an abstract, or (full text
  only) both exclude with different codes — so every inclusion decision equals that of a full
  three-vote majority. At title/abstract, PRISMA 2020 reports exclusions as a count without
  reasons, so differing codes are resolved by precedence rather than by R3
  (the conventional two-reviewers-plus-arbiter design). R3 additionally votes on a fixed
  10 % audit sample (deterministic by record-ID hash), on which Fleiss' κ is reported.
  The decision rule itself equals a full three-vote majority.
- Full text: the same panel and rule, on text extracted from the retrieved report.
- Agreement: Fleiss' κ across the panel and pairwise Cohen's κ, reported per stage.
- Calibration (before screening): every eligible paper in `search_strategies/seed_set.yml`
  must be included by the panel at the title/abstract stage; otherwise the prompt is revised
  and the check repeated before it is frozen.
- Validation (after panel screening, by the author): the author independently labels a
  random sample of 200 title/abstract records and all 1-of-3 split votes at full text, to
  report panel sensitivity and specificity and to retain human accountability for the final
  inclusion set. If title/abstract sensitivity is < 0.95, the prompt is amended (logged as an
  amendment) and all records are re-screened. The author labels on the site's `/check/` page:
  the sample (fixed in `data/human_check/ta_sample.txt`) is labelled blind to the panel votes,
  and sensitivity is computed from the blind label. Labels are kept in the append-only ledger
  `data/human_check/labels.jsonl`. An author decision on a full-text split or a seed paper
  replaces the panel decision. At title/abstract, an author include sends a panel-excluded
  record to full-text retrieval; an author exclude is reported but not applied when a
  full-text assessment exists, because that assessment supersedes it.
- Reproducibility caveat: served models are not bit-for-bit deterministic even at
  temperature 0; the stored votes are the record of decision and are not re-generated. A
  model retired from the gateway is replaced only by protocol amendment, after re-calibration
  on the pilot set.

## 7. Data collection process (PRISMA 9)

Extraction form: `protocol/extraction_prompt.md` (controlled vocabularies, JSON output),
piloted on 10 included studies and then frozen with `amlr freeze` before the remaining
extractions. R1 and R3 extract independently from the full text; coded fields are compared
exactly, list fields as sets, counts within 10 %, sizes within 25 %; only disputed fields are
extracted by R2 and settled by majority (multi-label fields — imaging modality, outputs, origin —
label-wise: a label is kept if at least two of the three extractors chose it); single-valued
fields with three different values are flagged for author resolution. Missing items are
recorded as missing, not imputed.

## 8. Data items (PRISMA 10)

Object class and name; primary task (T1 to T8); method family; imaging modality, instrument
and resolution; number of objects, scans and annotated samples; outputs; origin of the material;
metrics reported; validation type; code and data availability (`protocol/extraction_prompt.md`).

## 9. Risk of bias / study quality (PRISMA 11)

No validated tool exists for this literature. We use a pre-specified six-domain rating
(low / some concerns / high): D1 ground truth (quality and independence); D2 representativeness
of the samples for the target objects; D3 documentation of acquisition and processing; D4
validity of the evaluation; D5 data and code availability; D6 validation by papyrologists or
other domain experts. All three reviewers rate independently; the per-domain rating is the
majority, or "some concerns" if all three differ.

## 10. Effect measures (PRISMA 12)

Not applicable in the meta-analytic sense; outcomes are heterogeneous. Metrics are reported as given.

## 11. Synthesis methods (PRISMA 13)

Narrative synthesis organised by a taxonomy derived from the data items; evidence maps
(task x imaging modality, task x method family, origin x validation). No meta-analysis or vote
counting. Sensitivity: syntheses repeated excluding studies rated high risk in D1 or D4.

## 12. Reporting bias and certainty (PRISMA 14–15)

Comparison of preprint-only vs. peer-reviewed findings. Certainty per synthesis statement:
high / moderate / low, based on the number of independent objects, groups and datasets.

## 13. Living-review procedures

- Searches re-run monthly by `.github/workflows/living-update.yml` (secrets required; see README).
  Screening of new records is batched per update, and each update arrives as a pull request.
- Each update produces a dated snapshot (`data/snapshots/<date>/`), an updated PRISMA flow,
  and a change-log entry on the website.

## 14. Registration, support, competing interests, data availability (PRISMA 24–27)

- Registration: not yet registered.
- Support / funding: to be completed by the author (computing on the NHR@FAU LLM gateway).
- Competing interests: to be completed by the author.
- Availability: code (`pipeline/`), search strings, decisions, extraction data, and
  snapshots are public in this repository; subscriber full texts are not redistributed.
- Use of AI tools: screening and extraction are done by an LLM panel and validated by the
  author (`/check/`); all votes are stored.

## Amendment log

| Date | Change | Reason |
|---|---|---|
| 2026-11-23 | Protocol rewritten for UnLost (scope, search, prompts, data items); procedures of the Active Matter Living Review kept | New review in a forked pipeline; nothing screened yet |
