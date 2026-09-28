# Contact form → Resend (Cloudflare Worker)

`worker.js` receives the consultation form, emails the lead through Resend from `leads@factor42media.com`, optionally emails the visitor a confirmation, and redirects them to `/thank-you`. The site keeps using Web3Forms until the worker is deployed and `FORM_ENDPOINT` is set in `_build/build_pages.py`.

## 1. Verify factor42media.com in Resend

The domain is already added in Resend (region us-east-1). Add these records in **GoDaddy → factor42media.com → DNS → Add New Record**, then click **Verify** in Resend → Domains:

| Type | Name | Value | Priority |
|---|---|---|---|
| TXT | `resend._domainkey` | the DKIM value shown in Resend → Domains → factor42media.com (starts `p=MIGfMA0…`) | |
| MX | `send` | `feedback-smtp.us-east-1.amazonses.com` | 10 |
| TXT | `send` | `v=spf1 include:amazonses.com ~all` | |
| CNAME | `rsend` | `send.forge.rmta.net` | |

These all sit on the `send` / `resend._domainkey` / `rsend` subdomains, so they don't touch the MX or SPF records on `factor42media.com` itself. Your existing email keeps working.

## 2. Create a Resend API key

Resend → **API Keys → Create API Key**. Name it `factor42-website`, permission **Sending access**, domain **factor42media.com**. Copy the key; it's shown once.

## 3. Deploy the worker

**In the Cloudflare dashboard (no install needed):**

1. Sign up or log in at dash.cloudflare.com, then go to **Workers & Pages → Create → Create Worker**.
2. Name it `factor42-forms` → **Deploy** → **Edit code**.
3. Replace everything in the editor with the contents of `worker.js` → **Deploy**.
4. Go to **Settings → Variables and Secrets** and add:

| Name | Type | Value |
|---|---|---|
| `RESEND_API_KEY` | Secret | the key from step 2 |
| `LEADS_TO` | Text | inbox(es) for leads, comma-separated |
| `FROM_EMAIL` | Text | `Factor42 Website <leads@factor42media.com>` |
| `SITE_URL` | Text | `https://factor42media.com` |
| `SEND_CONFIRMATION` | Text | `true` (or `false` to skip the visitor confirmation) |

5. Copy the worker's address, e.g. `https://factor42-forms.<your-subdomain>.workers.dev`.

**Or with the CLI:** `npx wrangler deploy` in this folder, then `npx wrangler secret put RESEND_API_KEY` and `npx wrangler secret put LEADS_TO`.

## 4. Switch the site over

Set `FORM_ENDPOINT` in `_build/build_pages.py` to the worker address, rebuild with `python3 _build/build_pages.py .`, and push. Or send Claude the address and it will do this. Then submit a test on `/contact`.

## Behaviour

- Required: name, a valid email, company. Invalid submissions send nothing and return to `/contact?error=1`, which shows an error message.
- The hidden `botcheck` field catches simple bots; they're shown the thank-you page but nothing is sent.
- Only requests from factor42media.com (and the GitHub preview address) are accepted.
- The lead email's reply-to is the visitor, so hitting Reply goes straight to them.
- Failed sends show up in the Cloudflare worker's logs and in Resend → Logs.
