"""
SQLite-backed download history.

Responsible for persisting every completed/failed download and exposing
search, delete, and CSV export operations used by the "Download History"
menu screen.
"""

from __future__ import annotations

import csv
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from database.models import DownloadStatus, HistoryRecord
from utils.helpers import now_iso
from utils.logger import get_logger

log = get_logger("database.history")

APP_DIR = Path.home() / ".tubeforge"
DB_PATH = APP_DIR / "history.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    date TEXT NOT NULL,
    size_bytes INTEGER DEFAULT 0,
    dtype TEXT NOT NULL,
    output_path TEXT NOT NULL,
    duration_seconds INTEGER DEFAULT 0,
    status TEXT DEFAULT 'completed'
);
CREATE INDEX IF NOT EXISTS idx_history_title ON history(title);
CREATE INDEX IF NOT EXISTS idx_history_date ON history(date);
"""


class HistoryDB:
    """Thin, connection-per-call wrapper around SQLite for thread safety."""

    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(_SCHEMA)
        log.debug("History DB ready at %s", self.path)

    # ---- writes ------------------------------------------------------

    def add(self, record: HistoryRecord) -> int:
        if not record.date:
            record.date = now_iso()
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO history
                   (title, url, date, size_bytes, dtype, output_path, duration_seconds, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                record.as_row(),
            )
            log.info("History entry added: %s (%s)", record.title, record.dtype)
            return cur.lastrowid

    def delete(self, record_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM history WHERE id = ?", (record_id,))
            return cur.rowcount > 0

    def clear_all(self) -> int:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM history")
            return cur.rowcount

    # ---- reads -------------------------------------------------------

    def all(self, limit: int = 200) -> list[HistoryRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def search(self, query: str) -> list[HistoryRecord]:
        like = f"%{query}%"
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT * FROM history
                   WHERE title LIKE ? OR url LIKE ? OR dtype LIKE ?
                   ORDER BY id DESC""",
                (like, like, like),
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def stats(self) -> dict:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT COUNT(*) as total,
                          COALESCE(SUM(size_bytes), 0) as total_bytes,
                          COALESCE(SUM(duration_seconds), 0) as total_seconds
                   FROM history WHERE status = ?""",
                (DownloadStatus.COMPLETED.value,),
            ).fetchone()
            by_type = conn.execute(
                "SELECT dtype, COUNT(*) as c FROM history GROUP BY dtype"
            ).fetchall()
        return {
            "total": row["total"],
            "total_bytes": row["total_bytes"],
            "total_seconds": row["total_seconds"],
            "by_type": {r["dtype"]: r["c"] for r in by_type},
        }

    def export_csv(self, out_path: str | Path) -> Path:
        out_path = Path(out_path).expanduser()
        records = self.all(limit=100_000)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["id", "title", "url", "date", "size_bytes", "type", "output_path", "duration_seconds", "status"]
            )
            for r in records:
                writer.writerow([r.id, r.title, r.url, r.date, r.size_bytes, r.dtype, r.output_path, r.duration_seconds, r.status])
        log.info("Exported %d history records to %s", len(records), out_path)
        return out_path

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> HistoryRecord:
        return HistoryRecord(
            id=row["id"],
            title=row["title"],
            url=row["url"],
            date=row["date"],
            size_bytes=row["size_bytes"],
            dtype=row["dtype"],
            output_path=row["output_path"],
            duration_seconds=row["duration_seconds"],
            status=row["status"],
        )
