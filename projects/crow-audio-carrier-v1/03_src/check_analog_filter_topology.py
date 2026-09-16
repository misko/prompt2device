#!/usr/bin/env python3
"""Fail-closed audit of the Cirrus-derived input and corrected VMID topology.

The public ``validate`` function is pure so hostile tests can mutate one leg
without invoking KiCad.  The CLI parses KiCad 10's native S-expression
netlist with the same shared parser used by schematic parity.

Backend gap: the shared native parity parser does not interpret component
Values for this board's electrical predicates. The local adapter resolves
supplier codes through existing part.yaml identity fields; a shared typed
native-component reader would replace it if another board needs this seam.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

import yaml


class TopologyError(RuntimeError):
    """The generated analog network differs from the vendor-bound contract."""


def _expected() -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    pins: dict[str, dict[str, str]] = {}
    values: dict[str, str] = {}
    for n in range(1, 9):
        values[f"U_AFE{n}"] = "OPA2320AIDR"
        pins[f"U_AFE{n}"]={"1":f"OPA_P{n}","2":f"FB_P{n}","3":f"AIN_P{n}","4":"GND",
                           "5":f"AIN_N{n}","6":f"FB_N{n}","7":f"OPA_N{n}","8":"3V3_ADC"}
        for leg in ('P','N'):
            pins[f"R_IN{n}{leg}"]={"1":f"BIAS_{leg}{n}","2":f"AIN_{leg}{n}"}
            values[f"R_IN{n}{leg}"]="10k"
            pins[f"R_B{n}{leg}"]={"1":f"BIAS_{leg}{n}","2":f"VMID{1 if n<=4 else 2}_EXT"}
            values[f"R_B{n}{leg}"]="100k"
        pins[f"C_A{n}P"] = {"1": f"AUDIO_P{n}", "2": f"BIAS_P{n}"}
        pins[f"C_A{n}N"] = {"1": f"AUDIO_N{n}", "2": f"BIAS_N{n}"}
        values[f"C_A{n}P"] = "1uF"
        values[f"C_A{n}N"] = "1uF"
        pins[f"R_X{n}P"] = {"1": f"FB_P{n}", "2": f"FILTER{n}P"}
        pins[f"R_X{n}N"] = {"1": f"FB_N{n}", "2": f"FILTER{n}N"}
        values[f"R_X{n}P"] = "300"
        values[f"R_X{n}N"] = "300"
        pins[f"C_FB{n}P"] = {"1": f"FB_P{n}", "2": f"OPA_P{n}"}
        pins[f"C_FB{n}N"] = {"1": f"FB_N{n}", "2": f"OPA_N{n}"}
        values[f"C_FB{n}P"] = "680pF"
        values[f"C_FB{n}N"] = "680pF"
        for leg in ("P","N"):
            for k in (1,2):
                pins[f"C_FILTER{n}{leg}{k}"]={"1":f"FILTER{n}{leg}","2":"GND"}
                values[f"C_FILTER{n}{leg}{k}"]="15nF"
        pins[f"U_ISO{n}"] = {"1": f"FILTER{n}P", "2": f"ADC{n}P", "3": "AUDIO_EN",
                             "4": "GND", "5": f"FILTER{n}N", "6": f"ADC{n}N",
                             "7": "AUDIO_EN", "8": "5V_LDO_HOLD", "9": "GND"}
        for leg in ("P", "N"):
            pins[f"R_OUT{n}{leg}"] = {"1": f"OPA_{leg}{n}", "2": f"FILTER{n}{leg}"}
            values[f"R_OUT{n}{leg}"] = "10"
            pins[f"R_ADC_PD{n}{leg}"] = {"1": f"ADC{n}{leg}", "2": "GND"}
            values[f"R_ADC_PD{n}{leg}"] = "10k"
            pins[f"C_ADC_CM{n}{leg}"] = {"1": f"ADC{n}{leg}", "2": "GND"}
            values[f"C_ADC_CM{n}{leg}"] = "1nF"
    pins.update({
        "U_AFE9": {
            "1": "VMID1_RAW", "2": "VMID1_RAW", "3": "VMID1_IN", "4": "GND",
            "5": "VMID2_IN", "6": "VMID2_RAW", "7": "VMID2_RAW", "8": "5V_OPA",
        },
        "R_VMID1_ISO": {"1": "VMID1_RAW", "2": "VMID1_BUF"},
        "C_VMID1_BUF": {"1": "VMID1_BUF", "2": "GND"},
        "R_VMID2_ISO": {"1": "VMID2_RAW", "2": "VMID2_BUF"},
        "C_VMID2_BUF": {"1": "VMID2_BUF", "2": "GND"},
        "C_FILT1_470U": {"1": "FILT1P", "2": "GND"},
        "C_FILT2_470U": {"1": "FILT2P", "2": "GND"},
    })
    values.update({
        "U_AFE9": "OPA2320AIDR",
        "R_VMID1_ISO": "1k", "C_VMID1_BUF": "4.7uF",
        "R_VMID2_ISO": "1k", "C_VMID2_BUF": "4.7uF",
        "C_FILT1_470U": "470uF", "C_FILT2_470U": "470uF",
    })
    for n in (1, 2):
        pins[f"R_VMID{n}_IN"] = {"1": f"VMID{n}_EXT", "2": f"VMID{n}_IN"}
        values[f"R_VMID{n}_IN"] = "10k"
        pins[f"R_VMID{n}_TOP"] = {"1": "3V3_ADC", "2": f"VMID{n}_EXT"}
        pins[f"R_VMID{n}_BOT"] = {"1": f"VMID{n}_EXT", "2": "GND"}
        values[f"R_VMID{n}_TOP"] = values[f"R_VMID{n}_BOT"] = "10k"
        for suffix, value in (("4U7", "4.7uF"), ("470N", "470nF")):
            ref = f"C_VMID{n}_{suffix}"
            pins[ref] = {"1": f"VMID{n}", "2": "GND"}
            values[ref] = value
        for suffix, value in (("10U", "10uF"), ("1U", "1uF")):
            ref = f"C_VMID{n}_EXT_{suffix}"
            pins[ref] = {"1": f"VMID{n}_EXT", "2": "GND"}
            values[ref] = value
        pins[f"R_FILT{n}P"] = {"1": "3V3_ADC", "2": f"FILT{n}P"}
        values[f"R_FILT{n}P"] = "1"
        for suffix, value in (("10U", "10uF"), ("1U", "1uF")):
            pins[f"C_FILT{n}_{suffix}"] = {"1": f"FILT{n}P", "2": "GND"}
            values[f"C_FILT{n}_{suffix}"] = value
    # ADR0025 replaces the buffered reference with passive1k dividers.
    for ref in ("U_AFE9","C_VMID1_BUF","C_VMID2_BUF",
                "R_VMID1_IN","R_VMID2_IN","R_VMID1_ISO","R_VMID2_ISO"):
        pins.pop(ref,None); values.pop(ref,None)
    for n in (1,2):
        values[f"R_VMID{n}_TOP"]=values[f"R_VMID{n}_BOT"]="1k"
    return pins, values


EXPECTED_PINS, EXPECTED_VALUES = _expected()
ADC_REFERENCE_PINS = {"1": "VMID1", "12": "VMID2", "17": "GND",
                      "18": "FILT2P", "43": "FILT1P", "44": "GND"}


def _normalize_value(value: str | None) -> str | None:
    """Normalize display-only KiCad unit spelling, not electrical magnitude.

    KiCad 10 writes resistor values produced as bare SI numbers by tscircuit
    with a trailing ohm glyph (for example ``300Ω``).  Capacitor spellings
    already carry their SI suffix.  Removing only the display glyph keeps the
    checker exact while accepting the native exporter representation.
    """

    if value is None:
        return None
    normalized = value.strip().replace("µ", "u").replace("μ", "u")
    normalized = re.sub(r"(?:Ω|ohms?)$", "", normalized, flags=re.IGNORECASE)
    return normalized.strip()


def validate(pins_by_ref: dict[str, dict[str, str]], values: dict[str, str]) -> dict:
    """Validate exact channel census, pin maps and critical values."""

    expected_afe = {f"U_AFE{n}" for n in range(1, 9)}
    actual_afe = {ref for ref in pins_by_ref if ref.startswith("U_AFE")}
    if actual_afe != expected_afe:
        raise TopologyError(f"U_AFE census {sorted(actual_afe)!r}, expected {sorted(expected_afe)!r}")
    expected_rx = {f"R_X{n}{leg}" for n in range(1, 9) for leg in ("P", "N")}
    actual_rx = {ref for ref in pins_by_ref if re.fullmatch(r"R_X\d+[PN]", ref)}
    if actual_rx != expected_rx:
        raise TopologyError(
            f"R_X census {sorted(actual_rx)!r}, expected {sorted(expected_rx)!r}"
        )
    expected_shunts = {f'C_FILTER{n}{leg}{k}' for n in range(1,9)
                       for leg in ('P','N') for k in (1,2)}
    actual_shunts = {ref for ref in pins_by_ref if ref.startswith('C_FILTER')}
    if actual_shunts != expected_shunts:
        raise TopologyError('C_FILTER census must contain exactly32 independent shunts')
    for ref in set(pins_by_ref) | set(values):
        if ref.startswith('C_DIFF'):
            raise TopologyError(f'{ref} forbidden: cross-leg capacitor retired by ADR0025')
        if ref.startswith('C'):
            legs = {net for net in pins_by_ref.get(ref, {}).values()
                    if re.fullmatch(r'FILTER\d+[PN]', net)}
            if len(legs) > 1:
                raise TopologyError(f'{ref} forbidden: capacitor bridges independent filter legs')
    for pin, expected in ADC_REFERENCE_PINS.items():
        if pins_by_ref.get("U_ADC", {}).get(pin) != expected:
            raise TopologyError(f"U_ADC.{pin} must be {expected}")
    for ref in ("R_FILT1N", "R_FILT2N"):
        if ref in pins_by_ref or ref in values:
            raise TopologyError(f"{ref} forbidden: FILT negative returns must be direct GND")
    for n in (1, 2):
        allowed = {("U_ADC", "1" if n == 1 else "12"),
                   (f"C_VMID{n}_4U7", "1"), (f"C_VMID{n}_470N", "1")}
        actual = {(ref, pin) for ref, pins in pins_by_ref.items()
                  for pin, net in pins.items() if net == f"VMID{n}"}
        if actual != allowed:
            raise TopologyError(f"ADC_VMID{n} must have decouplers only: {sorted(actual)}")
        allowed_bias={(f'R_VMID{n}_TOP','2'),(f'R_VMID{n}_BOT','1'),
                      (f'C_VMID{n}_EXT_10U','1'),(f'C_VMID{n}_EXT_1U','1')}
        allowed_bias.update((f'R_B{k}{leg}','2') for k in range(1 if n==1 else 5,5 if n==1 else 9) for leg in ('P','N'))
        actual_bias={(ref,pin) for ref,terminals in pins_by_ref.items() for pin,net in terminals.items() if net==f'VMID{n}_EXT'}
        if actual_bias!=allowed_bias:raise TopologyError(f'VMID{n}_EXT passive-bias owners')
    for ref, expected in EXPECTED_PINS.items():
        actual = pins_by_ref.get(ref)
        if actual != expected:
            raise TopologyError(f"{ref} pin map {actual!r}, expected {expected!r}")
    for ref, expected in EXPECTED_VALUES.items():
        actual = values.get(ref)
        if _normalize_value(actual) != _normalize_value(expected):
            raise TopologyError(f"{ref} value {actual!r}, expected {expected!r}")
    return {
        "schema": 2,
        "kind": "crow-carrier-analog-filter-topology",
        "status": "PASS",
        "channels": 8,
        "exact_amplifiers": 8,
        "reference_input_current_limit_resistors": 0,
        "input_current_limit_resistors": 16,
        "same_leg_feedback_resistors": 16,
        "independent_filter_shunts": 32,
        "vmid_isolation_networks": 0,
        "external_half_supply_dividers": 2,
        "direct_filt_negative_returns": 2,
        "adc_vmid_decoupler_only_nodes": 2,
        "polarized_adc_filter_bulk_caps": 2,
    }


def _shared_parser():
    repo = Path(__file__).resolve().parents[3]
    path = repo / "skills/kicad-pcb/scripts/kicad_sch_parity.py"
    spec = importlib.util.spec_from_file_location("carrier_kicad_parser", path)
    if spec is None or spec.loader is None:
        raise TopologyError(f"cannot load shared KiCad parser: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_netlist


def _balanced_forms(text: str, name: str) -> list[str]:
    forms: list[str] = []
    for match in re.finditer(r"\(\s*" + re.escape(name) + r"\b", text):
        depth = 0
        quoted = False
        escaped = False
        for index in range(match.start(), len(text)):
            char = text[index]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    forms.append(text[match.start():index + 1])
                    break
        else:
            raise TopologyError(f"unterminated {name} form")
    return forms


def _field(form: str, name: str) -> str:
    match = re.search(r"\(\s*" + re.escape(name) + r'\s+"([^"\\]*)"\s*\)', form)
    return match.group(1) if match else ""


def _native_values(forms: list[str], parts: Path) -> dict[str, str]:
    """Interpret native Values through exact dossier identity, never refdes.

    The shared converter emits supplier codes for non-R/C parts. Resolve a
    code only against one dossier's manufacturer/MPN/FPID, including the
    actual native footprint. Do not infer an MPN from its directory name or
    use expected circuit values to repair the artifact being checked.
    Passive display values remain measurements from the native netlist.
    """
    by_token: dict[str, list[tuple[Path, dict]]] = {}
    for dossier in sorted(parts.glob('*/part.yaml')):
        try:
            record = yaml.safe_load(dossier.read_text(encoding='utf-8'))
        except yaml.YAMLError as exc:
            raise TopologyError(f'unparseable part authority: {dossier}') from exc
        if not isinstance(record, dict):
            raise TopologyError(f'unparseable part authority: {dossier}')
        sourcing = record.get('sourcing', {})
        code = sourcing.get('lcsc') if isinstance(sourcing, dict) else None
        seen = set()
        for token in (record.get('mpn'), code):
            if token is None or token == '':
                continue
            if not isinstance(token, str):
                raise TopologyError(f'non-string identity in {dossier}')
            if token not in seen:
                by_token.setdefault(token, []).append((dossier, record))
                seen.add(token)

    values: dict[str, str] = {}
    for form in forms:
        ref, raw = _field(form, 'ref'), _field(form, 'value').strip()
        if not ref or not raw:
            raise TopologyError('native component missing reference or value')
        if ref in values:
            raise TopologyError(f'duplicate native component: {ref}')
        matches = by_token.get(raw, [])
        if re.fullmatch(r'C\d+', raw) and not matches:
            raise TopologyError(f'{ref}: unresolved supplier code {raw} in {parts}')
        if len(matches) > 1:
            raise TopologyError(f'{ref}: ambiguous part identity {raw}: '
                                + ', '.join(str(path) for path, _ in matches))
        if matches:
            dossier, record = matches[0]
            if any(not isinstance(record.get(key), str) or not record[key].strip()
                   for key in ('mpn', 'manufacturer', 'footprint')):
                raise TopologyError(f'{ref}: incomplete part identity in {dossier}')
            footprint = _field(form, 'footprint')
            if footprint != record['footprint']:
                raise TopologyError(f'{ref}: footprint {footprint!r} differs from '
                                    f'{raw} authority {record["footprint"]!r}')
            values[ref] = record['mpn']
        else:
            values[ref] = _normalize_value(raw)
    if not values:
        raise TopologyError('native component value coverage is zero')
    return values


def parse_native_netlist(path: Path, *, parts: Path | None = None
                         ) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    if not text.lstrip().startswith("(export"):
        raise TopologyError("input is not a KiCad native S-expression netlist")
    net_to_nodes, no_connects = _shared_parser()(path, {}, {})
    if not net_to_nodes:
        raise TopologyError("shared parser found zero connected nets")
    pins: dict[str, dict[str, str]] = {}
    for net, nodes in net_to_nodes.items():
        for ref, pin in nodes:
            refpins = pins.setdefault(ref, {})
            if pin in refpins:
                raise TopologyError(f"{ref}.{pin} appears on two nets")
            refpins[pin] = net
    for ref, pin in no_connects:
        pins.setdefault(ref, {})[pin] = ""
    if parts is None:
        parts = Path(__file__).resolve().parents[1] / '02_parts'
    values = _native_values(_balanced_forms(text, 'comp'), parts)
    if missing := set(pins) - set(values):
        raise TopologyError(f'native pins lack component values: {sorted(missing)}')
    return pins, values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("netlist", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        primary = Path(__file__).resolve().parents[1] / "02_parts/CS5308P-DN/CS5308P_DS1314F1.pdf"
        if hashlib.sha256(primary.read_bytes()).hexdigest() != "6ca42cc09ac47ebdacacaee435f05e3f9c34b83d5692e52a2d8a26533e810e57":
            raise TopologyError("DS1314F1 authority changed; rederive Fig2-2/4.5.6")
        receipt = validate(*parse_native_netlist(args.netlist))
    except (OSError, TopologyError) as exc:
        print(f"ANALOG-FILTER FAIL: {exc}")
        return 1
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("ANALOG-FILTER PASS: 8 same-leg channels, 32 independent shunts, 2 passive VMID dividers, 2 direct FILT returns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
