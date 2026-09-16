// Crow microphone pod v3 — fresh first-article analog design.
//
// FIRST-ARTICLE-ONLY / DO NOT ORDER. The pod accepts the frozen four-wire
// spoke, derives a quiet 5 V rail, biases one hand-wired electret capsule and
// drives DC-coupled active-balanced audio at nominal 2.5 V common mode.
// There is intentionally no MCU, ADC, USB, Ethernet, PoE or beeper.

import { sel } from "tscircuit"

const N = (name: string) => `net.${/^\d/.test(name) ? `N${name}` : name}`

const SHEET: Record<string, string> = {
  "Spoke input and protection": "input",
  "Quiet five volt rail": "quiet_power",
  "Microphone and reference": "microphone",
  "Active balanced output": "balanced_output",
}

const sheetFor = (section: string) => {
  const sheet = SHEET[section]
  if (!sheet) throw new Error(`No schematic sheet owns section: ${section}`)
  return sheet
}

// Deterministic, non-overlapping source placement.  The governed KiCad
// floorplan remains the fabrication placement authority; these coordinates
// make the circuit-json geometry auditable instead of leaving every package
// at the origin.
const PCB: Record<string, [number, number]> = {
  J1: [-26, 15], F1: [-20, 9], D1: [-14, 9], D2: [-7, 13], R14: [-7, 17],
  C1: [-1, 15], C2: [4, 15], U2: [-1, 8], R1: [4, 12],
  R2: [9, 12], C3: [4, 9], C4: [-6, 5], C5: [0, 4], C6: [6, 5],
  R3: [12, 14], C7: [17, 14], R4: [22, 14], MK1: [25, 10],
  C8: [22, 7], R5: [17, 7], R6: [12, 10], R7: [12, 7], C9: [17, 10],
  U1: [3, -6], C10: [-4, -13], C11: [1, -13], R8: [-9, -1],
  R9: [-4, -1], R10: [8, -1], R11: [13, -1], R12: [18, -5],
  R13: [18, -9], U3: [-13, 15],
  TP1: [-22, -17], TP2: [-15, -17], TP3: [-8, -17], TP4: [-1, -17],
  TP5: [6, -17], TP6: [13, -17], TP7: [20, -17],
}

const pcbAt = (name: string) => {
  const p = PCB[name]
  if (!p) throw new Error(`No deterministic PCB position for ${name}`)
  return { pcbX: `${p[0]}mm`, pcbY: `${p[1]}mm` }
}

const R2 = ({ name, value, a, b, jlc, mpn, footprint = "0402", section, schX, schY }: any) => (
  <resistor name={name} resistance={value} footprint={footprint}
    supplierPartNumbers={{ jlcpcb: [jlc] }} manufacturerPartNumber={mpn}
    schSectionName={section} schSheetName={sheetFor(section)} schX={schX} schY={schY} {...pcbAt(name)}
    connections={{ pin1: N(a), pin2: N(b) }} />
)

const C2 = ({ name, value, a, b, jlc, mpn, footprint = "0402", section, schX, schY }: any) => (
  <capacitor name={name} capacitance={value} footprint={footprint}
    supplierPartNumbers={{ jlcpcb: [jlc] }} manufacturerPartNumber={mpn}
    schSectionName={section} schSheetName={sheetFor(section)} schX={schX} schY={schY} {...pcbAt(name)}
    connections={{ pin1: N(a), pin2: N(b) }} />
)

const SmaDiode = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-2mm" pcbY="0mm" width="2.5mm" height="1.8mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="2mm" pcbY="0mm" width="2.5mm" height="1.8mm" shape="rect" />
  </footprint>
)

const SmbDiode = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-2.15mm" pcbY="0mm" width="2.5mm" height="2.3mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="2.15mm" pcbY="0mm" width="2.5mm" height="2.3mm" shape="rect" />
  </footprint>
)

const Soic14D = () => (
  <footprint>
    {[1, 2, 3, 4, 5, 6, 7].map((pin, i) => (
      <smtpad key={pin} portHints={[`${pin}`]} pcbX="-2.475mm" pcbY={`${-3.81 + i * 1.27}mm`}
        width="1.95mm" height="0.6mm" shape="rect" />
    ))}
    {[8, 9, 10, 11, 12, 13, 14].map((pin, i) => (
      <smtpad key={pin} portHints={[`${pin}`]} pcbX="2.475mm" pcbY={`${3.81 - i * 1.27}mm`}
        width="1.95mm" height="0.6mm" shape="rect" />
    ))}
  </footprint>
)

const Sot553Drl = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-0.7125mm" pcbY="-0.5mm" width="0.675mm" height="0.35mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="-0.7125mm" pcbY="0mm" width="0.675mm" height="0.35mm" shape="rect" />
    <smtpad portHints={["3"]} pcbX="-0.7125mm" pcbY="0.5mm" width="0.675mm" height="0.35mm" shape="rect" />
    <smtpad portHints={["4"]} pcbX="0.7125mm" pcbY="0.5mm" width="0.675mm" height="0.35mm" shape="rect" />
    <smtpad portHints={["5"]} pcbX="0.7125mm" pcbY="-0.5mm" width="0.675mm" height="0.35mm" shape="rect" />
  </footprint>
)

const Hvssop8Ep = () => (
  <footprint>
    <smtpad portHints={["1"]} pcbX="-2.15mm" pcbY="-0.975mm" width="1.45mm" height="0.5mm" shape="rect" />
    <smtpad portHints={["2"]} pcbX="-2.15mm" pcbY="-0.325mm" width="1.45mm" height="0.5mm" shape="rect" />
    <smtpad portHints={["3"]} pcbX="-2.15mm" pcbY="0.325mm" width="1.45mm" height="0.5mm" shape="rect" />
    <smtpad portHints={["4"]} pcbX="-2.15mm" pcbY="0.975mm" width="1.45mm" height="0.5mm" shape="rect" />
    <smtpad portHints={["5"]} pcbX="2.15mm" pcbY="0.975mm" width="1.45mm" height="0.5mm" shape="rect" />
    <smtpad portHints={["6"]} pcbX="2.15mm" pcbY="0.325mm" width="1.45mm" height="0.5mm" shape="rect" />
    <smtpad portHints={["7"]} pcbX="2.15mm" pcbY="-0.325mm" width="1.45mm" height="0.5mm" shape="rect" />
    <smtpad portHints={["8"]} pcbX="2.15mm" pcbY="-0.975mm" width="1.45mm" height="0.5mm" shape="rect" />
    <smtpad portHints={["9"]} pcbX="0mm" pcbY="0mm" width="1.57mm" height="1.89mm" shape="rect" />
  </footprint>
)

const MicroFit4 = () => (
  <footprint>
    {/* Molex/KiCad exact land geometry: pad pitch 3.00 mm, 1.02 mm drills,
        asymmetric pad-1 shape, and two 3.00 mm locating/retention holes.
        The project-vendored KiCad footprint owns body, courtyard and 3D data. */}
    <platedhole portHints={["1"]} pcbX="0mm" pcbY="0mm" shape="circular_hole_with_rect_pad"
      holeDiameter="1.02mm" rectPadWidth="1.5mm" rectPadHeight="2.02mm" rectBorderRadius="0.25mm" />
    {[1, 2, 3].map((i) => (
      <platedhole key={i} portHints={[`${i + 1}`]} pcbX={`${i * 3}mm`} pcbY="0mm"
        outerWidth="1.5mm" outerHeight="2.02mm" holeWidth="1.02mm" holeHeight="1.02mm" shape="oval" />
    ))}
    <hole pcbX="2.15mm" pcbY="-4.32mm" diameter="3mm" />
    <hole pcbX="6.85mm" pcbY="-4.32mm" diameter="3mm" />
  </footprint>
)

const MicWirePads = () => (
  <footprint>
    <platedhole portHints={["1"]} pcbX="-2.5mm" pcbY="0mm"
      outerDiameter="2.2mm" holeDiameter="1.2mm" shape="circle" />
    <platedhole portHints={["2"]} pcbX="2.5mm" pcbY="0mm"
      outerDiameter="2.2mm" holeDiameter="1.2mm" shape="circle" />
  </footprint>
)

export default () => (
  <board width="60mm" height="40mm" routingDisabled>
    <schematicsheet name="input"
      displayName="SPOKE INPUT — 10.5–13.2 V at pod / no hot-plug / protected 12 V boundary" sheetIndex={1} />
    <schematicsheet name="quiet_power"
      displayName="QUIET 5 V — TPS7A4901 adjustable LDO / 10.1 uF connector-side capacitance" sheetIndex={2} />
    <schematicsheet name="microphone"
      displayName="ELECTRET FRONT END — hand-wired capsule / filtered bias / buffered half-rail" sheetIndex={3} />
    <schematicsheet name="balanced_output"
      displayName="ACTIVE BALANCED OUTPUT — gain 18/11 V/V differential / 100 ohm each leg / DC-coupled" sheetIndex={4} />

    <chip name="J1" manufacturerPartNumber="43650-0400"
      schSectionName="Spoke input and protection" schSheetName="input" schX="-10mm" schY="0mm"
      {...pcbAt("J1")}
      pinLabels={{ pin1: "12V_POD", pin2: "GND", pin3: "AUDIO_P", pin4: "AUDIO_N" }}
      schPinArrangement={{ leftSide: [1, 2], rightSide: [3, 4] }}
      connections={{ pin1: N("12V_POD"), pin2: N("GND"), pin3: N("AUDIO_P"), pin4: N("AUDIO_N") }}
      footprint={<MicroFit4 />} />

    <chip name="F1" supplierPartNumbers={{ jlcpcb: ["C194142"] }} manufacturerPartNumber="0ZCJ0010FF2E"
      schSectionName="Spoke input and protection" schSheetName="input" schX="-4mm" schY="4mm"
      {...pcbAt("F1")}
      pinLabels={{ pin1: "IN", pin2: "OUT" }} connections={{ pin1: N("12V_POD"), pin2: N("12V_FUSED") }}
      footprint="1206" />
    <chip name="D1" supplierPartNumbers={{ jlcpcb: ["C2972759"] }} manufacturerPartNumber="1N4007(M7)SMA"
      schSectionName="Spoke input and protection" schSheetName="input" schX="1mm" schY="4mm"
      {...pcbAt("D1")}
      pinLabels={{ pin1: "K", pin2: "A" }} connections={{ pin1: N("VIN_PROTECTED"), pin2: N("12V_FUSED") }}
      footprint={<SmaDiode />} />
    <chip name="D2" supplierPartNumbers={{ jlcpcb: ["C83846"] }} manufacturerPartNumber="SMBJ15A"
      schSectionName="Spoke input and protection" schSheetName="input" schX="6mm" schY="4mm"
      {...pcbAt("D2")}
      pinLabels={{ pin1: "K", pin2: "A" }} connections={{ pin1: N("VIN_PROTECTED"), pin2: N("GND") }}
      footprint={<SmbDiode />} />
    <R2 name="R14" value="4.7k" a="VIN_PROTECTED" b="GND" jlc="C17936" mpn="1206W4F4701T5E"
      footprint="1206" section="Spoke input and protection" schX="10mm" schY="-7mm" />
    <C2 name="C1" value="10uF" a="VIN_PROTECTED" b="GND" jlc="C77102" mpn="GRM32ER71H106KA12L"
      footprint="1210" section="Quiet five volt rail" schX="-5mm" schY="2mm" />
    <C2 name="C2" value="100nF" a="VIN_PROTECTED" b="GND" jlc="C131394" mpn="CC0402KRX7R9BB104"
      section="Quiet five volt rail" schX="-2mm" schY="2mm" />

    <chip name="U2" supplierPartNumbers={{ jlcpcb: ["C16430"] }} manufacturerPartNumber="TPS7A4901DGNR"
      schSectionName="Quiet five volt rail" schSheetName="quiet_power" schX="0mm" schY="0mm"
      {...pcbAt("U2")}
      pinLabels={{ pin1: "OUT", pin2: "FB", pin3: "NC", pin4: "GND", pin5: "EN", pin6: "NR_SS", pin7: "DNC", pin8: "IN", pin9: "EP_GND" }}
      schPinArrangement={{ leftSide: [8, 5, 6], rightSide: [1, 2], bottomSide: [4, 9], topSide: [3, 7] }}
      connections={{ pin1: N("5V_QUIET"), pin2: N("LDO_FB"), pin4: N("GND"), pin5: N("VIN_PROTECTED"), pin6: N("LDO_NR"), pin8: N("VIN_PROTECTED"), pin9: N("GND") }}
      footprint={<Hvssop8Ep />} />
    {/* Human-readable cross-sheet boundary. U2 IN and EN already share the
      VIN_PROTECTED source net; this label makes that fact visible on the
      quiet-power page instead of rendering an anonymous local loop. */}
    <group name="quiet_power_input_label" schSheetName="quiet_power">
      <netlabel net="VIN_PROTECTED" connectsTo={sel.U2.pin8}
        schX="-8mm" schY="0mm" anchorSide="right" />
    </group>
    <R2 name="R1" value="324k" a="5V_QUIET" b="LDO_FB" jlc="C113480" mpn="0402WGF3243TCE"
      section="Quiet five volt rail" schX="6mm" schY="3mm" />
    <R2 name="R2" value="100k" a="LDO_FB" b="GND" jlc="C25741" mpn="0402WGF1003TCE"
      section="Quiet five volt rail" schX="10mm" schY="0mm" />
    <C2 name="C3" value="10nF" a="5V_QUIET" b="LDO_FB" jlc="C15195" mpn="CL05B103KB5NNNC"
      section="Quiet five volt rail" schX="7mm" schY="6mm" />
    <C2 name="C4" value="10nF" a="LDO_NR" b="GND" jlc="C15195" mpn="CL05B103KB5NNNC"
      section="Quiet five volt rail" schX="-5mm" schY="-5mm" />
    <C2 name="C5" value="10uF" a="5V_QUIET" b="GND" jlc="C15850" mpn="CL21A106KAYNNNE" footprint="0805"
      section="Quiet five volt rail" schX="3mm" schY="-2mm" />
    <C2 name="C6" value="100nF" a="5V_QUIET" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC"
      section="Quiet five volt rail" schX="5mm" schY="-2mm" />

    <R2 name="R3" value="3.9k" a="5V_QUIET" b="MIC_BIAS" jlc="C17614" mpn="0805W8F3901T5E" footprint="0805"
      section="Microphone and reference" schX="-9mm" schY="5mm" />
    <C2 name="C7" value="100uF" a="MIC_BIAS" b="GND" jlc="C84455" mpn="GRM32ER61A107ME20L" footprint="1210"
      section="Microphone and reference" schX="-4mm" schY="5mm" />
    <R2 name="R4" value="2.2k" a="MIC_BIAS" b="MIC_RAW" jlc="C25879" mpn="0402WGF2201TCE"
      section="Microphone and reference" schX="1mm" schY="5mm" />
    <chip name="MK1" manufacturerPartNumber="AOM-5024L-HD-R"
      schSectionName="Microphone and reference" schSheetName="microphone" schX="7mm" schY="5mm"
      {...pcbAt("MK1")}
      pinLabels={{ pin1: "CAPSULE_POS", pin2: "CAPSULE_NEG" }}
      connections={{ pin1: N("MIC_RAW"), pin2: N("GND") }} footprint={<MicWirePads />} />
    <C2 name="C8" value="1uF" a="MIC_RAW" b="MIC_AC" jlc="C15849" mpn="CL10A105KB8NNNC" footprint="0603"
      section="Microphone and reference" schX="9mm" schY="0mm" />
    <R2 name="R5" value="100k" a="MIC_AC" b="VREF" jlc="C25741" mpn="0402WGF1003TCE"
      section="Microphone and reference" schX="9mm" schY="-5mm" />
    <R2 name="R6" value="22k" a="5V_QUIET" b="VREF_RAW" jlc="C25768" mpn="0402WGF2202TCE"
      section="Microphone and reference" schX="-8mm" schY="-4mm" />
    <R2 name="R7" value="22k" a="VREF_RAW" b="GND" jlc="C25768" mpn="0402WGF2202TCE"
      section="Microphone and reference" schX="-3mm" schY="-4mm" />
    <C2 name="C9" value="10uF" a="VREF_RAW" b="GND" jlc="C15850" mpn="CL21A106KAYNNNE" footprint="0805"
      section="Microphone and reference" schX="2mm" schY="-4mm" />

    <chip name="U1" supplierPartNumbers={{ jlcpcb: ["C2878631"] }} manufacturerPartNumber="OPA1679IDR"
      schSectionName="Active balanced output" schSheetName="balanced_output" schX="0mm" schY="0mm"
      {...pcbAt("U1")}
      pinLabels={{ pin1: "OUTA_VREF", pin2: "INA_NEG", pin3: "INA_POS", pin4: "VPLUS", pin5: "INB_POS", pin6: "INB_NEG", pin7: "OUTB_PRE", pin8: "OUTC", pin9: "INC_NEG", pin10: "INC_POS", pin11: "VMINUS", pin12: "IND_POS", pin13: "IND_NEG", pin14: "OUTD" }}
      schPinArrangement={{ leftSide: [3, 2, 5, 6, 10, 9, 12, 13], rightSide: [1, 7, 8], topSide: [4], bottomSide: [11, 14] }}
      connections={{
        pin1: N("VREF"), pin2: N("VREF"), pin3: N("VREF_RAW"), pin4: N("5V_QUIET"),
        pin5: N("VREF"), pin6: N("PRE_FB"), pin7: N("PRE_OUT"),
        pin8: N("OUTP_DRV"), pin9: N("OUTP_FB"), pin10: N("VREF"), pin11: N("GND"),
        pin12: N("VREF"), pin13: N("SPARE_BUF"), pin14: N("SPARE_BUF"),
      }} footprint={<Soic14D />} />
    <C2 name="C10" value="100nF" a="5V_QUIET" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC"
      section="Active balanced output" schX="-4mm" schY="2mm" />
    <C2 name="C11" value="10uF" a="5V_QUIET" b="GND" jlc="C15850" mpn="CL21A106KAYNNNE" footprint="0805"
      section="Active balanced output" schX="-2mm" schY="2mm" />
    <R2 name="R8" value="22k" a="MIC_AC" b="PRE_FB" jlc="C25768" mpn="0402WGF2202TCE"
      section="Active balanced output" schX="-9mm" schY="5mm" />
    <R2 name="R9" value="18k" a="PRE_OUT" b="PRE_FB" jlc="C25762" mpn="0402WGF1802TCE"
      section="Active balanced output" schX="-4mm" schY="5mm" />
    <R2 name="R10" value="10k" a="PRE_OUT" b="OUTP_FB" jlc="C60490" mpn="RC0402FR-0710KL"
      section="Active balanced output" schX="2mm" schY="5mm" />
    <R2 name="R11" value="10k" a="OUTP_DRV" b="OUTP_FB" jlc="C60490" mpn="RC0402FR-0710KL"
      section="Active balanced output" schX="7mm" schY="5mm" />
    <R2 name="R12" value="100" a="OUTP_DRV" b="AUDIO_P" jlc="C17408" mpn="0805W8F1000T5E"
      footprint="0805" section="Active balanced output" schX="8mm" schY="0mm" />
    <R2 name="R13" value="100" a="PRE_OUT" b="AUDIO_N" jlc="C17408" mpn="0805W8F1000T5E"
      footprint="0805" section="Active balanced output" schX="8mm" schY="-4mm" />
    <chip name="U3" supplierPartNumbers={{ jlcpcb: ["C1972959"] }} manufacturerPartNumber="TPD2E2U06DRLR"
      schSectionName="Active balanced output" schSheetName="balanced_output" schX="12mm" schY="-1mm"
      {...pcbAt("U3")}
      pinLabels={{ pin1: "NC1", pin2: "NC2", pin3: "IO1_AUDIO_P", pin4: "GND", pin5: "IO2_AUDIO_N" }}
      connections={{ pin3: N("AUDIO_P"), pin4: N("GND"), pin5: N("AUDIO_N") }}
      footprint={<Sot553Drl />} />

    {[
      { name: "TP1", net: "12V_POD", section: "Spoke input and protection", schX: "-9mm", schY: "-7mm" },
      { name: "TP2", net: "VIN_PROTECTED", section: "Spoke input and protection", schX: "-4mm", schY: "-7mm" },
      { name: "TP3", net: "5V_QUIET", section: "Quiet five volt rail", schX: "-9mm", schY: "4mm" },
      { name: "TP4", net: "VREF", section: "Microphone and reference", schX: "4mm", schY: "-8mm" },
      { name: "TP5", net: "AUDIO_P", section: "Active balanced output", schX: "13mm", schY: "5mm" },
      { name: "TP6", net: "AUDIO_N", section: "Active balanced output", schX: "13mm", schY: "-5mm" },
      { name: "TP7", net: "GND", section: "Quiet five volt rail", schX: "-9mm", schY: "-5mm" },
    ].map(({ name, net, section, schX, schY }) => (
      <testpoint key={name} name={name} footprintVariant="pad" padShape="circle" padDiameter="1.5mm"
        schSectionName={section} schSheetName={sheetFor(section)} schX={schX} schY={schY}
        {...pcbAt(name)}
        connections={{ pin1: N(net) }} />
    ))}
  </board>
)
