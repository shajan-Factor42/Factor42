/* Factor42 Media — site behaviour (progressive enhancement; every page works without it) */
(function () {
  var root = document.documentElement;
  root.classList.remove("no-js");
  root.classList.add("js");

  // Mobile menu
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".menu-toggle");
  if (header && toggle) {
    toggle.addEventListener("click", function () {
      var open = header.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }

  // Solutions dropdown: click/Enter toggles, Escape and outside click close (hover and focus open it via CSS)
  var dd = document.querySelector(".has-dd");
  if (dd) {
    var ddBtn = dd.querySelector(".dd-toggle");
    var setDd = function (open) { dd.classList.toggle("is-open", open); ddBtn.setAttribute("aria-expanded", open ? "true" : "false"); };
    ddBtn.addEventListener("click", function () { setDd(!dd.classList.contains("is-open")); });
    dd.addEventListener("mouseenter", function () { ddBtn.setAttribute("aria-expanded", "true"); });
    dd.addEventListener("mouseleave", function () { if (!dd.classList.contains("is-open")) ddBtn.setAttribute("aria-expanded", "false"); });
    document.addEventListener("click", function (e) { if (!dd.contains(e.target)) setDd(false); });
    dd.addEventListener("keydown", function (e) { if (e.key === "Escape") { setDd(false); ddBtn.focus(); } });
    dd.addEventListener("focusout", function (e) { if (!dd.contains(e.relatedTarget)) setDd(false); });
  }

  // Channel tabs (homepage)
  var tablist = document.querySelector("[role=tablist]");
  if (tablist) {
    var tabs = Array.prototype.slice.call(tablist.querySelectorAll("[role=tab]"));
    var select = function (tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
    };
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(tab, false); });
      tab.addEventListener("keydown", function (e) {
        var next = null;
        if (e.key === "ArrowDown" || e.key === "ArrowRight") next = tabs[(i + 1) % tabs.length];
        if (e.key === "ArrowUp" || e.key === "ArrowLeft") next = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === "Home") next = tabs[0];
        if (e.key === "End") next = tabs[tabs.length - 1];
        if (next) { e.preventDefault(); select(next, true); }
      });
    });
    select(tabs[0], false);
  }

  // Blog topic filter
  var filterBar = document.querySelector(".filters");
  if (filterBar) {
    filterBar.hidden = false;
    var cards = document.querySelectorAll(".post-card");
    filterBar.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-filter]");
      if (!btn) return;
      var f = btn.getAttribute("data-filter");
      filterBar.querySelectorAll("[data-filter]").forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      cards.forEach(function (c) { c.classList.toggle("is-hidden", f !== "all" && c.getAttribute("data-cat") !== f); });
    });
  }

  // Consultation form: send visitors to this site's thank-you page, wherever it is hosted
  var form = document.querySelector("form[data-consult]");
  if (form) {
    var redirect = form.querySelector("input[name=redirect]");
    if (redirect) redirect.value = new URL("thank-you", window.location.href).href;
    var page = form.querySelector("input[name=page]");
    if (page) page.value = window.location.href;
    var error = form.querySelector(".form-error");
    if (/[?&]error=1/.test(window.location.search)) {
      var sendErr = form.querySelector(".form-error--send");
      if (sendErr) sendErr.classList.add("is-visible");
    }
    form.addEventListener("submit", function (e) {
      if (!form.checkValidity()) {
        e.preventDefault();
        if (error) { error.classList.add("is-visible"); }
        var firstBad = form.querySelector(":invalid");
        if (firstBad) firstBad.focus();
      }
    });
  }
})();
