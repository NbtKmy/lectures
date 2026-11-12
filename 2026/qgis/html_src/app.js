/* Tabs, hash routing, lazy map start-up and the shared basemap. */
(function () {
  "use strict";

  window.DATA = JSON.parse(document.getElementById("session-data").textContent);
  window.MapInit = window.MapInit || {};

  var IDS = ["task1", "task2", "task3", "limits"];
  var tabs = Array.prototype.slice.call(document.querySelectorAll("button[data-tab]"));
  var panels = Array.prototype.slice.call(document.querySelectorAll("section[data-panel]"));
  var tabbar = document.getElementById("tabs");
  var maps = (window.SessionMaps = {}); // exposed for console checks

  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function showTab(id, opts) {
    if (IDS.indexOf(id) < 0) id = "task1";
    tabs.forEach(function (t) {
      var on = t.getAttribute("data-tab") === id;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
    });
    panels.forEach(function (p) {
      p.hidden = p.getAttribute("data-panel") !== id;
    });

    // Leaflet must start (and be resized) once its container is visible.
    var panel = document.querySelector('section[data-panel="' + id + '"]');
    var box = panel && panel.querySelector("[data-map]");
    if (box) {
      if (!maps[id] && typeof window.MapInit[id] === "function") {
        try {
          maps[id] = window.MapInit[id](box, window.DATA[id]);
        } catch (err) {
          console.error("map " + id + " failed", err);
        }
      } else if (maps[id]) {
        maps[id].invalidateSize();
      }
    }

    // Keep the active tab visible inside the (possibly horizontally scrolling) tab strip.
    // Set scrollLeft directly: scrollIntoView would also scroll the page past the landing.
    var active = tabs.filter(function (t) { return t.getAttribute("data-tab") === id; })[0];
    var strip = active && active.parentNode;
    if (strip) strip.scrollLeft = active.offsetLeft - (strip.clientWidth - active.offsetWidth) / 2;
    if (opts && opts.scroll && tabbar) {
      tabbar.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
    }
  }

  function idFromHash() {
    var id;
    try {
      id = decodeURIComponent(location.hash.replace(/^#/, ""));
    } catch (err) {
      id = ""; // malformed %-escape such as "#%": fall back to the default tab
    }
    return IDS.indexOf(id) >= 0 ? id : "task1";
  }

  function known() {
    return IDS.indexOf(location.hash.replace(/^#/, "")) >= 0;
  }

  tabs.forEach(function (t) {
    t.addEventListener("click", function () {
      var id = t.getAttribute("data-tab");
      if (location.hash === "#" + id) showTab(id);
      else location.hash = id; // adds a history entry; hashchange shows it
    });
    t.addEventListener("keydown", function (e) {
      var i = tabs.indexOf(t);
      var next = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : e.key === "Home" ? 0 : e.key === "End" ? tabs.length - 1 : null;
      if (next === null) return;
      e.preventDefault();
      var target = tabs[(next + tabs.length) % tabs.length];
      target.focus();
      target.click();
    });
  });

  function onNavigate() {
    showTab(idFromHash(), { scroll: known() });
  }
  window.addEventListener("hashchange", onNavigate);
  window.addEventListener("popstate", onNavigate);

  window.showTab = showTab;

  /* Shared basemap: GSI pale tiles, darkened by CSS. Offline => plain dark background. */
  window.makeBaseMap = function (container, options) {
    var map = L.map(container, Object.assign({ zoomControl: true, attributionControl: true }, options));
    var tiles = L.tileLayer("https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html">地理院タイル</a>',
    });
    tiles.on("tileerror", function () { /* offline: keep the dark background */ });
    tiles.addTo(map);
    return map;
  };

  onNavigate();
})();
