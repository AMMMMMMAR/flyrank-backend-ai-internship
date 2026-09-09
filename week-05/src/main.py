import requests
import os

USER_AGENT = "FlyRankInternshipA9/1.0 (https://github.com/AMMMMMMAR/flyrank-backend-ai-internship)"
TIMEOUT = 10

def fetch_page(url, cache_path):
    # 1. Check cache first
    if os.path.exists(cache_path):
        print(f"CACHE HIT: {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    # 2. Not in cache — fetch from internet
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    # 3. Check status code
    if response.status_code != 200:
        print(f"FAILED: {url} returned {response.status_code}")
        return None

    # 4. Save to cache
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"FETCH: {url} ({len(response.text)} characters)")
    return response.text


if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/page-1.html"
    html = fetch_page(url, "cache/catalogue-page-1.html")
    if html:
        print(f"Page size: {len(html)} characters")