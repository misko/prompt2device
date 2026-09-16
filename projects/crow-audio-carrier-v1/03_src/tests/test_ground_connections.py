"""Exactly 35 FULL and one dedicated NONE source-owned GND pad.

VACUITY: this source census cannot prove that a declared dedicated return has
realized copper or survives owner/drop cuts. The paired source-only fixture
below deletes route seeds while the mode census still passes; removing the
NONE declaration then fails. Native return-graph and DRC qualification is owed.

The positive test is run RED on 84db6eb2's unchanged source before repair.
The saved native-fill/DRC experiment separately grades realized copper;
these tests deliberately do not certify connectivity from a source setting.
"""
import copy
from pathlib import Path
import subprocess
import unittest

import pcbnew
import yaml

from test_digital_launch_source import native_geometry
from test_route_source_contract import load_source

SRC=Path(__file__).resolve().parents[1]
ROOT=SRC.parents[2]
BASE='84db6eb2'
# ADR0027 exchanged CM logical references over fixed physical lands. The
# complete physical pad-setting preservation is checked by test_adc_channel_map.
TARGETS={'C_ADC_CM2N.2','C_ADC_CM2P.2','C_ADC_CM6N.2','C_ADC_CM6P.2',
         'R_AUDIO_PD.2','C_VMID1_EXT_1U.2','R_ADC_PD1P.2','U_OE.3',
         'U_TDM_SCH.3','U_LDO.15'}
CLAMP_TARGETS={f'U_ESD{i}.4' for i in range(1,9)}
TARGETS |= CLAMP_TARGETS

# Exactly fourteen additions admitted with the ADC reservations/drop decision.
ADDITIONAL_TARGETS={'C_ADC_CM4P.2','C_ADC_CM4N.2','U_LDO_EN.3','C_VDDA1_10N.2',
                    'C_VMID1_470N.2','C_VMID2_470N.2'} | {f'C_ISO{i}.2' for i in range(1,9)}
TARGETS |= ADDITIONAL_TARGETS
# Keep TARGETS and inspect's (errors, full_selected) tuple compatible with
# callers that grade the existing solid pads. Enumerate NONE independently.
# Native placement970 exposed one starved thermal at this moved clock pad.
# Owning isolated generation976/977 proves solid GND connection clears it,
# with all other source geometry unchanged and DRC0/499unrouted/0parity.
# Missing-target/mode-swap hostile loops below include this pad.
TARGETS |= {'R_MCH_FSYNC_PD.2'}
# These congested exposed pads cannot realize the zone's required two thermal
# spokes. Their explicit routed bonds plus solid local plane connection close
# the native DRC without changing the board-wide zone rule.
TARGETS |= {'U_ISO3.9','U_ISO4.9'}
FULL_TARGETS = TARGETS
NONE_TARGETS = {'C_VDDA2_10N.2'}
MODE_TARGETS = {'full': FULL_TARGETS, 'none': NONE_TARGETS}
ANGLE_TARGETS = {'U_RST2.1':45,'U_RST2.4':45,'C_ADC_CM1N.2':45,
    'C_FILTER2N1.2':0,'U_ISO4.4':45,'C_FILTER2N2.2':30,
    'R_TDM_PD.2':45,'C_FILTER8P1.2':60,'C_PWR.2':45,'U_ISO3.4':45,
    'C_FILTER5P1.2':45,'R_ADC_PD1N.2':60,
    'C_FILTER5P2.2':30,'Q_PRE_EN.2':15,'C_FILTER7N2.2':15}


def frozen(name):
    path=(SRC/name).relative_to(ROOT)
    return yaml.safe_load(subprocess.check_output(['git','show',f'{BASE}:{path}'],
        cwd=ROOT,text=True,timeout=15))

def inspect_modes(floor,pins):
    """Closed project census; the generic consumer still permits glob selectors."""
    errors=[];selected={mode:[] for mode in MODE_TARGETS};all_selected=[];angles={}
    patterns=floor.get('placement',{}).get('patterns')
    if not isinstance(patterns,list):return ['malformed-patterns'],selected
    for row in patterns:
        if not isinstance(row,dict):errors.append('malformed-pattern');continue
        if 'pad_overrides' not in row:continue
        if set(row)!={'match','pad_overrides'}:errors.append('extra-pattern-field')
        refs=row.get('match')
        if not isinstance(refs,list) or not refs or any(
                not isinstance(r,str) or not r or any(c in r for c in '*?[]') for r in refs):
            errors.append('nonexact-ref-selector');continue
        overrides=row['pad_overrides']
        if not isinstance(overrides,list) or not overrides:
            errors.append('malformed-overrides');continue
        for ov in overrides:
            if not isinstance(ov,dict):errors.append('malformed-override');continue
            if 'thermal_spoke_angle_deg' in ov:
                if set(ov)!={'pads','on_net','thermal_spoke_angle_deg'}:
                    errors.append('extra-angle-field')
                value=ov['thermal_spoke_angle_deg']
                if type(value) not in (int,float) or not 0<=value<360:
                    errors.append('invalid-angle')
                if ov.get('on_net')!='GND':errors.append('not-ground-guarded')
                pads=ov.get('pads')
                if not isinstance(pads,list) or not pads:
                    errors.append('empty-pad-selector');continue
                for ref in refs:
                    for number in pads:
                        pin=ref+'.'+str(number)
                        if pin in angles:errors.append('duplicate-angle')
                        angles[pin]=value
                        if pins.get((ref,str(number)))!='GND':errors.append('wrong-native-net:'+pin)
                continue
            if set(ov)!={'pads','on_net','zone_connection'}:errors.append('extra-override-field')
            mode=ov.get('zone_connection')
            valid_mode=isinstance(mode,str) and mode in MODE_TARGETS
            if not valid_mode:errors.append('unknown-mode')
            if ov.get('on_net')!='GND':errors.append('not-ground-guarded')
            pads=ov.get('pads')
            if not isinstance(pads,list) or not pads:
                errors.append('empty-pad-selector');continue
            if any(type(n) not in (str,int) or not str(n) or any(c in str(n) for c in '*?[]') for n in pads):
                errors.append('nonexact-pad-selector');continue
            for ref in refs:
                for number in pads:
                    number=str(number)
                    pin=ref+'.'+number;all_selected.append(pin)
                    if valid_mode:selected[mode].append(pin)
                    if pins.get((ref,number))!='GND':errors.append('wrong-native-net:'+pin)
    if angles!=ANGLE_TARGETS:errors.append('angle-coverage')
    for mode,targets in MODE_TARGETS.items():
        if set(selected[mode])!=targets:
            errors.append('target-coverage' if mode=='full' else 'none-target-coverage')
    if len(all_selected)!=len(set(all_selected)):errors.append('duplicate-target')
    return errors,selected


def inspect(floor,pins):
    errors,selected=inspect_modes(floor,pins)
    return errors,selected['full']

class GroundConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor,cls.route,*_=load_source()
        cls.geometry=native_geometry(cls.floor)
        cls.pins=cls.geometry['pins']

    def test_exact_thirty_five_source_owned_ground_pads(self):
        errors,selected=inspect(self.floor,self.pins)
        self.assertEqual(errors,[])
        self.assertEqual(len(selected),35)

    def test_exact_modes_preserve_full_population_and_one_none(self):
        errors,selected=inspect_modes(self.floor,self.pins)
        self.assertEqual(errors,[])
        self.assertEqual(set(selected['full']),FULL_TARGETS)
        self.assertEqual(len(selected['full']),35)
        self.assertEqual(selected['none'],['C_VDDA2_10N.2'])
        self.assertEqual(inspect(self.floor,self.pins),(errors,selected['full']))

    def test_thermal_angles_have_exact_coverage_and_hostile_controls(self):
        for value in (False, -1, 360, float('nan'), 90):
            bad=copy.deepcopy(self.floor)
            row=next(o for p in bad['placement']['patterns']
                     for o in p.get('pad_overrides',[]) if 'thermal_spoke_angle_deg' in o)
            row['thermal_spoke_angle_deg']=value
            self.assertTrue(inspect_modes(bad,self.pins)[0])
        bad=copy.deepcopy(self.floor)
        row=next(p for p in bad['placement']['patterns']
                 if any('thermal_spoke_angle_deg' in o for o in p.get('pad_overrides',[])))
        bad['placement']['patterns'].append(copy.deepcopy(row))
        self.assertIn('duplicate-angle',inspect_modes(bad,self.pins)[0])

    def test_missing_none_and_every_mode_swap_are_rejected(self):
        for target in FULL_TARGETS | NONE_TARGETS:
            for replacement in ('full','thermal','none',None):
                expected='none' if target in NONE_TARGETS else 'full'
                if replacement==expected:continue
                bad=copy.deepcopy(self.floor)
                ref,number=target.rsplit('.',1)
                extra=None
                for row in bad['placement']['patterns']:
                    if ref not in row.get('match',[]):continue
                    for ov in row.get('pad_overrides',[]):
                        if number in [str(n) for n in ov['pads']]:
                            # Split grouped refs so exactly one target changes mode.
                            row['match'].remove(ref)
                            extra=copy.deepcopy(row);extra['match']=[ref]
                            if not row['match']:bad['placement']['patterns'].remove(row)
                            extra['pad_overrides']=[copy.deepcopy(ov)]
                            if replacement is None:extra['pad_overrides'][0].pop('zone_connection')
                            else:extra['pad_overrides'][0]['zone_connection']=replacement
                            break
                    else:continue
                    break
                self.assertIsNotNone(extra,('missing mutation target',target))
                bad['placement']['patterns'].append(extra)
                self.assertTrue(inspect_modes(bad,self.pins)[0],(target,replacement))
        bad=copy.deepcopy(self.floor)
        bad['placement']['patterns']=[row for row in bad['placement']['patterns']
            if row.get('match')!=['C_VDDA2_10N'] or 'pad_overrides' not in row]
        self.assertIn('none-target-coverage',inspect_modes(bad,self.pins)[0])

    def test_none_selector_and_conflicting_pattern_controls(self):
        good=next(row for row in self.floor['placement']['patterns']
                  if row.get('match')==['C_VDDA2_10N'] and 'pad_overrides' in row)
        mutations=[
            (lambda r:None,'duplicate-target'),
            (lambda r:r.update(match='C_VDDA2_10N'),'nonexact-ref-selector'),
            (lambda r:r.update(match=['C_VDDA*']),'nonexact-ref-selector'),
            (lambda r:r.update(match=[]),'nonexact-ref-selector'),
            (lambda r:r.update(match=['C_VDDA2_10N','C_VDDA2_10N']),'duplicate-target'),
            (lambda r:r['pad_overrides'][0].update(pads=['*']),'nonexact-pad-selector'),
            (lambda r:r['pad_overrides'][0].update(pads='2'),'empty-pad-selector'),
            (lambda r:r['pad_overrides'][0].update(pads=[]),'empty-pad-selector'),
            (lambda r:r['pad_overrides'][0].update(pads=['2','2']),'duplicate-target'),
            (lambda r:r['pad_overrides'][0].update(pads=['1','2']),'wrong-native-net:C_VDDA2_10N.1'),
            (lambda r:r['pad_overrides'][0].update(on_net='3V3_ADC'),'not-ground-guarded'),
            (lambda r:r['pad_overrides'][0].update(zone_connection='full'),'duplicate-target'),
            (lambda r:r.update(match=['C_VDDA1_10N']),'none-target-coverage'),
            (lambda r:r.update(attrs=['dnp']),'extra-pattern-field'),
        ]
        for mutate,expected in mutations:
            bad=copy.deepcopy(self.floor);row=copy.deepcopy(good);mutate(row)
            bad['placement']['patterns'].append(row)
            self.assertIn(expected,inspect_modes(bad,self.pins)[0],expected)
        for value in ('typo','NONE','thermal','',None,False,0,[],{}):
            bad=copy.deepcopy(self.floor)
            row=next(r for r in bad['placement']['patterns'] if r==good)
            row['pad_overrides'][0]['zone_connection']=value
            self.assertIn('unknown-mode',inspect_modes(bad,self.pins)[0],repr(value))
        badpins=dict(self.pins);badpins[('C_VDDA2_10N','2')]='3V3_ADC'
        self.assertIn('wrong-native-net:C_VDDA2_10N.2',inspect_modes(self.floor,badpins)[0])

    def test_mode_census_declared_realized_return_blind_spot(self):
        # Source settings still pass if every actual return seed is absent.
        # Native return graph/cuts, not this census, own realized connectivity.
        disconnected=copy.deepcopy(self.route)
        disconnected['prep']['seed_stubs']['stubs']=[]
        self.assertEqual(inspect_modes(self.floor,self.pins)[0],[])
        self.assertEqual(disconnected['prep']['seed_stubs']['stubs'],[])
        bad=copy.deepcopy(self.floor)
        for row in bad['placement']['patterns']:
            if row.get('match')==['C_VDDA2_10N'] and 'pad_overrides' in row:
                row['pad_overrides'][0]['zone_connection']='full'
        self.assertTrue(inspect_modes(bad,self.pins)[0])

    def test_real_old_source_is_rejected(self):
        self.assertIn('target-coverage',inspect(frozen('floorplan.yaml'),self.pins)[0])

    def test_wrong_net_broad_ref_and_extra_pad_are_rejected(self):
        good={'match':['U_OE'],'pad_overrides':[{'pads':['3'],'on_net':'GND','zone_connection':'full'}]}
        for mutate,expected in [
            (lambda r:None,'duplicate-target'),
            (lambda r:r['pad_overrides'][0].update(on_net='3V3_ADC'),'not-ground-guarded'),
            (lambda r:r.update(match=['U_*']),'nonexact-ref-selector'),
            (lambda r:r['pad_overrides'][0].update(pads=['2','3']),'wrong-native-net:U_OE.2'),
            (lambda r:r['pad_overrides'][0].update(clearance=0),'extra-override-field')]:
            bad=copy.deepcopy(self.floor);row=copy.deepcopy(good);mutate(row)
            bad['placement']['patterns'].append(row)
            self.assertIn(expected,inspect(bad,self.pins)[0])

    def test_no_required_solid_connection_can_be_omitted(self):
        for target in TARGETS:
            bad=copy.deepcopy(self.floor)
            for row in bad['placement']['patterns']:
                if 'pad_overrides' not in row:continue
                ref=target.rsplit('.',1)[0]
                if ref in row['match']:row['match'].remove(ref)
            self.assertIn('target-coverage',inspect(bad,self.pins)[0],target)

    def test_lt_quiet_returns_remain_isolated_from_direct_ep_bonds(self):
        from test_regulator_source import QUIET_PINS, quiet_errors, connected_reach
        self.assertEqual(quiet_errors(self.floor,self.route,self.geometry),[])
        for pin in QUIET_PINS:
            self.assertNotIn('U_LDO.15',connected_reach(self.route,self.geometry,pin))
            self.assertIn('C_LDO_OUT.2',connected_reach(self.route,self.geometry,pin))
        for pin in ('U_LDO.7','U_LDO.10','U_LDO.11'):
            self.assertIn('U_LDO.15',connected_reach(self.route,self.geometry,pin))

    def test_targets_are_real_smd_ground_lands_on_declared_sides(self):
        # Narrow side-aware witness: the shared signal-path native_geometry
        # helper plus this explicit native witness establishes all thirty-three top lands.
        from test_local_placement_source import source_builder
        from source_inventory import parse_netlist
        project=SRC.parent
        comps,pins,_=parse_netlist(project/self.floor['project']['netlist'])
        source=source_builder(self.floor)
        board=pcbnew.BOARD()
        board.SetCopperLayerCount(4)
        for ref in sorted({pin.split('.')[0] for pin in TARGETS}):
            lib,name=comps[ref][0].split(':')
            directory=(project/'03_src/lib/crow_audio_carrier.pretty' if lib=='crow_audio_carrier'
                       else Path('/usr/share/kicad/footprints')/(lib+'.pretty'))
            fp=pcbnew.FootprintLoad(str(directory),name)
            self.assertIsNotNone(fp,ref)
            board.Add(fp)  # Keep the parent alive before and throughout Flip.
            x,y,rot,_=source.initial_pose(ref)
            fp.SetOrientationDegrees(rot)
            fp.SetPosition(pcbnew.VECTOR2I(round(x*1e6),round(y*1e6)))
            if source.place_cfg.get('sides',{}).get(ref,'top')=='bottom':
                fp.Flip(fp.GetPosition(),False)
            for pin in sorted(p for p in TARGETS if p.split('.')[0]==ref):
                number=pin.split('.')[1]
                pads=[p for p in fp.Pads() if p.GetNumber()==number]
                self.assertEqual(len(pads),1,pin)
                self.assertEqual(pads[0].GetAttribute(),pcbnew.PAD_ATTRIB_SMD,pin)
                expected=pcbnew.F_Cu
                self.assertTrue(pads[0].IsOnLayer(expected),pin)
                self.assertFalse(pads[0].IsOnLayer(pcbnew.B_Cu),pin)
                self.assertEqual(pins[(ref,number)],'GND',pin)

if __name__=='__main__':unittest.main(verbosity=2)
