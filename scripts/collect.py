from common import ROOT,save
import source,json,shutil,argparse

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--seed',action='store_true');args=parser.parse_args()
 shutil.copyfile(ROOT/'config/regulations.json',source.ROOT/'regulation-map.json')
 if not args.seed:
  for file in ['sanctions.xml','sanctions-page.html']:source.get(file)
 rows=source.sanctions();meta=json.loads((source.ROOT/'sanctions-normalized.json').read_text())
 for r in rows:r['listed_year']=r.get('listed_date','')[:4] or 'Not reported';r['source_url']=meta['source_url']
 save(rows,sources=[{'label':'Global Affairs Canada consolidated XML','url':meta['source_url'],'sha256':meta['source_sha256'],'updated':meta['source_updated']},{'label':'Official list, limitations and regulations','url':source.URLS['sanctions-page.html']}],coverage=f"Complete parsed consolidated list · {len(rows):,} entries · source updated {meta['source_updated'] or 'not reported'}",warnings=['Reference list only. The linked regulations control and can change before this XML is updated.'],extra={'source_updated':meta['source_updated']})
if __name__=='__main__':main()
