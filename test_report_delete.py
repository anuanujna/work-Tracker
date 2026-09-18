import os
import tempfile
from pathlib import Path

import server


def test_delete_report_removes_row_by_id():
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_file.close()
    original_database = server.DATABASE
    try:
        server.DATABASE = Path(db_file.name)
        server.initialize_database()

        with server.connection() as database:
            database.execute(
                "INSERT INTO reports VALUES (?, ?, ?, ?, ?)",
                ("report-1", "Alpha report", "2026-01-01T00:00:00+00:00", 3, "[]"),
            )
            database.execute(
                "INSERT INTO reports VALUES (?, ?, ?, ?, ?)",
                ("report-2", "Beta report", "2026-01-02T00:00:00+00:00", 5, "[]"),
            )

        assert server.delete_report("report-1") is True

        with server.connection() as database:
            remaining = database.execute("SELECT id FROM reports ORDER BY viewed_at").fetchall()
            remaining_ids = [row["id"] for row in remaining]

        assert "report-1" not in remaining_ids
        assert "report-2" in remaining_ids
    finally:
        server.DATABASE = original_database
        if os.path.exists(db_file.name):
            os.remove(db_file.name)
