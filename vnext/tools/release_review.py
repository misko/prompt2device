"""Standalone prototype design archive and independent release admission.

An archive is not a seal or order authority. Requires verified non-RF scope.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
import assembly_verify as assembly

p = assembly.p
local = assembly.local
CONTRACT = '01_docs/release-review-contract.json'
RECEIPT = '06_build/checkpoints/release_reviewed.json'
STAGE = 'skills/pcb-design/workflow/stages/release-review.md'
MANUAL = 'skills/pcb-design/procedures/release/tooling.md'
CRITERIA = {'pin_identity', 'readability', 'electrical', 'layout_power', 'completeness', 'order_readiness'}
UPSTREAM = ('commissioned_brief', 'architecture_locked', 'parts_locked', 'schematic_reviewed',
            'placement_reviewed', 'mating_clearance', 'routed_board', 'layout_sealed',
            'fabrication_staged', 'assembly_verified')


def upstream_receipts(project):
    """Resolve the owning contract's selected revisions, never historical defaults."""
    routing=assembly.fab.seal.r
    contract=p.read(local(project,routing.CONTRACT))
    paths={role:'06_build/checkpoints/'+role+'.json' for role in UPSTREAM}
    paths['placement_reviewed']=routing.placement_receipt_path(contract)
    paths['mating_clearance']=routing.mating_receipt_path(contract)
    p.need(len(set(paths.values()))==len(paths),'upstream receipt roles alias one path')
    for role,name in paths.items():
        obj=p.read(local(project,name))
        p.need(obj.get('role')==role,'upstream receipt role differs: '+role)
    p.need(p.sha(local(project,paths['placement_reviewed']))==contract['placement_receipt_sha256'],
           'selected release placement adoption changed')
    return paths


def census(root, exclude=()):
    p.need(root.is_dir() and not root.is_symlink(), 'missing/linked release directory')
    result = {}
    for file in sorted(root.rglob('*')):
        p.need(not file.is_symlink(), 'linked release member')
        if file.is_file():
            name = file.relative_to(root).as_posix()
            if name not in exclude: result[name] = p.sha(file)
    return result


def dump(value): return json.dumps(value, indent=2, sort_keys=True)+'\n'


def refs(value):
    if isinstance(value, str): yield value
    elif isinstance(value, list):
        for item in value: yield from refs(item)
    elif isinstance(value, dict):
        for key,item in value.items(): yield key; yield from refs(item)


def closure(project, seeds):
    """Retain exact receipt subjects and transitive structured file references.

    Do not crawl arbitrary directories or interpret prose as executable paths.
    Owner replay remains the check that this dependency closure is sufficient.
    """
    found = {}; queue = list(seeds)
    while queue:
        name = queue.pop()
        if name in found: continue
        file = local(project, name); found[name] = p.sha(file)
        values = []
        if file.suffix == '.json': values = [p.read(file)]
        elif file.suffix == '.md':
            values = [json.loads(block) for block in re.findall(r'```json\s*\n(.*?)\n```', file.read_text(), re.S)]
        for obj in values:
            for item in refs(obj):
                if '/' not in item or '\n' in item or len(item)>1000: continue
                if Path(item).is_absolute() or '..' in Path(item).parts or str(Path(item)) != item: continue
                if any(len(os.fsencode(part))>255 for part in Path(item).parts): continue
                if (project/item).is_file(): queue.append(item)
    return found


def policy_check(project, policy):
    p.need(set(policy)=={'version','applicability','holds','dispositions'} and policy['version']==1,
           'unsupported release order policy')
    app = policy['applicability']
    p.need(app['rf'] is False, 'RF release requires a supported clearance adapter')
    assembly.text(app['rationale'])
    commission=p.read(local(project,'06_build/checkpoints/commissioned_brief.json'))
    cap='01_docs/capability-profile.json'
    p.need(commission['subjects'].get(cap)==p.sha(local(project,cap)) and
           p.read(local(project,cap))['rf'] is False, 'non-RF scope is not commissioned')
    p.need({cap,'06_build/checkpoints/commissioned_brief.json',commission['review']}<=set(app['evidence']),
           'applicability evidence coverage differs')
    names=set(app['evidence']); ids=set()
    p.need(isinstance(policy['holds'],list) and policy['holds'], 'explicit prototype order holds required')
    for kind in ('holds','dispositions'):
        for row in policy[kind]:
            p.need(set(row)=={'id','reason','evidence'}|({'closure'} if kind=='holds' else set()),
                   'unsupported hold/disposition')
            ident=assembly.text(row['id']); p.need(ident not in ids, 'duplicate hold/disposition');ids.add(ident)
            assembly.text(row['reason'])
            if kind=='holds': assembly.text(row['closure'])
            assembly.evidence(project,row['evidence'],{});names.update(row['evidence'])
    for name in names: local(project,name)
    return names


def inputs(project, name):
    contract=p.read(local(project,CONTRACT))
    p.need(set(contract)=={'version','authority','authority_sha256','assembly_receipt_sha256'} and
           contract['version'] in (1,2),'unsupported release contract')
    p.need(p.sha(local(project,contract['authority']))==contract['authority_sha256'],'release authority changed')
    p.need(p.sha(local(project,assembly.RECEIPT))==contract['assembly_receipt_sha256'], 'assembly adoption changed')
    accepted=assembly.check(project)
    spec=p.read(local(project,name))
    fields={'version','release_id','boards','order_policy','handoff','mechanical_basis','evidence'}
    if contract['version']==2:fields|={'runtime','calculations'}
    p.need(set(spec)==fields and spec['version']==contract['version'],'unsupported release manifest')
    p.need(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',spec['release_id']), 'unsafe release identity')
    assembly.text(spec['mechanical_basis']); assembly.evidence(project,spec['evidence'],{})
    quantities=p.read(local(project,assembly.fab.CONTRACT))['board_quantities']
    p.need(set(spec['boards'])==set(quantities),'release board coverage differs')
    for key,row in spec['boards'].items():
        p.need(set(row)=={'version','quantity'} and type(row['quantity']) is int and
               row['quantity']==quantities[key],'release board quantity differs')
        p.need(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',row['version']), 'unsafe board version')
    policy=p.read(local(project,spec['order_policy'])); evidence=policy_check(project,policy)
    review=assembly.fab.seal.r.review_json(project,accepted['review'])
    model=p.read(local(project,review['manifest'])); package=model['package']; views=review['output']
    p.need(p.read(local(project,views+'/assembly.json'))['version']==spec['version'],
           'release/assembly version adoption differs; no upgraded evidence downgrade')
    seeds={CONTRACT,contract['authority'],name,spec['order_policy'],spec['handoff'],
           '01_docs/placement-contract.json','01_docs/routing-contract.json',
           '01_docs/layout-seal-contract.json','01_docs/schematic-contract.json',
           *spec['evidence'],*evidence}
    if spec['version']==2:
        import release_evidence as upgraded
        upgraded.describe(project,spec,package,views)
        seeds.update(spec['runtime']+'/'+n for n in ('runtime.json','site-packages.tar.gz'))
        for names in spec['calculations'].values():seeds.update(names)
    for role,receipt in upstream_receipts(project).items():
        obj=p.read(local(project,receipt))
        seeds.update((receipt,obj['review'])); seeds.update(obj['subjects'])
        for n,digest in obj['subjects'].items():
            p.need(p.sha(local(project,n))==digest,'stale upstream subject: '+n)
    project_files=closure(project,seeds)
    origins={'source/project/'+n:dict(origin='project',path=n,sha256=d) for n,d in project_files.items()}
    # Preserve the complete adopted historical toolchain and current reusable package.
    archive=p.read(local(project,'01_docs/placement-contract.json'))['upstream_toolchain']
    for tree in ('tools','skills',archive):
        for n,digest in census(p.ROOT/tree).items():
            if '__pycache__' in Path(n).parts or n.endswith('.pyc'): continue
            rel=tree+'/'+n;origins['source/'+rel]=dict(origin='root',path=rel,sha256=digest)
    return spec,policy,origins,package,views


def presentation(project,spec,package,views):
    aliases={}
    def add(dest,src): local(project,src);aliases[dest]='source/project/'+src
    native=package+'/native';bundle=p.read(local(project,native+'/bundle.json'))
    schematic=p.read(local(project,native+'/design/'+bundle['schematics']['manifest']))
    for key in spec['boards']:
        for f in local(project,native+'/fab/'+key,False).rglob('*'):
            if not f.is_file(): continue
            rel=f.relative_to(project).as_posix();sub=f.relative_to(project/native/'fab'/key).as_posix()
            add(('pdf/'+key+'/'+sub[4:]) if sub.startswith('pdf/') else ('fab/'+key+'/'+sub), rel)
        add('pdf/'+key+'/schematic.pdf',native+'/design/'+schematic['boards'][key]['output']+'/native.pdf')
        for label in ('bare','populated'):add('mechanical/'+key+'-'+label+'.svg',views+'/'+key+'-'+label+'.svg')
    for f in local(project,package+'/assembly',False).iterdir():
        if f.is_file():add('fab/assembly/'+f.name,f.relative_to(project).as_posix())
    add('mechanical/geometry.json',views+'/geometry.json')
    add('HANDOFF.md',spec['handoff']);add('verification/order-policy.json',spec['order_policy'])
    for role,name in upstream_receipts(project).items():
        obj=p.read(local(project,name))
        add('verification/'+role+'.json',name)
        add('verification/reviews/'+Path(obj['review']).name,obj['review'])
    if spec.get('version')==2:
        import release_evidence as upgraded
        aliases.update(upgraded.describe(project,spec,package,views)['aliases'])
    return aliases


def order_text(spec,policy):
    rows=['# DO-NOT-ORDER / DO-NOT-UPLOAD', '',
          'Prototype PCB design candidate '+spec['release_id']+'. No seal or hardware qualification implied.', '',
          '## Active holds — closure required before ordering', '']
    for hold in policy['holds']:
        rows.extend(['- '+hold['id']+': '+hold['reason']+' Closure: '+hold['closure'], ''])
    rows.extend(['See HANDOFF.md for assembly, firmware, first-article and deployment obligations.', '',
                 'Mechanical scope: '+spec['mechanical_basis'], '', '## Reproduce offline', '',
                 'Requires Linux Landlock ABI >=3, libseccomp, Python3 with pcbnew, KiCad10.0.4,',
                 'pdftoppm and the system fonts used by the preserved PDF checks.',
                 *(['The indexed runtime.json also declares any required EGL/GL renderer, GPU driver and',
                    'specific character-device capabilities. A different or unavailable profile fails closed;',
                    'this Python capsule is not an OS image or a hardware-independent renderer.'] if spec.get('version')==2 else []),
                 'Run from this archive: `python3 -B source/tools/release_review.py replay --archive .`.',
                 'This checks the archived accepted chain, regenerates schematics/plots/PDF/DRC and assembly',
                 'views in disposable scratch. Original workspace and networking are denied.',
                 'Receipt verification is not independent electrical judgment or an immutable seal.', ''])
    return '\n'.join(rows)


def build(project,name,output):
    spec,policy,origins,package,views=inputs(project,name)
    aliases=presentation(project,spec,package,views)
    for source in aliases.values():
        if source not in origins:
            n=source.removeprefix('source/project/');origins[source]=dict(origin='project',path=n,sha256=p.sha(local(project,n)))
    dest=local(project,output,False);p.need(not dest.exists(),'refusing existing release output')
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.release-',dir=dest.parent) as tmp:
        stage=Path(tmp)/'archive';stage.mkdir()
        for n,row in origins.items():
            src=local(project if row['origin']=='project' else p.ROOT,row['path'])
            target=local(stage,n,False);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
        for n,src in aliases.items():
            target=local(stage,n,False);target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(local(stage,src),target)
        (stage/'ORDER-INSTRUCTIONS.md').write_text(order_text(spec,policy))
        record=dict(version=spec['version'],release_id=spec['release_id'],boards=spec['boards'],manifest=name,
                    assembly_receipt_sha256=p.sha(local(project,assembly.RECEIPT)),
                    order_status='DO-NOT-ORDER',design_status='UNREVIEWED',sealed=False,
                    order_policy=policy,mechanical_basis=spec['mechanical_basis'],
                    origins=origins,aliases=aliases,files=census(stage))
        if spec['version']==2:
            import release_evidence as upgraded
            record['recipient']=upgraded.describe(project,spec,package,views)
            (stage/'INDEX.md').write_text(upgraded.index(record))
            record['files']=census(stage)
        (stage/'release.json').write_text(dump(record));stage.rename(dest)
    return dict(archive=output,files=len(record['files']),design_status='UNREVIEWED')


def inventory_check(archive):
    record=p.read(local(archive,'release.json'))
    p.need(record.get('version') in (1,2) and record.get('sealed') is False and
           record.get('design_status')=='UNREVIEWED' and record.get('order_status')=='DO-NOT-ORDER',
           'unsupported mutable release record')
    p.need(census(archive,{'release.json'})==record['files'],'release inventory/hash differs')
    for n,row in record['origins'].items():
        p.need(p.sha(local(archive,n))==row['sha256'],'source inventory differs')
    for n,source in record['aliases'].items():
        p.need(p.sha(local(archive,n))==p.sha(local(archive,source)), 'release presentation/source differs')
    if record['version']==2:
        import release_evidence as upgraded
        p.need((archive/'INDEX.md').read_text()==upgraded.index(record), 'candidate status/index differs')
        recipient=record['recipient']
        p.need(recipient['aliases'].items()<=record['aliases'].items(), 'registered artifact aliases differ')
        for board,row in recipient['native'].items():
            for name in [*row['roles'].values(),*row['resources'],*recipient['calculations'][board]]:
                p.need(name in record['origins'], 'recipient entrypoint not inventoried')
        upgraded.release_runtime.validate(local(archive,recipient['runtime'],False))
    return record


def replay(archive):
    before=census(archive);record=inventory_check(archive)
    # Never execute an archive-supplied replacement for the currently trusted verifier.
    extra=('assembly_3d.py','mating_admission.py','release_evidence.py','release_runtime.py') if record['version']==2 else ()
    for tool in (*assembly.fab.TOOLS,'assembly_verify.py','offline_replay.py','release_review.py',*extra):
        p.need(p.sha(local(archive,'source/tools/'+tool))==p.sha(Path(__file__).parent/tool),
               'archive verifier differs: '+tool)
    with tempfile.TemporaryDirectory(prefix='vnext-release-offline-') as tmp:
        scratch=Path(tmp);copy=scratch/'archive';shutil.copytree(archive,copy)
        runtime_args=['--runtime',str(copy/record['recipient']['runtime'])] if record['version']==2 else []
        command=[sys.executable,'-B',str(Path(__file__).with_name('offline_replay.py')),
                 '--scratch',str(scratch),'--readonly-archive',*runtime_args,str(copy/'source/tools/release_review.py'),
                 'audit','--archive',str(copy)]
        result=subprocess.run(command,cwd=scratch,capture_output=True,text=True,timeout=1200 if extra else 240)
        p.need(result.returncode==0,'isolated owning replay failed:\n'+result.stderr[-12000:]+result.stdout[-1500:])
        observed=json.loads(result.stdout)
        graphics=None
        if record['version']==2:
            runtime=p.read(local(archive,record['recipient']['runtime']+'/runtime.json'))
            graphics=runtime.get('graphics')
            if graphics:p.need(observed.get('renderer_profile')==graphics['profile'],
                               'isolated renderer observation differs')
        p.need(census(copy)==before,'offline replay mutated archive')
    p.need(census(archive)==before,'release archive mutated')
    result=dict(replayed_boards=sorted(record['boards']),offline=True,original_workspace_access=False,
                assembly_receipt_sha256=record['assembly_receipt_sha256'])
    if graphics:result['renderer_profile']=graphics['profile']
    return result


def compare(project,name,archive):
    spec,policy,origins,package,views=inputs(project,name)
    record=inventory_check(archive);aliases=presentation(project,spec,package,views)
    p.need(record['version']==spec.get('version',1), 'release version adoption differs')
    for source in aliases.values():
        if source not in origins:
            n=source.removeprefix('source/project/');origins[source]=dict(origin='project',path=n,sha256=p.sha(local(project,n)))
    p.need(record['manifest']==name and record['release_id']==spec['release_id'] and
           record['boards']==spec['boards'] and record['origins']==origins and
           record['aliases']==aliases and record['order_policy']==policy and
           record['assembly_receipt_sha256']==p.sha(local(project,assembly.RECEIPT)) and
           record['mechanical_basis']==spec['mechanical_basis'],'release source/adoption differs')
    p.need((archive/'ORDER-INSTRUCTIONS.md').read_text()==order_text(spec,policy),'order hold presentation differs')
    expected=set(origins)|set(aliases)|{'ORDER-INSTRUCTIONS.md'}
    if record['version']==2:
        import release_evidence as upgraded
        p.need(record['recipient']==upgraded.describe(project,spec,package,views), 'recipient evidence differs')
        expected.add('INDEX.md')
    p.need(set(record['files'])==expected,'unaccounted release members')
    return record


def audit(archive):
    record=inventory_check(archive)
    compare(archive/'source/project',record['manifest'],archive)
    result=dict(archive_inputs_and_owning_chain='PASS',boards=sorted(record['boards']))
    if record['version']==2:
        import release_runtime
        runtime=release_runtime.validate(local(archive,record['recipient']['runtime'],False))
        if runtime.get('graphics'):
            actual=release_runtime.rendering_profile()
            p.need(actual==runtime['graphics']['profile'],'archive renderer observation differs')
            result['renderer_profile']=actual
    return result


def verify(project,name,output):
    archive=local(project,output,False);compare(project,name,archive)
    result=replay(archive)
    return dict(subjects={output+'/'+n:d for n,d in census(archive).items()},replay=result)


def certificate(project,name):
    stages=[s for s in p.read(p.ROOT/'skills/pcb-design/workflow/graph.json')['stages']
            if s['spec']['id']=='PCB-RELEASE-REVIEW']
    p.need(len(stages)==1,'release stage identity differs');stage=stages[0]
    binding=stage.get('local_execution',{})
    p.need(stage['spec']['requires']==['assembly_verified','rf_fab_clearance'] and
           stage['spec']['produces']==['release_reviewed'],'release graph contract differs')
    p.need('local_definition' not in stage and binding.get('tool')=='tools/release_review.py' and
           binding.get('contract')==STAGE and binding.get('status')=='pilot_under_validation',
           'release review adapter not adopted')
    review=assembly.fab.seal.r.review_json(project,name)
    result=verify(project,review['manifest'],review['output'])
    p.need(review.get('schema')==1 and review.get('stage')=='PCB-RELEASE-REVIEW' and
           review.get('design_verdict')=='SOUND' and review.get('order_verdict')=='DO-NOT-ORDER',
           'explicit sound design/separate order verdict required')
    p.need(assembly.text(review['author']).casefold()!=assembly.text(review['reviewer']).casefold(),
           'independent release reviewer required')
    p.need(review.get('subjects')==result['subjects'],'complete release review subject coverage differs')
    record=p.read(local(project,review['output']+'/release.json'))
    if record['version']==2:
        import release_evidence as upgraded
    criteria=CRITERIA|upgraded.EXTRA_CRITERIA if record['version']==2 else CRITERIA
    checks=review.get('checks',{});p.need(set(checks)==criteria,'release review criteria differ')
    geometry=p.read(local(project,review['output']+'/mechanical/geometry.json'))
    boards=sorted(record['boards'])
    units={'pin_identity':sorted(b+'/'+r for b in boards for r in geometry['boards'][b]['references']),
           'readability':boards,'electrical':boards,'layout_power':boards,
           'completeness':sorted(b+'/'+part for b in boards for part in ('source','schematic','fab','assembly','mechanical')),
           'order_readiness':sorted(h['id'] for h in record['order_policy']['holds'])}
    if record['version']==2:
        units.update(upgraded.units(record));units['completeness']=upgraded.completeness(record)
        upgraded.lenses(review)
    for key,row in checks.items():
        p.need(row.get('verdict')=='PASS','release check not PASS: '+key)
        assembly.text(row.get('rationale'));ev=row.get('evidence')
        p.need(isinstance(ev,list) and ev and all(n in result['subjects'] for n in ev),'unbound release evidence')
        scope=row.get('coverage')
        p.need(isinstance(scope,dict) and set(scope)=={'required','reviewed','findings'} and
               scope['required']==units[key] and scope['reviewed']==units[key] and
               scope['findings']==[], 'ungraded release scope: '+key)
    tools=('release_review.py','offline_replay.py')
    if record['version']==2:tools+=('release_evidence.py','release_runtime.py')
    return dict(schema=1,role='release_reviewed',review=name,review_sha256=p.sha(local(project,name)),
                subjects=result['subjects'],stage_spec=stage['spec'],design_verdict='SOUND',
                order_verdict='DO-NOT-ORDER',next_owner='PCB-RELEASE-SEAL',
                tools={n:p.sha(Path(__file__).parent/n) for n in tools},
                guidance={n:p.sha(p.ROOT/n) for n in (STAGE,MANUAL)})


def check(project):
    old=p.read(local(project,RECEIPT));p.need(old==certificate(project,old['review']),'stale release receipt');return old


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['build','verify','replay','audit','issue','check'])
    parser.add_argument('--project',type=Path);parser.add_argument('--archive',type=Path)
    for key in ('manifest','output','review'):parser.add_argument('--'+key)
    args=parser.parse_args()
    try:
        if args.action in ('replay','audit'):
            result=(replay if args.action=='replay' else audit)(args.archive.resolve())
        else:
            project=args.project.resolve()
            if args.action in ('build','verify'):
                result=(build if args.action=='build' else verify)(project,args.manifest,args.output)
            elif args.action=='check':result=check(project)
            else:
                result=certificate(project,args.review);target=local(project,RECEIPT,False)
                with target.open('x') as stream:stream.write(dump(result))
        print(dump(result));return 0
    except (ValueError,KeyError,TypeError,OSError,AttributeError,subprocess.TimeoutExpired) as exc:
        print('Release refused: '+str(exc),file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
