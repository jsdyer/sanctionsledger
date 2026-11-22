import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import common
class ArchiveTests(unittest.TestCase):
 def test_changes_preserve_corrections_and_absence(self):
  c=common.changes([{'id':'1','name':'old'},{'id':'2'}],[{'id':'1','name':'new'},{'id':'3'}]);self.assertEqual((c['added'],c['changed'],c['removed']),(1,1,1));self.assertFalse(c['initial'])
 def test_empty_duplicate_and_nan_records_rejected(self):
  for rows in [[],[{'id':'a'},{'id':'a'}],[{'id':'a','value':float('nan')}]]:
   with self.assertRaises(ValueError):common.validate({'schema':1,'records':rows,'sources':[{'url':'https://example.org'}]})
 def test_unchanged_dataset_does_not_replace_archive(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(common,'ROOT',Path(tmp)):
   common.save([{'id':'1','v':1}],sources=[{'url':'https://example.org'}],coverage='test');files=list(Path(tmp).glob('archive/*/*'));before=files[0].read_bytes()
   common.save([{'id':'1','v':1}],sources=[{'url':'https://example.org'}],coverage='test');self.assertEqual(len(list(Path(tmp).glob('archive/*/*'))),1);self.assertEqual(files[0].read_bytes(),before)
