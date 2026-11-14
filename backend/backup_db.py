"""Backup of the application database (accounts, profiles, consents, history, audit).

Uses SQLite's online backup API, so it is safe while the server is running, checks the copy with
PRAGMA integrity_check and keeps the most recent KEEP copies. The FooDrugs scientific database is
read-only and can be reinstalled, so it is not copied.
"""
import sqlite3, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'drugfood.db'
TARGET_DIR = ROOT.parent / 'backups' / 'drugfood'
KEEP = 14

def backup():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    target = TARGET_DIR / f'drugfood-{time.strftime("%Y%m%d-%H%M%S")}.db'
    src = sqlite3.connect(f'file:{SOURCE}?mode=ro', uri=True)
    dst = sqlite3.connect(target)
    with dst:
        src.backup(dst)
    ok = dst.execute('PRAGMA integrity_check').fetchone()[0]
    users = dst.execute('SELECT count(*) FROM usuarios').fetchone()[0]
    src.close(); dst.close()
    if ok != 'ok':
        target.unlink(missing_ok=True)
        raise SystemExit(f'Backup inválido: {ok}')
    copies = sorted(TARGET_DIR.glob('drugfood-*.db'))
    for old in copies[:-KEEP]:
        old.unlink()
    print(f'Backup criado: {target.name} ({users} contas, {target.stat().st_size // 1024} KB); mantidas {min(len(copies), KEEP)} cópias.')

if __name__ == '__main__':
    sys.exit(backup())
