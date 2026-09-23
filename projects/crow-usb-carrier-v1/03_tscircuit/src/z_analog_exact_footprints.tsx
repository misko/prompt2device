import { Fragment } from "react"
/**
 * Copper/drill geometry transcribed from the immutable KiCad libraries listed
 * in 06_build/tmp/analog-footprints/repair.json. KiCad's +Y-down centers are negated for tscircuit's +Y-up
 * convention. Paste-only apertures are deliberately left to the native
 * footprint authority because an smtpad would incorrectly create copper.
 */
type Smd = readonly [pin: string, x: number, yKiCad: number, w: number, h: number, radius?: number]
const pads = (ps: readonly Smd[]) => ps.map(([pin, x, y, w, h, radius]) =>
  <Fragment key={`${pin}:${x}:${y}`}><smtpad portHints={[pin]} pcbX={`${x}mm`} pcbY={`${-y}mm`}
    width={`${w}mm`} height={`${h}mm`} shape="rect"
    {...(radius === undefined ? {} : { rectBorderRadius: `${radius}mm` })} /></Fragment>)

export const Wurth615008160221Rj45 = () => <footprint>
  <hole pcbX="-3.28mm" pcbY="-0.7mm" diameter="3.18mm" />
  <hole pcbX="10.42mm" pcbY="-0.7mm" diameter="3.18mm" />
  <platedhole portHints={['1']} pcbX="0mm" pcbY="0mm" shape="circular_hole_with_rect_pad"
    holeDiameter="0.8mm" rectPadWidth="1.3mm" rectPadHeight="1.3mm" />
  {[2,3,4,5,6,7,8].map((pin) => <Fragment key={pin}><platedhole portHints={[`${pin}`]}
    pcbX={`${(pin - 1) * 1.02}mm`} pcbY={`${pin % 2 === 0 ? -4 : 0}mm`}
    shape="circle" holeDiameter="0.8mm" outerDiameter="1.3mm" /></Fragment>)}
  {[['9',10.97],['10',-3.83]].map(([pin,x]) => <Fragment key={pin}><platedhole portHints={[`${pin}`]}
    pcbX={`${x}mm`} pcbY="2.35mm" shape="oval" outerWidth="1.5mm" outerHeight="2.5mm"
    holeWidth="1mm" holeHeight="2mm" /></Fragment>)}
</footprint>

/** TI DRC0010J manufacturer-land centers; EP is pin 11 and must join RTN. */
export const TiDrc0010j = () => <footprint>{pads([
  ['1',-1.4,-1,0.6,0.24,0.05], ['2',-1.4,-0.5,0.6,0.24,0.05],
  ['3',-1.4,0,0.6,0.24,0.05], ['4',-1.4,0.5,0.6,0.24,0.05],
  ['5',-1.4,1,0.6,0.24,0.05], ['6',1.4,1,0.6,0.24,0.05],
  ['7',1.4,0.5,0.6,0.24,0.05], ['8',1.4,0,0.6,0.24,0.05],
  ['9',1.4,-0.5,0.6,0.24,0.05], ['10',1.4,-1,0.6,0.24,0.05],
  ['11',0,0,1.65,2.4],
])}</footprint>

export const Sot553 = () => <footprint>{pads([
  ['1',-0.7125,-0.5,0.675,0.35,0.0875], ['2',-0.7125,0,0.675,0.35,0.0875],
  ['3',-0.7125,0.5,0.675,0.35,0.0875], ['4',0.7125,0.5,0.675,0.35,0.0875],
  ['5',0.7125,-0.5,0.675,0.35,0.0875],
])}</footprint>

export const Diodes2N7002kSot23 = () => <footprint>{pads([
  ['1',-1,-0.95,0.9,0.8], ['2',-1,0.95,0.9,0.8], ['3',1,0,0.9,0.8],
])}</footprint>

export const PanasonicEeeFk8x10 = () => <footprint>{pads([
  ['1',-3.55,0,4,2,0.2], ['2',3.55,0,4,2,0.2],
])}</footprint>

export const TiDck0005a = () => <footprint>{pads([
  ['1',-1,0.65,0.6,1], ['2',-1,0,0.6,1], ['3',-1,-0.65,0.6,1],
  ['4',1,-0.65,0.6,1], ['5',1,0.65,0.6,1],
])}</footprint>

export const TiDse0006a = () => <footprint>{pads([
  ['1',-0.55,-0.5,0.8,0.25,0.05], ['2',-0.6,0,0.7,0.25,0.05],
  ['3',-0.6,0.5,0.7,0.25,0.05], ['4',0.6,0.5,0.7,0.25,0.05],
  ['5',0.6,0,0.7,0.25,0.05], ['6',0.6,-0.5,0.7,0.25,0.05],
])}</footprint>

export const TiDsg0008a = () => <footprint>
  {pads([
    ['1',-0.95,-0.75,0.5,0.25,0.05], ['2',-0.95,-0.25,0.5,0.25,0.05],
    ['3',-0.95,0.25,0.5,0.25,0.05], ['4',-0.95,0.75,0.5,0.25,0.05],
    ['5',0.95,0.75,0.5,0.25,0.05], ['6',0.95,0.25,0.5,0.25,0.05],
    ['7',0.95,-0.25,0.5,0.25,0.05], ['8',0.95,-0.75,0.5,0.25,0.05],
    ['9',0,0,0.9,1.6],
  ])}
</footprint>

/** TI YBH0009-C02 bump-side-down top view. KiCad +Y is down; tscircuit +Y is up.
 * JLC advanced 4L coupon: 0.25-mm perimeter lands and 0.35-mm B2 copper.
 * Native footprint owns B2's 0.25-mm mask/paste openings and Type VII via. */
export const TiYbh0009C02Tmux4827 = () => <footprint>
  {([['A',-0.4],['B',0],['C',0.4]] as const).flatMap(([row,y], ri) =>
    (['1','2','3'] as const).map((col, ci) => {
      const pin = `${row}${col}`
      const sourcePin = `${ri * 3 + ci + 1}` // 1=A1 ... 5=B2 ... 9=C3
      const diameter = pin === 'B2' ? 0.35 : 0.25
      return <Fragment key={pin}><smtpad portHints={[sourcePin]}
        pcbX={`${(ci - 1) * 0.4}mm`} pcbY={`${-y}mm`}
        radius={`${diameter / 2}mm`} shape="circle" /></Fragment>
    }))}
</footprint>

export const YageoRt0603 = () => <footprint>{pads([
  ['1',-0.825,0,0.8,0.95,0.2], ['2',0.825,0,0.8,0.95,0.2],
])}</footprint>

export const CirrusCs5308pQfn48 = () => {
  const left: Smd[] = Array.from({length:12},(_,i) => [`${i+1}`,-2.95,-2.2+i*0.4,0.8,0.2,0.05] as const)
  const top: Smd[] = Array.from({length:12},(_,i) => [`${i+13}`,-2.2+i*0.4,2.95,0.2,0.8,0.05] as const)
  const right: Smd[] = Array.from({length:12},(_,i) => [`${i+25}`,2.95,2.2-i*0.4,0.8,0.2,0.05] as const)
  const bottom: Smd[] = Array.from({length:12},(_,i) => [`${i+37}`,2.2-i*0.4,-2.95,0.2,0.8,0.05] as const)
  return <footprint>{pads([...left,...top,...right,...bottom,['49',0,0,4.6,4.6]])}</footprint>
}

/** TI RTW0024A primary land pattern, drawing 4222815/A: 0.5-mm pitch,
 * 24×0.6×0.25-mm lands on 3.8-mm opposite centerlines, 2.6-mm EP. */
export const TiRtw0024a = () => {
  const left: Smd[] = Array.from({length:6}, (_,i) => [`${i+1}`,-1.9, -1.25+i*0.5,0.6,0.25] as const)
  const bottom: Smd[] = Array.from({length:6}, (_,i) => [`${i+7}`,-1.25+i*0.5,1.9,0.25,0.6] as const)
  const right: Smd[] = Array.from({length:6}, (_,i) => [`${i+13}`,1.9,1.25-i*0.5,0.6,0.25] as const)
  const top: Smd[] = Array.from({length:6}, (_,i) => [`${i+19}`,1.25-i*0.5,-1.9,0.25,0.6] as const)
  return <footprint>{pads([...left,...bottom,...right,...top,['25',0,0,2.6,2.6]])}</footprint>
}
