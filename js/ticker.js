/* Bottom ticker: scrolls the current date, time and location.
   Location comes from the HTML5 Geolocation API. If the visitor says no (or the browser
   has no support) we show the time zone instead, so the ticker is never empty. */
(function ($) {
  var state = { place: "finding your location...", coords: "", elev: "" };
  var tips = [
    "Everest's summit air holds roughly a third of the oxygen found at sea level.",
    "Climb high, sleep low: the best advice for staying well at altitude.",
    "Set a turnaround time before you start and keep to it.",
    "Kami Rita Sherpa has stood on Everest 32 times.",
    "The Alpine Club in London was founded in 1857."
  ];

  function segment() {
    var now = new Date();
    var date = now.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long", year: "numeric" });
    var time = now.toLocaleTimeString(undefined, { hour12: false });
    var tz = "";
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone; } catch (e) {}
    return '<span class="ticker-seg">' +
      '<b>Date</b><span class="t-date">' + date + "</span>" +
      '<span class="sep">|</span><b>Time</b><span class="t-time">' + time + "</span>" + (tz ? " <small>(" + tz + ")</small>" : "") +
      '<span class="sep">|</span><b>Location</b><span class="t-loc">' + state.place + state.coords + state.elev + "</span>" +
      '<span class="sep">|</span><b>Did you know?</b>' + tips[Math.floor(now.getMinutes() / 12) % tips.length] +
      '<span class="sep">&#9650;</span></span>';
  }

  function build() {
    // two identical halves so the loop is seamless (the CSS moves the track by -50%)
    var one = segment();
    var $t = $("#tickerTrack").empty();
    var copies = 2;
    var half = $('<div class="ticker-half" style="display:flex"></div>');
    half.append(one);
    $t.append(half.clone());
    // make sure one half is wider than the screen, otherwise there would be a gap
    var need = Math.max(1, Math.ceil(window.innerWidth / Math.max(1, $t.children().first().width())));
    var first = $t.children().first();
    for (var i = 1; i < need; i++) first.append(one);
    $t.append(first.clone());
    $t.css("--tick-s", Math.max(30, Math.round(first.width() / 70)) + "s");
  }

  function tick() {
    var now = new Date();
    var time = now.toLocaleTimeString(undefined, { hour12: false });
    var date = now.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long", year: "numeric" });
    $("#tickerTrack .t-time").text(time);
    $("#tickerTrack .t-date").text(date);
  }

  function refreshLoc() {
    $("#tickerTrack .t-loc").text(state.place + state.coords + state.elev);
  }

  function withTimeout(url, ms) {
    var ctl = ("AbortController" in window) ? new AbortController() : null;
    if (ctl) setTimeout(function () { ctl.abort(); }, ms);
    return fetch(url, ctl ? { signal: ctl.signal } : {}).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
  }

  function fallbackPlace(msg) {
    var tz = "";
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone; } catch (e) {}
    state.place = (tz ? tz.replace(/_/g, " ").split("/").pop() + " area (from your time zone)" : "unknown") + " - " + msg;
    state.coords = ""; state.elev = "";
    refreshLoc();
  }

  function locate() {
    if (!("geolocation" in navigator)) { fallbackPlace("this browser has no geolocation"); return; }
    state.place = "asking for your location...";
    refreshLoc();
    navigator.geolocation.getCurrentPosition(function (pos) {
      var lat = pos.coords.latitude, lng = pos.coords.longitude;
      state.coords = " (" + Math.abs(lat).toFixed(2) + "\u00b0" + (lat >= 0 ? "N" : "S") + ", " + Math.abs(lng).toFixed(2) + "\u00b0" + (lng >= 0 ? "E" : "W") + ")";
      state.place = "your position";
      refreshLoc();
      window.AA_USER_POS = { lat: lat, lng: lng };
      $(document).trigger("aa:position", [window.AA_USER_POS]);

      // place name (free service, no key). If it fails the coordinates are still shown.
      withTimeout("https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=" + lat + "&longitude=" + lng + "&localityLanguage=en", 6000)
        .then(function (j) {
          var parts = [j.city || j.locality, j.principalSubdivision, j.countryName].filter(Boolean);
          if (parts.length) { state.place = parts.filter(function (p, i, a) { return a.indexOf(p) === i; }).join(", "); refreshLoc(); }
        }).catch(function () {});

      // height above sea level: device altitude if given, otherwise ask a free elevation service
      if (pos.coords.altitude != null && !isNaN(pos.coords.altitude)) {
        state.elev = " | " + Math.round(pos.coords.altitude) + " m above sea level"; refreshLoc();
      } else {
        withTimeout("https://api.open-meteo.com/v1/elevation?latitude=" + lat + "&longitude=" + lng, 6000)
          .then(function (j) { if (j.elevation && j.elevation.length) { state.elev = " | " + Math.round(j.elevation[0]) + " m above sea level"; refreshLoc(); } })
          .catch(function () {});
      }
    }, function (err) {
      fallbackPlace(err && err.code === 1 ? "location permission was not given" : "location not available");
    }, { enableHighAccuracy: false, timeout: 10000, maximumAge: 600000 });
  }

  $(function () {
    build();
    setInterval(tick, 1000);
    $(window).on("resize", (function () { var t; return function () { clearTimeout(t); t = setTimeout(build, 300); }; })());
    $("#tickerToggle").on("click", function () {
      var paused = $("#ticker").toggleClass("paused").hasClass("paused");
      $(this).attr("aria-label", paused ? "Play ticker" : "Pause ticker").find("i").attr("class", paused ? "bi bi-play-fill" : "bi bi-pause-fill");
    });
    $("#tickerLoc").on("click", locate);
    locate();
  });
})(jQuery);
