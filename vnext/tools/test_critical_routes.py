"""Native acceptance/recovery controls; synthetic fixtures are not board approval."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import critical_routes as c
import placement as p
import routing as r
import test_placement


class CriticalRoutes(unittest.TestCase):
    def setUp(self):
        fixture = test_placement.NativeReplay(methodName='test_native_replay_passes_with_real_cli')
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        self.root = fixture.root; self.put = fixture.put; self.output='out'
        self.board = p.pcb.LoadBoard(str(self.root/'out/board.kicad_pcb'))
        for net, points in [('V', [(9.5,10),(9.5,9),(13.5,9),(13.5,10)]),
                            ('GND', [(10.5,10),(10.5,11),(14.5,11),(14.5,10)])]:
            for start, end in zip(points, points[1:]):
                t=p.pcb.PCB_TRACK(self.board);t.SetStart(p.vector(*start));t.SetEnd(p.vector(*end))
                t.SetWidth(200000);t.SetLayer(p.pcb.F_Cu)
                t.SetNet(self.board.FindNet('/'+net));self.board.Add(t)
        self.put('trial.kicad_pro',json.dumps({'board':{'design_settings':{'rule_severities':{}}}}))
        self.save()
        self.put('engineering.md','Synthetic local supply and return fixture; not product approval.')
        contract=p.read(self.root/p.CONTRACT);contract.update(version=2,critical_routes='critical-scope.json')
        self.put(p.CONTRACT,json.dumps(contract))
        self.scope={'version':1,'boards':{'board':{'reason':'Local supply/return feasibility',
            'duties':[{'id':net,'terminals':[{'ref':ref,'pin':pin} for ref in ('U1','C1')],
                       'requirements':['Local connection and reviewed current/return allowance']}
                      for net,pin in [('supply','1'),('return','2')]]}}}
        self.trials={'version':1,'boards':{'board':{'native':{'source':'trial.kicad_pcb','project':'trial.kicad_pro'},
            'duties':{net:{'verdict':'PASS','evidence':['engineering.md'],'rationale':'Synthetic checked local fixture'}
                      for net in ('supply','return')}}}}
        self.sync()

    def save(self):
        p.pcb.SaveBoard(str(self.root/'trial.kicad_pcb'),self.board)

    def sync(self):
        self.put('critical-scope.json',json.dumps(self.scope));self.put('trials.json',json.dumps(self.trials))
        with patch.object(p,'upstream',return_value={}):
            verified=p.verify(self.root,'inputs.json','plan.json',self.output)
        subjects=dict(verified['subjects'])
        for name in ('critical-scope.json','trials.json','trial.kicad_pcb','trial.kicad_pro','engineering.md'):
            subjects[name]=p.sha(self.root/name)
        self.review=dict(schema=1,stage='KICAD-PLACEMENT',verdict='PASS',author='fixture author',
                         reviewer='fixture independent reviewer',inputs='inputs.json',plan='plan.json',
                         output=self.output,critical_routes='trials.json',subjects=subjects,
                         checks={k:dict(verdict='PASS',rationale='Synthetic test only',evidence=['engineering.md'])
                                 for k in p.CRITERIA})
        self.name='08_reviews/2026-10-20-critical-placement.md'
        self.put(self.name,'```json\n'+json.dumps(self.review)+'\n```\n')
        # Do not retain mutable SWIG native/net pointers across other board loads.
        self.board=p.pcb.LoadBoard(str(self.root/'trial.kicad_pcb'))

    def gate(self):
        return c.verify(self.root,self.review,{'board':'out/board.kicad_pcb'})

    def test_valid_native_trial_and_placement_certificate(self):
        self.gate()
        with patch.object(p,'upstream',return_value={}):
            receipt=p.certificate(self.root,self.name)
        self.assertEqual(receipt['role'],'placement_reviewed')
        self.assertEqual(set(receipt['critical_routes_tools']),
                         {'critical_routes.py','routing.py','routing_geometry.py'})

    def test_missing_scope_and_version_downgrade(self):
        contract=p.read(self.root/p.CONTRACT);contract['version']=1
        self.put(p.CONTRACT,json.dumps(contract))
        with self.assertRaisesRegex(ValueError,'version2'):self.gate()

    def test_missing_trial(self):
        del self.review['critical_routes']
        with self.assertRaisesRegex(ValueError,'manifest required'):self.gate()

    def test_changed_bound_native_and_engineering(self):
        for name in ('trial.kicad_pcb','engineering.md','critical-scope.json'):
            old=(self.root/name).read_text();self.put(name,old+'\n')
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError,'unbound'):self.gate()
            self.put(name,old)

    def test_omitted_board_and_duty(self):
        del self.trials['boards']['board']['duties']['return'];self.sync()
        with self.assertRaisesRegex(ValueError,'duty coverage'):self.gate()
        self.trials['boards']={};self.sync()
        with self.assertRaisesRegex(ValueError,'board coverage'):self.gate()

    def test_wrong_trial_placement(self):
        self.board.FindFootprintByReference('C1').SetPosition(p.vector(16,10));self.save();self.sync()
        with self.assertRaisesRegex(ValueError,'placement/pads/nets'):self.gate()

    def test_same_net_name_is_not_a_connection_and_shared_return_is_checked(self):
        for track in list(self.board.GetTracks()):
            if track.GetNetname()=='/GND':self.board.Remove(track)
        self.save();self.sync()
        with self.assertRaisesRegex(ValueError,'not routed'):self.gate()

    def test_wrong_net_terminal_rejected(self):
        self.scope['boards']['board']['duties'][0]['terminals'][1]['pin']='2';self.sync()
        with self.assertRaisesRegex(ValueError,'different or missing nets'):self.gate()

    def test_actual_foreign_copper_collision(self):
        track=p.pcb.PCB_TRACK(self.board);track.SetStart(p.vector(12,8));track.SetEnd(p.vector(12,12))
        track.SetWidth(200000);track.SetLayer(p.pcb.F_Cu);track.SetNet(self.board.FindNet('/GND'))
        self.board.Add(track);self.save();self.sync()
        with self.assertRaisesRegex(ValueError,'physical DRC'):self.gate()

    def test_old_ground_bore_under_positive_pad(self):
        via=p.pcb.PCB_VIA(self.board);via.SetPosition(p.vector(13.5,10));via.SetWidth(600000)
        via.SetDrill(300000);via.SetLayerPair(p.pcb.F_Cu,p.pcb.B_Cu)
        via.SetNet(self.board.FindNet('/GND'));self.board.Add(via);self.save();self.sync()
        with self.assertRaisesRegex(ValueError,'physical DRC|solder land'):self.gate()

    def test_rejected_engineering_is_not_overridden_by_connectivity(self):
        self.trials['boards']['board']['duties']['supply']['verdict']='FAIL';self.sync()
        with self.assertRaisesRegex(ValueError,'engineering review'):self.gate()

    def test_explicit_no_critical_block_is_not_implicit_unknown(self):
        self.scope['boards']['board']['duties']=[];self.trials['boards']['board']['duties']={};self.sync()
        with self.assertRaisesRegex(ValueError,'independent disposition'):self.gate()
        self.trials['boards']['board']['not_applicable_reason']='Synthetic noncritical variant only';self.sync()
        self.gate()

    def test_native_drc_exclusions_rejected(self):
        settings=p.read(self.root/'trial.kicad_pro');settings['board']['design_settings']['drc_exclusions']=['fake']
        self.put('trial.kicad_pro',json.dumps(settings));self.sync()
        with self.assertRaisesRegex(ValueError,'exclusions'):self.gate()

    def test_noncritical_open_is_not_complete_board_routing_requirement(self):
        self.scope['boards']['board']['duties']=self.scope['boards']['board']['duties'][:1]
        del self.trials['boards']['board']['duties']['return']
        for track in list(self.board.GetTracks()):
            if track.GetNetname()=='/GND':self.board.Remove(track)
        self.save();self.sync();self.gate()

    def test_unfilled_zone_cannot_claim_demonstrated_copper(self):
        zone=p.pcb.ZONE(self.board);zone.SetLayer(p.pcb.F_Cu);zone.SetNet(self.board.FindNet('/GND'))
        zone.SetLocalClearance(200000);outline=zone.Outline();outline.NewOutline()
        for x,y in [(8,8),(17,8),(17,13),(8,13)]:outline.Append(int(x*1e6),int(y*1e6))
        self.board.Add(zone);self.save();self.sync()
        with self.assertRaisesRegex(ValueError,'stale critical trial copper fill'):self.gate()

    def test_supporting_checker_identity_is_part_of_receipt(self):
        with patch.object(p,'upstream',return_value={}):
            before=p.certificate(self.root,self.name)
            changed=dict(before['critical_routes_tools']);changed['routing_geometry.py']='changed-tool'
            with patch.object(c,'tool_identities',return_value=changed):
                after=p.certificate(self.root,self.name)
        self.assertNotEqual(before,after)

    def test_real_placement_backtrack_requires_new_trial_and_review(self):
        self.gate();old=copy.deepcopy(self.review)
        plan=p.read(self.root/'plan.json');plan['boards']['board']['placements']['C1']=[16,10,0]
        self.put('plan.json',json.dumps(plan));p.build(self.root,'inputs.json','plan.json','successor')
        self.output='successor'
        self.review['output']='successor'
        with self.assertRaisesRegex(ValueError,'placement/pads/nets'):
            c.verify(self.root,self.review,{'board':'successor/board.kicad_pcb'})
        # Rebuild actual copper at the successor geometry, not just a receipt hash.
        self.board.FindFootprintByReference('C1').SetPosition(p.vector(16,10))
        for track in self.board.GetTracks():
            for getter,setter in ((track.GetStart,track.SetStart),(track.GetEnd,track.SetEnd)):
                xy=getter()
                if xy.x>12000000:setter(p.pcb.VECTOR2I(xy.x+2000000,xy.y))
        self.save();self.sync()
        c.verify(self.root,self.review,{'board':'successor/board.kicad_pcb'})
        with self.assertRaisesRegex(ValueError,'unbound'):
            c.verify(self.root,old,{'board':'successor/board.kicad_pcb'})


if __name__=='__main__':unittest.main()
