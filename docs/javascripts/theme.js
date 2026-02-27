/**
 * Atlas — Theme Engine
 *
 * Two responsibilities:
 * 1. IntersectionObserver for scroll-triggered reveal animations
 * 2. Cleanup of per-country accent styles when navigating away via
 *    Material's instant navigation (which doesn't reload <head>)
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
   * Clean up per-country accent styles when navigating to a non-country page.
   * Material's navigation.instant mode does XHR page swaps without reloading
   * <head>, so a country's inline <style id="atlas-theme-style"> persists
   * when navigating to the Map or Contribute page. This function detects
   * that and removes the stale style tag.
   */
  function cleanupThemeStyle() {
    var themeStyle = document.getElementById("atlas-theme-style");
    var countryMotif = document.querySelector('[data-atlas-page="country"]');

    // If there's a theme style but we're NOT on a country page, remove it
    if (themeStyle && !countryMotif) {
      themeStyle.remove();
    }
  }

  // ── Initial page load ─────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    initScrollReveals();
  });

  // ── Material instant navigation re-initialization ─────────────────
  // document$ is an RxJS observable exposed by Material for MkDocs.
  // It fires after every instant navigation page swap.
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      initScrollReveals();
      cleanupThemeStyle();
    });
  }
})();
