/**
 * Copper/drill geometry transcribed from the immutable KiCad libraries listed
 * in 06_build/tmp/analog-footprints/repair.json. KiCad's +Y-down centers are negated for tscircuit's +Y-up
 * convention. Paste-only apertures are deliberately left to the native
 * footprint authority because an smtpad would incorrectly create copper.
 */
type Smd = readonly [pin: string, x: number, yKiCad: number, w: number, h: number, radius?: number]
const pads = (ps: readonly Smd[]) => ps.map(([pin, x, y, w, h, radius]) =>
  <smtpad key={`${pin}:${x}:${y}`} portHints={[pin]} pcbX={`${x}mm`} pcbY={`${-y}mm`}
    width={`${w}mm`} height={`${h}mm`} shape="rect"
    {...(radius === undefined ? {} : { rectBorderRadius: `${radius}mm` })} />)

export const Wurth615008160221Rj45 = () => <footprint>
  <hole pcbX="-3.28mm" pcbY="-0.7mm" diameter="3.18mm" />
  <hole pcbX="10.42mm" pcbY="-0.7mm" diameter="3.18mm" />
  <platedhole portHints={['1']} pcbX="0mm" pcbY="0mm" shape="circular_hole_with_rect_pad"
    holeDiameter="0.8mm" rectPadWidth="1.3mm" rectPadHeight="1.3mm" />
  {[2,3,4,5,6,7,8].map((pin) => <platedhole key={pin} portHints={[`${pin}`]}
    pcbX={`${(pin - 1) * 1.02}mm`} pcbY={`${pin % 2 === 0 ? -4 : 0}mm`}
    shape="circle" holeDiameter="0.8mm" outerDiameter="1.3mm" />)}
  {[['9',10.97],['10',-3.83]].map(([pin,x]) => <platedhole key={pin} portHints={[`${pin}`]}
    pcbX={`${x}mm`} pcbY="2.35mm" shape="oval" outerWidth="1.5mm" outerHeight="2.5mm"
    holeWidth="1mm" holeHeight="2mm" />)}
</footprint>

export const Littelfuse1812L03560 = () => <footprint>{pads([
  ['1',-2.615,0,1.78,3.15], ['2',2.615,0,1.78,3.15],
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
