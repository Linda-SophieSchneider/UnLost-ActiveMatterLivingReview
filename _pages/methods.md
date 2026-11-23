---
layout: page
title: "Methods"
permalink: /methods/
---

The protocol, eligibility criteria, and per-database search
strings live under [`protocol/`](https://github.com/Linda-SophieSchneider/UnLost-ActiveMatterLivingReview/tree/main/protocol)
in the repository. The protocol is a draft until it is frozen and has not been registered.

## Databases queried

{% for s in site.data.sources %}
- **{{ s.name }}** — {{ s.endpoint }} (last run: {{ s.last_run | default: "pending" }})
{% endfor %}

## Eligibility criteria

See [`protocol/PICO.md`](https://github.com/Linda-SophieSchneider/UnLost-ActiveMatterLivingReview/blob/main/protocol/PICO.md).

## PRISMA 2020 checklist

The 27-item checklist, with per-item anchors into the repository, lives
at [`protocol/prisma_checklist.md`](https://github.com/Linda-SophieSchneider/UnLost-ActiveMatterLivingReview/blob/main/protocol/prisma_checklist.md).
