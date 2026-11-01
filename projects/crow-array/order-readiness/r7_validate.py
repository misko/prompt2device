"""Read recorded fresh KiCad outputs; validate r7 identities and raw checks."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pcbnew
import r7_quote as r

V=r.ROOT/'substitutions-20261101/r7-validation'


def components(x):
    return {c.attrib['ref']:dict(value=c.findtext('value'),footprint=c.findtext('footprint'),
            fields={f.attrib['name']:f.text for f in c.findall('./fields/field')})
            for c in x.findall('./components/comp')}


def nets(x):
    return sorted((n.attrib['name'],sorted((p.attrib['ref'],p.attrib['pin']) for p in n.findall('node')))
                  for n in x.findall('./nets/net'))


def validate():
    r.verify(r.OUT)
    result={}
    for b in ('carrier','pod'):
        old=ET.parse(V/f'{b}-r6.xml').getroot();new=ET.parse(V/f'{b}-r7.xml').getroot()
        r.q.need(nets(old)==nets(new),'Connectivity changed')
        a,z=components(old),components(new)
        expected={ref:c for c in r.CHANGES for ref in c['refs'].get(b,[])}
        for ref,c in a.items():
            if ref in expected:
                change=expected[ref]
                c['fields'].update(MPN=change['mpn'],Manufacturer=change['manufacturer'])
                c['value']=change['values'].get(c['value'],c['value'])
                if ref=='U10':c['footprint']=c['fields']['Footprint']=r.NEW_FP
        r.q.need(a==z,'Unexpected schematic change')
        pcb=pcbnew.LoadBoard(str(r.OUT/f'native/pcb/{b}/{b}.kicad_pcb'))
        fps={f.GetReference():f for f in pcb.GetFootprints()}
        for row in r.q.read_csv(r.OUT/f'{b}-bom.csv'):
            for ref in row['Designator'].split(','):
                c=z[ref];f=fps[ref]
                r.q.need(row['MPN']==c['fields']['MPN']==f.GetFieldText('MPN'),'MPN parity')
                r.q.need(row['Manufacturer']==c['fields']['Manufacturer']==f.GetFieldText('Manufacturer'),'Maker parity')
                r.q.need(row['Footprint']==c['footprint']==f.GetFPIDAsString(),'Footprint parity')
                r.q.need(row['Comment']==c['value']==f.GetValue(),'Value parity')
        erc=json.loads((V/f'{b}-erc.json').read_text());drc=json.loads((V/f'{b}-drc.json').read_text())
        r.q.need(not any(s.get('violations') for s in erc['sheets']),'ERC violations')
        r.q.need(not drc['violations'] and not drc['unconnected_items'],'DRC violations')
        r.q.need(not drc.get('ignored_checks'),'Ignored DRC checks')
        r.q.need(set(drc['included_severities'])=={'error','warning','exclusion'},'Incomplete DRC scope')
        if b=='carrier':r.q.need(not list(fps['U10'].Models()),'Wrong inherited model')
        result[b]=dict(connectivity='UNCHANGED',exact_changed_refs=sorted(expected),
             erc_violations=0,drc_violations=0,unconnected=0,
             inherited_erc_disabled_checks=erc.get('ignored_checks',[]))
    return dict(result='PASS',boards=result,kicad=pcbnew.Version(),
        manifest_sha256=r.q.sha(r.OUT/'manifest.json'),production_ready=False,
        raw_reports={p.name:r.q.sha(p) for p in sorted(V.iterdir()) if p.suffix in ('.xml','.json','.pdf') and p.name!='result.json'},
        validator_sha256=r.q.sha(Path(__file__)))


if __name__=='__main__':
    result=validate()
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);args=p.parse_args()
    if args.output:
        r.q.need(not args.output.exists(),'Refusing existing result')
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2))
