#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""One bounded aggregate discovery screen, never JLC stock/order acceptance."""
import concurrent.futures
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
import publication
sys.path.insert(0,str(ROOT.parents[2]/'vnext/tools'))
import stock_lookup


def run(output, lookup=stock_lookup.lookup):
    publication.verify(publication.DEFAULT)
    path=publication.DEFAULT/'fab/assembly/demand.csv'
    rows=list(csv.DictReader(path.open()))
    assert len(rows)==38 and sum(int(r['quantity']) for r in rows)==1000
    assert len({(r['manufacturer'],r['mpn']) for r in rows})==38
    output.mkdir(parents=True,exist_ok=False)
    def one(row):
        evidence=lookup(row['mpn'],int(row['quantity']))
        return dict(subject=row,evidence=evidence)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(one,rows))
    record=dict(scope='Aggregate discovery only; exact supplier confirmation and allocation OPEN',
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                demand_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                lookup_tool_sha256=hashlib.sha256(Path(stock_lookup.__file__).read_bytes()).hexdigest(),
                boards=publication.BOARDS,installed_need=1000,spares_authorized=0,results=results)
    (output/'observations.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    counts={}
    for r in results:
        e=r['evidence'];matches=e.get('matches',[])
        label=('reported_sufficient' if any(x['status']=='reported_sufficient' for x in matches)
               else e['lookup_state'])
        counts[label]=counts.get(label,0)+1
    print(json.dumps(dict(counts=counts,acceptance='NONE',evidence=str(output/'observations.json')),indent=2))


if __name__=='__main__':
    run(Path(sys.argv[1]).resolve())
