#!/usr/bin/env python3
"""Verified official source extraction proof. Research only; no repository writes.
Run --download to retrieve fresh source files, otherwise parse saved fixtures.
"""
import argparse,calendar,collections,csv,hashlib,html,json,re,xml.etree.ElementTree as ET
from datetime import datetime,timezone,timedelta
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]/'.cache'
ROOT.mkdir(exist_ok=True)
URLS={
 'sanctions.xml':'https://www.international.gc.ca/world-monde/assets/office_docs/international_relations-relations_internationales/sanctions/sema-lmes.xml',
 'sanctions-page.html':'https://www.international.gc.ca/world-monde/international_relations-relations_internationales/sanctions/consolidated-consolide.aspx?lang=eng',
 'current.csv':'https://www.cbsa-asfc.gc.ca/bwt-taf/bwt-eng.csv',
 'history.csv':'https://open.canada.ca/data/dataset/000fe5aa-1d77-42d1-bfe7-458c51dacfef/resource/2b5853e4-41b4-4858-86dd-38012e30d5b8/download/land-bwt-opengov-en.csv',
 'border-2019q4.csv':'https://www.cbsa-asfc.gc.ca/data/bwt-taf-2019-10-01--2019-12-31-en.csv',
 'border-reference.odt':'https://www.cbsa-asfc.gc.ca/data/bwt-taf--ref.odt',
 'changelog.txt':'https://www.cbsa-asfc.gc.ca/data/bwt-taf--changelog.txt'
}
CROSSINGS={'Douglas':'peace-arch','Douglas (Peace Arch)':'peace-arch','Pacific Highway':'pacific-highway','Aldergrove':'aldergrove','Abbotsford-Huntingdon':'sumas'}
LABELS={'peace-arch':'Peace Arch (Douglas)','pacific-highway':'Pacific Highway','aldergrove':'Aldergrove','sumas':'Sumas (Abbotsford-Huntingdon)'}
def get(name):
 with urlopen(Request(URLS[name],headers={'User-Agent':'CoolCode source research'}),timeout=60) as r: raw=r.read(40_000_001)
 if len(raw)>40_000_000:raise ValueError('Source exceeds size cap')
 (ROOT/name).write_bytes(raw)
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def clean(s):return ' '.join((s or '').split())
def dump(name,data): (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
def sanctions():
 fields={'Country-Pays':'regime','Schedule-Annexe':'schedule','Item-NumeroDarticle':'item','DateOfListing-DateDinscription':'listed_date','LastName-NomDeFamille':'surname','GivenName-Prenom':'given_names','Aliases-Alias':'aliases','EntityOrShip-EntiteOuNavire':'entity_or_ship','DateOfBirthOrShipBuildDate-DateDeNaissanceOuDateDeConstructionDuNavire':'birth_or_build_date','TitleOrShipType-TitreOuTypeDeNavire':'title_or_ship_type','ShipIMONumber-NumeroOMIDuNavire':'imo'}
 rows=[];keys=set()
 regulation_map=json.loads((ROOT/'regulation-map.json').read_text()) if (ROOT/'regulation-map.json').exists() else {}
 for element in ET.parse(ROOT/'sanctions.xml').getroot().findall('record'):
  row={fields[k.tag]:clean(k.text) for k in element if k.tag in fields}
  if not row.get('regime') or not row.get('item'):raise ValueError('Missing statutory slot')
  row.setdefault('schedule','');key='|'.join(row[k] for k in ['regime','schedule','item'])
  if key in keys:raise ValueError('Ambiguous statutory slot')
  keys.add(key);row['id']=hashlib.sha256(key.encode()).hexdigest()[:24]
  row['name']=row.get('entity_or_ship') or clean(row.get('given_names','')+' '+row.get('surname',''))
  row['kind']='ship' if row.get('imo') else 'entity' if row.get('entity_or_ship') else 'individual'
  row.update(regulation_map.get(row['regime'].split(' / ')[0],{}))
  rows.append(row)
 if len(rows)<1000:raise ValueError('Truncated sanctions response')
 plain=clean(html.unescape(re.sub(r'<[^>]*>',' ',(ROOT/'sanctions-page.html').read_text())))
 match=re.search(r'list was last updated on ([A-Za-z]+ \d{1,2}, \d{4})',plain)
 updated=datetime.strptime(match[1],'%B %d, %Y').date().isoformat() if match else None
 dump('sanctions-normalized.json',{'source_url':URLS['sanctions.xml'],'source_sha256':sha('sanctions.xml'),'source_updated':updated,'rows':rows,'count':len(rows)})
 return rows

def wait_value(raw):
 s=clean(raw).casefold()
 if s=='no delay':return {'status':'censored','lower':0,'upper':5,'raw':raw}
 m=re.fullmatch(r'(\d+)(?:\s+minutes?)?',s)
 if m:
  n=int(m[1]);
  if n>1440:raise ValueError('Out-of-range wait')
  return {'status':'numeric','lower':n,'upper':n,'raw':raw}
 if s in ('closed','temporarily closed'):return {'status':'closed','lower':None,'upper':None,'raw':raw}
 if s in ('missed entry','not applicable','--',''):return {'status':'missing','lower':None,'upper':None,'raw':raw}
 raise ValueError('Unknown wait category '+raw)
def timestamp(raw):
 # Respect the supplied zone label, not a guessed current DST policy.
 m=re.fullmatch(r'(\d{4}-\d\d-\d\d \d\d:\d\d) (PDT|PST)',raw)
 if not m:raise ValueError('Unexpected Pacific timestamp '+raw)
 dt=datetime.strptime(m[1],'%Y-%m-%d %H:%M').replace(tzinfo=timezone(timedelta(hours=-7 if m[2]=='PDT' else -8)))
 return {'local_time':m[1],'reported_zone':m[2],'reported_at':dt.astimezone(timezone.utc).isoformat().replace('+00:00','Z'),'weekday':dt.weekday(),'hour':dt.hour}
def quantile(vals,p):
 vals=sorted(vals);pos=(len(vals)-1)*p;lo=int(pos);hi=min(lo+1,len(vals)-1);return round(vals[lo]+(vals[hi]-vals[lo])*(pos-lo),2)
def stats(rows):
 usable=[r for r in rows if r.get('lower') is not None]
 return {'n':len(usable),'censored':sum(r['status']=='censored' for r in usable),'median_lower':quantile([r['lower'] for r in usable],.5) if usable else None,'median_upper':quantile([r['upper'] for r in usable],.5) if usable else None,'p90_lower':quantile([r['lower'] for r in usable],.9) if usable else None,'p90_upper':quantile([r['upper'] for r in usable],.9) if usable else None}
def border():
 groups=collections.defaultdict(list)
 for row in csv.DictReader((ROOT/'border-2019q4.csv').open(encoding='utf-8-sig')):
  crossing=CROSSINGS.get(row['Custom Office Name'].strip())
  if crossing and '2019-10-01'<=row['Updated'][:10]<='2019-12-31':groups[(crossing,row['Updated'])].append(row['Travellers Flow'])
 observations=[];conflicts=0;duplicate_copies=0
 for (crossing,t),vals in groups.items():
  distinct={clean(x).casefold() for x in vals};duplicate_copies+=len(vals)-len(distinct)
  row={'crossing':crossing,**timestamp(t),'source_rows':len(vals)}
  if len(distinct)>1:
   row.update({'status':'conflicting','lower':None,'upper':None,'reported_values':sorted(distinct)});conflicts+=1
  else: row.update(wait_value(vals[0]))
  observations.append(row)
 heat=collections.defaultdict(list)
 for r in observations:heat[(r['crossing'],r['weekday'],r['hour'])].append(r)
 cells=[{'crossing':k[0],'weekday':k[1],'hour':k[2],**stats(v),'conflicting':sum(r['status']=='conflicting' for r in v),'missing_or_closed':sum(r['status'] in ('closed','missing') for r in v)} for k,v in sorted(heat.items())]
 monthly=[]
 for row in csv.DictReader((ROOT/'history.csv').open(encoding='utf-8-sig')):
  crossing=CROSSINGS.get(row['Port of Entry'].strip())
  if not crossing:continue
  month=list(calendar.month_name).index(row['Month']);year=int(row['Fiscal Year'][:4])+(month<4)
  value=row['Percentage Met Service Standard'].strip().rstrip('%')
  try:p=float(value)
  except ValueError:p=None
  if p is not None and not 0<=p<=100:raise ValueError('Invalid service percentage')
  monthly.append({'crossing':crossing,'month':f'{year}-{month:02d}','service_standard_met_percent':p})
 current=[];lines=(ROOT/'current.csv').read_text(encoding='utf-8-sig').strip().splitlines()
 for line in lines[1:]:
  parts=[x.strip() for x in line.split(';;')]
  crossing=CROSSINGS.get(parts[0])
  if crossing:current.append({'crossing':crossing,'source_name':parts[0],**timestamp(parts[2]),'travellers':wait_value(parts[5]),'commercial':wait_value(parts[3])})
 result={'crossings':LABELS,'historical_period':['2019-10-01','2019-12-31'],'heatmap':cells,'observations':observations,'current':current,'monthly':monthly,'diagnostics':{'unique_crossing_hours':len(groups),'conflicting_hours_excluded':conflicts,'duplicate_copies':duplicate_copies,'usable_hours':sum(r['lower'] is not None for r in observations)},'sources':[{'url':URLS[n],'sha256':sha(n)} for n in ['border-2019q4.csv','history.csv','current.csv','border-reference.odt','changelog.txt']]}
 dump('border-normalized.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--download',action='store_true');args=p.parse_args()
 if args.download:
  for name in URLS:get(name)
 s=sanctions();b=border();print(json.dumps({'sanctions':len(s),'border':b['diagnostics'],'monthly':len(b['monthly']),'current':len(b['current'])},indent=2))
