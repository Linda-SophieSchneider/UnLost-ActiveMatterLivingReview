/* Human check: click-through validation and adjudication queue (see /check/).
 * Labels live in localStorage and leave the browser only through Export (a JSON download),
 * which `amlr human-import` reads. Format: amlr-human-check/1. */
(function () {
  "use strict";

  var root = document.getElementById("hc");
  if (!root) return;
  var STORE = "amlr-human-check-v1";

  var QUEUES = [
    { id: "ta_sample", label: "Title/abstract sample", blind: true, stage: "title/abstract" },
    { id: "ft_split", label: "Full-text splits", blind: false, stage: "full text" },
    { id: "extraction", label: "Extraction conflicts", blind: false },
    { id: "seeds", label: "Seed papers", blind: false }
  ];
  var CODES = [
    ["E5", "Not primary research (review, editorial, perspective, duplicate thesis)"],
    ["E4", "No results (protocol, announcement, news, exhibition text, abstract without results)"],
    ["E1", "Object not in scope: not a papyrus, not Herculaneum, not a document studied for unwrapping"],
    ["E3", "Generic method, no experiment on papyri or unwrapping objects"],
    ["E2", "Papyrus outside the topics and not Herculaneum (interpretation, edition, chemistry)"]
  ];
  var CODE_TEXT = {};
  CODES.forEach(function (c) { CODE_TEXT[c[0]] = c[1]; });
  var INCLUSION = [
    "I1 Papyrus (above all Herculaneum), or a rolled, folded, sealed or damaged document studied for unwrapping, or a phantom of one",
    "I2 Topic: unwrapping/flattening, ink or hidden-text imaging, reading characters, writers and scripts, restoration/assembly, or any study of Herculaneum papyri",
    "I3 Reports results: evaluated method, measurements, dataset, or Herculaneum edition",
    "I4 Primary research article, conference paper with results, preprint or dataset paper",
    "I5 Title and abstract in English, German, Italian or French"
  ];
  var FIELD_HELP = {
    object_class: "Object class",
    primary_task: "Primary task",
    method_family: "Method family",
    validation: "Validation",
    n_objects: "Number of physical objects studied",
    n_scans: "Number of scans, images or measurements",
    n_annotated_samples: "Annotated or ground-truth samples",
    resolution_um: "Voxel or pixel size (µm)",
    "rob.D1_ground_truth": "Risk of bias D1 · ground truth",
    "rob.D2_sample_representativeness": "Risk of bias D2 · sample representativeness",
    "rob.D3_acquisition_documentation": "Risk of bias D3 · acquisition documentation",
    "rob.D4_evaluation_validity": "Risk of bias D4 · evaluation validity",
    "rob.D5_data_code_availability": "Risk of bias D5 · data and code availability",
    "rob.D6_expert_validation": "Risk of bias D6 · expert validation"
  };

  var data = null;
  var storageOk = true;
  var state = load();
  state.labels = state.labels || {};
  state.notes = state.notes || {};
  state.peek = state.peek || {};
  state.pos = state.pos || {};
  state.tab = state.tab || "ta_sample";
  state.filter = state.filter || "all";

  function load() {
    try {
      return JSON.parse(window.localStorage.getItem(STORE)) || {};
    } catch (e) {
      storageOk = false;
      return {};
    }
  }
  function save() {
    try {
      window.localStorage.setItem(STORE, JSON.stringify(state));
    } catch (e) {
      storageOk = false;
    }
  }
  function esc(s) {
    return String(s === null || s === undefined ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function strip(s) {
    return String(s || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  }
  function human(v) {
    if (v === null || v === undefined || v === "") return "not reported";
    if (v === true) return "yes";
    if (v === false) return "no";
    if (Array.isArray(v)) return v.length ? v.map(human).join(", ") : "none";
    return String(v).replace(/_/g, " ");
  }
  function key(q, id, field) {
    return q + "|" + id + (field ? "|" + field : "");
  }
  function queue() {
    return QUEUES.filter(function (q) { return q.id === state.tab; })[0] || QUEUES[0];
  }
  function items(qid) {
    return (data && data.queues[qid]) || [];
  }
  function done(qid, it) {
    if (qid === "extraction") {
      return it.fields.every(function (f) { return state.labels[key(qid, it.id, f.field)]; });
    }
    return !!state.labels[key(qid, it.id)];
  }
  function disagrees(qid, it) {
    var l = state.labels[key(qid, it.id)];
    return !!(l && it.panel && l.include !== null && l.include !== it.panel.include);
  }
  function matches(qid, it) {
    var d = done(qid, it);
    if (state.filter === "open") return !d;
    if (state.filter === "done") return d;
    if (state.filter === "disagree") return d && disagrees(qid, it);
    return true;
  }
  function counts(qid) {
    var all = items(qid);
    var n = all.filter(function (it) { return done(qid, it); }).length;
    return { done: n, total: all.length };
  }
  function cursor(qid) {
    var n = items(qid).length;
    var i = state.pos[qid] || 0;
    return Math.max(0, Math.min(i, n - 1));
  }
  function step(dir, openOnly) {
    var q = queue().id;
    var all = items(q);
    var i = cursor(q);
    for (var j = i + dir; j >= 0 && j < all.length; j += dir) {
      if (openOnly ? !done(q, all[j]) : matches(q, all[j])) {
        state.pos[q] = j;
        save();
        render();
        toTop();
        return;
      }
    }
    flash(openOnly ? "No open item after this one." : dir > 0 ? "This is the last item." : "This is the first item.");
  }
  function toTop() {
    var y = root.getBoundingClientRect().top + window.pageYOffset - 12;
    if (window.pageYOffset > y) window.scrollTo({ top: y, behavior: "smooth" });
  }
  function changedSinceExport() {
    var since = (state.lastExport && state.lastExport.at) || "";
    return Object.keys(state.labels).filter(function (k) { return (state.labels[k].at || "") > since; }).length;
  }

  // ---- actions ---------------------------------------------------------------------------
  function decide(it, include, reason) {
    var q = queue();
    var k = key(q.id, it.id);
    var prev = state.labels[k];
    // In a blind queue the votes appear after the first decision, so any revision has seen them.
    var label = {
      queue: q.id, record_id: it.id, include: include, reason: include === false ? reason : null,
      saw_panel: !q.blind || !!state.peek[k] || !!prev, at: new Date().toISOString()
    };
    if (q.blind) {
      // The first blind answer is kept when a decision is revised after the votes were revealed.
      label.blind = prev ? prev.blind || null : state.peek[k] ? null : { include: include, reason: label.reason };
    }
    if (q.id === "seeds") label.stage = it.stage;
    state.labels[k] = label;
    save();
    if (state.auto && !q.blind) step(1, true);
    else render();
  }
  function choose(it, field, value, by) {
    state.labels[key("extraction", it.id, field)] = {
      queue: "extraction", record_id: it.id, field: field, value: value, chosen_from: by,
      at: new Date().toISOString()
    };
    save();
    if (state.auto && done("extraction", it)) step(1, true);
    else render();
  }
  function clearLabel(k) {
    delete state.labels[k];
    save();
    render();
  }
  function exportLabels() {
    var labels = Object.keys(state.labels).map(function (k) {
      var l = Object.assign({}, state.labels[k]);
      var base = k.split("|").slice(0, 2).join("|");
      l.note = state.notes[k] || state.notes[base] || "";
      return l;
    });
    var payload = {
      format: data.format, queue_sha256: data.queue_sha256, queue_built_at: data.built_at,
      exported_at: new Date().toISOString(), reviewer: "author", labels: labels
    };
    var stamp = new Date().toISOString().slice(0, 16).replace(/[-:]/g, "").replace("T", "-");
    var blob = new Blob([JSON.stringify(payload, null, 1)], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "human-check-" + stamp + ".json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 5000);
    state.lastExport = { at: new Date().toISOString(), n: labels.length, file: a.download };
    save();
    render();
  }
  function importLabels(file) {
    var reader = new FileReader();
    reader.onload = function () {
      var got;
      try {
        got = JSON.parse(reader.result);
      } catch (e) {
        flash("That file is not JSON.");
        return;
      }
      if (!got || got.format !== data.format || !Array.isArray(got.labels)) {
        flash("That file is not a human-check export.");
        return;
      }
      var n = 0;
      got.labels.forEach(function (l) {
        if (!l.queue || !l.record_id) return;
        var k = key(l.queue, l.record_id, l.field);
        var cur = state.labels[k];
        if (!cur || (l.at || "") > (cur.at || "")) {
          var copy = Object.assign({}, l);
          if (copy.note) state.notes[k] = copy.note;
          delete copy.note;
          state.labels[k] = copy;
          n += 1;
        }
      });
      save();
      render();
      flash(n + " labels restored.");
    };
    reader.readAsText(file);
  }

  // ---- rendering -------------------------------------------------------------------------
  var flashTimer = null;
  function flash(msg) {
    var el = root.querySelector(".hc-flash");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("on");
    clearTimeout(flashTimer);
    flashTimer = setTimeout(function () { el.classList.remove("on"); }, 2600);
  }

  function chip(include, reason) {
    if (include === null || include === undefined) return '<span class="hc-chip mid">unsure</span>';
    return include ? '<span class="hc-chip ok">Include</span>'
      : '<span class="hc-chip no" title="' + esc(CODE_TEXT[reason] || "") + '">Exclude' + (reason ? " · " + esc(reason) : "") + "</span>";
  }

  var CHECK = { verbatim: ["ok", "found in text"], close: ["mid", "nearly verbatim"], partial: ["mid", "partly in text"], not_found: ["no", "not found in text"] };
  function evidenceHtml(ev, original) {
    if (!ev) return "";
    var out = '<div class="hc-ev">';
    if (ev.decision !== undefined && original) {
      var now = ev.decision === "include" ? true : ev.decision === "exclude" ? false : null;
      if (now !== null && (now !== original.include || (!now && ev.reason && ev.reason !== original.reason))) {
        out += '<p class="hc-ev-rev">On re-reading: ' + chip(now, ev.reason) + "</p>";
      }
    }
    if (ev.claim) out += '<p class="hc-ev-claim">' + esc(ev.claim) + "</p>";
    var items = ev.evidence || [];
    if (!items.length) out += '<p class="hc-muted hc-ev-none">No supporting passage quoted.</p>';
    else out += "<ul>" + items.map(function (e) {
      var c = CHECK[e.check] || CHECK.not_found;
      return "<li>" + (e.criterion ? "<strong>" + esc(e.criterion) + "</strong> " : "") + "“" + esc(e.quote) + "” " +
        '<span class="hc-chip ' + c[0] + '" title="Automatic check of the quote against the full text">' + c[1] + "</span></li>";
    }).join("") + "</ul>";
    return out + "</div>";
  }

  function panelHtml(p, title) {
    if (!p) return '<p class="hc-muted">No panel decision recorded.</p>';
    var rows = (p.reviewers || []).map(function (v) {
      return '<tr><th scope="row">' + esc(v.r) + '<small>' + esc(v.model || "") + "</small></th><td>" +
        chip(v.include, v.reason) + (v.confidence !== null && v.confidence !== undefined
          ? '<small class="hc-conf">' + Math.round(v.confidence * 100) + "%</small>" : "") +
        "</td><td>" + esc(v.rationale || "") + evidenceHtml(v.evidence, v) + "</td></tr>";
    }).join("");
    return '<div class="hc-panel"><div class="hc-panel-head"><strong>' + esc(title) + "</strong> " +
      chip(p.include, p.reason) + ' <small class="hc-muted">' + esc(p.votes || "") + " include votes</small></div>" +
      '<table class="hc-votes"><tbody>' + rows + "</tbody></table></div>";
  }

  function headerHtml(it) {
    var badges = [];
    if (it.abstract_only) badges.push('<span class="hc-badge">assessed on abstract only</span>');
    if (it.phase) badges.push('<span class="hc-badge subtle">' + esc(human(it.phase)) + "</span>");
    var title = it.link ? '<a href="' + esc(it.link) + '" target="_blank" rel="noopener">' + esc(strip(it.title)) + "</a>"
      : esc(strip(it.title));
    return '<h2 class="hc-title">' + title + "</h2>" +
      '<p class="hc-meta">' + esc(it.authors) + (it.venue ? " · <em>" + esc(it.venue) + "</em>" : "") +
      (it.year ? " · " + esc(it.year) : "") + '</p><p class="hc-meta"><code>' + esc(it.id) + "</code> " +
      badges.join(" ") + (it.link ? ' · <a class="hc-open" href="' + esc(it.link) + '" target="_blank" rel="noopener">Open paper ↗</a>' : "") + "</p>";
  }

  function abstractHtml(it) {
    var a = strip(it.abstract);
    return a ? '<div class="hc-abstract">' + esc(a) + "</div>"
      : '<p class="hc-muted hc-abstract-none">No abstract in the metadata. Open the paper via the title link.</p>';
  }

  function screeningHtml(q, it) {
    var k = key(q.id, it.id);
    var l = state.labels[k];
    var reveal = !q.blind || !!l || !!state.peek[k];
    var btns = '<button type="button" class="hc-btn ok' + (l && l.include === true ? " on" : "") +
      '" data-act="inc" title="Include (I)">Include <kbd>I</kbd></button>';
    CODES.forEach(function (c) {
      var on = l && l.include === false && l.reason === c[0];
      btns += '<button type="button" class="hc-btn no' + (on ? " on" : "") + '" data-act="exc" data-code="' + c[0] +
        '" title="' + esc(c[1]) + '">' + c[0] + " <kbd>" + c[0].slice(1) + "</kbd></button>";
    });
    btns += '<button type="button" class="hc-btn mid' + (l && l.include === null ? " on" : "") +
      '" data-act="unsure" title="Unsure (U): kept, not applied">Unsure <kbd>U</kbd></button>';

    var stage = q.id === "seeds" ? (it.stage === "full_text" ? "full text" : "title/abstract") : q.stage;
    var out = headerHtml(it) + abstractHtml(it);
    out += '<div class="hc-decide"><div class="hc-decide-head">Your decision at ' + esc(stage) +
      (l ? " " + chip(l.include, l.reason) + ' <button type="button" class="hc-link" data-act="clear">clear</button>' : "") +
      '</div><div class="hc-btns">' + btns + "</div>" +
      '<label class="hc-note">Note <textarea rows="2" data-act="note" placeholder="Optional: why, or what to check">' +
      esc(state.notes[k] || "") + "</textarea></label></div>";

    if (reveal) {
      if (l && it.panel && l.include !== null) {
        out += l.include === it.panel.include
          ? '<p class="hc-verdict ok">You agree with the panel.</p>'
          : '<p class="hc-verdict no">You disagree with the panel. Your decision is the one applied' +
            (q.id === "ta_sample" && !l.include ? " if the record is later screened again; a full-text decision supersedes it." : ".") + "</p>";
      }
      out += panelHtml(it.panel, "Panel decision at " + stage);
      if (it.panel_ta) out += '<details class="hc-more"><summary>Title/abstract votes</summary>' + panelHtml(it.panel_ta, "Panel at title/abstract") + "</details>";
    } else {
      out += '<div class="hc-hidden">Panel votes are hidden until you decide, so this label stays independent. ' +
        '<button type="button" class="hc-link" data-act="peek">Show them now <kbd>V</kbd></button></div>';
    }
    return out;
  }

  function valueInput(f, cur) {
    var v = cur ? cur.value : undefined;
    if (f.vocab) {
      var opts = '<option value="">choose…</option>' + f.vocab.map(function (x, i) {
        return '<option value="' + i + '"' + (cur && cur.chosen_from === "author" && v === x ? " selected" : "") + ">" + esc(human(x)) + "</option>";
      }).join("");
      return '<select data-act="own-select">' + opts + "</select>";
    }
    return '<input type="number" min="0" step="any" inputmode="decimal" data-act="own-number" placeholder="value" value="' +
      (cur && cur.chosen_from === "author" && v !== null && v !== undefined ? esc(v) : "") + '">' +
      ' <button type="button" class="hc-btn subtle" data-act="own-number-set">Set</button>';
  }

  function extractionHtml(it) {
    var out = headerHtml(it);
    out += abstractHtml(it);
    var c = it.context || {};
    out += '<dl class="hc-context">' +
      "<dt>Object</dt><dd>" + esc(human(c.object_class)) + (c.object_name ? " · " + esc(c.object_name) : "") + "</dd>" +
      "<dt>Objects / scans</dt><dd>" + esc(human(c.n_objects)) + " / " + esc(human(c.n_scans)) + "</dd>" +
      "<dt>Task · method</dt><dd>" + esc(human(c.primary_task)) + " · " + esc(human(c.method_family)) + "</dd>" +
      "<dt>Outputs</dt><dd>" + esc(human(c.outputs)) + "</dd>" +
      "<dt>Origin · validation</dt><dd>" + esc(human(c.corpus_origin)) + " · " + esc(human(c.validation)) + "</dd>" +
      "<dt>Instrument</dt><dd>" + esc(c.instrument || "not reported") + "</dd>" +
      "<dt>Notes (R1)</dt><dd>" + esc(c.notes || "") + "</dd>" +
      "<dt>Notes (R3)</dt><dd>" + esc(c.notes_alt || "") + "</dd></dl>";
    it.fields.forEach(function (f, fi) {
      var k = key("extraction", it.id, f.field);
      var cur = state.labels[k];
      var opts = f.options.map(function (o, oi) {
        var on = cur && cur.chosen_from === o.by && JSON.stringify(cur.value) === JSON.stringify(o.value);
        return '<button type="button" class="hc-opt' + (on ? " on" : "") + '" data-act="pick" data-field="' + fi + '" data-opt="' + oi + '">' +
          '<small>' + esc(o.by) + "</small>" + esc(human(o.value)) + "</button>";
      }).join("");
      var evs = f.options.filter(function (o) { return o.evidence; }).map(function (o) {
        return '<div class="hc-ev-by"><strong>' + esc(o.by) + "</strong> argues for " + esc(human(o.evidence.value)) +
          evidenceHtml(o.evidence) + "</div>";
      }).join("");
      var nullOn = cur && cur.chosen_from === "author" && cur.value === null;
      out += '<fieldset class="hc-field" data-field="' + fi + '"><legend>' + esc(FIELD_HELP[f.field] || human(f.field)) +
        " <code>" + esc(f.field) + "</code>" + (cur ? ' <span class="hc-chip ok">set</span> <button type="button" class="hc-link" data-act="clear-field" data-field="' + fi + '">clear</button>' : "") +
        '</legend><div class="hc-opts">' + opts +
        '<button type="button" class="hc-opt' + (nullOn ? " on" : "") + '" data-act="pick-null" data-field="' + fi + '"><small>you</small>not reported</button></div>' +
        (evs ? '<div class="hc-evs">' + evs + "</div>" : '<p class="hc-muted">Evidence from the models is not in yet.</p>') +
        '<div class="hc-own">Your own value: ' + valueInput(f, cur) + "</div></fieldset>";
    });
    return out;
  }

  function render() {
    if (!data) return;
    var q = queue();
    var all = items(q.id);
    var i = cursor(q.id);
    var it = all[i];
    var tabs = QUEUES.map(function (x) {
      var c = counts(x.id);
      var pct = c.total ? Math.round((100 * c.done) / c.total) : 0;
      return '<button type="button" role="tab" class="hc-tab" aria-selected="' + (x.id === q.id) + '" data-tab="' + x.id + '">' +
        esc(x.label) + '<span class="n">' + c.done + "/" + c.total + '</span><span class="hc-bar"><i style="width:' + pct + '%"></i></span></button>';
    }).join("");
    var pending = changedSinceExport();
    var exp = state.lastExport ? "Last export " + new Date(state.lastExport.at).toLocaleString() + " (" + esc(state.lastExport.file) + ")"
      : "Not exported yet";
    var filters = [["all", "All"], ["open", "Open"], ["done", "Done"]];
    if (q.id !== "extraction") filters.push(["disagree", "Disagree with panel"]);
    if (!filters.some(function (f) { return f[0] === state.filter; })) state.filter = "all";
    var shown = all.filter(function (x) { return matches(q.id, x); }).length;

    var html = '<div class="hc-top"><div class="hc-tabs" role="tablist">' + tabs + "</div>" +
      '<div class="hc-tools"><button type="button" class="hc-btn primary' + (pending ? " attention" : "") + '" data-act="export">Export labels' +
      (pending ? " (" + pending + " new)" : "") + '</button><label class="hc-btn subtle hc-file">Import<input type="file" accept="application/json,.json" data-act="import"></label>' +
      '<button type="button" class="hc-link" data-act="reset">Clear all</button><span class="hc-muted hc-exp">' + exp + "</span></div></div>";
    if (!storageOk) html += '<p class="hc-warn">This browser is not keeping data for this page (private window or blocked storage). Export before you close it.</p>';
    html += '<details class="hc-criteria"><summary>Eligibility criteria</summary><ul>' +
      INCLUSION.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("") + "</ul><p>Exclusion, in order of precedence:</p><ul>" +
      CODES.map(function (c) { return "<li><strong>" + c[0] + "</strong> " + esc(c[1]) + "</li>"; }).join("") + "</ul></details>";
    html += '<div class="hc-nav"><button type="button" class="hc-btn subtle" data-act="prev">‹ Prev</button>' +
      '<span class="hc-pos">' + (all.length ? i + 1 : 0) + " / " + all.length + "</span>" +
      '<button type="button" class="hc-btn subtle" data-act="next">Next ›</button>' +
      '<button type="button" class="hc-btn subtle" data-act="next-open">Next open <kbd>N</kbd></button>' +
      '<label class="hc-filter">Show <select data-act="filter">' + filters.map(function (f) {
        return '<option value="' + f[0] + '"' + (f[0] === state.filter ? " selected" : "") + ">" + f[1] + "</option>";
      }).join("") + "</select> <small>(" + shown + ")</small></label>" +
      (q.blind ? "" : '<label class="hc-auto"><input type="checkbox" data-act="auto"' + (state.auto ? " checked" : "") + "> advance after deciding</label>") +
      "</div>";
    html += '<article class="hc-card">' + (it ? (q.id === "extraction" ? extractionHtml(it) : screeningHtml(q, it)) : '<p class="hc-muted">This queue is empty.</p>') + "</article>";
    html += '<div class="hc-flash" role="status" aria-live="polite"></div>';
    root.innerHTML = html;
    bind(q, it);
  }

  function bind(q, it) {
    root.querySelectorAll("[data-tab]").forEach(function (b) {
      b.addEventListener("click", function () { state.tab = b.getAttribute("data-tab"); save(); render(); toTop(); });
    });
    root.querySelectorAll("[data-act]").forEach(function (el) {
      var act = el.getAttribute("data-act");
      var fi = el.getAttribute("data-field");
      var f = it && it.fields && fi !== null ? it.fields[+fi] : null;
      if (act === "note") {
        el.addEventListener("input", function () { state.notes[key(q.id, it.id)] = el.value; save(); });
        return;
      }
      if (act === "import") {
        el.addEventListener("change", function () { if (el.files[0]) importLabels(el.files[0]); });
        return;
      }
      if (act === "filter") {
        el.addEventListener("change", function () { state.filter = el.value; save(); render(); });
        return;
      }
      if (act === "auto") {
        el.addEventListener("change", function () { state.auto = el.checked; save(); });
        return;
      }
      if (act === "own-select") {
        el.addEventListener("change", function () {
          if (el.value !== "") choose(it, f.field, f.vocab[+el.value], "author");
        });
        return;
      }
      el.addEventListener("click", function () {
        switch (act) {
          case "inc": decide(it, true, null); break;
          case "exc": decide(it, false, el.getAttribute("data-code")); break;
          case "unsure": decide(it, null, null); break;
          case "clear": clearLabel(key(q.id, it.id)); break;
          case "clear-field": clearLabel(key("extraction", it.id, f.field)); break;
          case "peek": state.peek[key(q.id, it.id)] = true; save(); render(); break;
          case "pick": var o = f.options[+el.getAttribute("data-opt")]; choose(it, f.field, o.value, o.by); break;
          case "pick-null": choose(it, f.field, null, "author"); break;
          case "own-number-set":
            var inp = el.parentNode.querySelector("input");
            var n = parseFloat(inp.value);
            if (isNaN(n)) { flash("Enter a number first."); break; }
            choose(it, f.field, f.kind === "count" ? Math.round(n) : n, "author");
            break;
          case "prev": step(-1, false); break;
          case "next": step(1, false); break;
          case "next-open": step(1, true); break;
          case "export": exportLabels(); break;
          case "reset":
            if (window.confirm("Delete all labels stored in this browser? Export first if you want to keep them.")) {
              state.labels = {}; state.notes = {}; state.peek = {}; state.lastExport = null; save(); render();
            }
            break;
        }
      });
    });
  }

  document.addEventListener("keydown", function (e) {
    if (!data || e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target && e.target.tagName;
    if (t === "INPUT" || t === "TEXTAREA" || t === "SELECT") return;
    var q = queue();
    var it = items(q.id)[cursor(q.id)];
    if (!it) return;
    var k = e.key;
    if (k === "ArrowRight") { step(1, false); e.preventDefault(); return; }
    if (k === "ArrowLeft") { step(-1, false); e.preventDefault(); return; }
    if (k === "n" || k === "N") { step(1, true); return; }
    if (q.id === "extraction") return;
    if (k === "i" || k === "I") decide(it, true, null);
    else if (k === "u" || k === "U") decide(it, null, null);
    else if (k === "v" || k === "V") { state.peek[key(q.id, it.id)] = true; save(); render(); }
    else if (/^[1-6]$/.test(k)) decide(it, false, "E" + k);
  });

  fetch(root.getAttribute("data-queue"), { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function (d) {
      data = d;
      render();
    })
    .catch(function (e) {
      root.innerHTML = '<p class="hc-warn">The queue could not be loaded (' + esc(e.message) + ").</p>";
    });
})();
