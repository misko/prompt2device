"""Check unchanged Crow clamp topology and conditional substitution arithmetic."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import pcbnew

HERE = Path(__file__).resolve().parent
ORDER = HERE.parent
ROOT = ORDER.parents[2]
BASE = ORDER/'quote-draft/r10-2c8p-outward-power'
SOURCE = HERE/'source-evidence'
HASHES = {
    'BRIEF-historical.md':'2fd110154d1234840a285f95d1b87f92219a32dbe1b8bcd7dc4ae18386c86699',
    'ROOF-INTERFACE.md':'f2dcad8c938e0e821ae41b691323df86471751a467dc023f018ac8575c95f0ed',
    'roof_model.py':'00a8fa68bec9aac577e75cd541c3803657ef287a99087ccf4980006f5a65ab37',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def nets(fp):
    return {p.GetNumber():p.GetNetname() for p in fp.Pads()}


def check_pod(board):
    for ref, output in [('D2','/AMP_P'),('D3','/AMP_M')]:
        fp=board.FindFootprintByReference(ref)
        need(nets(fp)=={'1':'/GND','2':'/3V3','3':output}, 'clamp pin mapping '+ref)
        need(fp.GetValue()=='BAT54S-7-F', 'baseline changed '+ref)
        need(fp.GetFPID().GetLibItemName()=='SOT-23', 'footprint '+ref)
        for p in fp.Pads():
            expected={'1':(-.9375,-.95),'2':(-.9375,.95),'3':(.9375,0)}[p.GetNumber()]
            actual=p.GetFPRelativePosition()
            need(math.dist(expected,(actual.x/1e6,actual.y/1e6))<1e-6,'land centre')
            need(math.dist((1.475,.6),(p.GetSize().x/1e6,p.GetSize().y/1e6))<1e-6,'land size')
    for ref, expected in [('R9',{'1':'/AMP_P','2':'/AUDIO_P'}),
                          ('R10',{'1':'/AMP_M','2':'/AUDIO_M'}),
                          ('R14',{'1':'/3V3','2':'/GND'})]:
        fp=board.FindFootprintByReference(ref)
        need(nets(fp)==expected, 'resistor topology '+ref)
        need(fp.GetValue().startswith('330R 1%' if ref=='R14' else '1k 1%'), 'resistor value '+ref)


def arithmetic(rc=2700, rp=1000, sink=330):
    branch=10.36/(rc*.99)+20e-6
    rail=2*branch*sink*1.01
    # Extra conservative instantaneous screen for the pod 1k branch under the
    # SAME bounded source/history states; not a new IEC/miswire guarantee.
    pod_branch=10.36/(rp*.99)+20e-6
    need(rail<3.6, 'off-rail limit')
    need(pod_branch<.02,'candidate current screen')
    return dict(carrier_history_branch_A=branch, off_rail_V=rail,
        conditional_pod_branch_A=pod_branch,
        diode_power_W_at_allocated_0_6V=pod_branch*.6,
        reference_delta_C_at_500K_W=pod_branch*.6*500,
        operating_air_C=[-20,60], candidate_ambient_C=[-55,150])


def run():
    manifest=ROOT/'projects/crow-array/releases/crow-prototype-v3-first-run-5c10p-public-v1/evidence/archive-manifest.json'
    archived=manifest.read_text()
    for name,digest in HASHES.items():
        need(hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()==digest,'source hash '+name)
        need(digest in archived,'source not present in historical manifest '+name)
    spec=importlib.util.spec_from_file_location('retained_roof_model',SOURCE/'roof_model.py')
    model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    inherited=model.bounds();model.invariant_check()
    result=arithmetic()
    need(abs(result['off_rail_V']-inherited['off_rail_V'])<1e-12,'model reproduction')
    pod=pcbnew.LoadBoard(str(BASE/'native/pcb/pod/pod.kicad_pcb'));check_pod(pod)
    carrier=pcbnew.LoadBoard(str(BASE/'native/pcb/carrier/carrier.kicad_pcb'))
    for port in range(1,9):
        for offset,sign in [(0,'P'),(1,'M')]:
            fp=carrier.FindFootprintByReference('R'+str(100+port*2+offset))
            adc=(port-1)//4+1;ch=(port-1)%4+1
            need(fp.GetValue()=='2.7k 1%', 'carrier resistor value')
            need(nets(fp)=={'1':f'/P{port}_C{sign}','2':f'/ADC{adc}_CH{ch}_{sign}'},'carrier resistor net')
    return dict(status='CONDITIONAL_ENGINEERING_SCREEN_ONLY', production_ready=False,
        candidate='Nexperia BAT54S,215 / C47546', calculations=result,
        limitations=['No all-temperature clamp-voltage guarantee',
                    'No live vendor placement or immediate PCBA inventory verification',
                    'No independent substitution acceptance; no BOM/CAD changes'],
        sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in [manifest,HERE/'check.py',*(SOURCE/n for n in HASHES),
                           BASE/'native/pcb/pod/pod.kicad_pcb',BASE/'native/pcb/carrier/carrier.kicad_pcb']})


if __name__=='__main__':
    data=json.dumps(run(),indent=2,sort_keys=True)+'\n'
    if len(sys.argv)>1:
        path=Path(sys.argv[1])
        if path.exists():need(path.read_text()==data,'existing evidence differs')
        else:path.write_text(data)
    print(data)
