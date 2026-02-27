(function () {
  "use strict";

  var COLORS = {
    1: "#2ecc71", // Visa-Free
    2: "#3498db", // e-Visa
    3: "#f39c12", // Visa on Arrival
    4: "#e74c3c", // Standard Visa
    5: "#8e44ad", // Restricted
  };
  var LABELS = {
    1: "Visa-Free",
    2: "e-Visa",
    3: "Visa on Arrival",
    4: "Standard Visa",
    5: "Restricted",
  };
  var NO_DATA_COLOR = "#dcdcdc";

  function initMap() {
    var svg = document.getElementById("world-map");
    if (!svg) return;

    var tooltip = document.getElementById("map-tooltip");
    var paths = svg.querySelectorAll("path");

    // The map page lives at /map/index.html but map-data.json is at site root.
    // "../map-data.json" from /map/ always resolves to /map-data.json (site root).
    fetch("../map-data.json")
      .then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(function (data) {
        applyMapData(svg, paths, data, tooltip);
      })
      .catch(function () {
        // If fetch fails (e.g., file:// protocol), still make the map interactive
        applyMapData(svg, paths, {}, tooltip);
      });
  }

  function applyMapData(svg, paths, data, tooltip) {
    // Country URLs in map-data.json are relative to site root (e.g., "japan/").
    // Since the map page is at /map/, we prepend "../" to navigate correctly.
    var urlPrefix = "../";

    // Build a set of all country path elements (skip groups, non-country elements)
    paths.forEach(function (path) {
      var id = path.id || (path.parentElement && path.parentElement.id);
      if (!id || id === "world-map" || id.charAt(0) === "_") return;

      var countryData = data[id];

      if (countryData && countryData.difficulty && COLORS[countryData.difficulty]) {
        // Country has data — color it by difficulty
        path.style.fill = COLORS[countryData.difficulty];
        path.classList.add("map-country", "map-country--active");

        path.addEventListener("click", function () {
          window.location.href = urlPrefix + countryData.url;
        });

        addTooltipListeners(path, tooltip, function () {
          return (
            '<strong>' + countryData.name + '</strong><br>' +
            '<span class="map-tooltip__badge map-tooltip__badge--' + countryData.difficulty + '">' +
            LABELS[countryData.difficulty] + '</span>'
          );
        });
      } else {
        // No data — gray, "Coming Soon" tooltip
        path.style.fill = NO_DATA_COLOR;
        path.classList.add("map-country", "map-country--disabled");

        var countryName = id.toUpperCase();
        addTooltipListeners(path, tooltip, function () {
          return '<strong>' + countryName + '</strong><br><em>Coming Soon</em>';
        });
      }
    });

    // Also handle grouped countries (<g id="xx"> with child paths)
    var groups = svg.querySelectorAll("g[id]");
    groups.forEach(function (g) {
      var id = g.id;
      if (id === "world-map" || id.charAt(0) === "_") return;
      var countryData = data[id];
      var childPaths = g.querySelectorAll("path");

      childPaths.forEach(function (path) {
        if (countryData && countryData.difficulty && COLORS[countryData.difficulty]) {
          path.style.fill = COLORS[countryData.difficulty];
          path.classList.add("map-country", "map-country--active");

          path.addEventListener("click", function () {
            window.location.href = urlPrefix + countryData.url;
          });

          addTooltipListeners(path, tooltip, function () {
            return (
              '<strong>' + countryData.name + '</strong><br>' +
              '<span class="map-tooltip__badge map-tooltip__badge--' + countryData.difficulty + '">' +
              LABELS[countryData.difficulty] + '</span>'
            );
          });
        } else {
          path.style.fill = NO_DATA_COLOR;
          path.classList.add("map-country", "map-country--disabled");

          var countryName = id.toUpperCase();
          addTooltipListeners(path, tooltip, function () {
            return '<strong>' + countryName + '</strong><br><em>Coming Soon</em>';
          });
        }
      });
    });
  }

  function addTooltipListeners(el, tooltip, contentFn) {
    el.addEventListener("mouseenter", function (e) {
      tooltip.innerHTML = contentFn();
      tooltip.style.display = "block";
      positionTooltip(tooltip, e);
    });

    el.addEventListener("mousemove", function (e) {
      positionTooltip(tooltip, e);
    });

    el.addEventListener("mouseleave", function () {
      tooltip.style.display = "none";
    });
  }

  function positionTooltip(tooltip, e) {
    var x = e.pageX + 12;
    var y = e.pageY - 28;

    // Prevent tooltip from overflowing viewport right edge
    if (x + tooltip.offsetWidth > window.innerWidth + window.scrollX - 16) {
      x = e.pageX - tooltip.offsetWidth - 12;
    }

    tooltip.style.left = x + "px";
    tooltip.style.top = y + "px";
  }

  // Initialize when DOM is ready (works with MkDocs Material instant loading)
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMap);
  } else {
    initMap();
  }

  // Re-initialize on MkDocs Material instant navigation
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      initMap();
    });
  }
})();
