"""Native fabrication export component. Not an assembly or release acceptance gate."""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile

import layout_seal as seal

p = seal.p


def layers(board):
    copper = [board.GetLayerName(n) for n in board.GetEnabledLayers().Seq()
              if p.pcb.IsCopperLayer(n)]
    p.need(len(copper) == board.GetCopperLayerCount() and len(copper) >= 2,
           'native copper layer census differs')
    physical = ['F.Cu', *[f'In{i}.Cu' for i in range(1,len(copper)-1)], 'B.Cu']
    p.need(set(copper)==set(physical), 'custom copper naming unsupported')
    copper=physical  # KiCad numeric layer IDs are not physical stack order.
    return copper + ['F.Mask','B.Mask','F.Paste','B.Paste','F.SilkS','B.SilkS','Edge.Cuts']


def canonical_plot(path):
    """Ignore plot timestamps only, never geometry or manufacturing attributes."""
    return '\n'.join(line for line in path.read_text().splitlines()
                     if not (re.fullmatch(r'%TF\.CreationDate,[^*]*\*%',line) or
                             re.fullmatch(r'G04 Created by [^*]*\*',line) or
                             line.startswith('; #@! TF.CreationDate,') or
                             re.match(r'; DRILL file .* date ',line)))


def census(directory, stem, wanted, drill_counts=None):
    named = {stem+'-'+name.replace('SilkS','Silkscreen').replace('.','_')+'.gbr':name for name in wanted}
    expected = set(named)
    expected |= {stem+'-PTH.drl', stem+'-NPTH.drl'}
    files = {f.name for f in directory.iterdir() if f.is_file()}
    # KiCad's optional job is diagnostic, not an additional copper layer.
    p.need(files - {stem+'-job.gbrjob'} == expected and
           all(f.is_file() for f in directory.iterdir()), 'fabrication payload census differs')
    copper = [n for n in wanted if n.endswith('.Cu')]
    for name in expected:
        text = (directory/name).read_text()
        p.need(text.strip(), 'empty plot: '+name)
        if name.endswith('.gbr'):
            layer=named[name]
            if layer in copper:
                side='Top' if layer=='F.Cu' else 'Bot' if layer=='B.Cu' else 'Inr'
                function=f'Copper,L{copper.index(layer)+1},{side}'
            elif layer=='Edge.Cuts':function='Profile,NP'
            else:
                kind={'Mask':'Soldermask','Paste':'Paste','SilkS':'Legend'}[layer.split('.')[1]]
                function=kind+(','+'Top' if layer.startswith('F.') else ',Bot')
            p.need(re.findall(r'%TF.FileFunction,([^*]+)\*%',text)==[function] and 'M02*' in text,
                   'incorrect/incomplete X2 Gerber function: '+name)
        else:
            kind='NPTH' if name.endswith('-NPTH.drl') else 'PTH'
            plated='NonPlated' if kind=='NPTH' else 'Plated'
            function=f'; #@! TF.FileFunction,{plated},1,{len(copper)},{kind}'
            p.need(text.startswith('M48\n') and 'M30' in text and '\nMETRIC\n' in text and
                   function in text and '\n%\n' in text, 'incomplete drill: '+name)
            hits=sum(bool(re.match(r'^X[-+0-9.]+Y[-+0-9.]+',line)) for line in text.splitlines())
            if drill_counts is not None:
                p.need(hits==drill_counts[kind], 'native drill hit census differs: '+name)
    return sorted(expected)


def holes(board):
    result={'PTH':0,'NPTH':0}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetDrillSize().x>0:
                result['NPTH' if pad.GetAttribute()==p.pcb.PAD_ATTRIB_NPTH else 'PTH']+=1
    for track in board.GetTracks():
        if isinstance(track,p.pcb.PCB_VIA):
            p.need(track.TopLayer()==p.pcb.F_Cu and track.BottomLayer()==p.pcb.B_Cu,
                   'blind/buried drilling not supported by this component')
            result['PTH']+=1
    return result


def native_payload(source, output):
    """Internal producer for tests and a verified parent stage; no acceptance claim."""
    p.need(not output.exists(), 'refusing existing native payload')
    output.mkdir(parents=True)
    board = p.pcb.LoadBoard(str(source)); wanted = layers(board)
    p.need(board.GetFootprints() and board.GetTracks(), 'empty/unrouted native input unsupported')
    plots = output/'plots'; plots.mkdir()
    p.command(['kicad-cli','pcb','export','gerbers','--no-protel-ext',
               '--layers',','.join(wanted),'--output',str(plots)+'/',str(source)])
    p.command(['kicad-cli','pcb','export','drill','--format','excellon',
               '--excellon-units','mm','--drill-origin','absolute','--excellon-separate-th',
               '--output',str(plots)+'/',str(source)])
    drill_counts=holes(board)
    members = census(plots, source.stem, wanted, drill_counts)
    zip_path = output/(source.stem+'-gerbers.zip')
    with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for name in members:
            info=zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0))
            info.create_system=3  # Stable Unix regular-file metadata on every host.
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644 << 16
            archive.writestr(info,(plots/name).read_bytes())
    with zipfile.ZipFile(zip_path) as archive:
        p.need(archive.namelist()==members and all(archive.read(n)==(plots/n).read_bytes() for n in members),
               'upload archive differs from plots')
    return {'layers':wanted,'members':members,'source_sha256':p.sha(source),
            'drill_counts':drill_counts,'kicad_version':p.pcb.Version(),
            'files':{str(f.relative_to(output)):p.sha(f) for f in sorted(output.rglob('*')) if f.is_file()},
            'scope':'PCB plots only; no BOM/CPL, assembly verification or release acceptance'}


def export(project, output):
    """Only export live projects from a CURRENT owning layout seal."""
    receipt=seal.check(project)
    review=seal.r.review_json(project,receipt['review'])
    source_manifest=p.read(p.local(project,review['manifest']))
    target=p.local(project,output,exists=False)
    p.need(not target.exists(),'refusing existing export directory')
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='vnext-fab-',dir=target.parent) as tmp:
        stage=Path(tmp)/'payload';stage.mkdir();result={}
        for key in source_manifest['boards']:
            source=p.local(project,review['output']+'/'+key+'/native/'+key+'.kicad_pcb')
            # Work from a copy: some native exporters populate project metadata.
            isolated=Path(tmp)/key;shutil.copytree(source.parent,isolated)
            result[key]=native_payload(isolated/source.name,stage/key)
        manifest={'version':1,'layout_receipt_sha256':p.sha(project/seal.RECEIPT),
                  'boards':result,'accepted':False,'order_status':'DO-NOT-ORDER',
                  'missing':['BOM/CPL and population','assembly/rotation/model review','release review and seal']}
        (stage/'payload.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
        stage.rename(target)
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('--output',required=True)
    a=parser.parse_args()
    try: print(json.dumps(export(a.project.resolve(),a.output),indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('Fabrication component refused: '+str(exc),file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
