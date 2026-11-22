"""Bounded public-source collection and append-only snapshot provenance."""
from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,json,time,urllib.request
ROOT=Path(__file__).resolve().parents[1]
def now():return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def fetch(url,limit=80_000_000,data=None,headers=None):
    if not url.startswith('https://'):raise ValueError('HTTPS sources required')
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,data=data,headers={'User-Agent':'CoolCode public data research (+https://coolcode.ca/)',**(headers or {})})
            with urllib.request.urlopen(req,timeout=90) as r:raw=r.read(limit+1)
            if len(raw)>limit:raise ValueError('Source exceeds size limit')
            return raw
        except (OSError,TimeoutError):
            if attempt==2:raise RuntimeError('Public source download failed') from None
            time.sleep(attempt+1)
def getjson(url,**kw):return json.loads(fetch(url,**kw))
def validate(data):
    rows=data.get('records')
    if data.get('schema')!=1 or not isinstance(rows,list) or not rows:raise ValueError('Expected a nonempty source dataset')
    ids=[r.get('id') for r in rows]
    if any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)):raise ValueError('Missing or duplicate source identities')
    json.dumps(data,allow_nan=False)
    if not data.get('sources') or not all(s.get('url','').startswith('https://') for s in data['sources']):raise ValueError('Expected HTTPS source evidence')
    return data

def changes(before,after):
    old={r['id']:r for r in before};new={r['id']:r for r in after}
    added=sorted(new.keys()-old.keys());removed=sorted(old.keys()-new.keys());changed=sorted(k for k in old.keys()&new.keys() if old[k].get('_fingerprint',old[k])!=new[k].get('_fingerprint',new[k]))
    return {'initial':not bool(old),'added':len(added),'removed':len(removed),'changed':len(changed),'examples':([{'kind':'added','after':new[k]} for k in added]+[{'kind':'changed','before':old[k],'after':new[k]} for k in changed]+[{'kind':'removed','before':old[k]} for k in removed])[:300]}

def save(records,*,sources,coverage,warnings=None,extra=None):
    stamp=now();folder=ROOT/'data';folder.mkdir(exist_ok=True)
    old=json.loads((folder/'current.json').read_text()) if (folder/'current.json').exists() else {'records':[]}
    payload=validate({'schema':1,'captured_at':stamp,'checked_at':stamp,'records':records,'sources':sources,'coverage':coverage,'warnings':warnings or [],**(extra or {})})
    encoded=json.dumps(records,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode();digest=sha(encoded)
    history=json.loads((folder/'history.json').read_text()) if (folder/'history.json').exists() else []
    if old.get('records_sha256')==digest:
        old['checked_at']=stamp;old['sources']=sources;old['warnings']=warnings or []
        payload=old
    else:
        payload['records_sha256']=digest;payload['changes']=changes(old['records'],records)
        filename='archive/'+stamp[:7]+'/'+stamp.replace(':','').replace('-','')+'-'+digest[:12]+'.json.gz'
        raw=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode();target=ROOT/filename;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(gzip.compress(raw,mtime=0))
        history.append({'captured_at':stamp,'file':filename,'count':len(records),'sha256':sha(raw),'initial':payload['changes']['initial'],'added':payload['changes']['added'],'removed':payload['changes']['removed'],'changed':payload['changes']['changed'],'coverage':coverage})
    for name,value in [('current.json',payload),('history.json',history)]:
        p=folder/name;temp=p.with_suffix('.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n');temp.replace(p)
    print(f'Saved {len(records):,} records; {len(history)} retained versions')
    return payload
