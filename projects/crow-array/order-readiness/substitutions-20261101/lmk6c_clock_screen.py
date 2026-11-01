"""Pre-layout TI source sensitivity on retained r7 geometry, NOT acceptance.

OPENBLAS_NUM_THREADS=1 uv run --no-project --with numpy==2.3.3 
 --with scipy==1.16.2 python -B lmk6c_clock_screen.py --output NEW.json
Uses retained reduced RLC model read-only. No CAD or quote-package writes.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HISTORY = Path('/home/mouse9911/gits/crow-first-run-5c10p-20261022/project/03_src/recovery')
sys.path.insert(0, str(HISTORY/'ls12-analysis'))
from native_model import analyze, construct
from model import trace, crossings
import numpy as np
from scipy.linalg import expm


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def periodic(g, rail, duty, **params):
    a, steady, sinks, pins, caps, edges = construct(g, **params)
    period = 1000/12.288
    ton = duty*period
    ph, pl = expm(a*ton), expm(a*(period-ton))
    eye = np.eye(len(a))
    # 80/20% envelope extends the TI nominal-rail 6.6mA DC endpoints as
    # an explicit prototype model, NOT guaranteed limits at every rail.
    hi, lo = steady*.8*rail, steady*.2*rail
    initial = np.linalg.solve(eye-pl@ph, pl@(eye-ph)@hi+(eye-pl)@lo)
    t1,y1=trace(a,steady,initial,.8*rail,ton,.02)
    t2,y2=trace(a,steady,y1[-1],.2*rail,period-ton,.02)
    t=np.concatenate((t1,t2[1:]+ton))
    y=np.concatenate((y1,y2[1:]))
    assert np.allclose(initial,y[-1],atol=1e-7)
    result=[]
    for n in sinks:
        up=crossings(t,y[:,n],.7*rail+.1,1)
        down=crossings(t,y[:,n],.7*rail+.1,-1)
        lu=crossings(t,y[:,n],.3*rail-.1,1)
        ld=crossings(t,y[:,n],.3*rail-.1,-1)
        assert len(up)==len(down)==len(lu)==len(ld)==1
        result.append(dict(high_ns=down[0]-up[0],low_ns=period-ld[0]+lu[0]))
    return dict(rail=rail,duty=duty,parameters=params,receivers=result)


def extract(board_path):
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew as pcb
    b=pcb.LoadBoard(str(board_path))
    def xy(v):return [pcb.ToMM(v.x),pcb.ToMM(v.y)]
    names=('MCLK_SRC','MCLK_FAN','MCLK_ADC1','MCLK_ADC2')
    g=dict(source=str(board_path),sha256=sha(board_path),
           nets={n:dict(segments=[],pads=[],vias=[]) for n in names})
    for t in b.GetTracks():
        name=t.GetNetname().lstrip('/')
        if name not in names:continue
        assert not isinstance(t,pcb.PCB_VIA)
        g['nets'][name]['segments'].append(dict(start_mm=xy(t.GetStart()),end_mm=xy(t.GetEnd()),
            width_mm=pcb.ToMM(t.GetWidth()),length_mm=pcb.ToMM(t.GetLength()),layer=b.GetLayerName(t.GetLayer())))
    for f in b.GetFootprints():
        for d in f.Pads():
            name=d.GetNetname().lstrip('/')
            if name in names:g['nets'][name]['pads'].append(dict(ref=f.GetReference(),pin=d.GetNumber(),
                at_mm=xy(d.GetPosition()),size_mm=xy(d.GetSize())))
    return g


def run(board=None):
    geometry=HISTORY/'first-run-r3-engineering/v2-native-clock-geometry.json'
    assert sha(geometry)=='39a3b60246075751e8f5367036e9468e7825009084a2060d445fbf444b8cc4f1'
    g=extract(board) if board else json.loads(geometry.read_text())
    fast=[]; slow=[]
    for h,er,rf,rs in itertools.product((.2944*.8,.2944*1.2),(3.91,5.4),
                                    ((.5,.5),(.5,1.5),(1.5,.5),(1.5,1.5)),(40.,60.)):
        p=dict(h=h,er=er,receiver_factor=rf,source_r=rs,
               common_ohm=68,branch_ohm=56,resistor_factor=(.94,.96,.96))
        fast.append(analyze(g,dt=.02,**p))
        p['resistor_factor']=(1.06,1.04,1.04)
        for rail,duty in itertools.product((3.135,3.465),(.45,.55)):
            slow.append(periodic(g,rail,duty,**p))
    return dict(status='POST_LAYOUT_MODEL_SCREEN_NOT_ADOPTION' if board else 'PRE_LAYOUT_SCREEN_ONLY_NOT_ADOPTION',
        geometry_sha256=hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest(),
        geometry=g,
        model_inputs={str(p):sha(p) for p in
                      (Path(__file__),HISTORY/'ls12-analysis/native_model.py',HISTORY/'ls12-analysis/model.py')},
        summary=dict(fast_cases=len(fast),slow_cases=len(slow),
            load_max_pf=max(r['total_cap_pf'] for r in fast),
            physical_overshoot_max_v=max(max(r['fast']['individual_peak_v'][:2])-3.6 for r in fast),
            min_high_ns=min(r['high_ns'] for x in slow for r in x['receivers']),
            min_low_ns=min(r['low_ns'] for x in slow for r in x['receivers'])),
        limitations=[
            'New native geometry is extracted when --board is supplied; otherwise retained CTS geometry.',
            '3.135..3.465 V is a proposed sensitivity, not established actual supply bounds.',
            '80/20% output envelope at non-nominal rails is an engineering model, not a TI guarantee.',
            'Fast step model uses 3.6 V conservatively for excursion only; TI operation at 3.6 V is NOT allowed.',
            'Ideal-reference RLC; single 100mV residual allowance remains unverified.',
            'Positive threshold dwell is a feasibility screen, NOT an invented ADC timing requirement.',
            'Finite source edge shape, jitter, new layout, power, process and actual waveform checks remain.'
        ],fast_cases=fast,slow_cases=slow)


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--board',type=Path)
    args=parser.parse_args(); data=run(args.board)
    with args.output.open('x') as stream:
        json.dump(data,stream,indent=2);stream.write('\n')
    print(json.dumps(data['summary'],indent=2))
