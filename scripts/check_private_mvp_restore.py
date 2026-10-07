"""Restore a backup into a NEW directory and smoke-test only that disposable copy."""

import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.private_mvp_backup import inspect_database, restore_backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = restore_backup(args.backup, args.output)
    database = args.output.resolve() / 'leverage.db'
    # The restored copy must not resume real external scans or send emails.
    with sqlite3.connect(database) as db:
        db.execute('UPDATE world_gymnastics_scan_control SET enabled=0')
    os.environ.update(DATABASE_URL=f'sqlite:///{database}', APP_ENV='development',
                      SMTP_HOST='', SMTP_USER='', SMTP_PASSWORD='', EMAIL_FROM='',
                      AI_SUGGESTIONS_PROVIDER='disabled')
    from fastapi.testclient import TestClient
    from app.database import engine
    from app.main import app

    if Path(engine.url.database).resolve() != database:
        raise RuntimeError('Refusing to test a database other than the restored copy')
    checks = []
    with TestClient(app) as client:
        for endpoint in ['/openapi.json', '/athletes/?limit=3', '/events/?limit=3',
                         '/events/calendar?limit=3', '/analytics/rankings?limit=3&discipline=MAG&apparatus=AA']:
            response = client.get(endpoint)
            assert response.status_code == 200, (endpoint, response.status_code)
            checks.append({'endpoint': endpoint, 'status': response.status_code})
        for role in ['user', 'admin', 'super_admin']:
            response = client.post('/auth/demo-login', json={'role': role})
            assert response.status_code == 200, (role, response.status_code)
            headers = {'Authorization': 'Bearer ' + response.json()['access_token']}
            me = client.get('/auth/me', headers=headers)
            assert me.status_code == 200 and me.json()['role'] == role
            for endpoint, expected in [('/preferences/athletes/followed', 200),
                                       ('/preferences/events/saved', 200),
                                       ('/notifications/', 200),
                                       ('/admin/data-overview', 403 if role == 'user' else 200),
                                       ('/admin/users', 200 if role == 'super_admin' else 403),
                                       ('/admin/audit-logs?limit=3', 200 if role == 'super_admin' else 403)]:
                result = client.get(endpoint, headers=headers)
                assert result.status_code == expected, (role, endpoint, result.status_code)
                checks.append({'role': role, 'endpoint': endpoint, 'status': result.status_code})
    engine.dispose()
    after = inspect_database(database)
    for table in ['athletes', 'events', 'results', 'event_calendar_entries', 'athlete_country_changes']:
        assert after['table_counts'][table] == manifest['database']['table_counts'][table], table
    report = {'status': 'passed', 'database': str(database), 'checks': checks,
              'integrity_check': after['integrity_check'], 'foreign_key_violations': after['foreign_key_violations'],
              'sports_table_counts_unchanged': True,
              'notes': 'Only the new restored copy was modified: scans disabled, demo sessions and reminders tested.'}
    (args.output / 'smoke-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
