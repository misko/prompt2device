from pathlib import Path
import shutil
import tempfile
import unittest

import verify_public as v


class PublicIntegrityTests(unittest.TestCase):
    def test_reviewed_payload(self):
        result = v.verify(v.HERE.parent / 'quote-draft/r6-2c8p-substitutions')
        self.assertEqual(result['files'], 94)
        self.assertFalse(result['full_engineering_replay_performed'])
        self.assertFalse(result['production_ready'])

    def test_tamper_missing_and_extra_are_rejected(self):
        source = v.HERE.parent / 'quote-draft/r6-2c8p-substitutions'
        with tempfile.TemporaryDirectory(prefix='crow-public-test-') as tmp:
            target = Path(tmp) / 'r6'
            shutil.copytree(source, target)
            bom = target / 'carrier-bom.csv'
            old = bom.read_bytes()
            bom.write_bytes(old.replace(b'PCM1864DBTR', b'WRONGPART'))
            with self.assertRaisesRegex(ValueError, 'Changed payload'):
                v.verify(target)
            bom.write_bytes(old)
            bom.rename(target / 'extra.csv')
            with self.assertRaisesRegex(ValueError, 'Extra or missing'):
                v.verify(target)
            (target / 'extra.csv').rename(bom)
            (target / 'unexpected.txt').write_text('not reviewed')
            with self.assertRaisesRegex(ValueError, 'Extra or missing'):
                v.verify(target)


if __name__ == '__main__':
    unittest.main()
