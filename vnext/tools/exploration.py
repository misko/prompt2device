"""Bounded draft exploration journal; NOT a scheduler or engineering verifier.

CLI: exploration.py init RUN BRIEF --budget 7200 --width 3 --rounds 2
     exploration.py event RUN EVENT.json
     exploration.py show RUN
     exploration.py subjects RUN   # verified compact review references, read-only

Events (coordinator-owned JSON):
 start: id, actor, seconds, kind=draft|repair|review|assist|diagnose; repair adds problem,parent
        assist adds parent (a live repair/recovery/work); bounded helper, not acceptance
        diagnose adds parent,problem,question at a reviewed checkpoint; read-only subjects
 bind: id, handle                  (actual external agent handle)
 finish: id, outcome=complete|partial|failed; candidate directory is snapshotted
         completed diagnose adds path to its evidence report (not acceptance)
 review: task, path                (JSON schema below, task is kind review)
 select: candidate, rationale      (selection for repair, never acceptance)
 reexplore: path                   (redesign JSON schema below)
 pause: reason; resume: user_authorized=true
        optional deadline,reason,path: new finite recovery window on fresh user
        direction; paused, settled/assessed only; retained authority evidence
 note: reason (coordinator decision; no promotion or budget reset)
 milestone-checkpoint: milestone, tasks, result=baseline|advanced|prerequisite|unchanged,
             reason, path (evidence); advanced adds closed,verifier,regressions=false
 reassess: action=continue|change|backtrack|escalate|pause,reason,hypothesis,check;
           after two no-progress checkpoints, non-pause recovery needs deadline
 progress-migration: milestone,tasks,prior_stalled>=2,reason,reviewer,path
 start kind=recovery: objective,writes; only an explicitly reassessed plateau;
                      does not reset candidate rounds, local repairs or selection
 start kind=work: objective,writes; ordinary bounded domain parent, no exploration
                  phase changes; parent duration may cover several worker segments
 allowance: budget_s, reason, authority (checkpoint reassessment; preserves spend)
            optional failed_review identifies terminal failed-dispatch recovery

Review JSON: reviewer, subjects:{candidate_id:snapshot_digest},
 (legacy full {relative_path:sha256} maps are also accepted),
 assessments:{candidate_id:{eligible:bool,rationale:str}},
 findings:[{id,kind:contradiction|uncertainty|qualification,statement,evidence,
 candidates:[candidate_id,...],blocking:bool}]. Evidence is explanatory text
 with exact file/pin/source references; truth/completeness is reviewer-owned.
Redesign JSON: brief_sha256, blockers:[finding_id,...], blocker_evidence:{id:review_evidence}, hypothesis,
 learned, unknowns, failed_attempts:[task_id,...], outcomes:{task_id:explanation}, freedom.
 One run.json is the execution journal. Artifacts/reviews are evidence, not state.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import time
import progress


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inside(root, relative):
    p = Path(relative)
    require(not p.is_absolute() and '..' not in p.parts, 'path must be local')
    resolved = (root/p).resolve()
    require(resolved.is_relative_to(root.resolve()), 'path escapes run')
    return resolved


def snapshot(root):
    files = {}
    for p in sorted(root.rglob('*')):
        require(not p.is_symlink(), 'candidate symlinks are not allowed')
        if p.is_file() and '__pycache__' not in p.parts:
            files[str(p.relative_to(root))] = digest(p)
    return files


def snapshot_digest(files):
    """SHA-256 of the complete path/hash map, sorted compact JSON (ASCII escaped)."""
    return hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':'),
                                     ensure_ascii=True).encode('utf-8')).hexdigest()


def subject_matches(reference, files):
    if isinstance(reference,dict):
        return reference==files
    return (isinstance(reference,str) and re.fullmatch('[0-9a-f]{64}',reference)
            is not None and reference==snapshot_digest(files))


def review_subjects(root):
    """Rehash frozen candidates; summarize identities, never engineering verdicts."""
    root=Path(root);s=json.loads((root/'run.json').read_text());fresh(root,s)
    candidates=current_candidates(s)
    require(candidates,'no review candidates')
    result={}
    for cid,t in candidates.items():
        require(t['status']=='finished' and 'snapshot' in t,'unfinished candidate')
        require(snapshot(root/'candidates'/cid)==t['snapshot'],'stale candidate')
        result[cid]=snapshot_digest(t['snapshot'])
    return result


def save(root, state):
    # Coordinator is the only writer; atomic replacement avoids torn checkpoints.
    temp = root/'run.json.tmp'
    temp.write_text(json.dumps(state, indent=2)+'\n')
    temp.replace(root/'run.json')


def initialize(root, brief, budget=7200, width=3, rounds=2, review_seconds=300):
    root, brief = Path(root), Path(brief)
    require(root.is_absolute() and not root.is_symlink(), 'absolute non-symlink run required')
    require(not root.exists() or not any(root.iterdir()), 'run must be absent or empty')
    require(type(budget) is int and budget>0 and type(width) is int and 1<=width<=3
            and type(rounds) is int and 1<=rounds<=3, 'invalid finite allowance')
    require(type(review_seconds) is int and 0<review_seconds<=1200
            and budget>=width+review_seconds, 'reserve a feasible first round and comparison')
    raw=brief.read_bytes(); require(raw.strip(), 'empty brief')
    root.mkdir(parents=True, exist_ok=True)
    (root/'BRIEF.md').write_bytes(raw)
    for name in ('candidates','reviews','lessons'):
        (root/name).mkdir()
    state=dict(version=1, brief_sha256=digest(root/'BRIEF.md'), budget_s=budget,
               charged_s=0, width=width, max_rounds=rounds, round=1,
               phase='drafts', paused=False, selected=None, review=None,
               round_draft_s=None, review_reserve_s=review_seconds,
               tasks={}, repairs={}, redesigns=[], events=[])
    save(root,state)
    return state


def fresh(root,s):
    require(digest(root/'BRIEF.md')==s['brief_sha256'], 'brief changed; explicit new requirements run needed')
    for event in s['events']:
        if event.get('op') in ('milestone-checkpoint','progress-migration'):
            require(digest(inside(root,event['path']))==event['evidence_sha256'],
                    'milestone evidence changed')
        elif event.get('op')=='resume' and 'deadline' in event:
            require(digest(inside(root,event['path']))==event['evidence_sha256'],
                    'user resume authority evidence changed')
    if s['redesigns']:
        r=s['redesigns'][-1]
        require(digest(inside(root,r['path']))==r['sha256'], 'redesign pointers changed')


def reviewed(root,s):
    r=s['review']; require(r is not None, 'current independent review required')
    p=inside(root,r['path']);require(digest(p)==r['sha256'],'review changed')
    d=json.loads(p.read_text())
    for cid, reference in d['subjects'].items():
        require(subject_matches(reference,snapshot(root/'candidates'/cid)), f'stale review: {cid}')
    return d


def current_candidates(s):
    return {k:v for k,v in s['tasks'].items()
            if v['round']==s['round'] and v['kind'] in ('draft','repair')}


def apply(root,event,now=None):
    root=Path(root);s=json.loads((root/'run.json').read_text());s=copy.deepcopy(s)
    now=time.time() if now is None else now
    # Compatibility for this pilot's initial journal, before reservation fields.
    s.setdefault('review_reserve_s',300)
    s.setdefault('round_draft_s',next((t['seconds'] for t in s['tasks'].values()
                                    if t['kind']=='draft' and t['round']==s['round']),None))
    fresh(root,s)
    op=event['op']
    require(not s['paused'] or op in ('finish','resume'), 'run paused')
    active=[k for k,v in s['tasks'].items() if v['status']=='running']
    if op=='start':
        cid=event['id'];kind=event['kind'];seconds=event['seconds'];actor=event['actor']
        require(isinstance(cid,str) and re.fullmatch('[a-zA-Z0-9_-]+',cid) and cid not in s['tasks'], 'unique safe task id required')
        require(kind in ('draft','repair','review','assist','diagnose','recovery','work') and actor, 'invalid task/actor')
        require(type(seconds) is int and seconds>0 and (kind in ('recovery','work') or seconds<=1200),
                'ordinary segment must be 1..1200 seconds; parents must fit available budget and deadline')
        milestone=progress.before_dispatch(s['events'],s['tasks'],now,seconds,
                                           kind=kind,parent=event.get('parent'))
        work_parents=[cid for cid in active if s['tasks'][cid]['kind']=='work']
        require(not work_parents or kind=='assist' and event.get('parent') in work_parents,
                'live work parent permits only its bounded helpers')
        require(s['charged_s']+seconds<=s['budget_s'],'total run budget exhausted')
        if kind in ('recovery','work'):
            if kind=='recovery':
                require(not active and milestone['stalled']>=2
                        and milestone['decision']['action'] in ('change','backtrack','escalate'),
                        'recovery requires an explicit plateau decision')
            else:require(not active,'work requires settled prior tasks')
            require(event.get('objective') and isinstance(event.get('writes'),list) and event['writes'],
                    'parent needs objective and bounded writes')
            for name in event['writes']:inside(root,name)
        elif kind=='draft':
            require(s['phase']=='drafts','not in draft exploration')
            require(len(current_candidates(s))<s['width'],'candidate width exhausted')
            require(all(t['actor']!=actor for t in current_candidates(s).values()),'distinct independent draft actors required')
            require(s['round_draft_s'] in (None,seconds),'independent drafts need equal round allowances')
            slots=s['width']-len(current_candidates(s))
            require(s['charged_s']+slots*seconds+s['review_reserve_s']<=s['budget_s'],
                    'reserve remaining fanout and independent comparison before dispatch')
            s['round_draft_s']=seconds
        elif kind=='repair':
            d=reviewed(root,s);problem=event['problem'];parent=event['parent']
            require(not active and s['phase']=='selected' and parent==s['selected'],'repair selected baseline only')
            require(problem in {f['id'] for f in d['findings'] if parent in f['candidates'] and f['blocking']},'repair needs current blocker')
            require(s['repairs'].get(problem,0)<2,'local repair ceiling reached; re-explore or escalate')
            require(s['charged_s']+seconds+s['review_reserve_s']<=s['budget_s'],'reserve repair review')
            s['repairs'][problem]=s['repairs'].get(problem,0)+1
            s['phase']='repair';s['review']=None
        elif kind=='diagnose':
            require(not active and s['phase'] in ('compared','selected'),'diagnosis needs settled review')
            d=reviewed(root,s);parent=event['parent'];problem=event['problem']
            require(parent in d['subjects'] and event.get('question'),'diagnosis needs subject and question')
            require(any(f['id']==problem and parent in f['candidates'] and f['blocking']
                        for f in d['findings']),'diagnosis needs current blocker')
            require(not any(t['kind']=='diagnose' and t['parent']==parent and t['problem']==problem
                            for t in s['tasks'].values()),'diagnosis already attempted on this subject/problem')
        elif kind=='assist':
            parent=event['parent']
            require(parent in s['tasks'] and s['tasks'][parent]['kind'] in ('repair','recovery','work')
                    and s['tasks'][parent]['status']=='running','assist requires a live repair, recovery or work parent')
            require(now+seconds<=s['tasks'][parent]['deadline'],'assist must fit parent deadline')
            require(s['charged_s']+seconds+s['review_reserve_s']<=s['budget_s'],'reserve independent review')
        else:
            require(not active and s['phase'] in ('drafts','repair','review','compared','selected'),'not ready for comparison')
            if s['phase'] in ('compared','selected'):
                require(event.get('reason'),'reopened review needs new evidence reason')
                reviewed(root,s)
            cs=current_candidates(s)
            require(cs and all(t['status']=='finished' for t in cs.values()),'unfinished candidates')
            require(sum(t['kind']=='draft' for t in cs.values())==s['width'],'initial fanout not complete')
            subjects_key=hashlib.sha256(json.dumps({k:t['snapshot'] for k,t in cs.items()},sort_keys=True).encode()).hexdigest()
            require(sum(t.get('subjects_key')==subjects_key and not (
                        t['status']=='finished' and t.get('outcome')=='failed' and not t.get('handle'))
                        for t in s['tasks'].values())<2,
                    'comparison attempt ceiling reached; coordinator escalation required')
            s['phase']='review'
        s['charged_s']+=seconds
        s['tasks'][cid]=dict(kind=kind,actor=actor,round=s['round'],seconds=seconds,
                            started=now,deadline=now+seconds,status='running',handle=None)
        if kind=='repair':s['tasks'][cid].update(problem=problem,parent=parent)
        if kind in ('recovery','work'):s['tasks'][cid].update(objective=event['objective'],writes=event['writes'])
        if kind=='assist':s['tasks'][cid]['parent']=parent
        if kind=='diagnose':s['tasks'][cid].update(parent=parent,problem=problem,
                                                question=event['question'],source_review=copy.deepcopy(s['review']))
        if kind=='review':s['tasks'][cid]['subjects_key']=subjects_key
        if kind in ('draft','repair'):(root/'candidates'/cid).mkdir()
    elif op=='bind':
        t=s['tasks'][event['id']];require(t['status']=='running' and event['handle'],'live handle required')
        t['handle']=event['handle']
    elif op=='finish':
        t=s['tasks'][event['id']];require(t['status']=='running','task already terminal')
        require(not any(c['status']=='running' and c.get('parent')==event['id']
                        for c in s['tasks'].values()),'finish child work before freezing parent')
        require(event['outcome'] in ('complete','partial','failed'),'invalid outcome')
        if t['kind']=='diagnose':
            # A diagnosis cannot silently rewrite its circuit subjects or promote them.
            require(s['review']==t['source_review'],'diagnosis review changed')
            reviewed(root,s)
            if event.get('path'):
                p=inside(root,event['path']);require(p.is_file() and p.stat().st_size,'empty diagnosis report')
                t['evidence']=dict(path=event['path'],sha256=digest(p))
            require(event['outcome']!='complete' or 'evidence' in t,'completed diagnosis needs evidence')
        t.update(status='finished',outcome=event['outcome'],finished=now,
                 elapsed_s=max(0,now-t['started']),overrun_s=max(0,now-t['deadline']))
        s['charged_s']+=t['overrun_s'] # never hide elapsed overrun or refund unused reservation
        if t['kind'] in ('draft','repair'):
            directory=root/'candidates'/event['id']
            t['snapshot']=snapshot(directory) if any(directory.iterdir()) else {}
    elif op=='review':
        require(s['phase']=='review' and not active,'review worker must return first')
        task=s['tasks'][event['task']]
        require(task['kind']=='review' and task['round']==s['round']
                and task['status']=='finished' and task['outcome']=='complete','review worker did not complete')
        p=inside(root,event['path']);d=json.loads(p.read_text());cs=current_candidates(s)
        require(d['reviewer']==task['actor'] and all(d['reviewer']!=c['actor'] for c in cs.values()),'review must be independent')
        require(set(d['subjects'])==set(cs)==set(d['assessments']),'comparison must cover all current candidates')
        for cid,c in cs.items():
            require(c['snapshot']==snapshot(root/'candidates'/cid)
                    and subject_matches(d['subjects'][cid],c['snapshot']),'stale candidate')
            a=d['assessments'][cid];require(type(a['eligible']) is bool and a['rationale'],'invalid assessment')
            require(c['snapshot'] or not a['eligible'],'empty candidate cannot be selected')
        seen=set()
        for f in d['findings']:
            require(f['id'] not in seen and f['id'] and f['kind'] in ('contradiction','uncertainty','qualification')
                    and f['statement'] and f['evidence'] and type(f['blocking']) is bool
                    and f['candidates'] and set(f['candidates'])<=set(cs),'invalid finding')
            seen.add(f['id'])
        s['review']=dict(path=event['path'],sha256=digest(p));s['phase']='compared'
    elif op=='select':
        d=reviewed(root,s);cid=event['candidate']
        require(not active and s['phase']=='compared' and d['assessments'][cid]['eligible'] and event['rationale'],'candidate not eligible')
        s['selected']=cid;s['phase']='selected'
    elif op=='reexplore':
        d=reviewed(root,s)
        require(not active and s['phase'] in ('selected','compared') and s['round']<s['max_rounds'],'no further exploration round')
        require(s['charged_s']<s['budget_s'],'no remaining budget')
        draft_s=event.get('draft_seconds',s['round_draft_s'])
        require(type(draft_s) is int and 0<draft_s<=1200
                and s['charged_s']+s['width']*draft_s+s['review_reserve_s']<=s['budget_s'],
                'reserve complete new round and comparison within remaining budget')
        p=inside(root,event['path']);lesson=json.loads(p.read_text())
        blockers={f['id'] for f in d['findings'] if f['blocking']}
        require(lesson['brief_sha256']==s['brief_sha256'] and lesson['blockers']
                and set(lesson['blockers'])<=blockers,'redesign must retain brief and cite reviewed blockers')
        expected={f['id']:f['evidence'] for f in d['findings'] if f['id'] in lesson['blockers']}
        require(lesson.get('blocker_evidence')==expected,'redesign must carry exact reviewed blocker evidence')
        require(all(lesson.get(k) for k in ('hypothesis','learned','unknowns','freedom')),'missing discriminating redesign pointers')
        require(isinstance(lesson['failed_attempts'],list) and set(lesson['failed_attempts'])<=set(s['tasks']),'invented attempt')
        owed={k for k,t in s['tasks'].items() if t['kind']=='repair' and t['problem'] in lesson['blockers']}
        require(owed<=set(lesson['failed_attempts']),'redesign omitted prior repairs on same blocker')
        require(set(lesson.get('outcomes',{}))==set(lesson['failed_attempts'])
                and all(lesson['outcomes'].values()),'redesign needs attempted-remedy outcomes')
        s['redesigns'].append(dict(path=event['path'],sha256=digest(p),from_round=s['round'],source_review=s['review']))
        s['round']+=1;s['phase']='drafts';s['selected']=None;s['review']=None;s['round_draft_s']=draft_s
    elif op in ('milestone-checkpoint','progress-migration'):
        if op=='milestone-checkpoint':progress.checkpoint(s['events'],s['tasks'],event)
        else:progress.migrate(s['events'],s['tasks'],event)
        p=inside(root,event['path']);require(p.is_file() and p.stat().st_size,'progress evidence required')
        event=dict(event,evidence_sha256=digest(p))
    elif op=='reassess':
        progress.reassess(s['events'],s['tasks'],event,now)
        if event['action']=='pause':s['paused']=True
    elif op=='pause':
        require(event.get('reason'),'pause reason required');s['paused']=True
    elif op=='note':
        require(event.get('reason'),'decision reason required')
    elif op=='allowance':
        # Explicit checkpoint decision, never automatic replenishment on retry.
        if event.get('failed_review'):
            task=s['tasks'].get(event['failed_review'],{})
            require(not active and s['phase']=='review' and s['review'] is None
                    and task.get('kind')=='review' and task.get('status')=='finished'
                    and task.get('outcome')=='failed',
                    'recovery allowance requires a terminal failed review without adoption')
            cs=current_candidates(s)
            subjects_key=hashlib.sha256(json.dumps({k:t['snapshot'] for k,t in cs.items()},sort_keys=True).encode()).hexdigest()
            require(task.get('subjects_key')==subjects_key,'failed review has stale subjects')
            require(not any(t.get('subjects_key')==subjects_key and t.get('outcome')=='complete'
                            for t in s['tasks'].values()),'completed comparison requires ordinary checkpoint adoption')
            require(not any(x.get('op')=='allowance' and x.get('failed_review')==event['failed_review']
                            for x in s['events']),'failed review recovery allowance already used')
        else:
            require(not active and s['phase'] in ('compared','selected'),
                    'allowance requires a settled independently reviewed checkpoint')
            reviewed(root,s)
        require(event.get('reason') and event.get('authority'),
                'allowance needs reassessment and authority')
        limit=event.get('budget_s')
        require(type(limit) is int and limit>s['budget_s'] and limit>s['charged_s'],
                'allowance must state a larger finite total')
        event=dict(event,previous_budget_s=s['budget_s'])
        s['budget_s']=limit
    elif op=='resume':
        require(s['paused'] and event.get('user_authorized') is True,'explicit user resume required')
        if 'deadline' in event:
            progress.resume_window(s['events'],s['tasks'],event,now)
            require(isinstance(event.get('path'),str) and event['path'],
                    'new recovery window needs retained user authority evidence')
            p=inside(root,event['path']);require(p.is_file() and p.stat().st_size,'user authority evidence required')
            evidence_sha256=digest(p)
            require(not any(previous.get('op')=='resume' and 'deadline' in previous
                            and previous['evidence_sha256']==evidence_sha256 for previous in s['events']),
                    'user authority evidence already used for a recovery window')
            event=dict(event,evidence_sha256=evidence_sha256)
        s['paused']=False
    else:
        raise ValueError('unsupported event; this adapter cannot accept a schematic')
    s['events'].append(dict(time=now,**event));save(root,s)
    return s


def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('init');a.add_argument('run',type=Path);a.add_argument('brief',type=Path)
    a.add_argument('--budget',type=int,default=7200);a.add_argument('--width',type=int,default=3);a.add_argument('--rounds',type=int,default=2)
    a.add_argument('--review-seconds',type=int,default=300)
    a=sub.add_parser('event');a.add_argument('run',type=Path);a.add_argument('event',type=Path)
    a=sub.add_parser('show');a.add_argument('run',type=Path)
    a=sub.add_parser('subjects');a.add_argument('run',type=Path)
    a=p.parse_args()
    if a.cmd=='init':s=initialize(a.run,a.brief,a.budget,a.width,a.rounds,a.review_seconds)
    elif a.cmd=='event':s=apply(a.run,json.loads(a.event.read_text()))
    elif a.cmd=='subjects':s=review_subjects(a.run)
    else:s=json.loads((a.run/'run.json').read_text())
    print(json.dumps(s,indent=2))


if __name__=='__main__':main()
