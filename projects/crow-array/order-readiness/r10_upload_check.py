"""Portable upload integrity/identity check. Does NOT rerun KiCad or issue acceptance."""
import json
from pathlib import Path
import r10_quote as r


def expand_bom(path):
    result = {}
    for row in r.q.read_csv(path):
        refs = [ref.strip() for ref in row['Designator'].split(',')]
        r.q.need(len(refs) == int(row['Quantity']), 'BOM row quantity mismatch')
        for ref in refs:
            r.q.need(ref not in result, 'Duplicate BOM reference')
            # Comment strings in the previously reviewed grouped upload differ;
            # exact manufacturer/MPN/package/catalog/installation identities do not.
            result[ref] = {k: v for k, v in row.items()
                           if k not in ('Designator', 'Quantity', 'Comment')}
    return result


def main():
    r.base.verify(r.BASE)
    review, board = r.reviewed()
    out = r.OUT
    m = json.loads((out / 'manifest.json').read_text())
    files = {str(p.relative_to(out)): r.q.sha(p) for p in out.rglob('*')
             if p.is_file() and p != out / 'manifest.json'}
    r.q.need(files == m['files'], 'Missing/changed/extra r10 payload')
    r.q.need(m['tool_sha256'] == r.q.sha(Path(r.__file__)), 'Changed r10 producer')
    r.q.need(m['source_review_sha256'] == r.q.sha(r.REVIEW), 'Changed review')
    r.q.need(m['base_manifest_sha256'] == r.q.sha(r.BASE / 'manifest.json'), 'Changed r9 manifest')
    prior = json.loads((r.BASE / 'manifest.json').read_text())
    protected = {k: v for k, v in prior['files'].items() if k not in r.CHANGED}
    r.q.need(m['protected'] == protected, 'Wrong preservation policy')
    for name, digest in protected.items():
        r.q.need(r.q.sha(out / name) == digest, 'Changed protected file: ' + name)
    r.q.need(r.q.sha(out / r.BOARD) == r.q.sha(board) == m['board_sha256'], 'Wrong native carrier')
    for name, rows in r.tables().items():
        r.q.need((out / name).read_bytes() == r.q.csv_bytes(rows), 'Wrong derived table: ' + name)
    r.q.need((out / 'README.md').read_bytes() == (r.ROOT / 'R10-INSTRUCTIONS.md').read_bytes(), 'Wrong instructions')
    counts = r.base.population(out)
    r.q.need(m['installed'] == {**counts, 'total': 524}, 'Wrong counts')
    r.q.need(m['fabricated'] == {'carrier': 5, 'pod': 10} and m['assembled'] == {'carrier': 2, 'pod': 8}, 'Wrong quantities')
    r.q.need(all(m[k] is False for k in ('production_ready', 'purchase_authorized', 'submitted',
                                       'stage_acceptance_issued', 'inherited_release_acceptance')), 'Invalid authority claim')
    grouped = {}
    for label in ('carrier', 'pod'):
        alternative = r.ROOT / f'quote-draft/r9-merged-bom-candidates/{label}-bom-merged-v2.csv'
        expected = expand_bom(out / f'{label}-bom.csv')
        r.q.need(expand_bom(alternative) == expected, 'Grouped BOM identity mismatch')
        grouped[label] = dict(references=len(expected), sha256=r.q.sha(alternative))
    print(json.dumps(dict(result='PASS_UPLOAD_INTEGRITY_ONLY', files=len(files),
        preserved_r9_files=len(protected), grouped_boms=grouped, installed=m['installed'],
        native_checks_rerun=False, production_ready=False), indent=2))


if __name__ == '__main__':
    main()
