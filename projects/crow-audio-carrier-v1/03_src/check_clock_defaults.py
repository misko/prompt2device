#!/usr/bin/env python3
"""Prototype DC screen for the carrier's independent-power boundary.

Backend gap: electrical_invariants checks exact values/pins but cannot express
aggregate input/gate leakage, divider corners and external-driver DC loading.
A future shared ``logic_bias`` schema would replace this one-board adapter.
This gate does NOT certify a module output driver, hot plug or temperature
performance: the explicit allocations below are first-article requirements.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

import yaml

from check_analog_filter_topology import parse_native_netlist, _normalize_value


PROJECT = Path(__file__).resolve().parents[1]
CLOCK_REFS = {
    "R_MCH_MCLK_PD": "MCH_MCLK",
    "R_MCH_BCLK_PD": "MCH_BCLK",
    "R_MCH_FSYNC_PD": "MCH_FSYNC",
}
EXPECTED = {
    **{ref: ("10k", net, "GND", "C60490", "RC0402FR-0710KL")
       for ref, net in CLOCK_REFS.items()},
    "R_MCH_SENSE": ("300", "MCH_3V3_SENSE", "TDM_SENSE_G", "C138010", "RC0402FR-07300RL"),
    "R_MCH_SENSE_PD": ("10k", "TDM_SENSE_G", "GND", "C60490", "RC0402FR-0710KL"),
    "R_TDM_PD": ("10k", "TDM_RAW", "GND", "C60490", "RC0402FR-0710KL"),
}
# Identity-bound manufacturer limits: SCES366L pp.4–5, SCES223U pp.5–6,
# Nexperia 74LVC1G14 Rev19 pp.1,3,5-7. No interpolated threshold guarantees.
PDFS = {
    "SN74LVC3G34DCUR": "d541afbccf6270522f5ba33b86ca31da0ec6bbf497c0d1f8ba265e9ac2e1faec",
    "SN74LVC1G125DBVR": "65afa3f9d879b37cb8be507caf84804b24bceeb2e0782ba449fff72160994e4c",
    "74LVC1G14GV,125": "b8f37c700d0fc8374de6d14f0e2caf310c34b480ffab9d63c69bb3b6defbebbf",
    "74LVC1G17GV,125": "3db133d57486306950ba1140ac13a8a0ea95509dcefb88db36c08423a819b163",
}


def screen(clock_r: float = 10_000, gate_r: float = 10_000,
           sense_r: float = 300, oe_load_uA: float = 25) -> dict:
    """Return arithmetic only; budgets here are not manufacturer guarantees."""
    if any(r <= 0 for r in (clock_r, gate_r, sense_r)) or oe_load_uA < 0:
        raise ValueError("resistances must be positive")
    r_lo, r_hi = 0.97, 1.03  # 1% initial + 2% engineering drift allocation
    gate_lo, series_hi = gate_r * r_lo, sense_r * r_hi
    parallel = gate_lo * series_hi / (gate_lo + series_hi)
    measurements = {
        "clock_receiver_only_low_V": 5e-6 * clock_r * r_hi,
        "clock_allocated_low_V": 25e-6 * clock_r * r_hi,
        "clock_driver_load_A": 3.6 / (clock_r * r_lo) + 5e-6,
        "sense_absent_gate_V": 20e-6 * gate_r * r_hi,
        "sense_present_gate_V": 3.0 * gate_lo / (gate_lo + series_hi) - 20e-6 * parallel,
        "sense_supply_load_A": 3.6 / ((sense_r + gate_r) * r_lo) + 20e-6,
        "oe_disabled_V": 3.0 - 0.1,
        "oe_enabled_V": 0.1,
        "oe_output_load_A": oe_load_uA * 1e-6,
    }
    predicates = {
        "receiver_low": measurements["clock_receiver_only_low_V"] < 0.8,
        "allocated_clock_low": measurements["clock_allocated_low_V"] < 0.4,
        "clock_load": measurements["clock_driver_load_A"] < 0.0004,
        "gate_absent": measurements["sense_absent_gate_V"] < 0.4,
        "gate_present": measurements["sense_present_gate_V"] > 2.8,
        "sense_supply_load": measurements["sense_supply_load_A"] < 0.0004,
        "oe_disabled": measurements["oe_disabled_V"] > 2.4,
        "oe_enabled": measurements["oe_enabled_V"] < 0.4,
        "oe_output_load": measurements["oe_output_load_A"] <= 100e-6,
    }
    return {"measurements": measurements, "checks": predicates}


def validate_source(text: str, project: Path) -> None:
    if text.count('N("TDM_RAW")') != 2 or text.count('a="TDM_RAW"') != 1 or 'b="TDM_RAW"' in text:
        raise ValueError("TDM_RAW: only ADC, Schmitt input and one bias branch are permitted")
    conditioner = re.findall(r'<Chip\b[^>]*\bname="U_TDM_SCH"[\s\S]*?footprint=\{<Sot23_5 />\} />', text)
    if len(conditioner) != 1 or 'manufacturerPartNumber="74LVC1G17GV,125" jlc="C6076"' not in conditioner[0]:
        raise ValueError("U_TDM_SCH: exact noninverting unlimited-input-slew Schmitt buffer required")
    conn = re.search(r'connections=\{\{(.*?)\}\}', conditioner[0], re.S)
    expected_conditioner = {"2":"TDM_RAW", "3":"GND", "4":"TDM_CLEAN", "5":"3V3_ADC"}
    if not conn or dict(re.findall(r'pin(\d+): N\("([^"]+)"\)', conn[1])) != expected_conditioner:
        raise ValueError("U_TDM_SCH: wrong pin/net or grounded NC")
    tdm = re.findall(r'<Chip\b[^>]*\bname="U_TDM"[\s\S]*?footprint=\{<Sot23_5 />\} />', text)
    if len(tdm) != 1 or 'manufacturerPartNumber="SN74LVC1G125DBVR" jlc="C23654"' not in tdm[0]:
        raise ValueError("U_TDM: retain exact Ioff tri-state boundary")
    conn = re.search(r'connections=\{\{(.*?)\}\}', tdm[0], re.S)
    if not conn or dict(re.findall(r'pin(\d+): N\("([^"]+)"\)', conn[1])) != {
        "1":"TDM_OE_N", "2":"TDM_CLEAN", "3":"GND", "4":"TDM_BUFFERED", "5":"3V3_ADC"}:
        raise ValueError("U_TDM: raw released node must not drive the CMOS input")
    if '<C2 name="C_TDM_SCH" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC"' not in text:
        raise ValueError("U_TDM_SCH: exact local bypass required")
    if 'name="Q_TDM_EN"' in text or 'name="R_TDM_OE_PU"' in text:
        raise ValueError("direct RC/NMOS OE drive is forbidden; use genuine Schmitt push-pull U_OE")
    form = re.findall(r'<Chip\b[^>]*\bname="U_OE"[\s\S]*?footprint=\{<Sot23_5 />\} />', text)
    if len(form) != 1 or 'manufacturerPartNumber="74LVC1G14GV,125" jlc="C131093"' not in form[0]:
        raise ValueError("U_OE: exact Nexperia Schmitt inverter identity/package required")
    expected = {"2": "TDM_SENSE_G", "3": "GND", "4": "TDM_OE_N", "5": "3V3_ADC"}
    connections = re.search(r'connections=\{\{(.*?)\}\}', form[0], re.S)
    if not connections or dict(re.findall(r'pin(\d+): N\("([^"]+)"\)', connections[1])) != expected:
        raise ValueError("U_OE: source pin map differs from Schmitt power boundary")
    if '<C2 name="C_OE" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC"' not in text:
        raise ValueError("U_OE: exact local bypass required")
    if 'pin38: N("3V3_ADC")' not in text:
        raise ValueError("U_ADC.38 SPI_CS must tie VDD_IO in hardware mode (DS1314F1 Table1-2)")
    for ref, (value, a, b, code, mpn) in EXPECTED.items():
        forms = re.findall(r'<R2\b[^>]*\bname="' + re.escape(ref) + r'"[^>]*/>', text)
        if len(forms) != 1:
            raise ValueError(f"{ref}: expected exactly one literal R2 source declaration")
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', forms[0]))
        for key, wanted in {"value": value, "a": a, "b": b, "jlc": code, "mpn": mpn}.items():
            if attrs.get(key) != wanted:
                raise ValueError(f"{ref}.{key}: {attrs.get(key)!r}, expected {wanted!r}")
        dossier = yaml.safe_load((project / "02_parts" / mpn / "part.yaml").read_text())
        if (dossier["mpn"], str(dossier["value"]), dossier["sourcing"]["lcsc"]) != (mpn, value, code):
            raise ValueError(f"{ref}: source/dossier identity mismatch")
        if str(dossier["limits"]["tolerance"]) != "1pct":
            raise ValueError(f"{ref}: the screen requires 1% initial tolerance")
    for mpn, digest in PDFS.items():
        partdir = project / "02_parts" / mpn
        dossier = yaml.safe_load((partdir / "part.yaml").read_text())
        actual = hashlib.sha256((partdir / dossier["datasheet"]["local"]).read_bytes()).hexdigest()
        if actual != digest or dossier["datasheet"]["sha256"] != digest:
            raise ValueError(f"{mpn}: leakage authority changed; rederive limits")


def validate_netlist(pins: dict, values: dict) -> None:
    raw = {(ref,pin) for ref, mapping in pins.items() for pin,net in mapping.items() if net == 'TDM_RAW'}
    if raw != {('U_ADC','25'),('U_TDM_SCH','2'),('R_TDM_PD','1')}:
        raise ValueError("TDM_RAW: missing or unbudgeted native load/bias/conditioning")
    expected_pins = {ref: {"1": a, "2": b}
                     for ref, (_, a, b, _, _) in EXPECTED.items()}
    expected_pins.update({
        "U_CLK": {"1": "MCH_MCLK", "2": "FSYNC_BUF", "3": "MCH_BCLK", "4": "GND",
                  "5": "BCLK_BUF", "6": "MCH_FSYNC", "7": "MCLK_BUF", "8": "3V3_ADC"},
        "U_TDM": {"1": "TDM_OE_N", "2": "TDM_CLEAN", "3": "GND", "4": "TDM_BUFFERED", "5": "3V3_ADC"},
        "U_TDM_SCH": {"1": "", "2": "TDM_RAW", "3": "GND", "4": "TDM_CLEAN", "5": "3V3_ADC"},
        "C_TDM_SCH": {"1": "3V3_ADC", "2": "GND"},
        "U_OE": {"1": "", "2": "TDM_SENSE_G", "3": "GND", "4": "TDM_OE_N", "5": "3V3_ADC"},
        "C_OE": {"1": "3V3_ADC", "2": "GND"},
    })
    for ref, wanted in expected_pins.items():
        if pins.get(ref) != wanted:
            raise ValueError(f"{ref}: generated pin map differs from the bias screen")
    for ref, (value, *_rest) in EXPECTED.items():
        if _normalize_value(values.get(ref)) != value:
            raise ValueError(f"{ref}: generated value {values.get(ref)!r}, expected {value}")


def tdm_screen(r_ohm=10_000., adc_board_leak_uA=20., raw_cap_pF=20.,
               clean_load_uA=25., path_allowance_ns=6., setup_allowance_ns=5.,
               bclk_hz=12_288_000., duty_min=.45) -> dict:
    """Conditional prototype screen; no invented ADC/output slew guarantees.

    ADC+PCB20uA, raw20pF, path6ns, remote setup5ns and45% duty are
    engineering acceptance allocations, not manufacturer specifications.
    Input capacitances are not added as if typical values were maxima.
    Nexperia1G17 allows arbitrary input slew; an ordinary CMOS replacement
    is rejected by exact identity, not by a fictitious RC slew proof.
    """
    args = (r_ohm, adc_board_leak_uA, raw_cap_pF, clean_load_uA,
            path_allowance_ns, setup_allowance_ns, bclk_hz, duty_min)
    if not all(math.isfinite(v) and v >= 0 for v in args) or r_ohm == 0 or bclk_hz == 0 or not 0 < duty_min <= .5:
        raise ValueError("invalid TDM screen corner")
    rlo, rhi = r_ohm*.97, r_ohm*1.03
    final = (adc_board_leak_uA+1)*1e-6*rhi
    release_ns = (rhi*raw_cap_pF*1e-3*math.log((3.6-final)/(.4-final))
                  if final < .4 else math.inf)
    # TI3G34 max4.1ns, Cirrus half-cycle launch/enable10ns (25C,
    # VDD_IO3.3V,50pF), Nexperia1G17 max5.5ns and TI1G125 max4.5ns.
    device_ns = 4.1+10.+5.5+4.5
    available_ns = duty_min/bclk_hz*1e9
    m = dict(released_raw_V=final, adc_high_load_A=3.6/rlo+1e-6,
             raw_load_allocation_pF=raw_cap_pF, release_to_0p4V_ns=release_ns,
             clean_high_V=2.9, clean_low_V=.1, clean_load_A=clean_load_uA*1e-6,
             device_delay_screen_ns=device_ns, path_allowance_ns=path_allowance_ns,
             remote_setup_allowance_ns=setup_allowance_ns,
             available_launch_to_sample_ns=available_ns,
             setup_margin_screen_ns=available_ns-device_ns-path_allowance_ns-setup_allowance_ns)
    checks = dict(released_low=final < .4, adc_load=m['adc_high_load_A'] < .0004,
                  raw_cap=0 < raw_cap_pF <= 20., clean_load=clean_load_uA <= 100.,
                  clean_high=m['clean_high_V'] > 2.4, clean_low=m['clean_low_V'] < .4,
                  timing_margin=m['setup_margin_screen_ns'] > 0)
    return dict(measurements=m, checks=checks, grade='CONDITIONAL_ENGINEERING_SCREEN',
                guarantee='NOT_ESTABLISHED',
                open=['ADC DOUT Hi-Z leakage over intended temperature',
                      'ADC VOH/VOL at the added pull load',
                      'actual total capacitance and fast active data edges',
                      '1G17 output slew at U_TDM.2; propagation delay is not slew',
                  'MCH duty/setup/hold and complete cable/PCB path timing',
                      'slow-input supply-current transient and four power states'])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = {"schema": 1, "kind": "crow-carrier-logic-bias-screen", "status": "FAIL",
               "physical_qualification": "OWED", "resistors": len(EXPECTED),
               "manufacturer_pdfs": len(PDFS), "netlist_checked": not args.source_only}
    try:
        source = args.project / "03_tscircuit/src/crow_audio_carrier_v1.tsx"
        validate_source(source.read_text(), args.project)
        receipt["source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        if not args.source_only:
            netlist = args.project / "06_build/netlists/crow_audio_carrier_v1.net"
            validate_netlist(*parse_native_netlist(netlist))
            receipt["netlist_sha256"] = hashlib.sha256(netlist.read_bytes()).hexdigest()
        receipt.update(screen())
        receipt['tdm'] = tdm_screen()
        if not all(receipt['tdm']['checks'].values()):
            raise ValueError("TDM conditional electrical allocations failed")
        failed = [name for name, ok in receipt["checks"].items() if not ok]
        if failed:
            raise ValueError(f"DC allocations failed: {failed}")
        receipt["status"] = "PASS"
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        receipt["error"] = str(exc)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
