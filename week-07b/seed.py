import sqlite3
import json
import os

# Path to your books.json from week-05
BOOKS_JSON = os.path.join(os.path.dirname(__file__), "..", "week-05", "output", "books.json")
DB_PATH = "report.db"

def seed():
    # Load books from JSON
    with open(BOOKS_JSON, "r", encoding="utf-8") as f:
        books = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            rating TEXT NOT NULL,
            url TEXT NOT NULL
        )
    """)

    # Delete all rows first — safe to run twice
    cursor.execute("DELETE FROM books")

    # Insert books
    for book in books:
        cursor.execute(
            "INSERT INTO books (title, price, rating, url) VALUES (?, ?, ?, ?)",
            (book["title"], book["price_gbp"], book["rating_text"], book["product_url"])
        )

    conn.commit()

    # Verify
    count = cursor.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    print(f"Seeded {count} books into report.db")

    conn.close()

if __name__ == "__main__":
    seed()