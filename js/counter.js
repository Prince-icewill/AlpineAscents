/* Visitor counter, shown top right next to the logo.
   With the small node server running (npm start) the count is kept in data/visitors.json
   and is shared by everyone. Without it (file:// or plain static hosting) it falls back to a
   count kept in this browser only. A visit is counted once per browser session. */
(function ($) {
  var $el = $("#visitorCount");

  function show(n) {
    var s = String(n).padStart(6, "0");
    $el.html(s.split("").map(function (d) { return '<span class="d">' + d + "</span>"; }).join(""));
    $el.attr("aria-label", "Visitor count " + n);
  }

  function localFallback() {
    var n = 0;
    try {
      n = parseInt(localStorage.getItem("aa_visits") || "0", 10) || 0;
      if (!sessionStorage.getItem("aa_counted")) {
        n += 1;
        localStorage.setItem("aa_visits", String(n));
        sessionStorage.setItem("aa_counted", "1");
      }
    } catch (e) { n = n || 1; }
    show(n);
    $(".visitor-box").attr("title", "Visitors counted on this browser (start the node server for a shared count)");
  }

  show(0);
  if (location.protocol === "file:") { localFallback(); return; }

  var counted = false;
  try { counted = !!sessionStorage.getItem("aa_counted"); } catch (e) {}

  fetch("api/visit" + (counted ? "" : "?hit=1"), { method: counted ? "GET" : "POST", cache: "no-store" })
    .then(function (r) { if (!r.ok) throw new Error("no api"); return r.json(); })
    .then(function (j) {
      show(j.count);
      try { sessionStorage.setItem("aa_counted", "1"); } catch (e) {}
    })
    .catch(localFallback);
})(jQuery);
