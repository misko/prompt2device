"""Reviewed TI-clock quotation derivative. No upload or order operations.

Frozen reviewed native source is authoritative. This is not stage admission.
Build refuses existing output; verify checks hashes, identities and fresh DRC.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import substitute_quote as q
import r7_quote

ROOT=Path(__file__).resolve().parent
BASE=r7_quote.OUT
ENG=ROOT/'substitutions-20261101/lmk6c-engineering'
SOURCE=ENG/'draft7'
OUT=ROOT/'quote-draft/r8-2c8p-ti-clock'
MPN='LMK6CE012288CDLFR'
FP='CrowPhysical:TI_LMK6C_DLF0004A'
LAYERS='F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts'


def command(*args):
    return subprocess.run([str(x) for x in args],check=True,capture_output=True,text=True).stdout


def inputs():
    r7_quote.verify(BASE)
    review=json.loads((ENG/'review.json').read_text())
    q.need(review['decision']=='PASS_FOR_PROTOTYPE_QUOTE','Engineering review missing')
    for name,digest in review['subjects'].items():q.need(q.sha(ENG/name)==digest,'Changed reviewed subject: '+name)
    return review


def tables():
    result={name:q.read_csv(BASE/name) for name in ('carrier-bom.csv','carrier-cpl.csv','scope.csv','procurement-plan.csv')}
    for row in result['carrier-bom.csv']:
        if row['Designator']=='X1':
            row.update(MPN=MPN,Manufacturer='Texas Instruments',Comment=MPN,Footprint=FP)
            row['JLCPCB Part #']='C36974742';row['Supply route']='JLC_overseas_stock_candidate'
        if row['Designator']=='C4':
            row.update(MPN='CL21B105KBFNNNE',Comment='1uF 50V X7R 10% CLOCK')
            row['JLCPCB Part #']='C28323';row['Supply route']='JLC_catalog_candidate'
    for row in result['carrier-cpl.csv']:
        if row['Designator']=='X1':row.update({'Mid X':'86.0mm','Mid Y':'-85.5mm','Rotation':'90.0'})
        if row['Designator']=='C4':row.update({'Mid X':'83.46mm','Mid Y':'-82.9mm','Rotation':'0.0'})
    for row in result['scope.csv']:
        if row['board']!='carrier':continue
        if row['reference']=='X1':row.update(manufacturer='Texas Instruments',mpn=MPN,footprint=FP)
        if row['reference']=='C4':row['mpn']='CL21B105KBFNNNE'
    for row in result['procurement-plan.csv']:
        if row['mpn']=='CB3LV-3I-12M288000':
            row.update(manufacturer='Texas Instruments',mpn=MPN,catalog_locator='C36974742',external_lead='',
                       proposed_route='JLC_overseas_stock_candidate',
                       evidence_status='10 overseas/presale observed Nov 1; overlapping pool, no allocation; usable date and job gross demand unknown')
        if row['mpn'] in ('CL21B104KBCNNNC','CL21B105KBFNNNE'):
            refs=row['carrier_refs'].split(';')
            if row['mpn']=='CL21B104KBCNNNC':refs.remove('C4')
            else:refs=['C4']+refs
            row['carrier_refs']=';'.join(refs);row['per_carrier']=str(len(refs))
            row['installed_2c8p']=str(2*len(refs)+8*int(row['per_pod']))
    return result


def preflight(output,checks):
    checks.mkdir(parents=True,exist_ok=True)
    board=output/'native/pcb/carrier/carrier.kicad_pcb'
    sch=output/'native/schematic/crow-carrier.kicad_sch'
    command('kicad-cli','pcb','drc','--format','json','--severity-all','--all-track-errors',
            '--schematic-parity','--refill-zones','-o',checks/'drc.json',board)
    d=json.loads((checks/'drc.json').read_text())
    q.need(not any(d.get(k) for k in ('violations','unconnected_items','schematic_parity','ignored_checks')),'DRC/parity failed')
    command('kicad-cli','sch','erc','--format','json','--severity-all','-o',checks/'erc.json',sch)
    e=json.loads((checks/'erc.json').read_text())
    q.need(not any(s.get('violations') for s in e['sheets']),'ERC failed')
    command('kicad-cli','sch','export','netlist','--format','kicadxml','-o',checks/'netlist.xml',sch)
    tree=ET.parse(checks/'netlist.xml').getroot()
    comps={c.attrib['ref']:c for c in tree.findall('./components/comp')}
    for row in q.read_csv(output/'carrier-bom.csv'):
        for ref in row['Designator'].split(','):
            c=comps[ref];fields={f.attrib['name']:f.text for f in c.findall('./fields/field')}
            q.need(fields['MPN']==row['MPN'] and fields['Manufacturer']==row['Manufacturer'],'BOM/schematic identity: '+ref)
            q.need(c.findtext('footprint')==row['Footprint'] and c.findtext('value')==row['Comment'],'BOM value/footprint: '+ref)
    return dict(drc=0,opens=0,parity=0,erc=0,erc_ignored=e.get('ignored_checks',[]))


def build(output):
    review=inputs();q.need(not output.exists(),'Refusing existing quote output')
    shutil.copytree(BASE,output)
    for relative in ('pcb/carrier/carrier.kicad_pcb','schematic/crow-carrier.kicad_sch','schematic/CrowCarrier.kicad_sym'):
        shutil.copyfile(SOURCE/'native'/relative,output/'native'/relative)
    shutil.copyfile(output/'native/schematic/crow-carrier.kicad_sch',output/'native/pcb/carrier/carrier.kicad_sch')
    for lib in ('pcb/carrier/CrowPhysical.pretty','schematic/CrowPhysical.pretty'):
        shutil.copyfile(ENG/'TI_LMK6C_DLF0004A.kicad_mod',output/'native'/lib/'TI_LMK6C_DLF0004A.kicad_mod')
    for name,rows in tables().items():(output/name).write_bytes(q.csv_bytes(rows))
    shutil.copyfile(ENG/'review.json',output/'qualification.json')
    (output/'engineering').mkdir()
    for src,name in ((ENG/'IMPLEMENTATION-REVIEW.md','CLOCK-POWER-MODEL.md'),
                     (SOURCE/'clock-v2.json','clock-model.json'),(ENG/'bypass-stock.json','bypass-stock.json'),
                     (ENG.parent/'LMK6C-STOCK-20261101.json','oscillator-stock.json')):
        shutil.copyfile(src,output/'engineering'/name)
    for src,digest in review['independent_outputs'].items():
        q.need(q.sha(Path(src))==digest,'Changed independent evidence')
        shutil.copyfile(src,output/'engineering'/Path(src).name)
    shutil.copyfile(ROOT/'R8-INSTRUCTIONS.md',output/'README.md')
    checks=preflight(output,output/'checks')
    command('kicad-cli','sch','export','pdf','-o',output/'carrier-schematic.pdf',output/'native/schematic/crow-carrier.kicad_sch')
    with tempfile.TemporaryDirectory(prefix='crow-r8-gerbers-') as tmp:
        folder=Path(tmp);board=output/'native/pcb/carrier/carrier.kicad_pcb'
        command('kicad-cli','pcb','export','gerbers','--no-protel-ext','--layers',LAYERS,'-o',str(folder)+'/',board)
        command('kicad-cli','pcb','export','drill','--excellon-separate-th','--drill-origin','absolute','-o',str(folder)+'/',board)
        files=sorted(p for p in folder.iterdir() if p.suffix in ('.gbr','.drl'))
        q.need(len(files)==13,'Expected eleven Gerbers plus two drill files')
        with zipfile.ZipFile(output/'carrier-gerbers.zip','w',zipfile.ZIP_DEFLATED) as z:
            for p in files:
                info=zipfile.ZipInfo(p.name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                z.writestr(info,p.read_bytes())
    protected=('pod-gerbers.zip','pod-bom.csv','pod-cpl.csv','home-install-parts.csv','jlc-tht-parts.csv','tht-placement-verification.csv')
    for name in protected:q.need(q.sha(output/name)==q.sha(BASE/name),'Changed protected payload: '+name)
    m=dict(status='INDEPENDENTLY_REVIEWED_PROTOTYPE_QUOTE_ONLY',production_ready=False,purchase_authorized=False,
           stage_acceptance_issued=False,inherited_release_acceptance=False,submitted=False,
           fabricated={'carrier':5,'pod':10},assembled={'carrier':2,'pod':8},
           installed={'JLC_SMT':478,'JLC_THT':28,'HOME':18,'total':524},
           oscillator_installed=2,oscillator_warehouse_date=None,
           source_review_sha256=q.sha(ENG/'review.json'),base_manifest_sha256=q.sha(BASE/'manifest.json'),
           tool_sha256=q.sha(Path(__file__)),checks=checks,
           protected={name:q.sha(BASE/name) for name in protected})
    m['files']={str(p.relative_to(output)):q.sha(p) for p in sorted(output.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    (output/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    return dict(result='BUILT',files=len(m['files']),production_ready=False)


def verify(output):
    inputs();m=json.loads((output/'manifest.json').read_text())
    q.need(not m['production_ready'] and not m['purchase_authorized'],'Invalid authorization')
    q.need(m['tool_sha256']==q.sha(Path(__file__)),'Changed producer')
    q.need(m['source_review_sha256']==q.sha(ENG/'review.json'),'Changed review')
    actual={str(p.relative_to(output)):q.sha(p) for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}
    q.need(actual==m['files'],'Changed/missing/extra payload')
    for name,rows in tables().items():q.need((output/name).read_bytes()==q.csv_bytes(rows),'Wrong derived table: '+name)
    for name,digest in m['protected'].items():q.need(q.sha(output/name)==digest==q.sha(BASE/name),'Protected payload changed')
    q.need(q.sha(output/'native/pcb/carrier/carrier.kicad_pcb')==q.sha(SOURCE/'native/pcb/carrier/carrier.kicad_pcb'),'Wrong reviewed carrier')
    with tempfile.TemporaryDirectory(prefix='crow-r8-verify-') as tmp:preflight(output,Path(tmp))
    return dict(result='PASS',files=len(actual),production_ready=False,oscillator_warehouse_date=None)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['build','verify'])
    p.add_argument('--output',type=Path,default=OUT);a=p.parse_args()
    print(json.dumps((build if a.action=='build' else verify)(a.output),indent=2))
