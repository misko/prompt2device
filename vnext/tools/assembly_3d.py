"""Registered scene integration for assembly; judgments stay independent."""
from pathlib import Path
import subprocess
import sys

import mating_admission as mechanical

p=mechanical.p
GUIDANCE='skills/pcb-design/procedures/mechanical/3d-verification.md'
VIEWS={'top','bottom','iso_nw','iso_se','edge_west','edge_east'}
BINDING={'scene_manifest','scene_output','toolchain','toolchain_files'}


def scene(project, binding, manifest_name, spec, envelope_report, subjects):
    """Reopen exact accepted-package scene and replay its retained producer."""
    p.need(isinstance(binding,dict) and set(binding)==BINDING,'explicit assembly scene binding required')
    subjects=dict(subjects)
    name=binding['scene_manifest']; output=binding['scene_output']
    source=p.read(p.local(project,name)); report=p.read(p.local(project,output+'/scene.json'))
    p.need(source['assembly_manifest']==manifest_name,'scene uses a different assembly manifest')
    p.need(report.get('version')==1 and report.get('accepted') is False and
           report.get('status')=='INCOMPLETE' and report.get('manifest')==name,
           'unsupported or failing assembly scene')
    mechanical.evidence(project,[name,output+'/scene.json'],subjects)
    p.need(set(report['models'])==set(spec['models']),'scene model census differs')
    p.need(set(report['boards'])==set(spec['boards'])==set(envelope_report['boards']),
           'scene board census differs')
    for name,digest in report['inputs'].items():
        p.need(p.sha(p.local(project,name))==digest,'stale assembly scene input: '+name)
        subjects[name]=digest
    # These entries may not be silently omitted from a rewritten report.
    core={manifest_name,binding['scene_manifest'],spec['package']+'/native/bundle.json',
          spec['package']+'/fabrication.json',spec['package']+'/assembly/population.csv'}
    p.need(core<=set(report['inputs']),'scene omits assembly/package inputs')
    files=mechanical.inventory(p.local(project,output+'/scene.json').parent)
    p.need(files==dict(report['files'],**{'scene.json':p.sha(p.local(project,output+'/scene.json'))}),
           'assembly scene artifact census/hash differs')
    for name,digest in report['files'].items():subjects[output+'/'+name]=digest
    archive=p.local(project,binding['toolchain']+'/tools/mechanical_scene.py').parents[1]
    observed=mechanical.inventory(archive)
    p.need(observed==binding['toolchain_files'],'assembly frozen producer inventory differs')
    for name,digest in report['tools'].items():
        p.need(Path(name).name==name and observed.get('tools/'+name)==digest,
               'assembly scene producer differs')
    p.need({'mechanical_scene.py','mechanical_kernel.py','assembly_verify.py'}<=set(report['tools']),
           'assembly scene omits producer identities')
    for name,digest in observed.items():subjects[binding['toolchain']+'/'+name]=digest
    bundle=p.read(p.local(project,spec['package']+'/native/bundle.json'))
    coverage={}
    for key,board in report['boards'].items():
        expected=envelope_report['boards'][key]['references']
        p.need(board['references']==expected and board['mounted_references']==len(expected)>0,
               'scene mounted reference/registration census differs: '+key)
        native=spec['package']+'/native/'+bundle['boards'][key]['native']
        p.need(report['inputs'].get(native)==spec['boards'][key]['source_sha256']==p.sha(p.local(project,native)),
               'scene native differs from accepted package: '+key)
        p.need(not board['contact_failures'] and board['clearance']['verdict']=='PASS' and
               not board['clearance']['failures'] and all(a['verdict']=='PASS' for a in board['access']),
               'assembly scene contact/clearance/access failures: '+key)
        p.need(board['step_roundtrip']['verdict']=='PASS' and
               set(board['step_roundtrip']['parts'])==set(expected)|{'board'} and
               all(r['verdict']=='PASS' and r['solids_after']>0 for r in board['step_roundtrip']['parts'].values()),
               'assembly STEP roundtrip/population differs: '+key)
        p.need(board['board_datum']['bare_step_roundtrip']['verdict']=='PASS',
               'assembly bare STEP roundtrip failed')
        p.need(set(board['frames'])==VIEWS,'assembly six-view camera coverage differs')
        required={key+'/'+key+'-populated.step',key+'/board.step',key+'/native-dielectric.step'}
        required|={key+'/twin_'+view+'.png' for view in VIEWS}
        required|={key+'/render_'+view+'_bare.png' for view in ('top','bottom')}
        required|={key+'/'+n for n in board['details']}
        p.need(required<=set(report['files']),'assembly STEP/view artifacts missing: '+key)
        coverage[key]={ref:row['model'] for ref,row in expected.items()}
    runtime=p.ROOT/'.venv-mechanical/bin/python'
    if not runtime.is_file():runtime=Path(sys.executable)
    command=[str(runtime),'-B',str(archive/'tools/mechanical_scene.py'),'verify',
             '--project',str(project),'--manifest',binding['scene_manifest'],
             '--output',str(p.local(project,output+'/scene.json').parent)]
    try:run=subprocess.run(command,capture_output=True,text=True,timeout=600)
    except subprocess.TimeoutExpired as exc:raise ValueError('assembly scene replay timed out') from exc
    p.need(run.returncode==0,'assembly frozen scene replay failed: '+(run.stderr+run.stdout)[-1800:])
    p.need(all(p.sha(p.local(project,n))==d for n,d in subjects.items()),
           'assembly mechanical subjects changed during replay')
    return dict(version=1,scene_manifest=binding['scene_manifest'],scene_output=output,
                coverage=coverage,limitations=mechanical.limitation_inventory(report),
                subjects=subjects,replay_exit_code=0,
                replay_command=['python[mechanical-runtime]','-B',binding['toolchain']+'/tools/mechanical_scene.py',
                                'verify','--project','PROJECT','--manifest',binding['scene_manifest'],'--output',output],
                scope='Registered assembly evidence; independent acceptance and physical qualification are separate',
                accepted=False)


def judgments(project, review, result, spec, subjects):
    """Complete scoped dispositions, never exporter-generated engineering PASS."""
    p.need(isinstance(review,dict) and set(review)=={'models','boards','limitations'},
           'independent registered assembly judgments required')
    def check(row, required=()):
        p.need(isinstance(row,dict) and set(row)=={'verdict','rationale','evidence'} and
               row['verdict']=='PASS' and isinstance(row['rationale'],str) and row['rationale'].strip(),
               'unresolved registered assembly judgment')
        mechanical.evidence(project,row['evidence'],subjects)
        p.need(set(required)<=set(row['evidence']),'registered assembly judgment omits required evidence')
    p.need(set(review['models'])==set(spec['models']),'registered model review coverage differs')
    p.need(set(review['boards'])==set(spec['boards']),'registered board review coverage differs')
    scene_spec=p.read(p.local(project,result['scene_manifest']))
    for key,row in review['models'].items():
        required=set(spec['models'][key]['evidence'])
        if key in scene_spec['step_models']:
            model=scene_spec['step_models'][key];required|={model['path'],*model['evidence']}
        check(row,required)
    scene_report=p.read(p.local(project,result['scene_output']+'/scene.json'))
    for key,row in review['boards'].items():
        required={result['scene_output']+'/'+n for n in scene_report['files'] if n.startswith(key+'/')}
        required.add(result['scene_output']+'/scene.json')
        check(row,required)
    p.need(set(review['limitations'])==set(result['limitations']),'assembly limitation review coverage differs')
    for row in review['limitations'].values():
        p.need(set(row)=={'classification','rationale','evidence'} and row['classification'] in
               {'design_resolved','physical_qualification'} and isinstance(row['rationale'],str) and row['rationale'].strip(),
               'unresolved assembly limitation; mating-only exclusions are not assembly acceptance')
        mechanical.evidence(project,row['evidence'],subjects)
