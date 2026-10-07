"""Create, verify and restore private SQLite snapshots without overwriting data."""

import argparse
import hashlib
import json
import shutil
import sqlite3
import time
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_database(path):
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
        integrity = [row[0] for row in db.execute('PRAGMA integrity_check')]
        foreign_keys = db.execute('PRAGMA foreign_key_check').fetchall()
        if integrity != ['ok'] or foreign_keys:
            raise ValueError(f'Database validation failed: {integrity}; foreign key violations: {len(foreign_keys)}')
        tables = [row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        counts = {name: db.execute('SELECT count(*) FROM "' + name.replace('"', '""') + '"').fetchone()[0]
                  for name in tables}
        revisions = [row[0] for row in db.execute('SELECT version_num FROM alembic_version')]
        return {'integrity_check': 'ok', 'foreign_key_violations': 0,
                'alembic_revisions': sorted(revisions), 'table_counts': counts}


def snapshot_database(source, destination):
    source = source.resolve(strict=True)
    if source == destination.resolve() or destination.exists():
        raise ValueError('Snapshot destination must be a new file, distinct from the source')
    deadline = time.monotonic() + 180

    def progress(status, remaining, total):
        if time.monotonic() > deadline:
            raise TimeoutError('Snapshot exceeded 180 seconds; retry when database activity is lower')

    # The backup API includes committed WAL pages; copying the .db file alone does not.
    with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True, timeout=30)) as src:
        with closing(sqlite3.connect(destination)) as dst:
            src.backup(dst, pages=1024, progress=progress, sleep=0.1)
            dst.execute('PRAGMA journal_mode=DELETE')
    destination.chmod(0o600)


def create_backup(database, destination, includes=()):
    database = database.resolve(strict=True)
    destination = destination.resolve()
    names = {'leverage.db', 'manifest.json'}
    sources = []
    for path in includes:
        if path.is_symlink():
            raise ValueError('Symlink directories are not supported')
        path = path.resolve(strict=True)
        if not path.is_dir() or path.name in names or path == destination or path in destination.parents:
            raise ValueError(f'Invalid or duplicate asset directory: {path}')
        if any(item.is_symlink() for item in path.rglob('*')):
            raise ValueError(f'Asset symlinks are not supported: {path}')
        names.add(path.name)
        sources.append(path)
    destination.mkdir(parents=True, exist_ok=False, mode=0o700)
    snapshot_database(database, destination / 'leverage.db')
    for source in sources:
        shutil.copytree(source, destination / source.name)
    files = {}
    for path in sorted(destination.rglob('*')):
        if path.is_file():
            path.chmod(0o600)
            files[path.relative_to(destination).as_posix()] = {'sha256': sha256(path), 'bytes': path.stat().st_size}
    manifest = {'format_version': 1, 'created_at_utc': datetime.now(timezone.utc).isoformat(),
                'database': inspect_database(destination / 'leverage.db'), 'files': files}
    manifest_path = destination / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    manifest_path.chmod(0o600)
    return manifest


def verify_backup(directory):
    directory = directory.resolve(strict=True)
    if any(path.is_symlink() for path in directory.rglob('*')):
        raise ValueError('Backup contains symlinks')
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('format_version') != 1 or 'leverage.db' not in manifest.get('files', {}):
        raise ValueError('Unsupported or incomplete backup manifest')
    actual = {path.relative_to(directory).as_posix() for path in directory.rglob('*')
              if path.is_file() and path != directory / 'manifest.json'}
    if actual != set(manifest['files']):
        raise ValueError('Backup inventory differs from the manifest')
    for relative, expected in manifest['files'].items():
        path = directory / relative
        if directory not in path.resolve().parents:
            raise ValueError('Invalid backup path')
        if path.stat().st_size != expected['bytes'] or sha256(path) != expected['sha256']:
            raise ValueError(f'Backup checksum mismatch: {relative}')
    if inspect_database(directory / 'leverage.db') != manifest['database']:
        raise ValueError('Database schema or counts differ from the snapshot')
    return manifest


def restore_backup(source, destination):
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if destination.exists() or source in destination.parents:
        raise ValueError('Restore destination must be a new directory outside the backup')
    manifest = verify_backup(source)
    destination.mkdir(parents=True, exist_ok=False, mode=0o700)
    shutil.copytree(source, destination, dirs_exist_ok=True)
    if verify_backup(destination) != manifest:
        raise ValueError('Restored snapshot does not match the backup')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('create')
    create.add_argument('--database', type=Path, default=Path('leverage.db'))
    create.add_argument('--output', type=Path, required=True)
    create.add_argument('--include', type=Path, action='append', default=[])
    verify = commands.add_parser('verify')
    verify.add_argument('directory', type=Path)
    restore = commands.add_parser('restore')
    restore.add_argument('directory', type=Path)
    restore.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'create':
        result = create_backup(args.database, args.output, args.include)
    elif args.command == 'verify':
        result = verify_backup(args.directory)
    else:
        result = restore_backup(args.directory, args.output)
    print(json.dumps({'command': args.command, 'status': 'verified',
                      'files': len(result['files']), 'database': result['database']}, indent=2))


if __name__ == '__main__':
    main()
