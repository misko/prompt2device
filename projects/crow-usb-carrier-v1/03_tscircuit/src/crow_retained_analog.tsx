import { Fragment } from "react"
import {
  CirrusCs5308pQfn48, Diodes2N7002kSot23, TiDrc0010j,
  PanasonicEeeFk8x10, Sot553, TiDck0005a, TiDse0006a, TiDsg0008a,
  Wurth615008160221Rj45, YageoRt0603,
} from "./z_analog_exact_footprints"

/**
 * Draft retained Crow analog subsystem for crow-usb-carrier-v1.
 *
 * Scope: eight powered analog spokes, complete OPA2320/filter/TMUX receive
 * paths, CS5308P analog/reference/hardware-mode network, quiet held analog
 * rail, and hardware reset. The parent owns the complete digital subsystem;
 * retired connector/presence logic, cable clock buffers, and output isolation
 * are outside this module.
 *
 * This file is reusable source, not a complete board and not an electrical
 * acceptance result. The parent board must provide the boundary nets below.
 */

export const CROW_ANALOG_BOUNDARY_NETS = {
  powerInputs: ["12V_PROTECTED", "5V_BUCK", "GND", "CHASSIS"],
  clockInputs: ["ADC_MCLK", "ADC_BCLK", "ADC_FSYNC"],
  dataOutputs: ["ADC_DOUT1"],
  connectorNets: Array.from({ length: 8 }, (_, i) => {
    const n = i + 1
    return [`12V_POD${n}`, `AUDIO_P${n}`, `AUDIO_N${n}`]
  }).flat(),
} as const

export interface CrowRetainedAnalogProps {
  /** Optional parent-board canonical-net remap. */
  net?: (canonicalName: string) => string
}

const defaultNet = (name: string) => `net.${/^\d/.test(name) ? `N${name}` : name}`
const POD_TO_ADC = [4, 3, 2, 1, 5, 6, 7, 8] as const
const adcInputNet = (physicalChannel: number, leg: "P" | "N") =>
  `ADC${(POD_TO_ADC as readonly number[]).indexOf(physicalChannel) + 1}${leg}`

// Selectively retained package geometry from the donor source. These contain
// no placement transform or board pose.
const FilmCap5mm = () => (
  <footprint>
    <platedhole portHints={["1"]} pcbX="-2.5mm" pcbY="0mm"
      shape="circular_hole_with_rect_pad" holeDiameter="0.75mm"
      rectPadWidth="1.5mm" rectPadHeight="1.5mm" rectBorderRadius="0.2mm" />
    <platedhole portHints={["2"]} pcbX="2.5mm" pcbY="0mm"
      shape="circle" holeDiameter="0.75mm" outerDiameter="1.5mm" />
  </footprint>
)

// ADI LT3045 DD package, LTC drawing 05-08-1699 Rev C.
const Lt3045Dd = () => (
  <footprint>
    {Array.from({ length: 5 }, (_, i) => <Fragment key={`l${i}`}><smtpad portHints={[`${i + 1}`]} pcbX="-1.425mm" pcbY={`${-1 + i * 0.5}mm`} width="0.7mm" height="0.25mm" shape="rect" /></Fragment>)}
    {Array.from({ length: 5 }, (_, i) => <Fragment key={`r${i}`}><smtpad portHints={[`${10 - i}`]} pcbX="1.425mm" pcbY={`${-1 + i * 0.5}mm`} width="0.7mm" height="0.25mm" shape="rect" /></Fragment>)}
    <smtpad portHints={["11"]} pcbX="0mm" pcbY="0mm" width="1.65mm" height="2.38mm" shape="rect" />
  </footprint>
)

const supplier = (jlc: string) => ({ jlcpcb: jlc ? [jlc] : [] })

const R = ({ name, value, a, b, mpn, jlc, footprint = "0402", n }: any) => (
  <resistor name={name} resistance={value} footprint={footprint}
    manufacturerPartNumber={mpn} supplierPartNumbers={supplier(sourced(mpn, jlc))}
    connections={{ pin1: n(a), pin2: n(b) }} />
)

const C = ({ name, value, a, b, mpn, jlc, footprint = "0402", polarized = false, n }: any) => (
  <capacitor name={name} capacitance={value} footprint={footprint} polarized={polarized}
    manufacturerPartNumber={mpn} supplierPartNumbers={supplier(sourced(mpn, jlc))}
    connections={{ pin1: n(a), pin2: n(b) }} />
)

const sourced = (mpn: string, jlc = "") => jlc || ({
  "615008160221": "C6461980", "R82DC4100CK60J": "C3778009",
  "SN74LVC1G04DCKR": "C8207", "SN74LVC1G125DCKT": "C2675550",
  "TPS389018DSER": "C2066910", "TPS389030DSER": "C2066942",
} as Record<string, string>)[mpn] || ""
const Chip = ({ jlc = "", manufacturerPartNumber, ...props }: any) => (
  <chip manufacturerPartNumber={manufacturerPartNumber} supplierPartNumbers={supplier(sourced(manufacturerPartNumber, jlc))} {...props} />
)

const Spoke = ({ index, n }: any) => (
  <>
    <Chip name={`J${index}`} manufacturerPartNumber="615008160221" jlc=""
      footprint={<Wurth615008160221Rj45 />}
      pinLabels={{ pin1: "12V_1", pin2: "GND_1", pin3: "12V_2", pin4: "AUDIO_N", pin5: "AUDIO_P", pin6: "GND_2", pin7: "12V_3", pin8: "GND_3", pin9: "SHIELD_S1", pin10: "SHIELD_S2" }}
      connections={{ pin1: n(`12V_POD${index}`), pin2: n("GND"), pin3: n(`12V_POD${index}`), pin4: n(`AUDIO_N${index}`), pin5: n(`AUDIO_P${index}`), pin6: n("GND"), pin7: n(`12V_POD${index}`), pin8: n("GND"), pin9: n("CHASSIS"), pin10: n("CHASSIS") }} />
    <Chip name={`U_SPOKE${index}`} manufacturerPartNumber="TPS26625DRCR" jlc="C2862873"
      footprint={<TiDrc0010j />}
      pinLabels={{ pin1: "IN", pin2: "UVLO", pin3: "OVP", pin4: "SHDN", pin5: "RTN", pin6: "GND", pin7: "ILIM", pin8: "dVdT", pin9: "FLT", pin10: "OUT", pin11: "EP" }}
      connections={{ pin1: n("12V_PROTECTED"), pin2: n(`SPOKE_UVLO${index}`), pin3: n(`SPOKE_RTN${index}`), pin4: n("12V_PROTECTED"), pin5: n(`SPOKE_RTN${index}`), pin6: n("GND"), pin7: n(`SPOKE_ILIM${index}`), pin8: n(`SPOKE_DVDT${index}`), pin10: n(`12V_POD${index}`), pin11: n(`SPOKE_RTN${index}`) }} />
    <R name={`R_SPOKE_UVLO${index}`} value="1M" a="12V_PROTECTED" b={`SPOKE_UVLO${index}`} mpn="RC0402FR-071ML" jlc="C138033" n={n} />
    <R name={`R_SPOKE_ILIM${index}`} value="44.2k" a={`SPOKE_ILIM${index}`} b={`SPOKE_RTN${index}`} mpn="RT0603BRD0744K2L" jlc="C861410" footprint={<YageoRt0603 />} n={n} />
    <C name={`C_SPOKE_DVDT${index}`} value="10nF" a={`SPOKE_DVDT${index}`} b={`SPOKE_RTN${index}`} mpn="CL05B103KB5NNNC" jlc="C15195" n={n} />
    <C name={`C_SPOKE_IN${index}`} value="100nF" a="12V_PROTECTED" b="GND" mpn="CC0805KRX7R9BB104" jlc="C49678" footprint="0805" n={n} />
    <C name={`C_SPOKE_OUT${index}`} value="100nF" a={`12V_POD${index}`} b="GND" mpn="CC0805KRX7R9BB104" jlc="C49678" footprint="0805" n={n} />
    <Chip name={`U_ESD${index}`} manufacturerPartNumber="TPD2E2U06DRLR" jlc="C1972959"
      footprint={<Sot553 />}
      pinLabels={{ pin1: "NC1", pin2: "NC2", pin3: "IO1", pin4: "GND", pin5: "IO2" }}
      connections={{ pin3: n(`AUDIO_P${index}`), pin4: n("GND"), pin5: n(`AUDIO_N${index}`) }} />
  </>
)

const AnalogChannel = ({ index, vmid, n }: any) => (
  <>
    <C name={`C_A${index}P`} value="1uF" a={`AUDIO_P${index}`} b={`BIAS_P${index}`} jlc="" mpn="R82DC4100CK60J" footprint={<FilmCap5mm />} n={n} />
    <C name={`C_A${index}N`} value="1uF" a={`AUDIO_N${index}`} b={`BIAS_N${index}`} jlc="" mpn="R82DC4100CK60J" footprint={<FilmCap5mm />} n={n} />
    <R name={`R_B${index}P`} value="100k" a={`BIAS_P${index}`} b={vmid} jlc="C60491" mpn="RC0402FR-07100KL" n={n} />
    <R name={`R_B${index}N`} value="100k" a={`BIAS_N${index}`} b={vmid} jlc="C60491" mpn="RC0402FR-07100KL" n={n} />
    <R name={`R_IN${index}P`} value="10k" a={`BIAS_P${index}`} b={`AIN_P${index}`} jlc="C60490" mpn="RC0402FR-0710KL" n={n} />
    <R name={`R_IN${index}N`} value="10k" a={`BIAS_N${index}`} b={`AIN_N${index}`} jlc="C60490" mpn="RC0402FR-0710KL" n={n} />
    <Chip name={`U_AFE${index}`} manufacturerPartNumber="OPA2320AID" jlc="C2861439" footprint="soic8"
      pinLabels={{ pin1: "OUTA", pin2: "A_NEG", pin3: "A_POS", pin4: "VNEG", pin5: "B_POS", pin6: "B_NEG", pin7: "OUTB", pin8: "VPOS" }}
      connections={{ pin1: n(`OPA_P${index}`), pin2: n(`FB_P${index}`), pin3: n(`AIN_P${index}`), pin4: n("GND"), pin5: n(`AIN_N${index}`), pin6: n(`FB_N${index}`), pin7: n(`OPA_N${index}`), pin8: n("3V3_ADC") }} />
    <R name={`R_X${index}P`} value="300" a={`FB_P${index}`} b={`FILTER${index}P`} jlc="C138010" mpn="RC0402FR-07300RL" n={n} />
    <R name={`R_X${index}N`} value="300" a={`FB_N${index}`} b={`FILTER${index}N`} jlc="C138010" mpn="RC0402FR-07300RL" n={n} />
    <C name={`C_FB${index}P`} value="680pF" a={`FB_P${index}`} b={`OPA_P${index}`} jlc="C126514" mpn="GCM1555C1H681JA16D" n={n} />
    <C name={`C_FB${index}N`} value="680pF" a={`FB_N${index}`} b={`OPA_N${index}`} jlc="C126514" mpn="GCM1555C1H681JA16D" n={n} />
    <R name={`R_OUT${index}P`} value="10" a={`OPA_P${index}`} b={`FILTER${index}P`} jlc="C138066" mpn="RC0402FR-0710RL" n={n} />
    <R name={`R_OUT${index}N`} value="10" a={`OPA_N${index}`} b={`FILTER${index}N`} jlc="C138066" mpn="RC0402FR-0710RL" n={n} />
    {(["P", "N"] as const).flatMap((leg) => [1, 2].map((unit) =>
      <C key={`${leg}${unit}`} name={`C_FILTER${index}${leg}${unit}`} value="15nF" a={`FILTER${index}${leg}`} b="GND" jlc="C97907" mpn="GRM2195C1H153JA01D" footprint="0805" n={n} />))}
    <Chip name={`U_ISO${index}`} manufacturerPartNumber="TMUX2821DSGR" jlc="C53283916"
      footprint={<TiDsg0008a />}
      pinLabels={{ pin1: "S1", pin2: "D1", pin3: "SEL2", pin4: "GND", pin5: "S2", pin6: "D2", pin7: "SEL1", pin8: "VDD", pin9: "EP" }}
      connections={{ pin1: n(`FILTER${index}P`), pin2: n(`ADC${index}P`), pin3: n("AUDIO_EN"), pin4: n("GND"), pin5: n(`FILTER${index}N`), pin6: n(`ADC${index}N`), pin7: n("AUDIO_EN"), pin8: n("5V_LDO_HOLD"), pin9: n("GND") }} />
    {/* R_ADC_PD stays within 1.5 mm of its U_ISO output partner. C_ADC_CM is ADC-pin local.
        Both belong to the joint TMUX/ADC physical proof; functional grouping is not placement. */}
    {(["P", "N"] as const).map((leg) => <R key={`pd${leg}`} name={`R_ADC_PD${index}${leg}`} value="10k" a={`ADC${index}${leg}`} b="GND" jlc="C60490" mpn="RC0402FR-0710KL" n={n} />)}
    {(["P", "N"] as const).map((leg) => <C key={`cm${leg}`} name={`C_ADC_CM${index}${leg}`} value="1nF" a={`ADC${index}${leg}`} b="GND" jlc="C76947" mpn="GRM1555C1H102JA01D" n={n} />)}
    <C name={`C_ISO${index}`} value="100nF" a="5V_LDO_HOLD" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" n={n} />
    <C name={`C_OPA${index}`} value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" n={n} />
  </>
)

const QuietAnalogPower = ({ n }: any) => (
  <>
    {/* 5V_BUCK is a boundary input. USB/core current is forbidden from 3V3_ADC and 5V_LDO_HOLD. */}
    <Chip name="D_HOLD" manufacturerPartNumber="B340A-13-F" jlc="C85098" footprint="sma"
      pinLabels={{ pin1: "K", pin2: "A" }} connections={{ pin1: n("5V_LDO_FEED"), pin2: n("5V_BUCK") }} />
    <Chip name="Q_PRE" manufacturerPartNumber="AO3401A" jlc="C15127" footprint="sot23"
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }} connections={{ pin1: n("PRE_GATE"), pin2: n("5V_LDO_FEED"), pin3: n("5V_LDO_HOLD") }} />
    <Chip name="Q_PRE_EN" manufacturerPartNumber="2N7002K-7" jlc="C85047" footprint={<Diodes2N7002kSot23 />}
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }} connections={{ pin1: n("PWR_EN"), pin2: n("GND"), pin3: n("PRE_GATE") }} />
    <R name="R_PRE" value="22" a="5V_LDO_FEED" b="5V_LDO_HOLD" mpn="CRCW120622R0FKEAHP" jlc="C844025" footprint="1206" n={n} />
    <R name="R_PRE_G" value="100k" a="PRE_GATE" b="5V_LDO_FEED" mpn="RC0402FR-07100KL" jlc="C60491" n={n} />
    <C name="C_HOLD1" value="470uF" a="5V_LDO_HOLD" b="GND" mpn="EEEFK1A471P" jlc="C178530" footprint={<PanasonicEeeFk8x10 />} polarized n={n} />
    <C name="C_HOLD2" value="470uF" a="5V_LDO_HOLD" b="GND" mpn="EEEFK1A471P" jlc="C178530" footprint={<PanasonicEeeFk8x10 />} polarized n={n} />
    <C name="C_LDO_IN" value="47uF" a="5V_LDO_HOLD" b="GND" mpn="GRM32ER71A476KE15L" jlc="C84494" footprint="1210" n={n} />
    <Chip name="U_LDO" manufacturerPartNumber="LT3045EDD#PBF" jlc="C666574" footprint={<Lt3045Dd />}
      pinLabels={{ pin1: "IN1", pin2: "IN2", pin3: "EN_UV", pin4: "PG_NC", pin5: "ILIM", pin6: "PGFB", pin7: "SET", pin8: "GND", pin9: "OUTS", pin10: "OUT", pin11: "EP_GND" }}
      connections={{ pin1: n("5V_LDO_HOLD"), pin2: n("5V_LDO_HOLD"), pin3: n("LDO_EN"), pin5: n("LDO_ILIM"), pin6: n("LDO_PGFB"), pin7: n("LDO_NR"), pin8: n("GND"), pin9: n("3V3_ADC"), pin10: n("3V3_ADC"), pin11: n("GND") }} />
    <R name="R_LDO_ILIM" value="300" a="LDO_ILIM" b="GND" mpn="RC0402FR-07300RL" jlc="C138010" n={n} />
    <C name="C_LDO_OUT" value="47uF" a="3V3_ADC" b="GND" mpn="GRM32ER71A476KE15L" jlc="C84494" footprint="1210" n={n} />
    <C name="C_OPA_BULK" value="47uF" a="3V3_ADC" b="GND" mpn="GRM32ER71A476KE15L" jlc="C84494" footprint="1210" n={n} />
    <C name="C_LDO_NR4" value="4.7uF" a="LDO_NR" b="GND" mpn="CL10A475KO8NNNC" jlc="C19666" footprint="0603" n={n} />
    <C name="C_LDO_NR5" value="1nF" a="LDO_NR" b="GND" mpn="GRM1555C1H102JA01D" jlc="C76947" n={n} />
    <R name="R_LDO_SET" value="33k" a="LDO_NR" b="GND" mpn="RT0603BRD0733KL" jlc="C705768" footprint="0603" n={n} />
    <R name="R_LDO_PG_TOP" value="100k" a="3V3_ADC" b="LDO_PGFB" mpn="RC0402FR-07100KL" jlc="C60491" n={n} />
    <R name="R_LDO_PG_BOT_A" value="10k" a="LDO_PGFB" b="LDO_PGFB_BOT" mpn="RT0603BRD0710KL" jlc="C95204" footprint="0603" n={n} />
    <R name="R_LDO_PG_BOT_B" value="1k" a="LDO_PGFB_BOT" b="GND" mpn="RT0603BRD071KL" jlc="C110776" footprint="0603" n={n} />
    <R name="R_OPA_BLEED1" value="100" a="3V3_ADC" b="OPA_BLEED_A" mpn="RC0402FR-07100RL" jlc="C106232" n={n} />
    <R name="R_OPA_BLEED2" value="100" a="OPA_BLEED_A" b="GND" mpn="RC0402FR-07100RL" jlc="C106232" n={n} />
    <Chip name="U_PWR" manufacturerPartNumber="TPS389001DSER" jlc="C1509297" footprint={<TiDse0006a />}
      pinLabels={{ pin1: "SENSE", pin2: "GND", pin3: "MR_N", pin4: "VDD", pin5: "CT", pin6: "RESET_N" }}
      connections={{ pin1: n("PWR_SENSE"), pin2: n("GND"), pin3: n("5V_LDO_HOLD"), pin4: n("5V_LDO_HOLD"), pin5: n("PWR_CT"), pin6: n("PWR_EN") }} />
    <C name="C_PWR_CT" value="1uF" a="PWR_CT" b="GND" mpn="C0603C105K4RACTU" jlc="C2167386" footprint="0603" n={n} />
    <C name="C_PWR" value="100nF" a="5V_LDO_HOLD" b="GND" mpn="CL05B104KO5NNNC" jlc="C1525" n={n} />
    <R name="R_PWR_PU" value="10k" a="5V_LDO_HOLD" b="PWR_EN" mpn="RC0402FR-0710KL" jlc="C60490" n={n} />
    <R name="R_PWR_TOP" value="30.9k" a="5V_BUCK" b="PWR_SENSE" mpn="RT0603BRD0730K9L" jlc="C861313" footprint={<YageoRt0603 />} n={n} />
    <R name="R_PWR_BOT" value="10k" a="PWR_SENSE" b="GND" mpn="RT0603BRD0710KL" jlc="C95204" footprint="0603" n={n} />
    <Chip name="U_AUDIO" manufacturerPartNumber="TPS389001DSER" jlc="C1509297" footprint={<TiDse0006a />}
      pinLabels={{ pin1: "SENSE", pin2: "GND", pin3: "MR_N", pin4: "VDD", pin5: "CT", pin6: "RESET_N" }}
      connections={{ pin1: n("ADC_SENSE"), pin2: n("GND"), pin3: n("PWR_EN"), pin4: n("5V_LDO_HOLD"), pin5: n("AUDIO_CT"), pin6: n("AUDIO_EN") }} />
    <C name="C_AUDIO_CT1" value="1uF" a="AUDIO_CT" b="GND" mpn="C0603C105K4RACTU" jlc="C2167386" footprint="0603" n={n} />
    <C name="C_AUDIO_CT2" value="1uF" a="AUDIO_CT" b="GND" mpn="C0603C105K4RACTU" jlc="C2167386" footprint="0603" n={n} />
    <C name="C_AUDIO" value="100nF" a="5V_LDO_HOLD" b="GND" mpn="CL05B104KO5NNNC" jlc="C1525" n={n} />
    <R name="R_AUDIO_PU" value="10k" a="5V_LDO_HOLD" b="AUDIO_EN" mpn="RC0402FR-0710KL" jlc="C60490" n={n} />
    <R name="R_AUDIO_PD" value="100k" a="AUDIO_EN" b="GND" mpn="RC0402FR-07100KL" jlc="C60491" n={n} />
    <R name="R_ADC_TOP" value="17.4k" a="3V3_ADC" b="ADC_SENSE" mpn="RT0603BRD0717K4L" jlc="C861167" footprint="0603" n={n} />
    <R name="R_ADC_BOT" value="10k" a="ADC_SENSE" b="GND" mpn="RT0603BRD0710KL" jlc="C95204" footprint="0603" n={n} />
    <Chip name="U_DUMP" manufacturerPartNumber="74LVC1G14GV,125" jlc="C131093" footprint="sot23_5"
      pinLabels={{ pin1: "NC", pin2: "A_SCHMITT", pin3: "GND", pin4: "Y", pin5: "VCC" }} connections={{ pin2: n("DUMP_RC"), pin3: n("GND"), pin4: n("DUMP_GATE"), pin5: n("5V_LDO_HOLD") }} />
    <Chip name="U_LDO_EN" manufacturerPartNumber="74LVC1G14GV,125" jlc="C131093" footprint="sot23_5"
      pinLabels={{ pin1: "NC", pin2: "A_SCHMITT", pin3: "GND", pin4: "Y", pin5: "VCC" }} connections={{ pin2: n("DUMP_GATE"), pin3: n("GND"), pin4: n("LDO_EN"), pin5: n("5V_LDO_HOLD") }} />
    <C name="C_DUMP_LOGIC" value="100nF" a="5V_LDO_HOLD" b="GND" mpn="CL05B104KO5NNNC" jlc="C1525" n={n} />
    <C name="C_LDO_EN" value="100nF" a="5V_LDO_HOLD" b="GND" mpn="CL05B104KO5NNNC" jlc="C1525" n={n} />
    <R name="R_DUMP_TIME1" value="100k" a="PWR_EN" b="DUMP_RC" mpn="RC0402FR-07100KL" jlc="C60491" n={n} />
    <R name="R_DUMP_TIME2" value="100k" a="PWR_EN" b="DUMP_RC" mpn="RC0402FR-07100KL" jlc="C60491" n={n} />
    <C name="C_DUMP_TIME" value="15nF" a="DUMP_RC" b="GND" mpn="GRM2195C1H153JA01D" jlc="C97907" footprint="0805" n={n} />
    <Chip name="Q_DUMP" manufacturerPartNumber="AO3400A" jlc="C20917" footprint="sot23"
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }} connections={{ pin1: n("DUMP_GATE"), pin2: n("GND"), pin3: n("ADC_DUMP") }} />
    <R name="R_DUMP" value="1" a="3V3_ADC" b="ADC_DUMP" mpn="CRCW12061R00FKEAHP" jlc="C844653" footprint="1206" n={n} />
    <R name="R_DUMP_PD" value="100k" a="DUMP_GATE" b="GND" mpn="RC0402FR-07100KL" jlc="C60491" n={n} />
  </>
)

const AdcReferenceAndMode = ({ n }: any) => (
  <>
    {[1, 2].map((bank) => <group key={`vmid-${bank}`}>
      <R name={`R_VMID${bank}_TOP`} value="1k" a="3V3_ADC" b={`VMID${bank}_EXT`} jlc="C110776" mpn="RT0603BRD071KL" footprint={<YageoRt0603 />} n={n} />
      <R name={`R_VMID${bank}_BOT`} value="1k" a={`VMID${bank}_EXT`} b="GND" jlc="C110776" mpn="RT0603BRD071KL" footprint={<YageoRt0603 />} n={n} />
      <C name={`C_VMID${bank}_EXT_10U`} value="10uF" a={`VMID${bank}_EXT`} b="GND" jlc="C2167576" mpn="C0805C106K8RACTU" footprint="0805" n={n} />
      <C name={`C_VMID${bank}_EXT_1U`} value="1uF" a={`VMID${bank}_EXT`} b="GND" jlc="C2167386" mpn="C0603C105K4RACTU" footprint="0603" n={n} />
    </group>)}
    <Chip name="U_ADC" manufacturerPartNumber="CS5308P-DNR" jlc=""
      footprint={<CirrusCs5308pQfn48 />}
      pinLabels={{ pin1: "ADC_VMID1", pin2: "CONFIG1", pin3: "CONFIG2", pin4: "CONFIG3", pin5: "VDD_A1", pin6: "GND_A1", pin7: "LDO_A_FILT", pin8: "GND_A2", pin9: "VDD_A2", pin10: "CONFIG4", pin11: "CONFIG5", pin12: "ADC_VMID2", pin13: "IN5N", pin14: "IN5P", pin15: "IN6N", pin16: "IN6P", pin17: "ADC_FILT2N", pin18: "ADC_FILT2P", pin19: "IN7N", pin20: "IN7P", pin21: "IN8N", pin22: "IN8P", pin23: "RESET", pin24: "ASP_FSYNC", pin25: "ASP_DOUT1", pin26: "ASP_DOUT2_NC", pin27: "ASP_DOUT3_NC", pin28: "ASP_DOUT4_NC", pin29: "ASP_BCLK", pin30: "GND_D", pin31: "VDD_IO", pin32: "LDO_D_FILT", pin33: "VDD_D", pin34: "MCLK", pin35: "SPI_SDO_I2C_SCL", pin36: "SPI_SCK_HIZ_SEL", pin37: "SPI_SDI_I2C_SDA", pin38: "SPI_CS_BCLK_INV", pin39: "IN1N", pin40: "IN1P", pin41: "IN2N", pin42: "IN2P", pin43: "ADC_FILT1P", pin44: "ADC_FILT1N", pin45: "IN3N", pin46: "IN3P", pin47: "IN4N", pin48: "IN4P", pin49: "EP_GND" }}
      connections={{ pin1: n("VMID1"), pin2: n("CFG1"), pin3: n("CFG2"), pin4: n("GND"), pin5: n("3V3_ADC"), pin6: n("GND"), pin7: n("LDO_A_FILT"), pin8: n("GND"), pin9: n("3V3_ADC"), pin10: n("CFG4"), pin11: n("CFG5"), pin12: n("VMID2"), pin13: n(adcInputNet(5, "N")), pin14: n(adcInputNet(5, "P")), pin15: n(adcInputNet(6, "N")), pin16: n(adcInputNet(6, "P")), pin17: n("GND"), pin18: n("FILT2P"), pin19: n(adcInputNet(7, "N")), pin20: n(adcInputNet(7, "P")), pin21: n(adcInputNet(8, "N")), pin22: n(adcInputNet(8, "P")), pin23: n("ADC_RESET_N"), pin24: n("ADC_FSYNC"), pin25: n("ADC_DOUT1"), pin29: n("ADC_BCLK"), pin30: n("GND"), pin31: n("3V3_ADC"), pin32: n("LDO_D_FILT"), pin33: n("LDO_D_FILT"), pin34: n("ADC_MCLK"), pin35: n("GND"), pin36: n("GND"), pin37: n("GND"), pin38: n("3V3_ADC"), pin39: n(adcInputNet(1, "N")), pin40: n(adcInputNet(1, "P")), pin41: n(adcInputNet(2, "N")), pin42: n(adcInputNet(2, "P")), pin43: n("FILT1P"), pin44: n("GND"), pin45: n(adcInputNet(3, "N")), pin46: n(adcInputNet(3, "P")), pin47: n(adcInputNet(4, "N")), pin48: n(adcInputNet(4, "P")), pin49: n("GND") }} />
    <R name="R_CFG1" value="4.7k" a="CFG1" b="GND" jlc="C105871" mpn="RC0402FR-074K7L" n={n} />
    <R name="R_CFG2" value="0" a="CFG2" b="3V3_ADC" jlc="C106231" mpn="RC0402FR-070RL" n={n} />
    <R name="R_CFG4" value="4.7k" a="CFG4" b="3V3_ADC" jlc="C105871" mpn="RC0402FR-074K7L" n={n} />
    <R name="R_CFG5" value="100k" a="CFG5" b="GND" jlc="C60491" mpn="RC0402FR-07100KL" n={n} />
    {[1, 2].map((bank) => <group key={`filt-${bank}`}>
      <R name={`R_FILT${bank}P`} value="1" a="3V3_ADC" b={`FILT${bank}P`} jlc="C844653" mpn="CRCW12061R00FKEAHP" footprint="1206" n={n} />
      <C name={`C_FILT${bank}_470U`} value="470uF" a={`FILT${bank}P`} b="GND" jlc="C178530" mpn="EEEFK1A471P" footprint={<PanasonicEeeFk8x10 />} polarized n={n} />
      <C name={`C_FILT${bank}_10U`} value="10uF" a={`FILT${bank}P`} b="GND" jlc="C2167576" mpn="C0805C106K8RACTU" footprint="0805" n={n} />
      <C name={`C_FILT${bank}_1U`} value="1uF" a={`FILT${bank}P`} b="GND" jlc="C2167386" mpn="C0603C105K4RACTU" footprint="0603" n={n} />
      <C name={`C_VMID${bank}_4U7`} value="10uF" a={`VMID${bank}`} b="GND" jlc="C2167576" mpn="C0805C106K8RACTU" footprint="0805" n={n} />
      <C name={`C_VMID${bank}_470N`} value="470nF" a={`VMID${bank}`} b="GND" jlc="C318640" mpn="CL10B474KA8NFNC" footprint="0603" n={n} />
    </group>)}
    <C name="C_LDO_A" value="4.7uF" a="LDO_A_FILT" b="GND" jlc="C90791" mpn="GCM21BR71C475KA73L" footprint="0805" n={n} />
    <C name="C_LDO_D" value="4.7uF" a="LDO_D_FILT" b="GND" jlc="C90791" mpn="GCM21BR71C475KA73L" footprint="0805" n={n} />
    <C name="C_VDDA1_4U7" value="4.7uF" a="3V3_ADC" b="GND" jlc="C19666" mpn="CL10A475KO8NNNC" footprint="0603" n={n} />
    <C name="C_VDDA1_10N" value="10nF" a="3V3_ADC" b="GND" jlc="C15195" mpn="CL05B103KB5NNNC" n={n} />
    <C name="C_VDDA2_4U7" value="4.7uF" a="3V3_ADC" b="GND" jlc="C19666" mpn="CL10A475KO8NNNC" footprint="0603" n={n} />
    <C name="C_VDDA2_10N" value="10nF" a="3V3_ADC" b="GND" jlc="C15195" mpn="CL05B103KB5NNNC" n={n} />
    <C name="C_VDDIO" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" n={n} />
  </>
)

const AdcReset = ({ n }: any) => (
  <>
    <Chip name="U_RST1" manufacturerPartNumber="TPS3839K33DBZR" jlc="C96333" footprint="sot23"
      pinLabels={{ pin1: "GND", pin2: "RESET_N", pin3: "VDD" }} connections={{ pin1: n("GND"), pin2: n("POR_N"), pin3: n("3V3_ADC") }} />
    <C name="C_RST1" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" n={n} />
    {/* Both digital rails must be valid before clocks or ADC reset are released.
        Open-drain supervisor outputs form ADC_DIGITAL_OK in the held domain. */}
    <Chip name="U_ADC_1V8_OK" manufacturerPartNumber="TPS389018DSER" jlc="" footprint={<TiDse0006a />}
      pinLabels={{ pin1: "SENSE", pin2: "GND", pin3: "MR_N", pin4: "VDD", pin5: "CT", pin6: "RESET_N" }}
      connections={{ pin1: n("1V8"), pin2: n("GND"), pin3: n("3V3_ADC"), pin4: n("3V3_ADC"), pin6: n("ADC_DIGITAL_OK") }} />
    <Chip name="U_ADC_3V3X_OK" manufacturerPartNumber="TPS389030DSER" jlc="" footprint={<TiDse0006a />}
      pinLabels={{ pin1: "SENSE", pin2: "GND", pin3: "MR_N", pin4: "VDD", pin5: "CT", pin6: "RESET_N" }}
      connections={{ pin1: n("3V3X"), pin2: n("GND"), pin3: n("3V3_ADC"), pin4: n("3V3_ADC"), pin6: n("ADC_DIGITAL_OK") }} />
    <R name="R_ADC_DIGITAL_OK_PU" value="10k" a="3V3_ADC" b="ADC_DIGITAL_OK" jlc="C60490" mpn="RC0402FR-0710KL" n={n} />
    <C name="C_ADC_DIGITAL_OK" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" n={n} />
    {/* Qualify the push-pull POR with the wired-open-drain digital-rail result.
        Disabled output is pulled low. ADC_READY rises only after both are valid. */}
    <Chip name="U_ADC_READY" manufacturerPartNumber="SN74LVC1G125DCKT" jlc="" footprint={<TiDck0005a />}
      pinLabels={{ pin1: "OE_N", pin2: "A", pin3: "GND", pin4: "Y", pin5: "VCC" }}
      connections={{ pin1: n("ADC_DIGITAL_BAD"), pin2: n("POR_N"), pin3: n("GND"), pin4: n("ADC_READY"), pin5: n("3V3_ADC") }} />
    <C name="C_ADC_READY" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" n={n} />
    <R name="R_ADC_READY_PD" value="100k" a="ADC_READY" b="GND" jlc="C60491" mpn="RC0402FR-07100KL" n={n} />
    <Chip name="U_ADC_DIGITAL_BAD" manufacturerPartNumber="SN74LVC1G04DCKR" jlc="" footprint={<TiDck0005a />}
      pinLabels={{ pin1: "NC", pin2: "A", pin3: "GND", pin4: "Y", pin5: "VCC" }}
      connections={{ pin2: n("ADC_DIGITAL_OK"), pin3: n("GND"), pin4: n("ADC_DIGITAL_BAD"), pin5: n("3V3_ADC") }} />
    <C name="C_ADC_DIGITAL_BAD" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" n={n} />
    <Chip name="Q_ADC_DIG_RST" manufacturerPartNumber="2N7002K-7" jlc="C85047" footprint={<Diodes2N7002kSot23 />}
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }} connections={{ pin1: n("ADC_DIGITAL_BAD"), pin2: n("GND"), pin3: n("ADC_RESET_N") }} />
    <R name="R_ADC_DIG_RST_PD" value="100k" a="ADC_DIGITAL_BAD" b="GND" jlc="C60491" mpn="RC0402FR-07100KL" n={n} />
    <Chip name="U_RST2" manufacturerPartNumber="SN74LVC1G123DCTR" jlc="C123302" footprint="ssop8"
      pinLabels={{ pin1: "A", pin2: "B", pin3: "CLR_N", pin4: "GND", pin5: "Q", pin6: "CEXT", pin7: "REXT_CEXT", pin8: "VCC" }}
      connections={{ pin1: n("GND"), pin2: n("ADC_START_DELAY"), pin3: n("ADC_READY"), pin4: n("GND"), pin5: n("RESET_PULSE_H"), pin6: n("RESET_C"), pin7: n("RESET_RC"), pin8: n("3V3_ADC") }} />
    <R name="R_ADC_START_DELAY" value="100k" a="ADC_READY" b="ADC_START_DELAY" jlc="C60491" mpn="RC0402FR-07100KL" n={n} />
    <C name="C_ADC_START_DELAY" value="470nF" a="ADC_START_DELAY" b="GND" jlc="C318640" mpn="CL10B474KA8NFNC" footprint="0603" n={n} />
    <Chip name="U_ADC_READY_BAD" manufacturerPartNumber="SN74LVC1G04DCKR" jlc="" footprint={<TiDck0005a />}
      pinLabels={{ pin1: "NC", pin2: "A", pin3: "GND", pin4: "Y", pin5: "VCC" }}
      connections={{ pin2: n("ADC_READY"), pin3: n("GND"), pin4: n("ADC_READY_BAD"), pin5: n("3V3_ADC") }} />
    <C name="C_ADC_READY_BAD" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" n={n} />
    <R name="R_ADC_DELAY_GATE_PD" value="100k" a="ADC_READY_BAD" b="GND" jlc="C60491" mpn="RC0402FR-07100KL" n={n} />
    <Chip name="Q_ADC_DELAY_DISCH" manufacturerPartNumber="2N7002K-7" jlc="C85047" footprint={<Diodes2N7002kSot23 />}
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }} connections={{ pin1: n("ADC_READY_BAD"), pin2: n("GND"), pin3: n("ADC_START_DELAY") }} />
    <R name="R_RST_T" value="100k" a="3V3_ADC" b="RESET_RC" jlc="C60491" mpn="RC0402FR-07100KL" n={n} />
    <C name="C_RST_T" value="220nF" a="RESET_C" b="RESET_RC" jlc="C21120" mpn="CL10B224KA8NNNC" footprint="0603" n={n} />
    <C name="C_RST2" value="100nF" a="3V3_ADC" b="GND" jlc="C1525" mpn="CL05B104KO5NNNC" n={n} />
    <Chip name="Q_RST1" manufacturerPartNumber="2N7002K-7" jlc="C85047" footprint={<Diodes2N7002kSot23 />}
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }} connections={{ pin1: n("RESET_PULSE_H"), pin2: n("GND"), pin3: n("ADC_RESET_N") }} />
    <R name="R_RESET_PU" value="10k" a="3V3_ADC" b="ADC_RESET_N" jlc="C60490" mpn="RC0402FR-0710KL" n={n} />
    <R name="R_RESET_GPD" value="100k" a="RESET_PULSE_H" b="GND" jlc="C60491" mpn="RC0402FR-07100KL" n={n} />
  </>
)

export const CrowRetainedAnalog = ({ net = defaultNet }: CrowRetainedAnalogProps) => (
  <>
    {Array.from({ length: 8 }, (_, i) => <Spoke key={`spoke-${i + 1}`} index={i + 1} n={net} />)}
    {Array.from({ length: 8 }, (_, i) => <AnalogChannel key={`channel-${i + 1}`} index={i + 1} vmid={i < 4 ? "VMID1_EXT" : "VMID2_EXT"} n={net} />)}
    <QuietAnalogPower n={net} />
    <AdcReferenceAndMode n={net} />
    <AdcReset n={net} />
  </>
)
