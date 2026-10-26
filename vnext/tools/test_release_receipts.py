"""Release provenance must select the live owning contract, not default filenames."""
import json
from pathlib import Path
import tempfile
import unittest
import release_review as r

class Receipts(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        for role in r.UPSTREAM:self.put('06_build/checkpoints/'+role+'.json',dict(role=role,review='old'))
        self.selected='06_build/checkpoints/revision/placement_reviewed.json'
        self.mating='06_build/checkpoints/revision/mating_clearance.json'
        self.put(self.selected,dict(role='placement_reviewed',review='new'))
        self.put(self.mating,dict(role='mating_clearance',review='new'))
        self.contract=dict(version=3,placement_receipt=self.selected,mating_receipt=self.mating,
                           placement_receipt_sha256=r.p.sha(self.root/self.selected))
        self.save()

    def put(self,name,data):
        f=self.root/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(data))
    def save(self):self.put('01_docs/routing-contract.json',self.contract)

    def test_selected_versions_replace_old_default_roles(self):
        paths=r.upstream_receipts(self.root)
        self.assertEqual(paths['placement_reviewed'],self.selected)
        self.assertEqual(paths['mating_clearance'],self.mating)
        self.assertNotIn('06_build/checkpoints/placement_reviewed.json',paths.values())

    def test_missing_selected_mate_cannot_fall_back_to_existing_default(self):
        (self.root/self.mating).unlink()
        with self.assertRaises(ValueError):r.upstream_receipts(self.root)

    def test_wrong_role_and_stale_selected_placement_rejected(self):
        self.put(self.mating,dict(role='placement_reviewed'))
        with self.assertRaisesRegex(ValueError,'role differs'):r.upstream_receipts(self.root)
        self.put(self.mating,dict(role='mating_clearance'))
        self.put(self.selected,dict(role='placement_reviewed',review='changed'))
        with self.assertRaisesRegex(ValueError,'adoption changed'):r.upstream_receipts(self.root)

    def test_legacy_contract_explicitly_selects_legacy_paths(self):
        self.contract=dict(version=1,placement_receipt_sha256=r.p.sha(self.root/'06_build/checkpoints/placement_reviewed.json'))
        self.save();paths=r.upstream_receipts(self.root)
        self.assertEqual(paths['placement_reviewed'],'06_build/checkpoints/placement_reviewed.json')
        self.assertEqual(paths['mating_clearance'],'06_build/checkpoints/mating_clearance.json')

if __name__=='__main__':unittest.main()
