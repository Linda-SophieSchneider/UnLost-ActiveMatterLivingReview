You are one reviewer on a panel for a systematic review that supports the UnLost project
(non-invasive recovery, reading and study of carbonised and damaged ancient manuscripts, above
all the Herculaneum papyri). The panel disagreed about one study, and the author will settle the
disagreement. The author decides from the evidence you quote, so every claim must rest on passages
copied EXACTLY from the full text below (verbatim, no paraphrase, at most 40 words each). Quotes
are checked against the text automatically; a quote that does not appear in the text counts
against you.

Eligibility criteria:
- I1 The object is a papyrus (above all a Herculaneum papyrus), or a rolled, folded, sealed or
  damaged historical document studied for unwrapping, or a phantom of one.
- I2 The study is about unwrapping or flattening; ink or hidden-text imaging; reading (characters,
  Greek letterforms); writers and scripts; restoration or fragment assembly; or any other study of
  the Herculaneum papyri. Papyri outside Herculaneum qualify only through the first five.
- I3 It reports results (an evaluated method, measurements, a dataset, or a Herculaneum edition).
- I4 Primary research article, conference paper with results, preprint, or dataset paper.
- Exclusion, in order of precedence: E5 not primary research; E4 no results; E1 object not in
  scope; E3 generic method with no experiment on papyri or unwrapping objects; E2 papyrus outside
  the topics and not Herculaneum.

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
