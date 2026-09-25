#!/usr/bin/env python3
"""Compare old union and southwest-cap source trial under exact TI native profile."""
from __future__ import annotations
import hashlib, importlib.util, shutil, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
PRIOR=ROOT/'projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-iso8-profile-replay-sol/replay.py'
EXPECTED_REPLAY='70d2c80368fed340c008f83b2925d74cc1970dc916c5fde5bfc7bb92c6809291'
OLD=ROOT/'projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-integrated-placement-sol/candidate.kicad_pcb'
NEW=HERE/'candidate.kicad_pcb'
SHA={'baseline':'20373950748ac51113b115b2d12d169160c24024a2a000572bb70c67b0f60919',
     'candidate':'0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if sha(PRIOR)!=EXPECTED_REPLAY or sha(OLD)!=SHA['baseline'] or sha(NEW)!=SHA['candidate']:
        raise SystemExit('profile replay or board SHA drift')
    spec=importlib.util.spec_from_file_location('pofv_replay',PRIOR)
    replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
    replay.INPUTS['baseline']=OLD;replay.INPUTS['candidate']=NEW
    replay.EXPECTED.update(SHA)
    with tempfile.TemporaryDirectory(prefix='crow-cap-profile-receipt-') as d:
        replay.HERE=Path(d)
        replay.main()
        shutil.copy2(Path(d)/'receipt.json',HERE/'profile_receipt.json')

if __name__=='__main__':main()
