#!/usr/bin/env python3
"""Crow TMUX4827 conditional 3x3 center-via escape, with tamper guards."""
import hashlib
import shutil
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import KPY, ROOT, must_fail, must_pass, run, test, tmpdir, main, contains  # noqa: E402

TOOL = ROOT / 'skills/kicad-pcb/scripts/escape_check.py'
FIXTURE = ROOT / 'tests/fixtures/tmux4827_center_via'
MPN = 'TMUX4827YBHR'


def fixture():
    d = tmpdir('center_bga_')
    p = d / '02_parts' / MPN
    p.mkdir(parents=True)
    for name in ('part.yaml', 'native.kicad_mod', 'coupon.kicad_pcb'):
        shutil.copy2(FIXTURE / name, p / name)
    return p / 'part.yaml', p / 'native.kicad_mod', p / 'coupon.kicad_pcb'


def update(path, edit):
    data = yaml.safe_load(path.read_text())
    edit(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False))


@test('exact Crow center-via evidence earns conditional advanced4L feasibility')
def t_center_crow_pass():
    part, _fp, _coupon = fixture()
    r = must_pass(run([KPY, TOOL, part]), 'exact coupon-bound topology')
    contains(r.out, 'P-ESC PASS', 'nonzero conditional source feasibility')


@test('center-via escape rejects cheaper non-via-in-pad tier', kind='known_bad')
def t_center_wrong_tier():
    part, _fp, _coupon = fixture()
    update(part, lambda d: d['escape'].__setitem__('tier_required', 'jlc_4layer_standard'))
    must_fail(run([KPY, TOOL, part]), 'standard tier', 'conditional escape requires tier jlc_4layer_advanced')


@test('center-via escape rejects BGA copper gap below JLC floor', kind='known_bad')
def t_center_gap():
    part, _fp, _coupon = fixture()
    update(part, lambda d: d['escape']['center_via_topology'].__setitem__('center_via_diameter_mm', 0.36))
    must_fail(run([KPY, TOOL, part]), '0.095 mm gap', 'NO known tier')


@test('center-via escape rejects drill unlike reviewed coupon', kind='known_bad')
def t_center_drill():
    part, _fp, _coupon = fixture()
    update(part, lambda d: d['escape']['center_via_topology'].__setitem__('center_via_drill_mm', 0.349))
    must_fail(run([KPY, TOOL, part]), 'near-zero annulus', 'NO known tier')


@test('center-via escape rejects an opening unlike reviewed coupon', kind='known_bad')
def t_center_tiny_opening():
    part, fp, _coupon = fixture()
    fp.write_text(fp.read_text().replace('(solder_mask_margin -0.05) (solder_paste_margin -0.05)',
                                         '(solder_mask_margin -0.17) (solder_paste_margin -0.17)'))
    def edit(d):
        t = d['escape']['center_via_topology']
        t['center_mask_opening_mm'] = 0.01
        t['native_footprint']['sha256'] = hashlib.sha256(fp.read_bytes()).hexdigest()
    update(part, edit)
    must_fail(run([KPY, TOOL, part]), 'tiny self-consistent opening', 'NO known tier')


@test('center-via escape rejects changed pitch despite self-consistent native', kind='known_bad')
def t_center_pitch():
    part, _fp, _coupon = fixture()
    update(part, lambda d: d['escape'].__setitem__('pitch', 0.41))
    must_fail(run([KPY, TOOL, part]), 'coupon pitch', 'NO known tier')


@test('center-via escape rejects changed coupon bytes', kind='known_bad')
def t_center_coupon_tamper():
    part, _fp, coupon = fixture()
    coupon.write_bytes(coupon.read_bytes() + b'\n; tampered\n')
    must_fail(run([KPY, TOOL, part]), 'coupon digest mismatch', 'coupon missing or SHA-256 mismatch')


@test('center-via escape rejects native ball movement even with refreshed hash', kind='known_bad')
def t_center_footprint_tamper():
    part, fp, _coupon = fixture()
    fp.write_text(fp.read_text().replace('(at 0.4 -0.4)', '(at 0.45 -0.4)', 1))
    update(part, lambda d: d['escape']['center_via_topology']['native_footprint'].__setitem__(
        'sha256', hashlib.sha256(fp.read_bytes()).hexdigest()))
    must_fail(run([KPY, TOOL, part]), 'native geometry mismatch', 'native footprint ball A3 geometry differs')


@test('center-via escape rejects self-hashed copper-layer deletion', kind='known_bad')
def t_center_no_copper():
    part, fp, _coupon = fixture()
    fp.write_text(fp.read_text().replace('(layers "F.Cu" "F.Paste" "F.Mask")',
                                         '(layers "F.Paste" "F.Mask")', 1))
    update(part, lambda d: d['escape']['center_via_topology']['native_footprint'].__setitem__(
        'sha256', hashlib.sha256(fp.read_bytes()).hexdigest()))
    must_fail(run([KPY, TOOL, part]), 'no pad copper', 'reviewed exact copper/mask/paste lands')


@test('center-via escape rejects non-ground interior ball', kind='known_bad')
def t_center_wrong_net():
    part, _fp, _coupon = fixture()
    update(part, lambda d: d['pins'].__setitem__('5', 'VDD'))
    must_fail(run([KPY, TOOL, part]), 'center must be GND', 'B2 GND')


@test('center-via escape rejects swapped perimeter ball functions', kind='known_bad')
def t_center_swapped_functions():
    part, _fp, _coupon = fixture()
    def swap(d):
        d['pins']['1'], d['pins']['8'] = d['pins']['8'], d['pins']['1']
    update(part, swap)
    must_fail(run([KPY, TOOL, part]), 'exact TI function map', 'exact TI TMUX4827 ball functions')


@test('center-via evidence cannot bypass validation by shrinking pins', kind='known_bad')
def t_center_two_pins():
    part, _fp, _coupon = fixture()
    update(part, lambda d: d.__setitem__('pins', {'1': 'S1A_UNUSED', '2': 'SEL'}))
    must_fail(run([KPY, TOOL, part]), 'two-pin bypass', 'exact numeric pads')


@test('center-via evidence cannot bypass validation as off-board', kind='known_bad')
def t_center_offboard():
    part, _fp, _coupon = fixture()
    update(part, lambda d: d.__setitem__('footprint', 'none_off_board'))
    must_fail(run([KPY, TOOL, part]), 'off-board bypass', 'contradicts')


@test('center-via escape rejects arbitrary self-hashed coupon', kind='known_bad')
def t_center_self_hashed_coupon():
    part, _fp, coupon = fixture()
    coupon.write_text('not a KiCad board')
    update(part, lambda d: d['escape']['center_via_topology']['coupon'].__setitem__(
        'sha256', hashlib.sha256(coupon.read_bytes()).hexdigest()))
    must_fail(run([KPY, TOOL, part]), 'reviewed coupon identity', 'independently reviewed exact diagnostic board')


@test('center-via escape requires explicit conditional state', kind='known_bad')
def t_center_no_condition():
    part, _fp, _coupon = fixture()
    update(part, lambda d: d['escape'].__setitem__('conditions', []))
    must_fail(run([KPY, TOOL, part]), 'cannot claim unconditional', 'conditional escape requires tier')


@test('center-via escape rejects non-finite topology dimension', kind='known_bad')
def t_center_nan():
    part, _fp, _coupon = fixture()
    update(part, lambda d: d['escape']['center_via_topology'].__setitem__('land_diameter_mm', float('nan')))
    must_fail(run([KPY, TOOL, part]), 'NaN land size', 'NO known tier')


if __name__ == '__main__':
    sys.exit(main())
