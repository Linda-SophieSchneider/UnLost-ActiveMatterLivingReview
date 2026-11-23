import json
from datetime import datetime, timezone

import yaml

from amlr import discord as D

MSGS = [
    {"id": "300", "content": "Ping <@123> new scan of PHerc. 172 released: https://example.org/scan and https://discord.com/channels/1/2/3",
     "author": {"username": "someone_real"}},
    {"id": "100", "content": "", "embeds": [{"title": "Prize deadline", "description": "Submissions for the unwrapping prize close on Friday."}]},
    {"id": "200", "content": "thanks everyone!"},
]


def test_snowflake_orders_with_time():
    a = D.snowflake(datetime(2026, 11, 1, tzinfo=timezone.utc))
    b = D.snowflake(datetime(2026, 11, 8, tzinfo=timezone.utc))
    assert 0 < a < b


def test_fetch_pages_until_short_page_and_sorts():
    calls = []

    def get(path, token, params):
        calls.append(params["after"])
        return MSGS if len(calls) == 1 else []

    out = D.fetch_messages("1", "t", 0, get=get)
    assert [m["id"] for m in out] == ["100", "200", "300"] and len(calls) == 1


def test_message_text_drops_mentions_and_ignores_author():
    t = D.message_text(MSGS[0])
    assert "<@123>" not in t and "someone_real" not in t and "PHerc. 172" in t
    assert "Prize deadline" in D.message_text(MSGS[1])


def test_links_exclude_discord():
    links = D.links_in([D.message_text(MSGS[0])])
    assert links == {"https://example.org/scan"}


def test_copied_passages_are_detected():
    src = ["Submissions for the unwrapping prize close on Friday at noon."]
    assert D.copies_source("Submissions for the unwrapping prize close on Friday at noon, they said", src)
    assert not D.copies_source("The unwrapping prize has a deadline this week", src)


def test_summarise_filters_links_and_copies():
    texts = [D.message_text(MSGS[0]), D.message_text(MSGS[1])]
    answer = json.dumps({"summary": "A quiet week with one release.", "highlights": [
        {"title": "New scan", "summary": "A new scan was released.", "links": ["https://example.org/scan", "https://evil.example/x", "https://discord.com/channels/1/2/3"]},
        {"title": "Copy", "summary": "Submissions for the unwrapping prize close on Friday.", "links": []},
    ]})
    out = D.summarise(texts, ask=lambda: answer)
    assert len(out["highlights"]) == 1 and out["dropped_as_copies"] == 1
    assert out["highlights"][0]["links"] == ["https://example.org/scan"]


def test_empty_week_makes_no_model_call():
    out = D.summarise([], ask=lambda: (_ for _ in ()).throw(AssertionError("called")))
    assert out["highlights"] == []


def test_run_writes_entry_and_state_and_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "OUT", tmp_path / "h.yml")
    monkeypatch.setattr(D, "STATE", tmp_path / "state.json")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "t")
    monkeypatch.setenv("DISCORD_CHANNEL_ID", "1")
    now = datetime(2026, 11, 23, tzinfo=timezone.utc)
    answer = json.dumps({"summary": "One release.", "highlights": [{"title": "Scan", "summary": "A scan.", "links": []}]})
    pages = iter([MSGS, []])
    res = D.run(now=now, get=lambda *a: next(pages), ask=lambda: answer)
    assert res["n_messages"] == 3
    assert json.loads((tmp_path / "state.json").read_text())["last_id"] == "300"
    D.run(now=now, get=lambda *a: [], ask=lambda: answer)  # nothing new: same week_end entry is replaced
    rows = yaml.safe_load((tmp_path / "h.yml").read_text())
    assert len(rows) == 1 and rows[0]["week_end"] == "2026-11-23"
