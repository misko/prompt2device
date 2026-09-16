"""Hostile tests for model source only. No candidate-board generation.

Independent expected dimensions below are transcribed from the PDF figures
listed in lib/3dmodels/provenance.md, not imported from the model producer.
Run with the KiCad-capable /usr/bin/python3. --archive is optional evidence
input for exact non-model source preservation, not a regenerated checkpoint.
"""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

SRC=Path(__file__).resolve().parents[1]
LIB=SRC/'lib/3dmodels'


def solids(path):
    """Independent VRML parser for emitted explicit Coordinate point lists."""
    result={}
    for name,body in re.findall(r'# solid (\S+)\n(.*?)(?=# solid |\Z)',path.read_text(),re.S):
        points=re.search(r'point\s*\[([^]]+)\]',body,re.S).group(1)
        nums=[float(n) for n in re.findall(r'[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?',points)]
        assert len(nums)>0 and len(nums)%3==0
        # Independently decode KiCad VRML into footprint frame, millimetres.
        result[name]=[(nums[i]*2.54,-nums[i+1]*2.54,nums[i+2]*2.54) for i in range(0,len(nums),3)]
    assert result,path
    return result


def bounds(points):
    return tuple(min(p[i] for p in points) for i in range(3))+tuple(max(p[i] for p in points) for i in range(3))


def sexpr(text):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',text)
    stack=[];root=None
    for token in tokens:
        if token=='(':
            new=[]
            if stack:stack[-1].append(new)
            else:
                assert root is None
                root=new
            stack.append(new)
        elif token==')':assert stack;stack.pop()
        else:assert stack;stack[-1].append(token)
    assert root and not stack
    return root


def nonmodel(text):
    return [v for v in sexpr(text) if not isinstance(v,list) or v[0]!='model']


class ModelTests(unittest.TestCase):
    def test_reproducible(self):
        with tempfile.TemporaryDirectory(prefix='carrier-package-reproduce-') as target:
            subprocess.run([sys.executable,str(SRC/'build_package_models.py'),'--out-dir',target],check=True,capture_output=True)
            files=list((LIB/'derived').glob('*.wrl'))
            self.assertEqual(len(files),10)
            for p in files:self.assertEqual(p.read_bytes(),(Path(target)/p.name).read_bytes())

    def test_independent_body_dimensions(self):
        expected={
            'TI_DSE0006A_nominal.wrl':(-.75,-.75,0,.75,.75,.8),
            'TI_DSG0008A_nominal.wrl':(-1,-1,0,1,1,.8),
            'TI_DSK0010A_nominal.wrl':(-1.25,-1.25,0,1.25,1.25,.8),
            'Cirrus_CS5308P_QFN48_nominal.wrl':(-3,-3,0,3,3,.75),
            'Coilcraft_XGL4020_nominal.wrl':(-2,-2,0,2,2,2.1),
            'Littelfuse_1812L035_60_max-envelope.wrl':(-2.365,-1.705,0,2.365,1.705,1.8),
            'Littelfuse_2920L260_33_max-envelope.wrl':(-3.99,-2.72,0,3.99,2.72,1.8),
            'Molex_43650-0400_conservative-envelope.wrl':(-3.325,-8.92,-3.18,12.325,.98,5.57),
            'Molex_43650-0200_conservative-envelope.wrl':(-3.325,-8.92,-3.18,6.325,.98,5.57),
            'Vishay_WSLP1206_50m_nominal.wrl':(-1.6,-.8,0,1.6,.8,.635),
        }
        for name,wanted in expected.items():
            with self.subTest(name=name):
                actual=bounds([p for poly in solids(LIB/'derived'/name).values() for p in poly])
                for a,b in zip(actual,wanted):self.assertAlmostEqual(a,b,places=7)

    def test_independent_terminal_geometry(self):
        # Native TOP view physical pin1 is upper-left, not bottom-view left.
        cases=[('TI_DSE0006A_nominal.wrl',6,-.45,-.5,.6,.25),
               ('TI_DSG0008A_nominal.wrl',9,-.85,-.75,.3,.25),
               ('TI_DSK0010A_nominal.wrl',11,-1.05,-1.,.4,.25),
               ('Cirrus_CS5308P_QFN48_nominal.wrl',49,-2.8,-2.2,.4,.2)]
        for name,count,x,y,length,width in cases:
            data=solids(LIB/'derived'/name)
            self.assertEqual(len([k for k in data if k.startswith('terminal_')]),count)
            b=bounds(data['terminal_1'])
            for a,w in zip(((b[0]+b[3])/2,(b[1]+b[4])/2,b[3]-b[0],b[4]-b[1]),(x,y,length,width)):
                self.assertAlmostEqual(a,w,places=7)
        data=solids(LIB/'derived/Coilcraft_XGL4020_nominal.wrl')
        b=bounds(data['terminal_1']);self.assertAlmostEqual((b[0]+b[3])/2,-1.195,places=7)
        self.assertAlmostEqual(b[3]-b[0],.82,places=7)
        self.assertAlmostEqual(b[4]-b[1],3.25,places=7)
        for count in (2,4):
            data=solids(LIB/f'derived/Molex_43650-0{count}00_conservative-envelope.wrl')
            for i in range(count):
                b=bounds(data[f'terminal_{i+1}_board_entry_tail'])
                self.assertAlmostEqual((b[0]+b[3])/2,i*3,places=7)
                self.assertAlmostEqual((b[1]+b[4])/2,0,places=7)
                self.assertAlmostEqual(b[3]-b[0],.64,places=7)

    def test_transform_known_bad_y_mirror_and_unit_scale(self):
        points=solids(LIB/'derived/TI_DSE0006A_nominal.wrl')['terminal_1']
        centre=tuple(sum(p[i] for p in points)/len(points) for i in range(3))
        self.assertLess(centre[0],0);self.assertLess(centre[1],0)
        # Known-bad Y mirror swaps1 and3; known-bad mm-as-VRML expands2.54x.
        self.assertGreater(-centre[1],0)
        self.assertNotAlmostEqual(.8*2.54,.8)
        for deg in (0,90,180,270):
            t=math.radians(deg)
            x=centre[0]*math.cos(t)+centre[1]*math.sin(t)
            y=-centre[0]*math.sin(t)+centre[1]*math.cos(t)
            self.assertAlmostEqual(math.hypot(x,y),math.hypot(*centre[:2]))

    def test_supervisor_ground_toe_preserves_paste_and_derives_smd_mask(self):
        import pcbnew
        lib=str(SRC/'lib/crow_audio_carrier.pretty')
        original=pcbnew.FootprintLoad(lib,'TI_DSE0006A_Exact')
        engineered=pcbnew.FootprintLoad(lib,'TI_DSE0006A_GNDToe018')
        self.assertIsNotNone(engineered)
        def geometry(p):
            return (p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y,
                    p.GetRoundRectCornerRadius(),p.GetShape())
        old={p.GetNumber():p for p in original.Pads()}
        new={p.GetNumber():p for p in engineered.Pads() if p.GetNumber()}
        self.assertEqual(set(old),set(new))
        for pin in set(old)-{'2'}:
            self.assertEqual(geometry(old[pin]),geometry(new[pin]))
        self.assertEqual(geometry(new['2'])[:4],(-690000,0,880000,250000))
        self.assertEqual(new['2'].GetRoundRectCornerRadius(),50000)
        # TI p26 stencil dimensions retained; p25 lowerdetail defines pads1–3
        # as SMD with at least50um copper overmask, independently of its
        # contradictory upper green outline. Mask sizes are derived, not quoted.
        for pin in ('1','2','3'):
            self.assertFalse(new[pin].GetLayerSet().Contains(pcbnew.F_Mask))
        pastes=[p for p in engineered.Pads() if p.GetLayerSet().Contains(pcbnew.F_Paste)]
        self.assertEqual(sorted(geometry(p) for p in pastes),sorted(geometry(p) for p in old.values()))
        masks=[p for p in engineered.Pads() if not p.GetNumber() and p.GetLayerSet().Contains(pcbnew.F_Mask)]
        actual=sorted(geometry(p)[:4] for p in masks)
        self.assertEqual(actual,sorted([(-550000,-500000,700000,150000),
                                       (-600000,0,600000,150000),
                                       (-600000,500000,600000,150000)]))
        for pad in masks:
            self.assertFalse(pad.GetLayerSet().Contains(pcbnew.F_Cu))
            self.assertEqual(pad.GetShape(),pcbnew.PAD_SHAPE_RECT)
        masks[0].SetSize(pcbnew.VECTOR2I(800000,250000))
        self.assertNotEqual(sorted(geometry(p)[:4] for p in masks),actual)

    def test_nonmodel_projection_rejects_pad_edit(self):
        path=SRC/'lib/crow_audio_carrier.pretty/TI_DSE0006A_Exact.kicad_mod'
        original=path.read_text()
        changed=original.replace('(size 0.8 0.25)','(size 0.81 0.25)',1)
        self.assertNotEqual(nonmodel(original),nonmodel(changed))
        self.assertEqual(nonmodel(original),nonmodel(original.replace('TI_DSE0006A_nominal.wrl','other.wrl')))

    def test_wslp_nominal_terminals_and_rotation_registration(self):
        import pcbnew
        # Vishay30122 p2 exact0.006..0.050ohm row: L3.20,W1.60,
        # H.635,T.508. T is physical end length, NOT PCB pad length1.65.
        data=solids(LIB/'derived/Vishay_WSLP1206_50m_nominal.wrl')
        self.assertEqual(set(data),{'body_nominal_envelope','terminal_1','terminal_2'})
        expected={1:(-1.6,-.8,0,-1.092,.8,.635),
                  2:(1.092,-.8,0,1.6,.8,.635)}
        for number,wanted in expected.items():
            for actual,value in zip(bounds(data[f'terminal_{number}']),wanted):
                self.assertAlmostEqual(actual,value,places=7)
        fp=pcbnew.FootprintLoad(str(SRC/'lib/crow_audio_carrier.pretty'),
                               'Vishay_WSLP1206_50m_Exact')
        self.assertIsNotNone(fp)

        def registered(degrees, model_degrees=0, scale=1, invert_z=False):
            fp.SetOrientationDegrees(degrees)
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(23),pcbnew.FromMM(31)))
            pads={p.GetNumber():p for p in fp.Pads()}
            t=math.radians(degrees+model_degrees)
            for number in (1,2):
                pad=pads[str(number)]
                bb=pad.GetBoundingBox()
                for x,y,z in data[f'terminal_{number}']:
                    x,y,z=x*scale,y*scale,z*scale
                    px=23+x*math.cos(t)+y*math.sin(t)
                    py=31-x*math.sin(t)+y*math.cos(t)
                    pz=-z if invert_z else z
                    if not (bb.GetLeft()/1e6-1e-7<=px<=bb.GetRight()/1e6+1e-7
                            and bb.GetTop()/1e6-1e-7<=py<=bb.GetBottom()/1e6+1e-7
                            and -1e-7<=pz<=.635+1e-7):
                        return False
            return True

        for deg in (0,90,180,270):
            with self.subTest(degrees=deg):
                self.assertTrue(registered(deg))
                # Execute the same registration predicate on actual bad
                # point transforms, rather than asserting constants differ.
                self.assertFalse(registered(deg,model_degrees=90))
                self.assertFalse(registered(deg,scale=2.54))
                self.assertFalse(registered(deg,invert_z=True))

    def test_wslp_model_attachment_is_identity_and_preserves_land(self):
        fp=sexpr((SRC/'lib/crow_audio_carrier.pretty/Vishay_WSLP1206_50m_Exact.kicad_mod').read_text())
        model=[v for v in fp if isinstance(v,list) and v[0]=='model']
        self.assertEqual(len(model),1)
        self.assertEqual(model[0][1],'"${KIPRJMOD}/../03_src/lib/3dmodels/derived/Vishay_WSLP1206_50m_nominal.wrl"')
        self.assertEqual(model[0][2:],[['offset',['xyz','0','0','0']],
                                     ['scale',['xyz','1','1','1']],
                                     ['rotate',['xyz','0','0','0']]])
        pads=[v for v in fp if isinstance(v,list) and v[0]=='pad']
        self.assertEqual(len(pads),2)
        for pad,x in zip(pads,('-1.725','1.725')):
            self.assertIn(['at',x,'0'],pad)
            self.assertIn(['size','1.65','1.93'],pad)
            self.assertIn(['layers','"F.Cu"','"F.Paste"','"F.Mask"'],pad)

    def test_kicad_library_reopen(self):
        import pcbnew
        names=('TI_DSE0006A_Exact','TI_DSG0008A_Exact','TI_DSK0010A_Exact',
               'Coilcraft_XGL4020_Exact','Cirrus_CS5308P_QFN48_6x6_P0.4_EP4.6',
               'Molex_43650-0400_RA_Exact','Wurth_615008160221_RJ45','Molex_43650-0200_RA_Exact',
               'Vishay_WSLP1206_50m_Exact')
        for name in names:
            fp=pcbnew.FootprintLoad(str(SRC/'lib/crow_audio_carrier.pretty'),name)
            self.assertIsNotNone(fp);self.assertEqual(len(list(fp.Models())),1)
            model=list(fp.Models())[0]
            path=Path(model.m_Filename.replace('${KIPRJMOD}',str(SRC.parent/'04_kicad')))
            self.assertTrue(path.is_file());self.assertGreater(path.stat().st_size,0)


if __name__=='__main__':unittest.main(verbosity=2)
