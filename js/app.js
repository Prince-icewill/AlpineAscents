/* Alpine Ascents - single page app
   - content comes from the JSON files in /data
   - pages are drawn into #view; the address bar uses #/page so back and forward still work */
(function ($) {
  "use strict";

  var KEYS = ["site", "history", "styles", "techniques", "shelter", "hazards", "records", "clubs", "stories", "gallery", "news", "guidelines"];
  var DATA = {};
  var TITLES = {
    home: "Home", history: "History", styles: "Types and Styles", techniques: "Techniques", shelter: "Sheltering",
    hazards: "Hazards", records: "Records", clubs: "Clubs and Map", stories: "Success Stories", gallery: "Gallery",
    latest: "Latest Developments", guidelines: "General Guidelines"
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function num(n) { return Number(n).toLocaleString("en-US"); }
  function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-"); }

  /* ---------- data ---------- */
  function loadData() {
    return Promise.all(KEYS.map(function (k) {
      return fetch("data/" + k + ".json", { cache: "no-cache" }).then(function (r) {
        if (!r.ok) throw new Error(k + " " + r.status);
        return r.json();
      });
    })).then(function (list) {
      KEYS.forEach(function (k, i) { DATA[k] = list[i]; });
    }).catch(function () {
      // opened straight from disk: browsers block fetch() on file://, so use the bundled copy
      if (window.AA_DATA) { DATA = window.AA_DATA; return; }
      throw new Error("Could not load the data files.");
    });
  }

  /* ---------- shared bits ---------- */
  function head(crumb, title, text, img) {
    return '<section class="page-head">' + (img ? '<img class="head-img" src="' + img + '" alt="">' : "") +
      '<div class="container-xl"><div class="crumb">' + esc(crumb) + "</div><h1>" + esc(title) + "</h1>" +
      (text ? "<p>" + esc(text) + "</p>" : "") + "</div></section>";
  }
  function wrap(inner) { return '<div class="container-xl section">' + inner + "</div>"; }
  function chips(list, current, attr) {
    return list.map(function (c) {
      return '<button type="button" class="chip' + (c === current ? " on" : "") + '" data-' + attr + '="' + esc(c) + '">' + esc(c) + "</button>";
    }).join(" ");
  }

  /* ---------- pages ---------- */
  var PAGES = {};

  PAGES.home = function () {
    var s = DATA.site;
    var facts = s.facts.map(function (f) {
      return '<div class="col-6 col-lg-3"><div class="fact"><div class="v">' + esc(f.value) + '</div><div class="l">' + esc(f.label) + '</div><div class="n">' + esc(f.note) + "</div></div></div>";
    }).join("");
    var cards = s.cards.map(function (c) {
      return '<div class="col-sm-6 col-lg-4"><a class="card-x topic-card" href="#/' + c.route + '"><img class="cover" src="' + c.img + '" alt="" loading="lazy">' +
        '<span class="icon"><i class="bi ' + c.icon + '"></i></span><div class="body"><h3>' + esc(c.title) + "</h3><p>" + esc(c.text) + "</p></div></a></div>";
    }).join("");
    return '<section class="hero"><img class="bg" src="' + s.hero.image + '" alt="">' +
      '<div class="container-xl"><h1>Climb smart.<br><span>Come back down.</span></h1><p>' + esc(s.hero.text) + "</p>" +
      '<div class="d-flex gap-2 flex-wrap mt-3"><a class="btn btn-ember btn-lg" href="#/history">Start with the history</a><a class="btn btn-ghost btn-lg" href="#/clubs">Find a club near you</a></div></div></section>' +
      '<div class="container-xl facts"><div class="row g-3">' + facts + "</div></div>" +
      wrap('<h2 class="section-title">What is on this site</h2><div class="row g-4">' + cards + "</div>") +
      '<div class="container-xl pb-5"><div class="rule-box row align-items-center g-3"><div class="col-md-8"><h3>The one rule worth remembering</h3>' +
      "<p class=\"mb-0\">The summit is optional. Getting back down is not. Set a turnaround time before you leave and keep to it, even when the top looks close.</p></div>" +
      '<div class="col-md-4 text-md-end"><a class="btn btn-ember" href="#/guidelines">Read the guidelines</a></div></div></div>';
  };

  PAGES.history = function () {
    var h = DATA.history;
    var nav = h.eras.map(function (e, i) { return '<button class="chip" type="button" data-scroll="era-' + i + '">' + esc(e.name) + "</button>"; }).join(" ");
    var eras = h.eras.map(function (e, i) {
      var items = e.items.map(function (it) {
        return '<article class="tl-item"><div class="tl-year">' + esc(it.year) + "</div><h3>" + esc(it.title) + "</h3><p>" + esc(it.text) + "</p></article>";
      }).join("");
      return '<div class="era" id="era-' + i + '"><div class="era-head"><h2>' + esc(e.name) + '</h2><span class="yrs">' + esc(e.years) + '</span></div><div class="timeline">' + items + "</div></div>";
    }).join("");
    return head("Mountaineering", "History", h.intro, h.image) + wrap('<div class="era-nav d-flex gap-2 flex-wrap">' + nav + "</div>" + eras);
  };

  PAGES.styles = function () {
    var s = DATA.styles;
    var cards = s.styles.map(function (x) {
      return '<div class="col-md-6 col-xl-4"><article class="card-x"><div class="body"><h3><i class="bi ' + x.icon + ' text-danger me-2"></i>' + esc(x.name) + "</h3><p>" + esc(x.summary) + "</p>" +
        '<p class="mb-1"><span class="pill">Good</span> ' + esc(x.good) + '</p><p class="mb-1"><span class="pill hot">Watch out</span> ' + esc(x.bad) + '</p><p class="mb-0 small text-muted"><strong>Example:</strong> ' + esc(x.example) + "</p></div></article></div>";
    }).join("");
    var rows = s.grades.rows.map(function (r) {
      return "<tr><td><strong>" + esc(r.system) + "</strong></td><td>" + esc(r.scale) + "</td><td>" + esc(r.meaning) + "</td></tr>";
    }).join("");
    return head("Mountaineering", "Types and Styles", s.intro, "assets/img/ice-climbing.svg") +
      wrap('<div class="row g-4">' + cards + "</div>") +
      wrap('<h2 class="section-title">' + esc(s.grades.title) + "</h2><p>" + esc(s.grades.text) + '</p><div class="table-responsive table-x"><table class="table mb-0"><thead><tr><th>System</th><th>Scale</th><th>What it means</th></tr></thead><tbody>' + rows + "</tbody></table></div>");
  };

  PAGES.techniques = function () {
    var t = DATA.techniques;
    var cats = ["All"].concat(t.items.map(function (i) { return i.cat; }).filter(function (c, i, a) { return a.indexOf(c) === i; }));
    var items = t.items.map(function (x, i) {
      var steps = x.steps.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("");
      return '<div class="accordion-item tech" data-cat="' + esc(x.cat) + '"><h3 class="accordion-header"><button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#t' + i + '" aria-expanded="false" aria-controls="t' + i + '">' +
        '<i class="bi ' + x.icon + ' me-3 fs-4 text-danger"></i><span><span class="d-block">' + esc(x.name) + '</span><small class="text-muted fw-normal fs-6">' + esc(x.cat) + " &middot; " + esc(x.summary) + "</small></span></button></h3>" +
        '<div id="t' + i + '" class="accordion-collapse collapse"><div class="accordion-body"><ol class="mb-0">' + steps + "</ol></div></div></div>";
    }).join("");
    return head("Mountaineering", "Techniques", t.intro, "assets/img/glacier-team.svg") +
      wrap('<div class="d-flex gap-2 flex-wrap mb-3" id="techChips">' + chips(cats, "All", "cat") + '</div><div class="accordion" id="techList">' + items + "</div>" +
        '<p class="note mt-4 mb-0"><i class="bi bi-info-circle"></i> Reading about a technique is not the same as learning it. Practise on safe ground with a qualified instructor.</p>');
  };

  PAGES.shelter = function () {
    var s = DATA.shelter;
    var cards = s.items.map(function (x) {
      var tips = x.tips.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("");
      return '<div class="col-md-6 col-xl-4"><article class="card-x"><img class="cover" src="' + x.img + '" alt="" loading="lazy"><div class="body"><h3><i class="bi ' + x.icon + ' text-danger me-2"></i>' + esc(x.name) + "</h3><p>" + esc(x.text) + '</p><strong class="small text-uppercase text-muted">Tips</strong><ul class="mb-0 small">' + tips + "</ul></div></article></div>";
    }).join("");
    var check = s.checklist.map(function (c, i) { return '<li><label><input type="checkbox" data-key="shelter-' + i + '"><span>' + esc(c) + "</span></label></li>"; }).join("");
    return head("Mountaineering", "Sheltering", s.intro, "assets/img/high-camp.svg") +
      wrap('<div class="row g-4">' + cards + "</div>") +
      wrap('<div class="card-x"><div class="body"><h2>Choosing a campsite: quick checklist</h2><ul class="check-list">' + check + "</ul></div></div>");
  };

  PAGES.hazards = function () {
    var hz = DATA.hazards;
    var colors = ["#3d8f5f", "#8aa13a", "#d9a21f", "#e8622a", "#a8281f"];
    var total = 5;
    var zones = hz.zones.map(function (z, i) {
      return '<div style="flex:1;background:' + colors[i] + '" title="' + esc(z.note) + '">' + esc(z.band) + "<br><small>" + esc(z.name) + "</small></div>";
    }).join("");
    var zoneNotes = hz.zones.map(function (z) { return "<li><strong>" + esc(z.band) + ":</strong> " + esc(z.note) + "</li>"; }).join("");
    var cards = hz.items.map(function (x) {
      var dots = ""; for (var i = 1; i <= total; i++) dots += '<i class="' + (i <= x.risk ? "on" : "") + '"></i>';
      return '<div class="col-lg-6 hz" data-type="' + esc(x.type) + '"><article class="card-x"><div class="body"><div class="d-flex justify-content-between align-items-start gap-2"><h3><i class="bi ' + x.icon + ' text-danger me-2"></i>' + esc(x.name) + "</h3>" +
        '<span class="pill' + (x.type === "Subjective" ? " hot" : "") + '">' + esc(x.type) + '</span></div><div class="small text-muted mb-2">Seriousness <span class="risk" aria-label="' + x.risk + ' out of 5">' + dots + "</span></div><p>" + esc(x.summary) + "</p>" +
        '<dl class="small mb-0"><dt>Signs</dt><dd>' + esc(x.signs) + "</dd><dt>Prevention</dt><dd>" + esc(x.prevent) + "</dd><dt>What to do</dt><dd class=\"mb-0\">" + esc(x.response) + "</dd></dl></div></article></div>";
    }).join("");
    return head("Mountaineering", "Hazards", hz.intro, "assets/img/k2-storm.svg") +
      wrap('<h2 class="section-title">Altitude zones</h2><div class="zone-bar mb-3">' + zones + '</div><ul class="small">' + zoneNotes + "</ul>") +
      wrap('<h2 class="section-title">The main hazards</h2><div class="d-flex gap-2 flex-wrap mb-3" id="hzChips">' + chips(["All", "Objective", "Subjective"], "All", "type") + '</div><div class="row g-4">' + cards + "</div>");
  };

  var recSort = { key: "height", dir: -1 };
  function recRows(q) {
    var list = DATA.records.peaks.slice();
    q = (q || "").toLowerCase();
    if (q) list = list.filter(function (p) { return (p.name + " " + p.country + " " + p.team).toLowerCase().indexOf(q) > -1; });
    list.sort(function (a, b) {
      var x = a[recSort.key], y = b[recSort.key];
      return (typeof x === "string" ? x.localeCompare(y) : x - y) * recSort.dir;
    });
    return list.map(function (p, i) {
      return "<tr><td>" + (i + 1) + "</td><td><strong>" + esc(p.name) + "</strong></td><td>" + num(p.height) + " m</td><td>" + esc(p.country) + "</td><td>" + p.first + "</td><td>" + esc(p.team) + "</td></tr>";
    }).join("") || '<tr><td colspan="6" class="text-center text-muted py-4">Nothing matches that search.</td></tr>';
  }

  PAGES.records = function () {
    var r = DATA.records;
    var seven = r.seven.map(function (p) {
      return '<div class="bar-row"><div><strong>' + esc(p.name) + '</strong><br><small class="text-muted">' + esc(p.continent) + '</small></div><div class="track"><div class="fill" data-w="' + (p.height / 8849 * 100).toFixed(1) + '"></div></div><div class="text-end"><strong>' + num(p.height) + " m</strong><br><small>" + p.first + "</small></div></div>";
    }).join("");
    var firsts = r.firsts.map(function (f) {
      return '<article class="tl-item"><div class="tl-year">' + f.year + "</div><h3>" + esc(f.what) + "</h3><p>" + esc(f.who) + "</p></article>";
    }).join("");
    var cur = r.current.map(function (c) {
      return '<div class="col-6 col-lg-3"><div class="card-x"><div class="body"><div class="big-num">' + esc(c.value) + "</div><strong>" + esc(c.label) + '</strong><div class="small text-muted">' + esc(c.who) + "</div></div></div></div>";
    }).join("");
    var dis = r.disasters.map(function (d) { return "<li><strong>" + d.year + ":</strong> " + esc(d.text) + "</li>"; }).join("");
    return head("Mountaineering", "Records", r.intro, "assets/img/summit-ridge.svg") +
      wrap('<h2 class="section-title">Current records (' + esc(r.asOf) + ')</h2><div class="row g-3">' + cur + "</div>") +
      wrap('<ul class="nav nav-pills gap-2 mb-3" role="tablist">' +
        '<li class="nav-item"><button class="chip on active" data-bs-toggle="tab" data-bs-target="#tab8k" type="button" role="tab">The fourteen 8,000 m peaks</button></li>' +
        '<li class="nav-item"><button class="chip" data-bs-toggle="tab" data-bs-target="#tab7" type="button" role="tab">Seven Summits</button></li>' +
        '<li class="nav-item"><button class="chip" data-bs-toggle="tab" data-bs-target="#tabFirst" type="button" role="tab">Famous firsts</button></li></ul>' +
        '<div class="tab-content">' +
        '<div class="tab-pane fade show active" id="tab8k" role="tabpanel"><input id="peakSearch" class="form-control mb-3" type="search" placeholder="Search by peak, country or climber" aria-label="Search peaks">' +
        '<div class="table-responsive table-x"><table class="table table-hover mb-0" id="peakTable"><thead><tr><th>#</th><th data-k="name">Peak <i class="bi bi-arrow-down-up"></i></th><th data-k="height">Height <i class="bi bi-arrow-down-up"></i></th><th data-k="country">Country <i class="bi bi-arrow-down-up"></i></th><th data-k="first">First ascent <i class="bi bi-arrow-down-up"></i></th><th>Who</th></tr></thead><tbody>' + recRows() + "</tbody></table></div>" +
        '<p class="small text-muted mt-2">Click a column heading to sort.</p></div>' +
        '<div class="tab-pane fade" id="tab7" role="tabpanel"><p>Bars are drawn to scale against Everest. Heights are those usually quoted for the Seven Summits list.</p><div id="sevenBars">' + seven + "</div></div>" +
        '<div class="tab-pane fade" id="tabFirst" role="tabpanel"><div class="timeline">' + firsts + "</div></div></div>") +
      wrap('<div class="note"><strong>Hard years on Everest</strong><ul class="mb-0 mt-2">' + dis + "</ul></div>");
  };

  /* clubs page keeps a little state so filters and distance sorting work together */
  var clubState = { region: "All", q: "", pos: null, sel: null };
  function clubList() {
    var list = DATA.clubs.clubs.filter(function (c) {
      return (clubState.region === "All" || c.region === clubState.region) &&
        (!clubState.q || (c.name + " " + c.city + " " + c.country + " " + c.focus).toLowerCase().indexOf(clubState.q) > -1);
    });
    if (clubState.pos) {
      list.forEach(function (c) { c._km = AAMap.km(clubState.pos, c); });
      list.sort(function (a, b) { return a._km - b._km; });
    }
    return list;
  }
  function drawClubs() {
    var list = clubList();
    var html = list.map(function (c) {
      var offers = c.offers.map(function (o) { return '<span class="pill me-1">' + esc(o) + "</span>"; }).join("");
      return '<div class="club' + (clubState.sel === c.id ? " sel" : "") + '" data-id="' + c.id + '" tabindex="0" role="button"><h3>' + esc(c.name) + '</h3><small>' + esc(c.city) + ", " + esc(c.country) + (c.founded ? " &middot; founded " + c.founded : "") + "</small>" +
        (c._km != null && clubState.pos ? ' <span class="dist">&middot; ' + num(Math.round(c._km)) + " km away</span>" : "") +
        '<p class="small mb-2 mt-1">' + esc(c.focus) + "</p><div class=\"mb-2\">" + offers + '</div><div class="small">' +
        (c.url ? '<a href="' + esc(c.url) + '" target="_blank" rel="noopener"><i class="bi bi-box-arrow-up-right"></i> Website</a> &nbsp; ' : "") +
        '<a href="https://www.google.com/maps/search/?api=1&query=' + c.lat + "," + c.lng + '" target="_blank" rel="noopener"><i class="bi bi-map"></i> Open in Google Maps</a></div></div>';
    }).join("") || '<p class="text-muted">No clubs match.</p>';
    $("#clubList").html(html);
    $("#clubCount").text(list.length + " of " + DATA.clubs.clubs.length + " clubs");
    AAMap.show(list.map(function (c) { return c.id; }));
  }

  PAGES.clubs = function () {
    var regions = ["All", "Europe", "Asia", "Americas", "Africa", "Oceania"];
    return head("Find a club", "Clubs and Map", DATA.clubs.intro, "assets/img/mountain-hut.svg") +
      wrap('<div class="d-flex gap-2 flex-wrap align-items-center mb-3" id="regionChips">' + chips(regions, clubState.region, "region") +
        '<input id="clubSearch" type="search" class="form-control ms-md-auto" style="max-width:260px" placeholder="Search clubs" aria-label="Search clubs">' +
        '<button id="nearMe" type="button" class="btn btn-ember"><i class="bi bi-crosshair"></i> Distance from me</button></div>' +
        '<div class="small text-muted mb-2" id="clubCount"></div><div id="nearMsg" class="small mb-2"></div>' +
        '<div class="row g-3"><div class="col-lg-7"><div id="clubMap" aria-label="Map of mountaineering clubs"></div></div><div class="col-lg-5"><div class="club-list" id="clubList"></div></div></div>');
  };

  PAGES.stories = function () {
    var s = DATA.stories;
    var cards = s.stories.map(function (x) {
      return '<div class="col-md-6"><article class="card-x story"><img class="cover" src="' + x.img + '" alt="" loading="lazy"><div class="body"><div class="d-flex gap-2 align-items-center mb-1"><span class="pill hot">' + x.year + '</span><small class="text-muted">' + esc(x.place) + "</small></div>" +
        "<h3>" + esc(x.title) + '</h3><div class="small text-muted mb-2"><i class="bi bi-people"></i> ' + esc(x.org) + "</div><p>" + esc(x.text) + '</p><div class="lesson"><strong>What it teaches:</strong> ' + esc(x.lesson) + "</div></div></article></div>";
    }).join("");
    return head("Organised expeditions", "Success Stories", s.intro, "assets/img/prayer-flags.svg") + wrap('<div class="row g-4">' + cards + "</div>");
  };

  var gal = { list: [], i: 0, cat: "All" };
  function galGrid() {
    gal.list = DATA.gallery.pictures.filter(function (p) { return gal.cat === "All" || p.cat === gal.cat; });
    $("#galGrid").html(gal.list.map(function (p, i) {
      return '<div class="col-6 col-lg-4"><button type="button" class="g-item" data-i="' + i + '" aria-label="Open ' + esc(p.title) + '"><img src="assets/img/' + p.file + '" alt="' + esc(p.title) + '" loading="lazy"><span class="cap">' + esc(p.title) + "</span></button></div>";
    }).join(""));
  }
  function lbShow(i) {
    gal.i = (i + gal.list.length) % gal.list.length;
    var p = gal.list[gal.i];
    $("#lbImg").attr({ src: "assets/img/" + p.file, alt: p.title });
    $("#lbTitle").text(p.title);
    $("#lbCaption").text(p.caption);
    $("#lbCount").text((gal.i + 1) + " / " + gal.list.length);
  }

  PAGES.gallery = function () {
    var g = DATA.gallery;
    var cats = ["All"].concat(g.pictures.map(function (p) { return p.cat; }).filter(function (c, i, a) { return a.indexOf(c) === i; }));
    var vids = g.videos.map(function (v) {
      return '<div class="col-md-6 col-xl-4"><div class="card-x"><video class="v" controls preload="metadata" poster="assets/video/' + v.poster + '"><source src="assets/video/' + v.file + '" type="video/mp4"><source src="assets/video/' + v.file.replace(".mp4", ".webm") + '" type="video/webm">Your browser cannot play this video.</video>' +
        '<div class="body"><h3>' + esc(v.title) + '</h3><p class="mb-1">' + esc(v.text) + '</p><small class="text-muted">' + esc(v.length) + "</small></div></div></div>";
    }).join("");
    var watch = g.watch.map(function (w) {
      return '<li class="mb-2"><strong>' + esc(w.title) + "</strong> <span class=\"text-muted\">(" + esc(w.by) + ')</span> &middot; <a href="https://www.youtube.com/results?search_query=' + encodeURIComponent(w.q) + '" target="_blank" rel="noopener">find it on YouTube</a></li>';
    }).join("");
    return head("Gallery", "Pictures and Videos", g.intro, "assets/img/denali-aurora.svg") +
      wrap('<h2 class="section-title">Pictures</h2><div class="d-flex gap-2 flex-wrap mb-3" id="galChips">' + chips(cats, gal.cat, "cat") + '</div><div class="row g-3" id="galGrid"></div>') +
      wrap('<h2 class="section-title">Videos</h2><div class="row g-4">' + vids + "</div>") +
      wrap('<h2 class="section-title">Worth watching</h2><p>Longer documentaries about the mountains in this guide. They are on other sites, so these links open a YouTube search.</p><ul class="list-unstyled">' + watch + "</ul>");
  };

  PAGES.latest = function () {
    var n = DATA.news;
    var items = n.items.slice().sort(function (a, b) { return a.date < b.date ? 1 : -1; }).map(function (x) {
      var d = x.dateLabel || new Date(x.date + "T00:00:00").toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
      return '<article class="news-item"><div><div class="news-date">' + esc(d) + '</div><span class="pill hot">' + esc(x.tag) + "</span></div><div><h3>" + esc(x.title) + "</h3><p class=\"mb-1\">" + esc(x.text) + '</p><a class="small" href="' + esc(x.url) + '" target="_blank" rel="noopener"><i class="bi bi-box-arrow-up-right"></i> ' + esc(x.source) + "</a></div></article>";
    }).join("");
    var trends = n.trends.map(function (t) {
      return '<div class="col-md-6"><div class="card-x"><div class="body"><h3>' + esc(t.title) + "</h3><p class=\"mb-0\">" + esc(t.text) + "</p></div></div></div>";
    }).join("");
    return head("What is new", "Latest Developments", n.intro + " Last checked: " + n.asOf + ".", "assets/img/matterhorn-noon.svg") +
      wrap(items) + wrap('<h2 class="section-title">Trends to watch</h2><div class="row g-3">' + trends + "</div>");
  };

  function savedChecks() { try { return JSON.parse(localStorage.getItem("aa_checks") || "{}"); } catch (e) { return {}; } }

  PAGES.guidelines = function () {
    var g = DATA.guidelines, saved = savedChecks();
    var secs = g.sections.map(function (s, si) {
      var li = s.items.map(function (it, ii) {
        var key = "g" + si + "-" + ii;
        return '<li><label><input type="checkbox" data-key="' + key + '"' + (saved[key] ? " checked" : "") + "><span>" + esc(it) + "</span></label></li>";
      }).join("");
      return '<div class="col-lg-6"><div class="card-x"><div class="body"><h3><i class="bi ' + s.icon + ' text-danger me-2"></i>' + esc(s.title) + '</h3><ul class="check-list">' + li + "</ul></div></div></div>";
    }).join("");
    var ess = g.essentials.map(function (e) { return '<span class="pill me-1 mb-1">' + esc(e) + "</span>"; }).join("");
    return head("Before you go", "General Guidelines", g.intro, "assets/img/aconcagua-dusk.svg") +
      wrap('<p class="small text-muted">Tick items as you plan. Your ticks are kept in this browser.</p><div class="row g-4">' + secs + "</div>") +
      wrap('<div class="card-x"><div class="body"><h3>The ten essentials</h3><p>A classic list of what every person in the hills should carry.</p>' + ess + '</div></div>');
  };

  /* ---------- behaviour after a page is drawn ---------- */
  var AFTER = {};
  AFTER.history = function () {
    $("#view").on("click", "[data-scroll]", function () {
      var el = document.getElementById($(this).data("scroll"));
      if (el) { var y = el.getBoundingClientRect().top + window.pageYOffset - 170; window.scrollTo({ top: y, behavior: "smooth" }); }
    });
  };
  AFTER.techniques = function () {
    $("#techChips").on("click", ".chip", function () {
      var c = $(this).data("cat");
      $("#techChips .chip").removeClass("on"); $(this).addClass("on");
      $(".tech").each(function () { $(this).toggle(c === "All" || $(this).data("cat") === c); });
    });
  };
  AFTER.shelter = AFTER.guidelines = function () {
    var saved = savedChecks();
    $("#view .check-list input").each(function () { var k = $(this).data("key"); if (saved[k]) this.checked = true; });
    $("#view .check-list").on("change", "input", function () {
      var s = savedChecks(); s[$(this).data("key")] = this.checked;
      try { localStorage.setItem("aa_checks", JSON.stringify(s)); } catch (e) {}
    });
  };
  AFTER.hazards = function () {
    $("#hzChips").on("click", ".chip", function () {
      var t = $(this).data("type");
      $("#hzChips .chip").removeClass("on"); $(this).addClass("on");
      $(".hz").each(function () { $(this).toggle(t === "All" || $(this).data("type") === t); });
    });
  };
  AFTER.records = function () {
    $("#peakSearch").on("input", function () { $("#peakTable tbody").html(recRows(this.value)); });
    $("#peakTable").on("click", "th[data-k]", function () {
      var k = $(this).data("k");
      recSort = { key: k, dir: recSort.key === k ? -recSort.dir : (k === "height" ? -1 : 1) };
      $("#peakTable tbody").html(recRows($("#peakSearch").val()));
    });
    $('[data-bs-target="#tab7"]').on("shown.bs.tab", function () {
      $("#sevenBars .fill").each(function () { $(this).css("width", $(this).data("w") + "%"); });
    });
    $("#view .nav-pills").on("click", ".chip", function () { $("#view .nav-pills .chip").removeClass("on"); $(this).addClass("on"); });
  };
  AFTER.clubs = function () {
    clubState.sel = null;
    AAMap.init(document.getElementById("clubMap"), DATA.clubs.clubs, function (id) {
      clubState.sel = id; drawClubs();
      var el = $('.club[data-id="' + id + '"]')[0]; if (el) el.scrollIntoView({ block: "nearest", behavior: "smooth" });
    });
    drawClubs();
    if (window.AA_USER_POS) AAMap.showMe(window.AA_USER_POS);
    $("#regionChips").on("click", ".chip", function () {
      clubState.region = $(this).data("region");
      $("#regionChips .chip").removeClass("on"); $(this).addClass("on"); drawClubs();
    });
    $("#clubSearch").on("input", function () { clubState.q = this.value.trim().toLowerCase(); drawClubs(); });
    $("#clubList").on("click keydown", ".club", function (e) {
      if (e.type === "keydown" && e.key !== "Enter" && e.key !== " ") return;
      if ($(e.target).closest("a").length) return;
      e.preventDefault();
      clubState.sel = $(this).data("id"); drawClubs(); AAMap.focus(clubState.sel);
    });
    function usePos(p) { clubState.pos = p; AAMap.showMe(p); drawClubs(); $("#nearMsg").text("Sorted by distance from your position."); }
    $("#nearMe").on("click", function () {
      if (window.AA_USER_POS) { usePos(window.AA_USER_POS); return; }
      if (!navigator.geolocation) { $("#nearMsg").text("This browser does not support geolocation."); return; }
      $("#nearMsg").text("Asking for your location...");
      navigator.geolocation.getCurrentPosition(function (pos) {
        window.AA_USER_POS = { lat: pos.coords.latitude, lng: pos.coords.longitude }; usePos(window.AA_USER_POS);
      }, function () { $("#nearMsg").text("Location permission was not given, so distances are not shown."); });
    });
    $(document).off("aa:position.clubs").on("aa:position.clubs", function (e, p) { if (location.hash.indexOf("clubs") > -1) usePos(p); });
  };
  AFTER.gallery = function () {
    galGrid();
    var modal = new bootstrap.Modal(document.getElementById("lightbox"));
    $("#galChips").on("click", ".chip", function () {
      gal.cat = $(this).data("cat"); $("#galChips .chip").removeClass("on"); $(this).addClass("on"); galGrid();
    });
    $("#galGrid").on("click", ".g-item", function () { lbShow(+$(this).data("i")); modal.show(); });
  };

  /* ---------- router ---------- */
  function route() {
    var r = (location.hash.replace(/^#\/?/, "") || "home").split("?")[0];
    return PAGES[r] ? r : "home";
  }
  function setActive(r) {
    $(".main-nav .active").removeClass("active").removeAttr("aria-current");
    var $a = $('.main-nav [data-route="' + r + '"]').addClass("active").attr("aria-current", "page");
    if ($a.hasClass("dropdown-item")) $('.main-nav [data-group="about"]').addClass("active");
    var c = document.getElementById("mainMenu");
    if (c && c.classList.contains("show")) bootstrap.Collapse.getOrCreateInstance(c).hide();
  }
  var first = true;
  function go() {
    var r = route();
    setActive(r);
    var $v = $("#view");
    AAMap.destroy();
    $v.stop(true, true).fadeOut(first ? 0 : 180, function () {
      $v.off(); // drop handlers from the previous page
      $v.html(PAGES[r]());
      if (AFTER[r]) AFTER[r]();
      document.title = (r === "home" ? "Alpine Ascents | Mountaineering guide" : TITLES[r] + " | Alpine Ascents");
      window.scrollTo(0, 0);
      $v.fadeIn(first ? 400 : 260, function () {
        var h = $v.find("h1").first(); if (h.length && !first) h.attr("tabindex", "-1").trigger("focus");
        first = false;
      });
    });
  }

  $(document).on("click", ".lb-prev", function () { lbShow(gal.i - 1); });
  $(document).on("click", ".lb-next", function () { lbShow(gal.i + 1); });
  $(document).on("keydown", function (e) {
    if (!$("#lightbox").hasClass("show")) return;
    if (e.key === "ArrowLeft") lbShow(gal.i - 1);
    if (e.key === "ArrowRight") lbShow(gal.i + 1);
  });
  // clicking the dropdown title itself should not jump anywhere
  $(document).on("click", '.dropdown-toggle[href="#"]', function (e) { e.preventDefault(); });

  $(function () {
    loadData().then(function () {
      $(window).on("hashchange", go);
      go();
    }).catch(function (err) {
      $("#view").html('<div class="container-xl py-5"><div class="alert alert-danger"><strong>Could not load the content.</strong> ' + esc(err.message) +
        "<br>Start the small server (<code>npm start</code>) or open the site through a web server.</div></div>");
    });
  });
})(jQuery);
