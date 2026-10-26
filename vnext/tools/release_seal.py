"""Git-backed immutable prototype PCB release. No publication or order authority."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
ROOT = Path(__file__).resolve().parents[1]
CONTRACT = '01_docs/release-seal-contract.json'
RECEIPT = '06_build/checkpoints/sealed_release.json'
REVIEW_RECEIPT = '06_build/checkpoints/release_reviewed.json'
STAGE = 'skills/pcb-design/workflow/stages/release-seal.md'
MANUAL = 'skills/pcb-design/procedures/release/seal-tooling.md'
CRITERIA = {'provenance', 'completeness', 'replay', 'integrity', 'handoff'}


def need(value, message):
    if not value: raise ValueError(message)


def pairs(items):
    result={}
    for k,v in items:
        need(k not in result, 'duplicate JSON key');result[k]=v
    return result


def read(file): return json.loads(file.read_text(),object_pairs_hook=pairs)
def dump(value): return json.dumps(value,indent=2,sort_keys=True)+'\n'
def sha(file): return hashlib.sha256(file.read_bytes()).hexdigest()


def local(root,name,exists=True):
    need(isinstance(name,str) and name and not Path(name).is_absolute() and
         '..' not in Path(name).parts and '.git' not in Path(name).parts and
         str(Path(name))==name, 'invalid relative release path')
    file=root/name
    need(not any((root/Path(*Path(name).parts[:i])).is_symlink()
                 for i in range(1,len(Path(name).parts)+1)), 'linked release path')
    need(file.resolve().is_relative_to(root.resolve()), 'release path escapes root')
    if exists: need(file.is_file(),'missing release file: '+name)
    return file


def inventory(root):
    need(root.is_dir() and not root.is_symlink(),'missing/linked directory')
    result={}
    def inaccessible(error): raise error
    for directory,dirs,files in os.walk(root,onerror=inaccessible):
        base=Path(directory)
        if base==root and '.git' in dirs: dirs.remove('.git')
        for n in dirs+files: need(not (base/n).is_symlink(),'linked inventory member')
        for n in files:
            file=base/n;name=file.relative_to(root).as_posix()
            need('.git' not in file.relative_to(root).parts,'nested Git metadata')
            need(file.is_file() and not file.stat().st_mode & 0o111,
                 'nonregular/executable release member');result[name]=sha(file)
    return dict(sorted(result.items()))


def copy(src,dest):
    need(src.is_file() and not src.is_symlink(),'invalid copy source')
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('xb') as out,src.open('rb') as inp:shutil.copyfileobj(inp,out)


def write(dest,value):
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('x') as stream:stream.write(dump(value))


def run(args,cwd=None,timeout=360):
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_NO_REPLACE_OBJECTS='1')
    result=subprocess.run(args,cwd=cwd,env=env,capture_output=True,timeout=timeout)
    need(result.returncode==0,'command failed: '+str(args)+'\n'+result.stderr.decode(errors='replace')[-10000:])
    return result.stdout


def git(repo,*args):
    return run(['git','-c','core.hooksPath=/dev/null','-c','commit.gpgSign=false','-C',str(repo),*args])


def parents(repo,commit):
    # rev-list honors grafts/replacement refs; raw commit headers are authority.
    raw=git(repo,'cat-file','commit',commit).split(b'\n\n',1)[0]
    return [line.split(b' ',1)[1].decode() for line in raw.splitlines() if line.startswith(b'parent ')]


def git_tree(repo,commit):
    need(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}',commit),'invalid commit identity')
    need(git(repo,'cat-file','-t',commit).strip()==b'commit','source/seal object is not a commit')
    entries={}
    for line in git(repo,'ls-tree','-rz','--full-tree',commit).split(b'\0'):
        if not line:continue
        header,name=line.split(b'\t',1);mode,kind,oid=header.split();name=name.decode()
        local(repo,name,False)
        need(mode==b'100644' and kind==b'blob','nonregular/executable Git entry unsupported')
        entries[name]=oid.decode()
    # Stream object bodies rather than starting thousands of git processes or
    # capturing every PDF at once. Git object IDs and SHA256 inventory differ.
    hashes={};proc=subprocess.Popen(['git','-C',str(repo),'cat-file','--batch'],
                                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                    env=dict(os.environ,GIT_NO_REPLACE_OBJECTS='1'))
    try:
        for oid in sorted(set(entries.values())):
            proc.stdin.write((oid+'\n').encode());proc.stdin.flush()
            header=proc.stdout.readline().split()
            need(len(header)==3 and header[0].decode()==oid and header[1]==b'blob','missing Git blob')
            remaining=int(header[2]);h=hashlib.sha256()
            while remaining:
                block=proc.stdout.read(min(1048576,remaining));need(block,'truncated Git object')
                h.update(block);remaining-=len(block)
            need(proc.stdout.read(1)==b'\n','invalid Git object framing');hashes[oid]=h.hexdigest()
        proc.stdin.close();need(proc.wait(timeout=30)==0,'Git object reader failed')
    finally:
        if proc.poll() is None:proc.kill();proc.wait()
        for stream in (proc.stdin,proc.stdout,proc.stderr):
            if stream is not None:stream.close()
    return {name:hashes[oid] for name,oid in sorted(entries.items())}


def review_json(file):
    blocks=re.findall(r'```json\s*\n(.*?)\n```',file.read_text(),re.S)
    need(len(blocks)==1,'one independent review JSON block required')
    return json.loads(blocks[0],object_pairs_hook=pairs)


def archive_check(archive,review_file,receipt_file):
    record=read(local(archive,'release.json'));actual=inventory(archive)
    need(record.get('version') in (1,2),'unsupported release version')
    need(actual.pop('release.json')==sha(archive/'release.json') and actual==record['files'],
         'archive membership/hash differs')
    receipt=read(receipt_file);review=review_json(review_file)
    need(receipt['role']=='release_reviewed' and receipt['review_sha256']==sha(review_file) and
         receipt['design_verdict']=='SOUND' and receipt['order_verdict']=='DO-NOT-ORDER',
         'accepted independent release review required')
    expected={review['output']+'/'+n:d for n,d in inventory(archive).items()}
    need(receipt['subjects']==review['subjects']==expected,'review/archive exact scope differs')
    for name,digest in receipt['tools'].items():
        need(sha(local(archive,'source/tools/'+name))==digest,'adopted verifier identity differs')
    for name,digest in receipt['guidance'].items():
        need(sha(local(archive,'source/'+name))==digest,'adopted guidance identity differs')
    if record['version']==2:
        need(record.get('design_status')=='UNREVIEWED' and record.get('order_status')=='DO-NOT-ORDER' and
             record.get('sealed') is False,'v2 candidate status differs')
        runtime=record['recipient']['runtime']
        need({runtime+'/runtime.json',runtime+'/site-packages.tar.gz','INDEX.md'}<=set(record['files']),
             'v2 runtime/index missing')
        need({'release_evidence.py','release_runtime.py'}<=set(receipt['tools']),
             'v2 reviewer tool coverage missing')
    return record,review,receipt


def owning_check(archive,review_file,receipt_file):
    """Rebuild a complete historical project and owning checker, offline/read-only.

    The independent review sits outside its own self-inventoried archive; restore
    its original logical paths without inserting it into the reviewed payload.
    """
    record,review,receipt=archive_check(archive,review_file,receipt_file)
    before=inventory(archive)
    with tempfile.TemporaryDirectory(prefix='vnext-seal-owning-') as tmp:
        scratch=Path(tmp);workspace=scratch/'archive/workspace'
        shutil.copytree(archive/'source',workspace)
        project=workspace/'project';target=local(project,review['output'],False)
        need(not target.exists(),'release path collides with historical source')
        shutil.copytree(archive,target)
        copy(review_file,local(project,receipt['review'],False))
        copy(receipt_file,local(project,REVIEW_RECEIPT,False))
        snapshot=inventory(workspace)
        guard=workspace/'tools/offline_replay.py';checker=workspace/'tools/release_review.py'
        runtime_args=[]
        if record['version']==2:
            runtime=record['recipient']['runtime']
            need(runtime.startswith('source/'),'runtime outside retained source')
            runtime_args=['--runtime',str(workspace/runtime.removeprefix('source/'))]
        result=run([sys.executable,'-B',str(guard),'--scratch',str(scratch),'--readonly-archive',
                    *runtime_args,str(checker),'check','--project',str(project)],
                   timeout=2400 if record['version']==2 else 360)
        need(json.loads(result)==receipt,'isolated owning acceptance differs')
        need(inventory(workspace)==snapshot,'owning replay mutated restored source')
    need(inventory(archive)==before,'owning replay mutated original archive')
    result=dict(boards=record['boards'],release_id=record['release_id'],
                design_verdict='SOUND',order_verdict='DO-NOT-ORDER',
                release_reviewed_sha256=sha(receipt_file),offline=True,archive_readonly=True)
    if record['version']==2:
        runtime=read(local(archive,record['recipient']['runtime']+'/runtime.json'))
        if runtime.get('graphics'):result['renderer_profile']=runtime['graphics']['profile']
    return result


def graph_check(root):
    stages=[s for s in read(root/'skills/pcb-design/workflow/graph.json')['stages']
            if s['spec']['id']=='PCB-RELEASE-SEAL']
    need(len(stages)==1,'seal stage identity differs');stage=stages[0];binding=stage.get('local_execution',{})
    need(stage['spec']['requires']==['release_reviewed'] and stage['spec']['produces']==['sealed_release'],
         'seal graph contract differs')
    need('local_definition' not in stage and binding.get('tool')=='tools/release_seal.py' and
         binding.get('contract')==STAGE and binding.get('status')=='pilot_under_validation','seal adapter not adopted')
    return stage['spec']


def project_inputs(project):
    c=read(local(project,CONTRACT))
    need(set(c)=={'version','authority','authority_sha256','archive','archive_record_sha256','review',
                  'review_sha256','release_reviewed_sha256','repository','release_id','boards','seal_tool_sha256'} and
         c['version']==1,'unsupported seal contract')
    for name,digest in [(c['authority'],c['authority_sha256']),(c['review'],c['review_sha256']),
                        (REVIEW_RECEIPT,c['release_reviewed_sha256'])]:
        need(sha(local(project,name))==digest,'stale seal adoption: '+name)
    archive=local(project,c['archive'],False)
    need(sha(local(archive,'release.json'))==c['archive_record_sha256'],'archive adoption changed')
    need(sha(Path(__file__))==c['seal_tool_sha256'],'seal implementation changed')
    record,_,_=archive_check(archive,local(project,c['review']),local(project,REVIEW_RECEIPT))
    need(record['release_id']==c['release_id'] and record['boards']==c['boards'],'board/version/quantity adoption differs')
    # Frozen tools may differ from today's development tools. Live participating
    # project inputs may NOT silently differ from the accepted design.
    for row in record['origins'].values():
        if row['origin']=='project':need(sha(local(project,row['path']))==row['sha256'],'live source changed: '+row['path'])
    graph_check(ROOT)
    return c,archive


def source_manifest(repo):
    name='inputs/source-files.json';expected=read(local(repo,name))
    actual=inventory(repo);actual.pop(name,None)
    need(actual==expected,'source snapshot inventory differs')
    return inventory(repo)


def prepare(project):
    c,archive=project_inputs(project);repo=local(project,c['repository'],False)
    need(not repo.exists(),'refusing existing source repository')
    # A source commit is not acceptance. Full owning replay occurs on staging
    # and again on the committed release before independent admission.
    repo.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.seal-source-',dir=repo.parent) as tmp:
        stage=Path(tmp)/'repo';stage.mkdir()
        for name in read(archive/'release.json')['origins']:
            need(name.startswith('source/'),'unexpected archive source location')
            copy(local(archive,name),local(stage,name,False))
        mapping={'archive-record.json':archive/'release.json','order-instructions.md':archive/'ORDER-INSTRUCTIONS.md',
                 'release-review.md':local(project,c['review']),'release_reviewed.json':local(project,REVIEW_RECEIPT),
                 'seal-contract.json':local(project,CONTRACT),'authority.md':local(project,c['authority'])}
        if read(archive/'release.json')['version']==2:mapping['archive-index.md']=archive/'INDEX.md'
        for name,src in mapping.items():copy(src,stage/'inputs'/name)
        for tree in ('tools','skills'):
            for name in inventory(ROOT/tree):
                if '__pycache__' in Path(name).parts or name.endswith('.pyc'):continue
                copy(local(ROOT,tree+'/'+name),stage/'seal-tools'/tree/name)
        # Complete adopted upstream toolchain remains under source/toolchains.
        write(stage/'inputs/source-files.json',inventory(stage))
        source_manifest(stage)
        git(stage,'init','-b','codex/'+c['release_id']);git(stage,'add','--','.')
        git(stage,'commit','-m','Source snapshot for '+c['release_id'])
        source=git(stage,'rev-parse','HEAD').decode().strip()
        need(git_tree(stage,source)==inventory(stage),'source commit differs from actual inputs')
        stage.rename(repo)
    return dict(repository=c['repository'],source_commit=source,release_id=c['release_id'])


def source_check(repo,source):
    tree=git_tree(repo,source)
    need(parents(repo,source)==[],
         'source commit must be the isolated repository root')
    expected=read(local(repo,'inputs/source-files.json'))
    need({n:d for n,d in tree.items() if n!='inputs/source-files.json'}==expected and
         tree.get('inputs/source-files.json')==sha(repo/'inputs/source-files.json'),'committed source inventory differs')
    actual=inventory(repo)
    need({n:d for n,d in actual.items() if not n.startswith('release/')}==tree,'dirty/missing/extra source input')
    need(sha(local(repo,'seal-tools/tools/release_seal.py'))==sha(Path(__file__)),'seal verifier version differs')
    graph_check(repo/'seal-tools')
    return tree


def construct(repo,dest):
    record=read(local(repo,'inputs/archive-record.json'))
    archive=dest/'archive';archive.mkdir(parents=True)
    for name in record['origins']:copy(local(repo,name),local(archive,name,False))
    for name,src in record['aliases'].items():copy(local(archive,src),local(archive,name,False))
    copy(local(repo,'inputs/order-instructions.md'),archive/'ORDER-INSTRUCTIONS.md')
    if record['version']==2:copy(local(repo,'inputs/archive-index.md'),archive/'INDEX.md')
    copy(local(repo,'inputs/archive-record.json'),archive/'release.json')
    copy(local(repo,'inputs/release-review.md'),dest/'verification/release-review.md')
    copy(local(repo,'inputs/release_reviewed.json'),dest/'verification/release_reviewed.json')
    archive_check(archive,dest/'verification/release-review.md',dest/'verification/release_reviewed.json')
    if record['version']==2:
        receipt=read(dest/'verification/release_reviewed.json')
        status=dict(version=1,release_id=record['release_id'],boards=record['boards'],
                    design_verdict=receipt['design_verdict'],order_verdict=receipt['order_verdict'],
                    authority='verification/release_reviewed.json',
                    authority_sha256=sha(dest/'verification/release_reviewed.json'),
                    candidate='archive/release.json',candidate_sha256=sha(archive/'release.json'),
                    candidate_status='Historical UNREVIEWED snapshot; superseded only by this accepted review',
                    provenance='seal.json',holds=record['order_policy']['holds'])
        write(dest/'CURRENT-STATUS.json',status)
        text='# Current release status\n\nSOUND / DO-NOT-ORDER\n\n'
        text+='Authority: [accepted release review](verification/release_reviewed.json).\n\n'
        text+='The archive is the historical candidate reviewed by that receipt, not a competing current status.\n\n'
        for h in status['holds']:text+='- '+h['id']+': '+h['reason']+' Closure: '+h['closure']+'\n'
        with (dest/'CURRENT-STATUS.md').open('x') as stream:stream.write(text)
        rows=['# '+record['release_id'], '', 'SOUND / DO-NOT-ORDER', '',
              '[Current status and all holds](CURRENT-STATUS.md) · [Machine authority](CURRENT-STATUS.json)', '',
              '[Source commit and seal inventory](seal.json) · [Independent release review](verification/release-review.md)', '',
              '[Complete candidate evidence index](archive/INDEX.md) · [Order instructions](archive/ORDER-INSTRUCTIONS.md)', '']
        for board,identity in sorted(record['boards'].items()):
            rows.extend(['## '+board+' / '+identity['version']+' / quantity '+str(identity['quantity']), ''])
            for role,path in record['recipient']['native'][board]['roles'].items():
                rows.append('- ['+role+'](archive/'+path+')')
            for path in record['recipient']['calculations'][board]:
                rows.append('- [Design calculation](archive/'+path+')')
            for path in sorted(record['aliases']):
                if path.startswith(('fab/'+board+'/', 'pdf/'+board+'/', 'mechanical/'+board+'/', 'documentation/'+board+'/',
                                    'fab/assembly/'+board+'-')):
                    rows.append('- ['+path+'](archive/'+path+')')
            rows.append('')
        with (dest/'INDEX.md').open('x') as stream:stream.write('\n'.join(rows))
    return record


def stage(repo):
    source=git(repo,'rev-parse','HEAD').decode().strip();tree=source_check(repo,source)
    need(not git(repo,'status','--porcelain','--untracked-files=all').strip(),'dirty source repository')
    need(not (repo/'release').exists(),'refusing existing release version')
    with tempfile.TemporaryDirectory(prefix='vnext-seal-stage-') as tmp:
        dest=Path(tmp)/'release';record=construct(repo,dest)
        result=owning_check(dest/'archive',dest/'verification/release-review.md',dest/'verification/release_reviewed.json')
        seal=dict(version=1,role='release_seal_record',source_commit=source,release_id=record['release_id'],
                  boards=record['boards'],design_verdict='SOUND',order_verdict='DO-NOT-ORDER',
                  immutable_when='committed as the direct child of source_commit',source_files=tree,
                  files=inventory(dest),owning_replay=result)
        write(dest/'seal.json',seal);shutil.copytree(dest,repo/'release')
    return dict(source_commit=source,release_id=record['release_id'],staged_files=len(seal['files'])+1)


def staged_check(repo,replay=True):
    seal=read(local(repo,'release/seal.json'));source=seal['source_commit'];tree=source_check(repo,source)
    c=read(local(repo,'inputs/seal-contract.json'));archive=repo/'release/archive'
    record=read(local(repo,'inputs/archive-record.json'))
    need(c.get('version')==1 and record['release_id']==c['release_id'] and
         record['boards']==c['boards'] and
         sha(local(repo,'inputs/authority.md'))==c['authority_sha256'],
         'committed authority/board adoption differs')
    need(seal.get('version')==1 and seal.get('role')=='release_seal_record' and
         seal['source_files']==tree and seal['release_id']==c['release_id'] and seal['boards']==c['boards'] and
         seal['design_verdict']=='SOUND' and seal['order_verdict']=='DO-NOT-ORDER','seal adoption/identity differs')
    actual=inventory(repo/'release');actual.pop('seal.json')
    need(actual==seal['files'],'stale/missing/extra release payload')
    need(sha(archive/'release.json')==c['archive_record_sha256'] and
         sha(repo/'release/verification/release-review.md')==c['review_sha256'] and
         sha(repo/'release/verification/release_reviewed.json')==c['release_reviewed_sha256'] and
         sha(Path(__file__))==c['seal_tool_sha256'],'accepted archive/review/tool changed')
    # Source commit must contain the actual bytes used to create every archive
    # member; a self-consistent but unrelated staged packet cannot pass.
    with tempfile.TemporaryDirectory(prefix='vnext-seal-reconstruct-') as tmp:
        fresh=Path(tmp)/'release';construct(repo,fresh)
        need(inventory(fresh)==seal['files'],'source/staged archive reconstruction differs')
    if replay:
        result=owning_check(archive,repo/'release/verification/release-review.md',repo/'release/verification/release_reviewed.json')
        need(result==seal['owning_replay'],'owning release result differs')
    return seal


def commit(repo):
    # Exact reconstruction prevents staging drift; do not regenerate the same
    # PCB a third time here. Post-commit check/issue MUST replay before acceptance.
    seal=staged_check(repo,replay=False);source=seal['source_commit']
    need(git(repo,'rev-parse','HEAD').decode().strip()==source,'source HEAD changed before seal')
    git(repo,'add','--','release')
    changed=git(repo,'diff','--cached','--name-only','-z',source).decode().split('\0')
    need({n for n in changed if n}=={'release/'+n for n in inventory(repo/'release')},'staged Git scope differs')
    git(repo,'commit','-m','Seal '+seal['release_id']+' prototype PCB design')
    return check(repo,replay=False)


def check(repo,replay=True):
    need(git(repo,'rev-parse','--show-toplevel').decode().strip()==str(repo.resolve()),'not the isolated repository root')
    need(not git(repo,'status','--porcelain','--untracked-files=all').strip(),'dirty sealed repository')
    seal=staged_check(repo,replay=replay);head=git(repo,'rev-parse','HEAD').decode().strip()
    need(parents(repo,head)==[seal['source_commit']],
         'seal commit is not the direct source child')
    need(git_tree(repo,head)==inventory(repo),'committed tree/worktree differs')
    return dict(version=1,role='sealed_release',release_id=seal['release_id'],boards=seal['boards'],
                source_commit=seal['source_commit'],seal_commit=head,seal_record_sha256=sha(repo/'release/seal.json'),
                design_verdict='SOUND',order_verdict='DO-NOT-ORDER',files=len(inventory(repo/'release')),
                committed_owning_replay=bool(replay))


def certificate(project,name):
    c,_=project_inputs(project);repo=local(project,c['repository'],False);result=check(repo)
    review=review_json(local(project,name));need(review.get('schema')==1 and review.get('stage')=='PCB-RELEASE-SEAL' and
         review.get('verdict')=='PASS','independent seal review not PASS')
    need(isinstance(review.get('author'),str) and isinstance(review.get('reviewer'),str) and
         review['author'].strip() and review['reviewer'].strip() and
         review['author'].strip().casefold()!=review['reviewer'].strip().casefold(),'independent reviewer required')
    need(review.get('result')==result,'independent review does not bind actual committed release')
    checks=review.get('checks',{});need(set(checks)==CRITERIA,'seal review scope differs')
    for key,row in checks.items():
        need(row.get('verdict')=='PASS' and isinstance(row.get('rationale'),str) and row['rationale'].strip(),
             'ungraded seal criterion: '+key)
    return dict(**result,review=name,review_sha256=sha(local(project,name)),contract_sha256=sha(local(project,CONTRACT)),
                stage_spec=graph_check(ROOT),tool_sha256=sha(Path(__file__)),
                guidance={n:sha(ROOT/n) for n in (STAGE,MANUAL)},repository=c['repository'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','stage','commit','check','issue','check-receipt'])
    parser.add_argument('--project',type=Path);parser.add_argument('--repo',type=Path);parser.add_argument('--review')
    args=parser.parse_args()
    try:
        if args.action=='prepare':result=prepare(args.project.resolve())
        elif args.action in ('stage','commit','check'):result=globals()[args.action](args.repo.resolve())
        else:
            project=args.project.resolve()
            if args.action=='issue':
                result=certificate(project,args.review);write(local(project,RECEIPT,False),result)
            else:
                old=read(local(project,RECEIPT));result=certificate(project,old['review'])
                need(result==old,'stale sealed-release receipt')
        print(dump(result));return 0
    except (ValueError,KeyError,TypeError,OSError,subprocess.TimeoutExpired) as exc:
        print('Seal refused: '+str(exc),file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
