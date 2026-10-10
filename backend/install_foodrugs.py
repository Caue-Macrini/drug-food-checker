"""Install the entire official FooDrugs V4 database and activate it without replacing accounts/history.

Run from backend: ../.venv/Scripts/python.exe install_foodrugs.py
Requires several GB of free disk space. No server-side SQL from the dump is executed.
"""
import hashlib, json, sqlite3, time
from pathlib import Path
from sqlalchemy import select
from models import Base, engine, Session, Dataset, Audit
from services import uid
from download_foodrugs import download, ROOT, MD5
from foodrugs_full import build
from index_foodrugs import index
from foodrugs_store import VERSION

def install():
    final=ROOT/'foodrugs-v4.sqlite';stage=ROOT/'foodrugs-v4.build.sqlite';dump=ROOT/'FinalFooDrugs_v4.sql'
    if not final.exists():
        if not dump.exists() or hashlib.file_digest(dump.open('rb'),'md5').hexdigest()!=MD5:download()
        if not stage.exists():build(dump,stage)
        c=sqlite3.connect(stage)
        try:
            manifest=json.loads(c.execute("SELECT value FROM _metadata WHERE key='manifest'").fetchone()[0])
            if not manifest.get('complete') or manifest['md5']!=MD5:raise ValueError('Incomplete staging database')
            indexed=bool(c.execute("SELECT 1 FROM _metadata WHERE key='coverage'").fetchone())
        finally:c.close()
        if not indexed:index(stage)
        stage.replace(final)
        stage.with_suffix('.manifest.json').replace(final.with_suffix('.manifest.json'))
    with sqlite3.connect(final) as c:
        manifest=json.loads(c.execute("SELECT value FROM _metadata WHERE key='manifest'").fetchone()[0])
        coverage=json.loads(c.execute("SELECT value FROM _metadata WHERE key='coverage'").fetchone()[0])
        if manifest.get('md5')!=MD5 or not manifest.get('complete'):raise ValueError('Invalid source manifest')
        if c.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Source database integrity failure')
    # Back up the active account database before changing only its dataset pointer.
    if engine.url.drivername.startswith('sqlite') and engine.url.database and Path(engine.url.database).exists():
        backups=ROOT.parent/'backups';backups.mkdir(exist_ok=True)
        with sqlite3.connect(engine.url.database) as source, sqlite3.connect(backups/f'antes-foodrugs-{int(time.time())}.db') as target:source.backup(target)
    Base.metadata.create_all(engine)
    with Session() as db:
        dataset=db.scalar(select(Dataset).where(Dataset.version==VERSION))
        if not dataset:
            dataset=Dataset(id=uid(),version=VERSION,source='FooDrugs 4.0.0 integral · IMDEA Food Institute · CC BY 4.0 · https://doi.org/10.5281/zenodo.8192515',count=coverage['associations'],active=False)
            db.add(dataset);db.flush()
        for item in db.scalars(select(Dataset)):item.active=item.id==dataset.id
        db.add(Audit(id=uid(),actor=hashlib.sha256(b'local-cli-foodrugs-install').hexdigest(),action='foodrugs.full.activated'))
        db.commit()
    (ROOT.parent/'data/foodrugs-full-manifest.json').write_text(json.dumps({**manifest,'coverage':coverage},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('ACTIVE:',json.dumps(coverage),flush=True)

if __name__=='__main__':install()
