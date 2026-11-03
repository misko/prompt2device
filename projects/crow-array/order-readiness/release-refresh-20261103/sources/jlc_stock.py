#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read-only JLCPCB stock CLI: exact parts, CSV BOMs, and description search."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import html
import io
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from stock_lookup import public_evidence

SEARCH = 'https://jlcsearch.tscircuit.com'
NOTICE = ('Reported public snapshots, not reserved PCBA inventory. Unknown is not zero. '
          'Overseas/presale pools are separate and never added. No purchasing actions.')


def positive(value):
    if not re.fullmatch(r'[1-9]\d*', str(value)):
        raise ValueError(f'expected a positive whole number, got {value!r}')
    return int(value)


def code_of(value):
    value = str(value or '').strip().upper()
    return value if re.fullmatch(r'C[1-9]\d*', value) else None


def count(value):
    return value if type(value) is int and value >= 0 else None


def get(url, timeout=15):
    request = Request(url, headers={'User-Agent': 'vnext-stock-lookup/1.0',
                                   'Accept': 'application/json,text/html'})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read(4_000_001)
        if len(raw) > 4_000_000:
            raise ValueError('response exceeds 4 MB limit')
        return raw.decode('utf-8'), {
            'url': response.url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
            'http_date': response.headers.get('Date'), 'http_age': response.headers.get('Age'),
            'sha256': hashlib.sha256(raw).hexdigest()}


def products(body):
    """Extract Product objects, not navigation's generic 'In Stock' labels."""
    def walk(obj):
        if isinstance(obj, list):
            for item in obj:
                yield from walk(item)
        elif isinstance(obj, dict):
            if obj.get('@type') == 'Product':
                yield obj
            if '@graph' in obj:
                yield from walk(obj['@graph'])
    for match in re.finditer(r'<script[^>]*type=["\x27]application/ld\+json["\x27][^>]*>(.*?)</script>', body, re.S):
        try:
            yield from walk(json.loads(html.unescape(match[1])))
        except ValueError:
            continue


def public_part(body, code, mpn=None):
    all_products = [p for p in products(body) if p.get('sku') == code]
    selected = [p for p in all_products if not mpn or p.get('mpn') == mpn]
    if not selected:
        return {'state': 'identity_mismatch' if all_products else 'unverified',
                'availability': None, 'stock': None}
    identities = {p.get('mpn') for p in selected}
    if len(identities) != 1 or not all(isinstance(m, str) and m for m in identities):
        return {'state': 'identity_mismatch', 'availability': None, 'stock': None}
    actual = next(iter(identities))
    fields = public_evidence(body, actual, code)['observations']
    def unique(key):
        values = [f[key] for f in fields if key in f]
        return values[0] if values and all(v == values[0] for v in values) else None
    avail = set()
    for p in selected:
        offers = p.get('offers', [])
        for offer in offers if isinstance(offers, list) else [offers]:
            if isinstance(offer, dict) and isinstance(offer.get('availability'), str):
                avail.add(offer['availability'].rsplit('/', 1)[-1])
    brand = selected[0].get('brand')
    return {'state': 'observed', 'mpn': actual,
            'manufacturer': brand.get('name') if isinstance(brand, dict) else brand,
            'package': unique('componentSpecificationEn'),
            'availability': next(iter(avail)) if len(avail) == 1 else None,
            'conflicting_availability': len(avail) > 1,
            'stock': count(unique('stockCount')),
            'overseas_stock': count(unique('overseasStockCount')),
            'presale': count(unique('canPresaleNumber')),
            'buy_enabled': unique('isBuyComponent'), 'reason': unique('noBuyReason'),
            'raw_fields': fields}


def stock_status(needed, aggregate=None, public=None):
    public = public or {}
    if public.get('state') == 'identity_mismatch':
        return 'IDENTITY_MISMATCH'
    if public.get('conflicting_availability'):
        return 'CONFLICT'
    a, p = count(aggregate), count(public.get('stock'))
    availability = public.get('availability')
    if availability == 'OutOfStock' and ((a is not None and a > 0) or (p is not None and p > 0)):
        return 'CONFLICT'
    if p is not None and a is not None and (p >= needed) != (a >= needed):
        return 'CONFLICT'
    if public.get('buy_enabled') == '0':
        return 'NOT_ORDERABLE'
    if availability == 'OutOfStock':
        return 'OUT_OF_STOCK'
    n = p if p is not None else a
    if n is not None:
        if n == 0:
            return 'CONFLICT' if availability == 'InStock' else 'OUT_OF_STOCK'
        return 'SUFFICIENT_REPORTED' if n >= needed else 'SHORT'
    return 'IN_STOCK_QTY_UNKNOWN' if availability == 'InStock' else 'UNVERIFIED'


class Client:
    def __init__(self, timeout=15, public=True, getter=get):
        self.timeout, self.public, self.getter = timeout, public, getter

    def search_rows(self, path, params, key='components'):
        url = SEARCH + path + '?' + urlencode(params)
        try:
            body, proof = self.getter(url, self.timeout)
            data = json.loads(body)
            rows = data.get(key) if isinstance(data, dict) else None
            if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
                raise ValueError(f'unexpected response: missing {key} array')
            return rows, {**proof, 'state': 'observed', 'returned_rows': len(rows)}
        except (OSError, ValueError, TimeoutError) as exc:
            return [], {'url': url, 'state': 'lookup_failed', 'error': str(exc)}

    def row(self, candidate, needed, expected_mpn=None, expected_maker=None):
        code = code_of('C' + str(candidate.get('lcsc', '')))
        mpn = candidate.get('mfr') or expected_mpn
        public = {'state': 'not_requested'}
        if self.public and code:
            url = 'https://jlcpcb.com/partdetail/' + code
            try:
                body, proof = self.getter(url, self.timeout)
                public = {**public_part(body, code, expected_mpn or mpn), 'provenance': proof}
            except (OSError, ValueError, TimeoutError) as exc:
                public = {'state': 'lookup_failed', 'url': url, 'error': str(exc)}
        result = {'mpn': mpn or public.get('mpn'), 'code': code, 'needed': needed,
                  'manufacturer': public.get('manufacturer'),
                  'package': candidate.get('package') or public.get('package'),
                  'description': candidate.get('description'),
                  'jlcsearch_stock': count(candidate.get('stock')),
                  'jlcsearch_stock_checked_at': candidate.get('stock_checked_at'),
                  'jlcpcb': public,
                  'status': stock_status(needed, candidate.get('stock'), public)}
        if expected_maker:
            result['requested_manufacturer'] = expected_maker
            # No guessed maker aliases. Mismatch needs human identity review.
            if public.get('manufacturer') and public['manufacturer'].casefold() != expected_maker.casefold():
                result['manufacturer_review'] = 'Catalog spelling differs; confirm identity (no alias inferred).'
        return result

    def part(self, query, needed=1, code=None, manufacturer=None):
        mpn = None if code_of(query) else query
        requested_code = code or code_of(query)
        term = requested_code or mpn
        rows, proof = self.search_rows('/api/search', {'q': term, 'limit': 100, 'full': 'true'})
        selected = [r for r in rows if (not mpn or r.get('mfr') == mpn)
                    and (not requested_code or code_of('C' + str(r.get('lcsc'))) == requested_code)]
        # Exact code can reach the public catalog even when the index misses it.
        if not selected and requested_code:
            selected = [{'lcsc': int(requested_code[1:]), 'mfr': mpn}]
        # Deduplicate catalog identities without adding reported counts.
        selected = list({(r.get('lcsc'), r.get('mfr')): r for r in selected}.values())
        result = [self.row(r, needed, mpn, manufacturer) for r in selected]
        if not result:
            result = [{'mpn': mpn, 'code': requested_code, 'needed': needed,
                       'status': 'LOOKUP_FAILED' if proof['state'] == 'lookup_failed' else 'NOT_FOUND',
                       'jlcsearch_stock': None, 'jlcpcb': {'state': 'not_located'}}]
        for r in result:
            r['query'] = query
            r['jlcsearch_query'] = proof
            if proof['state'] == 'lookup_failed' and r['status'] == 'UNVERIFIED':
                r['status'] = 'LOOKUP_FAILED'
        return result

    def search(self, description, package=None, resistance=None, limit=10, needed=1):
        if not description.strip():
            raise ValueError('search description must not be empty')
        filters = description_filters(description, package, resistance)
        params = {'limit': 100, 'full': 'true'}
        if filters['package']:
            params['package'] = filters['package']
        if filters['resistance_ohms'] is not None:
            params['resistance'] = str(filters['resistance_ohms'])
            rows, proof = self.search_rows('/resistors/list.json', params, 'resistors')
        else:
            params['q'] = description
            rows, proof = self.search_rows('/api/search', params)
        selected = []
        for row in rows:
            if filters['package'] and row.get('package') != filters['package']:
                continue
            if filters['resistance_ohms'] is not None:
                try:
                    if Decimal(str(row.get('resistance'))) != filters['resistance_ohms']:
                        continue
                except InvalidOperation:
                    continue
            else:
                # The search service sometimes returns unrelated rows: require all tokens.
                haystack = str(row.get('mfr', '')) + ' ' + str(row.get('description', ''))
                tokens = re.findall(r'[a-z0-9]+', description.lower())
                if not all(t in haystack.lower() for t in tokens):
                    continue
            if code_of('C' + str(row.get('lcsc'))) and row.get('mfr'):
                selected.append(row)
        selected = list({r['lcsc']: r for r in selected}.values())
        selected.sort(key=lambda r: count(r.get('stock')) if count(r.get('stock')) is not None else -1, reverse=True)
        result = [self.row(r, needed) for r in selected[:limit]]
        for r in result:
            r['jlcsearch_query'] = proof
        return result, {**filters, 'resistance_ohms': str(filters['resistance_ohms']) if filters['resistance_ohms'] is not None else None,
                        'query': proof, 'matching_rows_in_response': len(selected),
                        'limit': limit, 'exhaustive': False}


def ohms(text):
    text = re.sub(r'(?i)ohms?|Ω', '', str(text)).replace(' ', '')
    embedded = re.fullmatch(r'(\d+)([RrKkMm])(\d+)', text)
    if embedded:
        text = embedded[1] + '.' + embedded[3] + embedded[2]
    m = re.fullmatch(r'(\d+(?:\.\d+)?)([RrKkMm]?)', text)
    if not m:
        raise ValueError(f'invalid resistance {text!r}; use 10k, 4k7, 4.7ohm or 1M')
    factor = {'': 1, 'r': 1, 'k': 1000, 'M': 1000000, 'm': Decimal('.001')}
    return Decimal(m[1]) * factor.get(m[2], factor.get(m[2].lower(), 1))


def description_filters(description, package=None, resistance=None):
    sizes = re.findall(r'(?<!\d)(01005|0201|0402|0603|0805|1206|1210|2010|2512)(?!\d)', description)
    if not package and len(set(sizes)) > 1:
        raise ValueError('ambiguous package sizes; use --package')
    package = package or (sizes[0] if sizes else None)
    value = ohms(resistance) if resistance is not None else None
    if value is None and re.search(r'(?i)\b(?:resistor|resistors|restistor)\b', description):
        values = re.findall(r'(?<![\w.])(\d+[RrKkM]\d+|\d+(?:\.\d+)?\s*(?:[kKMRr](?:\s*(?:ohms?|Ω))?|(?:ohms?|Ω)))(?!\w)', description)
        if len(values) != 1:
            raise ValueError('resistor search needs one value, e.g. "resistor 10k 0603", or --resistance')
        value = ohms(values[0])
    return {'package': package, 'resistance_ohms': value,
            'filter_scope': 'resistance and package only; review other ratings' if value is not None else 'keyword candidates; review electrical specifications'}


def read_bom(path, boards=1, mpn_column=None, code_column=None, quantity_column=None):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        sample = stream.read(8192)
        stream.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t')
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(stream, dialect=dialect)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValueError('BOM has duplicate column names')
        normalized = {re.sub(r'[^a-z0-9]', '', h.lower()): h for h in headers}
        def column(explicit, aliases):
            if explicit:
                if explicit not in headers:
                    raise ValueError(f'BOM column not found: {explicit}')
                return explicit
            return next((normalized[a] for a in aliases if a in normalized), None)
        m = column(mpn_column, ['mpn', 'manufacturerpartnumber', 'mfrpart', 'mfrpartnumber'])
        c = column(code_column, ['jlcpcbpart', 'jlcpcbpartnumber', 'lcscpart', 'lcsc', 'jlcpcb', 'catalogcode'])
        q = column(quantity_column, ['quantity', 'qty'])
        refs = column(None, ['designator', 'designators', 'reference', 'references'])
        maker = column(None, ['manufacturer', 'maker'])
        if not m and not c:
            raise ValueError('BOM needs MPN or JLCPCB/LCSC code column; use --mpn-column/--code-column')
        result = {}
        for line, row in enumerate(reader, 2):
            if not any(row.values()):
                continue
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f'BOM line {line}: malformed CSV row')
            mpn, raw_code = row.get(m, '').strip(), row.get(c, '').strip()
            code = code_of(raw_code)
            if raw_code and not code:
                raise ValueError(f'BOM line {line}: invalid JLC code {raw_code!r}')
            if not mpn and not code:
                raise ValueError(f'BOM line {line}: missing exact identity (descriptions are not MPNs)')
            if q:
                qty = positive(row[q].strip())
                basis = 'quantity_column'
            elif refs and row[refs].strip():
                ref_list = re.split(r'[,;\s]+', row[refs].strip())
                if any('-' in ref for ref in ref_list):
                    raise ValueError(f'BOM line {line}: reference ranges need an explicit quantity')
                qty, basis = len(ref_list), 'designator_count'
            else:
                raise ValueError(f'BOM line {line}: quantity missing; supply a Quantity column')
            manufacturer = row.get(maker, '').strip() or None
            key = (mpn or code, manufacturer)
            if key in result:
                old = result[key]
                if old['code'] and code and old['code'] != code:
                    raise ValueError(f'BOM line {line}: conflicting catalog codes for {mpn}')
                old['code'] = old['code'] or code
                old['needed'] += qty * boards
                old['lines'].append(line)
            else:
                result[key] = {'query': mpn or code, 'code': code, 'needed': qty * boards,
                               'manufacturer': manufacturer, 'lines': [line], 'quantity_basis': basis}
        if not result:
            raise ValueError('BOM has no populated rows')
        return list(result.values())


def flattened(row):
    public = row.get('jlcpcb', {})
    return {'mpn': row.get('mpn'), 'code': row.get('code'), 'needed': row['needed'],
            'jlcsearch_stock': row.get('jlcsearch_stock'), 'jlcpcb_stock': public.get('stock'),
            'jlcpcb_availability': public.get('availability') or public.get('state'),
            'overseas_stock': public.get('overseas_stock'), 'presale': public.get('presale'),
            'status': row['status'], 'package': row.get('package'),
            'manufacturer': row.get('manufacturer'), 'reason': public.get('reason'),
            'manufacturer_review': row.get('manufacturer_review'),
            'jlcpcb_url': public.get('provenance', {}).get('url', public.get('url')),
            'jlcsearch_url': row.get('jlcsearch_query', {}).get('url'),
            'error': public.get('error') or row.get('jlcsearch_query', {}).get('error')}


def render(report, fmt):
    if fmt == 'json':
        return json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    rows = [flattened(r) for r in report['results']]
    if fmt == 'csv':
        output = io.StringIO()
        fields = list(flattened({'needed': 0, 'status': ''}))
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()
    if not rows:
        return 'No matches returned. See query diagnostics; this is not proof of zero stock.\n'
    columns = ['mpn', 'code', 'needed', 'jlcsearch_stock', 'jlcpcb_availability', 'overseas_stock', 'status']
    cells = [[str(r.get(k)) if r.get(k) is not None else '?' for k in columns] for r in rows]
    # Strip terminal control characters from network-supplied strings.
    cells = [[re.sub(r'[\x00-\x1f\x7f-\x9f]', '?', v) for v in row] for row in cells]
    widths = [max(len(k), *(len(row[i]) for row in cells)) for i, k in enumerate(columns)]
    return '\n'.join('  '.join(v.ljust(widths[i]) for i, v in enumerate(row))
                     for row in [columns, *cells]) + '\n'


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    subs = root.add_subparsers(dest='command', required=True)
    for name in ('part', 'bom', 'search'):
        sub = subs.add_parser(name)
        sub.add_argument('input', help={'part': 'Exact manufacturer MPN or C-code', 'bom': 'CSV BOM path',
                                       'search': 'Description, e.g. "resistor 10k 0603"'}[name])
        sub.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
        sub.add_argument('--output', type=Path, help='Write new report; refuses overwrite')
        sub.add_argument('--timeout', type=int, choices=range(1, 61), default=15, metavar='SECONDS')
        sub.add_argument('--no-public', action='store_true', help='jlcsearch only; skip direct JLC confirmation')
        sub.add_argument('--strict', action='store_true', help='Exit 1 unless all results report sufficient numeric stock')
        if name == 'bom':
            sub.add_argument('--boards', type=int, default=1)
            sub.add_argument('--jobs', type=int, choices=range(1, 9), default=3)
            for col in ('mpn', 'code', 'quantity'):
                sub.add_argument(f'--{col}-column')
        else:
            sub.add_argument('--need', type=int, default=1)
        if name == 'part':
            sub.add_argument('--code', help='Known JLC C-code; helps when the search index misses an MPN')
        if name == 'search':
            sub.add_argument('--package', help='Exact package; common numeric sizes use imperial convention')
            sub.add_argument('--resistance', help='Ohms, e.g. 10k, 4k7, 1M')
            sub.add_argument('--limit', type=int, choices=range(1, 51), default=10)
    return root


def main(argv=None, client_factory=Client):
    args = parser().parse_args(argv)
    try:
        if args.output and args.output.exists():
            raise ValueError(f'refusing to overwrite {args.output}')
        positive(args.boards if args.command == 'bom' else args.need)
        client = client_factory(timeout=args.timeout, public=not args.no_public)
        report = {'schema': 'jlc-stock-v1', 'command': args.command, 'input': args.input,
                  'created_at': datetime.now(timezone.utc).isoformat(), 'notice': NOTICE}
        if args.command == 'part':
            if not args.input.strip() or (args.code and not code_of(args.code)):
                raise ValueError('provide a nonempty MPN and/or a valid C-code')
            if code_of(args.input) and args.code and code_of(args.input) != code_of(args.code):
                raise ValueError('conflicting C-codes')
            report['results'] = client.part(args.input.strip(), args.need, code_of(args.code))
        elif args.command == 'bom':
            items = read_bom(Path(args.input), args.boards, args.mpn_column, args.code_column, args.quantity_column)
            def lookup(item):
                rows = client.part(item['query'], item['needed'], item['code'], item['manufacturer'])
                for r in rows:
                    r['bom_lines'] = item['lines']
                return rows
            with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                report['results'] = [r for batch in pool.map(lookup, items) for r in batch]
            report['boards'], report['unique_bom_identities'] = args.boards, len(items)
        else:
            report['results'], report['search'] = client.search(args.input, args.package, args.resistance, args.limit, args.need)
            filters = report['search']
            print(f"Search filters: resistance={filters['resistance_ohms'] or '?'} ohms; "
                  f"package={filters['package'] or '?'}. {filters['filter_scope']}", file=sys.stderr)
        output = render(report, args.format)
        if args.output:
            with args.output.open('x', encoding='utf-8', newline='') as stream:
                stream.write(output)
        else:
            sys.stdout.write(output)
        print(NOTICE, file=sys.stderr)
        reviews = [r.get('code') or r.get('mpn') for r in report['results'] if r.get('manufacturer_review')]
        if reviews:
            print('Manufacturer spelling needs review (stock status unchanged): ' + ', '.join(reviews), file=sys.stderr)
        for row in report['results']:
            err = flattened(row)['error']
            if err:
                print(f"Lookup warning ({row.get('mpn') or row.get('code')}): {err}", file=sys.stderr)
        search_error = report.get('search', {}).get('query', {}).get('error')
        if search_error:
            print('Search failed: ' + search_error, file=sys.stderr)
        if search_error or any(r['status'] == 'LOOKUP_FAILED' for r in report['results']):
            return 2
        if args.strict and (not report['results'] or any(r['status'] != 'SUFFICIENT_REPORTED' or r.get('manufacturer_review') for r in report['results'])):
            return 1
        return 0
    except (ValueError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
