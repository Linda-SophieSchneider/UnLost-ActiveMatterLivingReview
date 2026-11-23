---
layout: page
title: "Discord highlights"
permalink: /discord/
---

A weekly digest of the Vesuvius Challenge announcements, written by a language model from the
announcements channel and reviewed before it is published. It names no people, quotes no
messages, and links only to papers, code, data and web pages. Treat items marked "announced" as
claims, not results.

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
