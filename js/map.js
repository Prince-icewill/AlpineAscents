/* Map for the clubs page. Leaflet + OpenStreetMap tiles (no API key needed).
   Each club also has an "Open in Google Maps" link on its card. */
window.AAMap = (function ($) {
  var map = null, markers = {}, meMarker = null;

  function km(a, b) {
    var R = 6371, r = Math.PI / 180;
    var dLat = (b.lat - a.lat) * r, dLng = (b.lng - a.lng) * r;
    var x = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
    return 2 * R * Math.asin(Math.sqrt(x));
  }

  function popup(c) {
    var link = c.url ? '<br><a href="' + c.url + '" target="_blank" rel="noopener">Website</a> &middot; ' : "<br>";
    return "<strong>" + c.name + "</strong><br>" + c.city + ", " + c.country + (c.founded ? "<br>Founded " + c.founded : "") +
      link + '<a href="https://www.google.com/maps/search/?api=1&query=' + c.lat + "," + c.lng + '" target="_blank" rel="noopener">Google Maps</a>';
  }

  function init(el, clubs, onPick) {
    destroy();
    if (typeof L === "undefined") { $(el).html('<div class="p-4">The map library did not load.</div>'); return; }
    L.Icon.Default.imagePath = "vendor/leaflet/images/";
    map = L.map(el, { worldCopyJump: true, minZoom: 2 }).setView([30, 40], 2);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'
    }).addTo(map);
    markers = {};
    clubs.forEach(function (c) {
      var m = L.marker([c.lat, c.lng], { title: c.name }).addTo(map).bindPopup(popup(c));
      m.on("click", function () { if (onPick) onPick(c.id); });
      markers[c.id] = m;
    });
    var b = L.latLngBounds(clubs.map(function (c) { return [c.lat, c.lng]; }));
    map.fitBounds(b.pad(0.1));
    setTimeout(function () { map && map.invalidateSize(); }, 200);
  }

  function focus(id) {
    if (!map || !markers[id]) return;
    map.flyTo(markers[id].getLatLng(), Math.max(map.getZoom(), 6), { duration: 0.9 });
    markers[id].openPopup();
  }

  function showMe(pos) {
    if (!map) return;
    if (meMarker) map.removeLayer(meMarker);
    meMarker = L.marker([pos.lat, pos.lng], { icon: L.divIcon({ className: "", html: '<div class="me-dot"></div>', iconSize: [16, 16] }), title: "You are here" }).addTo(map).bindPopup("You are here");
  }

  function show(ids) {
    if (!map) return;
    Object.keys(markers).forEach(function (id) {
      var on = ids.indexOf(id) > -1;
      if (on && !map.hasLayer(markers[id])) markers[id].addTo(map);
      if (!on && map.hasLayer(markers[id])) map.removeLayer(markers[id]);
    });
  }

  function destroy() { if (map) { map.remove(); map = null; markers = {}; meMarker = null; } }

  return { init: init, focus: focus, showMe: showMe, show: show, destroy: destroy, km: km };
})(jQuery);
