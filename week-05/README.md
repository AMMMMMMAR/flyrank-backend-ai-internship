# Week 05 — The Polite Scraper

A polite web scraping pipeline that collects 60 books from a practice sandbox,
validates every record against a schema, and reports what happened at the end.

## Target Classification

- **Site:** Books to Scrape (books.toscrape.com)
- **Why:** This is a public sandbox built specifically for scraping practice.
  The site says "We love being scraped!" — it exists for this purpose.
- **Scope:** First 3 catalogue pages only (20 books per page = 60 books total)
- **Data collected:** Title, price, rating, availability, description, URL
- **robots.txt result:** 404 — no robots.txt file found. The site returned a 404
  when requesting /robots.txt. A missing file is not permission — permission comes
  from the site explicitly stating it is a public scraping sandbox.
- **Appropriate because:** This is a practice sandbox with no real users,
  no personal data, and explicit permission to scrape.

I will not reuse this code on another site without checking its rules and terms first.

## Politeness Rules

- Honest user-agent identifying who we are and linking to the repo
- 500ms minimum delay between real requests
- 10 second timeout on every request
- Cache saves pages locally — development never hits the site twice
- Status code checked before parsing — only 200 means success

## How to Run

```bash
cd week-05
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python src/main.py
```

One command processes exactly the first 3 catalogue pages and discovers 60 unique book URLs.

## Record Schema

Each book record contains:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Book title |
| `product_url` | string | Absolute URL of the book page |
| `price_text` | string | Raw price as scraped e.g. "£51.77" |
| `price_gbp` | float | Cleaned numeric price e.g. 51.77 |
| `availability_text` | string | Raw availability text |
| `rating_text` | string | Raw rating word e.g. "Three" |
| `description` | string or null | Book description (null if missing) |
| `source_page` | string | Catalogue page where the book was found |
| `fetched_at` | string | ISO timestamp of when the page was fetched |

## Output Files

| File | What it contains |
|------|-----------------|
| `output/books.json` | 60 validated book records |
| `output/errors.json` | Records that failed validation with reasons |
| `output/run-report.json` | Run statistics and summary |

## Ethics Note

Web scraping should always be done responsibly:
- Use an official API when one exists — it is always the better choice
- Never bypass logins, paywalls, or access controls
- Never collect personal data without consent
- Collect only what you need — this scraper collects 3 pages, not all 1000
- Identify yourself honestly in the user-agent header
- Be a polite guest — go slowly and never hammer a site

## Why No Browser Was Needed

The data on Books to Scrape is already in the HTML the server sends —
no JavaScript rendering is required. A plain HTTP request gets the same
content a browser would see, so using a browser (like Playwright) would
only add memory and time cost with no benefit for this target.

## Run Report

```json
[paste your run-report.json here after running the scraper]
```

## Lane

Python — requests + Beautiful Soup + Pydantic