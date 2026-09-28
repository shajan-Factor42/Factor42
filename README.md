# factor42media.com

The Factor42 Media website: plain static HTML and CSS, served by GitHub Pages. No build step, and every page is complete in its source.

## What's here

| Page | File | URL |
|---|---|---|
| Home | `index.html` | `/` |
| For agencies | `agencies.html` | `/agencies` |
| For broadcasters | `broadcasters.html` | `/broadcasters` |
| About | `about.html` | `/about` |
| Book a consultation | `contact.html` | `/contact` |
| Thank-you (after the form) | `thank-you.html` | `/thank-you` (not indexed) |
| Not found | `404.html` | any missing URL |
| Blog index | `blog/index.html` | `/blog/` |
| 105 blog articles | `blog/<slug>.html` | `/blog/<slug>` |
| Old-URL redirects | `consultation.html`, `white-label-ppc.html` | `/consultation` → `/contact`, `/white-label-ppc` → `/agencies#ppc` |

- `assets/css/site.css`: all styles (colours, type, layout, phone layouts)
- `assets/js/site.js`: mobile menu, the channel tabs on the homepage, form redirect. The site works without it.
- `assets/fonts/`: Schibsted Grotesk, Geist and Geist Mono, self-hosted
- `assets/img/`: logo files (`logo.svg`, `logo-reversed.svg`, `logo-horizontal.svg`, `mark.svg`, `logo-1200.png`, `logo-512.png`), favicons and the social share image (`og-image.png`)
- `sitemap.xml`, `robots.txt`, `llms.txt`: search engine and AI-assistant files
- Each page carries its title, description, canonical URL, social share tags and schema.org structured data.

Links are relative and extensionless, so the site works both at the GitHub preview address and at factor42media.com, and it keeps the URLs the current site already ranks for.

## Step 1: Turn on GitHub Pages (preview)

1. In this repo: **Settings → Pages**
2. **Source:** Deploy from a branch → Branch **`main`**, folder **`/ (root)`** → **Save**
3. In about a minute the preview is live at **https://shajan-factor42.github.io/Factor42/**

There is deliberately **no `CNAME` file yet**, so the current factor42media.com keeps running untouched while you review the preview.

## Step 2: Test the form on the preview

The form posts to Web3Forms using the same access key as deepthought.marketing, so submissions go to the same inbox. Each email's subject says **"New consultation request — factor42media.com"** so you can tell them apart.

1. Submit a test on `/contact` and confirm it arrives and you land on the thank-you page.
2. If it's rejected, open the Web3Forms dashboard and add `factor42media.com` and `shajan-factor42.github.io` to the key's allowed domains, if that setting is on.

## Step 3: Before switching the domain

These pages exist on the current site but aren't in this repo yet. The footer and nav link to them, so they'd 404 after the switch:

- [ ] `/privacy-policy`, `/terms-of-service`, `/sla` and `/security`. The form links to the privacy policy, so this one is required.
- [ ] `/careers`
- [ ] `/library`

Add each as an `.html` file in the repo root with the same name (e.g. `privacy-policy.html`), or tell Claude to build them.

## Step 4: Point factor42media.com here

1. Add a file named `CNAME` to the repo root containing one line: `factor42media.com`
2. At your domain registrar, change the DNS records:
   - **Apex `factor42media.com`:** replace the current A records with these four:
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - **`www`:** CNAME → `shajan-factor42.github.io`
   - **Do not touch MX, SPF, DKIM or DMARC records.** Those run your email.
3. Back in **Settings → Pages**, wait for the DNS check to pass, then tick **Enforce HTTPS**. The certificate can take up to an hour.

## Step 5: After it's live

- Google Search Console and Bing Webmaster Tools: submit `https://factor42media.com/sitemap.xml`
- Add your analytics snippet (GA4, Plausible or similar) to each page's `<head>`
- Test the form once more on the live domain

## The blog

The 105 articles come from the Word documents in Google Drive (**Factor 42 Blog Content** and its **Blogs 7/16** subfolder). Each has its own page with headings, reading time, topic, article structured data and related reading, and all are listed in `sitemap.xml`. The blog index at `/blog/` can be filtered by topic: Channels & platforms, Strategy & budget, Choosing a partner, and Seasonal & timing.

To add or change articles, ask Claude to rebuild the blog from the Drive folder.
