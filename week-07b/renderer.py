import asyncio
from playwright.async_api import async_playwright
from datetime import date

async def render_pdf(data: dict, output_path: str):
    html = build_html(data)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        await page.pdf(
            path=output_path,
            format="A4",
            print_background=True
        )
        await browser.close()

def build_html(data: dict) -> str:
    today = date.today().strftime("%B %d, %Y")
    
    # Top 5 expensive books table rows
    top5_rows = ""
    for i, book in enumerate(data["top_5_expensive"], 1):
        top5_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{book['title']}</td>
            <td>£{book['price']:.2f}</td>
        </tr>
        """

    # Rating breakdown rows
    rating_rows = ""
    for item in data["books_per_rating"]:
        rating_rows += f"""
        <tr>
            <td>{item['rating']}</td>
            <td>{item['count']}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Books Report</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 13px;
                color: #333;
                padding: 40px;
            }}
            .header {{
                background: #6366f1;
                color: white;
                padding: 24px 32px;
                border-radius: 8px;
                margin-bottom: 32px;
            }}
            .header h1 {{ font-size: 28px; margin-bottom: 4px; }}
            .header p {{ opacity: 0.8; font-size: 14px; }}
            .stats {{
                display: flex;
                gap: 16px;
                margin-bottom: 32px;
            }}
            .stat-card {{
                flex: 1;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
            }}
            .stat-card .value {{
                font-size: 32px;
                font-weight: bold;
                color: #6366f1;
            }}
            .stat-card .label {{
                font-size: 12px;
                color: #64748b;
                margin-top: 4px;
            }}
            h2 {{
                font-size: 16px;
                color: #6366f1;
                margin-bottom: 12px;
                padding-bottom: 8px;
                border-bottom: 2px solid #e2e8f0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 32px;
            }}
            thead th {{
                background: #6366f1;
                color: white;
                padding: 10px 12px;
                text-align: left;
                font-size: 12px;
            }}
            tbody tr {{ break-inside: avoid; }}
            tbody tr:nth-child(even) {{ background: #f8fafc; }}
            tbody td {{
                padding: 10px 12px;
                border-bottom: 1px solid #e2e8f0;
                font-size: 12px;
            }}
            .all-books-section {{ margin-top: 16px; }}

            @media print {{
                thead {{ display: table-header-group; }}
                tbody tr {{ break-inside: avoid; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📚 Books Report</h1>
            <p>Generated on {today} · Books to Scrape dataset</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="value">{data['total_books']}</div>
                <div class="label">Total Books</div>
            </div>
            <div class="stat-card">
                <div class="value">£{data['avg_price']:.2f}</div>
                <div class="label">Average Price</div>
            </div>
        </div>

        <h2>Top 5 Most Expensive Books</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Title</th>
                    <th>Price</th>
                </tr>
            </thead>
            <tbody>
                {top5_rows}
            </tbody>
        </table>

        <h2>Books by Star Rating</h2>
        <table>
            <thead>
                <tr>
                    <th>Rating</th>
                    <th>Number of Books</th>
                </tr>
            </thead>
            <tbody>
                {rating_rows}
            </tbody>
        </table>

        <div class="all-books-section">
            <h2>All Books</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Title</th>
                        <th>Price</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(f'<tr><td>{i}</td><td>{b["title"]}</td><td>£{b["price"]:.2f}</td><td>{b["rating"]}</td></tr>' for i, b in enumerate(data['all_books'], 1))}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    from queries import get_report_data
    data = get_report_data()
    asyncio.run(render_pdf(data, "reports/test.pdf"))
    print("PDF saved to reports/test.pdf")