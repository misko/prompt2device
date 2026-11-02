"""Package only an independently reviewed outward power-jack repair; no vendor actions."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
import zipfile
import r9_quote as base

r = base.r
q = base.q
ROOT = base.ROOT
BASE = base.OUT
OUT = ROOT / 'quote-draft/r10-2c8p-outward-power'
REVIEW = ROOT / 'power-jack-r10-review/review.json'
BOARD = 'native/pcb/carrier/carrier.kicad_pcb'
CHANGED = {BOARD, 'carrier-cpl.csv', 'carrier-gerbers.zip', 'README.md',
           'tht-placement-verification.csv', 'checks/drc.json', 'checks/erc.json', 'checks/netlist.xml'}


def reviewed():
    review = json.loads(REVIEW.read_text())
    q.need(review['decision'] == 'PASS_FOR_PROTOTYPE_QUOTE', 'Independent review not passed')
    for name, digest in review['subjects'].items():
        q.need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Nonportable review subject')
        q.need(q.sha(ROOT / name) == digest, 'Changed review subject: ' + name)
    q.need(not Path(review['board']).is_absolute() and '..' not in Path(review['board']).parts, 'Nonportable board path')
    board = ROOT / review['board']
    q.need(q.sha(board) == review['board_sha256'], 'Changed reviewed board')
    return review, board


def tables():
    cpl = q.read_csv(BASE / 'carrier-cpl.csv')
    jack = [row for row in cpl if row['Designator'] == 'J1']
    q.need(len(jack) == 1, 'Expected single power jack')
    jack[0]['Rotation'] = '180.000000'
    jack[0]['Mid Y'] = '-8.200000mm'
    tht = q.read_csv(BASE / 'tht-placement-verification.csv')
    jack = [row for row in tht if row['board'] == 'carrier' and row['reference'] == 'J1']
    q.need(len(jack) == 1, 'Expected single verification row')
    jack[0].update(anchor_y='14.7', body_center_y='8.2', cpl_y='-8.2', rotation='180',
                   orientation='Mouth toward native -Y / CPL +Y; pin 3 to left; native angle, verify JLC registration')
    return {'carrier-cpl.csv': cpl, 'tht-placement-verification.csv': tht}


def fabrication(board, folder):
    r.command('kicad-cli', 'pcb', 'export', 'gerbers', '--no-protel-ext', '--layers',
              r.LAYERS, '-o', str(folder) + '/', board)
    r.command('kicad-cli', 'pcb', 'export', 'drill', '--excellon-separate-th',
              '--drill-origin', 'absolute', '-o', str(folder) + '/', board)
    files = sorted(p for p in folder.iterdir() if p.suffix in ('.gbr', '.drl'))
    q.need(len(files) == 13, 'Expected eleven Gerbers plus two drill files')
    return files


def normalize_fabrication(data):
    # Ignore ONLY exporter timestamp comments, never geometry or aperture data.
    prefixes = ('%TF.CreationDate,', '; #@! TF.CreationDate,',
                'G04 Created by KiCad ', '; DRILL file KiCad ')
    return '\n'.join(line for line in data.decode().splitlines() if not line.startswith(prefixes))


def build(output):
    base.verify(BASE)
    review, board = reviewed()
    q.need(not output.exists(), 'Refusing existing output')
    shutil.copytree(BASE, output)
    shutil.copyfile(board, output / BOARD)
    for name, rows in tables().items():
        (output / name).write_bytes(q.csv_bytes(rows))
    shutil.copyfile(BASE / 'README.md', output / 'engineering/R9-HISTORICAL-INSTRUCTIONS.md')
    shutil.copyfile(ROOT / 'R10-INSTRUCTIONS.md', output / 'README.md')
    evidence = output / 'engineering/power-jack-r10'
    evidence.mkdir()
    shutil.copyfile(REVIEW, evidence / 'review.json')
    for name in review['subjects']:
        dest = evidence / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    previews = output / 'previews'
    previews.mkdir()
    for label, folder, native in [('carrier', 'carrier-final-v2', board),
                                  ('pod', 'pod', BASE / 'native/pcb/pod/pod.kicad_pcb')]:
        source = ROOT / 'render-review-r10' / folder
        report = json.loads((source / 'report.json').read_text())
        q.need(report['source_sha256'] == q.sha(native), 'Render is not current: ' + label)
        for name in ('upper_045.png', 'overview.png', 'report.json'):
            shutil.copyfile(source / name, previews / (label + '-' + name))
    shutil.copyfile(ROOT / 'render-review-r10/carrier-final-v2/detail-J1-upper_045.png',
                    previews / 'carrier-power-jack-45.png')
    checks = r.preflight(output, output / 'checks')
    with tempfile.TemporaryDirectory(prefix='crow-r10-gerbers-') as tmp:
        folder = Path(tmp)
        files = fabrication(output / BOARD, folder)
        with zipfile.ZipFile(output / 'carrier-gerbers.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for file in files:
                info = zipfile.ZipInfo(file.name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, file.read_bytes())
    totals = base.population(output)
    prior = json.loads((BASE / 'manifest.json').read_text())
    manifest = dict(status='REVIEWED_AFFECTED_REPAIR_QUOTE_ONLY',
        production_ready=False, purchase_authorized=False, submitted=False,
        stage_acceptance_issued=False, inherited_release_acceptance=False,
        fabricated={'carrier': 5, 'pod': 10}, assembled={'carrier': 2, 'pod': 8},
        installed={**totals, 'total': sum(totals.values())}, checks=checks,
        board_sha256=review['board_sha256'], source_review_sha256=q.sha(REVIEW),
        base_manifest_sha256=q.sha(BASE / 'manifest.json'), tool_sha256=q.sha(Path(__file__)),
        protected={k: v for k, v in prior['files'].items() if k not in CHANGED})
    manifest['files'] = {str(p.relative_to(output)): q.sha(p) for p in output.rglob('*')
                         if p.is_file() and p != output / 'manifest.json'}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return verify(output)


def verify(output):
    base.verify(BASE)
    review, board = reviewed()
    m = json.loads((output / 'manifest.json').read_text())
    q.need(m['tool_sha256'] == q.sha(Path(__file__)), 'Changed producer')
    q.need(m['source_review_sha256'] == q.sha(REVIEW), 'Changed independent review')
    q.need(m['base_manifest_sha256'] == q.sha(BASE / 'manifest.json'), 'Changed base')
    actual = {str(p.relative_to(output)): q.sha(p) for p in output.rglob('*')
              if p.is_file() and p != output / 'manifest.json'}
    q.need(m['files'] == actual, 'Changed/missing/extra payload')
    prior = json.loads((BASE / 'manifest.json').read_text())
    protected = {k: v for k, v in prior['files'].items() if k not in CHANGED}
    q.need(m['protected'] == protected, 'Wrong preservation policy')
    for name, digest in protected.items():
        q.need(q.sha(output / name) == digest, 'Changed protected file: ' + name)
    q.need(q.sha(output / BOARD) == q.sha(board) == m['board_sha256'], 'Wrong native board')
    for name, rows in tables().items():
        q.need((output / name).read_bytes() == q.csv_bytes(rows), 'Wrong derived table: ' + name)
    q.need((output / 'README.md').read_bytes() == (ROOT / 'R10-INSTRUCTIONS.md').read_bytes(), 'Changed instructions')
    totals = base.population(output)
    q.need(m['installed'] == {**totals, 'total': 524}, 'Wrong installed counts')
    q.need(m['fabricated'] == {'carrier': 5, 'pod': 10} and m['assembled'] == {'carrier': 2, 'pod': 8}, 'Wrong quantities')
    q.need(all(m[k] is False for k in ('production_ready', 'purchase_authorized', 'submitted',
               'stage_acceptance_issued', 'inherited_release_acceptance')), 'Invalid authority claim')
    with tempfile.TemporaryDirectory(prefix='crow-r10-verify-') as tmp:
        q.need(m['checks'] == r.preflight(output, Path(tmp)), 'Native checks changed')
        fresh = fabrication(output / BOARD, Path(tmp))
        with zipfile.ZipFile(output / 'carrier-gerbers.zip') as archive:
            q.need(set(archive.namelist()) == {p.name for p in fresh}, 'Wrong fabrication members')
            for file in fresh:
                q.need(normalize_fabrication(file.read_bytes()) == normalize_fabrication(archive.read(file.name)),
                       'Fabrication does not reproduce native: ' + file.name)
    return dict(result='PASS', files=len(actual), protected_r9_files=len(protected),
                installed=m['installed'], production_ready=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify'])
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    print(json.dumps((build if args.action == 'build' else verify)(args.output), indent=2))
