# database/db.py
# Database access layer
# All DB reads and writes go through here — routes and services never touch SQL directly

import sqlite3
from datetime import datetime
from config import Config


def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def clear_all_scans() -> None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM compliance_item")
    cursor.execute("DELETE FROM scan_result")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='scan_result'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='compliance_item'")
    conn.commit()
    conn.close()


def save_scan(raw_output: str, ai_summary: str, ai_raw: str) -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO scan_result (created_at, raw_output, ai_summary, ai_raw) VALUES (?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), raw_output, ai_summary, ai_raw)
    )
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scan_id


def get_all_scans() -> list:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scan_result ORDER BY created_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_scan_by_id(scan_id: int) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scan_result WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_latest_scan() -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scan_result ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_compliance_items(scan_id: int, items: list) -> None:
    conn = get_db()
    cursor = conn.cursor()
    for item in items:
        cursor.execute(
            "INSERT INTO compliance_item (scan_id, category, label, value, compliant, suggestion) VALUES (?, ?, ?, ?, ?, ?)",
            (
                scan_id,
                item.get("category", ""),
                item.get("label", ""),
                item.get("value", ""),
                item.get("compliant", 0),
                item.get("suggestion", "")
            )
        )
    conn.commit()
    conn.close()


def get_compliance_items(scan_id: int) -> list:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM compliance_item WHERE scan_id = ? ORDER BY category", (scan_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_compliance_summary(scan_id: int) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) AS total, SUM(compliant) AS passed, COUNT(*) - SUM(compliant) AS failed FROM compliance_item WHERE scan_id = ?",
        (scan_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {"total": 0, "passed": 0, "failed": 0}