import sqlite3

DB_PATH = "report.db"

def get_report_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Total number of books
    total_books = cursor.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    # 2. Average price
    avg_price = cursor.execute(
        "SELECT ROUND(AVG(price), 2) FROM books"
    ).fetchone()[0]

    # 3. Top 5 most expensive books
    top_5_expensive = cursor.execute(
        "SELECT title, price FROM books ORDER BY price DESC LIMIT 5"
    ).fetchall()

    # 4. Number of books per star rating
    books_per_rating = cursor.execute(
        "SELECT rating, COUNT(*) as count FROM books GROUP BY rating ORDER BY count DESC"
    ).fetchall()

    conn.close()

    return {
        "total_books": total_books,
        "avg_price": avg_price,
        "top_5_expensive": [
            {"title": row[0], "price": row[1]} for row in top_5_expensive
        ],
        "books_per_rating": [
            {"rating": row[0], "count": row[1]} for row in books_per_rating
        ]
    }

if __name__ == "__main__":
    import json
    data = get_report_data()
    print(json.dumps(data, indent=2))