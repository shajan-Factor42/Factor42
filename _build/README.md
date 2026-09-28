# Site build scripts

The pages in the repo root and `blog/` are generated from these files. Edit the source here, then rebuild:

```
python3 _build/build_pages.py .        # all pages, blog and sitemap.xml
python3 _build/check_site.py . /tmp/shots   # browser check of pages and links (needs playwright)
```

- `bodies/`: the main content of each page
- `articles/`: blog article text, one file per post, exported from the Google Drive folder "Factor 42 Blog Content"
- `build_logo.py`, `render_images.py`: regenerate the logo SVGs, PNGs and social share image (these need the font files from @fontsource)
