---
layout: page
title: "Contribute"
permalink: /contribute/
---

Missed a paper? Propose it here. The form writes a small YAML file and opens GitHub's
"propose new file" page, which turns it into a **pull request** that we review. A check runs on
every pull request: it confirms the DOI at Crossref, matches the title, and tells you whether the
review already holds the paper. After we merge it, the paper is screened in the next update by the
same panel and criteria as every database record. In PRISMA terms it is a record identified via
other methods, so merging does not guarantee inclusion.

The review is deliberately narrow: **papyri that are read** (characters, Greek letters, writers),
**everything on the Herculaneum papyri**, and **virtual unwrapping** of rolled, sealed or damaged
documents (see the eligibility criteria under Methods).

<link rel="stylesheet" href="{{ '/assets/css/contribute.css' | relative_url }}">
<form id="sub" class="sub" novalidate>
  <div class="sub-row">
    <label for="sub-doi">DOI</label>
    <div class="sub-inline">
      <input id="sub-doi" name="doi" placeholder="10.1126/sciadv.1601247" autocomplete="off">
      <button type="button" id="sub-lookup">Look up</button>
    </div>
    <small>Fills in title, authors, year and venue from Crossref. No DOI? Give an arXiv id instead.</small>
  </div>
  <div class="sub-row"><label for="sub-arxiv">arXiv id</label><input id="sub-arxiv" name="arxiv" placeholder="2401.01234"></div>
  <div class="sub-row"><label for="sub-title">Title <span>required</span></label><input id="sub-title" name="title" required></div>
  <div class="sub-row"><label for="sub-authors">Authors</label><input id="sub-authors" name="authors" placeholder="First Author; Second Author"></div>
  <div class="sub-two">
    <div class="sub-row"><label for="sub-year">Year <span>required</span></label><input id="sub-year" name="year" inputmode="numeric" required></div>
    <div class="sub-row"><label for="sub-venue">Venue</label><input id="sub-venue" name="venue"></div>
  </div>
  <div class="sub-row">
    <label for="sub-why">Why it belongs <span>required</span></label>
    <textarea id="sub-why" name="why" rows="3" required placeholder="e.g. Character detection on Greek papyri; reports detection accuracy on an annotated dataset."></textarea>
  </div>
  <div class="sub-row"><label for="sub-by">Your GitHub handle</label><input id="sub-by" name="submitted_by" placeholder="optional"></div>
  <p class="sub-msg" id="sub-msg" role="status" aria-live="polite"></p>
  <div class="sub-actions">
    <button type="submit" class="sub-primary">Propose on GitHub</button>
    <button type="button" id="sub-copy">Copy YAML</button>
  </div>
  <details class="sub-preview"><summary>Preview the file</summary><pre id="sub-yaml"></pre></details>
</form>

Prefer working in git? Copy
[`submissions/TEMPLATE.yml`](https://github.com/Linda-SophieSchneider/UnLost-ActiveMatterLivingReview/blob/main/submissions/TEMPLATE.yml)
to a new file in `submissions/` and open a pull request. One file per paper.

<script src="{{ '/assets/js/contribute.js' | relative_url }}"></script>
