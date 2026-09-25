#!/usr/bin/env python3
"""Replay the exact TI B2 POFV source profile on both isolated placement boards."""
from __future__ import annotations
import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path
try:
    import pcbnew as p
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages'); import pcbnew as p

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
P=ROOT/'projects/crow-usb-carrier-v1'
TI=P/'06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
UNION=P/'01_docs/research/2026-09-25-ti-integrated-placement-sol'
GEN=ROOT/'skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py'
CHECK=ROOT/'skills/jlcpcb-fab/scripts/via_process_check.py'
LIB=ROOT/'skills/jlcpcb-fab/scripts/tmux4827_pofv.py'
EXPECTED={
    'baseline':'3c3893e65100d51078e5f915e473585e4f38e3d6d34ef607992dcf6f2fc54cc8',
    'candidate':'20373950748ac51113b115b2d12d169160c24024a2a000572bb70c67b0f60919',
    'source':'0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868',
    'pro':'7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094',
    'dru':'00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a',
    'assembly':'76071a9190ae3923a7a1b4b709a5b3160ce1f06b8d8fb22292ce1cea23664cf3',
    'producer':'b3906f63e07e9f04ada58e757f4095989f6933eca98d93b0f1165e91064529b7',
    'profile_lib':'db5f49000a70af11997b80e246eefd13632a364681bd19835c37477bee16fc18',
    'process_checker':'cea702ce45081e9ff6a1c4409f636fb921941dba92e09d0bfe6f449470cb1054',
}
INPUTS={'baseline':UNION/'baseline.kicad_pcb','candidate':UNION/'candidate.kicad_pcb',
        'source':TI/'03_src/floorplan.yaml','pro':TI/'04_kicad/crow_carrier.kicad_pro',
        'dru':TI/'04_kicad/crow_carrier.kicad_dru','assembly':TI/'03_src/rules/assembly.yaml',
        'producer':GEN,'profile_lib':LIB,'process_checker':CHECK}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def issue_key(v):return(v['type'],v['description'],tuple(sorted(i['uuid'] for i in v['items'])))
def run(command):
    r=subprocess.run(command,capture_output=True,text=True)
    if r.returncode:raise SystemExit(f'{command[0]} failed ({r.returncode}): {r.stdout[-800:]} {r.stderr[-800:]}')
    return r

def main():
    hashes={name:sha(path) for name,path in INPUTS.items()}
    if hashes!=EXPECTED:raise SystemExit(f'profile source/input SHA drift: {hashes}')
    rows={}
    with tempfile.TemporaryDirectory(prefix='crow-iso8-profile-') as d:
        for name in ('baseline','candidate'):
            temp=Path(d)/name;temp.mkdir()
            board=temp/'crow_carrier.kicad_pcb'
            shutil.copy2(INPUTS[name],board)
            for ext in ('.kicad_pro','.kicad_dru'):
                shutil.copy2(TI/'04_kicad'/('crow_carrier'+ext),temp/('crow_carrier'+ext))
            produced=run(['python3',str(GEN),str(board),'--assembly',str(INPUTS['assembly'])])
            if 'eight exact B2 areas and rules emitted' not in produced.stdout:
                raise SystemExit('POFV producer did not emit eight exact areas')
            via_json=temp/'via.json'
            process=run(['python3',str(CHECK),str(board),'--assembly',str(INPUTS['assembly']),
                         '--json',str(via_json)])
            if 'V-PROCESS PASS' not in process.stdout:raise SystemExit('V-PROCESS did not pass')
            via_report=json.loads(via_json.read_text())
            if via_report['fails']:raise SystemExit(f'V-PROCESS failures: {via_report["fails"]}')
            native=p.LoadBoard(str(board))
            areas={z.GetZoneName():[p.ToMM(z.GetBoundingBox().GetLeft()),
                                    p.ToMM(z.GetBoundingBox().GetTop()),
                                    p.ToMM(z.GetBoundingBox().GetRight()),
                                    p.ToMM(z.GetBoundingBox().GetBottom())]
                   for z in native.Zones() if z.GetIsRuleArea() and
                   z.GetZoneName().startswith('tmux4827_b2_pofv_')}
            zones=sorted(areas)
            wanted=[f'tmux4827_b2_pofv_U_ISO{i}' for i in range(1,9)]
            if zones!=wanted:raise SystemExit(f'POFV rule area identity drift: {zones}')
            fp=next(f for f in native.GetFootprints() if f.GetReference()=='U_ISO8')
            pad=next(q for q in fp.Pads() if q.GetNumber()=='5')
            vias=[v for v in native.GetTracks() if isinstance(v,p.PCB_VIA) and
                  v.GetPosition()==pad.GetPosition() and v.GetNetname()=='GND']
            if len(vias)!=1:raise SystemExit('U_ISO8.5 centred GND via absent')
            via=vias[0]
            if p.ToMM(via.GetWidth(p.F_Cu))!=.35 or p.ToMM(via.GetDrill())!=.20:
                raise SystemExit('U_ISO8 via geometry drift')
            drc_path=temp/'drc.json'
            drc_cmd=subprocess.run(['kicad-cli','pcb','drc','--format','json','--output',str(drc_path),str(board)],
                                   capture_output=True,text=True)
            if not drc_path.exists():raise SystemExit(f'KiCad DRC report absent: {drc_cmd.stderr[-500:]}')
            drc=json.loads(drc_path.read_text())
            iso=[v for v in drc['violations'] if any('U_ISO8' in i['description'] for i in v['items'])
                 and v['type'] in ('clearance','hole_clearance')]
            if iso:raise SystemExit(f'U_ISO8 native via clearance remains: {iso}')
            rows[name]={'augmented_dru_sha256':sha(temp/'crow_carrier.kicad_dru'),
                        'project_sha256':sha(temp/'crow_carrier.kicad_pro'),
                        'rule_areas':zones,'rule_area_bounds_mm':areas,
                        'u_iso8_5_via_mm':[p.ToMM(via.GetPosition().x),
                                                              p.ToMM(via.GetPosition().y)],
                        'u_iso8_via_diameter_mm':.35,'u_iso8_via_drill_mm':.20,
                        'via_process_census':via_report['census'],
                        'drc':{'violations':len(drc['violations']),'unconnected':len(drc['unconnected_items']),
                               'u_iso8_clearance_issues':iso},
                        'issue_keys':sorted(issue_key(v) for v in drc['violations'])}
    old=set(tuple((a,b,tuple(c))) for a,b,c in rows['baseline']['issue_keys'])
    new=set(tuple((a,b,tuple(c))) for a,b,c in rows['candidate']['issue_keys'])
    if old!=new or len(old)!=213 or rows['baseline']['drc']['unconnected']!=499 or rows['candidate']['drc']['unconnected']!=499:
        raise SystemExit(f'full-profile DRC delta drift: {len(old)}, {len(new)}, +{len(new-old)}, -{len(old-new)}')
    for row in rows.values():del row['issue_keys']
    receipt={'schema':1,'status':'FULL_PROFILE_DRC_DELTA_CLEAN_RESEARCH_ONLY',
             'input_sha256':hashes,'boards':rows,
             'issue_identity_delta':{'added':0,'removed':0},
             'authority':'Exact conditional TMUX4827_YBH_B2_POFV profile generates eight pad-bound rule areas and 0.10-mm via-to-adjacent-pad clearance; V-PROCESS validates Type-VII 0.35/0.20 sites.',
             'bare_board_harness_defect':'Generic board generation and kicad-cli DRC without TI .kicad_pro/.kicad_dru and POFV producer reported the allowed 0.10-mm ISO8 via gap against the 0.20-mm default rule.',
             'augmented_board_hash_policy':'No augmented board byte SHA is claimed: pcbnew creates fresh UUIDs for the eight newly emitted rule areas on each replay. Input board bytes and semantic area names/bounds are pinned instead.',
             'offpad_via_repair':'Rejected without edit: profile audit requires exactly one 0.35/0.20 GND via centred on each U_ISO*.5 within 0.0015 mm; an off-pad via plus neck violates this source-governed profile and adds unproved return geometry.',
             'qualification':['Conditional POFV vendor/CAM/PCBA acceptance is still owed',
                              'ADC8 cap owner pinch, 28 reference labels, unfilled return and 499 opens remain',
                              'No P1/P2 or route/return credit from this DRC comparison']}
    (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'drc':[rows[n]['drc'] for n in ('baseline','candidate')],
                      'issue_delta':receipt['issue_identity_delta']},sort_keys=True))

if __name__=='__main__':main()
