// Crow roof array central audio carrier v1.
//
// FIRST-ARTICLE-ONLY / DO-NOT-ORDER. One CS5308P converts eight active-
// balanced analog spokes into one clock-synchronous TDM8 stream for an
// external cable-connected miniDSP MCHStreamer. Raspberry Pi, PoE, Ethernet,
// USB data and the MCHStreamer itself are intentionally off this PCB.

import { poseFor, chipStyle, Ground, LocalBypassRail, LocalChipRail, SchematicWires, sheets } from "./schematic_presentation"

// ADC physical channel order stays hardware-default; this fixed wiring table
// binds logical pod identity to stream slots. See ADR0027.
import channelMap from "../../03_src/adc_channel_map.json"
const expectedMapKeys = ["capture_requirements", "id", "pod_to_adc", "schema"]
if (Object.keys(channelMap).sort().join(",") !== expectedMapKeys.join(",") ||
    channelMap.schema !== 1 || typeof channelMap.id !== "string" || !channelMap.id.trim() ||
    !Array.isArray(channelMap.pod_to_adc)) {
  throw new Error("Invalid ADC channel-map header")
}
const podToAdc = channelMap.pod_to_adc
if (podToAdc.length !== 8 || new Set(podToAdc).size !== 8 ||
    podToAdc.some((ch, pod) => !Number.isInteger(ch) || ch < 1 || ch > 8 ||
      (ch <= 4) !== (pod < 4) || (pod >= 4 && ch !== pod + 1))) {
  throw new Error("Invalid eight-channel pod/ADC map")
}
// The path checker also grades the capture requirements and source digest;
// these are first-article obligations, not a claim that a recording passed.
const adcInputNet = (physicalChannel: number, leg: "P" | "N") =>
  `ADC${podToAdc.indexOf(physicalChannel) + 1}${leg}`

const N = (name: string) => `net.${/^\d/.test(name) ? `N${name}` : name}`

// The pinned producer ignores deprecated schPinSpacing. Per-pin margins are
// consumed by its box geometry: 0.2 mm base + 0.3 mm on either side = 0.8 mm.
const spacedPins = (count: number) => Object.fromEntries(
  Array.from({ length: count }, (_, i) => [`pin${i + 1}`, { topMargin: 0.3, bottomMargin: 0.3 }]),
)

const SHEET: Record<string, string> = {
  "Input and spoke power": "spoke_power",
  "Channels 1-4 analog": "analog_1_4",
  "Channels 5-8 analog": "analog_5_8",
  "ADC references and mode": "adc",
  "Reference buffers and filters": "references",
  "TDM clocks and reset": "digital",
}

const sheetFor = (section: string) => {
  const sheet = SHEET[section]
  if (!sheet) throw new Error(`No schematic sheet owns section: ${section}`)
  return sheet
}

// tscircuit still computes PCB collision diagnostics even though the governed
// board is regenerated from floorplan.yaml. Give every authored component a
// deterministic, sheet-separated scratch placement so this foreign producer
// cannot hide real circuit errors behind default-at-origin courtyard noise.
const PCB_SHEET_X: Record<string, number> = {
  "Input and spoke power": -2000,
  "Channels 1-4 analog": -1000,
  "Channels 5-8 analog": 0,
  "ADC references and mode": 1000,
  "TDM clocks and reset": 2000,
  "Reference buffers and filters": 3000,
}

const mmNumber = (value: number | string) =>
  typeof value === "number" ? value : Number.parseFloat(value)

const pcbAt = (section: string, x: number | string, y: number | string) => ({
  pcbX: `${PCB_SHEET_X[section] + 4 * mmNumber(x)}mm`,
  pcbY: `${4 * mmNumber(y)}mm`,
})

const Chip = ({ schSectionName, schX, schY, jlc, ...props }: any) => (
  <>
  <chip schSectionName={schSectionName} schX={schX} schY={schY}
    supplierPartNumbers={{ jlcpcb: jlc ? [jlc] : [] }}
    {...pcbAt(schSectionName, schX, schY)} {...props} {...poseFor(props.name)} {...chipStyle(props.name)} />
  <Ground refName={props.name} pins={Object.entries(props.connections??{}).filter(([,net])=>net===N("GND")).map(([pin])=>pin)} />
  <LocalChipRail refName={props.name} connections={props.connections} />
  </>
)

const R2 = ({ name, value, a, b, jlc, mpn, section, schX, schY, footprint = "0402" }: any) => (
  <>
  <resistor name={name} resistance={value} footprint={footprint}
    manufacturerPartNumber={mpn} supplierPartNumbers={{ jlcpcb: jlc ? [jlc] : [] }}
    schSectionName={section} schSheetName={sheetFor(section)} schX={schX} schY={schY}
    {...pcbAt(section, schX, schY)}
    connections={{ pin1: N(a), pin2: N(b) }} {...poseFor(name)} />
  <Ground refName={name} pins={b==="GND" ? ["pin2"] : []} passive />
  <LocalBypassRail refName={name} net={N(a)} returnNet={N(b)} />
  </>
)

const C2 = ({ name, value, a, b, jlc, mpn, section, schX, schY, footprint = "0402", polarized = false }: any) => (
  <>
  <capacitor name={name} capacitance={value} footprint={footprint} polarized={polarized}
    manufacturerPartNumber={mpn} supplierPartNumbers={{ jlcpcb: jlc ? [jlc] : [] }}
    schSectionName={section} schSheetName={sheetFor(section)} schX={schX} schY={schY}
    {...pcbAt(section, schX, schY)}
    connections={{ pin1: N(a), pin2: N(b) }} {...poseFor(name)} />
  <Ground refName={name} pins={b==="GND" ? ["pin2"] : []} passive />
  <LocalBypassRail refName={name} net={N(a)} />
  </>
)

// Schematic-source footprints below reproduce the exact pad numbering and
// land centres of the governed KiCad FPID.  They are not package-family
// approximations: the converter replaces them with the dossier-bound FPID,
// while tscircuit uses these same centres to preserve pad identity.
const Littelfuse1812L035 = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-2.615mm" pcbY="0mm" width="1.78mm" height="3.15mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="2.615mm" pcbY="0mm" width="1.78mm" height="3.15mm" shape="rect" />
  </footprint>
)

const YageoRT0603 = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-0.825mm" pcbY="0mm" width="0.8mm" height="0.95mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="0.825mm" pcbY="0mm" width="0.8mm" height="0.95mm" shape="rect" />
  </footprint>
)

const TwoSided = ({ pins, pitch = 0.65, span = 4.8, ep = false }: any) => {
  const left = Math.ceil(pins / 2)
  return (
    <footprint>
      {Array.from({ length: left }, (_, i) => (
        <smtpad key={`l${i}`} portHints={[`${i + 1}`]} pcbX={`${-span / 2}mm`}
          pcbY={`${((left - 1) / 2 - i) * pitch}mm`} width="1.4mm" height="0.35mm" shape="rect" />
      ))}
      {Array.from({ length: pins - left }, (_, i) => (
        <smtpad key={`r${i}`} portHints={[`${left + i + 1}`]} pcbX={`${span / 2}mm`}
          pcbY={`${(-(pins - left - 1) / 2 + i) * pitch}mm`} width="1.4mm" height="0.35mm" shape="rect" />
      ))}
      {ep && <smtpad portHints={[`${pins + 1}`]} pcbX="0mm" pcbY="0mm" width="2.4mm" height="2.4mm" shape="rect" />}
    </footprint>
  )
}

const Qfn48 = () => (
  <footprint>
    {Array.from({ length: 12 }, (_, i) => <smtpad key={`l${i}`} portHints={[`${i + 1}`]}
      pcbX="-2.95mm" pcbY={`${(-2.2 + i * 0.4)}mm`} width="0.8mm" height="0.2mm" shape="rect" />)}
    {Array.from({ length: 12 }, (_, i) => <smtpad key={`t${i}`} portHints={[`${i + 13}`]}
      pcbX={`${(-2.2 + i * 0.4)}mm`} pcbY="2.95mm" width="0.2mm" height="0.8mm" shape="rect" />)}
    {Array.from({ length: 12 }, (_, i) => <smtpad key={`r${i}`} portHints={[`${i + 25}`]}
      pcbX="2.95mm" pcbY={`${(2.2 - i * 0.4)}mm`} width="0.8mm" height="0.2mm" shape="rect" />)}
    {Array.from({ length: 12 }, (_, i) => <smtpad key={`b${i}`} portHints={[`${i + 37}`]}
      pcbX={`${(2.2 - i * 0.4)}mm`} pcbY="-2.95mm" width="0.2mm" height="0.8mm" shape="rect" />)}
    <smtpad portHints={["49"]} pcbX="0mm" pcbY="0mm" width="4.6mm" height="4.6mm" shape="rect" />
  </footprint>
)

// Wurth native land pattern, in tscircuit +Y-up coordinates.
// Contacts 1..8, shell tabs 9/10; blank NPTH guides are mechanical only.
const Rj45Shielded = () => (
  <footprint>
    <platedhole portHints={["1"]} pcbX="0mm" pcbY="0mm"
      shape="circular_hole_with_rect_pad" holeDiameter="0.8mm"
      rectPadWidth="1.3mm" rectPadHeight="1.3mm" />
    {[[2, 1.02, -4], [3, 2.04, 0], [4, 3.06, -4], [5, 4.08, 0],
      [6, 5.10, -4], [7, 6.12, 0], [8, 7.14, -4]].map(([pin, x, y]) => (
      <platedhole key={pin} portHints={[`${pin}`]} pcbX={`${x}mm`} pcbY={`${y}mm`}
        shape="circle" outerDiameter="1.3mm" holeDiameter="0.8mm" />
    ))}
    {[[9, 10.97], [10, -3.83]].map(([pin, x]) => (
      <platedhole key={pin} portHints={[`${pin}`]} pcbX={`${x}mm`} pcbY="2.35mm"
        shape="oval" outerWidth="1.5mm" outerHeight="3mm" holeWidth="1mm" holeHeight="2mm" />
    ))}
    <hole pcbX="-3.28mm" pcbY="-0.7mm" diameter="3.18mm" />
    <hole pcbX="10.42mm" pcbY="-0.7mm" diameter="3.18mm" />
  </footprint>
)

const MicroFit2 = () => (
  <footprint>
    <platedhole portHints={["1"]} pcbX="0mm" pcbY="0mm"
      shape="circular_hole_with_rect_pad" holeDiameter="1.02mm"
      rectPadWidth="1.5mm" rectPadHeight="2.02mm" rectBorderRadius="0.25mm" />
    <platedhole portHints={["2"]} pcbX="3mm" pcbY="0mm" shape="oval"
      outerWidth="1.5mm" outerHeight="2.02mm" holeWidth="1.02mm" holeHeight="1.02mm" />
    <hole pcbX="1.5mm" pcbY="-4.32mm" diameter="3mm" />
  </footprint>
)

const Header2x6 = () => (
  <footprint>
    <platedhole portHints={["1"]} pcbX="0mm" pcbY="0mm"
      shape="circular_hole_with_rect_pad" holeDiameter="0.8mm"
      rectPadWidth="1.35mm" rectPadHeight="1.35mm" rectBorderRadius="0.18mm" />
    {Array.from({ length: 5 }, (_, j) => { const row = j + 1; return <platedhole key={`o${row}`} portHints={[`${row * 2 + 1}`]}
      pcbX="0mm" pcbY={`${row * 2}mm`} outerDiameter="1.35mm" holeDiameter="0.8mm" shape="circle" /> })}
    {Array.from({ length: 6 }, (_, row) => <platedhole key={`e${row}`} portHints={[`${row * 2 + 2}`]}
      pcbX="2mm" pcbY={`${row * 2}mm`} outerDiameter="1.35mm" holeDiameter="0.8mm" shape="circle" />)}
  </footprint>
)

const Vssop8 = () => (
  <footprint>
    {[1, 2, 3, 4].map((pin, i) => <smtpad key={`l${pin}`} portHints={[`${pin}`]}
      pcbX="-1.4mm" pcbY={`${(-0.75 + i * 0.5)}mm`} width="1.25mm" height="0.35mm" shape="rect" />)}
    {[5, 6, 7, 8].map((pin, i) => <smtpad key={`r${pin}`} portHints={[`${pin}`]}
      pcbX="1.4mm" pcbY={`${(0.75 - i * 0.5)}mm`} width="1.25mm" height="0.35mm" shape="rect" />)}
  </footprint>
)

const Ssop8 = () => (
  <footprint>
    {[1, 2, 3, 4].map((pin, i) => <smtpad key={`l${pin}`} portHints={[`${pin}`]}
      pcbX="-1.7mm" pcbY={`${(-0.975 + i * 0.65)}mm`} width="1.6mm" height="0.3mm" shape="rect" />)}
    {[5, 6, 7, 8].map((pin, i) => <smtpad key={`r${pin}`} portHints={[`${pin}`]}
      pcbX="1.7mm" pcbY={`${(0.975 - i * 0.65)}mm`} width="1.6mm" height="0.3mm" shape="rect" />)}
  </footprint>
)

const Soic8 = () => (
  <footprint>
    {[1, 2, 3, 4].map((pin, i) => <smtpad key={`l${pin}`} portHints={[`${pin}`]}
      pcbX="-2.475mm" pcbY={`${(-1.905 + i * 1.27)}mm`} width="1.95mm" height="0.6mm" shape="rect" />)}
    {[5, 6, 7, 8].map((pin, i) => <smtpad key={`r${pin}`} portHints={[`${pin}`]}
      pcbX="2.475mm" pcbY={`${(1.905 - i * 1.27)}mm`} width="1.95mm" height="0.6mm" shape="rect" />)}
  </footprint>
)

const PowerDi3333 = () => (
  <footprint>
    {[1, 2, 3, 4].map((pin, i) => <smtpad key={`s${pin}`} portHints={[`${pin}`]}
      pcbX="-1.5mm" pcbY={`${(-0.975 + i * 0.65)}mm`} width="0.7mm" height="0.42mm" shape="rect" />)}
    <smtpad portHints={["5"]} pcbX="0.455mm" pcbY="0mm" width="2.37mm" height="2.37mm" shape="rect" />
  </footprint>
)

const Tsot23_6 = () => (
  <footprint>
    {[1, 2, 3].map((pin, i) => <smtpad key={`l${pin}`} portHints={[`${pin}`]}
      pcbX="-1.1375mm" pcbY={`${(-0.95 + i * 0.95)}mm`} width="1.325mm" height="0.6mm" shape="rect" />)}
    {[4, 5, 6].map((pin, i) => <smtpad key={`r${pin}`} portHints={[`${pin}`]}
      pcbX="1.1375mm" pcbY={`${(0.95 - i * 0.95)}mm`} width="1.325mm" height="0.6mm" shape="rect" />)}
  </footprint>
)

const Sot23_5 = () => (
  <footprint>
    {[1, 2, 3].map((pin, i) => <smtpad key={`l${pin}`} portHints={[`${pin}`]}
      pcbX="-1.1375mm" pcbY={`${(-0.95 + i * 0.95)}mm`} width="1.325mm" height="0.6mm" shape="rect" />)}
    <smtpad portHints={["4"]} pcbX="1.1375mm" pcbY="0.95mm" width="1.325mm" height="0.6mm" shape="rect" />
    <smtpad portHints={["5"]} pcbX="1.1375mm" pcbY="-0.95mm" width="1.325mm" height="0.6mm" shape="rect" />
  </footprint>
)

const Sot553 = () => (
  <footprint>
    {[1, 2, 3].map((pin, i) => <smtpad key={`l${pin}`} portHints={[`${pin}`]}
      pcbX="-0.7125mm" pcbY={`${(-0.5 + i * 0.5)}mm`} width="0.675mm" height="0.35mm" shape="rect" />)}
    <smtpad portHints={["4"]} pcbX="0.7125mm" pcbY="0.5mm" width="0.675mm" height="0.35mm" shape="rect" />
    <smtpad portHints={["5"]} pcbX="0.7125mm" pcbY="-0.5mm" width="0.675mm" height="0.35mm" shape="rect" />
  </footprint>
)

// Exact standard-terminal Panasonic FK size-F land. The manufacturer table
// gives gap a=3.1 mm, pad length b=4.0 mm and pad width c=2.0 mm, hence
// centres +/-3.55 mm. Pad 1 is positive; this is not the vibration-proof land.
const PanasonicFkF = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-3.55mm" pcbY="0mm" width="4mm" height="2mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="3.55mm" pcbY="0mm" width="4mm" height="2mm" shape="rect" />
  </footprint>
)

const FilmCap5mm = () => (
  <footprint>
    <platedhole portHints={["1"]} pcbX="-2.5mm" pcbY="0mm"
      shape="circular_hole_with_rect_pad" holeDiameter="0.75mm"
      rectPadWidth="1.5mm" rectPadHeight="1.5mm" rectBorderRadius="0.2mm" />
    <platedhole portHints={["2"]} pcbX="2.5mm" pcbY="0mm"
      shape="circle" holeDiameter="0.75mm" outerDiameter="1.5mm" />
  </footprint>
)

// Exact pad centres and land size of KiCad's governed
// Capacitor_SMD:CP_Elec_4x5.8 module. Pad 1 is positive.
const Electrolytic4x5_8 = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-1.8mm" pcbY="0mm"
      width="2.6mm" height="1.6mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="1.8mm" pcbY="0mm"
      width="2.6mm" height="1.6mm" shape="rect" />
  </footprint>
)

const Pptc2920 = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-3.3875mm" pcbY="0mm"
      width="1.925mm" height="5.45mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="3.3875mm" pcbY="0mm"
      width="1.925mm" height="5.45mm" shape="rect" />
  </footprint>
)

const Smbj = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-2.15mm" pcbY="0mm" width="2.5mm" height="2.3mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="2.15mm" pcbY="0mm" width="2.5mm" height="2.3mm" shape="rect" />
  </footprint>
)

const Xgl4020 = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-1.185mm" pcbY="0mm" width="0.98mm" height="3.4mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="1.185mm" pcbY="0mm" width="0.98mm" height="3.4mm" shape="rect" />
  </footprint>
)

const Sot23 = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-0.95mm" pcbY="0.95mm" width="0.9mm" height="1.0mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="-0.95mm" pcbY="-0.95mm" width="0.9mm" height="1.0mm" shape="rect" />
    <smtpad portHints={["3"]} pcbX="0.95mm" pcbY="0mm" width="0.9mm" height="1.0mm" shape="rect" />
  </footprint>
)

// DS30896 Rev20-2 p.7 exact land; tscircuit Y-up, KiCad Y-down.
const Diodes2N7002K = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-1.00mm" pcbY="0.95mm" width="0.9mm" height="0.8mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="-1.00mm" pcbY="-0.95mm" width="0.9mm" height="0.8mm" shape="rect" />
    <smtpad portHints={["3"]} pcbX="1.00mm" pcbY="0mm" width="0.9mm" height="0.8mm" shape="rect" />
  </footprint>
)

const Port = ({ n, section, x, y }: any) => (
  <>
    <Chip name={`J${n}`} manufacturerPartNumber="615008160221" jlc=""
      schSectionName={section} schSheetName={sheetFor(section)} schX={`${x}mm`} schY={`${y}mm`}
      pinLabels={{ pin1: "12V_1", pin2: "GND_1", pin3: "12V_2", pin4: "AUDIO_N", pin5: "AUDIO_P", pin6: "GND_2", pin7: "12V_3", pin8: "GND_3", pin9: "SHIELD_S1", pin10: "SHIELD_S2" }}
      schPinArrangement={{ leftSide: [1, 3, 7, 2, 6, 8], rightSide: [5, 4, 9, 10] }}
      connections={{ pin1: N(`12V_POD${n}`), pin2: N("GND"), pin3: N(`12V_POD${n}`), pin4: N(`AUDIO_N${n}`), pin5: N(`AUDIO_P${n}`), pin6: N("GND"), pin7: N(`12V_POD${n}`), pin8: N("GND"), pin9: N("CHASSIS"), pin10: N("CHASSIS") }}
      footprint={<Rj45Shielded />} />
    <Chip name={`F${n}`} manufacturerPartNumber="1812L035/60MR" jlc="C3761431"
      schSectionName="Input and spoke power" schSheetName="spoke_power" schX={`${-14 + ((n - 1) % 4) * 11}mm`} schY={n <= 4 ? "-4mm" : "-10mm"}
      pinLabels={{ pin1: "IN", pin2: "OUT" }}
      connections={{ pin1: N("12V_PROTECTED"), pin2: N(`12V_POD${n}`) }} footprint={<Littelfuse1812L035 />} />
    <Chip name={`U_ESD${n}`} manufacturerPartNumber="TPD2E2U06DRLR" jlc="C1972959"
      schSectionName={section} schSheetName={sheetFor(section)} schX={`${x + 5}mm`} schY={`${y + 4}mm`}
      pinLabels={{ pin1: "NC1", pin2: "NC2", pin3: "IO1", pin4: "GND", pin5: "IO2" }}
      connections={{ pin3: N(`AUDIO_P${n}`), pin4: N("GND"), pin5: N(`AUDIO_N${n}`) }}
      footprint={<Sot553 />} />
  </>
)

// Exact primary land centers, shared with source-owned KiCad footprints.
const Wson = ({ pins, span, width, ep }: any) => (
  <footprint>
    {Array.from({length:pins}, (_,i) => {
      const p=i+1, left=p<=pins/2
      return <smtpad key={p} portHints={[`${p}`]}
        pcbX={`${pins===6 && p===1 ? -0.55 : (left ? -span/2 : span/2)}mm`}
        pcbY={`${left ? (pins/2-1)*0.25-i*0.5 : -(pins/2-1)*0.25+(i-pins/2)*0.5}mm`}
        width={`${pins===6 && p===1 ? 0.8 : width}mm`} height="0.25mm" shape="rect" />
    })}
    {ep && <smtpad portHints={[`${pins+1}`]} pcbX="0mm" pcbY="0mm" width={`${ep[0]}mm`} height={`${ep[1]}mm`} shape="rect" />}
  </footprint>
)

const AnalogChannel = ({ n, section, x, y, vmid }: any) => (
  <>
    <C2 name={`C_A${n}P`} value="1uF" a={`AUDIO_P${n}`} b={`BIAS_P${n}`} jlc="" mpn="R82DC4100DQ60J" footprint={<FilmCap5mm />} section={section} schX={`${x}mm`} schY={`${y + 4}mm`} />
    <C2 name={`C_A${n}N`} value="1uF" a={`AUDIO_N${n}`} b={`BIAS_N${n}`} jlc="" mpn="R82DC4100DQ60J" footprint={<FilmCap5mm />} section={section} schX={`${x}mm`} schY={`${y - 4}mm`} />
    <R2 name={`R_B${n}P`} value="100k" a={`BIAS_P${n}`} b={vmid} jlc="C60491" mpn="RC0402FR-07100KL" section={section} schX={`${x + 4}mm`} schY={`${y + 4}mm`} />
    <R2 name={`R_B${n}N`} value="100k" a={`BIAS_N${n}`} b={vmid} jlc="C60491" mpn="RC0402FR-07100KL" section={section} schX={`${x + 4}mm`} schY={`${y - 4}mm`} />
    {/* ADR0021: current limit is AFTER the bias tee; no guessed clamp drop. */}
    <R2 name={`R_IN${n}P`} value="10k" a={`BIAS_P${n}`} b={`AIN_P${n}`} jlc="C60490" mpn="RC0402FR-0710KL" section={section} schX={`${x + 6}mm`} schY={`${y + 4}mm`} />
    <R2 name={`R_IN${n}N`} value="10k" a={`BIAS_N${n}`} b={`AIN_N${n}`} jlc="C60490" mpn="RC0402FR-0710KL" section={section} schX={`${x + 6}mm`} schY={`${y - 4}mm`} />
    <Chip name={`U_AFE${n}`} manufacturerPartNumber="OPA2320AIDR" jlc="C2863402"
      schSectionName={section} schSheetName={sheetFor(section)} schX={`${x + 9}mm`} schY={`${y}mm`}
      pinLabels={{ pin1: "OUTA", pin2: "A_NEG", pin3: "A_POS", pin4: "VNEG", pin5: "B_POS", pin6: "B_NEG", pin7: "OUTB", pin8: "VPOS" }}
      schPinArrangement={{ leftSide: [3, 2, 5, 6], rightSide: [1, 7], topSide: [8], bottomSide: [4] }}
      connections={{ pin1: N(`OPA_P${n}`), pin2: N(`FB_P${n}`), pin3: N(`AIN_P${n}`), pin4: N("GND"), pin5: N(`AIN_N${n}`), pin6: N(`FB_N${n}`), pin7: N(`OPA_N${n}`), pin8: N("3V3_ADC") }}
      footprint={<Soic8 />} />
    <R2 name={`R_X${n}P`} value="300" a={`FB_P${n}`} b={`FILTER${n}P`} jlc="C138010" mpn="RC0402FR-07300RL" section={section} schX={`${x + 13}mm`} schY={`${y + 5}mm`} />
    <R2 name={`R_X${n}N`} value="300" a={`FB_N${n}`} b={`FILTER${n}N`} jlc="C138010" mpn="RC0402FR-07300RL" section={section} schX={`${x + 13}mm`} schY={`${y - 5}mm`} />
    <C2 name={`C_FB${n}P`} value="680pF" a={`FB_P${n}`} b={`OPA_P${n}`} jlc="C126514" mpn="GCM1555C1H681JA16D" section={section} schX={`${x + 11}mm`} schY={`${y + 6}mm`} />
    <C2 name={`C_FB${n}N`} value="680pF" a={`FB_N${n}`} b={`OPA_N${n}`} jlc="C126514" mpn="GCM1555C1H681JA16D" section={section} schX={`${x + 11}mm`} schY={`${y - 6}mm`} />
    <R2 name={`R_OUT${n}P`} value="10" a={`OPA_P${n}`} b={`FILTER${n}P`} jlc="C138066" mpn="RC0402FR-0710RL" section={section} schX={`${x + 16}mm`} schY={`${y + 3}mm`} />
    <R2 name={`R_OUT${n}N`} value="10" a={`OPA_N${n}`} b={`FILTER${n}N`} jlc="C138066" mpn="RC0402FR-0710RL" section={section} schX={`${x + 16}mm`} schY={`${y - 3}mm`} />
    {/* ADR0025: positive independent RC legs; no cross-leg stored-charge transfer. */}
    <C2 name={`C_FILTER${n}P1`} value="15nF" a={`FILTER${n}P`} b="GND" jlc="C97907" mpn="GRM2195C1H153JA01D" footprint="0805" section={section} schX={`${x + 20}mm`} schY={`${y + 3}mm`} />
    <C2 name={`C_FILTER${n}P2`} value="15nF" a={`FILTER${n}P`} b="GND" jlc="C97907" mpn="GRM2195C1H153JA01D" footprint="0805" section={section} schX={`${x + 21}mm`} schY={`${y + 3}mm`} />
    <C2 name={`C_FILTER${n}N1`} value="15nF" a={`FILTER${n}N`} b="GND" jlc="C97907" mpn="GRM2195C1H153JA01D" footprint="0805" section={section} schX={`${x + 20}mm`} schY={`${y + -3}mm`} />
    <C2 name={`C_FILTER${n}N2`} value="15nF" a={`FILTER${n}N`} b="GND" jlc="C97907" mpn="GRM2195C1H153JA01D" footprint="0805" section={section} schX={`${x + 21}mm`} schY={`${y + -3}mm`} />
    {/* Isolation follows the complete filter, including300ohm feedback pickup. */}
    <Chip name={`U_ISO${n}`} manufacturerPartNumber="TMUX2821DSGR" jlc="C53283916"
      schSectionName={section} schSheetName={sheetFor(section)} schX={`${x+29}mm`} schY={`${y}mm`}
      pinLabels={{pin1:"S1",pin2:"D1",pin3:"SEL2",pin4:"GND",pin5:"S2",pin6:"D2",pin7:"SEL1",pin8:"VDD",pin9:"EP"}}
      connections={{pin1:N(`FILTER${n}P`),pin2:N(`ADC${n}P`),pin3:N("AUDIO_EN"),pin4:N("GND"),pin5:N(`FILTER${n}N`),pin6:N(`ADC${n}N`),pin7:N("AUDIO_EN"),pin8:N("5V_LDO_HOLD"),pin9:N("GND")}}
      footprint={<Wson pins={8} span={1.9} width={0.5} ep={[0.9,1.6]} />} />
    {["P","N"].map((leg,i)=>[
<R2 key={`r${leg}`} name={`R_ADC_PD${n}${leg}`} value="10k" a={`ADC${n}${leg}`} b="GND" jlc="C60490" mpn="RC0402FR-0710KL" section={section} schX={`${x+37}mm`} schY={`${y+4-i*8}mm`} />,
      <C2 key={`c${leg}`} name={`C_ADC_CM${n}${leg}`} value="1nF" a={`ADC${n}${leg}`} b="GND" jlc="C76947" mpn="GRM1555C1H102JA01D" section={section} schX={`${x+42}mm`} schY={`${y+4-i*8}mm`} />
    ])}
    <C2 name={`C_ISO${n}`} value="100nF" a="5V_LDO_HOLD" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" section={section} schX={`${x+29}mm`} schY={`${y-6}mm`} />
    <C2 name={`C_OPA${n}`} value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" section={section} schX={`${x + 9}mm`} schY={`${y - 8}mm`} />
  </>
)

export default () => (
  // The tscircuit PCB canvas is intentionally generous so its non-authoritative
  // auto-packer cannot emit overlap diagnostics. The governed 150 x 100 mm
  // physical board is generated only from 03_src/floorplan.yaml.
  <board width="8000mm" height="2000mm" routingDisabled schMaxTraceDistance={20}>
    {sheets.map(([name,title],i) => <schematicsheet key={name} name={name} displayName={title} sheetIndex={i+1} />)}
    <SchematicWires />

    <Port n={1} section="Channels 1-4 analog" x={-12} y={21} />
    <Port n={2} section="Channels 1-4 analog" x={-12} y={7} />
    <Port n={3} section="Channels 1-4 analog" x={-12} y={-7} />
    <Port n={4} section="Channels 1-4 analog" x={-12} y={-21} />
    <Port n={5} section="Channels 5-8 analog" x={-12} y={21} />
    <Port n={6} section="Channels 5-8 analog" x={-12} y={7} />
    <Port n={7} section="Channels 5-8 analog" x={-12} y={-7} />
    <Port n={8} section="Channels 5-8 analog" x={-12} y={-21} />

    <AnalogChannel n={1} section="Channels 1-4 analog" x={0} y={21} vmid="VMID1_EXT" />
    <AnalogChannel n={2} section="Channels 1-4 analog" x={0} y={7} vmid="VMID1_EXT" />
    <AnalogChannel n={3} section="Channels 1-4 analog" x={0} y={-7} vmid="VMID1_EXT" />
    <AnalogChannel n={4} section="Channels 1-4 analog" x={0} y={-21} vmid="VMID1_EXT" />
    <AnalogChannel n={5} section="Channels 5-8 analog" x={0} y={21} vmid="VMID2_EXT" />
    <AnalogChannel n={6} section="Channels 5-8 analog" x={0} y={7} vmid="VMID2_EXT" />
    <AnalogChannel n={7} section="Channels 5-8 analog" x={0} y={-7} vmid="VMID2_EXT" />
    <AnalogChannel n={8} section="Channels 5-8 analog" x={0} y={-21} vmid="VMID2_EXT" />

    <Chip name="J9" manufacturerPartNumber="43650-0200" jlc=""
      schSectionName="Input and spoke power" schSheetName="spoke_power" schX="-24mm" schY="15mm"
      pinLabels={{ pin1: "12V_IN", pin2: "GND" }} connections={{ pin1: N("12V_IN"), pin2: N("GND") }} footprint={<MicroFit2 />} />
    <Chip name="F_IN" manufacturerPartNumber="2920L260/33DR" jlc="C22870534"
      schSectionName="Input and spoke power" schSheetName="spoke_power" schX="-17mm" schY="15mm"
      pinLabels={{ pin1: "IN", pin2: "OUT" }} connections={{ pin1: N("12V_IN"), pin2: N("12V_FUSED") }} footprint={<Pptc2920 />} />
    <Chip name="Q_IN" manufacturerPartNumber="DMP6023LFG-13" jlc="C780842"
      schSectionName="Input and spoke power" schSheetName="spoke_power" schX="-9mm" schY="15mm"
      pinLabels={{ pin1: "S1", pin2: "S2", pin3: "S3", pin4: "G", pin5: "D5_8_COMMON" }}
      schPinArrangement={{ leftSide: [5], rightSide: [1, 2, 3], bottomSide: [4] }}
      connections={{ pin1: N("12V_PROTECTED"), pin2: N("12V_PROTECTED"), pin3: N("12V_PROTECTED"), pin4: N("Q_IN_GATE"), pin5: N("12V_FUSED") }}
      footprint={<PowerDi3333 />} />
    <R2 name="R_QIN_G" value="100k" a="Q_IN_GATE" b="GND" jlc="C60491" mpn="RC0402FR-07100KL" section="Input and spoke power" schX="-3mm" schY="11mm" />
    <Chip name="D_QIN_GS" manufacturerPartNumber="BZT52C12-7-F" jlc="C124196"
      schSectionName="Input and spoke power" schSheetName="spoke_power" schX="0mm" schY="11mm"
      pinLabels={{ pin1: "K", pin2: "A" }} connections={{ pin1: N("12V_PROTECTED"), pin2: N("Q_IN_GATE") }} footprint="sod123" />
    <Chip name="D_IN" manufacturerPartNumber="SMBJ15A" jlc="C83846"
      schSectionName="Input and spoke power" schSheetName="spoke_power" schX="1mm" schY="15mm"
      pinLabels={{ pin1: "K", pin2: "A" }} connections={{ pin1: N("12V_PROTECTED"), pin2: N("GND") }} footprint={<Smbj />} />
    {/* ADR0022: isolate VIN and ALL three local ceramics from the spoke bus. */}
    <Chip name="D_BUCK_IN" manufacturerPartNumber="US1B-13-F" jlc="C154439"
      schSectionName="Input and spoke power" schSheetName="spoke_power" schX="-3mm" schY="7mm"
      pinLabels={{pin1:"K",pin2:"A"}} connections={{pin1:N("12V_BUCK_IN"),pin2:N("12V_PROTECTED")}}
      footprint={<footprint><smtpad portHints={["1"]} pcbX="-2mm" pcbY="0mm" width="2.5mm" height="1.8mm" shape="rect" /><smtpad portHints={["2"]} pcbX="2mm" pcbY="0mm" width="2.5mm" height="1.8mm" shape="rect" /></footprint>} />
    <C2 name="C_BUCK_IN" value="10uF" a="12V_BUCK_IN" b="GND" jlc="C597579" mpn="12105C106K4Z2A" footprint="1210" section="Input and spoke power" schX="4mm" schY="15mm" />
    <C2 name="C_BUCK_IN2" value="10uF" a="12V_BUCK_IN" b="GND" jlc="C597579" mpn="12105C106K4Z2A" footprint="1210" section="Input and spoke power" schX="-17mm" schY="7mm" />
    <C2 name="C_BUCK_IN3" value="10uF" a="12V_BUCK_IN" b="GND" jlc="C597579" mpn="12105C106K4Z2A" footprint="1210" section="Input and spoke power" schX="-10mm" schY="7mm" />
    <Chip name="U_BUCK" manufacturerPartNumber="AP63205WU-7" jlc="C2071056"
      schSectionName="Input and spoke power" schSheetName="spoke_power" schX="7mm" schY="15mm"
      pinLabels={{ pin1: "FB", pin2: "EN", pin3: "VIN", pin4: "GND", pin5: "SW", pin6: "BST" }}
      connections={{ pin1: N("5V_BUCK"), pin2: N("12V_BUCK_IN"), pin3: N("12V_BUCK_IN"), pin4: N("GND"), pin5: N("BUCK_SW"), pin6: N("BUCK_BST") }}
      footprint={<Tsot23_6 />} />
    <C2 name="C_BUCK_BST" value="100nF" a="BUCK_BST" b="BUCK_SW" jlc="C1525" mpn="CL05B104KO5NNNC" section="Input and spoke power" schX="11mm" schY="18mm" />
    <Chip name="L_BUCK" manufacturerPartNumber="XGL4020-332MEC" jlc="C6937839"
      schSectionName="Input and spoke power" schSheetName="spoke_power" schX="12mm" schY="13mm"
      pinLabels={{ pin1: "SW", pin2: "OUT" }} connections={{ pin1: N("BUCK_SW"), pin2: N("5V_BUCK") }} footprint={<Xgl4020 />} />
    <C2 name="C_BUCK_O1" value="47uF" a="5V_BUCK" b="GND" jlc="C84494" mpn="GRM32ER71A476KE15L" footprint="1210" section="Input and spoke power" schX="16mm" schY="16mm" />
    <C2 name="C_BUCK_O2" value="47uF" a="5V_BUCK" b="GND" jlc="C84494" mpn="GRM32ER71A476KE15L" footprint="1210" section="Input and spoke power" schX="19mm" schY="16mm" />
    <C2 name="C_BUCK_O3" value="47uF" a="5V_BUCK" b="GND" jlc="C84494" mpn="GRM32ER71A476KE15L" footprint="1210" section="Input and spoke power" schX="22mm" schY="16mm" />
    {/* ADR0025: one ADC/amplifier domain; two local output ceramics and a passive 200 ohm rail sink. */}
    <C2 name="C_OPA_BULK" value="47uF" a="3V3_ADC" b="GND" jlc="C84494" mpn="GRM32ER71A476KE15L" footprint="1210" section="Input and spoke power" schX="20mm" schY="11mm" />
    <R2 name="R_OPA_BLEED1" value="100" a="3V3_ADC" b="OPA_BLEED_A" jlc="C106232" mpn="RC0402FR-07100RL" section="Input and spoke power" schX="24mm" schY="7mm" />
    <R2 name="R_OPA_BLEED2" value="100" a="OPA_BLEED_A" b="GND" jlc="C106232" mpn="RC0402FR-07100RL" section="Input and spoke power" schX="24mm" schY="3mm" />
    {/* ADR0009: isolate input energy, precharge before enabling, break audio before dump. */}
    <Chip name="U_LDO" manufacturerPartNumber="LT3041ADE#TRPBF" jlc="C7452883" schSectionName="Input and spoke power" schSheetName="spoke_power" schX="12mm" schY="-12mm"
      pinLabels={{pin1:"IN1",pin2:"IN2",pin3:"IN3",pin4:"VIOC_NC",pin5:"EN_UV",pin6:"PG_NC",pin7:"ILIM",pin8:"PGFB",pin9:"SET",pin10:"GND1",pin11:"GND2",pin12:"OUTS",pin13:"OUT1",pin14:"OUT2",pin15:"EP"}}
      connections={{pin1:N("5V_LDO_HOLD"),pin2:N("5V_LDO_HOLD"),pin3:N("5V_LDO_HOLD"),pin5:N("LDO_EN"),pin7:N("GND"),pin8:N("5V_LDO_HOLD"),pin9:N("LDO_NR"),pin10:N("GND"),pin11:N("GND"),pin12:N("3V3_ADC"),pin13:N("3V3_ADC"),pin14:N("3V3_ADC"),pin15:N("GND")}}
      footprint={<Wson pins={14} span={2.9} width={0.7} ep={[1.7,3.3]} />} />
    <Chip name="D_HOLD" manufacturerPartNumber="B340A-13-F" jlc="C85098" schSectionName="Input and spoke power" schSheetName="spoke_power" schX="-24mm" schY="-8mm"
      pinLabels={{pin1:"K",pin2:"A"}} connections={{pin1:N("5V_LDO_FEED"),pin2:N("5V_BUCK")}} footprint="sma" />
    <Chip name="Q_PRE" manufacturerPartNumber="AO3401A" jlc="C15127" schSectionName="Input and spoke power" schSheetName="spoke_power" schX="-8mm" schY="-8mm"
      pinLabels={{pin1:"G",pin2:"S",pin3:"D"}} connections={{pin1:N("PRE_GATE"),pin2:N("5V_LDO_FEED"),pin3:N("5V_LDO_HOLD")}} footprint={<Sot23 />} />
    <Chip name="Q_PRE_EN" manufacturerPartNumber="2N7002K-7" jlc="C85047" schSectionName="Input and spoke power" schSheetName="spoke_power" schX="-8mm" schY="-17mm"
      pinLabels={{pin1:"G",pin2:"S",pin3:"D"}} connections={{pin1:N("PWR_EN"),pin2:N("GND"),pin3:N("PRE_GATE")}} footprint={<Diodes2N7002K />} />
    <R2 name="R_PRE" value="22" a="5V_LDO_FEED" b="5V_LDO_HOLD" mpn="CRCW120622R0FKEAHP" jlc="C844025" footprint="1206" section="Input and spoke power" schX="-16mm" schY="-8mm" />
    <R2 name="R_PRE_G" value="100k" a="PRE_GATE" b="5V_LDO_FEED" mpn="RC0402FR-07100KL" jlc="C60491" footprint="0402" section="Input and spoke power" schX="-16mm" schY="-17mm" />
    <C2 name="C_HOLD1" value="470uF" a="5V_LDO_HOLD" b="GND" mpn="EEEFK1A471P" jlc="C178530" footprint={<PanasonicFkF />} polarized section="Input and spoke power" schX="-16mm" schY="-25mm" />
    <C2 name="C_HOLD2" value="470uF" a="5V_LDO_HOLD" b="GND" mpn="EEEFK1A471P" jlc="C178530" footprint={<PanasonicFkF />} polarized section="Input and spoke power" schX="-8mm" schY="-25mm" />
    <C2 name="C_LDO_IN" value="47uF" a="5V_LDO_HOLD" b="GND" mpn="GRM32ER71A476KE15L" jlc="C84494" footprint="1210" section="Input and spoke power" schX="0mm" schY="-20mm" />
    <C2 name="C_LDO_OUT" value="47uF" a="3V3_ADC" b="GND" mpn="GRM32ER71A476KE15L" jlc="C84494" footprint="1210" section="Input and spoke power" schX="22mm" schY="-20mm" />
    <C2 name="C_LDO_NR4" value="1nF" a="LDO_NR" b="GND" mpn="GRM1555C1H102JA01D" jlc="C76947" section="Input and spoke power" schX="26mm" schY="-26mm" />
    <C2 name="C_LDO_NR5" value="1nF" a="LDO_NR" b="GND" mpn="GRM1555C1H102JA01D" jlc="C76947" section="Input and spoke power" schX="31mm" schY="-26mm" />
    <R2 name="R_LDO_SET" value="33k" a="LDO_NR" b="GND" mpn="RT0603BRD0733KL" jlc="C705768" footprint="0603" section="Input and spoke power" schX="28mm" schY="-8mm" />
    <Chip name="U_PWR" manufacturerPartNumber="TPS389001DSER" jlc="C1509297" schSectionName="Input and spoke power" schSheetName="spoke_power" schX="-16mm" schY="-38mm"
      pinLabels={{pin1:"SENSE",pin2:"GND",pin3:"MR_N",pin4:"VDD",pin5:"CT",pin6:"RESET_N"}}
      connections={{pin1:N("PWR_SENSE"),pin2:N("GND"),pin3:N("5V_LDO_HOLD"),pin4:N("5V_LDO_HOLD"),pin5:N("PWR_CT"),pin6:N("PWR_EN")}}
      footprint={<Wson pins={6} span={1.2} width={0.7} />} />
    <C2 name="C_PWR_CT" value="1uF" a="PWR_CT" b="GND" mpn="C0603C105K4RACTU" jlc="C2167386" footprint="0603" section="Input and spoke power" schX="-16mm" schY="-47mm" />
    <C2 name="C_PWR" value="100nF" a="5V_LDO_HOLD" b="GND" mpn="CL05B104KO5NNNC" jlc="C1525" footprint="0402" section="Input and spoke power" schX="-21mm" schY="-47mm" />
    <R2 name="R_PWR_PU" value="10k" a="5V_LDO_HOLD" b="PWR_EN" mpn="RC0402FR-0710KL" jlc="C60490" footprint="0402" section="Input and spoke power" schX="-9mm" schY="-43mm" />
    <Chip name="U_AUDIO" manufacturerPartNumber="TPS389001DSER" jlc="C1509297" schSectionName="Input and spoke power" schSheetName="spoke_power" schX="12mm" schY="-38mm"
      pinLabels={{pin1:"SENSE",pin2:"GND",pin3:"MR_N",pin4:"VDD",pin5:"CT",pin6:"RESET_N"}}
      connections={{pin1:N("ADC_SENSE"),pin2:N("GND"),pin3:N("PWR_EN"),pin4:N("5V_LDO_HOLD"),pin5:N("AUDIO_CT"),pin6:N("AUDIO_EN")}}
      footprint={<Wson pins={6} span={1.2} width={0.7} />} />
    <C2 name="C_AUDIO_CT1" value="1uF" a="AUDIO_CT" b="GND" mpn="C0603C105K4RACTU" jlc="C2167386" footprint="0603" section="Input and spoke power" schX="12mm" schY="-47mm" />
    <C2 name="C_AUDIO" value="100nF" a="5V_LDO_HOLD" b="GND" mpn="CL05B104KO5NNNC" jlc="C1525" footprint="0402" section="Input and spoke power" schX="7mm" schY="-47mm" />
    <R2 name="R_AUDIO_PU" value="10k" a="5V_LDO_HOLD" b="AUDIO_EN" mpn="RC0402FR-0710KL" jlc="C60490" footprint="0402" section="Input and spoke power" schX="19mm" schY="-43mm" />
    <C2 name="C_AUDIO_CT2" value="1uF" a="AUDIO_CT" b="GND" mpn="C0603C105K4RACTU" jlc="C2167386" footprint="0603" section="Input and spoke power" schX="18mm" schY="-47mm" />
    <R2 name="R_PWR_TOP" value="30.9k" a="5V_BUCK" b="PWR_SENSE" mpn="RT0603BRD0730K9L" jlc="C861313" footprint={<YageoRT0603 />} section="Input and spoke power" schX="-25mm" schY="-34mm" />
    <R2 name="R_PWR_BOT" value="10k" a="PWR_SENSE" b="GND" mpn="RT0603BRD0710KL" jlc="C95204" footprint="0603" section="Input and spoke power" schX="-25mm" schY="-40mm" />
    <R2 name="R_ADC_TOP" value="17.4k" a="3V3_ADC" b="ADC_SENSE" mpn="RT0603BRD0717K4L" jlc="C861167" footprint="0603" section="Input and spoke power" schX="2mm" schY="-34mm" />
    <R2 name="R_ADC_BOT" value="10k" a="ADC_SENSE" b="GND" mpn="RT0603BRD0710KL" jlc="C95204" footprint="0603" section="Input and spoke power" schX="2mm" schY="-40mm" />
    <Chip name="U_DUMP" manufacturerPartNumber="74LVC1G14GV,125" jlc="C131093" schSectionName="Input and spoke power" schSheetName="spoke_power" schX="-8mm" schY="-58mm"
      pinLabels={{pin1:"NC",pin2:"A_SCHMITT",pin3:"GND",pin4:"Y",pin5:"VCC"}} connections={{pin2:N("DUMP_RC"),pin3:N("GND"),pin4:N("DUMP_GATE"),pin5:N("5V_LDO_HOLD")}} footprint={<Sot23_5 />} />
    <C2 name="C_DUMP_LOGIC" value="100nF" a="5V_LDO_HOLD" b="GND" mpn="CL05B104KO5NNNC" jlc="C1525" footprint="0402" section="Input and spoke power" schX="-8mm" schY="-65mm" />
    <Chip name="U_LDO_EN" manufacturerPartNumber="74LVC1G14GV,125" jlc="C131093" schSectionName="Input and spoke power" schSheetName="spoke_power" schX="4mm" schY="-58mm"
      pinLabels={{pin1:"NC",pin2:"A_SCHMITT",pin3:"GND",pin4:"Y",pin5:"VCC"}} connections={{pin2:N("DUMP_GATE"),pin3:N("GND"),pin4:N("LDO_EN"),pin5:N("5V_LDO_HOLD")}} footprint={<Sot23_5 />} />
    <C2 name="C_LDO_EN" value="100nF" a="5V_LDO_HOLD" b="GND" mpn="CL05B104KO5NNNC" jlc="C1525" footprint="0402" section="Input and spoke power" schX="4mm" schY="-65mm" />
    <R2 name="R_DUMP_TIME1" value="100k" a="PWR_EN" b="DUMP_RC" mpn="RC0402FR-07100KL" jlc="C60491" footprint="0402" section="Input and spoke power" schX="-24mm" schY="-59mm" />
    <R2 name="R_DUMP_TIME2" value="100k" a="PWR_EN" b="DUMP_RC" mpn="RC0402FR-07100KL" jlc="C60491" footprint="0402" section="Input and spoke power" schX="-24mm" schY="-64mm" />
    <C2 name="C_DUMP_TIME" value="15nF" a="DUMP_RC" b="GND" mpn="GRM2195C1H153JA01D" jlc="C97907" footprint="0805" section="Input and spoke power" schX="-16mm" schY="-65mm" />
    <Chip name="Q_DUMP" manufacturerPartNumber="AO3400A" jlc="C20917" schSectionName="Input and spoke power" schSheetName="spoke_power" schX="20mm" schY="-58mm"
      pinLabels={{pin1:"G",pin2:"S",pin3:"D"}} connections={{pin1:N("DUMP_GATE"),pin2:N("GND"),pin3:N("ADC_DUMP")}} footprint={<Sot23 />} />
    <R2 name="R_DUMP" value="1" a="3V3_ADC" b="ADC_DUMP" mpn="CRCW12061R00FKEAHP" jlc="C844653" footprint="1206" section="Input and spoke power" schX="27mm" schY="-53mm" />
    <R2 name="R_DUMP_PD" value="100k" a="DUMP_GATE" b="GND" mpn="RC0402FR-07100KL" jlc="C60491" footprint="0402" section="Input and spoke power" schX="27mm" schY="-65mm" />
    <R2 name="R_AUDIO_PD" value="100k" a="AUDIO_EN" b="GND" mpn="RC0402FR-07100KL" jlc="C60491" footprint="0402" section="Input and spoke power" schX="25mm" schY="-42mm" />

    {/* ADR0025: passive external half-supply bias feeds the high-impedance
        noninverting channel inputs. Each channel still buffers its ADC input;
        no retained VMID reservoir can back-drive an unpowered reference output.
        ADC_VMID1/2 remain separately decoupled and are not bias sources. */}
    {[1, 2].map((n) => <group key={`external-vmid-${n}`}>
      <R2 name={`R_VMID${n}_TOP`} value="1k" a="3V3_ADC" b={`VMID${n}_EXT`} jlc="C110776" mpn="RT0603BRD071KL" footprint="0603" section="Reference buffers and filters" schX="-40mm" schY={`${27 - n * 12}mm`} />
      <R2 name={`R_VMID${n}_BOT`} value="1k" a={`VMID${n}_EXT`} b="GND" jlc="C110776" mpn="RT0603BRD071KL" footprint="0603" section="Reference buffers and filters" schX="-29mm" schY={`${27 - n * 12}mm`} />
      <C2 name={`C_VMID${n}_EXT_10U`} value="10uF" a={`VMID${n}_EXT`} b="GND" jlc="C2167576" mpn="C0805C106K8RACTU" footprint="0805" section="Reference buffers and filters" schX="-40mm" schY={`${22 - n * 12}mm`} />
      <C2 name={`C_VMID${n}_EXT_1U`} value="1uF" a={`VMID${n}_EXT`} b="GND" jlc="C2167386" mpn="C0603C105K4RACTU" footprint="0603" section="Reference buffers and filters" schX="-29mm" schY={`${22 - n * 12}mm`} />
    </group>)}

    <Chip name="U_ADC" manufacturerPartNumber="CS5308P-DN" jlc="C42457798"
      schSectionName="ADC references and mode" schSheetName="adc" schX="0mm" schY="0mm" schPinStyle={spacedPins(49)} schWidth="5mm"
      pinLabels={{
        pin1: "ADC_VMID1", pin2: "CONFIG1", pin3: "CONFIG2", pin4: "CONFIG3", pin5: "VDD_A1", pin6: "GND_A1", pin7: "LDO_A_FILT", pin8: "GND_A2", pin9: "VDD_A2", pin10: "CONFIG4", pin11: "CONFIG5", pin12: "ADC_VMID2",
        pin13: "IN5N", pin14: "IN5P", pin15: "IN6N", pin16: "IN6P", pin17: "ADC_FILT2N", pin18: "ADC_FILT2P", pin19: "IN7N", pin20: "IN7P", pin21: "IN8N", pin22: "IN8P", pin23: "RESET", pin24: "ASP_FSYNC", pin25: "ASP_DOUT1", pin26: "ASP_DOUT2_NC", pin27: "ASP_DOUT3_NC", pin28: "ASP_DOUT4_NC", pin29: "ASP_BCLK", pin30: "GND_D", pin31: "VDD_IO", pin32: "LDO_D_FILT", pin33: "VDD_D", pin34: "MCLK", pin35: "SPI_SDO_I2C_SCL", pin36: "SPI_SCK", pin37: "SPI_SDI_I2C_SDA", pin38: "SPI_CS", pin39: "IN1N", pin40: "IN1P", pin41: "IN2N", pin42: "IN2P", pin43: "ADC_FILT1P", pin44: "ADC_FILT1N", pin45: "IN3N", pin46: "IN3P", pin47: "IN4N", pin48: "IN4P", pin49: "EP_GND",
      }}
      connections={{
        pin1: N("VMID1"), pin2: N("CFG1"), pin3: N("CFG2"), pin4: N("GND"), pin5: N("3V3_ADC"), pin6: N("GND"), pin7: N("LDO_A_FILT"), pin8: N("GND"), pin9: N("3V3_ADC"), pin10: N("CFG4"), pin11: N("CFG5"), pin12: N("VMID2"),
        pin13: N(adcInputNet(5, "N")), pin14: N(adcInputNet(5, "P")), pin15: N(adcInputNet(6, "N")), pin16: N(adcInputNet(6, "P")), pin17: N("GND"), pin18: N("FILT2P"), pin19: N(adcInputNet(7, "N")), pin20: N(adcInputNet(7, "P")), pin21: N(adcInputNet(8, "N")), pin22: N(adcInputNet(8, "P")), pin23: N("ADC_RESET_N"), pin24: N("ADC_FSYNC"), pin25: N("TDM_RAW"), pin29: N("ADC_BCLK"), pin30: N("GND"), pin31: N("3V3_ADC"), pin32: N("LDO_D_FILT"), pin33: N("LDO_D_FILT"), pin34: N("ADC_MCLK"), pin35: N("GND"), pin36: N("GND"), pin37: N("GND"), pin38: N("3V3_ADC"), pin39: N(adcInputNet(1, "N")), pin40: N(adcInputNet(1, "P")), pin41: N(adcInputNet(2, "N")), pin42: N(adcInputNet(2, "P")), pin43: N("FILT1P"), pin44: N("GND"), pin45: N(adcInputNet(3, "N")), pin46: N(adcInputNet(3, "P")), pin47: N(adcInputNet(4, "N")), pin48: N(adcInputNet(4, "P")), pin49: N("GND"),
      }} footprint={<Qfn48 />} />

    <R2 name="R_CFG1" value="4.7k" a="CFG1" b="GND" jlc="C105871" mpn="RC0402FR-074K7L" section="ADC references and mode" schX="-14mm" schY="-16mm" />
    <R2 name="R_CFG2" value="0" a="CFG2" b="3V3_ADC" jlc="C106231" mpn="RC0402FR-070RL" section="ADC references and mode" schX="-4mm" schY="-16mm" />
    <R2 name="R_CFG4" value="4.7k" a="CFG4" b="3V3_ADC" jlc="C105871" mpn="RC0402FR-074K7L" section="ADC references and mode" schX="6mm" schY="-16mm" />
    <R2 name="R_CFG5" value="100k" a="CFG5" b="GND" jlc="C60491" mpn="RC0402FR-07100KL" section="ADC references and mode" schX="16mm" schY="-16mm" />
    <R2 name="R_FILT1P" value="1" a="3V3_ADC" b="FILT1P" footprint="1206" jlc="C844653" mpn="CRCW12061R00FKEAHP" section="Reference buffers and filters" schX="-18mm" schY="-11mm" />
    <R2 name="R_FILT2P" value="1" a="3V3_ADC" b="FILT2P" footprint="1206" jlc="C844653" mpn="CRCW12061R00FKEAHP" section="Reference buffers and filters" schX="7mm" schY="-11mm" />
    <C2 name="C_FILT1_470U" value="470uF" a="FILT1P" b="GND" jlc="C178530" mpn="EEEFK1A471P" footprint={<PanasonicFkF />} polarized section="Reference buffers and filters" schX="-8mm" schY="-11mm" />
    <C2 name="C_FILT1_10U" value="10uF" a="FILT1P" b="GND" jlc="C2167576" mpn="C0805C106K8RACTU" footprint="0805" section="Reference buffers and filters" schX="-8mm" schY="-15mm" />
    <C2 name="C_FILT1_1U" value="1uF" a="FILT1P" b="GND" jlc="C2167386" mpn="C0603C105K4RACTU" footprint="0603" section="Reference buffers and filters" schX="-8mm" schY="-19mm" />
    <C2 name="C_FILT2_470U" value="470uF" a="FILT2P" b="GND" jlc="C178530" mpn="EEEFK1A471P" footprint={<PanasonicFkF />} polarized section="Reference buffers and filters" schX="17mm" schY="-11mm" />
    <C2 name="C_FILT2_10U" value="10uF" a="FILT2P" b="GND" jlc="C2167576" mpn="C0805C106K8RACTU" footprint="0805" section="Reference buffers and filters" schX="17mm" schY="-15mm" />
    <C2 name="C_FILT2_1U" value="1uF" a="FILT2P" b="GND" jlc="C2167386" mpn="C0603C105K4RACTU" footprint="0603" section="Reference buffers and filters" schX="17mm" schY="-19mm" />
    <C2 name="C_VMID1_4U7" value="4.7uF" a="VMID1" b="GND" jlc="C389010" mpn="GRM188Z71C475KE21D" footprint="0603" section="Reference buffers and filters" schX="-18mm" schY="14mm" />
    <C2 name="C_VMID1_470N" value="470nF" a="VMID1" b="GND" jlc="C318640" mpn="CL10B474KA8NFNC" footprint="0603" section="Reference buffers and filters" schX="-18mm" schY="10mm" />
    <C2 name="C_VMID2_4U7" value="4.7uF" a="VMID2" b="GND" jlc="C389010" mpn="GRM188Z71C475KE21D" footprint="0603" section="Reference buffers and filters" schX="-18mm" schY="3mm" />
    <C2 name="C_VMID2_470N" value="470nF" a="VMID2" b="GND" jlc="C318640" mpn="CL10B474KA8NFNC" footprint="0603" section="Reference buffers and filters" schX="-18mm" schY="-1mm" />
    <C2 name="C_LDO_A" value="4.7uF" a="LDO_A_FILT" b="GND" jlc="C389010" mpn="GRM188Z71C475KE21D" footprint="0603" section="ADC references and mode" schX="22mm" schY="8mm" />
    <C2 name="C_LDO_D" value="4.7uF" a="LDO_D_FILT" b="GND" jlc="C389010" mpn="GRM188Z71C475KE21D" footprint="0603" section="ADC references and mode" schX="32mm" schY="8mm" />
    <C2 name="C_VDDA1_4U7" value="4.7uF" a="3V3_ADC" b="GND" jlc="C19666" mpn="CL10A475KO8NNNC" footprint="0603" section="ADC references and mode" schX="22mm" schY="2mm" />
    <C2 name="C_VDDA1_10N" value="10nF" a="3V3_ADC" b="GND" jlc="C15195" mpn="CL05B103KB5NNNC" section="ADC references and mode" schX="22mm" schY="-4mm" />
    <C2 name="C_VDDA2_4U7" value="4.7uF" a="3V3_ADC" b="GND" jlc="C19666" mpn="CL10A475KO8NNNC" footprint="0603" section="ADC references and mode" schX="32mm" schY="2mm" />
    <C2 name="C_VDDA2_10N" value="10nF" a="3V3_ADC" b="GND" jlc="C15195" mpn="CL05B103KB5NNNC" section="ADC references and mode" schX="32mm" schY="-4mm" />
    <C2 name="C_VDDIO" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" section="ADC references and mode" schX="22mm" schY="-10mm" />

    <Chip name="J10" manufacturerPartNumber="TMM-106-01-L-D" jlc=""
      schSectionName="TDM clocks and reset" schSheetName="digital" schX="-12mm" schY="10mm"
      pinLabels={{ pin1: "NC1", pin2: "TDM_IN_1_8", pin3: "NC3", pin4: "NC4", pin5: "NC5", pin6: "NC6", pin7: "NC7", pin8: "NC8", pin9: "MCLK_OUT", pin10: "BCLK_OUT", pin11: "GND", pin12: "FSYNC_OUT" }}
      connections={{ pin2: N("ADC_TDM"), pin9: N("MCH_MCLK"), pin10: N("MCH_BCLK"), pin11: N("GND"), pin12: N("MCH_FSYNC") }} footprint={<Header2x6 />} />
    <Chip name="J11" manufacturerPartNumber="TMM-106-01-L-D" jlc=""
      schSectionName="TDM clocks and reset" schSheetName="digital" schX="-12mm" schY="3mm"
      pinLabels={{ pin1: "GND", pin2: "MCH_3V3_SENSE", pin3: "NC3", pin4: "NC4", pin5: "NC5", pin6: "NC6", pin7: "NC7", pin8: "NC8", pin9: "NC9", pin10: "NC10", pin11: "NC11", pin12: "NC12" }}
      connections={{ pin1: N("GND"), pin2: N("MCH_3V3_SENSE") }} footprint={<Header2x6 />} />
    <Chip name="U_CLK" manufacturerPartNumber="SN74LVC3G34DCUR" jlc="C130024"
      schSectionName="TDM clocks and reset" schSheetName="digital" schX="-4mm" schY="10mm"
      pinLabels={{ pin1: "1A", pin2: "3Y", pin3: "2A", pin4: "GND", pin5: "2Y", pin6: "3A", pin7: "1Y", pin8: "VCC" }}
      connections={{ pin1: N("MCH_MCLK"), pin2: N("FSYNC_BUF"), pin3: N("MCH_BCLK"), pin4: N("GND"), pin5: N("BCLK_BUF"), pin6: N("MCH_FSYNC"), pin7: N("MCLK_BUF"), pin8: N("3V3_ADC") }} footprint={<Vssop8 />} />
    <C2 name="C_CLK" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" section="TDM clocks and reset" schX="-4mm" schY="5mm" />
    <R2 name="R_MCH_MCLK_PD" value="10k" a="MCH_MCLK" b="GND" jlc="C60490" mpn="RC0402FR-0710KL" section="TDM clocks and reset" schX="-8mm" schY="8mm" />
    <R2 name="R_MCH_BCLK_PD" value="10k" a="MCH_BCLK" b="GND" jlc="C60490" mpn="RC0402FR-0710KL" section="TDM clocks and reset" schX="-8mm" schY="5mm" />
    <R2 name="R_MCH_FSYNC_PD" value="10k" a="MCH_FSYNC" b="GND" jlc="C60490" mpn="RC0402FR-0710KL" section="TDM clocks and reset" schX="-8mm" schY="2mm" />
    <R2 name="R_MCLK" value="22" a="MCLK_BUF" b="ADC_MCLK" jlc="C114765" mpn="RC0402FR-0722RL" section="TDM clocks and reset" schX="2mm" schY="13mm" />
    <R2 name="R_BCLK" value="22" a="BCLK_BUF" b="ADC_BCLK" jlc="C114765" mpn="RC0402FR-0722RL" section="TDM clocks and reset" schX="2mm" schY="10mm" />
    <R2 name="R_FSYNC" value="22" a="FSYNC_BUF" b="ADC_FSYNC" jlc="C844025" mpn="CRCW120622R0FKEAHP" footprint="1206" section="TDM clocks and reset" schX="2mm" schY="7mm" />
    {/* ADR0005: high-to-Hi-Z decay lands on a genuine noninverting Schmitt
        input, never directly on the standard CMOS tri-state input. */}
    <R2 name="R_TDM_PD" value="10k" a="TDM_RAW" b="GND" jlc="C60490" mpn="RC0402FR-0710KL" section="TDM clocks and reset" schX="1mm" schY="1mm" />
    <Chip name="U_TDM_SCH" manufacturerPartNumber="74LVC1G17GV,125" jlc="C6076"
      schSectionName="TDM clocks and reset" schSheetName="digital" schX="2mm" schY="3mm"
      pinLabels={{ pin1: "NC", pin2: "A_SCHMITT", pin3: "GND", pin4: "Y", pin5: "VCC" }}
      connections={{ pin2: N("TDM_RAW"), pin3: N("GND"), pin4: N("TDM_CLEAN"), pin5: N("3V3_ADC") }} footprint={<Sot23_5 />} />
    <C2 name="C_TDM_SCH" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" section="TDM clocks and reset" schX="2mm" schY="0mm" />
    <Chip name="U_TDM" manufacturerPartNumber="SN74LVC1G125DBVR" jlc="C23654"
      schSectionName="TDM clocks and reset" schSheetName="digital" schX="5mm" schY="3mm"
      pinLabels={{ pin1: "OE_N", pin2: "A", pin3: "GND", pin4: "Y", pin5: "VCC" }}
      connections={{ pin1: N("TDM_OE_N"), pin2: N("TDM_CLEAN"), pin3: N("GND"), pin4: N("TDM_BUFFERED"), pin5: N("3V3_ADC") }} footprint={<Sot23_5 />} />
    <C2 name="C_TDM" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" section="TDM clocks and reset" schX="5mm" schY="0mm" />
    {/* Genuine Schmitt inverter accepts arbitrarily slow presence ramps;
        its push-pull output, not an RC/NMOS node, drives the 1G125 OE. */}
    <Chip name="U_OE" manufacturerPartNumber="74LVC1G14GV,125" jlc="C131093"
      schSectionName="TDM clocks and reset" schSheetName="digital" schX="12mm" schY="3mm"
      pinLabels={{ pin1: "NC", pin2: "A_SCHMITT", pin3: "GND", pin4: "Y", pin5: "VCC" }}
      connections={{ pin2: N("TDM_SENSE_G"), pin3: N("GND"), pin4: N("TDM_OE_N"), pin5: N("3V3_ADC") }} footprint={<Sot23_5 />} />
    <C2 name="C_OE" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" section="TDM clocks and reset" schX="12mm" schY="0mm" />
    <R2 name="R_MCH_SENSE" value="300" a="MCH_3V3_SENSE" b="TDM_SENSE_G" jlc="C138010" mpn="RC0402FR-07300RL" section="TDM clocks and reset" schX="12mm" schY="7mm" />
    <R2 name="R_MCH_SENSE_PD" value="10k" a="TDM_SENSE_G" b="GND" jlc="C60490" mpn="RC0402FR-0710KL" section="TDM clocks and reset" schX="16mm" schY="7mm" />
    <R2 name="R_TDM" value="33" a="TDM_BUFFERED" b="ADC_TDM" jlc="C138002" mpn="RC0402FR-0733RL" section="TDM clocks and reset" schX="2mm" schY="4mm" />

    <Chip name="U_RST1" manufacturerPartNumber="TPS3839K33DBZR" jlc="C96333"
      schSectionName="TDM clocks and reset" schSheetName="digital" schX="-5mm" schY="-2mm"
      pinLabels={{ pin1: "GND", pin2: "RESET_N", pin3: "VDD" }}
      connections={{ pin1: N("GND"), pin2: N("POR_N"), pin3: N("3V3_ADC") }} footprint={<Sot23 />} />
    <C2 name="C_RST1" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" section="TDM clocks and reset" schX="-8mm" schY="-5mm" />
    <Chip name="U_RST2" manufacturerPartNumber="SN74LVC1G123DCTR" jlc="C123302"
      schSectionName="TDM clocks and reset" schSheetName="digital" schX="3mm" schY="-2mm"
      pinLabels={{ pin1: "A", pin2: "B", pin3: "CLR_N", pin4: "GND", pin5: "Q", pin6: "CEXT", pin7: "REXT_CEXT", pin8: "VCC" }}
      connections={{ pin1: N("GND"), pin2: N("3V3_ADC"), pin3: N("POR_N"), pin4: N("GND"), pin5: N("RESET_PULSE_H"), pin6: N("RESET_C"), pin7: N("RESET_RC"), pin8: N("3V3_ADC") }} footprint={<Ssop8 />} />
    <R2 name="R_RST_T" value="100k" a="3V3_ADC" b="RESET_RC" jlc="C60491" mpn="RC0402FR-07100KL" section="TDM clocks and reset" schX="8mm" schY="1mm" />
    <C2 name="C_RST_T" value="220nF" a="RESET_C" b="RESET_RC" jlc="C21120" mpn="CL10B224KA8NNNC" footprint="0603" section="TDM clocks and reset" schX="8mm" schY="-3mm" />
    <C2 name="C_RST2" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" section="TDM clocks and reset" schX="3mm" schY="-7mm" />
    <Chip name="Q_RST1" manufacturerPartNumber="2N7002K-7" jlc="C85047"
      schSectionName="TDM clocks and reset" schSheetName="digital" schX="13mm" schY="-2mm"
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }}
      connections={{ pin1: N("RESET_PULSE_H"), pin2: N("GND"), pin3: N("ADC_RESET_N") }} footprint={<Diodes2N7002K />} />
    <R2 name="R_RESET_PU" value="10k" a="3V3_ADC" b="ADC_RESET_N" jlc="C60490" mpn="RC0402FR-0710KL" section="TDM clocks and reset" schX="17mm" schY="1mm" />
    <R2 name="R_RESET_GPD" value="100k" a="RESET_PULSE_H" b="GND" jlc="C60491" mpn="RC0402FR-07100KL" section="TDM clocks and reset" schX="17mm" schY="-4mm" />
  </board>
)
