/* Factor42 website chat bubble (adapted from the Deep Thought chat, 2026-10-10).
   Talks to the shared chat relay (Deep Thought repo, chat-worker/) at this script tag's data-endpoint;
   the relay sees the request comes from factor42media.com and answers as Factor42.
   No libraries. Loads after the page is idle so it doesn't slow the first paint.
   GA4/GTM events: chat_open, chat_message, chat_link_click, chat_error. Added 2026-10-01. */
(function () {
  if (window.__F42_CHAT) return;
  window.__F42_CHAT = true;
  var me = document.currentScript;
  var ENDPOINT = me && me.getAttribute("data-endpoint");
  if (!ENDPOINT) return;

  var KEY = "f42-chat-v1";
  var BOOK = "https://factor42media.com/contact";
  var GREETING = "Hi, I'm Factor42's assistant. Ask me how white-label fulfillment works, which channels we run, or how to get started.";
  var CHIPS = ["How does white-label work?", "Which channels do you run?", "What does it cost?", "Will my clients know?"];

  function track(event, extra) {
    try { (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: event }, extra || {})); } catch (e) {}
  }
  function load() { try { return JSON.parse(sessionStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function save(m) { try { sessionStorage.setItem(KEY, JSON.stringify(m.slice(-24))); } catch (e) {} }

  var EVENT = ENDPOINT.replace(/\/chat$/, "/event");
  // Conversation id: date (New York) + random, so the daily digest can find yesterday's chats.
  function newConv() {
    var d = new Intl.DateTimeFormat("en-CA", { timeZone: "America/New_York" }).format(new Date()).replace(/-/g, "");
    return d + "-" + Math.random().toString(36).slice(2, 12);
  }
  var CONV = (function () { try { return sessionStorage.getItem(KEY + "-id") || (function (c) { sessionStorage.setItem(KEY + "-id", c); return c; })(newConv()); } catch (e) { return newConv(); } })();
  function booked() {
    try { fetch(EVENT, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ type: "booking", conv: CONV }), keepalive: true }); } catch (e) {}
  }

  var messages = load();
  var busy = false;

  var css = "\
#dtc-btn{position:fixed;right:20px;bottom:20px;z-index:2147483000;width:60px;height:60px;border-radius:50%;border:0;cursor:pointer;\
background:#C2410C;color:#fff;box-shadow:0 10px 30px rgba(194,65,12,.35);display:flex;align-items:center;justify-content:center;transition:transform .15s}\
#dtc-btn:hover{transform:translateY(-2px)}#dtc-btn:focus-visible{outline:3px solid #F4A26B;outline-offset:3px}\
#dtc-btn svg{width:28px;height:28px}\
#dtc-panel{position:fixed;right:20px;bottom:92px;z-index:2147483001;width:380px;max-width:calc(100vw - 32px);height:560px;max-height:calc(100vh - 120px);\
background:#fff;border-radius:18px;box-shadow:0 24px 60px rgba(11,22,38,.22);display:none;flex-direction:column;overflow:hidden;\
font-family:Geist,system-ui,-apple-system,'Segoe UI',sans-serif;color:#26303F;border:1px solid #E6E2DA}\
#dtc-panel.open{display:flex}\
#dtc-head{padding:16px 18px;background:#0B1626;border-bottom:3px solid #C2410C;color:#fff;display:flex;align-items:center;gap:12px}\
#dtc-head b{font-family:'Schibsted Grotesk',Geist,system-ui,sans-serif;font-size:16px;font-weight:700;display:block}\
#dtc-head span{font-size:12.5px;color:#B8BFCC}\
#dtc-x{margin-left:auto;background:none;border:0;color:#cbd5e1;font-size:24px;line-height:1;cursor:pointer;padding:4px 6px}\
#dtc-x:focus-visible{outline:2px solid #F4A26B}\
#dtc-log{flex:1;overflow-y:auto;padding:16px;background:#F5F3EE;display:flex;flex-direction:column;gap:10px}\
.dtc-m{max-width:86%;padding:10px 13px;border-radius:14px;font-size:14.5px;line-height:1.55;white-space:pre-wrap;word-wrap:break-word}\
.dtc-a{background:#fff;border:1px solid #E6E2DA;align-self:flex-start;border-bottom-left-radius:4px}\
.dtc-u{background:#C2410C;color:#fff;align-self:flex-end;border-bottom-right-radius:4px}\
.dtc-a a{color:#C2410C;font-weight:600}\
.dtc-chips{display:flex;flex-wrap:wrap;gap:8px}\
.dtc-chip{background:#fff;border:1px solid rgba(194,65,12,.35);color:#9A3412;border-radius:999px;padding:7px 12px;font-size:13px;cursor:pointer;font-family:inherit}\
.dtc-chip:hover{background:#FDF1EA}\
.dtc-dots{display:inline-flex;gap:4px}.dtc-dots i{width:6px;height:6px;border-radius:50%;background:#B8BFCC;animation:dtcb 1s infinite}\
.dtc-dots i:nth-child(2){animation-delay:.15s}.dtc-dots i:nth-child(3){animation-delay:.3s}\
@keyframes dtcb{0%,80%,100%{opacity:.3}40%{opacity:1}}\
#dtc-form{display:flex;gap:8px;padding:12px;border-top:1px solid #e2e8f0;background:#fff}\
#dtc-in{flex:1;border:1px solid #cbd5e1;border-radius:10px;padding:10px 12px;font:inherit;font-size:14.5px;resize:none;max-height:96px;color:#0B1626}\
#dtc-in:focus{outline:2px solid rgba(194,65,12,.4);border-color:#C2410C}\
#dtc-send{border:0;border-radius:10px;padding:0 14px;background:#C2410C;color:#fff;font-weight:600;cursor:pointer;font-family:inherit}\
#dtc-send:disabled{opacity:.5;cursor:default}\
#dtc-foot{font-size:11.5px;color:#4A5264;padding:0 14px 10px;background:#fff}\
#dtc-foot a{color:#4A5264}\
@media (max-width:520px){#dtc-panel{right:0;bottom:0;width:100vw;max-width:100vw;height:100%;max-height:100%;border-radius:0}\
#dtc-btn{right:16px;bottom:16px;width:56px;height:56px}html[data-dtc-open] #dtc-btn{display:none}}\
#dtc-tip{position:fixed;right:92px;bottom:30px;z-index:2147483000;display:none;align-items:center;gap:6px;background:#fff;color:#0B1626;\
border:1px solid #E6E2DA;border-radius:14px;border-bottom-right-radius:4px;box-shadow:0 10px 30px rgba(11,22,38,.15);padding:9px 8px 9px 14px;\
font-family:Geist,system-ui,-apple-system,'Segoe UI',sans-serif;font-size:14px;font-weight:600;cursor:pointer}\
#dtc-tip.show{display:flex}#dtc-tip button{background:none;border:0;color:#4A5264;font-size:18px;line-height:1;cursor:pointer;padding:2px 6px}\
@media (max-width:767px){#dtc-tip{bottom:24px;right:82px}}html[data-dtc-open] #dtc-tip{display:none}\
@media (prefers-reduced-motion:reduce){#dtc-btn{transition:none}.dtc-dots i{animation:none;opacity:.6}}";

  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    for (var k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (html != null) e.innerHTML = html;
    return e;
  }
  function esc(s) { return s.replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  // Minimal, safe formatting: escape everything, then allow **bold** and [text](https://...) links.
  function fmt(s) {
    return esc(s)
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, function (_, t, u) {
        var same = u.indexOf("https://factor42media.com") === 0;
        return '<a href="' + u + '"' + (same ? "" : ' target="_blank" rel="noopener"') + ">" + t + "</a>";
      })
      .replace(/(^|\n)[-•] /g, "$1• ");
  }

  var style = el("style", null, css);
  var btn = el("button", { id: "dtc-btn", type: "button", "aria-label": "Chat with Factor42", "aria-expanded": "false", "aria-controls": "dtc-panel" },
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.5 7.2L4 20l1.1-4.4A8 8 0 1 1 21 12z"/></svg>');
  var panel = el("div", { id: "dtc-panel", role: "dialog", "aria-label": "Factor42 chat", "aria-modal": "false" },
    '<div id="dtc-head"><div><b>Ask Factor42</b><span>AI assistant · usually instant</span></div><button id="dtc-x" type="button" aria-label="Close chat">×</button></div>' +
    '<div id="dtc-log" aria-live="polite"></div>' +
    '<form id="dtc-form"><textarea id="dtc-in" rows="1" maxlength="1200" placeholder="Type your question…" aria-label="Your message"></textarea><button id="dtc-send" type="submit">Send</button></form>' +
    '<div id="dtc-foot">AI answers can be wrong. Chats are saved for 90 days to improve answers; don\'t share sensitive info. <a href="/privacy-policy">Privacy</a> · <a href="' + BOOK + '">Talk to a person</a></div>');

  function mount() {
    document.head.appendChild(style);
    document.body.appendChild(btn);
    document.body.appendChild(panel);
    var log = panel.querySelector("#dtc-log");
    var form = panel.querySelector("#dtc-form");
    var input = panel.querySelector("#dtc-in");
    var send = panel.querySelector("#dtc-send");

    function bubble(role, text) {
      var b = el("div", { class: "dtc-m " + (role === "user" ? "dtc-u" : "dtc-a") });
      b.innerHTML = role === "user" ? esc(text) : fmt(text);
      log.appendChild(b);
      log.scrollTop = log.scrollHeight;
      return b;
    }
    function render() {
      log.innerHTML = "";
      bubble("assistant", GREETING);
      messages.forEach(function (m) { bubble(m.role, m.content); });
      if (!messages.length) {
        var chips = el("div", { class: "dtc-chips" });
        CHIPS.forEach(function (c) {
          var b = el("button", { type: "button", class: "dtc-chip" }, esc(c));
          b.onclick = function () { ask(c); };
          chips.appendChild(b);
        });
        log.appendChild(chips);
      }
    }

    function open(auto) {
      hideTip();
      try { sessionStorage.setItem(KEY + "-pop", "1"); } catch (e) {}
      panel.classList.add("open");
      document.documentElement.setAttribute("data-dtc-open", "");
      btn.setAttribute("aria-expanded", "true");
      render();
      if (auto !== true) setTimeout(function () { input.focus(); }, 50);
      track(auto === true ? "chat_auto_open" : "chat_open", { chat_page: location.pathname });
    }
    function close() {
      panel.classList.remove("open");
      document.documentElement.removeAttribute("data-dtc-open");
      btn.setAttribute("aria-expanded", "false");
      btn.focus();
    }
    btn.onclick = function () { panel.classList.contains("open") ? close() : open(); };

    // Nudge once per visit, 5 seconds after the page opened: on desktop the chat opens in the corner;
    // on phones (where the chat is full screen) only a small "Questions? Ask me here" bubble shows.
    // Never on the form / thank-you pages, never while someone is typing, never again once dismissed.
    var tip = el("div", { id: "dtc-tip", role: "button", tabindex: "0", "aria-label": "Open chat" }, 'Questions? Ask me here <button type="button" aria-label="Dismiss">×</button>');
    document.body.appendChild(tip);
    function hideTip() { tip.classList.remove("show"); }
    tip.onclick = function (e) { if (e.target.tagName === "BUTTON") { hideTip(); return; } open(); };
    tip.onkeydown = function (e) { if (e.key === "Enter") open(); };
    function nudge() {
      var seen; try { seen = sessionStorage.getItem(KEY + "-pop"); } catch (e) { seen = "1"; }
      if (seen || panel.classList.contains("open") || /contact|thank-you/.test(location.pathname)) return;
      var a = document.activeElement;
      if (a && /^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)) return;
      try { sessionStorage.setItem(KEY + "-pop", "1"); } catch (e) {}
      if (window.matchMedia("(max-width:520px)").matches) { tip.classList.add("show"); track("chat_teaser_shown", { chat_page: location.pathname }); }
      else open(true);
    }
    setTimeout(nudge, Math.max(0, 5000 - (window.performance && performance.now ? performance.now() : 0)));
    panel.querySelector("#dtc-x").onclick = close;
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && panel.classList.contains("open")) close(); });
    log.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a");
      if (a) {
        var isBook = /\/contact(\.html)?($|[?#])/.test(a.href);
        track("chat_link_click", { chat_link: a.getAttribute("href"), chat_booking: isBook });
        if (isBook && messages.length) booked();
      }
    });
    panel.querySelector("#dtc-foot").addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a");
      if (a && /\/contact(\.html)?($|[?#])/.test(a.href)) { track("chat_link_click", { chat_link: a.getAttribute("href"), chat_booking: true }); if (messages.length) booked(); }
    });

    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.onsubmit(e); }
    });
    input.addEventListener("input", function () { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 96) + "px"; });
    form.onsubmit = function (e) { e.preventDefault(); var t = input.value.trim(); if (t) ask(t); };

    function ask(q) {
      if (busy) return;
      if (messages.length >= 24) {
        bubble("assistant", "This chat has reached its limit. For anything else, [book a consultation](" + BOOK + ").");
        return;
      }
      busy = true; send.disabled = true; input.value = ""; input.style.height = "auto";
      var chips = log.querySelector(".dtc-chips"); if (chips) chips.remove();
      messages.push({ role: "user", content: q.slice(0, 1200) });
      bubble("user", q);
      var a = bubble("assistant", "");
      a.innerHTML = '<span class="dtc-dots" aria-label="Typing"><i></i><i></i><i></i></span>';
      track("chat_message", { chat_turn: Math.ceil(messages.length / 2) });

      var reply = "";
      fetch(ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: messages, page: location.pathname, conv: CONV }),
      }).then(function (res) {
        if (!res.ok || !res.body) return res.text().then(function (t) { throw new Error(t || "HTTP " + res.status); });
        var reader = res.body.getReader();
        var dec = new TextDecoder();
        function pump() {
          return reader.read().then(function (r) {
            if (r.done) return;
            reply += dec.decode(r.value, { stream: true });
            a.innerHTML = fmt(reply);
            log.scrollTop = log.scrollHeight;
            return pump();
          });
        }
        return pump();
      }).then(function () {
        if (!reply.trim()) throw new Error("empty");
        messages.push({ role: "assistant", content: reply });
        save(messages);
      }).catch(function (err) {
        messages.pop(); // drop the unanswered question so the conversation stays valid
        var msg = String(err && err.message || "");
        a.innerHTML = fmt(msg.length > 20 && msg.length < 300 && msg.indexOf("<") === -1 ? msg :
          "Sorry, I couldn't answer just now. You can [book a consultation](" + BOOK + ") and our team will get back to you.");
        track("chat_error", { chat_error: msg.slice(0, 80) });
      }).then(function () { busy = false; send.disabled = false; input.focus(); });
    }
  }

  function start() { try { mount(); } catch (e) {} }
  if (document.readyState === "complete") setTimeout(start, 1500);
  else window.addEventListener("load", function () { setTimeout(start, 1500); });
})();
