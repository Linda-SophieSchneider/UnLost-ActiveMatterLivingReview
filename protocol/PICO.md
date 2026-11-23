# Eligibility criteria (UnLost literature review)

Status: **DRAFT** (scope narrowed 2026-11-23 at the author's request; freezes with the protocol).

The review supports the UnLost project and is deliberately narrow: papyri that are read, Greek
letters that are identified, everything on the Herculaneum papyri, and virtual unwrapping.

| Element | Definition |
|---|---|
| **Object** | Papyri (any collection), above all the carbonised Herculaneum papyri; rolled, folded, sealed or fire-damaged historical documents when the study is about unwrapping or flattening them (En-Gedi scroll, sealed letters, damaged parchment); phantoms of such objects. |
| **Topic** | One of the topics below. |
| **Outcome** | Results are reported: a method with an evaluation, measurements, a dataset, or an edition of Herculaneum material. |
| **Study design** | Primary research: journal article, conference paper with results, preprint, dataset or benchmark paper. |

## Topics (data item `primary_task`)

- T1 Unwrapping: virtual unwrapping, unrolling, unfolding and flattening; surface and layer segmentation; CT acquisition for it.
- T2 Ink and hidden text: ink detection and enhancement; imaging that makes faded or concealed text on papyri readable (CT, infrared, multispectral, hyperspectral, XRF, thermography, radar, photogrammetry).
- T3 Reading: detection and recognition of characters and letters on papyri and on ancient Greek handwriting of the Hellenistic and Roman period (Greek letterforms), text-line segmentation on papyri.
- T4 Writers and scripts: writer retrieval and identification, palaeography of papyri.
- T5 Restoration and assembly: restoring lost text of papyri, reassembling papyrus fragments.
- T6 Herculaneum: any study of the Herculaneum papyri that falls outside T1 to T5, including ink chemistry, materials, editions, and the organisation of the library.

## Inclusion

- I1 The object is a papyrus, a Herculaneum papyrus, or a rolled, folded, sealed or damaged historical document studied for unwrapping (or a phantom of one).
- I2 The study falls under T1 to T6. For papyri outside Herculaneum, only T1 to T5 qualify.
- I3 It reports results: an evaluated method, measurements, a dataset, or an edition of Herculaneum material.
- I4 Primary research article, conference paper with results, preprint, or dataset/benchmark paper.
- I5 Title and abstract in English, German, Italian or French; any publication date.

## Exclusion (codes listed in order of precedence)

When several apply, the record is assigned the first applicable code, so the PRISMA flow
reports exactly one reason per excluded report.

- **E5** Not primary research: reviews, editorials, perspectives, theses duplicating an article. (Reviews are mined for citation chasing.)
- **E4** No results: protocols, project announcements, news, exhibition texts, abstracts without results.
- **E1** The object is not in scope: not a papyrus, not Herculaneum, and not a document studied for unwrapping. Examples: modern paper, medical or battery CT, handwriting and OCR on medieval or modern material, inscriptions on stone, the Papyrus modelling software, the plant.
- **E3** Generic method with no experiment on, or evaluation against, papyri or the unwrapping objects above.
- **E2** Papyrus, but outside T1 to T5 and not Herculaneum: for example literary or historical interpretation, an edition of a non-Herculaneum papyrus, or chemistry of a non-Herculaneum papyrus.

## Decisions taken (2026-11-23)

1. Scope narrowed to the six topics above (author: "papyri are read, Greek letters identified, anything Herculaneum, unwrapping").
2. Chemistry, registration and provenance only count for Herculaneum material (T6).
3. Non-papyrus manuscripts (Dead Sea Scrolls, Dunhuang, Qur'an fragments) are out unless the study is about unwrapping a rolled, sealed or damaged document.
4. Reviewers: a panel of three LLMs on the NHR@FAU gateway (see `PROTOCOL.md` §6).
5. The author's Obsidian paper collection (`01 - Research/UnLost/Paper`) is the known-item set (`seed_set.yml`).
