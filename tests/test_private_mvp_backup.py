import sqlite3
from pathlib import Path

import pytest

from scripts.private_mvp_backup import create_backup, restore_backup, verify_backup


def test_backup_includes_wal_and_restores_all_assets(tmp_path):
    source = tmp_path / 'source.db'
    with sqlite3.connect(source) as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
        db.execute('CREATE TABLE alembic_version (version_num TEXT)')
        db.execute("INSERT INTO alembic_version VALUES ('test')")
        db.execute('CREATE TABLE scores (value REAL)')
        db.execute('INSERT INTO scores VALUES (13.5)')
        db.commit()
        assert Path(str(source) + '-wal').stat().st_size > 0
        assets = tmp_path / 'uploads'
        assets.mkdir()
        (assets / 'image.png').write_bytes(b'example')
        backup = tmp_path / 'backup'
        manifest = create_backup(source, backup, [assets])
        assert manifest['database']['table_counts']['scores'] == 1
        assert verify_backup(backup) == manifest
        restored = tmp_path / 'restored'
        assert restore_backup(backup, restored) == manifest
        assert (restored / 'uploads/image.png').read_bytes() == b'example'
        with sqlite3.connect(restored / 'leverage.db') as copy:
            assert copy.execute('SELECT value FROM scores').fetchone()[0] == 13.5
        with pytest.raises((ValueError, FileExistsError)):
            restore_backup(backup, restored)
        with pytest.raises(FileExistsError):
            create_backup(source, backup)
        assert db.execute('SELECT value FROM scores').fetchone()[0] == 13.5
        (backup / 'uploads/image.png').write_bytes(b'changed')
        with pytest.raises(ValueError, match='checksum mismatch'):
            restore_backup(backup, tmp_path / 'invalid')
        assert not (tmp_path / 'invalid').exists()


def test_invalid_database_and_symlinks_are_rejected(tmp_path):
    source = tmp_path / 'source.db'
    with sqlite3.connect(source) as db:
        db.execute('CREATE TABLE alembic_version (version_num TEXT)')
        db.execute('CREATE TABLE parent (id INTEGER PRIMARY KEY)')
        db.execute('CREATE TABLE child (parent_id INTEGER REFERENCES parent(id))')
        db.execute('INSERT INTO child VALUES (99)')
    with pytest.raises(ValueError, match='foreign key violations: 1'):
        create_backup(source, tmp_path / 'invalid')
    assets = tmp_path / 'uploads'
    assets.mkdir()
    (assets / 'link').symlink_to(source)
    with pytest.raises(ValueError, match='symlinks'):
        create_backup(source, tmp_path / 'symlink', [assets])
