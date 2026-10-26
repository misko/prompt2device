"""Real local Git fixtures; expensive owning PCB replay is mocked ONLY here.

The real board acceptance must separately run the unmocked owner offline.
"""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import release_seal as s


def put(file, value):
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(s.dump(value) if isinstance(value, dict) else value)


def md(file, value):
    put(file, '# Independent synthetic review\n\n```json\n'+s.dump(value)+'```\n')


class SealTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='vnext-seal-test-base-')
        cls.base=Path(cls.tmp.name);p=cls.base/'project';p.mkdir();cls.project=p
        a=p/'archive';a.mkdir()
        put(p/'brief.txt','Two boards, one accepted prototype design.\n')
        put(a/'source/project/brief.txt',(p/'brief.txt').read_text())
        put(a/'ORDER-INSTRUCTIONS.md','DO-NOT-ORDER\nPhysical qualification pending.\n')
        record=dict(version=1,release_id='test-prototype',
                    boards={'main':{'version':'rev-a','quantity':2},'sensor':{'version':'rev-a','quantity':8}},
                    aliases={},origins={'source/project/brief.txt':dict(origin='project',path='brief.txt',sha256=s.sha(p/'brief.txt'))},
                    files=s.inventory(a))
        put(a/'release.json',record)
        review=dict(output='archive',subjects={'archive/'+n:d for n,d in s.inventory(a).items()})
        md(p/'review.md',review)
        receipt=dict(role='release_reviewed',review='review.md',review_sha256=s.sha(p/'review.md'),
                     design_verdict='SOUND',order_verdict='DO-NOT-ORDER',subjects=review['subjects'],tools={},guidance={})
        put(p/s.REVIEW_RECEIPT,receipt);put(p/'scope.md','Local synthetic Git fixture only.\n')
        contract=dict(version=1,authority='scope.md',authority_sha256=s.sha(p/'scope.md'),archive='archive',
                      archive_record_sha256=s.sha(a/'release.json'),review='review.md',review_sha256=s.sha(p/'review.md'),
                      release_reviewed_sha256=s.sha(p/s.REVIEW_RECEIPT),repository='sealed',release_id=record['release_id'],
                      boards=record['boards'],seal_tool_sha256=s.sha(Path(s.__file__)))
        put(p/s.CONTRACT,contract)
        cls.replay=dict(boards=record['boards'],release_id=record['release_id'],design_verdict='SOUND',
                        order_verdict='DO-NOT-ORDER',release_reviewed_sha256=s.sha(p/s.REVIEW_RECEIPT),
                        offline=True,archive_readonly=True)
        # Fixture-specific identity; never changes user's config.
        cls.env=patch.dict(os.environ,{'GIT_AUTHOR_NAME':'Fixture','GIT_AUTHOR_EMAIL':'fixture@example.invalid',
                                     'GIT_COMMITTER_NAME':'Fixture','GIT_COMMITTER_EMAIL':'fixture@example.invalid'})
        cls.env.start()
        with patch.object(s,'owning_check',return_value=cls.replay):
            cls.prepared=s.prepare(p);repo=p/'sealed';s.stage(repo);cls.committed=s.commit(repo)

    @classmethod
    def tearDownClass(cls):
        cls.env.stop();cls.tmp.cleanup()

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='vnext-seal-test-');self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'project';shutil.copytree(self.project,self.p);self.repo=self.p/'sealed'

    def test_real_git_valid_relocated_seal_and_replay_required(self):
        with patch.object(s,'owning_check',return_value=self.replay) as replay:
            result=s.check(self.repo);self.assertTrue(result['committed_owning_replay']);replay.assert_called_once()
        self.assertEqual(result['source_commit'],self.prepared['source_commit'])
        self.assertNotEqual(result['seal_commit'],result['source_commit'])
        self.assertEqual(s.git(self.repo,'rev-list','--count','HEAD').strip(),b'2')
        with patch.object(s,'owning_check',side_effect=ValueError('owning replay failed')):
            with self.assertRaisesRegex(ValueError,'owning replay failed'):s.check(self.repo)

    def test_dirty_and_ignored_extra_source_rejected(self):
        put(self.repo/'source/project/brief.txt','changed')
        with self.assertRaises(ValueError):s.check(self.repo,replay=False)
        shutil.copyfile(self.project/'sealed/source/project/brief.txt',self.repo/'source/project/brief.txt')
        put(self.repo/'.git/info/exclude','hidden-extra\n');put(self.repo/'hidden-extra','not inventoried')
        self.assertFalse(s.git(self.repo,'status','--porcelain').strip())
        with self.assertRaisesRegex(ValueError,'source input'):s.check(self.repo,replay=False)

    def test_missing_extra_and_modified_release_rejected(self):
        target=self.repo/'release/archive/ORDER-INSTRUCTIONS.md';original=target.read_bytes()
        for action in ('modified','missing','extra'):
            with self.subTest(action=action):
                if action=='modified':put(target,'ORDER NOW')
                elif action=='missing':target.unlink()
                else:put(self.repo/'release/archive/extra.txt','extra')
                with self.assertRaises(ValueError):s.staged_check(self.repo,replay=False)
                if action=='extra':(self.repo/'release/archive/extra.txt').unlink()
                else:target.write_bytes(original)

    def test_rehashed_payload_still_must_equal_committed_sources(self):
        put(self.repo/'release/archive/ORDER-INSTRUCTIONS.md','changed')
        seal=s.read(self.repo/'release/seal.json')
        seal['files']['archive/ORDER-INSTRUCTIONS.md']=s.sha(self.repo/'release/archive/ORDER-INSTRUCTIONS.md')
        put(self.repo/'release/seal.json',seal)
        with self.assertRaises(ValueError):s.staged_check(self.repo,replay=False)

    def test_mixed_board_versions_fail(self):
        seal=s.read(self.repo/'release/seal.json');seal['boards']['sensor']['version']='rev-b'
        put(self.repo/'release/seal.json',seal)
        with self.assertRaisesRegex(ValueError,'adoption/identity'):s.staged_check(self.repo,replay=False)

    def test_absent_design_review_fails(self):
        (self.repo/'release/verification/release-review.md').unlink()
        with self.assertRaises(ValueError):s.staged_check(self.repo,replay=False)

    def test_stale_live_source_authority_and_receipt_fail(self):
        for name in ('brief.txt','scope.md',s.REVIEW_RECEIPT):
            with self.subTest(name=name):
                file=self.p/name;original=file.read_bytes();file.write_bytes(original+b' ')
                with self.assertRaises(ValueError):s.project_inputs(self.p)
                file.write_bytes(original)

    def test_postseal_commit_cannot_replace_original_seal(self):
        s.git(self.repo,'commit','--allow-empty','-m','Not an admissible amendment')
        with self.assertRaisesRegex(ValueError,'direct source child'):s.check(self.repo,replay=False)

    def test_wrong_source_commit_fails(self):
        seal=s.read(self.repo/'release/seal.json');seal['source_commit']=self.committed['seal_commit']
        put(self.repo/'release/seal.json',seal)
        with self.assertRaisesRegex(ValueError,'repository root'):s.staged_check(self.repo,replay=False)

    def test_symlink_and_traversal_fail(self):
        (self.repo/'linked').symlink_to(self.repo/'inputs/archive-record.json')
        with self.assertRaises(ValueError):s.inventory(self.repo)
        for name in ('../escape','/absolute','a/../b','.git/config'):
            with self.assertRaises(ValueError):s.local(self.repo,name,False)

    def test_no_existing_repository_overwrite(self):
        with self.assertRaisesRegex(ValueError,'existing source repository'):s.prepare(self.p)

    def test_independent_review_exact_result_and_criteria(self):
        with patch.object(s,'owning_check',return_value=self.replay):result=s.check(self.repo)
        review=dict(schema=1,stage='PCB-RELEASE-SEAL',author='Author',reviewer='Reviewer',verdict='PASS',result=result,
                    checks={k:dict(verdict='PASS',rationale='Synthetic mechanism scope checked.') for k in s.CRITERIA})
        md(self.p/'seal-review.md',review)
        with patch.object(s,'check',return_value=result):
            self.assertEqual(s.certificate(self.p,'seal-review.md')['seal_commit'],result['seal_commit'])
            cases=[]
            v=copy.deepcopy(review);v['reviewer']=' author ';cases.append(v)
            v=copy.deepcopy(review);v['result']['seal_commit']='0'*40;cases.append(v)
            v=copy.deepcopy(review);v['checks'].pop('provenance');cases.append(v)
            v=copy.deepcopy(review);v['checks']['handoff']['rationale']=' ';cases.append(v)
            v=copy.deepcopy(review);v['verdict']='FAIL';cases.append(v)
            for case in cases:
                md(self.p/'seal-review.md',case)
                with self.assertRaises(ValueError):s.certificate(self.p,'seal-review.md')

    def test_unique_adopted_graph_stage(self):
        root=Path(self.tmp.name)/'graph';path=root/'skills/pcb-design/workflow/graph.json'
        graph=s.read(s.ROOT/'skills/pcb-design/workflow/graph.json')
        node=next(n for n in graph['stages'] if n['spec']['id']=='PCB-RELEASE-SEAL')
        put(path,{'stages':[node]});s.graph_check(root)
        for nodes in ([],[node,node]):
            put(path,{'stages':nodes})
            with self.assertRaises(ValueError):s.graph_check(root)

    def test_child_bytecode_environment_is_inherited(self):
        work=Path(self.tmp.name)/'child';work.mkdir();put(work/'probe.py','VALUE=1\n')
        s.run([sys.executable,'-c','import subprocess,sys; subprocess.run([sys.executable,"-c","import probe"],check=True)'],cwd=work)
        self.assertFalse((work/'__pycache__').exists())

    def test_executable_mode_rejected_even_if_git_ignores_it(self):
        s.git(self.repo,'config','core.filemode','false')
        (self.repo/'source/project/brief.txt').chmod(0o755)
        self.assertFalse(s.git(self.repo,'status','--porcelain').strip())
        with self.assertRaisesRegex(ValueError,'executable'):s.check(self.repo,replay=False)

    def test_unreadable_directory_fails_closed(self):
        opaque=self.repo/'opaque';put(opaque/'payload','must be counted');opaque.chmod(0)
        try:
            if os.geteuid()==0:
                self.skipTest('root can read mode000; kernel permission regression requires unprivileged runner')
            with self.assertRaises(PermissionError):s.inventory(self.repo)
        finally:opaque.chmod(0o755)

    def test_git_replacements_and_grafts_cannot_hide_postseal_commit(self):
        original=self.committed['seal_commit'];source=self.prepared['source_commit']
        s.git(self.repo,'commit','--allow-empty','-m','Unauthorized successor')
        successor=s.git(self.repo,'rev-parse','HEAD').decode().strip()
        tree=s.git(self.repo,'rev-parse','HEAD^{tree}').decode().strip()
        fake=s.git(self.repo,'commit-tree',tree,'-p',source,'-m','Fake ancestry').decode().strip()
        s.git(self.repo,'replace',successor,fake)
        put(self.repo/'.git/info/grafts',successor+' '+source+'\n')
        self.assertEqual(s.parents(self.repo,successor),[original])
        with self.assertRaisesRegex(ValueError,'direct source child'):s.check(self.repo,replay=False)

    def test_git_blob_replacement_cannot_override_source_objects(self):
        source=self.prepared['source_commit']
        blob=s.git(self.repo,'rev-parse',source+':source/project/brief.txt').decode().strip()
        other=s.git(self.repo,'rev-parse',source+':inputs/authority.md').decode().strip()
        s.git(self.repo,'replace',blob,other)
        self.assertEqual(s.git_tree(self.repo,source)['source/project/brief.txt'],
                         s.sha(self.repo/'source/project/brief.txt'))


if __name__=='__main__':unittest.main()
