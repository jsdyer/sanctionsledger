from pathlib import Path
import contextlib,http.server,socketserver,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'dist'),**kwargs)
 def log_message(self,*args):pass
with socketserver.TCPServer(('127.0.0.1',0),Handler) as server:
 threading.Thread(target=server.serve_forever,daemon=True).start()
 with sync_playwright() as p:
  browser=p.chromium.launch();page=browser.new_page(viewport={'width':1280,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_address[1]}/');page.locator('#rows tr').first.wait_for(timeout=60000)
  page.locator('#query').fill('zzzz_no_such_record_5938');assert page.locator('#rows tr').count()==0;assert page.locator('#empty').is_visible()
  page.locator('#query').fill('');page.locator('#rows tr button').first.click();assert page.locator('#detail').is_visible()
  with page.expect_download() as download:page.locator('#export').click()
  assert download.value.suggested_filename.endswith('.csv')
  page.locator('#snapshot').select_option(index=1);page.locator('#rows tr').first.wait_for(timeout=60000)
  page.locator('#detail').evaluate('(el)=>el.hidden=true')
  page.locator('body').press('Control+Home');(ROOT/'browser-checks').mkdir(exist_ok=True);page.screenshot(path=str(ROOT/'browser-checks/desktop.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(ROOT/'browser-checks/mobile.png'),full_page=True)
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'), 'Mobile viewport overflow'
  assert not errors,errors
  browser.close()
 server.shutdown()
print('Desktop/mobile flows and CSV passed')
