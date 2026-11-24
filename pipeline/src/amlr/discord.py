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


# ---------------------------------------------------------------------------------------------
# One-off snapshot from a Markdown export of several channels (`amlr discord-snapshot`).
# Authors are replaced by P1, P2, ... before the model sees the text; names found in the export are
# also replaced in the model's answer. Only links to code, data and papers are kept.

SNAPSHOT_PROMPT = REPO_ROOT / "protocol" / "discord_snapshot_prompt.md"
SNAPSHOT_OUT = REPO_ROOT / "_data" / "discord_snapshot.yml"
# Channels without threads (a continuous text channel): entries link to the channel itself.
CHANNEL_LINKS = {"unrolling-vc3d": "https://discord.com/channels/1079907749569237093/1243576621722767412"}
TOPICS = {
    "unwrapping_surfaces": "Unwrapping and surface tracing",
    "ink_detection": "Ink detection",
    "reading_text": "Reading and papyrology",
    "data_and_scans": "Data and scans",
    "tools_and_viewers": "Tools and viewers",
    "robots_and_hardware": "Robots and hardware",
    "community_and_competition": "Community and competition",
    "other": "Other",
}
_AUTHOR = re.compile(r"^\*\*(.+?)\*\* · ", re.M)
_REPO_HOST = re.compile(
    r"https?://(?:www\.)?(?:github\.com|gitlab\.com|huggingface\.co|zenodo\.org|arxiv\.org|doi\.org|"
    r"colab\.research\.google\.com|scrollprize\.org|pypi\.org|crates\.io|kaggle\.com|dl\.ash2txt\.org|"
    r"vesuvius-challenge-open-data\.s3[\w.-]*\.amazonaws\.com)\S*", re.I)
_NOT_A_REPO = re.compile(r"/user-attachments/|cdn-thumbnails|/resolve/|\.(?:png|jpe?g|gif|webp|mp4)(?:\?|$)", re.I)


def parse_export(text: str) -> list[dict]:
    """Threads (`## title` under `# #channel`) and, for channels without threads, calendar weeks."""

    items, channel, cur = [], None, None
    days: list[tuple[str, str]] = []

    def close():
        nonlocal cur
        if cur:
            cur["body"] = "\n".join(cur.pop("lines")).strip()
            items.append(cur)
        cur = None

    for line in text.splitlines():
        if line.startswith("# #"):
            close()
            channel = line[3:].split(" (")[0].strip()
            days = []
        elif line.startswith("## ") and channel:
            close()
            cur = {"channel": channel, "title": line[3:].strip(), "period": "", "lines": []}
        elif line.startswith("### ") and channel and re.match(r"### \d{4}-\d{2}-\d{2}$", line):
            day = line[4:].strip()
            iso = datetime.fromisoformat(day).isocalendar()
            key = f"{iso[0]}-W{iso[1]:02d}"
            if not cur or cur.get("week") != key:
                close()
                cur = {"channel": channel, "title": f"Week {key}", "week": key, "period": day, "lines": []}
        elif cur is not None:
            m = re.match(r"Thread: \S+ \(erstellt (\d{4}-\d{2}-\d{2})", line)
            if m and not cur["period"]:
                cur["period"] = m.group(1)
            cur["lines"].append(line)
    close()
    out = []
    for i in items:
        m = re.search(r"^Thread: (https://discord\.com/channels/\S+)", i["body"], flags=re.M)
        i["url"] = m.group(1) if m else CHANNEL_LINKS.get(i["channel"])
        i["body"] = re.sub(r"^Thread: \S+.*\n?", "", i["body"], flags=re.M).strip()
        if not i["body"]:
            continue
        if "week" in i:  # a channel without threads: split long weeks at message boundaries
            parts = _chunks(i["body"])
            for n, part in enumerate(parts, 1):
                out.append({**i, "title": i["title"] + (f" (part {n} of {len(parts)})" if len(parts) > 1 else ""), "body": part})
        else:
            out.append(i)
    return out


def _chunks(body: str, size: int = 14000) -> list[str]:
    parts, cur = [], ""
    for block in re.split(r"\n\n(?=\*\*)", body):
        if cur and len(cur) + len(block) > size:
            parts.append(cur)
            cur = ""
        cur += ("\n\n" if cur else "") + block
    return parts + [cur] if cur else parts


_FIRST_NAMES = {"abner", "albin", "amir", "anna", "chris", "diego", "george", "giovanni", "jack", "jason", "jay",
                "johannes", "joseph", "jude", "lee", "louis", "marco", "nathaniel", "noah", "pablo", "paul", "seth",
                "stewart", "tom", "tyler", "victoria", "yao", "adam", "david", "han", "jeff", "monte", "nick", "sean",
                "steve"}


def _dictionary() -> set[str]:
    p = Path("/usr/share/dict/words")
    return {w.strip().lower() for w in p.read_text(errors="ignore").splitlines()} if p.exists() else set()


def author_names(text: str) -> set[str]:
    """Display names in full, plus their parts when a part is not an ordinary word (handles such as
    "Scroll" or "Lab" would otherwise be erased from the prose) or is a common first name."""

    common = _dictionary()
    names = set()
    for a in _AUTHOR.findall(text):
        names.add(a.strip())
        for t in re.findall(r"[\w.-]+", a):
            if len(t) >= 3 and (t.lower() not in common or t.lower() in _FIRST_NAMES):
                names.add(t)
    return names


def anonymise(body: str, names: set[str]) -> str:
    """Authors -> P1, P2 (per discussion); other mentions of known names and @handles -> 'a participant'."""

    labels: dict[str, str] = {}

    def label(m):
        n = m.group(1).strip()
        return f"**{labels.setdefault(n, f'P{len(labels) + 1}')}** · "

    body = _AUTHOR.sub(label, body)
    body = re.sub(r"@\w[\w.-]*", "a participant", body)
    for n in sorted(names, key=len, reverse=True):
        body = re.sub(rf"(?<!\w){re.escape(n)}(?!\w)", "a participant", body, flags=re.I)
    return re.sub(r"\ba participant(?: a participant)+", "a participant", body)


def link_label(url: str) -> str:
    """Short, readable label: github.com/org/repo, huggingface.co/org/name, arXiv:id, doi:..."""

    u = re.sub(r"^https?://(?:www\.)?", "", url).split("#")[0].split("?")[0].rstrip("/")
    host, _, path = u.partition("/")
    if host == "arxiv.org":
        return "arXiv:" + path.split("/")[-1]
    if host == "doi.org":
        return "doi:" + path
    parts = path.split("/")
    if host in ("github.com", "gitlab.com"):
        return "/".join([host] + parts[:2])
    if host == "huggingface.co":
        return "/".join([host] + (parts[:3] if parts and parts[0] in ("datasets", "spaces") else parts[:2]))
    return host + ("/" + "/".join(parts[:2]) if path else "")


def labelled(urls: list[str]) -> list[dict]:
    return [{"url": u, "label": link_label(u)} for u in urls]


def repo_links(body: str, limit: int = 4) -> list[str]:
    seen: list[str] = []
    for u in _URL.findall(body):
        u = u.rstrip(".,;:)")
        if _REPO_HOST.match(u) and not _NOT_A_REPO.search(u) and "opengraph" not in u and u not in seen:
            seen.append(u)
    return seen[:limit]


def _clip(body: str, head: int = 8000, tail: int = 6000) -> str:
    return body if len(body) <= head + tail else body[:head] + "\n[...]\n" + body[-tail:]


def scrub(text: str, names: set[str]) -> str:
    """Names in the model's prose -> 'a participant'; P-labels removed."""

    for n in sorted(names, key=len, reverse=True):
        text = re.sub(rf"(?<!\w){re.escape(n)}(?!\w)", "a participant", text, flags=re.I)
    return re.sub(r"\bP\d{1,2}\b", "a participant", text)


def summarise_item(item: dict, names: set[str], ask) -> dict | None:
    """One discussion -> title, summary, topic, relevance, repo links; None if the model fails twice or keeps
    repeating the source (one retry asks for different wording)."""

    system, template = load_prompt(SNAPSHOT_PROMPT)
    body = _clip(anonymise(item["body"], names))
    user = template.format(channel=item["channel"], title=scrub(item["title"], names), period=item["period"], body=body)
    note = ""
    for _ in range(2):
        try:
            d = parse_json_object(ask(system, user + note), "summary")
        except Exception:  # no usable JSON
            continue
        title, summary = scrub(str(d.get("title", "")).strip(), names), scrub(str(d.get("summary", "")).strip(), names)
        if summary and not copies_source(f"{title} {summary}", [item["body"]]):
            topic = d.get("topic") if d.get("topic") in TOPICS else "other"
            rel = d.get("relevance") if d.get("relevance") in (0, 1, 2, 3) else 0
            return {"channel": item["channel"], "date": item["period"], "title": title, "summary": summary,
                    "topic": topic, "relevance": rel, "links": labelled(repo_links(item["body"])), "discord": item.get("url")}
        note = ("\n\nYour previous answer repeated passages of the text. Write the summary again in your own "
                "words, with different sentence structure and no copied phrases; numbers may stay.")
    return None


def _fallback(item: dict, names: set[str]) -> dict:
    """Discussion the model could not summarise: kept in the link directory under its (scrubbed) title."""

    return {"channel": item["channel"], "date": item["period"], "title": scrub(item["title"], names), "summary": "",
            "topic": "other", "relevance": 1, "links": labelled(repo_links(item["body"], limit=99)), "discord": item.get("url"),
            "unsummarised": True}


def build_snapshot(items: list[dict], names: set[str], ask, workers: int = 6, per_topic: int = 25, min_relevance: int = 2,
                   meta: dict | None = None) -> dict:
    """Highlights (summary, relevance >= min_relevance, at most per_topic per topic) and a link directory
    (every code, data and paper link of every discussion that is not chat, grouped by topic)."""

    from concurrent.futures import ThreadPoolExecutor

    def one(item):
        r = summarise_item(item, names, ask)
        if r is None:
            return _fallback(item, names)
        r["links_all"] = labelled(repo_links(item["body"], limit=99))
        return r

    with ThreadPoolExecutor(workers) as ex:
        done = list(ex.map(one, items))
    topics, directory = [], []
    for tid, label in TOPICS.items():
        pool = [r for r in done if r["topic"] == tid]
        sel = sorted((r for r in pool if r["summary"] and r["relevance"] >= min_relevance),
                     key=lambda r: (r["relevance"], r["date"]), reverse=True)[:per_topic]
        if sel:
            topics.append({"id": tid, "label": label, "items": [
                {k: v for k, v in r.items() if k not in ("topic", "links_all", "unsummarised")} for r in sel]})
        entries = [{"title": r["title"], "date": r["date"], "links": r.get("links_all") or r["links"], "discord": r.get("discord")}
                   for r in sorted(pool, key=lambda r: r["date"], reverse=True)
                   if (r.get("links_all") or r["links"]) and (r["relevance"] >= 1 or r.get("unsummarised"))]
        if entries:
            directory.append({"id": tid, "label": label, "items": entries})
    n_links = len({l["url"] for d in directory for e in d["items"] for l in e["links"]})
    return {**(meta or {}), "n_discussions": len(items), "n_summarised": sum(not r.get("unsummarised") for r in done),
            "n_selected": sum(len(t["items"]) for t in topics), "n_links": n_links, "topics": topics, "directory": directory}


def run_snapshot(export: Path, limit: int | None = None, dry_run: bool = False, ask=None) -> dict:
    text = export.read_text(encoding="utf-8")
    items = parse_export(text)
    if limit:
        items = items[:limit]
    names = author_names(text)
    if ask is None:
        client = client_for(PANEL["R1"])
        ask = lambda system, user: chat(client, system, user, max_tokens=4096).content
    days = sorted(re.findall(r"\b(20\d\d-\d\d-\d\d)\b", " ".join(i["period"] for i in items)))
    meta = {"snapshot": datetime.now(timezone.utc).date().isoformat(), "period_start": days[0] if days else "",
            "period_end": days[-1] if days else ""}
    snap = build_snapshot(items, names, ask, meta=meta)
    if not dry_run:
        SNAPSHOT_OUT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_OUT.write_text(yaml.safe_dump(snap, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
    return {k: v for k, v in snap.items() if k not in ("topics", "directory")} | {"topics": {t["id"]: len(t["items"]) for t in snap["topics"]}}
