#!/usr/bin/env python3
"""ADR0025 fixed-source topology and bounded architecture arithmetic.

No time integration, sweep, investigation attempt, or physical acceptance.
The source state is a coherent electrical correction with physical integration
still open. Engineering envelopes are explicit, not vendor timing guarantees.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import yaml

PROJECT = Path(__file__).resolve().parents[1]
REMOVED = {'U_AFE9','C_OPA9','C_RAW_HOLD','R_OPA_FEED','C_OPA_BULK2',
           'R_OPA_BLEED3','R_LDO_TOP','R_LDO_BOT','C_LDO_NR1','C_LDO_NR2',
           'C_LDO_NR3',*(f'R_VMID{n}_{s}' for n in (1,2) for s in ('IN','ISO')),
           'C_VMID1_BUF','C_VMID2_BUF'}
LDO_PINS = {'1':'5V_LDO_HOLD','2':'5V_LDO_HOLD','3':'5V_LDO_HOLD',
            '4':'','5':'LDO_EN','6':'','7':'GND','8':'5V_LDO_HOLD',
            '9':'LDO_NR','10':'GND','11':'GND','12':'3V3_ADC',
            '13':'3V3_ADC','14':'3V3_ADC','15':'GND'}

def validate(pins, values):
    """Exact electrical source contract; fail hostile rail/pin/value changes."""
    from check_power_source import POWER_PINS,POWER_VALUES
    # Preserve every unchanged power guard when replacing only the selected
    # converter/rail/reference entries. The LT branch must not bypass them.
    changed={'U_LDO','R_OPA_BLEED1','R_OPA_BLEED2'}|REMOVED
    for ref,wanted in POWER_PINS.items():
        if ref not in changed and pins.get(ref)!=wanted:raise ValueError(f'{ref}: retained power pin contract')
    for ref,wanted in POWER_VALUES.items():
        if ref not in changed and values.get(ref)!=wanted:raise ValueError(f'{ref}: retained power value contract')
    owners={ref for ref,row in pins.items() if '12V_BUCK_IN' in row.values()}
    if owners!={'D_BUCK_IN','U_BUCK','C_BUCK_IN','C_BUCK_IN2','C_BUCK_IN3'}:
        raise ValueError('upstream reverse-isolated input census')
    if len(values)!=333 or sum(len(row) for row in pins.values())!=985:
        raise ValueError('shared-rail component/pin census changed')
    for pin in ('5','9','31'):
        if pins['U_ADC'].get(pin)!='3V3_ADC':raise ValueError('ADC must share the amplifier rail')
    if REMOVED.intersection(values):
        raise ValueError(f'old split-rail/reference components remain: {sorted(REMOVED.intersection(values))}')
    if values.get('U_LDO') != 'LT3041ADE#TRPBF' or pins.get('U_LDO') != LDO_PINS:
        raise ValueError('exact LT3041 identity or pin map')
    if any(net == '5V_OPA' or net.startswith(('VMID1_RAW','VMID2_RAW','VMID1_BUF','VMID2_BUF','VMID1_IN','VMID2_IN'))
           for row in pins.values() for net in row.values()):
        raise ValueError('retired independent amplifier/reference rail')
    required = {'R_OPA_BLEED1':({'1':'3V3_ADC','2':'OPA_BLEED_A'},'100'),
                'R_OPA_BLEED2':({'1':'OPA_BLEED_A','2':'GND'},'100'),
                'R_LDO_SET':({'1':'LDO_NR','2':'GND'},'33k')}
    for ref in ('C_LDO_OUT','C_OPA_BULK'):
        required[ref]=({'1':'3V3_ADC','2':'GND'},'47uF')
    required['C_LDO_IN']=({'1':'5V_LDO_HOLD','2':'GND'},'47uF')
    for n in (4,5):required[f'C_LDO_NR{n}']=({'1':'LDO_NR','2':'GND'},'1nF')
    for n in (1,2):
        required[f'R_VMID{n}_TOP']=({'1':'3V3_ADC','2':f'VMID{n}_EXT'},'1k')
        required[f'R_VMID{n}_BOT']=({'1':f'VMID{n}_EXT','2':'GND'},'1k')
    afe={ref for ref in values if ref.startswith('U_AFE')}
    if afe != {f'U_AFE{n}' for n in range(1,9)}:raise ValueError('eight dual amplifier census')
    for n in range(1,9):
        if values[f'U_AFE{n}']!='OPA2320AIDR' or pins[f'U_AFE{n}']['8']!='3V3_ADC':
            raise ValueError('amplifier must share ADC supply')
        required[f'C_OPA{n}']=({'1':'3V3_ADC','2':'GND'},'100nF')
        for leg in ('P','N'):
            required[f'R_B{n}{leg}']=({'1':f'BIAS_{leg}{n}','2':f'VMID{1 if n<=4 else 2}_EXT'},'100k')
            required[f'R_ADC_PD{n}{leg}']=({'1':f'ADC{n}{leg}','2':'GND'},'10k')
            required[f'C_ADC_CM{n}{leg}']=({'1':f'ADC{n}{leg}','2':'GND'},'1nF')
    for ref,(connection,value) in required.items():
        if pins.get(ref)!=connection or values.get(ref)!=value:raise ValueError(f'{ref}: shared-rail contract')
    # Existing source topology checker owns all channel feedback/filter maps.
    from check_analog_filter_topology import validate as analog_validate,TopologyError
    try:analog_validate(pins,values)
    except TopologyError as exc:raise ValueError(str(exc)) from exc
    return {'channels':8,'amplifiers':8,'pulldowns':16,'passive_bias_banks':2,
            'LDO_connected_pins':13,'LDO_explicit_NC_pins':2,'removed_refs':len(REMOVED),
            'independent_filter_shunts':32,'components':333,'pins':985}

def calculate(cap_nominal_uF=1109.36, bleed_ohm=200., adc_bleed_ohm=10000.,
              direct_min_uF=32.3595, startup_available_A=1., sink_load_A=.23,
              series_ohm=10000., pod_max_V=5.5, leakage_A=1e-6,
              falling_load_A=.315, switch_charge_C=50e-12, return_error_V=.1,
              output_tracking_error_V=.05):
    args=(cap_nominal_uF,bleed_ohm,adc_bleed_ohm,direct_min_uF,startup_available_A,sink_load_A,series_ohm,pod_max_V,leakage_A,falling_load_A,switch_charge_C,return_error_V,output_tracking_error_V)
    if not all(math.isfinite(v) and v>0 for v in args) or startup_available_A<=sink_load_A or cap_nominal_uF<940:
        raise ValueError('finite positive architecture bounds required')
    qmax=pod_max_V+leakage_A*105000
    barrier=3.4
    incoming=16*max(0,pod_max_V+qmax-barrier)/(series_ohm*.95)
    bleed=barrier/(bleed_ohm*1.05)
    # At the rail barrier each passive VMID node is below the rail, hence its
    # top resistor is a sink, not another positive rail source. No credit taken.
    bias_peak=(barrier/1000+8*(pod_max_V+qmax)/95000)/(2/1000+8/95000)
    margin=bleed-incoming-100e-6  # extra total unexplained-current reserve
    # Fastest external dump: ignore beneficial FILT backfill and all extra
    # direct caps. Two47uF ceramics alone, each with declared .34425 factor.
    rail_tau=.95*direct_min_uF*1e-6
    adc_tau=adc_bleed_ohm*1.01*1e-9*1.05
    # Charge a full0.30A additional rail sink plus LT3041's up15mA reverse
    # overshoot recovery current. This is an explicit load envelope, not zero
    # reverse discharge. At x=Vrail+0.3 the off-node derivative must point in.
    rail_slew=(3.4/.95+falling_load_A)/(direct_min_uF*1e-6)
    off_slope_margin=1/adc_tau-1/rail_tau
    off_intercept_margin=.3/adc_tau-falling_load_A/(direct_min_uF*1e-6)
    filter_lag=10*1.05*(30e-9*1.05+1e-9*1.05)*rail_slew
    charge_step=switch_charge_C/(1e-9*.95)
    # No unconditional ideal output clamp claim: reserve50mV for amplifier
    # rail tracking/overshoot. This declared engineering envelope requires a
    # physical supply-removal/brownout/restart capture before energization acceptance.
    signal_error=filter_lag+charge_step+return_error_V+output_tracking_error_V
    cap_hi=940*1.2*1.3*1.1+(cap_nominal_uF-940)*1.1*1.15
    charge=cap_hi*1e-6*3.4/(startup_available_A-sink_load_A)
    # A deliberately conservative sum, not identification of the two events
    # as sequential silicon behavior. SET has no fast-start boost selected.
    set_99=33000*1.003*2e-9*1.05*math.log(100)
    vleg=1.2/math.sqrt(2)
    ipk=math.sqrt(2)*1.2/3000 + vleg/9500 + 2*math.pi*20000*vleg*(30e-9*1.05+1e-9*1.05)
    audio_supply=16*ipk/math.pi
    static_pd=16*1.7/9500
    steady=.15+16*.0017+audio_supply+static_pd+3.4/190+3.4/999
    buck_steady=steady+.025+.002+8*.00013
    thermal=(5.15-3.23)*steady+5.15*.025
    # Separate signed1uA/leg engineering screen; does not claim the room-temp
    # R82 insulation specification is valid at every outdoor/lifetime state.
    vlo=3.23*.4995-8*leakage_A*500.5
    vhi=3.35*.5005+8*leakage_A*500.5
    # A-grade full-temperature SET current +/-1%, resistor initial0.1%
    # plus25ppm/C over75C rounded to0.3%, and +/-2mV offset.
    regulated_lo=99e-6*33000*.997-.002
    regulated_hi=101e-6*33000*1.003+.002
    result={
      'rail_barrier_V':barrier,'coupling_charge_voltage_envelope_V':qmax,
      'all16_injection_at_barrier_A':incoming,'bleed_at_barrier_min_A':bleed,
      'rail_injection_margin_A':margin,'passive_bias_upper_at_rail_barrier_V':bias_peak,
      'input_positive_current_max_A':(pod_max_V+qmax)/(series_ohm*.95),
      'input_negative_current_max_A':qmax/(series_ohm*.95),
      'direct_rail_dump_tau_min_us':rail_tau*1e6,'isolated_ADC_tau_max_us':adc_tau*1e6,
      'falling_rail_additional_sink_envelope_A':falling_load_A,
      'off_barrier_slope_margin_per_s':off_slope_margin,
      'off_barrier_intercept_margin_V_per_s':off_intercept_margin,
      'rail_fall_slew_envelope_V_per_s':rail_slew,
      'switch_charge_engineering_budget_C':switch_charge_C,
      'return_error_engineering_budget_V':return_error_V,
      'amplifier_output_tracking_engineering_budget_V':output_tracking_error_V,
      'combined_signal_relative_error_budget_V':signal_error,
      'regulated_A_grade_voltage_window_V':[regulated_lo,regulated_hi],
      'on_filter_rail_lag_bound_V':filter_lag,'charge_all_life_upper_uF':cap_hi,
      'startup_charge_and_SET99_budget_ms':1000*(charge+set_99),
      'startup_current_is_engineering_charge_budget':True,
      'ADC_reference_and_logic_reserve_A':.15,'AFE_IQ_max_A':16*.0017,
      'audio_supply_triangle_bound_A':audio_supply,'pulldown_DC_load_A':static_pd,
      'shared_3V3_steady_A':steady,'local_5V_steady_A':buck_steady,
      'LDO_dissipation_W':thermal,'reference_board_TJ_at_85C_C':85+37*thermal,
      'reference_DC_engineering_window_V':[vlo,vhi],
      'normal_leg_signal_window_V':[vlo-vleg,vhi+vleg],
      'added_shunt_gain_lower':9500/(9500+.3),
      'upstream_trunk_budget_A':.8+.30*5.15/(.85*9.86)+.001,
      'header_floor_V':11.4-1.2*(1*.2+.1*2.2),
      'switch_off_injection_typical_V':5e-12/(1e-9*.95),
      'checks':{
        'all16_rail_barrier':margin>0 and bias_peak<barrier,
        'OPA_input_current':(pod_max_V+qmax)/(series_ohm*.95)<.010,
        'off_ADC_inward_barrier_derivative':off_slope_margin>0 and off_intercept_margin>0,
        'combined_relative_pin_error_below_0p3V':signal_error<.3,
        'regulated_voltage_allocation':regulated_lo>=3.23 and regulated_hi<=3.35,
        'startup_charge_budget_10ms':charge+set_99<.010,
        'steady_3V3_allocation':steady<=.23,
        'steady_5V_allocation':buck_steady<=.30,
        'reference_DC_window':vlo>=1.60 and vhi<=1.70,
        'header_floor':11.4-1.2*(.2+.22)>=10.8}
    }
    return result

def source_receipt(pins=None,values=None):
    from check_power_source import capacitance_inventory,source_power_maps
    if pins is None:
        sys.path.insert(0,str(PROJECT/'03_src/tests'))
        from source_inventory import inventory
        comps,flat,_=inventory();pins,values=source_power_maps(comps,flat)
    coverage=validate(pins,values)
    for folder in ('LT3041ADE-TRPBF','RT0603BRD071KL','RT0603BRD0733KL'):
        part=yaml.safe_load((PROJECT/'02_parts'/folder/'part.yaml').read_text());ds=part['datasheet']
        if hashlib.sha256((PROJECT/'02_parts'/folder/ds['local']).read_bytes()).hexdigest()!=ds['sha256']:
            raise ValueError(f'{folder}: selected primary bytes changed')
    inv=capacitance_inventory(pins,values)
    result=calculate(cap_nominal_uF=inv['conservative_charge_inventory_nominal_uF'])
    result.update(schema=1,kind='carrier-protection-architecture-source',adr='0025',
      input_authority='live JSX source; native stale and unreviewed',coverage=coverage,
      capacitor_inventory=inv,status='PASS_BOUNDED_ELECTRICAL_SOURCE' if all(result['checks'].values()) else 'FAIL_ELECTRICAL_SOURCE',
      generation_admitted=False,physical_qualified=False,
      before_generation=['Reconcile and grade LT3041 local placement/return/OUTS/dual-output-cap geometry; old TPS-specific routes were removed, not transferred',
                         'Update remaining historical source-geometry fixtures, rebuild native under owner permission, then independent pin/footprint/placement/parity review'],
      prototype_validation=['Supply and signal relative-slew captures across start/removal/brownout/rapid restart; shared-rail lower-bound load/discharge and1A charge budget',
                            'OPA common/differential loop stability and full8channel1.2Vrms distortion/crosstalk with10k pulldowns and passive bias',
                            'LT3041 effective capacitor ESR/ESL, Kelvin routing, SET noise, hot thermal behavior and exact supply ramp endpoints',
                            'TMUX charge injection is typical; verify pin overshoot with layout return impedance, without using switch timing as the protection barrier'],
      investigation_launched=False)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    result=source_receipt();print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if all(result['checks'].values()) else 1

if __name__=='__main__':raise SystemExit(main())
