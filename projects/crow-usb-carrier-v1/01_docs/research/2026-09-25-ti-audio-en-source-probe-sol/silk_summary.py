#!/usr/bin/env python3
"""Compare generator WARN silk ownership refs in baseline/trial logs."""
import json, re, sys
from pathlib import Path

if len(sys.argv)!=3:raise SystemExit('usage: silk_summary.py BASELINE_LOG TRIAL_LOG')
def refs(path):
    return set(re.findall(r"^WARN silk ownership: refdes '([^']+)'",
                          Path(path).read_text(),re.M))
before,after=map(refs,sys.argv[1:])
print(json.dumps({'baseline_degraded_ref_count':len(before),
                  'trial_degraded_ref_count':len(after),
                  'new_degraded_refs':sorted(after-before),
                  'cleared_degraded_refs':sorted(before-after)},indent=2))
