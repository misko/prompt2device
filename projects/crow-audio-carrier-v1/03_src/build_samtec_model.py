#!/usr/bin/env python3
"""Reproduce the drawing-derived Samtec TMM-106-01-L-D reference model.

STOPGAP backend gap: the shared backend has no manufacturer-drawing package
geometry schema. A future package-model declaration would select these exact
style-01 dimensions and output path. Geometry and native coordinate encoding
remain owned by build_package_models.py; this wrapper selects its Samtec entry.
"""
import argparse
import hashlib
from pathlib import Path

from build_package_models import encode, samtec_tmm_106_01_l_d


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,
                        default=Path(__file__).parent/'lib/3dmodels/derived/connectors')
    args=parser.parse_args();args.out_dir.mkdir(parents=True,exist_ok=True)
    name='Samtec_TMM-106-01-L-D_reference.wrl'
    data=encode(samtec_tmm_106_01_l_d()).encode()
    (args.out_dir/name).write_bytes(data)
    print(hashlib.sha256(data).hexdigest(),name)


if __name__=='__main__':
    main()
