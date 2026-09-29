// Renders the proposal page from a measurements object. Same logic as propose.py:
// verdicts, main numbers, fit and warnings are computed here from raw counts, so
// whoever supplies the counts (the script, or an assistant using the Ahrefs MCP
// server) gets the same page. WORDING and MENU are injected at build time.
(function () {
  "use strict";
  const W = WORDING, M = MENU;
  const ORDER = { keep: 0, floor: 1, thin: 2, zero: 3, unavailable: 4 };
  const BRAND_NUM = new Set(["mention_rate", "top_three_rate", "win_rate", "capture", "cohort_sov", "owned_citation_share"]);
  const CIT = new Set(["owned_citation_share", "citation_split"]);
  const COLORS = { branded: ["#ede9fe", "#5b21b6", "#8b5cf6"], conquest: ["#fee2e2", "#991b1b", "#ef4444"],
    list: ["#dbeafe", "#1e40af", "#3b82f6"], task: ["#dcfce7", "#166534", "#22c55e"],
    category: ["#fef3c7", "#92400e", "#f59e0b"], none: ["#e5e7eb", "#374151", "#9ca3af"] };

  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#x27;" }[c]));
  const f = (s, B) => String(s).split("{B}").join(B);
  // Python-style round-half-even, so numbers match propose.py exactly
  function rhe(x, d) { const p = Math.pow(10, d), m = x * p, fl = Math.floor(m);
    const n = Math.abs(m - fl - 0.5) < 1e-9 ? (fl % 2 === 0 ? fl : fl + 1) : Math.round(m); return n / p; }
  const fx = (x, d) => rhe(x, d).toFixed(d);
  const pct = (n, d) => fx(n * 100 / d, 0) + "%";
  function ordinal(x) { const n = Math.max(1, rhe(x, 0)); const t = n % 100 >= 11 && n % 100 <= 13 ? "th" : ({ 1: "st", 2: "nd", 3: "rd" }[n % 10] || "th"); return n + t; }
  const typeName = (k, B) => f((W.TYPES[k] || [k])[0], B);
  const typeDesc = (k, B) => f((W.TYPES[k] || ["", ""])[1], B);

  function splitText(split, B) {
    const names = { owned: B + "'s site", competitor: "competitors' sites", ugc: "forums & social", "third-party": "everyone else" };
    const tot = split.reduce((a, x) => a + x[1], 0);
    return split.map(([k, v]) => `${names[k] || k} ${Math.floor(v * 100 / tot)}%`).join(", ");
  }

  function verdict(id, spec, m, applies, surfaces, hasFacts) {
    if (spec.requires === "fact_sheet" && !hasFacts) return ["unavailable", "facts"];
    if (spec.sampled === false) return ["keep", "unsampled"];
    const looked = m ? (m.looked_at || 0) : 0;
    if (!m || looked === 0) return ["unavailable", "noanswers"];
    const week = m.den * (applies * surfaces * 7) / Math.max(1, looked);
    if (applies < 5 && !CIT.has(id)) return ["thin", "fewq", applies];
    if (m.den === 0) return ["zero", "noden"];
    if (week < (spec.min_n || 20)) return ["thin", "fewa"];
    if (m.num === 0 && BRAND_NUM.has(id)) return ["floor", "zero"];
    return ["keep", "week", week];
  }

  function reason(id, v, B) {
    const [kind, why, x] = v;
    if (kind === "keep") {
      if (why === "unsampled") return "Enough data to see real changes.";
      const unit = { cohort_sov: "brand mentions", owned_citation_share: "cited websites", citation_split: "cited websites" }[id] || "answers";
      return `About ${fx(x, 0)} ${unit} a week to count, enough to see real changes.`;
    }
    if (kind === "floor") return `${B} never shows up here yet, so this would read 0% every day. Worth tracking only if you're trying to get in.`;
    if (kind === "thin") return why === "fewq" ? `Only ${x} question${x !== 1 ? "s" : ""} in this topic suit${x === 1 ? "s" : ""} this, too few to be reliable.` : "Too few answers a week to read reliably.";
    if (kind === "zero") {
      if (["position", "top_three_rate", "negative_rate"].includes(id)) return `${B} is never named in these answers, so there's nothing to measure.`;
      if (id === "win_rate") return `No answer that names ${B} picks a single winner.`;
      if (id === "capture") return "No answer recommends a specific brand or organization.";
      if (id === "cohort_sov") return "None of the tracked brands are named.";
      if (CIT.has(id)) return "These answers cite no sources.";
      return "Nothing to count in these answers.";
    }
    return why === "facts" ? `Needs a list of verified facts about ${B} to check answers against.` : "No real answers loaded for these questions yet.";
  }

  function metricView(id, spec, m, v, B, g) {
    const n = m ? m.num : 0, d = m ? m.den : 0;
    const [tech, top, bottom] = W.FORMULA[id];
    let value = "—", worked, sentence = "";
    if (id === "citation_split") {
      worked = d && m.split && m.split.length ? `${splitText(m.split, B)} of ${d} cited websites` : "no cited websites in the sample";
      sentence = d && m.split ? splitText(m.split, B) : "";
    } else if (d === 0) {
      worked = `${n} ÷ 0: nothing to divide by in the sample`;
    } else if (id === "position") {
      value = fx(n / d, 1); worked = `${n} ÷ ${d} = ${fx(n / d, 1)}`;
      sentence = `when named, ${B} is usually the ${ordinal(n / d)} name mentioned (average ${fx(n / d, 1)}, from ${d} answers)`;
    } else {
      value = pct(n, d); worked = `${n} ÷ ${d} = ${pct(n, d)}`;
      sentence = W.SENTENCE[id] ? f(W.SENTENCE[id], B).replace("{n}", n).replace("{d}", d) : `${n} of ${d}`;
    }
    return { id, value, verdict: v[0], name: f(W.METRICS[id][0], B), what: f(W.METRICS[id][1], B),
      status: W.STATUS[v[0]][0], css: W.STATUS[v[0]][1], reason: reason(id, v, B), sentence,
      tech, formula: `${f(top, B)} ÷ ${f(bottom, B)}`, worked, n, d, applies: v.applies, of: g.questions.length };
  }

  function compute(D) {
    const B = D.brand, surfaces = D.surfaces.length || 4, hasFacts = !!D.has_fact_sheet;
    const counts = {}; let nq = 0, nNone = 0, nReview = 0, nNoAns = 0;
    const groups = D.groups.map(g => {
      const mix = {}; g.questions.forEach(q => { mix[q.type] = (mix[q.type] || 0) + 1; counts[q.type] = (counts[q.type] || 0) + 1;
        nq++; if (q.type === "none") nNone++; if (q.note) nReview++; if (q.answers === 0) nNoAns++; });
      let dom = null, domN = 0; Object.keys(mix).forEach(k => { if (mix[k] > domN) { dom = k; domN = mix[k]; } });
      const ms = [];
      Object.keys(M.metrics).forEach(id => {
        const spec = M.metrics[id];
        const applies = g.questions.filter(q => spec.shapes.includes(q.type)).length;
        if (!applies) return;
        const m = (g.metrics || {})[id];
        const v = verdict(id, spec, m, applies, surfaces, hasFacts); v.applies = applies;
        ms.push(metricView(id, spec, m, v, B, g));
      });
      const cands = (M.headline_by_shape[dom] || []).map(h => ms.find(x => x.id === h)).filter(Boolean);
      const head = cands.find(x => x.verdict === "keep" && x.n > 0) || cands.find(x => x.verdict === "keep") || cands.find(x => x.verdict === "floor") || null;
      ms.forEach(x => x.headline = head && x.id === head.id);
      const sorted = ms.map((x, i) => [x, i]).sort((a, b) => ((b[0].headline ? 1 : 0) - (a[0].headline ? 1 : 0)) || (ORDER[a[0].verdict] - ORDER[b[0].verdict]) || (a[1] - b[1])).map(x => x[0]);
      return { ...g, mix, dom, head, flat: head && head.verdict === "keep" && head.n === 0,
        track: sorted.filter(x => x.verdict === "keep" || x.verdict === "floor"),
        skip: sorted.filter(x => x.verdict !== "keep" && x.verdict !== "floor") };
    });
    const scored = nq - nNone, share = nq ? nNone / nq : 0;
    const fit = share > 0.5 ? "citations-only" : (share > 0.2 || scored < 15) ? "partial" : "full";
    const notes = [];
    if (groups.some(g => g.questions.length < 5)) notes.push("Some topics have fewer than 5 questions. Numbers for them jump around a lot; consider merging them.");
    const flat = groups.filter(g => g.flat).map(g => g.name);
    if (flat.length) notes.push(`The main number reads 0 for: ${flat.join(", ")}. That may be the finding itself, or a sign to pick a different main number.`);
    if (nReview) notes.push(`${nReview} of ${nq} questions were hard to sort. They're marked ⚠ in each topic's question list and are worth a quick look.`);
    if (D.answers > 0 && D.cited_flag === false) notes.push("The sample doesn't say which links were actually cited, so source numbers will read high.");
    if (!D.answers) notes.push("No real AI answers have been loaded yet, so nothing could be checked. Every number below reads “can't measure yet”.");
    if (D.answers_expected && D.answers < 0.9 * D.answers_expected) notes.push(`Only ${D.answers} of ${D.answers_expected} expected answers were loaded (questions × AI surfaces × days). Treat every number as incomplete.`);
    (D.extra_notes || []).forEach(n => notes.push(n));
    if (D.answers && nNoAns) notes.push(`${nNoAns} of ${nq} questions had no answers in the sample, so some topics rest on fewer questions.`);
    return { B, groups, counts, nq, fit, notes };
  }

  const chip = (k, text, cls) => `<span class="${cls || "chip"} t-${esc(k)}">${esc(text)}</span>`;
  const st = (v, label) => `<span class="st st-${W.STATUS[v][1]}">${esc(label)}</span>`;

  function render(D) {
    const C = compute(D), B = C.B, o = [];
    const types = Object.entries(C.counts).sort((a, b) => b[1] - a[1]);
    const total = C.nq || 1, days = D.days === 1 ? "one day" : `${D.days} days`;
    o.push(`<header><h1>What to track for ${esc(B)} in AI answers</h1><p class="lead">We read the ${C.nq} questions this report asks AI assistants, sorted them into ${C.groups.length} topics, and checked which numbers are worth putting on a dashboard for each one, using ${D.answers} real AI answers from ${days}.</p></header>`);
    const [fitT, fitX] = W.SET_TEXT[C.fit];
    o.push(`<div class="grid2"><div class="card"><div class="h">${esc(fitT)}</div><p>${esc(f(fitX, B))}</p><p class="small muted">Numbers on this page come from a small sample. They show whether something is worth tracking, not what the real figure is. “3 of 12” doesn't mean 25%.</p></div>`);
    const bar = types.map(([k, v]) => `<span style="width:${(v / total * 100).toFixed(1)}%;background:${COLORS[k][2]}" title="${esc(typeName(k, B))}: ${v}"></span>`).join("");
    const lis = types.map(([k, v]) => `<li>${chip(k, v + " · " + typeName(k, B))} <span class="muted">${esc(typeDesc(k, B))}</span></li>`).join("");
    o.push(`<div class="card"><div class="h2">What kinds of questions are in this report</div><div class="bar">${bar}</div><ul class="types">${lis}</ul><p class="small muted">The type decides what can be measured: ${esc(B)} can only “win” a question that asks for a recommendation.</p></div></div>`);
    if (C.notes.length) o.push(`<div class="warn"><div class="h2">Worth checking</div><ul>${C.notes.map(n => `<li>${esc(n)}</li>`).join("")}</ul></div>`);
    o.push(`<h2>The dashboard this suggests</h2><p class="small muted">One card per topic, showing the number most worth watching there. Click a card for details.</p><div class="cards">`);
    C.groups.forEach((g, i) => {
      const h = g.head, k = g.track.length;
      const body = h ? `<div class="big${h.verdict === "floor" ? " dim" : ""}">${esc(h.value)}</div><div class="mname">${esc(h.name)}</div><div class="small muted">${esc(h.sentence)}</div><div class="mono small muted">${esc(h.tech)}: ${esc(h.worked)}</div>` : `<div class="muted">Nothing worth tracking here</div>`;
      o.push(`<a class="card link" href="#g${i + 1}"><div class="topic">${esc(g.name)}</div>${body}<div class="small muted foot">${g.questions.length} questions · ${k} number${k !== 1 ? "s" : ""} worth tracking</div></a>`);
    });
    o.push(`</div>`);
    C.groups.forEach((g, i) => {
      const mix = Object.entries(g.mix).sort((a, b) => b[1] - a[1]).map(([k, v]) => chip(k, v + " " + typeName(k, B).toLowerCase())).join("");
      o.push(`<section id="g${i + 1}" class="card topicsec"><div class="sechead"><h3>${esc(g.name)}</h3>${g.description ? `<p>${esc(g.description)}</p>` : ""}<div>${mix}</div></div><div class="secbody">`);
      if (g.track.length) {
        o.push(`<div class="label">Worth tracking</div>`);
        g.track.forEach(m => {
          const val = m.id === "citation_split" ? "" : esc(m.value);
          const tags = (m.headline ? `<span class="tag main">main number</span>` : "") + (m.verdict === "floor" ? st("floor", m.status) : "");
          const part = m.applies !== m.of ? ` Based on ${m.applies} of ${m.of} questions in this topic; the rest don't fit this measure.` : "";
          o.push(`<div class="metric"><div class="val${m.verdict === "floor" ? " dim" : ""}">${val}</div><div><div class="mname">${esc(m.name)} ${tags}</div><div class="small muted">${esc(m.what)}</div><div class="calc"><b>${esc(m.tech)}</b> <span class="muted">= ${esc(m.formula)}</span><br><span class="mono">= ${esc(m.worked)}</span></div><div class="small muted">${esc(m.reason)}${esc(part)}</div></div></div>`);
        });
      } else o.push(`<p class="muted">Nothing here is worth tracking yet.</p>`);
      if (g.skip.length) {
        o.push(`<details><summary>Not worth tracking here (${g.skip.length})</summary><ul class="skip">`);
        g.skip.forEach(m => o.push(`<li><b>${esc(m.name)}</b> <span class="muted">(${esc(m.tech)})</span> ${st(m.verdict, m.status)}<div class="muted">${esc(m.reason)}</div><div class="mono muted">${esc(m.formula)}${m.verdict !== "unavailable" ? " = " + esc(m.worked) : ""}</div></li>`));
        o.push(`</ul></details>`);
      }
      o.push(`</div>`);
      const nr = g.questions.filter(q => q.note).length;
      o.push(`<details class="qs"><summary>The ${g.questions.length} questions in this topic${nr ? ` · ⚠ ${nr} to check` : ""}</summary><ul>`);
      g.questions.forEach(q => o.push(`<li>${chip(q.type, typeName(q.type, B), "chip qt")}<div>${esc(q.q)}${q.note ? `<div class="small muted">⚠ ${esc(q.note)}</div>` : ""}</div></li>`));
      o.push(`</ul></details></section>`);
    });
    const S = W.STATUS;
    o.push(`<details class="card"><summary><b>How to read this page</b></summary><div class="howto"><p><b>Topics</b> group questions that people would ask for the same reason. An AI model proposed them; a person should check them.</p><p><b>Question types</b> decide what can be measured. You can only count ${esc(B)} “winning” when a question asks for a recommendation. On a general question AI rarely recommends anyone, so the useful measure there is whether ${esc(B)}'s website is used as a source.</p><p><b>Calculations</b> under each number show the metric's standard name, what it divides by what, and the sample's actual counts. The part after “÷” says which answers the percentage is out of.</p><ul><li>${st("keep", S.keep[0])} enough answers each week to see real changes.</li><li>${st("floor", S.floor[0])} ${esc(B)} doesn't appear yet, so it reads 0%. Useful only if you're trying to get in.</li><li>${st("thin", S.thin[0])} too few questions or answers to be reliable.</li><li>${st("zero", S.zero[0])} the thing it counts never happens in these answers.</li><li>${st("unavailable", S.unavailable[0])} needs something not provided, like a list of verified facts.</li></ul><p>⚠ marks questions whose type was hard to decide. Changing one can move a number between topics.</p></div></details>`);
    o.push(`<p class="small muted footer">Generated by the <a href="https://github.com/mmakosiewicz/ai-visibility-dashboard-kit/blob/main/09-proposal/README.md">AI visibility dashboard kit</a>, step 0. Sorted by ${esc(D.classifier || "an AI model")} · ${esc(D.generated || "")}. Source: Ahrefs Brand Radar.</p>`);
    document.title = `What to track for ${B} in AI answers`;
    return o.join("");
  }

  const colors = Object.entries(COLORS).map(([k, [b, c]]) => `.t-${k}{background:${b};color:${c}}`).join("");
  const style = document.createElement("style"); style.textContent = colors; document.head.appendChild(style);
  const main = document.getElementById("report");
  const b64 = t => decodeURIComponent(escape(atob(t.replace(/-/g, "+").replace(/_/g, "/"))));
  function fromHash() {
    const h = (typeof location !== "undefined" && location.hash) || "";
    if (h.startsWith("#data=")) return JSON.parse(b64(h.slice(6)));
    if (h.startsWith("#json=")) return JSON.parse(decodeURIComponent(h.slice(6)));
    return null;
  }
  function saveButton(D) {
    const t = document.documentElement.outerHTML.replace(/(<script type="application\/json" id="measurements">)[\s\S]*?(<\/script>)/,
      (m, a, b) => a + "\n" + JSON.stringify(D, null, 1).replace(/<\//g, "<\\/") + "\n" + b);
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob(["<!DOCTYPE html>\n" + t], {type: "text/html"}));
    a.download = "ai-visibility-proposal.html"; a.textContent = "Save this report as a file"; a.className = "save small";
    main.appendChild(a);
  }
  function show(D) { main.innerHTML = render(D); if (typeof window !== "undefined" && typeof Blob !== "undefined" && typeof URL !== "undefined" && URL.createObjectURL) saveButton(D); }
  function pasteBox(msg) {
    main.innerHTML = `<div class="card"><div class="h">Paste your measurements</div><p>Your assistant (Claude or ChatGPT with the Ahrefs MCP server) gives you a block of measurements at the end of its run. Paste all of it here.</p>${msg ? `<div class="warn">${esc(msg)}</div>` : ""}<textarea id="paste" rows="12" placeholder='{"brand": "…", "groups": […]}'></textarea><p><button id="go">Show report</button></p><p class="small muted">Nothing is uploaded: the page is worked out in your browser.</p></div>`;
    document.getElementById("go").onclick = () => {
      const raw = document.getElementById("paste").value.trim().replace(/^```(json)?/, "").replace(/```$/, "");
      try { show(JSON.parse(raw)); } catch (e) { pasteBox("That isn't a complete measurements block: " + e.message); }
    };
  }
  try {
    const H = fromHash();
    if (H) { show(H); return; }
    const D = JSON.parse(document.getElementById("measurements").textContent);
    if (D._template) { pasteBox(""); return; }
    show(D);
  } catch (e) { main.innerHTML = `<div class="warn"><b>Couldn't read the measurements.</b> ${esc(e.message)}</div>`; }
})();
