#!/usr/bin/env python3
"""One full-profile verification of the bounded robust-contact geometry candidate."""
from pathlib import Path
import importlib.util,json,sys
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
HERE=Path(__file__).resolve().parent
INPUT=HERE.parent/'2026-09-25-ti-tps26625-input-loop-sol/loop_probe.py'
spec=importlib.util.spec_from_file_location('pinned_input_loop_probe',INPUT)
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
PROFILE_SHA='7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094'
if probe.sha(probe.base.PROFILE/'crow_carrier.kicad_pro')!=PROFILE_SHA:
    raise RuntimeError('archived native profile SHA drift')
probe.HERE=HERE
probe.SUPPLY_START=(188.35,46.025)
probe.SUPPLY_END=(188.35,44.0)
probe.main()
receipt=json.loads((HERE/'receipt.json').read_text())
board=HERE/'candidate_filled_profile.kicad_pcb'
if receipt['native_profile']['added_issue_identities'] or receipt['native_profile']['removed_issue_identities']:
    raise RuntimeError('full-profile issue-set delta')
native=p.LoadBoard(str(board))
land=probe.base.pad(native,'U_SPOKE8','1')
track=next(t for t in native.GetTracks() if t.GetNetname()=='N12V_PROTECTED' and
           t.GetLayer()==p.F_Cu and abs(probe.base.mm(t.GetWidth())-1.2)<1e-6)
if not track.GetEffectiveShape(p.F_Cu).Collide(land.GetPosition(),0):
    raise RuntimeError('U.1 native land center not contained by supply copper')
cap=probe.base.pad(native,'C_SPOKE_IN8','1')
direct_gap=probe.trial.copper_gap(land,cap)
if direct_gap>2.5:raise RuntimeError(f'IN/CIN project copper gap {direct_gap}>2.5')
receipt['native_u1_center_contained']=True
receipt['native_u1_to_cin1_direct_pad_copper_gap_mm']=direct_gap
board.unlink()
(HERE/'native_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
(HERE/'receipt.json').unlink()
print('full-profile native candidate PASS; transient board removed')
