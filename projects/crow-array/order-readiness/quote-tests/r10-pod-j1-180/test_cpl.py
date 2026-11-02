"""Build/verify a single-field quote experiment; never edits the r10 package."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = HERE.parents[1]
SOURCE = ORDER/'quote-draft/r10-2c8p-outward-power/pod-cpl.csv'
EXPECTED_SOURCE = '6d1884eae3369d239da8d7f6214e27d8296df49d61daed141d9a126b4b2df9ae'
BASELINE = 'pod-cpl-J1-000-BASELINE.csv'
TRIAL = 'pod-cpl-J1-180-TEST-ONLY.csv'
HEADER = ['Designator','Mid X','Mid Y','Rotation','Layer']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rows(data):
    reader = csv.DictReader(io.StringIO(data.decode('utf-8')))
    if reader.fieldnames != HEADER:
        raise ValueError('Unexpected CSV columns')
    result = list(reader)
    if len(result) != 29 or len({r['Designator'] for r in result}) != 29:
        raise ValueError('Expected 29 unique references')
    if any(set(r) != set(HEADER) or any(v is None for v in r.values()) for r in result):
        raise ValueError('Malformed CSV row')
    return result


def make_trial(data):
    original = rows(data)
    target = next((r for r in original if r['Designator']=='J1'), None)
    if target != dict(zip(HEADER,['J1','10.556000mm','-8.373000mm','0.000000','Top'])):
        raise ValueError('Unexpected baseline J1 pose')
    old = b'J1,10.556000mm,-8.373000mm,0.000000,Top'
    new = b'J1,10.556000mm,-8.373000mm,180.000000,Top'
    lines = data.splitlines(keepends=True)
    matched = [i for i,line in enumerate(lines) if line.rstrip(b'\r\n') == old]
    if len(matched) != 1:
        raise ValueError('Expected one exact baseline J1 row')
    i = matched[0]
    lines[i] = new + lines[i][len(old):]
    return b''.join(lines)


def compare(base, trial):
    a,b = rows(base),rows(trial)
    differences = [(x['Designator'],key,x[key],y[key])
                   for x,y in zip(a,b) for key in HEADER if x[key] != y[key]]
    if differences != [('J1','Rotation','0.000000','180.000000')]:
        raise ValueError('Trial changes more than the one authorized field')
    if trial != make_trial(base):
        raise ValueError('Unexpected byte changes outside J1 rotation')
    return differences


def expected():
    source = SOURCE.read_bytes()
    if sha(source) != EXPECTED_SOURCE:
        raise ValueError('Original r10 CPL changed')
    trial = make_trial(source)
    differences = compare(source,trial)
    native = ORDER/'quote-draft/r10-2c8p-outward-power/native/pcb/pod/pod.kicad_pcb'
    native_sha = 'd67134d2361f32f25a1f8841134f21f84791d3d36ede1acb74b383d5b007ceb9'
    if sha(native.read_bytes()) != native_sha:
        raise ValueError('Original pod board changed')
    record = {
        'status':'QUOTE_ONLY_UNACCEPTED_ROTATION_EXPERIMENT',
        'source':str(SOURCE.relative_to(ORDER)), 'source_sha256':EXPECTED_SOURCE,
        'pod_native_sha256':native_sha, 'references':29,
        'changes':[dict(zip(['reference','field','before','after'],d)) for d in differences],
        'files':{BASELINE:sha(source),TRIAL:sha(trial)},
        'generator_sha256':sha(Path(__file__).read_bytes()),
        'jlc_upload_performed':False, 'alignment_verified':False, 'production_ready':False}
    return {BASELINE:source,TRIAL:trial,
            'manifest.json':(json.dumps(record,indent=2)+'\n').encode()}


def run(build=False):
    payload = expected()
    if build:
        # Refuse to overwrite unrelated or changed artifacts before writing anything.
        for name,data in payload.items():
            if (HERE/name).exists() and (HERE/name).read_bytes()!=data:
                raise ValueError('Refusing changed existing output: '+name)
        for name,data in payload.items():
            if not (HERE/name).exists():
                (HERE/name).write_bytes(data)
    for name,data in payload.items():
        if (HERE/name).read_bytes()!=data:
            raise ValueError('Verification mismatch: '+name)
    compare((HERE/BASELINE).read_bytes(),(HERE/TRIAL).read_bytes())
    return {'result':'PASS_SINGLE_FIELD_TEST_INTEGRITY','references':29,
            'only_change':'J1 Rotation 0.000000 -> 180.000000',
            'native_and_r10_unchanged':True,'production_ready':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['build','verify'])
    args=p.parse_args()
    print(json.dumps(run(args.command=='build'),indent=2))
