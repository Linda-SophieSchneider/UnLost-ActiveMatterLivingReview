# Eligibility criteria (UnLost literature review)

Status: **DRAFT** (scope proposed 2026-11-23 from the UnLost work-package overview; freezes with the protocol).

The review supports the UnLost project: non-invasive recovery, reading and study of carbonised and
damaged ancient manuscripts, above all the Herculaneum papyri (Villa dei Papiri).

| Element | Definition |
|---|---|
| **Object** | Ancient papyrus, parchment or other manuscripts, in particular carbonised, rolled, layered or fragmentary ones (Herculaneum papyri, En-Gedi and Dead Sea scrolls, mummy cartonnage, opened and unopened scrolls); also phantoms or synthetic scrolls built to stand in for them. |
| **Topic** | One or more of the work-package topics below. |
| **Outcome** | Results are reported: data, a method with an evaluation on such objects, an analysis, or an edition. |
| **Study design** | Primary research: journal article, conference paper with results, preprint, dataset or benchmark paper. |

## Topics (data item `primary_task`)

- T1 Acquisition and imaging: micro-CT, synchrotron and phase-contrast CT, multispectral or hyperspectral imaging, photoacoustic imaging, NeRF (WP1.2).
- T2 Virtual unwrapping: surface segmentation, flattening, layer and winding analysis, stratigraphy (WP1.2, WP3.2).
- T3 Ink detection and enhancement: ink segmentation, denoising, multimodal enhancement (WP2.1).
- T4 Text recognition and decipherment: OCR on volumes or flattened images, reading of revealed text (WP2.2, WP3.4).
- T5 Script and writer analysis: glyph skeletons, scribal hands, writer identification, classification of scripts (WP2.3, WP3.3).
- T6 Chemical and material characterisation: FTIR, XRF, XRD, Raman, isotopes, degree of carbonisation, ink composition (WP1.1).
- T7 Registration, provenance and metadata: alignment of multimodal witnesses, provenance of digital transformations, METS-type frameworks (WP1.3, WP1.4).
- T8 Papyrological study and context: editions of Herculaneum texts, joining of pieces, organisation of the ancient library (WP3.4, WP3.5).

## Inclusion

- I1 The object is an ancient manuscript as defined above (or a phantom of one).
- I2 The study falls under at least one of T1 to T8.
- I3 It reports results from or about such objects: measurements, a method with an evaluation on them, an analysis, or a text edition.
- I4 Primary research article, conference paper with results, preprint, or dataset/benchmark paper.
- I5 Title and abstract in English, German, Italian or French; any publication date.

## Exclusion (codes listed in order of precedence)

When several apply, the record is assigned the first applicable code, so the PRISMA flow
reports exactly one reason per excluded report.

- **E5** Not primary research: reviews, editorials, perspectives, theses duplicating an article. (Reviews are mined for citation chasing.)
- **E4** No results: protocols, project announcements, news, exhibition texts, abstracts without results.
- **E1** The object is not an ancient manuscript: modern paper or documents, medical or industrial CT without manuscripts, handwriting or OCR work on modern or medieval material, the Papyrus modelling software, the plant.
- **E3** Generic method with no experiment on, or evaluation against, ancient manuscripts or their phantoms.
- **E2** Ancient manuscript, but only literary, historical or archaeological interpretation of a text or site, with no imaging, computational or chemical method and no edition of Herculaneum material (T8).

## Decisions taken (2026-11-23)

1. Scope covers all eight topics, taken from the UnLost work packages WP1 to WP3.
2. Herculaneum is the core case; other ancient manuscripts qualify only through imaging, computational or chemical work (E2, E3).
3. Reviewers: a panel of three LLMs on the NHR@FAU gateway (see `PROTOCOL.md` §6).

Open for the author: whether non-Herculaneum papyrology (editions of other collections) stays out (current rule: yes, E2), and which languages beyond I5 to read.
