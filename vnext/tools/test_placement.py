"""Portable placement negative controls. Synthetic geometry is not board approval."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import placement as p


def fp(x,y):
 return {'box':[x-1,y-1,x+1,y+1],'pads':{'1':[{'xy':[x,y],'box':[x-.3,y-.3,x+.3,y+.3],'drill':[0,0]}]}}


class Geometry(unittest.TestCase):
 def test_local_execution_agrees_with_coverage_inventory(self):
  root=Path(__file__).resolve().parents[1]
  graph=json.loads((root/'skills/pcb-design/workflow/graph.json').read_text())
  rows={r['stage_id']:r for r in json.loads((root/'skills/pcb-design/workflow/coverage.json').read_text())['stages']}
  for stage in graph['stages']:
   if 'local_execution' not in stage:continue
   adapter=stage['local_execution'];row=rows[stage['spec']['id']]
   self.assertEqual(row['backing'],'local_procedure')
   self.assertEqual(row['procedure'],adapter['contract'])
   self.assertTrue((root/adapter['contract']).is_file())
   self.assertTrue((root/adapter['tool']).is_file())
 def setUp(self):
  self.spec={'_components':[{'ref':'U1'},{'ref':'C1'}], 'rules':{'proximity':[{'id':'local','a':['C1','1'],'b':['U1','1'],'max_mm':5}]}}
  self.b={'outline':[30,30],'placements':{'U1':[10,10,0],'C1':[14,10,0]},'mounts':[]}
  self.parts={'U1':fp(10,10),'C1':fp(14,10)}
 def failures(self):return p.geometry(self.spec,self.b,self.parts)['failures']
 def test_valid_nonzero_geometry(self):
  self.assertFalse(self.failures());self.assertEqual(p.geometry(self.spec,self.b,self.parts)['physical_parts'],2)
 def test_displaced_decoupler(self):
  self.parts['C1']=fp(23,10);self.assertTrue(any('proximity:' in x for x in self.failures()))
 def test_collision(self):
  self.parts['C1']=fp(10.5,10);self.assertTrue(any('collision:' in x for x in self.failures()))
 def test_mount_keepout(self):
  self.parts['MH1']=fp(10,10);self.assertTrue(any('collision:' in x for x in self.failures()))
 def test_pad_outside(self):
  self.parts['C1']=fp(0,10);self.assertTrue(any('pad-outside:' in x for x in self.failures()))
 def test_reversed_connector(self):
  self.b['placements']['U1']=[10,1,180];self.parts['U1']=fp(10,1)
  self.spec['rules']['access']=[{'ref':'U1','point':[0,-1],'direction':[0,-1],'max_gap_mm':2,'width_mm':3,'depth_mm':10}]
  self.assertTrue(any('access-edge:' in x for x in self.failures()))
 def test_blocked_escape(self):
  self.b['reservations']=[{'id':'clock','rect':[12,9,16,11],'layer':'F.Cu','owner_refs':['U1']}]
  self.assertTrue(any('reservation-pad:' in x for x in self.failures()))
 def test_empty_connector_service_envelope_rejected(self):
  for width,depth in [(0,10),(-1,10),(3,0),(3,-1)]:
   self.spec['rules']['access']=[{'ref':'U1','point':[0,-1],'direction':[0,-1],'max_gap_mm':20,'width_mm':width,'depth_mm':depth}]
   with self.assertRaisesRegex(ValueError,'positive'):self.failures()
 def test_conflicting_corridors(self):
  self.b['reservations']=[{'id':str(i),'rect':[20,20,24,24],'layer':'F.Cu','owner_refs':[]} for i in (1,2)]
  self.assertTrue(any('reservation-conflict:' in x for x in self.failures()))
 def test_internal_layer_on_two_layer_board_rejected(self):
  self.b['layers']=2
  self.b['reservations']=[{'id':'invalid','rect':[20,20,24,24],'layer':'In1.Cu','owner_refs':[]}]
  with self.assertRaisesRegex(ValueError,'unavailable'):self.failures()
 def test_unknown_endpoint_fails(self):
  self.spec['rules']['proximity'][0]['a']=['MISSING','1']
  with self.assertRaises(ValueError):self.failures()
 def test_invalid_replica_is_not_waived(self):
  self.parts.update({'U2':fp(20,20),'C2':fp(27,20)})
  self.spec['rules']['proximity'].append({'id':'replica','a':['C2','1'],'b':['U2','1'],'max_mm':5})
  self.assertTrue(any('replica' in x for x in self.failures()))
 def test_missing_component(self):
  data={'boards':{'b':{'_components':[{'ref':'U1'},{'ref':'C1'}]}}}
  b={**self.b,'layers':2,'layer_plan':'continuous return','notes':'fixture','blocks':[{'id':'all','members':['U1']}]}
  del b['placements']['C1']
  with self.assertRaisesRegex(ValueError,'membership'):p.validate_plan(data,{'version':1,'boards':{'b':b}})
 def test_duplicate_membership(self):
  data={'boards':{'b':{'_components':[{'ref':'U1'},{'ref':'C1'}]}}}
  b={**self.b,'layers':2,'layer_plan':'continuous return','notes':'fixture','blocks':[{'id':'all','members':['U1','C1','C1']}]}
  with self.assertRaisesRegex(ValueError,'membership'):p.validate_plan(data,{'version':1,'boards':{'b':b}})
 def test_nonfinite_and_path_escape(self):
  with self.assertRaises(ValueError):p.number(float('nan'))
  with self.assertRaises(ValueError):p.local(Path('/tmp'),'../escape',False)
 def test_changed_schematic_receipt_fails_before_verifier(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'01_docs').mkdir();(root/'s.json').write_text('changed')
   archive=root/'archive/tools';archive.mkdir(parents=True)
   script=archive/'schematic_admission.py';script.write_text('# synthetic archived verifier')
   c={'version':1,'upstream_toolchain':'archive','archive_files':{'tools/schematic_admission.py':p.sha(script)},
      'schematic_receipt':'s.json','schematic_receipt_sha256':'old'}
   (root/p.CONTRACT).write_text(json.dumps(c))
   with patch.object(p,'ROOT',root):
    with self.assertRaisesRegex(ValueError,'schematic receipt changed'):p.upstream(root)


class NativeReplay(unittest.TestCase):
 """Real pcbnew/CLI artifacts on self-contained fixtures; upstream mocked only here."""
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='vnext-placement-test-');self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
  def put(name,text):
   f=self.root/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text);return f
  self.put=put
  put('lib/Fixture.kicad_mod','''(footprint "Fixture" (version 20260206) (generator "pcbnew") (layer "F.Cu")
 (attr smd)
 (property "Reference" "REF**" (at 0 -2) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))
 (property "Value" "Fixture" (at 0 2) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))
 (fp_rect (start -1 -1) (end 1 1) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))
 (pad "1" smd rect (at -.5 0) (size .6 .6) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "00000000-0000-4000-8000-000000000001"))
 (pad "2" smd rect (at .5 0) (size .6 .6) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "00000000-0000-4000-8000-000000000002"))
 (group "inner" (uuid "00000000-0000-4000-8000-000000000003") (members "00000000-0000-4000-8000-000000000001" "00000000-0000-4000-8000-000000000002"))
 (group "outer" (uuid "00000000-0000-4000-8000-000000000004") (members "00000000-0000-4000-8000-000000000003")))''')
  cs=[{'ref':r,'value':'fixture','physical':True,'footprint':'Test:Fixture','fields':{'MPN':'TEST'},
       'pins':[{'number':'1','net':'V'},{'number':'2','net':'GND'}]} for r in ('U1','C1')]
  put('intent.json',json.dumps({'version':1,'components':cs}))
  put('native.xml','<export><components>'+''.join(f'<comp ref="{r}"><footprint>Test:Fixture</footprint></comp>' for r in ('U1','C1'))+'</components><nets>'+''.join('<net name="/'+n+'">'+''.join(f'<node ref="{r}" pin="{pin}"/>' for r in ('U1','C1'))+'</net>' for pin,n in [('1','V'),('2','GND')])+'</nets></export>')
  put('01_docs/schematic-contract.json',json.dumps({'manifest':'assembly.json'}))
  put('assembly.json',json.dumps({'boards':{'board':{'producer':'imported','source':'import.json','output':'export'}}}))
  put('import.json',json.dumps({'intent':'intent.json'}))
  put('export/native.xml',(self.root/'native.xml').read_text())
  accepted={'assembly':{'boards':{'board':{}}},'subjects':{n:p.sha(self.root/n) for n in ('intent.json','export/native.xml','lib/Fixture.kicad_mod','01_docs/schematic-contract.json','assembly.json','import.json')}}
  put('schematic.json',json.dumps(accepted));put('authority.md','Synthetic test only')
  put(p.CONTRACT,json.dumps({'version':1,'schematic_receipt':'schematic.json','authority':'authority.md'}))
  inputs={'version':1,'boards':{'board':{'intent':'intent.json','netlist':'export/native.xml','footprints':{'Test:Fixture':'lib/Fixture.kicad_mod'},'rules':{'proximity':[{'id':'cap','a':['C1','1'],'b':['U1','1'],'max_mm':5}]}}}}
  put('inputs.json',json.dumps(inputs))
  plan={'version':1,'boards':{'board':{'outline':[30,30],'layers':2,'layer_plan':'synthetic ground plane',
       'placements':{'U1':[10,10,0],'C1':[14,10,0]},'mounts':[[3,3,2,4]],'notes':'synthetic',
       'blocks':[{'id':'local','members':['U1','C1']}]}}}
  put('plan.json',json.dumps(plan));p.build(self.root,'inputs.json','plan.json','out')
 def verify(self):
  with patch.object(p,'upstream',return_value={}):return p.verify(self.root,'inputs.json','plan.json','out')
 def test_native_replay_passes_with_real_cli(self):
  self.assertEqual(self.verify()['checks']['board']['verdict'],'PASS')
 def test_courtyard_boundary_not_drawing_stroke(self):
  # Two rectangular courtyards touching, separated by 30 um, or truly
  # overlapping by 20 um. Ink width must not change the mechanical verdict.
  board=p.pcb.LoadBoard(str(self.root/'out/board.kicad_pcb'))
  cap=board.FindFootprintByReference('C1')
  cap.SetOrientationDegrees(90)
  for width in (.05,.20):
   for f in board.GetFootprints():
    for g in f.GraphicalItems():
     if g.GetLayer()==p.pcb.F_CrtYd:g.SetWidth(round(width*1e6))
   for distance,collides in ((2.0,False),(2.03,False),(1.98,True)):
    cap.SetPosition(p.vector(10+distance,10))
    target=self.root/'boundary.kicad_pcb';p.pcb.SaveBoard(str(target),board)
    parts=p.observe(target)
    with self.subTest(width=width,distance=distance):
     self.assertEqual(parts['U1']['box'],[9,9,11,11])
     self.assertEqual(p.overlap(parts['U1']['box'],parts['C1']['box']),collides)
     # Native pad extents remain physical copper, not shrunk with drawing ink.
     self.assertAlmostEqual(parts['U1']['pads']['1'][0]['box'][0],9.2)
     self.assertEqual(parts['MH1']['box'],[1,1,5,5])
 def test_actual_courtyard_outside_edge_is_not_ink_allowance(self):
  data,plan=p.load(self.root,'inputs.json','plan.json')
  parts=p.observe(self.root/'out/board.kicad_pcb')
  parts['U1']['box']=[-.01,9,1.99,11]
  failures=p.geometry(data['boards']['board'],plan['boards']['board'],parts)['failures']
  self.assertIn('edge:U1',failures)
 def test_grouped_footprints_replay_across_fresh_build(self):
  for i in range(8):
   p.build(self.root,'inputs.json','plan.json','out'+str(i+2))
   self.assertEqual(p.canonical(self.root/'out/board.kicad_pcb'),p.canonical(self.root/('out'+str(i+2))/'board.kicad_pcb'))
 def test_native_move_cannot_be_hidden_by_summary(self):
  path=self.root/'out/board.kicad_pcb';b=p.pcb.LoadBoard(str(path));f=b.FindFootprintByReference('C1')
  f.SetPosition(p.vector(23,10));p.pcb.SaveBoard(str(path),b)
  self.put('out/board.json',json.dumps(p.observe(path)))
  with self.assertRaisesRegex(ValueError,'native placement replay differs'):self.verify()
 def test_forged_preview_fails(self):
  self.put('out/board.svg','<svg>wrong board</svg>')
  with self.assertRaisesRegex(ValueError,'native preview differs'):self.verify()
 def test_plot_timestamp_is_not_geometry(self):
  file=self.root/'out/board.svg'
  file.write_text(p.re.sub(r'date \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', 'date 2001-01-01T00:00:00',file.read_text()))
  self.assertEqual(self.verify()['checks']['board']['verdict'],'PASS')
 def test_changed_schematic_intent_fails(self):
  self.put('intent.json',(self.root/'intent.json').read_text()+'\n')
  with self.assertRaisesRegex(ValueError,'not bound by accepted schematic'):self.verify()
 def test_changed_footprint_fails(self):
  self.put('lib/Fixture.kicad_mod',(self.root/'lib/Fixture.kicad_mod').read_text()+'\n')
  with self.assertRaisesRegex(ValueError,'not bound by accepted schematic'):self.verify()
 def test_other_accepted_intent_cannot_impersonate_board(self):
  self.put('other-intent.json',(self.root/'intent.json').read_text())
  accepted=p.read(self.root/'schematic.json');accepted['subjects']['other-intent.json']=p.sha(self.root/'other-intent.json')
  self.put('schematic.json',json.dumps(accepted))
  inputs=p.read(self.root/'inputs.json');inputs['boards']['board']['intent']='other-intent.json';self.put('inputs.json',json.dumps(inputs))
  with self.assertRaisesRegex(ValueError,'assembly owner'):self.verify()
 def test_forged_checks_fail(self):
  self.put('out/checks.json','{}')
  with self.assertRaisesRegex(ValueError,'stale geometry checks'):self.verify()


if __name__=='__main__':unittest.main()
