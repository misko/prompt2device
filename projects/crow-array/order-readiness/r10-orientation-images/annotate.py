"""Readable inspection sheets, preserving original KiCad renders alongside them."""
from pathlib import Path
import hashlib
import json
import math
import sys
import pcbnew
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
E = json.loads((HERE/'evidence.json').read_text())
sys.path.insert(0, str(ROOT/'skills/jlcpcb-fab/scripts'))
import jlc_twin as twin
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def font(size):
    return ImageFont.truetype(FONT, size)


def sheet(board):
    # Both signs of the 45-degree rotation, retained with explicit camera labels.
    im = Image.new('RGB', (1600, 1500), '#f7f9fc')
    d = ImageDraw.Draw(im)
    d.text((25, 15), f'{board.upper()} r10 | Exact catalog connector models, fitted to native numbered pads', font=font(27), fill='#10263c')
    d.text((25, 58), 'DIAGNOSTIC ONLY: not the JLC draft preview. Other component bodies omitted.', font=font(23), fill='#a43c27')
    for i, (view, title) in enumerate([('front45', '45-degree view from connector edge'), ('opposite45', 'Opposite 45-degree view')]):
        raw = Image.open(HERE/f'{board}-{view}.png').convert('RGB')
        # Crop unused renderer margins only, no geometry change.
        w, h = raw.size
        ylo,yhi = (.27,.76) if board=='carrier' else (.06,.87)
        crop = raw.crop((int(w*.19), int(h*ylo), int(w*.81), int(h*yhi)))
        crop.thumbnail((1540, 620))
        x, y = (1600-crop.width)//2, 145+i*680
        im.paste(crop, (x, y))
        d.text((25, 111+i*680), title, font=font(24), fill='#10263c')
    im.save(HERE/f'{board}-orientation.png')


def pinmap():
    im = Image.new('RGB', (1800, 900), '#f7f9fc')
    d = ImageDraw.Draw(im)
    d.text((25, 15), 'Native holes + manufacturer mouth direction | TOP / COMPONENT SIDE', font=font(30), fill='#10263c')
    d.text((25, 62), 'Gold: native pads. Blue crosses: fitted catalog pad centers. Gray: locator holes. Cyan: drawing-derived mouth.', font=font(22), fill='#31465a')
    for n, (board_name, ref) in enumerate([('carrier','J101'), ('pod','J1'), ('carrier','J1')]):
        record = E['boards'][board_name]
        src = ROOT/record['source']
        assert hashlib.sha256(src.read_bytes()).hexdigest() == record['sha256']
        board = pcbnew.LoadBoard(str(src))
        fp = next(f for f in board.GetFootprints() if f.GetReference()==ref)
        f = next(f for f in record['connectors'] if f['ref']==ref)
        mod = next((HERE/'catalog'/f['lcsc']/'jlc.pretty').glob('*.kicad_mod'))
        vendor = pcbnew.FootprintLoad(str(mod.parent), mod.stem)
        ours = twin.pads_of(fp, footprint_local=True)
        theirs = twin.pads_of(vendor, footprint_local=True)
        oc,jc = twin.centroid(ours),twin.centroid(theirs)
        fitted = {}
        for number, points in theirs.items():
            x,y=points[0]
            x,y=twin.local_to_board(x-jc[0],y-jc[1],f['catalog_to_native_local_rotation'])
            x,y=twin.local_to_board(x+oc[0],y+oc[1],fp.GetOrientationDegrees())
            fitted[number]=(fp.GetPosition().x/1e6+x,fp.GetPosition().y/1e6+y)
        px, py = fp.GetPosition().x/1e6, fp.GetPosition().y/1e6
        power = board_name == 'carrier' and ref == 'J1'
        left, right, front, rear = (183.5,192.5,1,15.4) if power else (px-4.318, px+11.430, py-7.620, py+7.366)
        cx = (left+right)/2
        x0 = n*600+300
        def xy(x,y): return (x0+(x-cx)*23, 250+y*23)
        d.text((n*600+22, 117), f'{board_name.upper()} {ref}', font=font(27), fill='#10263c')
        d.text((n*600+22, 154), 'PJ-102AH' if power else 'RJHSE-5080', font=font(22), fill='#31465a')
        d.rectangle((n*600+10,250,n*600+590,740),fill='#e4efe9')
        # Native Edge.Cuts segments, including the pod notch.
        for edge in board.GetDrawings():
            if edge.GetLayer()!=pcbnew.Edge_Cuts: continue
            a,b=edge.GetStart(),edge.GetEnd()
            ax,ay,bx,by=a.x/1e6,a.y/1e6,b.x/1e6,b.y/1e6
            if abs(ay-by)<1e-6 and -.1<=ay<=20:
                lo,hi=max(min(ax,bx),cx-12.5),min(max(ax,bx),cx+12.5)
                if hi>=lo:d.line((*xy(lo,ay),*xy(hi,ay)),fill='#173b2c',width=4)
            elif abs(ax-bx)<1e-6 and cx-12.5<=ax<=cx+12.5:
                lo,hi=max(min(ay,by),0),min(max(ay,by),20)
                if hi>=lo:d.line((*xy(ax,lo),*xy(ax,hi)),fill='#173b2c',width=4)
        d.rectangle((*xy(left,front),*xy(right,rear)),outline='#727e89',width=3)
        d.line((*xy(left,front),*xy(right,front)),fill='#008aab',width=7)
        ax,ay=xy(cx,front)
        d.line((ax,ay,ax,205),fill='#008aab',width=5)
        d.polygon([(ax,195),(ax-9,211),(ax+9,211)],fill='#008aab')
        for pad in fp.Pads():
            x,y=pad.GetPosition().x/1e6,pad.GetPosition().y/1e6
            X,Y=xy(x,y)
            num=pad.GetNumber()
            r=11 if num else pad.GetDrillSize().x/1e6*23/2
            d.ellipse((X-r,Y-r,X+r,Y+r),fill='#edc448' if num else '#bcc5cc',outline='#4e5e67',width=2)
            if num:
                # Independently transformed catalog centers, not copied native centers.
                FX,FY=xy(*fitted[num])
                d.line((FX-5,FY,FX+5,FY),fill='#1474dd',width=2)
                d.line((FX,FY-5,FX,FY+5),fill='#1474dd',width=2)
                dy=15 if power or int(num)%2==0 else -34
                d.text((X-7,Y+dy),num,font=font(20),fill='#152b3b')
            else:
                d.text((X-20,Y-10),'peg',font=font(18),fill='#152b3b')
        d.text((n*600+22, 767), f'Catalog pad fit: {f["max_pad_error_mm"]:.3f} mm maximum',font=font(21),fill='#10263c')
        d.text((n*600+22, 800), 'Mouth points toward native -Y / board edge',font=font(20),fill='#10263c')
    d.text((25,855),'Manufacturer dimensions define the cyan direction; outlines are not independently verified CAD or plug-clearance approval.',font=font(21),fill='#a43c27')
    im.save(HERE/'numbered-holes.png')


for name in ('carrier','pod'):
    sheet(name)
pinmap()
manifest = {str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in HERE.rglob('*') if p.is_file() and
            p.suffix in {'.png','.py','.json','.pdf','.kicad_pcb','.wrl','.step','.kicad_mod','.kicad_sym'}
            and p.name!='manifest.json' and '__pycache__' not in p.parts}
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
