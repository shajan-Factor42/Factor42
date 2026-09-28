/**
 * Factor42 consultation form → Resend
 *
 * Receives the contact form from factor42media.com, emails the lead to your
 * inbox through Resend, optionally sends the visitor a short confirmation,
 * then redirects them to the thank-you page.
 *
 * Settings (Cloudflare → your worker → Settings → Variables and Secrets):
 *   RESEND_API_KEY     secret   Resend API key with sending access
 *   LEADS_TO           text     inbox(es) that receive leads, comma-separated
 *   FROM_EMAIL         text     e.g. Factor42 Website <leads@factor42media.com>
 *   SITE_URL           text     https://factor42media.com
 *   SEND_CONFIRMATION  text     "true" to email the visitor a confirmation
 */

const FIELDS = {
  name: 120, email: 200, company: 160, organization_type: 60,
  monthly_spend: 40, message: 5000, page: 300,
};
const CHANNELS = ["Paid search", "Paid social", "YouTube", "OTT / CTV", "Programmatic", "Streaming audio", "Email", "DOOH"];

export default {
  async fetch(request, env) {
    const site = (env.SITE_URL || "https://factor42media.com").replace(/\/$/, "");
    const allowed = [site, site.replace("://", "://www."), "https://shajan-factor42.github.io"];
    const origin = request.headers.get("Origin") || "";
    const cors = allowed.includes(origin) ? { "Access-Control-Allow-Origin": origin, "Vary": "Origin" } : {};

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: { ...cors, "Access-Control-Allow-Methods": "POST", "Access-Control-Allow-Headers": "Content-Type" } });
    }
    if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
    if (origin && !cors["Access-Control-Allow-Origin"]) return new Response("Forbidden", { status: 403 });

    const wantsJson = (request.headers.get("Accept") || "").includes("application/json");
    const back = (ok) => wantsJson
      ? new Response(JSON.stringify({ ok }), { status: ok ? 200 : 400, headers: { ...cors, "Content-Type": "application/json" } })
      : Response.redirect(ok ? `${site}/thank-you` : `${site}/contact?error=1`, 303);

    let form;
    try { form = await request.formData(); } catch { return back(false); }

    // Honeypot: real people never tick this hidden box. Pretend success to bots.
    if (form.get("botcheck")) return back(true);

    const d = {};
    for (const [k, max] of Object.entries(FIELDS)) d[k] = String(form.get(k) || "").trim().slice(0, max);
    const channels = CHANNELS.filter((c) => form.get(`Channel: ${c}`));

    if (!d.name || !d.company || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) return back(false);

    const rows = [
      ["Name", d.name], ["Email", d.email], ["Company", d.company],
      ["Organization", d.organization_type], ["Channels", channels.join(", ") || "None selected"],
      ["Monthly spend", d.monthly_spend], ["Message", d.message || "(none)"], ["Submitted from", d.page],
    ];
    const html = `<div style="font-family:Arial,sans-serif;font-size:15px;color:#0B1626">
<p style="font-size:18px;font-weight:bold;margin:0 0 16px">New consultation request</p>
<table cellpadding="8" style="border-collapse:collapse">${rows.map(([k, v]) =>
      `<tr><td style="border-top:1px solid #D9D5CC;color:#5A6272;vertical-align:top;white-space:nowrap">${esc(k)}</td><td style="border-top:1px solid #D9D5CC;white-space:pre-wrap">${esc(v)}</td></tr>`).join("")}</table>
<p style="color:#5A6272;font-size:13px">Reply to this email to respond to ${esc(d.name)} directly.</p></div>`;
    const text = rows.map(([k, v]) => `${k}: ${v}`).join("\n");

    const to = String(env.LEADS_TO || "").split(",").map((s) => s.trim()).filter(Boolean);
    const from = env.FROM_EMAIL || "Factor42 Website <leads@factor42media.com>";
    if (!env.RESEND_API_KEY || !to.length) return back(false);

    const sent = await send(env, {
      from, to, reply_to: d.email,
      subject: `New consultation request — ${d.company}`.slice(0, 150),
      html, text,
    });
    if (!sent) return back(false);

    if (String(env.SEND_CONFIRMATION).toLowerCase() === "true") {
      const first = d.name.split(/\s+/)[0].slice(0, 40);
      await send(env, {
        from, to: [d.email], reply_to: to[0],
        subject: "We've got your request — Factor42 Media",
        text: `Hi ${first},\n\nThanks for reaching out to Factor42 Media. We've received your consultation request and someone from our team will be in touch to set up a call.\n\n— Factor42 Media\n${site}`,
        html: `<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.6;color:#0B1626"><p>Hi ${esc(first)},</p><p>Thanks for reaching out to Factor42 Media. We've received your consultation request and someone from our team will be in touch to set up a call.</p><p>— Factor42 Media<br><a href="${site}" style="color:#C2410C">${esc(site.replace(/^https?:\/\//, ""))}</a></p></div>`,
      });
    }
    return back(true);
  },
};

async function send(env, payload) {
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) console.log("Resend error", res.status, await res.text());
  return res.ok;
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
