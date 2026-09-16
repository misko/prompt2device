#!/usr/bin/env python3
"""Reproduce this carrier's explicitly simplified, dimension-derived VRML.

STOPGAP backend gap: the shared backend has model attachment overrides but no
manufacturer-drawing-to-nominal-body producer. A future package-model schema
would own dimensional authority, body/terminal solids and omitted geometry.
This script changes NO footprint, pad, board, dossier or checkpoint. It emits
ten source-owned model files under lib/3dmodels/derived (or --out-dir).
Dimensions are mm; VRML vertices are divided by KiCad's 2.54 mm/model-unit.
Input coordinates are footprint X/Y (Y down), Z above seating plane; the
single exporter negates Y into native KiCad model coordinates. See adjacent
model provenance for exact PDF hashes/pages, tolerances and explicit limits.

These are nominal/conservative envelopes, NOT manufacturer CAD, solder-joint
models, mechanical qualification, or accepted current-board registration.
No code or geometric entities from downloaded TI CAD files are consumed.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

UNIT_MM = 2.54
BODY = (0.075, 0.075, 0.080)
METAL = (0.70, 0.70, 0.72)
MARK = (0.55, 0.55, 0.55)
FUSE = (0.55, 0.40, 0.14)


def prism(name, polygon, z0, z1, color=BODY):
    """Closed, convex prism from footprint-frame polygon; geometric source."""
    assert len(polygon) >= 3 and z1 > z0
    return dict(name=name, polygon=polygon, z0=z0, z1=z1, color=color)


def box(name, x0, y0, x1, y1, z0, z1, color=BODY):
    assert x1 > x0 and y1 > y0
    return prism(name, [(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,color)


def profile_prism(name, polygon, start, end, axis, color=BODY):
    """Extrude a convex profile in a right-handed cyclic coordinate frame.

    axis X uses (Y,Z); axis Y uses (Z,X). This is source geometry in mm,
    before the single native-VRML Y reflection in encode().
    """
    assert axis in ('x', 'y')
    area=sum(a[0]*b[1]-b[0]*a[1]
             for a,b in zip(polygon,polygon[1:]+polygon[:1]))
    assert abs(area)>1e-9
    shape=prism(name,polygon if area>0 else list(reversed(polygon)),start,end,color)
    shape['axis']=axis
    return shape


def wson(name, size, count, terminal_length, ep=None, pin1_length=None):
    # TI DSE4220552/B, DSG4218900/E and DSK4218903/C package outlines.
    # Body plan is nominal, height0.8 is maximum; body standoff0.025 is
    # midpoint of the specified0..0.05. Rectangular ends omit fine radii.
    half=size/2
    shapes=[box('body',-half,-half,half,half,0.025,0.8)]
    n=count//2
    for i in range(n):
        y=(i-(n-1)/2)*0.5
        length=pin1_length if i==0 and pin1_length else terminal_length
        shapes.append(box('terminal_'+str(i+1),-half,y-0.125,-half+length,y+0.125,0,0.2,METAL))
        shapes.append(box('terminal_'+str(count-i),half-terminal_length,y-0.125,half,y+0.125,0,0.2,METAL))
    if ep:
        x,y=ep[0]/2,ep[1]/2
        # The0.25 corner is explicitly dimensioned for DSG. DSK optional
        # pin1 chamfer is not dimensioned: use rectangular EP, not guessed.
        poly=[(-x+0.25,-y),(x,-y),(x,y),(-x,y),(-x,-y+0.25)] if name=='TI_DSG0008A' else [(-x,-y),(x,-y),(x,y),(-x,y)]
        shapes.append(prism('terminal_'+str(count+1),poly,0,0.2,METAL))
    # Tiny top-side index graphic is illustrative, entirely within envelope.
    shapes.append(box('illustrative_pin1_index',-half+0.12,-half+0.12,-half+0.23,-half+0.23,0.799,0.8,MARK))
    return shapes


def qfn48():
    # Cirrus DS1314F1 p93 Figure10-1:6BSC, e=.4, b=.2,L=.4,
    # exposed paddle4.6, A=.75nom,A1=.035nom,A3=.203ref.
    shapes=[box('body',-3,-3,3,3,0.035,0.75)]
    for i in range(12):
        p=-2.2+i*0.4
        shapes += [box('terminal_'+str(i+1),-3,p-0.1,-2.6,p+0.1,0,0.203,METAL),
                   box('terminal_'+str(i+13),p-0.1,2.6,p+0.1,3,0,0.203,METAL),
                   box('terminal_'+str(i+25),2.6,-p-0.1,3,-p+0.1,0,0.203,METAL),
                   box('terminal_'+str(i+37),-p-0.1,-3,-p+0.1,-2.6,0,0.203,METAL)]
    shapes.append(box('terminal_49',-2.3,-2.3,2.3,2.3,0,0.203,METAL))
    shapes.append(box('illustrative_pin1_index',-2.65,-2.65,-2.4,-2.4,0.749,0.75,MARK))
    return shapes


def xgl4020():
    # Coilcraft Document1529-3:4.0+/-.3body,2.1maximum total height;
    # terminal length.82+/-.05, width3.25typ, internal gap1.57+/-.25.
    # Terminal centre pitch1.57+.82=2.39, NOT PCB land-centre pitch2.37.
    # Undimensioned metal thickness modeled as0.05mm visual estimate.
    shapes=[box('body',-2,-2,2,2,0.05,2.1)]
    for number,centre in ((1,-1.195),(2,1.195)):
        shapes.append(box('terminal_'+str(number),centre-.41,-1.625,centre+.41,1.625,0,.05,METAL))
    shapes.append(box('illustrative_start_lead_index',-1.6,-1.6,-1.5,1.6,2.099,2.1,MARK))
    return shapes


def fuse(length,width,height,end_width):
    # Max overall envelope from the exact electrical-family dimension row.
    # End-band E midpoint is VISUAL ONLY; castellation/D extremes omitted.
    h=length/2;w=width/2
    # Partition the envelope: overlapping coplanar body/band faces made one
    # visual band disappear in native side renders. No dimensional change.
    return [box('body_centre_of_maximum_envelope',-h+end_width,-w,h-end_width,w,0,height,FUSE),
            box('terminal_1_visual_band',-h,-w,-h+end_width,w,0,height,METAL),
            box('terminal_2_visual_band',h-end_width,-w,h,w,0,height,METAL)]


def molex(count):
    # Molex SD43650001/D8 p1: A=9.65/15.65,B=3/9,pitch3;
    # front-to-peg4.6 plus peg-to-pin4.32 => frontY=-8.92;
    # depth9.9 => backY=.98. Body4.37 plus latch1.2 => maximumZ5.57.
    # D8 front/side/isometric views establish one cavity per circuit, lower
    # outer-corner chamfers on the first/last cavities, and a roof latch near
    # the mouth. Their undimensioned profiles below are visual estimates:
    # this NTS drawing is NOT a scale source for mating dimensions.
    # These features support visual orientation/keying identity only.
    # Tolerance-qualified mating, retention and cable-service fit are separate.
    width={2:9.65,4:15.65}[count];centre=(count-1)*3/2
    x0=centre-width/2;x1=centre+width/2
    wall=.60;roof=.60;rear_y=-2.25;opening_half=1.18
    body_h=4.37  # visual dimensions above are estimates; body_h is drawing-controlled
    shapes=[box('housing_rear_wall',x0,rear_y,x1,.98,0,body_h),
            box('housing_mouth_roof',x0,-8.92,x1,rear_y,body_h-roof,body_h),
            box('housing_mouth_floor',x0,-8.92,x1,rear_y,0,wall),
            box('housing_first_outer_wall',x0,-8.92,-opening_half,rear_y,0,body_h),
            box('housing_last_outer_wall',(count-1)*3+opening_half,-8.92,x1,rear_y,0,body_h)]
    for i in range(count-1):
        shapes.append(box('housing_cavity_divider_'+str(i+1),
                          i*3+opening_half,-8.92,(i+1)*3-opening_half,rear_y,0,body_h))
    # End-cavity polarization: fill the lower outside corner, as depicted
    # in the D8 front view. 0.65 is an explicit illustrative chamfer leg.
    chamfer=.65
    left=-opening_half;right=(count-1)*3+opening_half
    shapes.append(profile_prism('housing_first_cavity_lower_outer_chamfer_visual',
        [(wall,left),(wall,left+chamfer),(wall+chamfer,left)],
        -8.92,rear_y,'y'))
    shapes.append(profile_prism('housing_last_cavity_lower_outer_chamfer_visual',
        [(wall,right),(wall+chamfer,right),(wall,right-chamfer)],
        -8.92,rear_y,'y'))
    # The source views put the latch near the front, not beside the rear pin
    # row. Plan location/width and ramp shape are illustrative; only its
    # 1.20mm rise and 5.57mm total height are dimensioned.
    shapes.append(profile_prism('housing_roof_latch_visual',
        [(-8.3,body_h),(-7.2,5.57),(-6.4,5.57),(-6.4,body_h)],
        centre-1.25,centre+1.25,'x'))
    for i in range(count):
        shapes.append(box('terminal_'+str(i+1)+'_board_entry_tail',i*3-.32,-.32,i*3+.32,.32,-3.18,0,METAL))
        # Depicted horizontal pin inside each cavity. Cross section .64SQ
        # is specified; the tip station and height are visual estimates.
        shapes.append(box('contact_'+str(i+1)+'_horizontal_visual',
                          i*3-.32,-7.35,i*3+.32,.32,1.865,2.505,METAL))
    return shapes


def samtec_tmm_106_01_l_d():
    # Samtec TMM revision AS sheet1, selected TMM-106-01-L-D style01.
    # Body3.94x12x1.50mm REF; post A3.20 (not labelled MIN), tail B3.50REF,
    # overall L8.20REF and contact area C2.54REF. Pins are0.50mm square.
    # Grooves, tip chamfers, flash, bow, tilt and tolerance extremes omitted.
    shapes=[box('insulator_reference_envelope',-.97,-1.,2.97,11.,0.,1.5)]
    for row in range(6):
        for col in range(2):
            pin=2*row+col+1;x=2.*col;y=2.*row
            shapes.append(box('terminal_'+str(pin),x-.25,y-.25,x+.25,y+.25,-3.5,4.7,METAL))
    return shapes


def wslp1206_50m():
    # Vishay30122 rev09-Sep-2024 p2, exact0.006..0.050ohm row:
    # nominal L3.20,W1.60,H.635,T.508; each has tolerance+/-.254mm.
    # T is the physical end-terminal length, not the1.65mm PCB pad length.
    # The undimensioned underside relief, coating and weld details are
    # omitted: centre fills its nominal enclosing prism down to seating Z0.
    # Partition instead of coplanar overlapping solids. This is NOT the
    # maximum3.454x1.854x.889 production envelope or a thermal model.
    return [box('body_nominal_envelope',-1.092,-.8,1.092,.8,0,.635),
            box('terminal_1',-1.6,-.8,-1.092,.8,0,.635,METAL),
            box('terminal_2',1.092,-.8,1.6,.8,0,.635,METAL)]


def models():
    return {
        'TI_DSE0006A_nominal.wrl':wson('TI_DSE0006A',1.5,6,.5,pin1_length=.6),
        'TI_DSG0008A_nominal.wrl':wson('TI_DSG0008A',2.,8,.3,ep=(.9,1.6)),
        'TI_DSK0010A_nominal.wrl':wson('TI_DSK0010A',2.5,10,.4,ep=(1.2,2.)),
        'Cirrus_CS5308P_QFN48_nominal.wrl':qfn48(),
        'Coilcraft_XGL4020_nominal.wrl':xgl4020(),
        'Littelfuse_1812L035_60_max-envelope.wrl':fuse(4.73,3.41,1.8,.4),
        'Littelfuse_2920L260_33_max-envelope.wrl':fuse(7.98,5.44,1.8,1.125),
        'Molex_43650-0400_conservative-envelope.wrl':molex(4),
        'Molex_43650-0200_conservative-envelope.wrl':molex(2),
        'Vishay_WSLP1206_50m_nominal.wrl':wslp1206_50m(),
    }


def encode(shapes):
    lines=['#VRML V2.0 utf8',
           '# Source-owned dimension-derived geometry; NOT manufacturer CAD.',
           '# Reproduce with03_src/build_package_models.py; see provenance.md.',
           '# Units: one coordinate unit is2.54mm; nativeY=-footprintY.']
    for s in shapes:
        n=len(s['polygon'])
        points=[(x,y,z) for z in (s['z0'],s['z1']) for x,y in s['polygon']]
        if s.get('axis')=='x':
            points=[(z,x,y) for x,y,z in points]
        elif s.get('axis')=='y':
            points=[(y,z,x) for x,y,z in points]
        vertices=[(x/UNIT_MM,-y/UNIT_MM,z/UNIT_MM) for x,y,z in points]
        # Negating Y reverses polygon winding. Bottom keeps order, top
        # reverses, side quads follow outward orientation in model frame.
        faces=[list(range(n)),list(range(2*n-1,n-1,-1))]
        faces += [[i,(i+n),((i+1)%n+n),(i+1)%n] for i in range(n)]
        lines += ['# solid '+s['name'],'Shape {',' appearance Appearance { material Material { diffuseColor '+' '.join(map(str,s['color']))+' } }',
                  ' geometry IndexedFaceSet { solid TRUE','  coord Coordinate { point [']
        lines += ['   '+ ' '.join(f'{v:.9f}' for v in vertex)+',' for vertex in vertices]
        lines += ['  ] }','  coordIndex [']
        lines += ['   '+', '.join(map(str,face))+', -1,' for face in faces]
        lines += ['  ]',' }','}']
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=Path(__file__).parent/'lib/3dmodels/derived')
    args=parser.parse_args();args.out_dir.mkdir(parents=True,exist_ok=True)
    for name,shapes in models().items():
        data=encode(shapes).encode();(args.out_dir/name).write_bytes(data)
        print(hashlib.sha256(data).hexdigest(),name)


if __name__=='__main__':main()
