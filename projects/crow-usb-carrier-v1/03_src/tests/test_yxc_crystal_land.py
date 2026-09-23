"""YXC YSX321SL p1 top-view terminal and recommended-land parity.

Manufacturer drawing: upper row 4,3; lower row 1,2. tscircuit uses Y-up;
KiCad footprint coordinates use Y-down (circuit_json_to_kicad_pcb.py:202).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TSX = ROOT / '03_tscircuit/src/crow_usb_digital.tsx'
MOD = ROOT / '03_src/lib/crow_usb_digital.pretty/YXC_YSX321SL_3225_4Pin.kicad_mod'
CONVERTER = Path(__file__).resolve().parents[4] / 'skills/kicad-pcb/scripts/circuit_json_to_kicad_pcb.py'

# Exact YXC primary p1: 1/3 crystal, 2/4 cover ground; 1.4 x 1.2 mm
# suggested pads on 2.2 x 1.7 mm centers, seen from the component top.
EXPECTED_NATIVE = {1: (-1.1, 0.85), 2: (1.1, 0.85),
                   3: (1.1, -0.85), 4: (-1.1, -0.85)}


def test_yxc_primary_top_view_and_transform():
    src = TSX.read_text()
    native = MOD.read_text()
    converter = CONVERTER.read_text()
    assert 'ky = oy - ty' in converter, 'tCircuit to KiCad Y transform changed'
    tsx_land = re.search(r'function YxcYSX321SLLand\(\).*?</footprint>}', src)
    assert tsx_land, 'YXC authored TSX land absent'
    tsx_pads = {
        int(n): (float(x), float(y), float(w), float(h))
        for n, x, y, w, h in re.findall(
            r'<P n=\{(\d+)\} x=\{([-\d.]+)\} y=\{([-\d.]+)\} '
            r'w=\{([-\d.]+)\} h=\{([-\d.]+)\}/>', tsx_land.group())
    }
    native_pads = {
        int(n): (float(x), float(y), float(w), float(h))
        for n, x, y, w, h in re.findall(
            r'\(pad "(\d+)" smd rect \(at ([-\d.]+) ([-\d.]+)\) '
            r'\(size ([-\d.]+) ([-\d.]+)\)', native)
    }
    assert set(tsx_pads) == set(native_pads) == {1, 2, 3, 4}
    for pin, (x, y) in EXPECTED_NATIVE.items():
        assert native_pads[pin] == (x, y, 1.4, 1.2), pin
        assert tsx_pads[pin] == (x, -y, 1.4, 1.2), pin
    assert '(fp_rect (start -1.6 -1.25) (end 1.6 1.25)' in native
    assert '(layer "F.Fab")' in native
    assert '(fp_rect (start -2.4 -1.85) (end 2.4 1.85)' in native
    assert '(layer "F.CrtYd")' in native
    assert '(fp_circle (center -2.1 1.60)' in native
    assert 'pin1:n("XTAL_IN_R"),pin2:n("GND"),pin3:n("XTAL_OUT"),pin4:n("GND")' in src


if __name__ == '__main__':
    test_yxc_primary_top_view_and_transform()
    print('YXC primary terminal map and TSX/native land parity: PASS')
