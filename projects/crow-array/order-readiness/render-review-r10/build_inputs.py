"""Reuse documented local connector models; preserve the independent edge intent."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'render-review-20261101'
for board in ('carrier', 'pod'):
    out = ROOT / f'{board}-inspection.json'
    if out.exists():
        raise ValueError('Refusing existing input')
    data = json.loads((BASE / f'{board}-inspection.json').read_text())
    data['label'] = f'Crow r10 {board} | native X right / Y down'
    if board == 'carrier':
        data['connectors']['J1']['limitations'] = (
            'Nominal bounding housing and mouth axis; roof, cavity and terminal profiles illustrative. '
            'Existing enlarged round holes differ from maker slots. Native 180-degree pose now '
            'transforms documented local +Y mouth outward to board -Y. '
            'Actual affected access/clearance evidence is in power-jack-r10-review, not these solids.')
    out.write_text(json.dumps(data, indent=2) + '\n')
