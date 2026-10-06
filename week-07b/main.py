import sqlite3
import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
from queries import get_report_data
from renderer import render_pdf

DB_PATH = "report.db"
REPORTS_DIR = "reports"

app = FastAPI(title="PDF Report Generator")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reports", status_code=201)
async def generate_report():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert report record
    created_at = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO reports (path, created_at) VALUES (?, ?)",
        ("", created_at)
    )
    report_id = cursor.lastrowid
    conn.commit()

    # Generate PDF
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")

    data = get_report_data()
    await render_pdf(data, path)

    # Update path
    cursor.execute("UPDATE reports SET path = ? WHERE id = ?", (path, report_id))
    conn.commit()
    conn.close()

    return {
        "id": report_id,
        "file": f"/reports/{report_id}/file"
    }

@app.get("/reports/{report_id}")
def get_report(report_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id, path, created_at FROM reports WHERE id = ?",
        (report_id,)
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": row[0],
        "file": f"/reports/{row[0]}/file",
        "created_at": row[2]
    }

@app.get("/reports/{report_id}/file")
def download_report(report_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT path FROM reports WHERE id = ?",
        (report_id,)
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    path = row[0]
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"books-report-{report_id}.pdf"
    )