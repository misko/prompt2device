"""RJ45 entry contract controls, plus independent isolated native pad geometry.

Full board/schematic net census, clearance and post-route acceptance remain
conductor gates. The isolated footprint test never emits a production board.
"""
from pathlib import Path
import copy,math,sys,unittest
import yaml,pcbnew
P=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(P/'03_src'))
sys.path.insert(0,str(Path(__file__).parent))
import check_analog_paths as checker
from test_local_placement_source import source_builder

class EntryTests(unittest.TestCase):
    def setUp(self):
        self.config=checker.critical.load_config(P/'03_src/rules/critical_paths.yaml')
        self.route=yaml.safe_load((P/'03_src/route.yaml').read_text())
        self.pins={}
        for n in range(1,9):
            for leg,j,u in [('P',5,3),('N',4,5)]:
                for r,p in [(f'J{n}',str(j)),(f'U_ESD{n}',str(u)),(f'C_A{n}{leg}','1')]:self.pins[r,p]=f'AUDIO_{leg}{n}'
            for p in ['9','10']:self.pins[f'J{n}',p]='CHASSIS'
    def test_complete_entry_contract(self):
        r=checker.validate_entry_paths(self.config,self.route,self.pins)
        self.assertEqual((r['prefixes'],r['downstream_paths'],r['shield_pads']),(16,16,16))
    def test_dropped_branch_missing_clamp_and_ghost_pad_fail(self):
        for defect in ['drop','clamp','ghost']:
            c=copy.deepcopy(self.config);pins=dict(self.pins)
            if defect=='drop':c['prefixes'].pop()
            if defect=='clamp':del pins['U_ESD8','5']
            if defect=='ghost':pins['TP_GHOST','1']='AUDIO_P1'
            with self.assertRaises(checker.PathError):checker.validate_entry_paths(c,self.route,pins)
    def test_layer_via_seed_and_relaxed_limits_fail(self):
        for defect in ['layer','via','seed','limit','span']:
            c=copy.deepcopy(self.config);r=copy.deepcopy(self.route)
            if defect=='layer':c['short_paths'][0]['layer']='B.Cu'
            if defect=='via':next(x for x in r['prep']['seed_stubs']['stubs'] if x.get('pin')=='J1.5')['vias']=[[1,1]]
            if defect=='seed':r['prep']['seed_stubs']['stubs'].remove(next(x for x in r['prep']['seed_stubs']['stubs'] if x.get('pin')=='J1.5'))
            if defect=='limit':c['short_paths'][0]['max_length_mm']=9.001
            if defect=='span':c['short_paths'][0]['max_pad_centre_mm']=8.601
            with self.assertRaises(checker.PathError):checker.validate_entry_paths(c,r,self.pins)
    def test_extra_ghost_duplicate_and_offpad_seeds_fail(self):
        for defect in ('extra','ghost','duplicate','offpad','post-via'):
            r=copy.deepcopy(self.route)
            entry=next(x for x in r['prep']['seed_stubs']['stubs'] if x.get('pin')=='J1.5')
            launch=next(x for x in r['prep']['seed_stubs']['stubs'] if x.get('pin')=='U_ESD1.3')
            if defect=='extra':r['prep']['seed_stubs']['stubs'].append(dict(net='AUDIO_P1',pin='TP_GHOST.1',segments=[]))
            if defect=='ghost':launch['pin']='U_ESD1.2'
            if defect=='duplicate':r['prep']['seed_stubs']['stubs'].append(copy.deepcopy(entry))
            if defect=='offpad':entry['segments'][0]['pts'][-1][0]+=.1
            if defect=='post-via':launch['vias'][0][0]+=.1
            with self.assertRaises(checker.PathError):checker.validate_entry_paths(self.config,r,self.pins)
    def test_exact_admitted_signal_width_layer_and_negative_via(self):
        for defect in ('old-width','below-floor','wrong-layer','old-n-via','missing-n-via','extra-bank','unknown-bank','via-family'):
            r=copy.deepcopy(self.route)
            e=next(x for x in r['prep']['seed_stubs']['stubs'] if x.get('pin')=='J1.5')
            n=next(x for x in r['prep']['seed_stubs']['stubs'] if x.get('pin')=='U_ESD1.5')
            if defect=='old-width':e['segments'][0]['width']=.26
            if defect=='below-floor':e['segments'][0]['width']=.19
            if defect=='wrong-layer':e['segments'][0]['layer']='B.Cu'
            if defect=='old-n-via':n['vias']=[[40.35,35.25]];n['segments'][0]['pts'][-1]=[40.35,35.25]
            if defect=='missing-n-via':n['vias']=[]
            if defect=='unknown-bank':r['prep']['seed_stubs']['stubs'].append(dict(net='AUDIO_P9',pin='J9.5',segments=[]))
            if defect=='via-family':r['prep']['seed_stubs']['via']['size']=.6
            if defect=='extra-bank':r['prep']['seed_stubs']['stubs'].append(copy.deepcopy(n))
            with self.assertRaises(checker.PathError,msg=defect):checker.validate_entry_paths(self.config,r,self.pins)
    def test_grounded_shell_or_missing_route_owner_fails(self):
        pins=dict(self.pins);pins['J1','9']='GND'
        with self.assertRaises(checker.PathError):checker.validate_entry_paths(self.config,self.route,pins)
        bad=copy.deepcopy(self.route)
        bad['prep']['waves']['groups']['pod_power'].remove('CHASSIS')
        with self.assertRaises(checker.PathError):checker.validate_entry_paths(self.config,bad,self.pins)
    def test_all_sixteen_seeds_land_on_independent_native_top_pads(self):
        f=yaml.safe_load((P/'03_src/floorplan.yaml').read_text());b=source_builder(f)
        anchors=b.place_cfg['anchors'];pads={}; native_board=pcbnew.BOARD()
        for n in range(1,9):
            for ref,lib,name,bottom in [(f'J{n}',str(P/'03_src/lib/crow_audio_carrier.pretty'),'Wurth_615008160221_RJ45',False),(f'U_ESD{n}','/usr/share/kicad/footprints/Package_TO_SOT_SMD.pretty','SOT-553',False)]:
                fp=pcbnew.FootprintLoad(lib,name);self.assertIsNotNone(fp);native_board.Add(fp)
                x,y,rot=anchors[ref];fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)));fp.SetOrientationDegrees(rot)
                if bottom:fp.Flip(fp.GetPosition(),False)
                pads.update({f'{ref}.{p.GetNumber()}':(pcbnew.ToMM(p.GetPosition().x),pcbnew.ToMM(p.GetPosition().y)) for p in fp.Pads() if p.GetNumber()})
        seeds={x['pin']:x for x in self.route['prep']['seed_stubs']['stubs'] if x['net'].startswith('AUDIO_') and x['pin'].startswith('J')}
        self.assertEqual(len(seeds),16)
        for path in self.config['short_paths']:
            start,end=path['from'],path['to'];parts=seeds[start]['segments'];pts=parts[0]['pts']
            self.assertLess(math.dist(pads[start],pts[0]),1e-6)
            self.assertLess(math.dist(pads[end],pts[-1]),1e-6)
            self.assertLess(math.dist(pads[start],pads[end]),path['max_pad_centre_mm'])
            self.assertLess(sum(math.dist(a,b) for a,b in zip(pts,pts[1:])),path['max_length_mm'])
            self.assertEqual(len(parts),1)
            for a,b in zip(pts,pts[1:]):
                dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);self.assertTrue(min(dx,dy)<1e-7 or abs(dx-dy)<1e-7)
if __name__=='__main__':unittest.main()
