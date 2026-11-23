from amlr.fetch import crossref_subqueries
from amlr.search import SYNTAX, load_concepts, matches, render, render_ieee

C = load_concepts()


def test_local_matcher_follows_boolean_logic():
    assert matches(C, "Virtual unwrapping of a carbonized scroll with micro-CT")
    assert matches(C, "Ink detection in Herculaneum papyri using deep learning")
    assert matches(C, "X-ray fluorescence of papyri from the Villa dei Papiri")
    assert matches(C, "The Vesuvius Challenge")
    assert not matches(C, "A single robot arm grasps objects")
    assert not matches(C, "Computed tomography of the lung")
    assert not matches(C, "Herculaneum street plan")  # object without a method
    # Spelling variants and plurals are matched; truncation works on the last word only.
    assert matches(C, "Palaeographic analysis of scribal hands in a papyrus")
    assert matches(C, "Deep learning segmentation of rolled scrolls")


def test_renderers_respect_source_truncation_rules():
    oa = render(C, SYNTAX["openalex"])
    assert "*" not in oa  # OpenAlex has no truncation operator
    pm = render(C, SYNTAX["pubmed"])
    assert '"carbonized scroll*"[tiab]' in pm  # PubMed truncates inside phrases
    ax = render(C, SYNTAX["arxiv"])
    assert "all:tomograph*" in ax and 'all:"carbonized scroll"' in ax


def test_crossref_subqueries_cover_pairs_and_phrases():
    sq = crossref_subqueries(C)
    assert len(sq) == len(C["object"]) * len(C["method"]) + len(C["composite_phrases"])
    assert "virtual unwrapping" in sq


def test_ieee_queries_stay_within_limits():
    q1, q2 = render_ieee(C)
    assert q1.count("*") <= 10 and "virtual unwrapping" in q2
