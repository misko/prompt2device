#!/usr/bin/env python3
"""Project procurement worksheet; never produces a vendor-ready BOM or receipt."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
from pathlib import Path

from exact_stock_recovery import ROOT, observe

RELEASE = ROOT.parent / 'releases/crow-prototype-v3-first-run-5c10p-public-v1'
ASSEMBLY = RELEASE / 'fab/assembly'
# User-selected ownership, 2026-10-26. Requested JLC work is not vendor acceptance.
MANUAL_ROUTES = {
    'SC0915': 'user_pico_installation',
    'CMA-4544PF-W': 'user_acoustic_hand_solder',
    'CPE-203': 'user_acoustic_hand_solder',
    'RJHSE-5080': 'jlc_manual_requested_pending_acceptance',
    'PJ-102AH': 'jlc_manual_requested_pending_acceptance',
    'R-78E5.0-0.5': 'jlc_manual_requested_pending_acceptance',
}
ALIASES = {
    'Amphenol': {'Amphenol ICC', 'Amphenol'},
    'Diodes Incorporated': {'DIODES', 'Diodes Incorporated'},
    'Littelfuse': {'Littelfuse'},
    'Murata': {'muRata', 'Murata Electronics'},
    'RECOM Power': {'Recom Power', 'RECOM Power'},
    'Samsung Electro-Mechanics': {'Samsung Electro-Mechanics', 'SAMSUNG'},
    'TDK': {'TDK'},
    'Texas Instruments': {'Texas Instruments', 'TI'},
    'Vishay': {'VISHAY', 'Vishay Intertech'},
    'Vishay Dale': {'VISHAY', 'Vishay Intertech'},
    'onsemi': {'onsemi', 'ON Semiconductor', 'ON'},
}


def csv_rows(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def stock_state(offer, need):
    """No pooling, no positive badge overriding insufficient published quantity."""
    if not isinstance(offer, dict):
        return 'unknown'
    count = offer.get('inventoryLevel')
    if isinstance(count, dict):
        count = count.get('value')
    if type(count) in (int, float) and count >= 0:
        if count < need:
            return 'insufficient'
        if offer.get('availability', '').endswith('/OutOfStock'):
            return 'conflicting'
        return 'displayed_sufficient'
    availability = offer.get('availability', '')
    if availability.endswith('/InStock'):
        return 'in_stock_quantity_unknown'
    if availability.endswith('/OutOfStock'):
        return 'out_of_stock'
    return 'unknown'


def disposition(subject, obs):
    supplier = obs.get('supplier', {}) if obs else {}
    offers = supplier.get('exact_product_offers', [])
    matches = []
    for p in offers:
        brand = p.get('brand', {})
        brand = brand.get('name') if isinstance(brand, dict) else brand
        if (p.get('mpn') == subject['mpn'] and p.get('sku') == obs.get('code')
                and brand in ALIASES.get(subject['manufacturer'], {subject['manufacturer']})):
            matches.append(p)
    if not matches:
        return 'identity_or_lookup_pending', 'unknown'
    states = {stock_state(p.get('offers'), int(subject['quantity'])) for p in matches}
    if len(states) != 1:
        return 'conflicting_supplier_observations', 'conflicting'
    return 'exact_maker_mpn_code', states.pop()


def collect(output):
    if output.exists():
        raise ValueError('Refusing to overwrite observations')
    need = {r['mpn']: int(r['quantity']) for r in csv_rows(ASSEMBLY / 'demand.csv')}
    leads = csv_rows(ROOT / 'catalog-leads-20261026.csv')
    assert len({r['mpn'] for r in leads}) == len(leads)
    old = {r['mpn']: r for r in json.loads((ROOT / 'code-stock-recovery-20261026.json').read_text())}
    def one(lead):
        mpn = lead['mpn']
        if mpn in old:
            assert old[mpn]['code'] == lead['code'] and old[mpn]['installed_need'] == need[mpn]
            return dict(old[mpn], reused_from='code-stock-recovery-20261026.json')
        return observe((mpn, need[mpn], lead['code'], lead['supplier_url']))
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(one, leads))
    with output.open('x') as f:
        json.dump(rows, f, indent=2)
        f.write('\n')
    for r in rows:
        print(r['mpn'], r['code'], len(r.get('supplier', {}).get('exact_product_offers', [])))


def build(observations, output):
    if output.exists():
        raise ValueError('Refusing to overwrite worksheet')
    demand = csv_rows(ASSEMBLY / 'demand.csv')
    population = csv_rows(ASSEMBLY / 'population.csv')
    observed = {r['mpn']: r for r in json.loads(observations.read_text())}
    fallback = {r['mpn']: r for r in csv_rows(ROOT / 'supplier-observations-20261026.csv')}
    # OR3 supersedes the inadequate OR2 TDK offer and old Panasonic page locator.
    fallback['C3216X7R1V106K160AC']['supplier_url'] = json.loads(
        (ROOT / 'buerklin-20261026.json').read_text())['provenance']['url']
    fallback['ERJ-3EKF68R0V']['supplier_url'] = (
        'https://www.digikey.com/en/products/detail/panasonic-industry/ERJ-3EKF68R0V/1746805')
    fields = ['manufacturer', 'mpn', 'installed_need', 'carrier_refs', 'pod_refs',
              'native_footprints', 'population_mode', 'catalog_code', 'identity_status',
              'supplier_stock_observation', 'supplier_url', 'evidence_file',
              'fallback_url', 'proposed_route', 'remaining_check']
    rows = []
    for d in demand:
        mpn = d['mpn']
        refs = [r for r in population if r['mpn'] == mpn and r['manufacturer'] == d['manufacturer']]
        assert sum(int(r['demand']) for r in refs) == int(d['quantity'])
        modes = {r['mode'] for r in refs}
        assert len(modes) == 1
        mode = next(iter(modes))
        obs = observed.get(mpn)
        identity, stock = disposition(d, obs)
        url = (obs or {}).get('supplier', {}).get('provenance', {}).get('url', '')
        route = (MANUAL_ROUTES[mpn] if mode == 'manual' else
                 'jlc_catalog_candidate' if identity == 'exact_maker_mpn_code'
                 and 'jlcpcb.com/' in url and stock in ('displayed_sufficient', 'in_stock_quantity_unknown') else
                 'lcsc_catalog_candidate_jlc_eligibility_pending' if identity == 'exact_maker_mpn_code'
                 and stock in ('displayed_sufficient', 'in_stock_quantity_unknown') else
                 'external_sourcing_or_consignment_candidate')
        rows.append(dict(manufacturer=d['manufacturer'], mpn=mpn, installed_need=d['quantity'],
            carrier_refs=';'.join(r['reference'] for r in refs if r['board']=='carrier'),
            pod_refs=';'.join(r['reference'] for r in refs if r['board']=='pod'),
            native_footprints=';'.join(sorted({r['footprint'] for r in refs})), population_mode=mode,
            catalog_code=(obs or {}).get('code', ''), identity_status=identity,
            supplier_stock_observation=stock, supplier_url=url, evidence_file=observations.name if obs else '',
            fallback_url=fallback[mpn]['supplier_url'], proposed_route=route,
            remaining_check='Package / orderable pool / packaging and attrition / vendor placement preview; no allocation claimed'
            if mode != 'manual' else 'Exact manual supply and handling; no machine placement'))
    assert len(rows) == 38 and sum(int(r['installed_need']) for r in rows) == 1000
    with output.open('x', newline='') as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(dict(authority='DRAFT_PROCUREMENT_WORKSHEET_ONLY',
        demand_sha256=hashlib.sha256((ASSEMBLY/'demand.csv').read_bytes()).hexdigest(),
        observations_sha256=hashlib.sha256(observations.read_bytes()).hexdigest(),
        identities=len(rows), installed=1000,
        routes=dict(Counter(r['proposed_route'] for r in rows))), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['collect', 'build'])
    parser.add_argument('--observations', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.action == 'collect':
        collect(args.observations)
    else:
        if args.output is None:
            parser.error('build requires --output')
        build(args.observations, args.output)
