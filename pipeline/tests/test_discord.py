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


EXPORT = """# Vesuvius Challenge Discord – Export
# #show-and-tell

## Ink labels: one dataset
Thread: https://discord.com/channels/1/2 (erstellt 2026-11-23 19:25)

**alicehandle** · 2026-11-23 19:25
Released labels, see https://huggingface.co/datasets/someone/ink-labels and https://cdn.discordapp.com/x.png thanks @bobhandle

**bobhandle** · 2026-11-23 19:40
great work alicehandle, repo https://github.com/org/tool and https://github.com/user-attachments/assets/1

# #unrolling-vc3d (4 Nachrichten, chronologisch)

### 2026-06-29

**alicehandle** · 13:16 UTC
fiber question

### 2026-07-01

**bobhandle** · 10:00 UTC
reply
"""


def test_parse_export_threads_and_weeks():
    items = D.parse_export(EXPORT)
    # 29 June and 1 July fall into the same ISO week, so they form one item
    assert [i["channel"] for i in items] == ["show-and-tell", "unrolling-vc3d"]
    assert items[0]["title"] == "Ink labels: one dataset" and items[0]["period"] == "2026-11-23"
    assert "Thread:" not in items[0]["body"]
    assert items[1]["title"] == "Week 2026-W27" and "reply" in items[1]["body"] and "fiber question" in items[1]["body"]


def test_anonymise_replaces_authors_and_mentions():
    names = D.author_names(EXPORT)
    out = D.anonymise(D.parse_export(EXPORT)[0]["body"], names)
    assert "alicehandle" not in out and "bobhandle" not in out
    assert "**P1**" in out and "**P2**" in out


def test_repo_links_keep_code_and_data_only():
    body = D.parse_export(EXPORT)[0]["body"]
    assert D.repo_links(body) == ["https://huggingface.co/datasets/someone/ink-labels", "https://github.com/org/tool"]


def test_snapshot_selects_by_relevance_and_scrubs_names():
    items = D.parse_export(EXPORT)
    names = D.author_names(EXPORT)

    def ask(system, user):
        rel = 3 if "Ink labels" in user else 0
        return json.dumps({"title": "Ink label dataset", "summary": "alicehandle released a merged ink dataset.",
                           "topic": "ink_detection", "relevance": rel})

    snap = D.build_snapshot(items, names, ask, workers=1)
    assert snap["n_discussions"] == 2 and snap["n_selected"] == 1
    item = snap["topics"][0]["items"][0]
    assert item["summary"] == "a participant released a merged ink dataset."
    assert item["links"][0].startswith("https://huggingface.co/")


def test_long_week_is_split():
    body = "\n\n".join(f"**a** · 10:{i:02d} UTC\n" + "x" * 3000 for i in range(10))
    parts = D._chunks(body, size=14000)
    assert len(parts) >= 3 and all(len(p) <= 14000 + 3100 for p in parts)
