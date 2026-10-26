"""Verify a source-owned flat KiCad producer without redrawing its schematic.

Declaration schema1: {version:1, producer:{entrypoint,inputs:[relative files]},
intent:relative JSON, schematic:relative native file, context:[relative files]}.
All paths are relative to ROOT. Entry point is trusted local Python, invoked
in a temporary input copy with a 120s timeout; this is NOT a security sandbox.
Intent/native outputs cannot be producer inputs. Context names the project,
symbol/library tables and resolved local libraries used by native checks.

Intent schema1: {version:1,nets:[names],components:[{ref,value,footprint,
physical:bool,fields:{name:value},pins:[{number,name,type,net}|{number,name,type,nc:true}]}]}.
Independent membership: {version:1,nets:[names],components:{ref:{value,
footprint,physical,pins:[numbers]}}}. Do not derive it from a partial export.
Native pin functions/types, values, fields, physical exclusions and connectivity
are compared, not just counts. Hierarchy and suppressed ERC are unsupported.

CLI: native_import.py ROOT build|verify DECLARATION OUTPUT [--membership FILE]
Build refuses a nonempty OUTPUT. Provenance is not an engineering verdict.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile

if __package__:
    from . import native_schematic as native
else:
    import native_schematic as native


def require(test, reason):
    if not test:
        raise ValueError(reason)


def read(path):
    def unique(pairs):
        result={}
        for key,value in pairs:
            require(key not in result, f'duplicate JSON key: {key}')
            result[key]=value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def local(root, name, exists=True):
    require(isinstance(name,str) and name, 'relative file path required')
    p=PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and str(p)==name
            and name!='.' and '\\' not in name, 'invalid import path')
    path=(root/name).resolve()
    require(path.is_relative_to(root.resolve()), 'import path escapes root')
    if exists:
        require(path.is_file() and path.stat().st_size, f'missing/empty import file: {name}')
    return path


def declaration(root, path):
    d=read(path)
    native.keys(d,{'version','producer','intent','schematic','context'})
    require(type(d['version']) is int and d['version']==1,'unsupported import declaration')
    native.keys(d['producer'],{'entrypoint','inputs'})
    for key,values in (('inputs',d['producer']['inputs']),('context',d['context'])):
        require(isinstance(values,list) and values and all(isinstance(v,str) for v in values)
                and len(values)==len(set(values)),f'nonempty unique {key} required')
        for name in values: local(root,name)
    entry=d['producer']['entrypoint']
    require(isinstance(entry,str) and entry.endswith('.py') and entry in d['producer']['inputs'],
            'Python entrypoint must be a declared input')
    require(d['intent']!=d['schematic'] and all(n not in d['producer']['inputs']
            for n in (d['intent'],d['schematic'])), 'native/intent must be produced, not copied inputs')
    for name in (d['intent'],d['schematic']): local(root,name)
    require(Path(d['schematic']).suffix=='.kicad_sch','native KiCad schematic required')
    project=str(PurePosixPath(d['schematic']).with_suffix('.kicad_pro'))
    require(project in d['context'],'adjacent project context must be declared')
    return d


def check_intent(s):
    native.keys(s,{'version','nets','components'})
    require(type(s['version']) is int and s['version']==1,'unsupported intent')
    nets=s['nets'];comps=s['components']
    require(isinstance(nets,list) and nets and all(isinstance(n,str) and n for n in nets)
            and len(nets)==len(set(nets)), 'nonempty unique nets required')
    require(isinstance(comps,list) and comps,'empty component coverage')
    refs=set();used=set()
    for c in comps:
        native.keys(c,{'ref','value','footprint','physical','fields','pins'})
        require(isinstance(c['ref'],str) and re.fullmatch(r'[A-Z]+[1-9][0-9]*',c['ref'])
                and c['ref'] not in refs,'duplicate/invalid component')
        refs.add(c['ref'])
        require(isinstance(c['value'],str) and c['value'],'value required')
        require(type(c['physical']) is bool and isinstance(c['footprint'],str)
                and bool(c['footprint'])==c['physical'], 'physical part needs footprint; virtual part must have none')
        require(isinstance(c['fields'],dict) and all(isinstance(k,str) and k and isinstance(v,str)
                for k,v in c['fields'].items()),'invalid component fields')
        require(not set(c['fields']) & {'Reference','Value','Footprint','Datasheet','Description'},
                'reserved field in custom identity fields')
        require(isinstance(c['pins'],list) and c['pins'],'nonempty pins required')
        numbers=set()
        for p in c['pins']:
            native.keys(p,{'number','name','type'},{'net','nc'})
            require(isinstance(p['number'],str) and p['number'] and p['number'] not in numbers,
                    'duplicate/invalid pin')
            numbers.add(p['number'])
            require(isinstance(p['name'],str) and p['name'] and p['type'] in native.PIN_TYPES,
                    'invalid pin function/type')
            require(('net' in p)!=('nc' in p) and ('nc' not in p or p['nc'] is True),
                    'pin requires one net or explicit NC')
            if 'net' in p:
                require(isinstance(p['net'],str) and p['net'] in nets,'unknown net')
                used.add(p['net'])
    require(used==set(nets),'unused/omitted net coverage')
    return s


def membership(s,m):
    check_intent(s);native.keys(m,{'version','nets','components'})
    require(type(m['version']) is int and m['version']==1,'invalid membership version')
    expected=m['components']
    require(isinstance(expected,dict) and expected,'empty independent membership')
    normalized={}
    for ref,item in expected.items():
        native.keys(item,{'value','footprint','physical','pins'})
        pins=item['pins']
        require(type(item['physical']) is bool and isinstance(pins,list) and pins
                and all(isinstance(p,str) and p for p in pins) and len(pins)==len(set(pins)),
                'invalid membership pins/physical status')
        normalized[ref]=dict(item,pins=sorted(pins))
    actual={c['ref']:{k:c[k] for k in ('value','footprint','physical')} |
            {'pins':sorted(p['number'] for p in c['pins'])} for c in s['components']}
    require(isinstance(m['nets'],list) and all(isinstance(n,str) for n in m['nets'])
            and len(m['nets'])==len(set(m['nets'])),'invalid membership nets')
    require(actual==normalized and set(s['nets'])==set(m['nets']), 'independent membership mismatch')


def parity(s,path):
    tree=native.ET.parse(path)
    require(len(tree.findall('./design/sheet'))==1,'import supports flat schematic only')
    components=tree.findall('./components/comp')
    refs=[c.get('ref') for c in components]
    require(len(refs)==len(set(refs)),'duplicate exported component')
    # Native helper checks all values, footprints, nodes and intentional NCs.
    native.parity(s,path)
    libs={}
    for lib in tree.findall('./libparts/libpart'):
        key=(lib.get('lib'),lib.get('part'))
        require(key not in libs,'duplicate exported library identity')
        pins=lib.findall('./pins/pin')
        require(len(pins)==len({p.get('num') for p in pins}),'duplicate library pin')
        libs[key]={p.get('num'):(p.get('name'),p.get('type')) for p in pins}
    intended={c['ref']:c for c in s['components']}
    for comp in components:
        c=intended[comp.get('ref')];lib=comp.find('libsource')
        require(lib is not None,'missing library pin facts')
        expected={p['number']:(p['name'],p['type']) for p in c['pins']}
        require(libs.get((lib.get('lib'),lib.get('part')))==expected,'native pin function/type/coverage differs')
        fields={f.get('name'):f.text or '' for f in comp.findall('./fields/field')
                if f.get('name') not in {'Reference','Value','Footprint','Datasheet','Description'}}
        require(fields==c['fields'],'native ordering/custom fields differ')
        properties={p.get('name') for p in comp.findall('property')}
        require(('exclude_from_board' in properties)==(not c['physical'])
                and ('exclude_from_bom' in properties)==(not c['physical']), 'physical/BOM exclusions differ')


def artifacts(root,d,out):
    return {'source':local(root,d['intent']), 'schematic':local(root,d['schematic']),
            'netlist':out/'native.xml','erc':out/'native-erc.json',
            'erc_all':out/'native-erc-all.json','pdf':out/'native.pdf'}


def subjects(root,path,out):
    d=declaration(root,path)
    return set([path,*artifacts(root,d,out).values(),out/'receipt.json']+
               [local(root,n) for n in d['producer']['inputs']+d['context']])


def export(sch,out,s):
    paths={'netlist':out/'native.xml','erc':out/'native-erc.json',
           'erc_all':out/'native-erc-all.json','pdf':out/'native.pdf'}
    # Reject project-level overrides/exclusions before ERC. Local generated
    # projects with nonempty ERC customization need explicit future support.
    project=read(sch.with_suffix('.kicad_pro'))
    require(not project.get('erc'), 'customized/suppressed ERC is unsupported')
    out.mkdir(parents=True,exist_ok=True)
    native.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(paths['netlist']),str(sch)])
    parity(s,paths['netlist'])
    native.run(['kicad-cli','sch','erc','--format','json','--severity-all','-o',str(paths['erc_all']),str(sch)])
    native.erc_summary(paths['erc_all'])
    native.run(['kicad-cli','sch','erc','--format','json','--severity-error','--exit-code-violations','-o',str(paths['erc']),str(sch)])
    native.erc_clean(paths['erc'])
    native.run(['kicad-cli','sch','export','pdf','-o',str(paths['pdf']),str(sch)])
    return paths


def replay(root,d,work):
    for name in d['producer']['inputs']:
        target=local(work,name,False);target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(local(root,name),target)
    result=subprocess.run([sys.executable,str(local(work,d['producer']['entrypoint']))],
                          cwd=work,text=True,capture_output=True,timeout=120)
    require(result.returncode==0,f'producer replay failed: {result.stdout}\n{result.stderr}')
    require(not re.search(r'(?im)^\s*(?:error|fatal)\s*:',result.stdout+'\n'+result.stderr),
            'producer emitted error diagnostic')
    for name in (d['intent'],d['schematic'],*d['context']):
        require(local(root,name).read_bytes()==local(work,name).read_bytes(),f'producer replay differs: {name}')
    return local(work,d['schematic'])


def record(root,path,out):
    d=declaration(root,path)
    tracked=subjects(root,path,out)-{out/'receipt.json'}
    require(all(p.resolve().is_relative_to(root) for p in tracked),'import artifact escapes root')
    return {'version':1,'tool_version':native.TOOLCHAIN,
            'verifiers':{'native_import':native.digest(Path(__file__)),
                         'native_schematic':native.digest(Path(native.__file__))},
            'hashes':{p.relative_to(root).as_posix():native.digest(p) for p in sorted(tracked)},
            'erc_all_severity_counts':native.erc_summary(out/'native-erc-all.json'),
            'note':'Producer/native replay provenance only; no engineering or stage acceptance.'}


def erc_facts(path):
    """Keep source, scope, ignored checks and every violation; only date varies."""
    report=read(path)
    require(isinstance(report,dict),'ERC report must be an object')
    report.pop('date',None)
    return report


def verify(root,path,out,member=None,building=False):
    root=root.resolve();path=local(root,path.relative_to(root).as_posix());out=out.resolve()
    require(out.is_relative_to(root),'import output escapes root')
    require(native.run(['kicad-cli','version']).stdout.strip()==native.TOOLCHAIN,'wrong KiCad toolchain')
    d=declaration(root,path);s=check_intent(read(local(root,d['intent'])))
    if member is not None:
        member=local(root,member.relative_to(root).as_posix())
        membership(s,read(member))
    if not building:
        receipt=local(root,(out/'receipt.json').relative_to(root).as_posix())
        require(read(receipt)==record(root,path,out),'stale import receipt/subjects')
    with tempfile.TemporaryDirectory(prefix='vnext-import-') as tmp:
        work=Path(tmp)/'producer';work.mkdir()
        sch=replay(root,d,work)
        fresh=export(sch,Path(tmp)/'exports',s)
        if building:
            for p in fresh.values():shutil.copyfile(p,out/p.name)
        else:
            old=artifacts(root,d,out)
            parity(s,old['netlist']);native.erc_clean(old['erc'])
            for key in ('erc','erc_all'):
                require(erc_facts(fresh[key])==erc_facts(old[key]), 'ERC replay differs')
            require(native.raster_hashes(old['pdf'],Path(tmp)/'stored-page')==
                    native.raster_hashes(fresh['pdf'],Path(tmp)/'fresh-page'),'PDF replay differs')
    return {'declaration_sha256':native.digest(path),'build_receipt_sha256':native.digest(out/'receipt.json')
            if not building else None, 'membership_sha256':native.digest(member) if member else None,
            'verifier_sha256':native.digest(Path(__file__)),
            'note':'Flat imported producer/native replay; independent engineering admission still required.'}


def build(root,path,out):
    root=root.resolve();path=path.resolve();out=out.resolve()
    require(out.is_relative_to(root) and (not out.exists() or not any(out.iterdir())),
            'import output must be new/empty inside root')
    out.mkdir(parents=True,exist_ok=True)
    verify(root,path,out,building=True)
    (out/'receipt.json').write_text(json.dumps(record(root,path,out),indent=2,sort_keys=True)+'\n')
    return verify(root,path,out)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path);p.add_argument('command',choices=('build','verify'))
    p.add_argument('declaration');p.add_argument('output');p.add_argument('--membership')
    a=p.parse_args();root=a.root.resolve()
    try:
        path=local(root,a.declaration);out=local(root,a.output,False)
        result=build(root,path,out) if a.command=='build' else verify(root,path,out,
                       local(root,a.membership) if a.membership else None)
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,KeyError,TypeError,subprocess.TimeoutExpired,native.ET.ParseError) as exc:
        p.exit(1,f'native import refused: {exc}\n')


if __name__=='__main__': main()
