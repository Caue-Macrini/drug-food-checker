"""Lossless, data-only MySQL dump reader. Never executes the downloaded SQL."""
import argparse, hashlib, json, re, sqlite3, time, unicodedata
from pathlib import Path

EXPECTED_MD5='3c8f26240dd571ded1e4b100d1dfc9d2'
TOKEN=re.compile(r"'(?:[^'\\]|\\.)*'|NULL|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?",re.S)
ESCAPES={'0':'\0','n':'\n','r':'\r','t':'\t','Z':'\x1a'}
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',(s or '').strip().lower()) if not unicodedata.combining(c))
def value(token):
    if token=='NULL':return None
    if token.startswith("'"):return re.sub(r'\\(.)',lambda m:ESCAPES.get(m[1],m[1]),token[1:-1],flags=re.S)
    return float(token) if any(c in token.lower() for c in '.e') else int(token)

def tuples(text, columns):
    pos=0;length=len(text)
    while pos<length:
        while pos<length and text[pos].isspace():pos+=1
        if text[pos:pos+1]==';':
            if text[pos+1:].strip():raise ValueError('Data after statement')
            return
        if text[pos:pos+1]!='(':raise ValueError(f'Expected tuple at {pos}: {text[pos:pos+40]!r}')
        pos+=1;row=[]
        for col in range(columns):
            m=TOKEN.match(text,pos)
            if not m:raise ValueError(f'Unsupported SQL literal at {pos}: {text[pos:pos+60]!r}')
            row.append(value(m[0]));pos=m.end()
            delimiter=',' if col<columns-1 else ')'
            if text[pos:pos+1]!=delimiter:raise ValueError('Unexpected tuple arity')
            pos+=1
        yield row
        if text[pos:pos+1]==',':pos+=1

def build(source, output, verify=True):
    source=Path(source);output=Path(output)
    digest=hashlib.file_digest(source.open('rb'),'md5').hexdigest()
    if verify and digest!=EXPECTED_MD5:raise ValueError('Official checksum mismatch; refusing partial dump')
    if output.exists():raise ValueError('Output already exists; choose a new staging filename')
    conn=sqlite3.connect(output);conn.execute('PRAGMA journal_mode=OFF');conn.execute('PRAGMA synchronous=OFF');conn.execute('PRAGMA cache_size=-100000')
    schemas={};counts={};current=None;columns=[];types=[];complete=False;t0=time.time()
    try:
        with source.open(encoding='utf-8') as stream:
            for line in stream:
                create=re.match(r'CREATE TABLE `([A-Za-z0-9_]+)` \(',line)
                if create:current=create[1];columns=[];types=[];continue
                if current:
                    column=re.match(r'  `([A-Za-z0-9_]+)` ([a-zA-Z]+)',line)
                    if column:
                        columns.append(column[1]);types.append('INTEGER' if 'int' in column[2] else 'REAL' if column[2] in ('float','double','decimal') else 'TEXT')
                    elif line.startswith(') ENGINE='):
                        schemas[current]=columns;counts[current]=0
                        conn.execute('CREATE TABLE "'+current+'" ('+','.join('"'+n+'" '+t for n,t in zip(columns,types))+')')
                        current=None
                    continue
                insert=re.match(r'INSERT INTO `([A-Za-z0-9_]+)` VALUES ',line)
                if insert:
                    table=insert[1]
                    if table not in schemas:raise ValueError('Missing table schema')
                    batch=list(tuples(line[insert.end():],len(schemas[table])))
                    conn.executemany('INSERT INTO "'+table+'" VALUES ('+','.join('?' for _ in schemas[table])+')',batch)
                    counts[table]+=len(batch)
                if line.startswith('UNLOCK TABLES;'):
                    conn.commit();print('Imported',counts,'seconds',round(time.time()-t0),flush=True)
                if line.startswith('-- Dump completed on '):complete=True
        if not complete:raise ValueError('Missing dump completion marker')
        conn.commit()
        manifest={'version':'FooDrugs 4.0.0','doi':'10.5281/zenodo.8192515','md5':digest,'bytes':source.stat().st_size,'tables':{t:{'columns':cols,'rows':counts[t]} for t,cols in schemas.items()},'complete':True}
        conn.execute('CREATE TABLE _metadata (key TEXT PRIMARY KEY, value TEXT)')
        conn.execute('INSERT INTO _metadata VALUES (?,?)',('manifest',json.dumps(manifest)))
        conn.commit()
        if conn.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Database integrity check failed')
        output.with_suffix('.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        print('ALL TABLES IMPORTED',json.dumps(counts),flush=True)
        return manifest
    finally:conn.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('dump');p.add_argument('output');a=p.parse_args();build(a.dump,a.output)
