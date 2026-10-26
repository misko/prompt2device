"""Source-exact population/demand and native coordinates; not vendor CPL approval."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile

import layout_seal as seal

p = seal.p
MODES = {'factory', 'consigned', 'manual', 'dnp', 'mechanical'}
EMPTY_COLUMNS = {'positions':['board','reference','x_mm','y_mm','kicad_angle_deg','side','mode'],
                 'demand':['manufacturer','mpn','quantity']}
BOM_COLUMNS = ['Comment','Designator','Footprint','JLCPCB Part #','Manufacturer','MPN','Quantity']
CPL_COLUMNS = ['Designator','Mid X','Mid Y','Rotation','Layer']


def csv_text(rows, columns):
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=columns, lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    return output.getvalue()


def data(project, manifest):
    p.need(isinstance(manifest, dict) and manifest.get('version') == 1 and isinstance(manifest.get('boards'), dict)
           and manifest['boards'], 'nonempty board population manifest required')
    population = []; positions = []; demand = {}; subjects = {}; counts = {}
    for key, spec in sorted(manifest['boards'].items()):
        p.need(isinstance(key, str) and key.strip(), 'board key required')
        p.need(set(spec) == {'source','intent','quantity','population'}, 'unsupported board population fields')
        quantity = spec['quantity']
        p.need(type(quantity) is int and quantity > 0, 'positive integer board quantity required')
        native = p.local(project, spec['source']); intent_path = p.local(project, spec['intent'])
        subjects[spec['source']] = p.sha(native); subjects[spec['intent']] = p.sha(intent_path)
        components = p.read(intent_path)['components']
        refs = [c['ref'] for c in components]
        p.need(len(refs) == len(set(refs)), 'duplicate intent reference')
        physical = {c['ref']:c for c in components if c.get('physical')}
        p.need(physical, 'empty electrical population')
        board = p.pcb.LoadBoard(str(native))
        p.need(board is not None, 'invalid native board: '+spec['source'])
        footprints = list(board.GetFootprints())
        native_refs = [f.GetReference() for f in footprints]
        p.need(len(native_refs) == len(set(native_refs)), 'duplicate native reference')
        policies = spec['population']
        p.need(isinstance(policies, dict) and set(policies) == set(native_refs)
               and set(physical) <= set(native_refs), 'population/reference coverage differs')
        counts[key] = dict(boards=quantity, electrical=len(physical), mechanical=0, populated=0)
        for fp in sorted(footprints, key=lambda f:f.GetReference()):
            ref = fp.GetReference(); policy = policies[ref]; mode = policy['mode']
            p.need(set(policy) == {'mode','reason','evidence'}, 'unsupported population policy fields: '+ref)
            p.need(mode in MODES and isinstance(policy.get('reason'), str)
                   and policy['reason'].strip(), 'explicit population mode/reason required: '+ref)
            evidence = policy.get('evidence', [])
            p.need(isinstance(evidence, list) and evidence, 'population evidence required: '+ref)
            for name in evidence: subjects[name] = p.sha(p.local(project, name))
            fields = {}; assembly = ''; value = fp.GetValue(); footprint = fp.GetFPIDAsString()
            if ref in physical:
                c = physical[ref]; fields = c.get('fields', {})
                p.need(isinstance(fields, dict), 'invalid intent fields: '+ref)
                assembly = fields.get('Assembly', '')
                p.need(mode != 'mechanical', 'electrical part excluded as mechanical: '+ref)
                p.need(not fp.IsDNP() or mode == 'dnp', 'native DNP contradicts population: '+ref)
                p.need(mode != 'factory' or not (fp.IsExcludedFromBOM() or fp.IsExcludedFromPosFiles()),
                       'native exclusion contradicts factory population: '+ref)
                p.need(mode != 'consigned' or not fp.IsExcludedFromPosFiles(),
                       'native position exclusion contradicts consigned population: '+ref)
                p.need(value == c['value'] and footprint == c['footprint'], 'native value/footprint mismatch: '+ref)
                for name in ('Manufacturer', 'MPN', 'Assembly'):
                    expected = fields.get(name, '')
                    p.need(isinstance(expected, str) and expected.strip()
                           and fp.GetFieldText(name) == expected, 'native/intent '+name+' mismatch: '+ref)
                for name, expected in fields.items():
                    p.need(isinstance(expected, str) and fp.GetFieldText(name) == expected,
                           'native/intent field mismatch: '+ref+'/'+name)
            else:
                p.need(mode == 'mechanical' and not footprint and list(fp.Pads())
                       and all(pad.GetAttribute() == p.pcb.PAD_ATTRIB_NPTH and not pad.GetNetname()
                               for pad in fp.Pads()), 'unsupported/unaccounted extra footprint: '+ref)
                counts[key]['mechanical'] += 1
            populated = mode in {'factory', 'consigned', 'manual'}
            needed = quantity if populated else 0
            counts[key]['populated'] += int(populated)
            population.append(dict(board=key, reference=ref, mode=mode,
                manufacturer=fields.get('Manufacturer',''), mpn=fields.get('MPN',''),
                value=value, footprint=footprint, assembly=assembly, board_quantity=quantity,
                fields_json=json.dumps(fields, sort_keys=True, separators=(',',':')),
                native_dnp=fp.IsDNP(), native_exclude_bom=fp.IsExcludedFromBOM(),
                native_exclude_positions=fp.IsExcludedFromPosFiles(),
                demand=needed, reason=policy['reason'], evidence=';'.join(evidence)))
            if populated:
                ident = (fields['Manufacturer'], fields['MPN'])
                demand[ident] = demand.get(ident, 0) + needed
                positions.append(dict(board=key, reference=ref, x_mm=fp.GetPosition().x/1e6,
                    y_mm=fp.GetPosition().y/1e6, kicad_angle_deg=fp.GetOrientationDegrees(),
                    side='bottom' if fp.IsFlipped() else 'top', mode=mode))
    return dict(population=population, positions=positions,
                demand=[dict(manufacturer=m, mpn=n, quantity=q) for (m,n),q in sorted(demand.items())],
                subjects=subjects, counts=counts)


def assembly_files(project, manifest, result):
    """Translate supplied source-bound geometry/identity decisions; not their approval."""
    mapping = manifest['assembly']
    p.need(isinstance(mapping, dict) and set(mapping) == {'version','boards'}
           and mapping['version'] == 1 and isinstance(mapping['boards'], dict)
           and set(mapping['boards']) == set(manifest['boards']), 'assembly board coverage differs')
    output = {}; code_identities = {}
    population = {(r['board'],r['reference']):r for r in result['population']}
    positions = {(r['board'],r['reference']):r for r in result['positions']}
    for key, spec in sorted(mapping['boards'].items()):
        p.need(re.fullmatch(r'[a-zA-Z0-9_-]+', key), 'unsafe assembly board filename')
        p.need(isinstance(spec, dict) and set(spec) == {'source_sha256','placements'},
               'assembly mapping needs exact native source hash and placements')
        source = manifest['boards'][key]['source']
        p.need(spec['source_sha256'] == result['subjects'][source], 'stale assembly source: '+key)
        needed = {ref for (board,ref),r in population.items()
                  if board == key and r['mode'] in {'factory','consigned'}}
        placements = spec['placements']
        p.need(isinstance(placements, dict) and set(placements) == needed,
               'factory/consigned geometry coverage differs: '+key)
        groups = {'factory':{}, 'consigned':{}}; cpl = {'factory':[], 'consigned':[]}
        for ref, entry in sorted(placements.items()):
            row = population[(key,ref)]; pos = positions[(key,ref)]
            p.need(isinstance(entry, dict) and set(entry) == {
                'manufacturer','mpn','footprint','supplier_code','centroid_offset_mm','rotation_deg','evidence'},
                'unsupported assembly mapping fields: '+ref)
            p.need(all(entry[name] == row[name] for name in ('manufacturer','mpn','footprint')),
                   'assembly/native identity differs: '+ref)
            evidence = entry['evidence']
            p.need(isinstance(evidence,list) and evidence, 'identity/geometry evidence required: '+ref)
            for name in evidence: result['subjects'][name] = p.sha(p.local(project,name))
            code = entry['supplier_code']
            p.need(isinstance(code,str) and (re.fullmatch(r'C[1-9][0-9]*',code)
                   or (row['mode'] == 'consigned' and code == '')), 'exact supplier code required: '+ref)
            # Any known native supplier-code field must agree; absent code needs retained
            # mapping evidence, not a silent field mutation or guessed catalog identity.
            fields = json.loads(row['fields_json'])
            for field in ('LCSC','LCSC Part #','JLCPCB Part #','Supplier'):
                value = fields.get(field, '')
                if value and (field != 'Supplier' or re.fullmatch(r'C[1-9][0-9]*',value)):
                    p.need(value == code, 'native supplier code contradicts mapping: '+ref)
            identity = (row['manufacturer'],row['mpn'])
            if code:
                p.need(code_identities.setdefault(code,identity) == identity,
                       'supplier code maps to conflicting manufacturer/MPN: '+code)
            offset = entry['centroid_offset_mm']
            p.need(isinstance(offset,list) and len(offset) == 2, 'centroid needs two board-axis offsets')
            dx,dy = map(p.number,offset); rotation = p.number(entry['rotation_deg'])
            p.need(0 <= rotation < 360, 'vendor rotation must be in [0,360)')
            # Absolute origin agrees with fab_payload gerbers and absolute drills.
            # Offsets are in native board axes, not footprint-local axes. Bottom is
            # never automatically mirrored; final vendor angle is an explicit input.
            def mm(value): return format(0.0 if abs(value)<0.0000005 else value,'.6f')+'mm'
            cpl[row['mode']].append({'Designator':ref,
                'Mid X':mm(pos['x_mm']+dx), 'Mid Y':mm(-pos['y_mm']-dy),
                'Rotation':format(rotation,'.6f'), 'Layer':pos['side'].title()})
            ident = (row['manufacturer'],row['mpn'],row['value'],row['footprint'],code)
            groups[row['mode']].setdefault(ident,[]).append(ref)
        for mode in ('factory','consigned'):
            bom = []
            for (maker,mpn,value,footprint,code),refs in sorted(groups[mode].items()):
                bom.append({'Comment':value,'Designator':','.join(refs),'Footprint':footprint,
                    'JLCPCB Part #':code,'Manufacturer':maker,'MPN':mpn,'Quantity':len(refs)})
            prefix = key+'-'+mode
            output[prefix+'-bom.csv'] = csv_text(bom,BOM_COLUMNS)
            output[prefix+'-cpl.csv'] = csv_text(cpl[mode],CPL_COLUMNS)
    return output


def produce(project, manifest, output, context=None):
    """Internal component; callers must supply acceptance. Tests use explicit fixtures."""
    p.need(not output.exists(), 'refusing existing population output')
    result = data(project, manifest)
    assembly = assembly_files(project,manifest,result) if 'assembly' in manifest else {}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='vnext-population-', dir=output.parent) as tmp:
        stage = Path(tmp)/'population'; stage.mkdir()
        for name in ('population', 'positions', 'demand'):
            rows = result[name]
            columns = list(rows[0]) if rows else EMPTY_COLUMNS.get(name)
            p.need(columns, 'empty '+name+' export')
            (stage/(name+'.csv')).write_text(csv_text(rows, columns))
        for name, content in assembly.items(): (stage/name).write_text(content)
        record = dict(version=1, subjects=result['subjects'], counts=result['counts'],
            acceptance_context=context,
            accepted=False, order_status='DO-NOT-ORDER',
            coordinates='KiCad absolute footprint anchors, mm, +Y down; native angles, NOT vendor CPL',
            missing=['vendor datum/centroid/rotation review', 'quantity-aware stock observations',
                     'process/assembly verification', 'fabrication stage acceptance'],
            files={f.name:p.sha(f) for f in sorted(stage.iterdir())})
        if assembly:
            record['assembly'] = dict(
                mapping_sha256=hashlib.sha256(json.dumps(manifest['assembly'],
                    sort_keys=True, separators=(',',':')).encode()).hexdigest(),
                coordinates='Absolute native origin, mm, +X right/+Y up; no bottom mirroring; explicit vendor angles',
                scope='Supplied identity/centroid/rotation mapping translated, NOT independently approved',
                quantity='BOM/CPL describe one board; demand.csv multiplies all board quantities',
                order_holds=['independent manufacturer geometry/identity review',
                    'vendor matching/orientation preview', 'stock/allocation and process confirmation'])
        (stage/'population.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
        stage.rename(output)
    return record


def verify(project, manifest, output, context=None):
    p.need(output.is_dir() and not output.is_symlink(), 'missing or linked population output')
    with tempfile.TemporaryDirectory(prefix='vnext-population-verify-') as tmp:
        expected = Path(tmp)/'expected'; record = produce(project, manifest, expected, context)
        wanted = {f.name for f in expected.iterdir()}
        p.need({f.name for f in output.iterdir()} == wanted and
               all(f.is_file() and not f.is_symlink() for f in output.iterdir()),
               'population output census differs')
        for name in wanted:
            p.need((output/name).read_bytes() == (expected/name).read_bytes(),
                   'stale population output: '+name)
    return record


def export(project, manifest_name, output_name, checking=False):
    receipt = seal.check(project)
    review = seal.r.review_json(project, receipt['review'])
    sealed = p.read(p.local(project, review['manifest']))
    _, placement_review, _ = seal.r.upstream(project)
    inputs = p.read(p.local(project, placement_review['inputs']))
    manifest = p.read(p.local(project, manifest_name))
    p.need(set(manifest['boards']) == set(sealed['boards']), 'sealed board coverage differs')
    for key, row in manifest['boards'].items():
        p.need(row['source'] == review['output']+'/'+key+'/native/'+key+'.kicad_pcb'
               and row['intent'] == inputs['boards'][key]['intent'], 'source differs from accepted board: '+key)
    output = p.local(project, output_name, exists=False)
    context = dict(layout_receipt_sha256=p.sha(project/seal.RECEIPT),
                   manifest_sha256=p.sha(project/manifest_name), tool_sha256=p.sha(Path(__file__)),
                   manual_sha256=p.sha(p.ROOT/'skills/pcb-design/procedures/fabrication/population.md'))
    return (verify if checking else produce)(project, manifest, output, context)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify'])
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--manifest', required=True); parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(export(args.project.resolve(), args.manifest, args.output,
                                args.action == 'verify'), indent=2)); return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('Population component refused: '+str(exc), file=sys.stderr); return 1


if __name__ == '__main__': sys.exit(main())
