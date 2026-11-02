"""Verify retained diagnostic bytes and their native subjects; not acceptance."""
import hashlib
import json
from pathlib import Path


def verify(folder=None):
    base = Path(folder) if folder else Path(__file__).resolve().parent
    root = base.parents[3]
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = json.loads((base/'manifest.json').read_text())
    if not manifest:
        raise ValueError('Empty evidence manifest')
    for relative, expected in manifest.items():
        path = (base/relative).resolve()
        if not path.is_relative_to(base.resolve()) or digest(path) != expected:
            raise ValueError('Evidence mismatch: '+relative)
    evidence = json.loads((base/'evidence.json').read_text())
    for name, board in evidence['boards'].items():
        if digest(root/board['source']) != board['sha256']:
            raise ValueError('Native source changed: '+name)
        if digest(base/f'{name}-catalog-diagnostic.kicad_pcb') != board['diagnostic_board_sha256']:
            raise ValueError('Diagnostic board changed: '+name)
    for relative, expected in evidence['catalog_hashes'].items():
        if digest(base/relative) != expected:
            raise ValueError('Catalog changed: '+relative)
    for filename in ('jlc-browser-assessment.json','jlc-focused-assessment.json',
                     'jlc-browser-run.json','jlc-focused-browser-run.json',
                     'sources/rjhsex080.pdf'):
        if filename not in manifest:
            raise ValueError('Missing evidence binding: '+filename)
    return {'result':'PASS_DIAGNOSTIC_INTEGRITY_ONLY','files':len(manifest),
            'native_boards':len(evidence['boards']),'jlc_alignment_verified':False,
            'production_ready':False}


if __name__ == '__main__':
    print(json.dumps(verify(),indent=2))
