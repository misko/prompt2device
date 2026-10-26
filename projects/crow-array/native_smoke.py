#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Isolated native replot check of the public subset, not full release replay."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

import publication as p

sys.dont_write_bytecode = True
sys.path.insert(0, str(p.ROOT.parents[1]/'vnext/tools'))
import fab_replay as f


def check(package):
    before = p.verify(package)
    manifest = p.load(package,'publication.json')
    p.require(f.p.pcb.Version()=='10.0.4','requires KiCad 10.0.4')
    results={}
    for board, roles in manifest['native'].items():
        pcb=package/roles['pcb']; sch=package/roles['schematic']
        resources=sorted(x.relative_to(pcb.parent).as_posix() for x in pcb.parent.rglob('*')
                         if x.is_file() and x not in (pcb,pcb.with_suffix('.kicad_pro')))
        entry=dict(native=roles['pcb'].removeprefix('native/'),
                   project=roles['project'].removeprefix('native/'),resources=resources)
        with tempfile.TemporaryDirectory(prefix='crow-public-native-') as tmp:
            scratch=Path(tmp)
            result=f.regenerate(package/'native',board,entry,scratch/'fab',sch)
            with zipfile.ZipFile(package/f'fab/{board}/{board}-gerbers.zip') as z:
                p.require(set(z.namelist())==set(result['members']),'plot member mismatch')
                for name in z.namelist():
                    p.require(f.fab.canonical_plot(package/f'fab/{board}/plots/{name}') ==
                              f.fab.canonical_plot(scratch/'fab/plots'/name),
                              'replot geometry differs: '+name)
            for name in f.PDF_NAMES:
                p.require(f.imported.native.raster_hashes(package/f'pdf/{board}/{name}',scratch/('old-'+name)) ==
                          f.imported.native.raster_hashes(scratch/'fab/pdf'/name,scratch/('new-'+name)),
                          'rendered PCB PDF differs: '+name)
            shutil.copytree(sch.parent,scratch/'schematic')
            f.p.command(['kicad-cli','sch','export','pdf','-o',str(scratch/'schematic.pdf'),
                         str(scratch/'schematic'/sch.name)])
            p.require(f.imported.native.raster_hashes(package/f'pdf/{board}/schematic.pdf',scratch/'old-sch') ==
                      f.imported.native.raster_hashes(scratch/'schematic.pdf',scratch/'new-sch'),
                      'rendered schematic PDF differs')
            drc=p.load(scratch,'fab/drc.json')
            results[board]=dict(plots=len(result['members']),pdfs=4,
                violations=len(drc['violations']),unconnected=len(drc['unconnected_items']),
                schematic_parity=len(drc['schematic_parity']),native_refill_unchanged=True)
    p.require(p.verify(package)==before,'package changed during native check')
    return dict(scope='public native 2D replot only; not full sealed replay or engineering acceptance',
                package_id=p.IDENTITY,package_manifest_sha256=p.digest(package/'publication.json'),
                verifier_sha256=p.digest(Path(__file__)),kicad='10.0.4',boards=results,
                order='DO-NOT-ORDER',original_archive_accessed=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=p.DEFAULT)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    p.require(not args.output.exists(),'output must be absent')
    result=check(args.package.resolve())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    p.write_json(args.output,result)
    print(json.dumps(result,indent=2))
