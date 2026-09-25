#!/usr/bin/env python3
"""Replay one selected first-ILIM-via candidate against the pinned recut probe."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/'2026-09-25-ti-tps26625-placement-return-sol/probe.py'
spec=importlib.util.spec_from_file_location('prior_recut',PRIOR)
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
probe.HERE=HERE
probe.ILIM=[(191.4,48.0),(192.2,47.8),(191.825,50.2),(191.825,51.0)]
probe.main()
