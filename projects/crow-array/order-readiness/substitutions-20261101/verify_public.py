"""Verify the reviewed r6 quote payload without KiCad or private research files.

Integrity only: not stock verification, fresh CAD replay or production approval.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_MANIFEST = 'c01cb5e90b31738b6afd0102aca1b22ae3322c1e82f17fbe5492c8f198f19099'
EXTERNAL = {'substitutions-20261101/evidence/pcm1864.pdf',
            'substitutions-20261101/evidence/capacitor-primary-research.tar.gz'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(package):
    require(digest(package / 'manifest.json') == EXPECTED_MANIFEST, 'Unreviewed manifest')
    manifest = json.loads((package / 'manifest.json').read_text())
    actual = {str(p.relative_to(package)) for p in package.rglob('*') if p.is_file()}
    require(actual == set(manifest['files']) | {'manifest.json'}, 'Extra or missing payload files')
    for name, expected in manifest['files'].items():
        path = package / name
        require(path.resolve().is_relative_to(package.resolve()), 'Escaping payload path')
        require(digest(path) == expected, 'Changed payload: ' + name)
    spec = HERE / 'adopted-changes.json'
    require(digest(spec) == manifest['spec_sha256'], 'Changed adopted map')
    require(digest(HERE.parent / 'substitute_quote.py') == manifest['tool_sha256'], 'Changed generator')
    skipped = []
    for name, expected in json.loads(spec.read_text())['evidence'].items():
        path = HERE.parent / name
        require(path.resolve().is_relative_to(HERE.parent.resolve()), 'Escaping evidence path')
        if name in EXTERNAL and not path.exists():
            skipped.append(name)
            continue
        require(digest(path) == expected, 'Missing or changed evidence: ' + name)
    return {'result': 'QUOTE_PAYLOAD_INTEGRITY_PASS', 'files': len(actual),
            'assembled': manifest['assembled'], 'fabricated': manifest['fabricated'],
            'external_research_not_bundled': skipped,
            'full_engineering_replay_performed': False, 'production_ready': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path,
                        default=HERE.parent / 'quote-draft/r6-2c8p-substitutions')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.package), indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, 'FAIL: ' + str(exc) + '\n')
