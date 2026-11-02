"""Scoped connector diagnostic: native copper + pad-fitted public catalog CAD.

Run with /usr/bin/python3. This is NOT a full JLC twin/assembly acceptance.
Never changes source boards or CPL. Other component bodies are deliberately absent.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pcbnew

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ORDER = HERE.parent
sys.path.insert(0, str(ROOT / 'skills/jlcpcb-fab/scripts'))
import jlc_twin as twin


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cache = HERE / 'catalog'
    if not cache.exists():
        shutil.copytree('/tmp/crow-orientation-catalog', cache)
    evidence = {'scope': 'CONNECTOR_DIAGNOSTIC_ONLY', 'accepted': False,
                'limitations': ['Public catalog CAD is not a captured JLC draft preview.',
                                'No complete body census, plug-fit or factory acceptance.',
                                'Other component bodies deliberately omitted.'],
                'boards': {}, 'catalog_hashes': {}}
    for path in cache.rglob('*'):
        if path.is_file():
            evidence['catalog_hashes'][str(path.relative_to(HERE))] = sha(path)
    for name in ('carrier', 'pod'):
        src = ORDER / f'quote-draft/r10-2c8p-outward-power/native/pcb/{name}/{name}.kicad_pcb'
        before = sha(src)
        board = pcbnew.LoadBoard(str(src))
        rows = []
        for fp in board.GetFootprints():
            ref = fp.GetReference()
            fp.Models().clear()
            if not ref.startswith('J'):
                continue
            power = name == 'carrier' and ref == 'J1'
            code = 'C3096093' if power else 'C599441'
            mod = next((cache/code/'jlc.pretty').glob('*.kicad_mod'))
            vendor = pcbnew.FootprintLoad(str(mod.parent), mod.stem)
            twin.rebase_cached_model_paths(vendor, mod)
            ours = twin.pads_of(fp, footprint_local=True)
            theirs = twin.pads_of(vendor, footprint_local=True)
            assert set(ours) == set(theirs)
            oc, jc = twin.centroid(ours), twin.centroid(theirs)
            fits = twin.best_fit(twin.centered(ours), twin.centered(theirs))
            error, mirrored, angle = fits[0]
            assert not mirrored and error < .03, (ref, fits)
            pegs = []
            native_pegs = [p for p in fp.Pads() if not p.GetNumber()]
            for p in vendor.Pads():
                if p.GetNumber():
                    continue
                x, y = p.GetPosition().x/1e6, p.GetPosition().y/1e6
                dx, dy = twin.local_to_board(x-jc[0], y-jc[1], angle)
                dx, dy = twin.local_to_board(dx+oc[0], dy+oc[1], fp.GetOrientationDegrees())
                actual = [fp.GetPosition().x/1e6+dx, fp.GetPosition().y/1e6+dy]
                residual = min(((p.GetPosition().x/1e6-actual[0])**2 +
                                (p.GetPosition().y/1e6-actual[1])**2)**.5 for p in native_pegs)
                assert residual < .03
                pegs.append({'position_mm': actual, 'error_mm': residual})
            for jm in vendor.Models():
                m = pcbnew.FP_3DMODEL()
                m.m_Filename = jm.m_Filename
                m.m_Scale = jm.m_Scale
                m.m_Rotation = jm.m_Rotation
                bx, by = twin.xform({'p': [(jm.m_Offset.x-jc[0], -jm.m_Offset.y-jc[1])]}, angle, False)['p'][0]
                m.m_Offset.x, m.m_Offset.y = bx+oc[0], -(by+oc[1])
                m.m_Offset.z = jm.m_Offset.z
                m.m_Rotation.z = (jm.m_Rotation.z-angle) % 360
                fp.Models().push_back(m)
            rows.append({'ref': ref, 'lcsc': code, 'catalog_to_native_local_rotation': angle,
                         'native_rotation': fp.GetOrientationDegrees(), 'max_pad_error_mm': error,
                         'all_fit_candidates': fits, 'peg_witnesses': pegs,
                         'native_numbered_pads_mm': twin.pads_of(fp)})
        dst = HERE / f'{name}-catalog-diagnostic.kicad_pcb'
        pcbnew.SaveBoard(str(dst), board)
        evidence['boards'][name] = {'source': str(src.relative_to(ROOT)), 'sha256': before,
                                   'diagnostic_board_sha256': sha(dst), 'connectors': rows}
        for view, angles in [('top', None), ('front45', '45,0,0'), ('oblique45', '45,0,-25'), ('opposite45', '315,0,0')]:
            command = ['kicad-cli', 'pcb', 'render', '--width', '2200', '--height', '1300',
                       '--background', 'opaque', '--quality', 'high', '--side', 'top',
                       '--output', str(HERE/f'{name}-{view}.png')]
            if angles:
                command += ['--rotate', angles]
            result = subprocess.run(command+[str(dst)], capture_output=True, text=True)
            (HERE/f'{name}-{view}.log').write_text(result.stdout+result.stderr)
            result.check_returncode()
        assert sha(src) == before
    (HERE/'evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(json.dumps(evidence['boards'], indent=2))


if __name__ == '__main__':
    main()
