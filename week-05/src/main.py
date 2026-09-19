import requests
import os
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
import time
from pydantic import BaseModel, ValidationError
from typing import Optional


USER_AGENT = "FlyRankInternshipA9/1.0 (https://github.com/AMMMMMMAR/flyrank-backend-ai-internship)"
TIMEOUT = 10


class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: Optional[str] = None
    source_page: str
    fetched_at: str


def fetch_page(url, cache_path):
    if os.path.exists(cache_path):
        print(f"CACHE HIT: {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        response.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    if response.status_code != 200:
        print(f"FAILED: {url} returned {response.status_code}")
        return None

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


def extract_book(html, product_url, source_page):
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h1")
    title = title_tag.text.strip() if title_tag else None

    price_tag = soup.find("p", class_="price_color")
    price_text = price_tag.text.strip() if price_tag else None

    availability_tag = soup.find("p", class_="instock availability")
    availability_text = availability_tag.text.strip() if availability_tag else None

    rating_tag = soup.find("p", class_="star-rating")
    rating_text = rating_tag["class"][1] if rating_tag else None

    description = None
    desc_header = soup.find("div", id="product_description")
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        if desc_p:
            description = desc_p.text.strip()

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }


def parse_price(price_text: str) -> float:
    # "£51.77" → 51.77
    cleaned = price_text.replace("£", "").replace(",", "").strip()
    return float(cleaned)


if __name__ == "__main__":
    # --- Stage 2: discover all 60 book links ---
    base_url = "https://books.toscrape.com/catalogue/page-1.html"
    current_url = base_url
    all_book_links = []
    source_pages = {}
    page_num = 1

    while current_url and page_num <= 3:
        cache_path = f"cache/catalogue-page-{page_num}.html"
        html = fetch_page(current_url, cache_path)
        if html:
            links = get_book_links(html, current_url)
            for link in links:
                source_pages[link] = current_url
            all_book_links.extend(links)
            current_url = get_next_page(html, current_url)
            page_num += 1

    seen = set()
    unique_urls = []
    for url in all_book_links:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    print(f"catalogue_pages={page_num-1} discovered={len(all_book_links)} unique_urls={len(unique_urls)}")

    # --- Stage 3: fetch and extract each book ---
    books = []
    for i, book_url in enumerate(unique_urls):
        cache_path = f"cache/book-{i+1}.html"
        already_cached = os.path.exists(cache_path)

        html = fetch_page(book_url, cache_path)
        if html:
            source = source_pages.get(book_url, "unknown")
            book = extract_book(html, book_url, source)
            books.append(book)

        if not already_cached:
            time.sleep(0.5)

    print(f"detail_pages={len(books)}")

    # --- Stage 4: clean, validate and save ---
    good_books = []
    errors = []

    for book in books:
        # add price_gbp
        try:
            book["price_gbp"] = parse_price(book["price_text"])
        except Exception:
            book["price_gbp"] = None

        # validate with Pydantic
        try:
            validated = BookRecord(**book)
            good_books.append(validated.model_dump())
        except ValidationError as e:
            errors.append({
                "product_url": book.get("product_url"),
                "reason": str(e)
            })

    # save good records
    os.makedirs("output", exist_ok=True)
    with open("output/books.json", "w", encoding="utf-8") as f:
        json.dump(good_books, f, indent=2, ensure_ascii=False)

    # save errors
    with open("output/errors.json", "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2, ensure_ascii=False)

    print(f"valid={len(good_books)} invalid={len(errors)}")
    print(f"Saved to output/books.json and output/errors.json")

    # print sample
    if good_books:
        print("Sample validated record:")
        print(json.dumps(good_books[0], indent=2, ensure_ascii=False))