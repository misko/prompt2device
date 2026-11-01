"""Bounded r6 -> r7 quote derivative. No browser, ordering or release approval."""
import argparse
import json
from pathlib import Path
import re
import shutil
import tempfile
import substitute_quote as q
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'quote-draft/r6-2c8p-substitutions'
OUT = ROOT / 'quote-draft/r7-2c8p-stocked-power'
REVIEW = ROOT / 'substitutions-20261101/r7-review.json'
OLD_FP = 'Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT'
NEW_FP = 'Converter_DCDC:Converter_DCDC_TRACO_TSR1_RetainedLands'
CHANGES = [
    dict(old_mpn='1206L010/30WR', old_manufacturer='Littelfuse',
         mpn='1206L010/30NR', manufacturer='LUTE', code='C7542926',
         refs={'carrier': [f'F{i}' for i in range(101,109)], 'pod':['F1']},
         values={'1206L010/30WR':'1206L010/30NR'}),
    dict(old_mpn='R-78E5.0-0.5', old_manufacturer='RECOM Power',
         mpn='TSR 1-2450', manufacturer='TRACO POWER', code='C6886877',
         refs={'carrier':['U10']}, values={'R-78E5.0-0.5':'TSR 1-2450'})]


def spans(text):
    stack, result = [], []
    for token in q.TOKENS.finditer(text):
        if token.group() == '(':
            stack.append(token.start())
        elif token.group() == ')':
            result.append((stack.pop(),token.end()))
    q.need(not stack, 'Unbalanced source')
    return result


def mechanical(text):
    """Only U10's non-fabricated graphics/model and footprint identity change."""
    found = []
    for a,b in spans(text):
        s=text[a:b]
        if re.match(r'\(footprint\s',s) and '(property "Reference" "U10"' in s:
            found.append((a,b,s))
    q.need(len(found)==1,'Expected one U10 footprint')
    a,b,s=found[0]
    edits=[]
    for c,d in spans(s):
        item=s[c:d]
        if (re.match(r'\(fp_(line|rect|poly|text)\s',item) and
                any(f'(layer "{l}")' in item for l in ('F.Fab','F.CrtYd'))) or item.startswith('(model '):
            edits.append((c,d))
    for c,d in sorted(edits,reverse=True): s=s[:c]+s[d:]
    s=s.replace('Converter_DCDC_RECOM_R-78E-0.5_THT', 'Converter_DCDC_TRACO_TSR1_RetainedLands')
    s=re.sub(r'\(descr "[^"\n]*"\)', '(descr "TRACO TSR 1-2450; reviewed retained SIP3 copper; no qualified 3D model")', s)
    s=re.sub(r'\(tags "[^"\n]*"\)', '(tags "TRACO SIP3 retained lands")', s)
    extra='''
    (fp_rect (start -3.32 -5.5) (end 8.38 2)
      (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))
    (fp_rect (start -4.05 -6.25) (end 9.1 2.75)
      (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))
'''
    s=s[:-1]+extra+')'
    return text[:a]+s+text[b:]


def native(text,board,physical=False):
    result,seen=q.rewrite(text,board,CHANGES)
    result=result.replace(OLD_FP,NEW_FP) if board=='carrier' else result
    if physical and board=='carrier': result=mechanical(result)
    return result,seen


def base_check():
    spec=spec_from_file_location('r6_verify',ROOT/'substitutions-20261101/verify_public.py')
    module=module_from_spec(spec);spec.loader.exec_module(module)
    module.verify(BASE)
    review=json.loads(REVIEW.read_text())
    q.need(review['decision']=='PASS_FOR_QUOTE_REVISION', 'Engineering review missing')
    q.need(not review['production_ready'], 'Cannot promote production')
    q.need(review['cts_unchanged'], 'Clock change outside scope')
    for relative,digest in review['bound_inputs'].items():
        q.need(q.sha(ROOT/relative)==digest, 'Changed qualification input: '+relative)


def build(output):
    base_check()
    q.need(not output.exists(),'Refusing existing output')
    shutil.copytree(BASE,output)
    for board in ('carrier','pod'):
        for relative,physical in [(f'native/pcb/{board}/{board}.kicad_pcb',True),
              (f'native/schematic/crow-{board}.kicad_sch',False),
              (f'native/schematic/Crow{board.title()}.kicad_sym',False)]:
            p=output/relative
            result,seen=native(p.read_text(),board,physical)
            count=sum(len(c['refs'].get(board,[])) for c in CHANGES)
            q.need(len(seen)==count*(2 if p.suffix=='.kicad_sch' else 1),'Native reference coverage')
            p.write_text(result)
    # Bind the new footprint in the PCB and schematic resource libraries.
    for folder in ('native/pcb/carrier','native/schematic'):
        parent=output/folder/'libraries/Converter_DCDC.pretty'
        old=BASE/'native/pcb/carrier/libraries/Converter_DCDC.pretty/Converter_DCDC_RECOM_R-78E-0.5_THT.kicad_mod'
        updated,_=q.rewrite(old.read_text(),'carrier',CHANGES)
        new=parent/'Converter_DCDC_TRACO_TSR1_RetainedLands.kicad_mod'
        new.write_text(mechanical(updated))
    for name in ('carrier-bom.csv','pod-bom.csv','scope.csv','procurement-plan.csv','jlc-tht-parts.csv'):
        rows=q.read_csv(output/name)
        for row in rows:
            key='MPN' if 'MPN' in row else 'mpn'
            c=next((c for c in CHANGES if row[key]==c['old_mpn']),None)
            if not c: continue
            maker='Manufacturer' if 'Manufacturer' in row else 'manufacturer'
            q.need(row[maker]==c['old_manufacturer'],'CSV identity mismatch')
            row[key],row[maker]=c['mpn'],c['manufacturer']
            for k,v in [('JLCPCB Part #',c['code']),('catalog_locator',c['code']),
                        ('Supply route','JLC_catalog_candidate'),('proposed_route','JLC_catalog_candidate'),
                        ('external_lead',''),('evidence_status','Reviewed quote substitute; allocation and factory process acceptance pending')]:
                if k in row: row[k]=v
            if 'Comment' in row: row['Comment']=c['values'].get(row['Comment'],row['Comment'])
            if row.get('Footprint')==OLD_FP:row['Footprint']=NEW_FP
            if row.get('footprint')==OLD_FP:row['footprint']=NEW_FP
        (output/name).write_bytes(q.csv_bytes(rows))
    rows=q.read_csv(output/'carrier-cpl.csv')
    for row in rows:
        if row['Designator']=='U10':
            row['Mid X']='184.53mm'; row['Mid Y']='-36.25mm'
    (output/'carrier-cpl.csv').write_bytes(q.csv_bytes(rows))
    rows=q.read_csv(output/'tht-placement-verification.csv')
    for row in rows:
        if row['board']=='carrier' and row['reference']=='U10':
            row.update(mpn='TSR 1-2450',body_center_x='184.53',body_center_y='36.25',
                       cpl_x='184.53',cpl_y='-36.25')
    (output/'tht-placement-verification.csv').write_bytes(q.csv_bytes(rows))
    shutil.copyfile(ROOT/'substitutions-20261101/R7-INSTRUCTIONS.txt',output/'README.md')
    shutil.copyfile(REVIEW,output/'qualification.json')
    unchanged=['carrier-gerbers.zip','pod-gerbers.zip','pod-cpl.csv','home-install-parts.csv']
    for n in unchanged:q.need(q.sha(output/n)==q.sha(BASE/n),'Changed protected artifact')
    manifest=dict(status='QUALIFIED_PROTOTYPE_SUBSTITUTION_QUOTE_ONLY',
        assembled={'carrier':2,'pod':8},fabricated={'carrier':5,'pod':10},
        installed={'JLC_SMT':478,'JLC_THT':28,'HOME':18,'total':524},
        production_ready=False,purchase_authorized=False,submitted=False,
        inherited_release_acceptance=False,independent_adversarial_review_performed=False,
        cts_unchanged=True,base_manifest_sha256=q.sha(BASE/'manifest.json'),
        tool_sha256=q.sha(Path(__file__)),review_sha256=q.sha(REVIEW),
        instructions_sha256=q.sha(ROOT/'substitutions-20261101/R7-INSTRUCTIONS.txt'),
        unchanged={n:q.sha(BASE/n) for n in unchanged})
    manifest['files']={str(p.relative_to(output)):q.sha(p) for p in sorted(output.rglob('*'))
                       if p.is_file() and p!=output/'manifest.json'}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest


def verify(output):
    with tempfile.TemporaryDirectory(prefix='crow-r7-replay-') as tmp:
        target=Path(tmp)/'expected';build(target)
        wanted={str(p.relative_to(target)):q.sha(p) for p in target.rglob('*') if p.is_file()}
        actual={str(p.relative_to(output)):q.sha(p) for p in output.rglob('*') if p.is_file()}
        q.need(wanted==actual,'Changed/missing/extra r7 payload')
    return dict(result='PASS',files=len(actual),production_ready=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['build','verify']);p.add_argument('--output',type=Path,default=OUT)
    a=p.parse_args(); print(json.dumps((build if a.action=='build' else verify)(a.output),indent=2))
