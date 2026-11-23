"""Weekly highlights of a Discord channel (`amlr discord-digest`).

A bot that the author owns reads one channel (an announcements channel followed into the
author's own server). The messages stay in memory: only the id of the last message seen
(`data/discord/state.json`) and the anonymised highlights (`_data/discord_highlights.yml`) are
written. Highlights carry no personal names, no quotes and only links found in the messages;
the model is told so (`protocol/discord_prompt.md`) and the output is checked afterwards.

Credentials, never in the repository: DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from .config import REPO_ROOT
from .llm import PANEL, chat, client_for, parse_json_object

API = "https://discord.com/api/v10"
DISCORD_EPOCH_MS = 1420070400000
PROMPT_FILE = REPO_ROOT / "protocol" / "discord_prompt.md"
STATE = REPO_ROOT / "data" / "discord" / "state.json"
OUT = REPO_ROOT / "_data" / "discord_highlights.yml"
MAX_PROMPT_CHARS = 60_000
_SPLIT = "<!-- RECORD TEMPLATE -->"
_URL = re.compile(r"https?://[^\s<>\")\]]+")
_MENTION = re.compile(r"<@[!&]?\d+>|<#\d+>|@(?:everyone|here)")
_DISCORD_LINK = re.compile(r"https?://(?:[\w-]+\.)?(?:discord\.com|discord\.gg|discordapp\.com|discordapp\.net)\S*", re.I)


def snowflake(when: datetime) -> int:
    """Smallest message id created at `when` (for `after=` paging)."""

    return (int(when.timestamp() * 1000) - DISCORD_EPOCH_MS) << 22


def _get(path: str, token: str, params: dict) -> list[dict]:
    url = f"{API}{path}?" + "&".join(f"{k}={v}" for k, v in params.items())
    for attempt in range(5):
        req = urllib.request.Request(url, headers={"Authorization": f"Bot {token}", "User-Agent": "amlr-digest (bot)"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(float(e.headers.get("Retry-After", 2 ** attempt)) + 0.5)
                continue
            if e.code in (401, 403):
                raise RuntimeError(f"Discord refused the bot (HTTP {e.code}): check the token, the channel id, "
                                   "that the bot is in the server, and its View Channel and Read Message History rights") from e
            raise
    raise RuntimeError("Discord rate limit not clearing")


def fetch_messages(channel_id: str, token: str, after: int, get=_get) -> list[dict]:
    """All messages after the snowflake `after`, oldest first."""

    out: list[dict] = []
    while True:
        page = get(f"/channels/{channel_id}/messages", token, {"limit": 100, "after": after})
        if not page:
            break
        out.extend(page)
        after = max(int(m["id"]) for m in page)
        if len(page) < 100:
            break
    return sorted(out, key=lambda m: int(m["id"]))


def message_text(m: dict) -> str:
    """Content plus embed titles/descriptions; author names and ids are never read."""

    parts = [m.get("content") or ""]
    for e in m.get("embeds") or []:
        parts += [e.get("title") or "", e.get("description") or "", e.get("url") or ""]
    for snap in m.get("message_snapshots") or []:  # forwarded messages
        parts.append((snap.get("message") or {}).get("content") or "")
    text = "\n".join(p for p in parts if p).strip()
    return _MENTION.sub("someone", text)


def links_in(texts: list[str]) -> set[str]:
    return {u.rstrip(".,;:") for t in texts for u in _URL.findall(t) if not _DISCORD_LINK.match(u)}


def _words(s: str) -> list[str]:
    return re.findall(r"\w+", s.lower())


def copies_source(text: str, sources: list[str], n: int = 8) -> bool:
    """True if `text` repeats n or more consecutive words of any source message."""

    grams = {tuple(w[i:i + n]) for s in sources for w in [_words(s)] for i in range(len(w) - n + 1)}
    w = _words(text)
    return any(tuple(w[i:i + n]) in grams for i in range(len(w) - n + 1))


def load_prompt(path: Path = PROMPT_FILE) -> tuple[str, str]:
    system, template = path.read_text(encoding="utf-8").split(_SPLIT, 1)
    return system.strip(), template.strip()


def summarise(texts: list[str], ask=None) -> dict:
    """Highlights of the week from `texts`, checked: only source links, no copied passages."""

    if not texts:
        return {"summary": "No announcements this week.", "highlights": []}
    system, template = load_prompt()
    body = "\n\n---\n\n".join(texts)[:MAX_PROMPT_CHARS]
    user = template.replace("{n}", str(len(texts))).replace("{body}", body)
    if ask is None:
        client = client_for(PANEL["R1"])
        ask = lambda: chat(client, system, user, max_tokens=4096).content
    data = parse_json_object(ask(), "highlights")
    allowed = links_in(texts)
    kept, dropped = [], 0
    for h in data.get("highlights") or []:
        blob = f"{h.get('title', '')} {h.get('summary', '')}"
        if copies_source(blob, texts):
            dropped += 1
            continue
        kept.append({"title": str(h.get("title", "")).strip(), "summary": str(h.get("summary", "")).strip(),
                     "links": [u for u in h.get("links") or [] if u.rstrip(".,;:") in allowed][:4]})
    summary = str(data.get("summary", "")).strip()
    if copies_source(summary, texts):
        summary = ""
    return {"summary": summary, "highlights": kept[:6], "dropped_as_copies": dropped}


def merge_entry(path: Path, entry: dict) -> None:
    """Newest first; one entry per week_end (a rerun replaces it)."""

    rows = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else []
    rows = [r for r in (rows or []) if r.get("week_end") != entry["week_end"]]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump([entry, *rows], sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")


def run(since_days: int = 7, dry_run: bool = False, now: datetime | None = None, get=_get, ask=None) -> dict:
    token, channel = os.environ.get("DISCORD_BOT_TOKEN", "").strip(), os.environ.get("DISCORD_CHANNEL_ID", "").strip()
    if not token or not channel:
        raise RuntimeError("Set DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID (see README, Discord highlights).")
    now = now or datetime.now(timezone.utc)
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    after = int(state["last_id"]) if state.get("last_id") else snowflake(now - timedelta(days=since_days))
    messages = fetch_messages(channel, token, after, get=get)
    texts = [t for t in (message_text(m) for m in messages) if t]
    result = summarise(texts, ask=ask)
    entry = {"week_start": (now - timedelta(days=since_days)).date().isoformat(), "week_end": now.date().isoformat(),
             "n_messages": len(texts), "summary": result["summary"], "highlights": result["highlights"]}
    if not dry_run:
        merge_entry(OUT, entry)
        if messages:
            STATE.parent.mkdir(parents=True, exist_ok=True)
            STATE.write_text(json.dumps({"last_id": str(max(int(m["id"]) for m in messages))}) + "\n")
    return {**entry, "dropped_as_copies": result.get("dropped_as_copies", 0), "dry_run": dry_run}
