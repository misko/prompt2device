"""Portable 2D native PCB/replot component; not a complete release archive."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

sys.dont_write_bytecode = True  # Standalone replay must not modify its own package.
import fab_payload as fab
import native_import as imported
import schematic_assembly as assembly

s = fab.seal
p = s.p
TOOL_NAMES = ('fab_replay.py','fab_payload.py','layout_seal.py','routing.py','placement.py',
              'critical_routes.py','routing_geometry.py',
              'native_import.py','native_schematic.py','schematic_assembly.py')
PDF_NAMES = ('pcb.pdf','assembly-top.pdf','assembly-bottom.pdf')


def scope(schematics):
    missing=['3D models and mechanical qualification','BOM/CPL and assembly review',
             'fabrication and release acceptance']
    if schematics is None:
        return ('Portable 2D PCB plots/DRC only; not complete authoring source, schematic or release',
                ['schematic/authoring source and replay',*missing])
    return ('Portable flat schematic authoring/native replay plus 2D PCB plots/PDFs; not release acceptance',missing)


def pcb_pdfs(native, output):
    output.mkdir()
    layers = fab.layers(p.pcb.LoadBoard(str(native)))
    for name, selected, mode in (
        ('pcb.pdf',layers,'--mode-multipage'),
        ('assembly-top.pdf',['F.Fab','F.SilkS','F.CrtYd','Edge.Cuts'],'--mode-single'),
        ('assembly-bottom.pdf',['B.Fab','B.SilkS','B.CrtYd','Edge.Cuts'],'--mode-single')):
        p.command(['kicad-cli','pcb','export','pdf',mode,'--black-and-white','--no-property-popups',
                   '--scale','0','--layers',','.join(selected),'--output',str(output/name),str(native)])


def design_sources(root, spec, board_keys):
    p.need(isinstance(spec,dict) and set(spec) == {'manifest','expected'}, 'schematic replay declaration required')
    manifest = imported.read(p.local(root,spec['manifest']))
    p.need(set(manifest['boards']) == set(board_keys), 'schematic/PCB board coverage differs')
    names = {spec['manifest'],spec['expected']}
    for row in manifest['boards'].values():
        p.need(assembly.producer(row) == 'imported', 'standalone replay currently requires imported flat producer')
        declaration = imported.declaration(root,p.local(root,row['source']))
        names.update((row['source'],row['membership'],declaration['intent'],declaration['schematic']))
        names.update(declaration['producer']['inputs']);names.update(declaration['context'])
    for name in names:p.local(root,name)
    return manifest,names


def pcb_schematic_parity(root, entries, spec):
    """Electrical identity, not physical design soundness or assembly acceptance."""
    design = root/'design'; manifest,_ = design_sources(design,spec,entries)
    for key,row in manifest['boards'].items():
        declaration = imported.declaration(design,p.local(design,row['source']))
        intent = imported.check_intent(imported.read(p.local(design,declaration['intent'])))
        intended = {c['ref']:c for c in intent['components'] if c['physical']}
        native_pins = p.native_pin_nets(list(intended.values()),
            ET.parse(p.local(design,row['output']+'/native.xml')))
        board = p.pcb.LoadBoard(str(p.local(root,entries[key]['native'])))
        footprints = list(board.GetFootprints());refs=[fp.GetReference() for fp in footprints]
        p.need(len(set(refs)) == len(refs) and set(intended) <= set(refs), 'PCB/schematic reference coverage differs')
        for fp in footprints:
            ref = fp.GetReference();pads=list(fp.Pads())
            if ref not in intended:
                p.need(not fp.GetFPIDAsString() and fp.GetAttributes() & p.pcb.FP_BOARD_ONLY
                       and pads and all(pad.GetAttribute() == p.pcb.PAD_ATTRIB_NPTH
                       and not pad.GetNumber() and not pad.GetNetname() for pad in pads),
                       'unaccounted PCB footprint: '+ref)
                continue
            c = intended[ref]
            p.need(not fp.GetAttributes() & p.pcb.FP_BOARD_ONLY,
                   'schematic component incorrectly marked board-only: '+ref)
            p.need(fp.GetValue() == c['value'] and fp.GetFPIDAsString() == c['footprint']
                   and all(fp.GetFieldText(k) == v for k,v in c['fields'].items()),
                   'PCB/schematic identity differs: '+ref)
            pins = {pin['number']:native_pins[ref,pin['number']] for pin in c['pins']}
            actual = {}
            for pad in pads:
                number = pad.GetNumber()
                if not number:
                    p.need(not pad.GetNetname() and pad.GetAttribute() == p.pcb.PAD_ATTRIB_NPTH,
                           'unaccounted electrical pad: '+ref)
                    continue
                p.need(number not in actual or actual[number] == pad.GetNetname(), 'duplicate pad nets differ: '+ref)
                actual[number] = pad.GetNetname()
            p.need(actual == pins, 'PCB/schematic pin nets differ: '+ref)


def copy_design(project, stage, spec, entries):
    manifest,names = design_sources(project,spec,entries)
    design = stage/'design';design.mkdir()
    for name in sorted(names):
        target=p.local(design,name,exists=False);target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p.local(project,name),target)
    # Build fresh provenance for the copied inputs; never silently refresh accepted
    # historical receipts. The package remains explicitly unaccepted.
    for row in manifest['boards'].values():
        imported.build(design,p.local(design,row['source']),p.local(design,row['output'],exists=False))
    assembly.verify(design,spec['manifest'],spec['expected'])
    pcb_schematic_parity(stage,entries,spec)


def verify_design(package, spec, entries):
    design=package/'design';manifest,names=design_sources(design,spec,entries)
    # Every copied source and exact native export is accounted for. A board omitted
    # from metadata must not leave an unverified directory masquerading as evidence.
    expected=set(names)
    for row in manifest['boards'].values():
        expected.update(str((Path(row['output'])/name)) for name in
                        ('native.xml','native-erc.json','native-erc-all.json','native.pdf','receipt.json'))
    actual={f.relative_to(design).as_posix() for f in design.rglob('*') if f.is_file()}
    p.need(actual == expected, 'standalone schematic file census differs')
    assembly.verify(design,spec['manifest'],spec['expected'])
    pcb_schematic_parity(package,entries,spec)


def inventory(root):
    result = {}
    p.need(root.is_dir() and not root.is_symlink(), 'missing/linked replay package')
    for path in sorted(root.rglob('*')):
        p.need(not path.is_symlink(), 'linked package member')
        if path.is_file() and path.relative_to(root).as_posix() != 'bundle.json':
            result[path.relative_to(root).as_posix()] = p.sha(path)
    return result


def model_refs(path):
    result = []
    def walk(node):
        if node[:1] == ['model']: result.append(json.loads(node[1]))
        for child in node:
            if isinstance(child, list): walk(child)
    walk(s.parse(path.read_text()))
    return sorted(set(result))


def resources(root, key, entry):
    p.need(entry['native'] == 'source/'+key+'/'+key+'.kicad_pcb', 'noncanonical native location')
    native = p.local(root, entry['native'])
    base = native.parent
    p.need(native.name == key+'.kicad_pcb' and
           entry['project'] == str(native.with_suffix('.kicad_pro').relative_to(root)),
           'native/settings identity differs')
    mapping = {name:str((base/name).relative_to(root)) for name in entry['resources']}
    p.need(isinstance(entry['resources'],list) and len(mapping) == len(entry['resources']),
           'invalid resource census')
    expected = {key+'.kicad_pcb',key+'.kicad_pro',*mapping}
    p.need({f.relative_to(base).as_posix() for f in base.rglob('*') if f.is_file()} == expected,
           'native resource file census differs')
    s.resources(root, mapping, native)
    p.need(not native.with_suffix('.kicad_dru').exists(), 'custom DRC rules unsupported')
    settings = p.read(p.local(root, entry['project']))['board']['design_settings']
    p.need(not settings.get('drc_exclusions'), 'DRC exclusions unsupported')
    return native


def native_schematic(root, key, spec, entries):
    if spec is None:return None
    design=root/'design';manifest,_=design_sources(design,spec,entries)
    declaration=imported.declaration(design,p.local(design,manifest['boards'][key]['source']))
    return p.local(design,declaration['schematic'])


def regenerate(root, key, entry, output, schematic=None):
    native = resources(root, key, entry)
    # Work only in a copy; the archive must not acquire editor preferences/fills.
    with tempfile.TemporaryDirectory(prefix='vnext-offline-pcb-') as tmp:
        isolated = Path(tmp)/'native'; shutil.copytree(native.parent, isolated)
        copied = isolated/native.name; report = Path(tmp)/'drc.json'
        if schematic is not None:
            shutil.copyfile(schematic,copied.with_suffix('.kicad_sch'))
        command=['kicad-cli','pcb','drc','--format','json','--units','mm','--severity-all',
                 '--all-track-errors','--refill-zones','--save-board','--exit-code-violations']
        if schematic is not None:command.append('--schematic-parity')
        # Relative CLI paths make the actual invocation replayable after relocation.
        command+=['--output','../drc.json',copied.name]
        process=subprocess.run(command,cwd=isolated,capture_output=True,text=True,timeout=300)
        p.need(process.returncode == 0, 'standalone strict DRC failed: '+key+'\n'+process.stdout+process.stderr)
        data=p.read(report)
        p.need(all(isinstance(data.get(k),list) for k in
                   ('violations','unconnected_items','schematic_parity')),
               'incomplete native DRC report: '+key)
        p.need(s.strict_summary(data)['layout_clean'], 'standalone strict DRC failed: '+key)
        p.need(s.r.normalized(native) == s.r.normalized(copied), 'stale/native refill change: '+key)
        result = fab.native_payload(copied, output)
        shutil.copyfile(report, output/'drc.json')
        execution=dict(version=1,command=command,exit_code=process.returncode,
                       native_sha256=p.sha(native),
                       schematic_sha256=p.sha(schematic) if schematic is not None else None)
        (output/'drc-execution.json').write_text(json.dumps(execution,indent=2,sort_keys=True)+'\n')
        pcb_pdfs(copied,output/'pdf')
    return result


def produce(project, boards, target, context=None, schematics=None):
    """Internal fixture seam. Current acceptance is mandatory in public build."""
    p.need(isinstance(boards, dict) and boards, 'nonempty board set required')
    p.need(not target.exists(), 'refusing existing replay package')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='vnext-replay-package-', dir=target.parent) as tmp:
        stage = Path(tmp)/'package'; stage.mkdir(); entries = {}
        for key, row in sorted(boards.items()):
            p.need(isinstance(key,str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',key), 'unsafe board key')
            p.need(set(row) == {'source','project','resources'}, 'unsupported source bundle fields')
            source = p.local(project,row['source']); s.resources(project,row['resources'],source)
            base = stage/'source'/key; base.mkdir(parents=True)
            for name, src in row['resources'].items():
                dest = base/name; dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(p.local(project,src),dest)
            native = base/(key+'.kicad_pcb'); shutil.copyfile(source,native)
            settings = native.with_suffix('.kicad_pro'); shutil.copyfile(p.local(project,row['project']),settings)
            entry = dict(native=native.relative_to(stage).as_posix(), project=settings.relative_to(stage).as_posix(),
                         resources=sorted(row['resources']), unbundled_3d_models=model_refs(native))
            entries[key]=entry
        if schematics is not None:copy_design(project,stage,schematics,entries)
        for key,entry in entries.items():
            regenerate(stage,key,entry,stage/'fab'/key,native_schematic(stage,key,schematics,entries))
        tools = stage/'tools'; tools.mkdir()
        for name in TOOL_NAMES: shutil.copyfile(Path(__file__).parent/name,tools/name)
        record = dict(version=2, boards=entries, context=context, kicad_version=p.pcb.Version(),
            accepted=False, order_status='DO-NOT-ORDER',
            scope='Portable 2D PCB plots/DRC only; not complete authoring source, schematic or release',
            missing=['schematic/authoring source and replay','3D models and mechanical qualification',
                     'BOM/CPL and assembly review','fabrication and release acceptance'], files=inventory(stage))
        record['schematics'] = schematics
        record['scope'],record['missing']=scope(schematics)
        (stage/'bundle.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
        stage.rename(target)
    return record


def verify(package):
    record = p.read(p.local(package,'bundle.json'))
    p.need(isinstance(record,dict) and record.get('version') == 2 and record.get('accepted') is False
           and record.get('order_status') == 'DO-NOT-ORDER', 'unsupported replay record')
    p.need(inventory(package) == record['files'], 'replay package inventory/hash differs')
    tool_dir=package/'tools'
    p.need(tool_dir.is_dir() and {f.name for f in tool_dir.iterdir()} == set(TOOL_NAMES)
           and all(f.is_file() for f in tool_dir.iterdir()), 'replay tool census differs')
    for name in TOOL_NAMES:
        p.need(p.sha(tool_dir/name) == p.sha(Path(__file__).parent/name),
               'copied replay tool differs from verifying toolchain: '+name)
    p.need(p.pcb.Version() == record['kicad_version'], 'KiCad version differs')
    p.need(isinstance(record['boards'],dict) and record['boards'], 'empty replay board set')
    for name in ('source','fab'):
        directory = package/name
        p.need(directory.is_dir() and {f.name for f in directory.iterdir()} == set(record['boards'])
               and all(f.is_dir() for f in directory.iterdir()), 'replay board directory census differs')
    spec=record.get('schematics')
    if spec is not None:verify_design(package,spec,record['boards'])
    else:p.need(not (package/'design').exists(), 'unclaimed schematic design directory')
    p.need((record.get('scope'),record.get('missing')) == scope(spec),
           'replay scope/limitations disagree with schematic coverage')
    for key, entry in record['boards'].items():
        p.need(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',key), 'unsafe board key')
        native = resources(package,key,entry)
        p.need(model_refs(native) == entry['unbundled_3d_models'], '3D limitation inventory differs')
        with tempfile.TemporaryDirectory(prefix='vnext-archive-replot-') as tmp:
            result = regenerate(package,key,entry,Path(tmp)/'fab',
                                native_schematic(package,key,spec,record['boards']))
            plots = package/'fab'/key/'plots'
            fab.census(plots,key,result['layers'],result['drill_counts'])
            with zipfile.ZipFile(package/'fab'/key/(key+'-gerbers.zip')) as zipped:
                p.need(zipped.namelist() == result['members'], 'archive layer census differs')
                for name in result['members']:
                    info=zipped.getinfo(name)
                    p.need(info.create_system == 3 and info.external_attr == 0o100644 << 16
                           and info.compress_type == zipfile.ZIP_DEFLATED
                           and info.file_size == (plots/name).stat().st_size,
                           'noncanonical archive member metadata: '+name)
                    p.need(zipped.read(name) == (plots/name).read_bytes(), 'archive/plot bytes differ')
                    p.need(fab.canonical_plot(plots/name) == fab.canonical_plot(Path(tmp)/'fab/plots'/name),
                           'offline source/plot geometry differs: '+name)
            p.need(s.r.grade_drc(package/'fab'/key/'drc.json') == s.r.grade_drc(Path(tmp)/'fab/drc.json'),
                   'offline DRC differs')
            p.need(p.read(package/'fab'/key/'drc-execution.json') == p.read(Path(tmp)/'fab/drc-execution.json'),
                   'native DRC/parity execution differs')
            pdfs=package/'fab'/key/'pdf'
            p.need(pdfs.is_dir() and {f.name for f in pdfs.iterdir()} == set(PDF_NAMES), 'PCB PDF census differs')
            for name in PDF_NAMES:
                p.need(imported.native.raster_hashes(pdfs/name,Path(tmp)/('stored-'+name)) ==
                       imported.native.raster_hashes(Path(tmp)/'fab/pdf'/name,Path(tmp)/('fresh-'+name)),
                       'PCB PDF rendered pages differ: '+name)
    return dict(replayed_boards=sorted(record['boards']), accepted=False, order_status='DO-NOT-ORDER')


def export(project, output):
    receipt = s.check(project); review = s.r.review_json(project,receipt['review'])
    manifest = p.read(p.local(project,review['manifest'])); boards = {}
    for key, row in manifest['boards'].items():
        base = review['output']+'/'+key+'/native/'
        boards[key] = dict(source=base+key+'.kicad_pcb',project=base+key+'.kicad_pro',
                           resources={name:base+name for name in row['resources']})
    context = dict(layout_receipt_sha256=p.sha(project/s.RECEIPT),
                   layout_review_sha256=p.sha(project/receipt['review']))
    contract=p.read(p.local(project,'01_docs/schematic-contract.json'))
    schematics={name:contract[name] for name in ('manifest','expected')}
    return produce(project,boards,p.local(project,output,exists=False),context,schematics)


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('action',choices=['build','verify'])
    ap.add_argument('--project',type=Path); ap.add_argument('--output'); ap.add_argument('--package',type=Path)
    a=ap.parse_args()
    try:
        if a.action=='build':
            p.need(a.project and a.output,'project/output required'); result=export(a.project.resolve(),a.output)
        else:
            p.need(a.package,'package required'); result=verify(a.package.absolute())
        print(json.dumps(result,indent=2)); return 0
    except (ValueError,OSError,KeyError,TypeError,zipfile.BadZipFile) as exc:
        print('Native replay component refused: '+str(exc),file=sys.stderr); return 1


if __name__=='__main__': sys.exit(main())
