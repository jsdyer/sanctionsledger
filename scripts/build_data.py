import json,shutil
from common import validate
from xml.sax.saxutils import escape

def assemble(root,stage):
    current=validate(json.loads((root/'data/current.json').read_text()))
    history=json.loads((root/'data/history.json').read_text())
    if not history:raise ValueError('Missing archive provenance')
    shutil.copytree(root/'data',stage/'data')
    shutil.copytree(root/'archive',stage/'archive')
    tool=json.loads((root/'tool.json').read_text());url='https://coolcode.ca/'+tool['id']+'/'
    items=[]
    for entry in reversed(history[-52:]):
        detail='Initial baseline' if entry['initial'] else f"{entry['added']} added, {entry['changed']} changed, {entry['removed']} removed from the selected dataset"
        items.append('<item><title>'+escape(entry['captured_at']+' · '+detail)+'</title><link>'+url+'</link><guid>'+url+entry['file']+'</guid><description>'+escape(entry['coverage'])+'</description></item>')
    (stage/'feed.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>'+escape(tool['title']+' · snapshot diary')+'</title><link>'+url+'</link><description>New captures and observed changes; baseline is not a historical event.</description>'+''.join(items)+'</channel></rss>')
