"""Download the complete official V4 dump, with resumable HTTP ranges and MD5 verification."""
import concurrent.futures, hashlib, json, time, urllib.request
from pathlib import Path

URL='https://zenodo.org/records/8192515/files/FinalFooDrugs_v4.sql?download=1'
SIZE=1561331208
MD5='3c8f26240dd571ded1e4b100d1dfc9d2'
ROOT=Path(__file__).resolve().parents[1]/'.local-data'

def download(workers=6):
    ROOT.mkdir(exist_ok=True)
    size=32*1024*1024
    def part(i):
        start=i*size;end=min(SIZE,start+size)-1
        p=ROOT/f'foodrugs-v4.part-{i:03d}'
        # An interrupted filesystem write can leave zero-filled holes. MySQL's
        # text dump escapes NUL characters; raw NUL bytes are never valid here.
        if p.exists():
            with p.open('r+b') as check:
                position=0
                while block:=check.read(1024*1024):
                    if b'\x00' in block:
                        check.truncate(position);break
                    position+=len(block)
        for attempt in range(8):
            have=p.stat().st_size if p.exists() else 0
            if have==end-start+1:return p
            if have>end-start+1:raise ValueError('Invalid part length')
            request=urllib.request.Request(URL,headers={'Range':f'bytes={start+have}-{end}','User-Agent':'DrugFoodChecker-academic-import/1.0'})
            try:
                with urllib.request.urlopen(request,timeout=90) as response:
                    expected=f'bytes {start+have}-{end}/{SIZE}'
                    if response.status!=206 or response.headers.get('Content-Range')!=expected:
                        raise ValueError('Unexpected HTTP range: '+str(response.headers))
                    with p.open('ab') as out:
                        while chunk:=response.read(1024*1024):out.write(chunk)
            except Exception as exc:
                print(f'Part {i}: retry {attempt+1}: {exc}',flush=True)
                time.sleep(min(30,2**attempt))
        raise RuntimeError(f'Download incomplete: {p}')
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(part,i) for i in range((SIZE+size-1)//size)]
        for n,f in enumerate(concurrent.futures.as_completed(futures),1):
            f.result();print(f'Download: {n}/{len(futures)} complete parts',flush=True)
    target=ROOT/'FinalFooDrugs_v4.sql';digest=hashlib.md5()
    with target.open('wb') as out:
        for i in range((SIZE+size-1)//size):
            with (ROOT/f'foodrugs-v4.part-{i:03d}').open('rb') as inp:
                while chunk:=inp.read(4*1024*1024):digest.update(chunk);out.write(chunk)
    if digest.hexdigest()!=MD5:raise RuntimeError('Official MD5 mismatch')
    (ROOT/'download-manifest.json').write_text(json.dumps({'url':URL,'size':target.stat().st_size,'md5':digest.hexdigest(),'verified':True},indent=2),encoding='utf-8')
    print('Complete official dump verified: '+str(target),flush=True)
    return target

if __name__=='__main__':download()
