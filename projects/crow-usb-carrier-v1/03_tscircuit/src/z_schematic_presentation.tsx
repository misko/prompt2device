import React, { Fragment, isValidElement } from "react"
import { chipStyle as analogChipStyle, poseFor as analogPoseFor } from "./z_analog_schematic_presentation"

type Domain = "analog" | "power" | "digital" | "usb"
type Pose = { schSheetName: string; schSectionName: string; schX: number; schY: number; schRotation?: number }

const powerPoses: Record<string, [string, number, number, number?]> = {
  J_PWR:["power_input",-14,4], F_IN:["power_input",-10,4], Q_IN:["power_input",-5,4],
  R_QIN_G:["power_input",-5,-2,-90], D_QIN_GS:["power_input",0,1], D_IN:["power_input",5,1],
  C_IN1:["power_input",8,4,-90], C_IN2:["power_input",11,4,-90], C_IN3:["power_input",14,4,-90], C_IN_HF:["power_input",17,4,-90],
  U_BUCK:["power_buck",0,2], R_RT:["power_buck",-8,-3,-90], R_AGND_JOIN:["power_buck",-3,-5],
  C_VCC:["power_buck",5,-4,-90], C_VLDO:["power_buck",8,-4,-90],
  C_OUT1:["power_buck",7,3,-90], C_OUT2:["power_buck",10,3,-90], C_OUT3:["power_buck",13,3,-90],
}

const digitalPage = (ref: string) => {
  if (ref === "U_XU") return "xmos_core"
  if (/^C_XU_|^FB_PLL$|^C_PLL_/.test(ref)) return "xmos_decoupling"
  if (/^(U_|C_U_)(3V3X|1V8|CORE)|^L_U_(3V3X|1V8|CORE)$|^R_CORE_|^C_CORE_|^U_1V8_OK$|^U_XU_3V3_OK$|^C_XU_3V3_OK_|^C_1V8|^R_XU_RST/.test(ref)) return "digital_power"
  if (/FLASH|QSPI|XTAL|^Y_XU$/.test(ref)) return "flash_clock"
  if (/JTAG/.test(ref)) return "debug"
  if (/VBUS/.test(ref)) return "usb_logic"
  if (/^Y_AUDIO$|^C_AUDIO_OSC$/.test(ref)) return "audio_oscillator"
  if (/^U_TDM_XLATE$|^C_XLATE_|^R_ADC_DATA_PD$|^R_(BCLK|FSYNC)_RAW_PD$/.test(ref)) return "tdm_translation"
  if (/^U_FSYNC_|^U_BCLK_INV$|^C_FSYNC_|^C_FSYNC_INV$/.test(ref)) return "fsync_shaping"
  return "adc_clock_control"
}

const counters: Record<string, number> = {}
const decouplingRefs = [
  "C_XU_VDD_5","C_XU_VDD_11","C_XU_VDD_14","C_XU_VDD_18","C_XU_VDD_39",
  "C_XU_VDD_45","C_XU_VDD_50","C_XU_VDD_54","C_XU_VDD_68","C_XU_VDD_85",
  "C_XU_VDD_95","C_XU_VDD_104","C_XU_VDD_105","C_XU_VDD_106","C_XU_VDD_113",
  "C_XU_VDDIO_10","C_XU_VDDIO_17","C_XU_VDDIO_35","C_XU_VDDIO_56",
  "C_XU_VDDIO_72","C_XU_VDDIO_89","C_XU_VDDIO_109","C_XU_VDDIO_121",
]
const explicitDigitalPose = (ref: string): Pose | undefined => {
  const flash: Record<string,[number,number,number?]> = {
    U_FLASH:[-7,-1], R_QSPI_CS:[-3,4,-90], C_FLASH:[-3,-5,-90],
    Y_XU:[0,-1], R_XTAL_DRIVE:[7,-1], R_XTAL_FB:[3,5],
    C_XTAL_IN:[8,5,-90], C_XTAL_OUT:[12,5,-90],
  }
  if (flash[ref]) { const p=flash[ref]; return {schSheetName:"flash_clock",schSectionName:"flash_clock",schX:p[0],schY:p[1],schRotation:p[2]??0} }
  const i=decouplingRefs.indexOf(ref)
  if (i>=0) return {schSheetName:"xmos_decoupling",schSectionName:"xmos_decoupling",
    schX:(i%8)*4-14,schY:8-Math.floor(i/8)*5,schRotation:-90}
  const support: Record<string,[number,number,number?]> = {
    C_XU_3V3_OK_VDD:[-12,-9,-90], C_XU_3V3_OK_CT:[-8,-9,-90],
    C_XU_USB33:[-2,-9,-90], C_XU_USB18:[2,-9,-90],
    FB_PLL:[8,-8], C_PLL_1U:[12,-8,-90], C_PLL_100N:[16,-8,-90],
  }
  if (support[ref]) { const p=support[ref]; return {schSheetName:"xmos_decoupling",schSectionName:"xmos_decoupling",schX:p[0],schY:p[1],schRotation:p[2]??0} }
}
const gridPose = (sheet: string): Pose => {
  const i = counters[sheet] ?? 0
  counters[sheet] = i + 1
  const columns = sheet === "xmos_decoupling" ? 6 : 5
  return { schSheetName: sheet, schSectionName: sheet,
    schX: (i % columns) * 8 - (columns - 1) * 4,
    schY: 14 - Math.floor(i / columns) * 6,
    schRotation: /decoupling|power/.test(sheet) ? -90 : 0 }
}

const xmosArrangement = {
  leftSide: Array.from({length:32},(_,i)=>i+1),
  topSide: Array.from({length:32},(_,i)=>i+33),
  rightSide: Array.from({length:32},(_,i)=>96-i),
  bottomSide: [...Array.from({length:32},(_,i)=>128-i),129],
}

const pose = (domain: Domain, ref: string, existing: any): Pose => {
  if (domain === "analog") {
    const p=analogPoseFor(ref)
    return p.schSheetName === "buck" ? {...p,schSheetName:"analog_power_aux",schSectionName:"Analog rail bulk and bleed"} : p
  }
  if (domain === "power") {
    const p = powerPoses[ref]
    if (!p) throw new Error(`No power schematic pose: ${ref}`)
    return {schSheetName:p[0],schSectionName:p[0],schX:p[1],schY:p[2],schRotation:p[3]??0}
  }
  if (domain === "usb") {
    const positions: Record<string, [number, number, number?]> = {
      J_USB: [-7, 0], U_USB_ESD: [1, 4], U_USB_VBUS_ESD: [1, 8],
      U_USB_CC_ESD: [1, -3], R_USB_CC1: [-4, -6, -90], R_USB_CC2: [0, -6, -90],
      C_USB_VBUS: [5, 8, -90], R_USB_VBUS_BLEED: [5, 11, -90],
    }
    const p = positions[ref]
    if (!p) throw new Error(`No USB schematic pose: ${ref}`)
    return {schSheetName:"usb_frontend",schSectionName:"USB Type-C device front end",
      schX:p[0],schY:p[1],schRotation:p[2]??0}
  }
  if (ref === "U_XU") return {schSheetName:"xmos_core",schSectionName:"XU316 core and ports",schX:0,schY:0}
  const explicit=explicitDigitalPose(ref)
  if (explicit) return explicit
  return gridPose(digitalPage(ref))
}

const style = (domain: Domain, ref: string, tag: string) => {
  if (tag !== "chip") return {}
  if (domain === "analog") return analogChipStyle(ref)
  if (ref === "U_XU") return {schWidth:16,schHeight:20,schPinArrangement:xmosArrangement,
    schPinStyle:Object.fromEntries(Array.from({length:129},(_,i)=>[`pin${i+1}`,{topMargin:.08,bottomMargin:.08}]))}
  if (ref === "Y_XU") return {schWidth:3.5}
  return {}
}

const expand = (node: any, domain: Domain, page?: string): any => {
  if (node == null || typeof node === "boolean") return node
  if (Array.isArray(node)) return node.map((child) => expand(child, domain, page))
  if (!isValidElement(node)) return node
  const element: any = node
  if (element.type === Fragment) return <>{React.Children.map(element.props.children, (child) => expand(child, domain, page))}</>
  if (typeof element.type === "function") return expand(element.type(element.props), domain, page)
  const children = React.Children.map(element.props.children, (child) => expand(child, domain, page))
  const ref = element.props.name
  if (typeof element.type === "string" && ref && ["chip","resistor","capacitor","inductor","diode","fuse","crystal"].includes(element.type)) {
    const schematicPose=pose(domain, ref, element.props)
    if (page && schematicPose.schSheetName !== page) return null
    return React.cloneElement(element, {...schematicPose,...style(domain, ref, element.type)}, children)
  }
  return React.cloneElement(element, {}, children)
}

export const Presented = ({domain, page, children}:{domain:Domain;page?:string;children:any}) => {
  for (const key of Object.keys(counters)) delete counters[key]
  return expand(children,domain,page)
}
