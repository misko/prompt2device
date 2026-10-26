"""The complete real catalog must render without implying acceptance."""
import json
from pathlib import Path
import tempfile
import unittest
import hashlib

import workflow


class Display(unittest.TestCase):
    def test_version3_selects_unissued_mating_instead_of_historical_receipt(self):
        graph=json.loads((workflow.ROOT/'skills/pcb-design/workflow/graph.json').read_text())
        stages=[s for s in graph['stages'] if s['spec']['id']=='KICAD-MATING-IMPORT']
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'01_docs').mkdir();(root/'06_build/checkpoints').mkdir(parents=True)
            (root/'06_build/checkpoints/mating_clearance.json').write_text('historical')
            (root/'01_docs/routing-contract.json').write_text(json.dumps(dict(version=3,mating_receipt='new/mating.json')))
            calls=[];rows=workflow.stage_rows(root,stages,None,True,lambda p,c:calls.append(c))
            self.assertIn('no receipt','\n'.join(rows));self.assertFalse(calls)
            (root/'new').mkdir();(root/'new/mating.json').write_text('fixture')
            rows=workflow.stage_rows(root,stages,None,True,lambda p,c:calls.append(c))
            self.assertEqual(calls,[['routing.py','check','--kind','mating']])

    def test_every_catalog_stage_renders_without_receipts(self):
        graph = json.loads((workflow.ROOT/'skills/pcb-design/workflow/graph.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            rows = workflow.stage_rows(Path(directory), graph['stages'], 'KICAD-MATING-IMPORT')
        text = '\n'.join(rows)
        for stage in graph['stages']:
            self.assertIn('| '+stage['spec']['id']+' |', text)
        self.assertNotIn('owning check PASS', text)
        self.assertIn('yes (STATUS only)', text)

    def test_versioned_receipt_is_selected_and_checked(self):
        graph=json.loads((workflow.ROOT/'skills/pcb-design/workflow/graph.json').read_text())
        stages=[s for s in graph['stages'] if s['spec']['id']=='KICAD-PLACEMENT']
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'01_docs').mkdir();(root/'versioned').mkdir()
            receipt=root/'versioned/placement.json';receipt.write_text('{"fixture":true}')
            contract=dict(version=2,placement_receipt='versioned/placement.json',
                          placement_receipt_sha256=hashlib.sha256(receipt.read_bytes()).hexdigest())
            binding=root/'01_docs/routing-contract.json';binding.write_text(json.dumps(contract))
            calls=[]
            rows=workflow.stage_rows(root,stages,None,True,lambda p,c:calls.append(c))
            self.assertIn('owning check PASS','\n'.join(rows))
            self.assertEqual(calls,[['placement.py','check','--receipt','versioned/placement.json']])
            self.assertEqual(workflow.OWNERS['KICAD-PLACEMENT'][1],['placement.py','check'])
            contract['placement_receipt_sha256']='wrong';binding.write_text(json.dumps(contract));calls.clear()
            rows=workflow.stage_rows(root,stages,None,True,lambda p,c:calls.append(c))
            self.assertIn('hash differs','\n'.join(rows));self.assertFalse(calls)
            contract['placement_receipt']='../escape.json';binding.write_text(json.dumps(contract))
            rows=workflow.stage_rows(root,stages,None,True,lambda p,c:calls.append(c))
            self.assertIn('invalid versioned','\n'.join(rows));self.assertFalse(calls)


if __name__ == '__main__': unittest.main()
