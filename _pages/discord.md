---
layout: page
title: "Discord highlights"
permalink: /discord/
---

A weekly digest of the Vesuvius Challenge announcements, written by a language model from the
announcements channel and reviewed before it is published. It names no people, quotes no
messages, and links only to papers, code, data and web pages. Treat items marked "announced" as
claims, not results.

{% assign snap = site.data.discord_snapshot %}
{% if snap and snap.topics %}
## Snapshot of {{ snap.snapshot }}

Discussions from {{ snap.period_start }} to {{ snap.period_end }} in four channels (show-and-tell, ink-detection,
robots, unrolling-vc3d): {{ snap.n_discussions }} discussions read, {{ snap.n_selected }} listed here,
grouped by topic and ordered by relevance to unwrapping, ink detection and reading. Links go to the code,
data and papers named in the discussions, and to the Discord thread (readable for members of the server).

{% for t in snap.topics %}
### {{ t.label }}

{% for h in t.items %}
- **{{ h.title }}.** {{ h.summary }}{% for l in h.links %} [{{ l.label }}]({{ l.url }}){% unless forloop.last %},{% endunless %}{% endfor %}{% if h.discord %} · [Discord thread]({{ h.discord }}){% endif %} <small>({{ h.date }}, #{{ h.channel }})</small>
{% endfor %}
{% endfor %}

### Link directory

{{ snap.n_links }} links to code, data and papers named in the discussions, by topic and newest first.

{% for d in snap.directory %}
#### {{ d.label }}

{% for e in d.items %}
- {{ e.title }}: {% for l in e.links %}[{{ l.label }}]({{ l.url }}){% unless forloop.last %}, {% endunless %}{% endfor %}{% if e.discord %} · [Discord thread]({{ e.discord }}){% endif %} <small>({{ e.date }})</small>
{% endfor %}
{% endfor %}

## Weekly digests
{% endif %}

{% if site.data.discord_highlights and site.data.discord_highlights.size > 0 %}
{% for week in site.data.discord_highlights %}
## Week of {{ week.week_start }} to {{ week.week_end }}

{{ week.summary }}

{% for h in week.highlights %}
- **{{ h.title }}.** {{ h.summary }}{% for u in h.links %} [link]({{ u }}){% endfor %}
{% endfor %}

<small>{{ week.n_messages }} messages screened.</small>
{% endfor %}
{% else %}
No digest yet. The first one appears after the weekly run is set up (see the README).
{% endif %}
