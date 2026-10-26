#!/usr/bin/env python3
"""Read-only recovery observations; not an acceptance or ordering adapter."""
import concurrent.futures
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2] / 'vnext/tools'))
from stock_lookup import fetch, discover, public_evidence


def product_offers(body, mpn, code=None):
    """Only exact Product identity; ignore generic navigation and related products."""
    results = []
    for match in re.finditer(r'<script[^>]*type=[\"\x27]application/ld\+json[\"\x27][^>]*>(.*?)</script>', body, re.S):
        try:
            obj = json.loads(html.unescape(match[1]))
        except ValueError:
            continue
        candidates = obj if isinstance(obj, list) else [obj]
        for p in candidates:
            if not isinstance(p, dict) or p.get('@type') != 'Product':
                continue
            if p.get('mpn') != mpn or (code and p.get('sku') != code):
                continue
            results.append({k: p[k] for k in ('mpn', 'sku', 'brand', 'offers') if k in p})
    return results


SUBJECTS = [
    ('TPS70933DBVR', 10, 'C89347', 'https://jlcpcb.com/partdetail/TPS70933DBVR/C89347'),
    ('BZT52C3V9-7-F', 80, 'C154917', 'https://jlcpcb.com/partdetail/DiodesIncorporated-BZT52C3V9_7F/C154917'),
    ('GRM32ER71A476KE15L', 10, 'C84494', 'https://jlcpcb.com/partdetail/MurataElectronics-GRM32ER71A476KE15L/C84494'),
    ('GRM31MR71E225KA93L', 80, 'C97962', 'https://www.lcsc.com/product-detail/C97962.html'),
    ('BAT54S-7-F', 20, 'C83574', 'https://www.lcsc.com/product-detail/Schottky-Barrier-Diodes-SBD_Diodes-Incorporated-BAT54S-7-F_C83574.html'),
    ('RJHSE-5080', 50, 'C599441', 'https://jlcpcb.com/partdetail/AmphenolICC-RJHSE5080/C599441'),
]


def observe(subject):
    mpn, need, code, supplier_url = subject
    record = dict(mpn=mpn, installed_need=need, code=code, authority='OBSERVATIONS_ONLY')
    url = 'https://jlcsearch.tscircuit.com/api/search?' + urlencode(dict(q=code, limit=20, full='true'))
    try:
        body, provenance = fetch(url)
        payload = json.loads(body)
        record['discovery'] = dict(provenance=provenance, raw=payload, **discover(payload, mpn, need))
    except (OSError, ValueError, TimeoutError) as e:
        record['discovery'] = dict(error=str(e), request_url=url)
    try:
        body, provenance = fetch(supplier_url)
        record['supplier'] = dict(provenance=provenance,
                                  exact_product_offers=product_offers(body, mpn, code),
                                  identity_fields=public_evidence(body, mpn, code))
    except (OSError, ValueError, TimeoutError) as e:
        record['supplier'] = dict(error=str(e), request_url=supplier_url)
    return record


if __name__ == '__main__':
    path = Path(sys.argv[1])
    if path.exists():
        raise SystemExit('Refusing to overwrite retained observations')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(observe, SUBJECTS))
    with path.open('x') as stream:
        json.dump(records, stream, indent=2)
        stream.write('\n')
    for r in records:
        print(json.dumps(r, ensure_ascii=False))
