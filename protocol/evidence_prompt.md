You are one reviewer on a panel for a systematic review that supports the UnLost project
(non-invasive recovery, reading and study of carbonised and damaged ancient manuscripts, above
all the Herculaneum papyri). The panel disagreed about one study, and the author will settle the
disagreement. The author decides from the evidence you quote, so every claim must rest on passages
copied EXACTLY from the full text below (verbatim, no paraphrase, at most 40 words each). Quotes
are checked against the text automatically; a quote that does not appear in the text counts
against you.

Eligibility criteria:
- I1 The object is an ancient manuscript (papyrus, parchment, scroll), in particular carbonised,
  rolled or fragmentary, or a phantom of one.
- I2 The study falls under acquisition/imaging, virtual unwrapping, ink detection, text
  recognition, script/writer analysis, chemical characterisation, registration/provenance, or
  papyrological study of Herculaneum material.
- I3 It reports results from or about such objects (measurements, an evaluated method, an
  analysis, or an edition).
- I4 Primary research article, conference paper with results, preprint, or dataset paper.
- Exclusion, in order of precedence: E5 not primary research; E4 no results; E1 object is not an
  ancient manuscript; E3 generic method with no experiment on or evaluation against ancient
  manuscripts; E2 only literary/historical/archaeological interpretation, no method and no
  Herculaneum edition.

{task}

Respond with ONLY one JSON object. Give at most 4 quotes per claim. If no passage supports a
claim, give an empty "evidence" list and say so in "claim"; you may revise your earlier answer
if the text does not bear it out.
<!-- SCREENING TASK -->
Your earlier full-text decision: {decision}. Your earlier rationale: {rationale}

Re-read the full text. State your decision and quote the passages that establish it, naming the
criterion each quote bears on.
{{"decision": "include" | "exclude", "reason": "E1".."E5" or null, "claim": "<one sentence>",
 "evidence": [{{"criterion": "I1" | "I2" | "I3" | "I4" | "E1" | ... | "E5", "quote": "<verbatim>"}}]}}
<!-- EXTRACTION TASK -->
The extractors gave different values for the fields below. Your earlier values are shown. For each
field, state the value the paper supports and quote the passages that establish it (or state
that the paper does not report it, with value null).
{fields}
{{"fields": {{"<field>": {{"value": ..., "claim": "<one sentence>", "evidence": [{{"quote": "<verbatim>"}}]}}}}}}
<!-- RECORD TEMPLATE -->
Title: {title}
Year: {year}
Venue: {venue}

Full text:
{body}
