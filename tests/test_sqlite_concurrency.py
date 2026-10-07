import sqlite3

from app.database import set_sqlite_pragma


def test_preview_read_during_pending_write(tmp_path):
    path = tmp_path / 'concurrency.db'
    writer = sqlite3.connect(path)
    reader = sqlite3.connect(path)
    try:
        set_sqlite_pragma(writer, None)
        set_sqlite_pragma(reader, None)
        assert reader.execute('PRAGMA journal_mode').fetchone()[0] == 'wal'
        assert reader.execute('PRAGMA busy_timeout').fetchone()[0] == 30000
        writer.execute('CREATE TABLE scores (value INTEGER)')
        writer.execute('INSERT INTO scores VALUES (10)')
        writer.commit()
        writer.execute('BEGIN IMMEDIATE')
        writer.execute('UPDATE scores SET value = 11')
        assert reader.execute('SELECT value FROM scores').fetchone()[0] == 10
        writer.commit()
        assert reader.execute('SELECT value FROM scores').fetchone()[0] == 11
    finally:
        writer.close()
        reader.close()
