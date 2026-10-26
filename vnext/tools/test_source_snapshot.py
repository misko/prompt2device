import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import admission
import source_snapshot as s

class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='pcb-snapshot-test-')
        self.addCleanup(self.temp.cleanup); self.p=Path(self.temp.name)
        self.a='03_src/rules/power_tree.yaml';self.b='03_src/rules/integration.yaml'
        self.write(self.a,{'value':1,'peer':{'path':self.b,'pointer':'/value'}})
        self.write(self.b,{'value':2,'peer':{'path':self.a,'pointer':'/value'}})
    def write(self,name,obj):
        path=self.p/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(obj))
    def test_mutual_semantic_references_work(self):
        self.assertEqual(len(s.validate(self.p,s.collect(self.p))),2)
    def test_old_embedded_hash_rejected_even_if_fresh(self):
        obj=s.read(self.p,self.a);obj['peer']['sha256']=s.digest(self.p,self.b)
        self.write(self.a,obj)
        with self.assertRaisesRegex(s.SnapshotError,'embedded'):s.validate(self.p,s.collect(self.p))
    def test_stale_and_unbound_members(self):
        snap=s.collect(self.p);self.write(self.b,{'value':3})
        with self.assertRaisesRegex(s.SnapshotError,'stale'):s.validate(self.p,snap)
        snap=s.collect(self.p);snap.pop(self.b)
        with self.assertRaisesRegex(s.SnapshotError,'unbound'):s.validate(self.p,snap)
    def test_added_and_deleted_members(self):
        snap=s.collect(self.p);self.write('03_src/rules/new.json',{'value':3})
        with self.assertRaisesRegex(s.SnapshotError,'unbound'):s.validate(self.p,snap)
        snap=s.collect(self.p);(self.p/self.b).unlink()
        with self.assertRaisesRegex(s.SnapshotError,'missing'):s.validate(self.p,snap)
    def test_pointer_and_path_escape(self):
        self.write(self.a,{'value':1,'peer':{'path':self.b,'pointer':'/absent'}})
        with self.assertRaisesRegex(s.SnapshotError,'pointer'):s.validate(self.p,s.collect(self.p))
        self.write(self.a,{'value':1,'peer':{'path':'03_src/../../outside.json'}})
        with self.assertRaisesRegex(s.SnapshotError,'unsafe'):s.validate(self.p,s.collect(self.p))
    def test_duplicate_yaml_and_malformed_pointer(self):
        path=self.p/'03_src/rules/requirements.yaml';path.write_text('value: 1\nvalue: 2\n')
        with self.assertRaisesRegex(s.SnapshotError,'duplicate'):s.validate(self.p,s.collect(self.p))
        path.unlink()
        self.write(self.a,{'value':1,'peer':{'path':self.b,'pointer':'/value~2'}})
        with self.assertRaisesRegex(s.SnapshotError,'pointer'):s.validate(self.p,s.collect(self.p))
    def test_symlink_escape(self):
        target=self.p/'outside.json';target.write_text('{}')
        other=self.p/'03_src/rules/link.json';other.symlink_to('/etc/hosts')
        with self.assertRaisesRegex(s.SnapshotError,'escaping'):s.collect(self.p)
    def test_architecture_admission_enforces_membership_and_coverage(self):
        for name in ('01_docs/ARCHITECTURE.md','01_docs/DETAIL_DESIGN.md'):
            path=self.p/name;path.parent.mkdir(exist_ok=True);path.write_text('fixture source')
        subjects=s.collect(self.p)
        for name in ('01_docs/ARCHITECTURE.md','01_docs/DETAIL_DESIGN.md'):subjects[name]=s.digest(self.p,name)
        review=dict(schema=1,stage='PCB-ARCHITECTURE',author='author',reviewer='reviewer',verdict='PASS',subjects=subjects,
            checks={k:dict(verdict='PASS',evidence=list(subjects),rationale='fixture-only independent evidence') for k in admission.CRITERIA['PCB-ARCHITECTURE']})
        path=self.p/'08_reviews/2026-10-03-fixture.md';path.parent.mkdir()
        def save():path.write_text('```json\n'+json.dumps(review)+'\n```\n')
        save();admission.review_data(self.p,'08_reviews/2026-10-03-fixture.md')
        extra='03_src/rules/pod.json';self.write(extra,{'value':4})
        with self.assertRaisesRegex(admission.AdmissionError,'snapshot'):admission.review_data(self.p,'08_reviews/2026-10-03-fixture.md')
        review['subjects'][extra]=s.digest(self.p,extra);save()
        with self.assertRaisesRegex(admission.AdmissionError,'coverage'):admission.review_data(self.p,'08_reviews/2026-10-03-fixture.md')
    def test_crow_isolated_representation_replay(self):
        # Replay from the preserved pre-migration case, never mutable live inputs.
        source=Path(__file__).resolve().parents[1]/'project/01_docs/history/pre-live-source-snapshot-20261004/rules'
        if not source.is_dir():self.skipTest('Crow replay input not in this checkout')
        dest=self.p/'crow';shutil.copytree(source,dest/'03_src/rules')
        with self.assertRaisesRegex(s.SnapshotError,'embedded'):s.validate(dest,s.collect(dest))
        removed=0
        for file in (dest/'03_src/rules').glob('*'):
            if not file.read_text().lstrip().startswith('{'):continue
            obj=json.loads(file.read_text()); before=copy.deepcopy(obj)
            for ref in s.objects(obj):
                if isinstance(ref.get('path'),str) and ref['path'].startswith('03_src/') and 'sha256' in ref:
                    del ref['sha256'];removed+=1
            file.write_text(json.dumps(obj,indent=2)+'\n')
        self.assertEqual(removed,44)
        snapshot=s.collect(dest);self.assertEqual(len(s.validate(dest,snapshot)),12)
        # Source drift after the whole-set snapshot invalidates it, even with no embedded hashes.
        path=dest/'03_src/rules/pod.yaml';path.write_text(path.read_text()+'\n')
        with self.assertRaisesRegex(s.SnapshotError,'stale'):s.validate(dest,snapshot)

if __name__=='__main__':unittest.main(verbosity=2)
