"""Drawing-derived diagnostic inputs. Does not change native boards or releases."""
import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BLACK=[.12,.13,.15];GOLD=[.86,.64,.17];SILVER=[.65,.70,.75]


def box(bounds,color=BLACK,**extra):return dict(kind='box',bounds=bounds,color=color,**extra)
def cylinder(base,axis,radius,length,color=SILVER,**extra):
    return dict(kind='cylinder',base=base,axis=axis,radius=radius,length=length,color=color,**extra)


def rj():
    pads={str(n):[(n-1)*.040*25.4,.070*25.4 if n%2==0 else 0] for n in range(1,9)}
    pegs=[[-.110*25.4,-.100*25.4],[.390*25.4,-.100*25.4]]
    solids=[box([-4.318,-7.620,0,11.430,7.366,13.208],cuts=[
        box([-2.4,-7.7,2.4,9.5,1.0,9.5]),box([1.5,-7.7,9.4,5.6,-1.0,11.4])])]
    solids += [cylinder([x,y,-3],[0,0,1],1.5,3,BLACK,tag='illustrative peg at drawing-derived center') for x,y in pegs]
    solids += [cylinder([x,y,-3],[0,0,1],.20,3.2,GOLD,tag='pin'+n) for n,(x,y) in pads.items()]
    return dict(mpn='RJHSE-5080',source='Amphenol P-RJHSE-X080 RevA May22/2019, component-side PCB pattern, primary inch dimensions; retained rjhsex080.pdf SHA256 e96d3f6cde115981be470e0edd3159dfda3ebe1a453db0c45d525e629668a756',
                limitations='Nominal housing and contact/peg centers. Cavity, latch, peg diameter/projection and circular contact profiles illustrative; no fit or plating acceptance.',
                expected_pads=pads,expected_pegs=pegs,tolerance_mm=.006,
                mouth_direction=[0,-1],intended_direction=[0,-1],solids=solids)


def barrel():
    pads={'1':[0,0],'2':[0,6],'3':[4.7,3]}
    solids=[box([-4.5,-.7,0,4.5,13.7,11],cuts=[cylinder([0,13.8,6.5],[0,-1,0],3.25,8)]),
            cylinder([0,13.3,6.5],[0,-1,0],1,6,GOLD)]
    solids += [box([x-.35,y-.35,-3.5,x+.35,y+.35,.1],GOLD,tag='terminal'+n) for n,(x,y) in pads.items()]
    return dict(mpn='PJ-102AH',source='CUI PJ-102AH RevA Nov17/2005, side view/front offset and PCB TOP VIEW; https://cdn-shop.adafruit.com/datasheets/21mmdcjackDatasheet.pdf',
                limitations='Nominal bounding housing and mouth axis; square roof and terminal profiles illustrative. Existing enlarged round holes differ from maker slots. Historic outward corridor contradicts actual +Y mouth.',
                expected_pads=pads,expected_pegs=[],tolerance_mm=.006,
                mouth_direction=[0,1],intended_direction=[0,-1],solids=solids)


def pico():
    # Original SC0915 module, USB at pin1/pin40 end, not header accessories.
    return dict(mpn='SC0915',source='Raspberry Pi Pico original module pinout/mechanical drawing; https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf; prior first-run native registration retained',
                limitations='21x51 module outline and pin1/pin40 end identify USB direction. Shell/cavity dimensions and 1mm module height illustrative, not exact official STEP; no connector clearance or assembly-height signoff.',
                expected_pads={'1':[-9.69,-24.13],'20':[-9.69,24.13],'40':[9.69,-24.13]},
                expected_pegs=[],tolerance_mm=.006,mouth_direction=[0,-1],intended_direction=[0,-1],
                solids=[box([-10.5,-25.5,0,10.5,25.5,1],[.10,.42,.25]),
                        box([-3.9,-26.5,1,3.9,-20.5,3.5],SILVER,cuts=[box([-3.2,-26.6,1.5,3.2,-23,3.0])]),
                        box([-3,-3,1,3,3,2],BLACK)])


def build():
    common=dict(version=1,model_notes=['Drawing-derived connector diagnostics, not production-approved models.',
        'All other component bodies are native-footprint XY envelopes with illustrative1mm heights; not collision evidence.',
        'Carrier J1 outward direction is an independent edge-access requirement from prior mating review; do not change it to hide disagreement.'])
    carrier={**copy.deepcopy(common),'label':'Crow r9 carrier | native X right / Y down',
             'connectors':{**{f'J{i}':rj() for i in range(101,109)},'J1':barrel(),'U3':pico()}}
    pod={**copy.deepcopy(common),'label':'Crow r9 pod | native X right / Y down','connectors':{'J1':rj()}}
    for name,data in [('carrier',carrier),('pod',pod)]:
        path=ROOT/f'{name}-inspection.json'
        if path.exists():raise ValueError('Refusing existing input '+str(path))
        path.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':build()
