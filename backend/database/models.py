# database/models.py
# Defines the database schema
# Two tables: ScanResult and ComplianceItem

import sqlite3
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_result (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at  TEXT    NOT NULL,
            raw_output  TEXT    NOT NULL,
            ai_summary  TEXT,
            ai_raw      TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compliance_item (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id     INTEGER NOT NULL,
            category    TEXT    NOT NULL,
            label       TEXT    NOT NULL,
            value       TEXT,
            compliant   INTEGER NOT NULL DEFAULT 0,
            suggestion  TEXT,
            FOREIGN KEY (scan_id) REFERENCES scan_result(id)
        )
    """)
    conn.commit()
    conn.close()