"""Render retained inventory evidence without promoting it to PCBA allocation."""
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = HERE.parent


def build():
    plan = ORDER/'quote-draft/r10-2c8p-outward-power/procurement-plan.csv'
    evidence = ORDER/'JLC-REFRESH-20261103.json'
    recovery = ORDER/'BAT54S-ORIGINAL-RECOVERY-20261103.json'
    rows = list(csv.DictReader(plan.open()))
    observed = json.loads(evidence.read_text())['results']
    assert len(rows) == len(observed) == 38
    text = ['# Crow inventory observations on 3 November 2026', '',
        'Scope: two assembled carriers and eight assembled pods, including agreed home installations. '
        'Five carriers and ten pods are fabricated. Quantities below are installed need, not attrition.', '',
        'Public InStock badges are not confirmed immediate PCBA stock. Numeric overseas/presale '
        'pools are kept separate and never added. The BAT54S recovery and signed-in diagnostic '
        'shortage take precedence over the failed initial public request. Manufacturer spelling '
        'flags remain in the raw evidence for identity reconciliation.', '',
        '| Exact MPN | Code | Need | Installation | Public observation | Overseas pool | Presale pool |',
        '| --- | --- | ---: | --- | --- | ---: | ---: |']
    for row, obs in zip(rows, observed):
        assert row['mpn'] == obs['mpn'] and int(row['installed_2c8p']) == obs['needed']
        assert int(row['per_carrier'])*2+int(row['per_pod'])*8 == obs['needed']
        if row['mpn'] == 'BAT54S-7-F':
            obs = json.loads(recovery.read_text())['results'][0]
            state = 'SHORT in signed-in draft: 4 available / 21 gross required'
        else:
            state = {'IN_STOCK_QTY_UNKNOWN':'InStock badge; immediate quantity unknown',
                     'IDENTITY_MISMATCH':'Identity spelling unresolved',
                     'NOT_FOUND':'Not located; not proof of zero stock'}.get(obs['status'], obs['status'])
        pub = obs.get('jlcpcb', {})
        num = lambda k: str(pub[k]) if pub.get(k) is not None else 'unknown'
        text.append(f"| {row['mpn']} | {row['catalog_locator'] or '—'} | {row['installed_2c8p']} | "
                    f"{row['owner']} | {state} | {num('overseas_stock')} | {num('presale')} |")
    text += ['', 'The hyphenated Panasonic ERJ-3EKF68R0V / C403329 spelling mismatch is inherited '
             'from the catalog, not evidence that a resistor replacement is needed. Home parts '
             'without an exact JLC result retain their existing external sourcing route pending '
             'a deliberate decision; no assembly ownership was changed.', '',
             '## Source integrity', '']
    sources = [plan, evidence, recovery, HERE/'summarize.py']
    sources += sorted(ORDER.glob('BAT54S-*-STOCK-20261103.json'))
    sources += sorted((HERE/'sources').glob('*'))
    for path in sources:
        text.append(f"- `{path.relative_to(ORDER)}`: `{hashlib.sha256(path.read_bytes()).hexdigest()}`")
    return '\n'.join(text)+'\n'


if __name__ == '__main__':
    target = HERE/'INVENTORY.md'
    output = build()
    if target.exists():
        assert target.read_text() == output, 'Existing summary differs; do not overwrite evidence'
    else:
        target.write_text(output)
    print('PASS: 38 identities and 2-carrier/8-pod quantity arithmetic; no sourcing acceptance claimed')
