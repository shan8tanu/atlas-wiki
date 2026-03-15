/**
 * Atlas — Theme Engine
 *
 * Responsibilities:
 * 1. IntersectionObserver for scroll-triggered reveal animations
 * 2. Page-type class management for Material instant navigation
 * 3. Interactive checklist with localStorage persistence (country pages)
 * 4. Homepage mini-map initialization
 */

(function () {
  "use strict";

  /** Set up scroll-triggered reveals for elements with .atlas-reveal */
  function initScrollReveals() {
    var elements = document.querySelectorAll(
      ".atlas-reveal:not(.atlas-visible)"
    );
    if (!elements.length) return;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("atlas-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );

    elements.forEach(function (el) {
      observer.observe(el);
    });
  }

  /**
   * Update body class based on page type marker.
   * Material's instant navigation does XHR page swaps without full
   * page reloads, so we re-check for the data-atlas-page marker on
   * every navigation and update the body class accordingly.
   */
  function updatePageClass() {
    // Remove old atlas-page-- classes
    var classes = document.body.className;
    document.body.className = classes
      .replace(/\batlas-page--\S+/g, "")
      .replace(/\s{2,}/g, " ")
      .trim();

    // Add new class if a page-type marker exists
    var marker = document.querySelector("[data-atlas-page]");
    if (marker) {
      document.body.classList.add(
        "atlas-page--" + marker.dataset.atlasPage
      );
    }
  }

  /**
   * Interactive checklist with localStorage persistence.
   * Each country page has a checklist where users can track their
   * visa application progress. State is saved per-country using
   * the key pattern: atlas-checklist-{country-slug}
   */
  function initChecklist() {
    var checklist = document.querySelector(".atlas-checklist");
    if (!checklist) return;

    var countrySlug = checklist.dataset.country;
    if (!countrySlug) return;

    var storageKey = "atlas-checklist-" + countrySlug;

    // Restore saved state from localStorage
    var saved = {};
    try {
      saved = JSON.parse(localStorage.getItem(storageKey)) || {};
    } catch (e) {
      saved = {};
    }

    var checkboxes = checklist.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function (cb) {
      var key = cb.dataset.key;
      if (!key) return;

      // Restore saved state (explicit reset handles instant nav carry-over)
      cb.checked = !!saved[key];

      // Save on every change
      cb.addEventListener("change", function () {
        saved[key] = cb.checked;
        localStorage.setItem(storageKey, JSON.stringify(saved));
      });
    });
  }

  /**
   * Visa-type selector — prominent tab strip above the Document Checklist.
   * Switching tabs shows only the process-specific checklist items for that
   * visa type. State persists per country: atlas-vtype-{country-slug}
   */
  function initVisaTypeSelector() {
    var selector = document.querySelector(".atlas-vtype-selector");
    if (!selector) return;

    var countrySlug = selector.dataset.country;
    var storageKey = "atlas-vtype-" + countrySlug;

    // Find the associated checklist (two siblings down: occ-selector, then checklist)
    var checklist = null;
    var sibling = selector.nextElementSibling;
    while (sibling) {
      if (sibling.classList.contains("atlas-checklist")) {
        checklist = sibling;
        break;
      }
      sibling = sibling.nextElementSibling;
    }
    if (!checklist) return;

    // Determine the default: first tab's data-vtype
    var firstBtn = selector.querySelector(".atlas-vtype-tab");
    var defaultVtype = firstBtn ? firstBtn.dataset.vtype : null;
    var saved = localStorage.getItem(storageKey) || defaultVtype;

    // Validate saved value is still a real tab (guards against stale data)
    var validVtypes = Array.from(selector.querySelectorAll(".atlas-vtype-tab"))
      .map(function (b) { return b.dataset.vtype; });
    if (validVtypes.indexOf(saved) === -1) saved = defaultVtype;

    function activate(vtype) {
      // Update tab active state
      selector.querySelectorAll(".atlas-vtype-tab").forEach(function (btn) {
        var isActive = btn.dataset.vtype === vtype;
        btn.classList.toggle("atlas-vtype-tab--active", isActive);
        btn.setAttribute("aria-selected", isActive ? "true" : "false");
      });
      // Show/hide visa-type-specific checklist items
      checklist.querySelectorAll(".atlas-checklist__item--vtype").forEach(function (item) {
        item.hidden = item.dataset.vtype !== vtype;
      });
      // Uncheck hidden items so they don't pollute saved state
      checklist.querySelectorAll(".atlas-checklist__item--vtype[hidden] input").forEach(function (cb) {
        cb.checked = false;
      });
      localStorage.setItem(storageKey, vtype);
    }

    // Restore saved selection
    activate(saved);

    // Wire tab clicks
    selector.querySelectorAll(".atlas-vtype-tab").forEach(function (btn) {
      btn.addEventListener("click", function () { activate(btn.dataset.vtype); });
    });
  }

  /**
   * Occupation-type selector — pill tabs above the Document Checklist.
   * Switches which financial proof items are visible. Selection persists
   * in localStorage per country using key: atlas-occ-{country-slug}
   */
  function initOccupationSelector() {
    var selector = document.querySelector(".atlas-occ-selector");
    if (!selector) return;

    var checklist = selector.nextElementSibling; // .atlas-checklist
    if (!checklist) return;

    var countrySlug = checklist.dataset.country;
    var storageKey = "atlas-occ-" + countrySlug;
    var saved = localStorage.getItem(storageKey) || "salaried";

    function activate(occ) {
      // Update button active state
      selector.querySelectorAll(".atlas-occ-btn").forEach(function (btn) {
        btn.classList.toggle("atlas-occ-btn--active", btn.dataset.occ === occ);
      });
      // Show/hide checklist items by occupation type
      checklist.querySelectorAll(".atlas-checklist__item--occ").forEach(function (item) {
        item.hidden = item.dataset.occ !== occ;
      });
      localStorage.setItem(storageKey, occ);
    }

    // Restore saved selection on page load
    activate(saved);

    // Wire button clicks
    selector.querySelectorAll(".atlas-occ-btn").forEach(function (btn) {
      btn.addEventListener("click", function () { activate(btn.dataset.occ); });
    });
  }

  /**
   * Cover letter copy-to-clipboard button.
   * Copies the <pre> text and flashes "Copied!" for 2 seconds.
   */
  function initCoverLetter() {
    var btn = document.querySelector(".atlas-cover-letter__copy");
    if (!btn) return;

    btn.addEventListener("click", function () {
      var text = btn.closest(".atlas-cover-letter__body")
                    .querySelector(".atlas-cover-letter__text").innerText;
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = "Copied!";
        setTimeout(function () { btn.textContent = "Copy to clipboard"; }, 2000);
      });
    });
  }

  /**
   * Homepage mini-map: fetches the SVG world map and map-data.json,
   * renders a small colored preview in the bottom-right corner.
   * Clicking it navigates to the full /map/ page.
   */
  function initMiniMap() {
    if (!document.body.classList.contains("atlas-page--home")) return;
    var container = document.getElementById("atlas-minimap");
    if (!container || container.dataset.loaded) return;

    var COLORS = {
      1: "#2ecc71",
      2: "#3498db",
      3: "#f39c12",
      4: "#e74c3c",
      5: "#8e44ad",
    };
    var NO_DATA = "#dcdcdc";

    // Fetch map page and map data in parallel
    Promise.all([
      fetch("map/").then(function (r) { return r.text(); }),
      fetch("map-data.json").then(function (r) { return r.json(); }),
    ])
      .then(function (results) {
        var mapHtml = results[0];
        var mapData = results[1];

        // Extract the SVG from the map page
        var parser = new DOMParser();
        var doc = parser.parseFromString(mapHtml, "text/html");
        var svg = doc.getElementById("world-map");
        if (!svg) return;

        // Clone the SVG and insert into mini-map
        var clone = svg.cloneNode(true);
        clone.removeAttribute("id");
        clone.setAttribute("aria-hidden", "true");

        // Color the paths using map data
        var allPaths = clone.querySelectorAll("path");
        allPaths.forEach(function (path) {
          var id = path.id || (path.parentElement && path.parentElement.id);
          if (!id || id.charAt(0) === "_") {
            path.style.fill = NO_DATA;
            return;
          }
          var data = mapData[id];
          if (data && data.difficulty && COLORS[data.difficulty]) {
            path.style.fill = COLORS[data.difficulty];
          } else {
            path.style.fill = NO_DATA;
          }
          // Remove individual IDs to avoid DOM ID conflicts
          path.removeAttribute("id");
        });

        // Also handle <g> groups (remove their IDs too)
        var groups = clone.querySelectorAll("g[id]");
        groups.forEach(function (g) {
          var gid = g.id;
          g.removeAttribute("id");
          var childPaths = g.querySelectorAll("path");
          childPaths.forEach(function (p) {
            var data = mapData[gid];
            if (data && data.difficulty && COLORS[data.difficulty]) {
              p.style.fill = COLORS[data.difficulty];
            } else {
              p.style.fill = NO_DATA;
            }
          });
        });

        var inner = container.querySelector(".atlas-minimap__inner");
        if (inner) {
          inner.appendChild(clone);
        }

        container.dataset.loaded = "true";
        container.classList.add("atlas-minimap--loaded");
      })
      .catch(function () {
        // Silently fail — mini-map is non-critical
      });

    // Click handler — navigate to full map
    container.addEventListener("click", function () {
      window.location.href = "map/";
    });
    container.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        window.location.href = "map/";
      }
    });
  }

  // ── Initial page load ─────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    initScrollReveals();
    updatePageClass();
    initChecklist();
    initVisaTypeSelector();
    initOccupationSelector();
    initCoverLetter();
    initMiniMap();
  });

  // ── Material instant navigation re-initialization ─────────────────
  // document$ is an RxJS observable exposed by Material for MkDocs.
  // It fires after every instant navigation page swap.
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      initScrollReveals();
      updatePageClass();
      initChecklist();
      initVisaTypeSelector();
      initOccupationSelector();
      initCoverLetter();
      initMiniMap();
    });
  }
})();
