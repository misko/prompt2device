"""Recipient-facing v2 release roles, identity and review denominators.

Called after the assembly owner checks its chain. This module does not issue
engineering verdicts or reinterpret historical v1 archives.
"""
import csv
import io
from pathlib import Path

import assembly_verify as assembly
import release_runtime

p = assembly.p
local = assembly.local
VIEWS = {'top','bottom','iso_nw','iso_se','edge_west','edge_east'}
EXTRA_CRITERIA = {'mechanical', 'bom_identity'}
LENSES = {'pin_electrical': {'pin_identity','electrical'},
          'visual_mechanical': {'readability','mechanical','bom_identity'},
          'layout_power': {'layout_power'}, 'integrated': {'completeness','order_readiness'}}


def csv_rows(file, headers=None):
    text = file.read_bytes().decode('utf-8', errors='strict')
    p.need('\ufffd' not in text and '\x00' not in text and
           all(ord(c) >= 32 or c in '\r\n\t' for c in text), 'unreadable CSV text')
    rows = list(csv.reader(io.StringIO(text, newline=''), strict=True))
    p.need(rows and rows[0] and len(rows[0]) == len(set(rows[0])) and
           (headers is None or rows[0] == headers), 'CSV headers differ')
    p.need(all(len(row) == len(rows[0]) for row in rows[1:]), 'malformed CSV columns')
    return [dict(zip(rows[0], row)) for row in rows[1:]]


def bom_check(project, package, boards, geometry):
    """Reopen the actual delivered CSVs against accepted population and mapping."""
    pop = assembly.fab.population
    fabrication = p.read(local(project, package+'/fabrication.json'))
    manifest = p.read(local(project, fabrication['manifest']))
    population_spec = p.read(local(project, manifest['population']))
    mapping = population_spec['assembly']['boards']
    root = package+'/assembly/'
    rows = csv_rows(local(project, root+'population.csv'))
    required = {'board','reference','mode','manufacturer','mpn','value','footprint'}
    p.need(rows and required <= set(rows[0]), 'population CSV identity columns missing')
    identities = {(row['board'],row['reference']):row for row in rows}
    p.need(len(identities) == len(rows) and {b for b,r in identities} == set(boards),
           'population CSV duplicate/wrong boards')
    declared = {(b,ref):row for b,board in population_spec['boards'].items()
                for ref,row in board['population'].items()}
    p.need(set(identities) == set(declared) and
           all(row['mode'] in pop.MODES and row['mode'] == declared[key]['mode']
               for key,row in identities.items()), 'population CSV policy/reference census differs')
    result = {}
    for board in boards:
        mounted = {ref for (b,ref),r in identities.items() if b == board and r['mode'] in
                   {'factory','consigned','manual'}}
        p.need(mounted == set(geometry['boards'][board]['references']), 'BOM/geometry references differ')
        for mode in ('factory','consigned'):
            name = board+'-'+mode
            bom = csv_rows(local(project, root+name+'-bom.csv'), pop.BOM_COLUMNS)
            cpl = csv_rows(local(project, root+name+'-cpl.csv'), pop.CPL_COLUMNS)
            expected = {ref for (b,ref),r in identities.items() if b == board and r['mode'] == mode}
            seen = set()
            for row in bom:
                refs = row['Designator'].split(',')
                p.need(refs and len(refs) == len(set(refs)) and not seen.intersection(refs) and
                       set(refs) <= expected and row['Quantity'] == str(len(refs)), 'BOM reference/quantity differs')
                seen.update(refs)
                for ref in refs:
                    source = identities[(board,ref)]; selected = mapping[board]['placements'][ref]
                    p.need(all(row[column] == source[field] for column,field in
                               [('Manufacturer','manufacturer'),('MPN','mpn'),('Comment','value'),('Footprint','footprint')])
                           and row['JLCPCB Part #'] == selected['supplier_code'], 'BOM exact identity differs: '+ref)
            p.need(seen == expected and len(cpl) == len(expected) and
                   {r['Designator'] for r in cpl} == expected, 'BOM/CPL population coverage differs')
            # Owning fabrication replay validates actual coordinates and angles.
            result[name] = dict(references=sorted(expected), bom_rows=len(bom), cpl_rows=len(cpl),
                                encoding='utf-8', identity='PASS', vendor_matching=False)
    return result


def describe(project, spec, package, views):
    record = p.read(local(project, views+'/assembly.json'))
    p.need(record['version'] == 2 and record['package'] == package, 'v2 requires registered assembly')
    accepted = p.read(local(project, assembly.RECEIPT))
    mechanical = p.read(local(project, views+'/mechanical.json'))
    scene_path = mechanical['scene_output']+'/scene.json'
    scene = p.read(local(project, scene_path))
    geometry = p.read(local(project, views+'/geometry.json'))
    model = p.read(local(project, record['manifest']))
    p.need(set(scene['boards']) == set(geometry['boards']) == set(mechanical['coverage']) ==
           set(spec['boards']) == set(model['boards']), 'v2 mechanical board census differs')
    p.need(set(scene['models']) == set(model['models']) and scene['models'], 'v2 model census differs')
    paths = {views+'/assembly.json', views+'/mechanical.json', views+'/geometry.json', scene_path,
             record['manifest'], mechanical['scene_manifest']}
    for name,digest in mechanical['subjects'].items():
        p.need(accepted['subjects'].get(name) == digest == p.sha(local(project,name)),
               'unbound/stale v2 mechanical subject: '+name)
    aliases = {'mechanical/scene.json': 'source/project/'+scene_path,
               'mechanical/verification.json': 'source/project/'+views+'/mechanical.json'}
    artifact_units = []
    for board, row in scene['boards'].items():
        expected = geometry['boards'][board]['references']
        p.need(row['references'] == expected and row['mounted_references'] == len(expected) > 0 and
               mechanical['coverage'][board] == {r:v['model'] for r,v in expected.items()},
               'v2 reference/model registration differs')
        required = {board+'/'+board+'-populated.step', board+'/board.step', board+'/native-dielectric.step'}
        required |= {board+'/twin_'+v+'.png' for v in VIEWS}
        required |= {board+'/render_'+v+'_bare.png' for v in ('top','bottom')}
        required |= {board+'/'+n for n in row['details']}
        p.need(set(row['frames']) == VIEWS and required <= set(scene['files']), 'v2 STEP/view roles missing')
        artifact_units.extend(sorted(required))
    for name, digest in scene['files'].items():
        source = mechanical['scene_output']+'/'+name
        p.need(accepted['subjects'].get(source) == digest == p.sha(local(project,source)),
               'v2 scene artifact not accepted: '+name)
        aliases['mechanical/'+name] = 'source/project/'+source
        paths.add(source)
    for name in paths:
        p.need(accepted['subjects'].get(name) == p.sha(local(project,name)), 'unbound v2 assembly artifact: '+name)

    fabrication=p.read(local(project,package+'/fabrication.json'))
    fab_spec=p.read(local(project,fabrication['manifest']))
    for board in spec['boards']:
        b=fab_spec['boards'][board]
        for role,names in [('instructions',b['instructions']),('mechanical',b['mechanical_views']),
                           ('process',b['process']['evidence'])]:
            p.need(names, 'missing recipient fabrication documents')
            for i,name in enumerate(names):
                retained=package+'/inputs/'+name
                p.need(fabrication['files'].get('inputs/'+name)==p.sha(local(project,retained))==
                       p.sha(local(project,name)), 'fabrication document identity differs')
                aliases['documentation/'+board+'/'+role+'/'+str(i+1).zfill(2)+'-'+Path(name).name]=\
                    'source/project/'+retained

    native = package+'/native'; bundle = p.read(local(project,native+'/bundle.json'))
    schematic = p.read(local(project,native+'/design/'+bundle['schematics']['manifest']))
    entries = {}
    for board in spec['boards']:
        b = bundle['boards'][board]; s = schematic['boards'][board]
        p.need(s['producer'] == 'imported', 'v2 native entrypoint adapter requires imported native schematic')
        source = p.read(local(project,native+'/design/'+s['source']))
        roles = dict(pcb=native+'/'+b['native'], project=native+'/'+b['project'],
                     schematic=native+'/design/'+source['schematic'],
                     netlist=native+'/design/'+s['output']+'/native.xml')
        resources = {native+'/'+str(Path(b['native']).parent/f) for f in b['resources']}
        resources |= {native+'/design/'+n for n in source['context']}
        for name in {*roles.values(), *resources}:
            rel = name.removeprefix(native+'/')
            p.need(bundle['files'].get(rel) == p.sha(local(project,name)), 'native entrypoint/resource not retained')
        entries[board] = dict(roles={k:'source/project/'+v for k,v in roles.items()},
                              resources=sorted('source/project/'+n for n in resources))
    calculations = spec['calculations']
    p.need(isinstance(calculations,dict) and set(calculations) == set(spec['boards']), 'calculation board scope differs')
    for board,names in calculations.items():
        p.need(isinstance(names,list) and names and len(names) == len(set(names)), 'explicit calculations required')
        for name in names:
            local(project,name)
    runtime_path = spec['runtime']
    runtime = release_runtime.validate(local(project,runtime_path,False))
    p.need({'cadquery','OCP','vtkmodules','numpy'} <= set(runtime['modules']), 'mechanical runtime modules missing')
    return dict(aliases=aliases, native=entries,
                calculations={b:sorted('source/project/'+n for n in names) for b,names in calculations.items()},
                runtime='source/project/'+runtime_path,
                models=sorted(scene['models']), coverage=mechanical['coverage'],
                limitations=sorted(mechanical['limitations']), artifacts=sorted(artifact_units),
                bom=bom_check(project,package,spec['boards'],geometry))


def index(record):
    rows = ['# '+record['release_id']+' — candidate evidence index', '',
            'UNREVIEWED / DO-NOT-ORDER. This is the immutable input to later independent review,',
            'not a current acceptance record. In a sealed package use the parent CURRENT-STATUS.json and INDEX.md.', '',
            '[Order holds and closure actions](ORDER-INSTRUCTIONS.md) · [Handoff](HANDOFF.md)', '',
            'Retained source status snapshots are historical evidence, not competing current verdicts.', '']
    recipient = record['recipient']
    for board, identity in sorted(record['boards'].items()):
        rows.extend(['## '+board+' / '+identity['version']+' / quantity '+str(identity['quantity']), ''])
        for role,path in sorted(recipient['native'][board]['roles'].items()):
            rows.append('- ['+role+']('+path+')')
        for path in recipient['calculations'][board]: rows.append('- [Design calculation]('+path+')')
        for path in sorted(record['aliases']):
            if path.startswith(('fab/'+board+'/', 'pdf/'+board+'/', 'mechanical/'+board+'/', 'documentation/'+board+'/',
                                'fab/assembly/'+board+'-')):
                rows.append('- ['+path+']('+path+')')
        rows.append('')
    rows.extend(['## Evidence and reproduction', ''])
    for path in sorted(record['aliases']):
        if path.startswith('verification/') or path in ('mechanical/scene.json','mechanical/verification.json',
                                                       'fab/assembly/population.csv','fab/assembly/demand.csv'):
            rows.append('- ['+path+']('+path+')')
    rows.extend(['- [Runtime ABI and package inventory]('+recipient['runtime']+'/runtime.json)',
                 '- [Complete file hashes, roles and review denominators](release.json)', ''])
    return '\n'.join(rows)


def units(record):
    r = record['recipient']
    return dict(mechanical=sorted(['model/'+n for n in r['models']] +
                ['reference/'+b+'/'+ref for b,refs in r['coverage'].items() for ref in refs] +
                ['limitation/'+n for n in r['limitations']] + ['artifact/'+n for n in r['artifacts']]),
                bom_identity=sorted(r['bom']))


def completeness(record):
    r = record['recipient']
    return sorted(['candidate-status','runtime','evidence-index'] +
                  ['native/'+b+'/'+role for b,row in r['native'].items() for role in row['roles']] +
                  ['calculation/'+b+'/'+n for b,names in r['calculations'].items() for n in names] +
                  ['artifact/'+n for n in record['aliases']])


def lenses(review):
    rows = review.get('lenses',{})
    p.need(set(rows) == set(LENSES), 'independent release lenses missing')
    author = assembly.text(review['author']).casefold()
    reviewers = []
    for name, required in LENSES.items():
        row = rows[name]; reviewer = assembly.text(row['reviewer']).casefold()
        p.need(reviewer != author and row['checks'] == sorted(required), 'invalid independent focused lens')
        reviewers.append(reviewer)
    p.need(len(set(reviewers)) == len(LENSES), 'focused and integrated lenses must be independent')
