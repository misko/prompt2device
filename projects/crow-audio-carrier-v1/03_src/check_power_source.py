#!/usr/bin/env python3
"""Exact source power-state screens, not prototype qualification.

Backend gap: shared E-CAP does not own a filtered large-bank LDO startup,
reverse-current or unpowered analog interface contract. This project adapter
pins topology and computes explicit conservative scenarios; manufacturer
typical-only timing and unavailable partial-VDD guarantees remain named OWED
rows. PASS here means these conditional screens pass, not all-fault immunity.
VACUITY: identical netlist with a poorly soldered EP or a slower-than-budgeted
supervisor still passes arithmetic. Physical captures and thermal tests own it.
"""
import hashlib
import json
import math
from pathlib import Path
import re
import yaml
from check_analog_filter_topology import parse_native_netlist

PROJECT = Path(__file__).resolve().parents[1]

def capacitance_inventory(pins, values):
    """Inventory actual source caps; this is NOT an LDO stability equivalent.

    Internal regulator/reference and divider caps are charged through distinct
    paths. Counting their full values is a conservative charge-inventory screen,
    not a claim that every capacitor is directly in the external LDO control loop.
    The reset timing capacitor is included as an additional conservative load.
    """
    groups = {"direct_3V3_ADC": {"3V3_ADC"},
              "positive_FILT_banks": {"FILT1P", "FILT2P"},
              "internal_ADC_outputs": {"LDO_A_FILT", "LDO_D_FILT", "VMID1", "VMID2"},
              "external_VMID_dividers": {"VMID1_EXT", "VMID2_EXT"},
              "driven_filter_shunts": {f"FILTER{n}{leg}" for n in range(1,9) for leg in "PN"},
              "reset_timing": {"RESET_C", "RESET_RC"}}
    rows = []
    for ref, terminals in sorted(pins.items()):
        if not ref.startswith("C_"):
            continue
        hits = [name for name, nets in groups.items() if nets.intersection(terminals.values())]
        if not hits:
            continue
        if len(hits) != 1:
            raise ValueError(f"{ref}: cross-group capacitor needs explicit analysis")
        value = values[ref].replace("µ", "u").replace("μ", "u")
        match = re.fullmatch(r"([0-9.]+)([pnum]?)F", value)
        if not match:
            raise ValueError(f"{ref}: unsupported capacitance {value!r}")
        nominal = float(match[1]) * {"p": 1e-6, "n": 1e-3, "u": 1, "m": 1e3, "": 1e6}[match[2]]
        rows.append({"ref": ref, "group": hits[0], "nominal_uF": nominal,
                     "pins": terminals})
    totals = {name: sum(r["nominal_uF"] for r in rows if r["group"] == name)
              for name in groups}
    bulk = sum(r["nominal_uF"] for r in rows if r["ref"] in {"C_FILT1_470U", "C_FILT2_470U"})
    nominal = sum(totals.values())
    return {"components": rows, "group_nominal_uF": totals,
            "conservative_charge_inventory_nominal_uF": nominal,
            "initial_engineering_upper_uF": bulk * 1.2 + (nominal - bulk) * 1.1 * 1.15,
            "upper_model_assumptions": "Initial bulk +20%; ceramics +10% tolerance and +15% temperature. Excludes reflow/endurance drift, parasitics and actual DC-bias minima; NOT an all-life bound or loop-stability equivalent."}


POWER_PINS = {
    "D_BUCK_IN": {"1":"12V_BUCK_IN","2":"12V_PROTECTED"},
    "U_BUCK": {"1":"5V_BUCK","2":"12V_BUCK_IN","3":"12V_BUCK_IN","4":"GND","5":"BUCK_SW","6":"BUCK_BST"},
    **{r:{"1":"12V_BUCK_IN","2":"GND"} for r in ("C_BUCK_IN","C_BUCK_IN2","C_BUCK_IN3")},
    "U_LDO": {"1":"3V3_ADC","2":"3V3_ADC","3":"LDO_FB","4":"GND","5":"","6":"GND",
              "7":"LDO_EN","8":"LDO_NR","9":"5V_LDO_HOLD","10":"5V_LDO_HOLD","11":"GND"},
    "D_HOLD": {"1":"5V_LDO_FEED","2":"5V_BUCK"},
    "Q_PRE": {"1":"PRE_GATE","2":"5V_LDO_FEED","3":"5V_LDO_HOLD"},
    "Q_PRE_EN": {"1":"PWR_EN","2":"GND","3":"PRE_GATE"},
    "R_PRE": {"1":"5V_LDO_FEED","2":"5V_LDO_HOLD"},
    "U_PWR": {"1":"PWR_SENSE","2":"GND","3":"5V_LDO_HOLD","4":"5V_LDO_HOLD","5":"PWR_CT","6":"PWR_EN"},
    "U_AUDIO": {"1":"ADC_SENSE","2":"GND","3":"PWR_EN","4":"5V_LDO_HOLD","5":"AUDIO_CT","6":"AUDIO_EN"},
    "U_DUMP": {"1":"","2":"DUMP_RC","3":"GND","4":"DUMP_GATE","5":"5V_LDO_HOLD"},
    "U_LDO_EN": {"1":"","2":"DUMP_GATE","3":"GND","4":"LDO_EN","5":"5V_LDO_HOLD"},
    "Q_DUMP": {"1":"DUMP_GATE","2":"GND","3":"ADC_DUMP"},
    "R_DUMP": {"1":"3V3_ADC","2":"ADC_DUMP"},
    "C_RAW_HOLD": {"1":"5V_OPA","2":"GND"},
    "C_OPA_BULK2": {"1":"5V_OPA","2":"GND"},
    "R_OPA_FEED": {"1":"5V_BUCK","2":"5V_OPA"},
    "R_OPA_BLEED1": {"1":"5V_OPA","2":"OPA_BLEED_A"},
    "R_OPA_BLEED2": {"1":"OPA_BLEED_A","2":"OPA_BLEED_B"},
    "R_OPA_BLEED3": {"1":"OPA_BLEED_B","2":"GND"},
    "C_HOLD1": {"1":"5V_LDO_HOLD","2":"GND"},
    "C_HOLD2": {"1":"5V_LDO_HOLD","2":"GND"},
    "R_LDO_TOP": {"1":"3V3_ADC","2":"LDO_FB"},
    "R_LDO_BOT": {"1":"LDO_FB","2":"GND"},
    "R_PWR_TOP": {"1":"5V_BUCK","2":"PWR_SENSE"},
    "R_PWR_BOT": {"1":"PWR_SENSE","2":"GND"},
    "R_ADC_TOP": {"1":"3V3_ADC","2":"ADC_SENSE"},
    "R_ADC_BOT": {"1":"ADC_SENSE","2":"GND"},
    **{f"C_LDO_NR{n}":{"1":"LDO_NR","2":"GND"} for n in range(1,6)},
    "U_AFE9": {"1":"VMID1_RAW","2":"VMID1_RAW","3":"VMID1_IN","4":"GND",
               "5":"VMID2_IN","6":"VMID2_RAW","7":"VMID2_RAW","8":"5V_OPA"},
    **{f"R_VMID{n}_IN":{"1":f"VMID{n}_EXT","2":f"VMID{n}_IN"} for n in (1,2)},
    **{f"R_VMID{n}_ISO":{"1":f"VMID{n}_RAW","2":f"VMID{n}_BUF"} for n in (1,2)},
}
POWER_VALUES = {
    "D_BUCK_IN":"US1B-13-F", "U_BUCK":"AP63205WU-7",
    **{r:"10uF" for r in ("C_BUCK_IN","C_BUCK_IN2","C_BUCK_IN3")},
    "R_PRE":"22","R_DUMP":"1","R_LDO_TOP":"3.57k","R_LDO_BOT":"1.15k",
    "R_PWR_TOP":"30.9k","R_PWR_BOT":"10k","R_ADC_TOP":"17.4k","R_ADC_BOT":"10k",
    "C_LDO_IN":"47uF","C_LDO_OUT":"47uF",
    "C_RAW_HOLD":"470uF","C_HOLD1":"470uF","C_HOLD2":"470uF",
    "C_OPA_BULK2":"47uF", "R_OPA_FEED":"0.05",
    "R_OPA_BLEED1":"300", "R_OPA_BLEED2":"100", "R_OPA_BLEED3":"100",
    "C_PWR_CT":"1uF","C_AUDIO_CT1":"1uF","C_AUDIO_CT2":"1uF",
    "C_DUMP_TIME":"15nF","R_DUMP_TIME1":"100k","R_DUMP_TIME2":"100k",
    **{f"C_LDO_NR{n}": "15nF" if n <= 3 else "1nF" for n in range(1,6)},
    "U_AFE9":"OPA2320AIDR",
    **{f"R_VMID{n}_IN":"10k" for n in (1,2)},
    **{f"R_VMID{n}_ISO":"1k" for n in (1,2)},
}

def validate_legacy_power(pins, values):
    """Historical TPS fixture only; never used for current source/native admission."""
    local_owners={ref for ref,row in pins.items() if '12V_BUCK_IN' in row.values()}
    if local_owners != {'D_BUCK_IN','U_BUCK','C_BUCK_IN','C_BUCK_IN2','C_BUCK_IN3'}:
        raise ValueError(f'12V_BUCK_IN unexpected owners: {sorted(local_owners)}')
    for ref, wanted in POWER_PINS.items():
        if pins.get(ref) != wanted:
            raise ValueError(f"{ref}: power pin map {pins.get(ref)!r} != {wanted!r}")
    for ref, wanted in POWER_VALUES.items():
        got = values.get(ref, "").replace("Ω","").replace("µ","u")
        if got != wanted:
            raise ValueError(f"{ref}: {got!r} != {wanted!r}")
    return {"power_pin_maps":len(POWER_PINS), "power_values":len(POWER_VALUES)}


def validate_power(pins, values):
    """The sole live topology boundary: stale TPS output must fail, not dispatch."""
    if values.get('U_LDO') != 'LT3041ADE#TRPBF':
        raise ValueError('U_LDO: current ADR0025 LT3041 required; stale/retired converter rejected')
    from check_protection_architecture import validate
    return validate(pins, values)

def divider(vref, rtop, rbot, ref_tol, resistor_tol=0.003125, ibias=1e-7):
    # Per resistor:0.1%initial +25ppm*65C +0.05%engineering aging.
    lo = vref*(1-ref_tol)*(1+rtop*(1-resistor_tol)/(rbot*(1+resistor_tol)))-ibias*rtop
    hi = vref*(1+ref_tol)*(1+rtop*(1+resistor_tol)/(rbot*(1-resistor_tol)))+ibias*rtop
    return lo,hi

def discharge(cmain_uF=154, cbank_uF=806.52, rdump=1.2, rfeed=2.0, initial=3.34):
    """Two physical FILT feeds, no constant load assistance: slow-fall screen.
    Main cap conservatively includes isolated internal/divider charge inventory.
    rfeed=1ohm feed plus1ohm cold/aged cap ESR engineering envelope.
    """
    dt=1e-6
    a=b=initial
    crossings={"main":{},"filt":{}}
    min_reverse=100
    held=4.10
    held_cap=(940*.8*.7*.9 + 47*.34425)*1e-6
    # 1.5ms design timing envelope, NOT a maximum supplied by Nexperia.
    held -= .154*.0015/held_cap
    min_reverse=min(min_reverse,held-a)
    for k in range(25000):
        da=((2*(b-a)/rfeed)-a/rdump)/(cmain_uF*1e-6)
        db=-(b-a)/rfeed/(cbank_uF*1e-6)
        a+=da*dt; b+=db*dt
        held-=.022*dt/held_cap #20mA diode100C maximum +2mA held controls.
        min_reverse=min(min_reverse,held-a)
        for name,v in (("main",a),("filt",b)):
            for frac in (.9,.1,.05,.01):
                if v<=initial*frac and frac not in crossings[name]:
                    crossings[name][frac]=(k+1)*dt*1000
    return {name:{"fall_90_to_10_ms":v[.1]-v[.9],
                  "to_5pct_ms":v[.05],"to_1pct_ms":v[.01]} for name,v in crossings.items()} | {"minimum_held_minus_output_V":min_reverse}

def nr_settling_estimate(cap_F=47e-9, settled_fraction=.99):
    """Typical two-phase estimate, NOT a loaded-bank or restart bound.

    TI SBVS318B p14, Fig36 and p19, Eq5: use the approximate linear
    charge equation up to the approximately97% transition, then the280kohm
    typical RC tail. This deliberately does not solve Fig36's parallel
    resistor contribution during the initial phase or the regulator loop.
    Assume NR starts at zero and feedback tracks NR. Neither assumption
    establishes partial-reset behavior; the250ohm discharge is at OUT.
    """
    if not math.isfinite(cap_F) or cap_F<=0:
        raise ValueError('NR capacitance must be finite and positive')
    if not math.isfinite(settled_fraction) or not .97<settled_fraction<1:
        raise ValueError('NR tail target must be strictly between97% and100%')
    initial=.97*.8*cap_F/6.2e-6
    tail=280000*cap_F*math.log(.03/(1-settled_fraction))
    return {
        'model':'Eq5 linear phase to97%, then typical RNR-C tail; not a circuit simulation',
        'capacitance_F':cap_F,
        'transition_fraction_typical':.97,
        'settled_fraction':settled_fraction,
        'RNR_typical_ohm':280000,
        'linear_to_transition_ms':initial*1000,
        'tail_ms':tail*1000,
        'total_ms':(initial+tail)*1000,
        'is_guaranteed_bound':False,
        'guaranteed_settling_max_ms':None,
        'guaranteed_NR_reset_max_ms':None,
    }

def reference_protection_screen(input_ohm=10000, output_ohm=1000,
                                retained_V=5.4, resistance_reserve=.05):
    """ADR0023 conditional retained-reference current/power arithmetic.

    SBOS513F6.1 note2 permits <=10mA current-limited input overdrive.
    Charge on EXT capacitors sees R_IN before +IN; BUF sees R_ISO before
    the combined OUT/-IN node. Do not assume how internal diodes share it.
    retained_V is an assumed maximum resistor differential in either
    polarity, NOT proof of the attainable node voltage or an output rating.
    RC_L series:1/16W at70C, linearly derated to zero at155C.
    """
    if (not all(math.isfinite(v) for v in
                (input_ohm, output_ohm, retained_V, resistance_reserve))
            or min(input_ohm, output_ohm, retained_V) <= 0
            or not 0 <= resistance_reserve < 1):
        raise ValueError("finite positive reference values and reserve in [0,1) required")
    rin = input_ohm * (1-resistance_reserve)
    rout = output_ohm * (1-resistance_reserve)
    ipos, ifeedback = retained_V/rin, retained_V/rout
    power_rating = .0625*(155-85)/(155-70)
    return {
        'positive_input_current_A': ipos,
        'combined_output_feedback_current_A': ifeedback,
        'retained_differential_engineering_envelope_V': retained_V,
        'resistance_engineering_reserve': resistance_reserve,
        'input_resistor_power_W': retained_V**2/rin,
        'output_resistor_power_W': retained_V**2/rout,
        'resistor_85C_power_rating_W': power_rating,
        'output_RC_nominal_ms': output_ohm*4.7e-6*1000,
        'proves_node_voltage_envelope': False,
        'proves_output_pin_overdrive_rating': False,
        'limits': ['Resistor differential envelope needs correlated all-state source argument',
                   'Input10mA protection specification is not an output backdrive rating',
                   'Feedback stays before R_ISO; leakage, bank loading and settling remain separate'],
        'checks': {'positive_input_current': ipos < .010,
                   'feedback_input_current': ifeedback < .010,
                   'input_resistor_power': retained_V**2/rin < power_rating,
                   'output_resistor_power': retained_V**2/rout < power_rating},
    }


def screen(vin=5.15,vout=3.23,current=.15,ambient=85,theta_ja=56.9,tj_limit=125,
           cap_inventory_uF=1060.98, buck_ramp_ms=4, local_allocation_A=.30,
           opa_extra_uF=47, bleed_ohm=500, feed_ohm=.05,
           held_control_A=.002, held_leakage_A=.000104,
           bypass_equalization_R_budget_ohm=.1, input_diode_drop_V=1.3,
           input_diode_leakage_A=.0001, buck_reverse_control_A=.001,
           input_diode_recovery_budget_C=100e-9):
    vlo,vhi=divider(.8,3570,1150,.01)
    rawlo,rawhi=divider(1.15,30900,10000,.01)
    audiolo,audiohi=divider(1.15,17400,10000,.01)
    # Panasonic: tolerance20%, endurance30%, solder10%. Ceramic high uses
    # tolerance10%, temperature15%; aging/DC bias do not increase capacitance.
    cbulk_hi=940*1.2*1.3*1.1
    cout_hi=cbulk_hi+(cap_inventory_uF-940)*1.1*1.15
    raw_hi=(470*1.2*1.3*1.1 + (188.9+opa_extra_uF)*1.1*1.15)*1e-6
    bleed_max=5.5/(bleed_ohm*.95)
    held_hi=(940*1.2*1.3*1.1 + 47*1.1*1.15)*1e-6
    nr_lo=47e-9*.95*.997
    nr_hi=47e-9*1.05*1.003
    ss_fast=.792*nr_lo/9e-6
    ss_slow=.808*nr_hi/4e-6
    ldo_peak=cout_hi*1e-6*vhi/ss_fast+current+.004
    fmin=1.1e6*.94
    lmin=3.3e-6*.8*.8 #initial20% plus engineering20% DC-bias screen
    ripple=(5.15*(1-5.15/13.2))/(lmin*fmin)
    ramp=buck_ramp_ms*.001
    raw_charge=raw_hi*5.15/ramp
    held_charge=held_hi*(5.15/ramp)*(1-math.exp(-ramp/(22*held_hi))) #linear raw ramp response
    startup_peak=raw_charge+held_charge+.100+ripple/2+bleed_max
    ldo_start_peak=ldo_peak+.100+ripple/2+bleed_max
    ct_min=.34425e-6*1.17/1.35e-6
    # Constant-load RC upper screen, not the old unloaded exponential.
    # 2mA control allocation plus94uA two bulk-cap leakage and10uA ceramic
    # reserve; these are engineering bounds to qualify at temperature/life.
    held_static=held_control_A+held_leakage_A
    rpre_hi=22*1.02
    unloaded_residual=5.15*math.exp(-ct_min/(rpre_hi*held_hi))
    precharge_residual=held_static*rpre_hi+(5.15-held_static*rpre_hi)*math.exp(-ct_min/(rpre_hi*held_hi))
    equalization_budget=precharge_residual/bypass_equalization_R_budget_ohm
    # 1.2Vrms differential, all8channels at20kHz. Triangle inequality
    # bounds resistive+capacitive output current; no cancellation credit.
    ac_diff_peak=math.sqrt(2)*1.2*(1/3000+2*math.pi*20000*16e-9)
    audio_supply=8*2*ac_diff_peak/math.pi
    # Keep the previous conservative allocations;5mA/channel is NOT the
    # new OPA2320's1.7mA maximum unloaded IQ or a vendor transient bound.
    steady=current+.004+18*.005+audio_supply+8*.00013+.002+bleed_max
    upstream=.8+local_allocation_A*5.15/(.85*(11.16-input_diode_drop_V))+.001
    shutdown_load=.11+bleed_max+input_diode_leakage_A+buck_reverse_control_A
    shutdown_cap=(470*.504+(188.9+opa_extra_uF)*.34425)*1e-6
    dissipation=(vin-vout)*current+vin*.004
    result={
        "dissipation_mW":dissipation*1000,
        "reference_board_tj_C":ambient+dissipation*theta_ja,
        "reference_board_budget_mW":(tj_limit-ambient)/theta_ja*1000,
        "thermal_screen_pass":ambient+dissipation*theta_ja <= tj_limit,
        "feedback_output_V":[vlo,vhi],
        "raw_falling_threshold_V":[rawlo,rawhi],
        "raw_rising_max_V":rawhi*1.00825,
        "audio_falling_threshold_V":[audiolo,audiohi],
        "audio_rising_max_V":audiohi*1.00825,
        "charge_inventory_all_life_upper_uF":cout_hi,
        # Eq5's equivalent charge interval does not include final settling.
        "NR_linear_charge_equivalent_ms":[ss_fast*1000,ss_slow*1000],
        "NR_ramp_10_to_90_screen_ms":[ss_fast*800,ss_slow*800],
        "NR_settling_typical_estimate":nr_settling_estimate(),
        "raw_buck_startup_peak_A":startup_peak,
        "ldo_bank_startup_peak_A":ldo_start_peak,
        "buck_peak_limit_min_A":2.5,
        "ldo_peak_current_A":ldo_peak,
        "ldo_current_limit_min_A":2.3,
        "precharge_min_delay_ms":ct_min*1000,
        "precharge_residual_max_V":precharge_residual,
        "precharge_unloaded_residual_V":unloaded_residual,
        "precharge_static_load_A":held_static,
        "precharge_bypass_R_engineering_min_ohm":bypass_equalization_R_budget_ohm,
        "precharge_bypass_equalization_budget_A":equalization_budget,
        "precharge_bypass_difference_energy_upper_uJ":.5*held_hi*precharge_residual**2*1e6,
        "precharge_bypass_is_coupled_network_proof":False,
        "precharge_energy_upper_mJ":.5*held_hi*5.15**2*1000,
        "precharge_peak_W":5.15**2/(22*.98),
        "all_channel_steady_screen_A":steady,
        "local_5V_allocation_A":local_allocation_A,
        "upstream_trunk_bound_A":upstream,
        "raw_OPA_hold_screen_V":rawlo-(shutdown_load*.000320+input_diode_recovery_budget_C)/shutdown_cap-shutdown_load*feed_ohm*1.05,
        "OPA_part":"OPA2320AIDR",
        "OPA_unloaded_IQ_allocation_per_channel_A":.005,
        "OPA_shutdown_load_allocation_A":.11,
        "OPA_hold_engineering_floor_V":4.5,
        "OPA_hold_floor_scope":"Retained conservative design screen, NOT OPA2320 minimum supply or a valid-audio-during-shutdown requirement; no all-state guarantee",
        "input_diode_drop_budget_V":input_diode_drop_V,
        "input_diode_leakage_budget_A":input_diode_leakage_A,
        "buck_reverse_control_budget_A":buck_reverse_control_A,
        "input_diode_recovery_budget_C":input_diode_recovery_budget_C,
        "input_diode_recovery_is_vendor_guarantee":False,
        "shutdown_loading_includes_shared_spokes":False,
        "OPA_bleed_max_A":bleed_max,
        "off_leakage_ADC_85C_V":.1e-6*101000,
        "charge_injection_typical_V":5e-12/(1e-9*.95),
        "ADC_input_bleed_99pct_us":101000*1e-9*1.05*math.log(100)*1e6,
        "discharge":discharge(cmain_uF=max(1,cout_hi-cbulk_hi),initial=vhi),
    }
    result["checks"]={
        "thermal":result["thermal_screen_pass"],
        "feedback_window":vlo>=3.23 and vhi<=3.34,
        "dropout":4.10-vhi>=.4,
        "raw_enable":result["raw_rising_max_V"]<4.85,
        "audio_enable":result["audio_rising_max_V"]<vlo,
        "precharge_bypass_conditional_current":equalization_budget<4.,
        "buck_typical_4ms_start":startup_peak<2.5,
        "buck_ldo_charge":ldo_start_peak<2.5,
        "LDO_current":ldo_peak<2.3,
        # Preserve the existing conservative linear-proxy admission limits;
        # this check does NOT assert full settling within10ms.
        "NR_ramp_screen":ss_slow<=.010 and ss_fast>=.00001,
        "discharge_90_10":all(result["discharge"][n]["fall_90_to_10_ms"]<=10 for n in ("main","filt")),
        "reverse_hold":result["discharge"]["minimum_held_minus_output_V"]>0,
        "OPA_before_isolation":result["raw_OPA_hold_screen_V"]>result["OPA_hold_engineering_floor_V"],
        "steady_local":steady<=local_allocation_A,
        "upstream":upstream<=1.0,
    }
    result["qualification_owed"]=[
        "POWER-PRECHARGE: static controls/leakage and0.1ohm equalization-path engineering minimum require qualification; RC difference-energy/current screen does not prove repeated coupled finite-L startup",
        "POWER-COLD: Schmitt behavior at held1.4..1.65V and TMUX partialVDD0..1.8V; no datasheet guarantee claimed",
        "POWER-START: AP63205 4ms is typical not minimum; NR4..9uA specified atNR=0; measure no hiccup/overshoot and complete bank rise",
        "POWER-NR: approximately97% transition and280kohm tail are typical; no guaranteed full-settling or NR reset time.250ohm typical active discharge belongs to OUT, not NR. Partial-reset restart and loaded bank tracking remain unqualified",
        "POWER-FALL: supervisor100us +220us isolation and dump1.5ms are scoped design budgets, not vendor maximum for detector/gates",
        "POWER-LOOP: large filtered bank stability across ESR, cold/hot, aged-equivalent capacitance and rapid restart",
        "POWER-REVERSE: ADR0022 blocks shared-spoke loading;100uA external diode leakage,1mA local buck/control draw and100nC recovery are explicit conditional budgets. Capture VIN/SW/raw/OPA/feed current during removal, brownout and restart; neither trr nor PFM proves these budgets. Destructive internal5Vshort excluded",
        "POWER-AUDIO: 5pC charge injection and THD are typical only; step/feedthrough, off pin voltage/current and loaded audio/stability must be measured",
        "POWER-DRIFT: RTseries0.05% prototype drift allowance is NOT published0.5%life/heat-test maximum; all-life divider margins are not closed",
        "POWER-THERMAL: EP solder, achieved thermal resistance and pulse resistor/MOSFET temperature/SOA; reference board is not this PCB",
    ]
    result["status"]="PASS_CONDITIONAL_SCREENS" if all(result["checks"].values()) else "OPEN_SOURCE_SCREEN_FAILURE"
    result["physical_qualification_waiver"]=False
    return result

def cold_start_screen(series_ohm=10000, bleed_ohm=500, rail_barrier=5.4,
                      pod_max=5.5, leakage_A=1e-6, feed_L_H=10e-9,
                      feed_current_budget_A=4.0):
    """ADR0021 bounded connected-pod screen, NOT absolute-voltage assurance.

    TI OPA2320 SBOS513F6.1 note2 /7.3.2 limits steering current to10mA when inputs
    exceed the rails, including power-off. No exact diode voltage is claimed.
    Passive steering, rail-limited outputs,1uA unexplained input leakage and
    10nH complete feed-loop L are explicit prototype engineering assumptions.
    The common rail barrier covers raw/OPA/held RC sharing, not an isolated rail.
    """
    rmin=series_ohm*.95; rbmax=100000*1.05
    # q=u-tee. At q>pod_max+Ileak*Rbmax, tee<-Ileak*Rbmax:
    # bias/negative steering drive q down. Opposite face drives q up.
    qmax=pod_max+leakage_A*rbmax
    positive=16*max(0,pod_max+qmax-rail_barrier)/rmin
    bleed_min=rail_barrier/(bleed_ohm*1.05)
    c_raw=141*.34425e-6
    c_opa=94.9*.34425e-6 #HF damping gets no electrolytic/ESR credit
    c_eq=c_raw*c_opa/(c_raw+c_opa)
    critical_R=2*math.sqrt(feed_L_H/c_eq)
    result={
        "pod_engineering_envelope_V":[0,pod_max],
        "reachable_capacitor_voltage_bound_V":qmax,
        "positive_input_current_bound_A":(pod_max+qmax)/rmin,
        "negative_input_current_bound_A":qmax/rmin,
        "all16_rail_injection_at_barrier_A":positive,
        "bleed_at_barrier_min_A":bleed_min,
        "rail_barrier_V":rail_barrier,
        "rail_current_margin_A":bleed_min-positive-18*leakage_A,
        "feed_critical_damping_R_ohm":critical_R,
        "feed_min_R_ohm":.05*.95,
        "buck_HS_peak_limit_min_max_A":[2.5,3.1],
        "buck_LS_valley_limit_min_max_A":[2.5,3.9],
        "feed_current_engineering_budget_A":feed_current_budget_A,
        "feed_current_budget_is_vendor_guarantee":False,
        "feed_budget_power_W":feed_current_budget_A**2*.05*1.05,
        "feed_85C_power_rating_W":.85,
        "series_20kHz_differential_thermal_noise_Vrms":math.sqrt(4*1.380649e-23*(85+273.15)*2*series_ohm*1.05*20000),
        "bleed_300ohm_max_power_W":(5.5/(bleed_ohm*.95))**2*300*1.05,
        "RC0402_85C_power_rating_W":.0625*(155-85)/(155-70),
        "steady_input_common_mode_max_V":1.7+math.sqrt(2)*1.2/2+series_ohm*1.05*leakage_A,
        "amplifier_part":"OPA2320AIDR",
        "steady_input_common_mode_allowed_max_V":4.85-(.11+5.5/(bleed_ohm*.95))*.05*1.05+.1,
        "limitations":["No manufacturer-guaranteed exact diode drop or input absolute-voltage PASS",
                        "TI recommended current-limited overload mode; audio validity is not claimed during startup",
                        "0..5.5V pod, <=1uA unexplained leakage, <=10nH feed loop and rail-limited outputs are prototype budgets, not vendor guarantees",
                        "Raw buck overshoot, parasitic behavior, feed impedance and powered-off rail captures remain first-article holds"]}
    result['checks']={
        'current_limited':max(result['positive_input_current_bound_A'],result['negative_input_current_bound_A'])<.010,
        'all_rails_barrier':result['rail_current_margin_A']>0,
        'feed_overdamped':critical_R<result['feed_min_R_ohm'],
        'feed_power':result['feed_budget_power_W']<result['feed_85C_power_rating_W'],
        'bleed_power':result['bleed_300ohm_max_power_W']<result['RC0402_85C_power_rating_W'],
        'steady_common_mode':result['steady_input_common_mode_max_V']<result['steady_input_common_mode_allowed_max_V']}
    return result

def adr0021_bound(name, value=None):
    """Reproduce fixed-source scalar limits or evaluate a candidate value.

    These are algebraic consequences of cold_start_screen's explicit model,
    NOT measured parasitics, reachable trajectories, or source admission.
    Evaluation returns dimensionless utilization: at most one passes the
    conditional calculation. No source/default budget is changed.
    """
    base = cold_start_screen()
    names = {'leakage_uA', 'loop_nH', 'part_nH', 'pcb_nH',
             'feed_current_A', 'feed_resistance_ohm', 'bleed_resistance_ohm'}
    if name not in names:
        raise ValueError(f'unknown ADR0021 bound: {name}')
    if value is None:
        if name == 'leakage_uA':
            # Sixteen q-bound contributions plus eighteen leakage reserves.
            slope = 16 * (100000 * 1.05) / (10000 * .95) + 18
            return (1e-6 + base['rail_current_margin_A'] / slope) * 1e6
        if name in {'loop_nH', 'part_nH', 'pcb_nH'}:
            total = 10 * (base['feed_min_R_ohm'] /
                          base['feed_critical_damping_R_ohm']) ** 2
            return total if name == 'loop_nH' else total - 5
        if name == 'feed_current_A':
            return 4 * math.sqrt(base['feed_85C_power_rating_W'] /
                                 base['feed_budget_power_W'])
        if name == 'feed_resistance_ohm':
            return base['feed_critical_damping_R_ohm'] / .95
        return 500 * math.sqrt(base['bleed_300ohm_max_power_W'] /
                               base['RC0402_85C_power_rating_W'])
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError('candidate bound must be finite and positive')
    if name == 'leakage_uA':
        row = cold_start_screen(leakage_A=value * 1e-6)
        return (row['all16_rail_injection_at_barrier_A'] +
                18 * value * 1e-6) / row['bleed_at_barrier_min_A']
    if name in {'loop_nH', 'part_nH', 'pcb_nH'}:
        total = value if name == 'loop_nH' else value + 5
        row = cold_start_screen(feed_L_H=total * 1e-9)
        return row['feed_critical_damping_R_ohm'] / row['feed_min_R_ohm']
    if name == 'feed_current_A':
        row = cold_start_screen(feed_current_budget_A=value)
        return row['feed_budget_power_W'] / row['feed_85C_power_rating_W']
    if name == 'feed_resistance_ohm':
        return base['feed_critical_damping_R_ohm'] / (value * .95)
    row = cold_start_screen(bleed_ohm=value)
    return row['bleed_300ohm_max_power_W'] / row['RC0402_85C_power_rating_W']


def source_power_maps(comps,flat):
    """Preserve actual terminals; never fill missing or overwrite wired NC."""
    pins={r:{p:('' if n.startswith('unconnected-') else n)
             for (ref,p),n in flat.items() if ref==r} for r in comps}
    return pins,{r:v for r,(_,v) in comps.items()}

def main(source_only=False):
    for mpn in ("LT3041ADE-TRPBF","TPS389001DSER","TMUX2821DSGR","AO3400A","AO3401A","B340A-13-F","AP63205WU-7","US1B-13-F","OPA2320AIDR","RC0402FR-071KL"):
        part=yaml.safe_load((PROJECT/"02_parts"/mpn/"part.yaml").read_text())
        ds=part["datasheet"]
        if hashlib.sha256((PROJECT/"02_parts"/mpn/ds["local"]).read_bytes()).hexdigest()!=ds["sha256"]:
            raise ValueError(f"{mpn}: primary authority changed")
    if source_only:
        # Fresh source boundary only. Default native parity remains mandatory
        # in both conductors after regeneration; stale native is not reused.
        import sys
        sys.path.insert(0,str(PROJECT/'03_src/tests'))
        from source_inventory import inventory
        comps,flat,_=inventory()
        pins,values=source_power_maps(comps,flat)
    else:
        pins,values=parse_native_netlist(PROJECT/"06_build/netlists/crow_audio_carrier_v1.net")
    validate_power(pins, values)
    from check_protection_architecture import source_receipt
    result=source_receipt(pins,values)
    result['input_authority']='live JSX source; native parity owed' if source_only else 'exported native netlist; exact downstream reviews owed'
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if all(result['checks'].values()) else 1

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only',action='store_true')
    parser.add_argument('--adr0021-bound', help='read-only conditional scalar bound')
    parser.add_argument('--evaluate', type=float, help='candidate value; emits utilization')
    args=parser.parse_args()
    if args.adr0021_bound:
        if args.source_only:
            parser.error('--source-only cannot be combined with --adr0021-bound')
        try:
            print(adr0021_bound(args.adr0021_bound, args.evaluate))
        except ValueError as exc:
            parser.error(str(exc))
    elif args.evaluate is not None:
        parser.error('--evaluate requires --adr0021-bound')
    else:
        raise SystemExit(main(source_only=args.source_only))
