import json

from amlr.extract import disputed, reconcile, run
from amlr.llm import PANEL
from amlr.storage import read_jsonl, write_jsonl

BASE = {
    "object_class": "vibration_driven_robots", "object_name": "Hexbug", "n_objects": 10,
    "n_scans": 100, "resolution_um": 40, "primary_task": "vibration",
    "imaging_modality": ["steric_contact"], "method_family": "no_control_passive_rules",
    "instrument": "circular arena", "outputs": ["flocking_polar_order", "boundary_accumulation"],
    "metrics": ["polar order"], "corpus_origin": ["active_brownian_particles"], "validation": "quantitative",
    "n_annotated_samples": 5, "code_available": False, "data_available": None,
    "rob": {k: {"rating": "low", "why": "ok"} for k in [
        "D1_ground_truth", "D2_sample_representativeness", "D3_acquisition_documentation",
        "D4_evaluation_validity", "D5_data_code_availability", "D6_expert_validation"]},
    "notes": None,
}


def test_comparison_rules():
    b = dict(BASE, n_scans=105, outputs=["boundary_accumulation", "flocking_polar_order"], object_name="HEXBUG nano")
    assert disputed(BASE, b) == []  # counts within 10 %, sets order-free, free text not compared
    c = dict(BASE, primary_task="legs", n_scans=200)
    assert set(disputed(BASE, c)) == {"primary_task", "n_scans"}


def test_reconcile_majority_and_unresolved():
    b = dict(BASE, primary_task="legs", validation="qualitative")
    arb = dict(BASE, primary_task="legs", validation="none")
    final, unresolved = reconcile(BASE, b, arb)
    assert final["primary_task"] == "legs"
    assert final["validation"] is None and unresolved == ["validation"]
    assert final["rob.D1_ground_truth"] == "low"


def test_run_calls_arbiter_only_for_disputes(tmp_path):
    corpus = tmp_path / "corpus.jsonl"
    write_jsonl(corpus, [{"id": "a", "phase": "included", "title": "t", "fulltext_txt_path": "x"},
                         {"id": "b", "phase": "included", "title": "u", "fulltext_txt_path": "y"}])
    answers = {("R1", "t"): BASE, ("R3", "t"): BASE,
               ("R1", "u"): BASE, ("R3", "u"): dict(BASE, primary_task="legs"), ("R2", "u"): dict(BASE, primary_task="legs")}
    rv_of = {m: rv for rv, m in PANEL.items()}
    calls = []

    def transport(url, headers, body, timeout):
        p = json.loads(body)
        title = p["messages"][1]["content"].split("Title: ", 1)[1].split("\n", 1)[0]
        rv = rv_of[p["model"]]
        calls.append((rv, title))
        return {"model": p["model"], "choices": [{"message": {"content": json.dumps(answers[(rv, title)])}, "finish_reason": "stop"}]}

    out = run(corpus, lambda r: "full text " * 100, workers=1, transport=transport,
              ledger=tmp_path / "votes.jsonl", final_path=tmp_path / "final.jsonl")
    assert out["extracted"] == 2 and out["with_unresolved_fields"] == 0
    assert ("R2", "t") not in calls and ("R2", "u") in calls
    rows = {r["id"]: r for r in read_jsonl(corpus)}
    assert rows["b"]["extraction"]["primary_task"] == "legs"


def test_multilabel_fields_use_labelwise_majority():
    a = dict(BASE, outputs=["chirality_or_rotation", "transport_or_locomotion", "boundary_accumulation"])
    b = dict(BASE, outputs=["chirality_or_rotation", "swarming_or_vortex", "transport_or_locomotion"])
    c = dict(BASE, outputs=["chirality_or_rotation", "boundary_accumulation"])
    final, unresolved = reconcile(a, b, c)
    assert final["outputs"] == ["boundary_accumulation", "chirality_or_rotation", "transport_or_locomotion"]
    assert "outputs" not in unresolved


def test_rob_three_way_split_resolves_to_some_concerns():
    rob = lambda r: {k: {"rating": r, "why": ""} for k in BASE["rob"]}
    final, unresolved = reconcile(dict(BASE, rob=rob("low")), dict(BASE, rob=rob("high")), dict(BASE, rob=rob("some_concerns")))
    assert final["rob.D1_ground_truth"] == "some_concerns" and not any(u.startswith("rob.") for u in unresolved)


def test_availability_null_and_false_agree():
    assert "code_available" not in disputed(dict(BASE, code_available=None), dict(BASE, code_available=False))
    assert "code_available" in disputed(dict(BASE, code_available=True), dict(BASE, code_available=None))
