"""Read-only complete rules snapshots, not engineering verdicts. Requires PyYAML."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys
import yaml

class SnapshotError(ValueError): pass

class UniqueLoader(yaml.SafeLoader): pass
def unique_mapping(loader,node):
    result={}
    for key_node,value_node in node.value:
        key=loader.construct_object(key_node,deep=True)
        if key in result: raise SnapshotError(f'duplicate YAML key: {key}')
        result[key]=loader.construct_object(value_node,deep=True)
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,unique_mapping)

def safe_file(project,name):
    if not isinstance(name,str) or not name or '\\' in name or Path(name).is_absolute() or any(p in ('','.','..') for p in name.split('/')):
        raise SnapshotError(f'unsafe path: {name}')
    p=project/name
    if not p.is_file() or not p.resolve().is_relative_to(project.resolve()): raise SnapshotError(f'missing or escaping source: {name}')
    return p

def members(project):
    names=sorted(p.relative_to(project).as_posix() for p in (project/'03_src/rules').rglob('*') if p.is_file() and p.suffix.lower() in ('.json','.yaml','.yml'))
    if not names: raise SnapshotError('empty rules set')
    for n in names: safe_file(project,n)
    return names

def digest(project,name): return hashlib.sha256(safe_file(project,name).read_bytes()).hexdigest()

def read(project,name):
    try:
        def unique(pairs):
            obj={}
            for k,v in pairs:
                if k in obj: raise SnapshotError(f'duplicate key: {k}')
                obj[k]=v
            return obj
        text=safe_file(project,name).read_text()
        return json.loads(text,object_pairs_hook=unique) if text.lstrip().startswith(('{','[')) else yaml.load(text,Loader=UniqueLoader)
    except (ValueError,yaml.YAMLError) as exc: raise SnapshotError(f'invalid source {name}: {exc}') from exc

def objects(obj,seen=frozenset()):
    if not isinstance(obj,(dict,list)): return
    if id(obj) in seen: raise SnapshotError('recursive YAML object')
    seen=seen|{id(obj)}
    if isinstance(obj,dict): yield obj
    for v in (obj.values() if isinstance(obj,dict) else obj): yield from objects(v,seen)

def pointer(obj,path):
    if not isinstance(path,str) or (path and not path.startswith('/')) or re.search(r'~(?![01])',path): raise SnapshotError('invalid pointer')
    try:
        for token in path.split('/')[1:]:
            token=token.replace('~1','/').replace('~0','~')
            if isinstance(obj,list):
                if not token.isdigit() or (len(token)>1 and token[0]=='0'): raise KeyError(token)
                obj=obj[int(token)]
            else: obj=obj[token]
    except (KeyError,IndexError,TypeError,ValueError) as exc: raise SnapshotError(f'unresolved pointer: {path}') from exc
    return obj

def source_closure(project):
    """Rules plus transitive source references; file cycles are valid."""
    pending = list(members(project))
    parsed = {}
    names = set()
    while pending:
        name = pending.pop()
        if name in names:
            continue
        safe_file(project, name)
        names.add(name)
        # Binary and program sources are bound, not interpreted as YAML.
        if Path(name).suffix.lower() not in ('.json', '.yaml', '.yml'):
            continue
        parsed[name] = read(project, name)
        for ref in objects(parsed[name]):
            target = ref.get('path')
            if isinstance(target, str) and target.startswith('03_src/'):
                pending.append(target)
    return sorted(names), parsed

def collect(project):
    names, _ = source_closure(project)
    return {n:digest(project,n) for n in names}

def validate(project,subjects):
    if not isinstance(subjects,dict): raise SnapshotError('subjects must be a map')
    names, parsed=source_closure(project)
    if set(names)-subjects.keys(): raise SnapshotError('unbound source members')
    for n in subjects:
        if not isinstance(n,str): raise SnapshotError('invalid subject key')
        if (n in names or n.startswith('03_src/rules/')) and digest(project,n)!=subjects[n]: raise SnapshotError(f'stale source: {n}')
    for owner,doc in parsed.items():
        for ref in objects(doc):
            target=ref.get('path')
            if not isinstance(target,str) or not target.startswith('03_src/'): continue
            safe_file(project,target)
            if target not in subjects: raise SnapshotError(f'unbound reference: {target}')
            if digest(project,target)!=subjects[target]: raise SnapshotError(f'stale reference: {target}')
            if 'sha256' in ref: raise SnapshotError(f'embedded live-source hash: {owner} -> {target}')
            if 'pointer' in ref: pointer(parsed[target] if target in parsed else read(project,target),ref['pointer'])
    return names

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--project',required=True,type=Path)
    ap.add_argument('--check',type=Path,help='JSON review subjects or task inputs map');a=ap.parse_args()
    try:
        packet=json.loads(a.check.read_text()) if a.check else {'subjects':collect(a.project)}
        subjects=packet.get('subjects',packet.get('inputs',packet));names=validate(a.project,subjects)
        print(f'{len(names)} source members current; structural only' if a.check else json.dumps({'subjects':subjects},indent=2,sort_keys=True));return 0
    except (SnapshotError,OSError,ValueError,TypeError) as exc:
        print(f'snapshot refused: {exc}',file=sys.stderr);return 1
if __name__=='__main__': sys.exit(main())
