import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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


def get_book_links(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    book_links = []
    for h3 in soup.find_all("h3"):
        a_tag = h3.find("a")
        if a_tag and "href" in a_tag.attrs:
            relative_link = a_tag["href"]
            absolute_link = urljoin(page_url, relative_link)
            book_links.append(absolute_link)
    return book_links

def get_next_page(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    next_button = soup.find("li", class_="next")
    if next_button:
        a_tag = next_button.find("a")
        if a_tag and "href" in a_tag.attrs:
            relative_link = a_tag["href"]
            absolute_link = urljoin(page_url, relative_link)
            return absolute_link
    return None

if __name__ == "__main__":
    base_url = "https://books.toscrape.com/catalogue/page-1.html"
    current_url = base_url
    all_book_links = []
    page_num = 1

    while current_url and page_num <= 3:
        cache_path = f"cache/catalogue-page-{page_num}.html"
        html = fetch_page(current_url, cache_path)
        if html:
            links = get_book_links(html, current_url)
            all_book_links.extend(links)
            current_url = get_next_page(html, current_url)
            page_num += 1

    unique_urls = list(set(all_book_links))
    print(f"catalogue_pages={page_num-1} discovered={len(all_book_links)} unique_urls={len(unique_urls)}")