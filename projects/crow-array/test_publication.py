# SPDX-License-Identifier: MIT
"""Real public-subset negative controls; no CAD or original archive required."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import publication as p


class PublicPackage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='crow-public-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'package'
        shutil.copytree(p.DEFAULT, self.root)

    def manifest(self):
        return p.load(self.root, 'publication.json')

    def save(self, m):
        p.write_json(self.root/'publication.json', m)

    def rehash(self, name):
        m=self.manifest()
        m['files'][name]['sha256']=p.digest(self.root/name)
        self.save(m)

    def test_valid_relocated_package(self):
        result=p.verify(self.root)
        self.assertEqual(result['boards'], ['carrier','pod'])
        self.assertEqual(result['order'], 'DO-NOT-ORDER')

    def test_missing_board(self):
        (self.root/self.manifest()['native']['pod']['pcb']).unlink()
        with self.assertRaisesRegex(ValueError,'missing'): p.verify(self.root)

    def test_extra_unlisted_vendor_asset(self):
        (self.root/'vendor.pdf').write_bytes(b'not authorized')
        with self.assertRaisesRegex(ValueError,'extra'): p.verify(self.root)

    def test_extra_listed_vendor_asset(self):
        path=self.root/'vendor.pdf';path.write_bytes(b'not authorized')
        m=self.manifest();m['files']['vendor.pdf']=dict(origin=None,sha256=p.digest(path),license='MIT')
        self.save(m)
        with self.assertRaisesRegex(ValueError,'selection'): p.verify(self.root)

    def test_rehashed_native_mutation(self):
        name=self.manifest()['native']['carrier']['pcb']
        with (self.root/name).open('a') as f:f.write('\n; changed native\n')
        self.rehash(name)
        with self.assertRaisesRegex(ValueError,'origin binding'): p.verify(self.root)

    def test_rehashed_gerber_mutation(self):
        name='fab/carrier/plots/carrier-F_Cu.gbr'
        with (self.root/name).open('a') as f:f.write('\nchanged copper\n')
        self.rehash(name)
        with self.assertRaisesRegex(ValueError,'origin binding'): p.verify(self.root)

    def test_rehashed_boundary_and_license_forgery(self):
        for name in ('README.md','KiCad-LICENSE.md','LICENSE','THIRD-PARTY-NOTICES.md',
                     'EXTERNAL-DEPENDENCIES.json'):
            with self.subTest(name=name):
                path=self.root/name;old=path.read_bytes()
                path.write_text('Complete sealed replay, ready to order, exclusively MIT.\n')
                self.rehash(name)
                with self.assertRaisesRegex(ValueError,'policy mismatch'): p.verify(self.root)
                path.write_bytes(old);self.rehash(name)

    def test_wrong_quantities(self):
        m=self.manifest();m['boards']['pod']['quantity']=40;self.save(m)
        with self.assertRaisesRegex(ValueError,'scope'): p.verify(self.root)

    def test_order_ready_claim(self):
        m=self.manifest();m['order_verdict']='READY';self.save(m)
        with self.assertRaisesRegex(ValueError,'scope'): p.verify(self.root)

    def test_wrong_native_role(self):
        m=self.manifest();m['native']['pod']['pcb']=m['native']['carrier']['pcb'];self.save(m)
        with self.assertRaisesRegex(ValueError,'native role'): p.verify(self.root)

    def test_rehashed_seal_and_status(self):
        for name in ('evidence/seal.json','evidence/CURRENT-STATUS.json',
                     'evidence/sealed-release-receipt.json'):
            with self.subTest(name=name):
                path=self.root/name;old=path.read_bytes()
                path.write_text('{}');self.rehash(name)
                with self.assertRaises(ValueError): p.verify(self.root)
                path.write_bytes(old);self.rehash(name)

    def test_symlink_even_to_identical_bytes(self):
        path=self.root/'LICENSE';path.unlink();path.symlink_to(p.DEFAULT/'LICENSE')
        with self.assertRaisesRegex(ValueError,'symlink'): p.verify(self.root)

    def test_missing_native_library(self):
        next((self.root/'native').rglob('*.kicad_mod')).unlink()
        with self.assertRaisesRegex(ValueError,'missing'): p.verify(self.root)

    def test_library_relicensed_in_manifest(self):
        m=self.manifest()
        name=next(n for n in m['files'] if '/libraries/' in n)
        m['files'][name]['license']='MIT';self.save(m)
        with self.assertRaisesRegex(ValueError,'license changed'): p.verify(self.root)

    def test_generated_license_metadata_tamper(self):
        m=self.manifest();m['files']['KiCad-LICENSE.md']['license']='MIT';self.save(m)
        with self.assertRaisesRegex(ValueError,'license changed'): p.verify(self.root)


if __name__=='__main__':
    unittest.main()
