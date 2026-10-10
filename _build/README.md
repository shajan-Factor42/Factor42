# Site build scripts

The pages in the repo root and `blog/` are generated from these files. Edit the source here, then rebuild:

```
python3 _build/build_pages.py .        # all pages, blog and sitemap.xml
python3 _build/audit_site.py .        # SEO, schema, brand and internal-link audit (add -v for every finding)
python3 _build/check_site.py . /tmp/shots   # browser check of pages and links (needs playwright)
```

The build also writes `sitemap.xml` (last-modified dates come from git: only pages that changed get today's date),
`robots.txt` (explicitly open to search and AI crawlers), `llms.txt` and `llms-full.txt` (for AI assistants),
and forwarding pages for old-site addresses (`OLD_BLOG` in `build_pages.py`).

- `linker.py`: adds contextual links between articles. Each phrase rule maps a natural mention to related
  articles; links are spread so every article receives several. Wording is never changed.

- `bodies/`: the main content of each page
- `articles/`: blog article text, one file per post, exported from the Google Drive folder "Factor 42 Blog Content"
- `build_logo.py`, `render_images.py`: regenerate the logo SVGs, PNGs and social share image (these need the font files from @fontsource)
