"""Registered-scene evidence for the existing mating owner; no receipt issuer.

Deterministic replay establishes geometry/provenance. Independent exact-subject
judgments establish the adequacy of tolerances, omitted features and engagement.
Neither one substitutes for the other or for actual hardware qualification.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import placement as p

CHECKS={'registration','model_coverage','clearance','tolerances','engagement','access'}


def inventory(directory):
    p.need(directory.is_dir() and not directory.is_symlink(),'regular toolchain directory required')
    result={}
    for file in directory.rglob('*'):
        p.need(not file.is_symlink(),'linked toolchain member')
        if file.is_file():result[file.relative_to(directory).as_posix()]=p.sha(file)
    return result


def geometry(path):
    # Retain all pads/nets/attributes/models/keepouts/outline and their UUIDs.
    # Only the existing layout owner's documented cosmetic projection applies.
    import routing as r
    import layout_seal as s
    board=p.pcb.LoadBoard(str(path))
    return (board.GetDesignSettings().GetBoardThickness(),board.GetCopperLayerCount(),
            sorted(json.dumps(s.physical(s.parse(f)),sort_keys=True)
                   for f in r.identity(path) if s.physical(s.parse(f)) is not None))


def limitation_inventory(report):
    result={}
    def add(owner,words):
        for word in words:
            p.need(isinstance(word,str) and word.strip(),'empty scene limitation')
            key=hashlib.sha256((owner+'\n'+word).encode()).hexdigest()
            result[key]={'owner':owner,'text':word}
    add('scene',report['unresolved'])
    for name,row in report['models'].items():add('model:'+name,row['limitations'])
    for name,row in report['boards'].items():add('board:'+name,[row['board_datum']['limitation']])
    return result


def evidence(project,names,subjects):
    p.need(isinstance(names,list) and names,'nonempty mechanical evidence required')
    for name in names:subjects[name]=p.sha(p.local(project,name))


def judgments(project,requirements,mechanical,report,subjects):
    """Judge completeness, not the truth of an independent engineer's conclusion."""
    rows=requirements['interfaces'];p.need(isinstance(rows,dict),'interface inventory required')
    p.need(set(mechanical['interfaces'])==set(rows),'mating interface review coverage differs')
    for name,row in rows.items():
        p.need(set(row)=={'board','references','requirement','evidence'} and
               isinstance(row['requirement'],str) and row['requirement'].strip(),'incomplete interface requirement')
        board=report['boards'].get(row['board'])
        refs=row['references']
        p.need(isinstance(refs,list) and refs and len(set(refs))==len(refs) and
               board and set(refs)<=set(board['references']),'interface absent from mounted scene')
        evidence(project,row['evidence'],subjects)
        checks=mechanical['interfaces'][name]
        p.need(isinstance(checks,dict) and set(checks)==CHECKS,'incomplete interface checks: '+name)
        for key,check in checks.items():
            p.need(set(check)=={'verdict','rationale','evidence'} and check['verdict']=='PASS' and
                   isinstance(check['rationale'],str) and check['rationale'].strip(),
                   'unresolved interface '+name+'/'+key)
            evidence(project,check['evidence'],subjects)
    limitations=limitation_inventory(report)
    p.need(set(mechanical['limitations'])==set(limitations),'scene/model limitation coverage differs')
    for key,check in mechanical['limitations'].items():
        p.need(set(check)=={'classification','rationale','evidence'} and check['classification'] in
               {'design_resolved','physical_qualification','outside_mating_scope'} and
               isinstance(check['rationale'],str) and check['rationale'].strip(),
               'unresolved scene/model limitation')
        evidence(project,check['evidence'],subjects)
    return limitations


def scene_evidence(project,mechanical,placement_review,subjects):
    """Reopen a frozen producer, without refreshing its old report/tool hashes."""
    required={'scene_manifest','scene_output','toolchain','toolchain_files','interfaces','limitations'}
    p.need(isinstance(mechanical,dict) and set(mechanical)==required,'registered mechanical evidence required')
    name=mechanical['scene_output']+'/scene.json';report=p.read(p.local(project,name))
    p.need(report.get('version')==1 and report.get('accepted') is False and
           report.get('status')=='INCOMPLETE','scene has nominal faults or unsupported status')
    p.need(report['manifest']==mechanical['scene_manifest'],'scene manifest binding differs')
    evidence(project,[name,mechanical['scene_manifest']],subjects)
    for name,digest in report['inputs'].items():
        p.need(p.sha(p.local(project,name))==digest,'stale scene input: '+name);subjects[name]=digest
    for name,digest in report['files'].items():
        path=mechanical['scene_output']+'/'+name
        p.need(p.sha(p.local(project,path))==digest,'stale scene artifact: '+name);subjects[path]=digest
    archive=p.local(project,mechanical['toolchain']+'/tools/mechanical_scene.py').parents[1]
    observed=inventory(archive)
    p.need(observed==mechanical['toolchain_files'],'scene producer archive changed')
    for name,digest in report['tools'].items():
        p.need(observed.get('tools/'+name)==digest,'archived producer differs from scene')
    for name,digest in observed.items():subjects[mechanical['toolchain']+'/'+name]=digest
    manifest=p.read(p.local(project,mechanical['scene_manifest']))
    assembly=p.read(p.local(project,manifest['assembly_manifest']))
    bundle=p.read(p.local(project,assembly['package']+'/native/bundle.json'))
    plan=p.read(p.local(project,placement_review['plan']))
    p.need(set(report['boards'])==set(bundle['boards'])==set(plan['boards']), 'scene/placement board coverage differs')
    for key,board in report['boards'].items():
        p.need(board['mounted_references']>0 and not board['contact_failures'] and
               board['clearance']['verdict']=='PASS' and not board['clearance']['failures'] and
               all(a['verdict']=='PASS' for a in board['access']),'nominal mechanical failures: '+key)
        native=assembly['package']+'/native/'+bundle['boards'][key]['native']
        placed=placement_review['output']+'/'+key+'.kicad_pcb'
        p.need(geometry(p.local(project,native))==geometry(p.local(project,placed)),
               'scene no longer matches accepted placement: '+key)
        evidence(project,[native,placed],subjects)
    return report,archive


def verify(project,requirements_name,review,placement_review,subjects):
    subjects=dict(subjects)
    requirements=p.read(p.local(project,requirements_name))
    p.need(set(requirements)=={'version','interfaces','scope_evidence'} and requirements['version']==1,
           'unsupported mating requirements')
    p.need(isinstance(requirements['scope_evidence'],list) and requirements['scope_evidence'],
           'mating scope authority required')
    evidence(project,[requirements_name,*requirements['scope_evidence']],subjects)
    mechanical=review.get('mechanical')
    report,archive=scene_evidence(project,mechanical,placement_review,subjects)
    p.need(bool(requirements['interfaces'])==(review['applicability']=='applicable'),
           'mating applicability contradicts contracted interface inventory')
    limitations=judgments(project,requirements,mechanical,report,subjects)
    # Use the mechanical runtime to call routing.py for the upgraded route.
    # No supplied arbitrary command or report-only success can replace replay.
    runtime=p.ROOT/'.venv-mechanical/bin/python'
    if not runtime.is_file():runtime=Path(sys.executable)
    command=[str(runtime),'-B',str(archive/'tools/mechanical_scene.py'),'verify',
             '--project',str(project),'--manifest',mechanical['scene_manifest'],
             '--output',str(p.local(project,mechanical['scene_output']+'/scene.json').parent)]
    try:run=subprocess.run(command,capture_output=True,text=True,timeout=600)
    except subprocess.TimeoutExpired as exc:raise ValueError('frozen scene replay timed out') from exc
    p.need(run.returncode==0,'frozen scene replay failed: '+(run.stderr+run.stdout)[-1800:])
    p.need(all(p.sha(p.local(project,name))==digest for name,digest in subjects.items()),
           'mechanical subjects changed during verification')
    return dict(subjects=subjects,interfaces=sorted(requirements['interfaces']),
                limitations=limitations,scope='design-stage mating only; physical qualification not performed',
                replay_command=['python[mechanical-runtime]','-B',mechanical['toolchain']+'/tools/mechanical_scene.py',
                    'verify','--project','PROJECT','--manifest',mechanical['scene_manifest'],
                    '--output',mechanical['scene_output']],
                replay_exit_code=run.returncode,tool_sha256=p.sha(Path(__file__)))
