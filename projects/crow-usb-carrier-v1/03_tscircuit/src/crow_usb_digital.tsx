import { MurataGrm32e1210 } from "./z_power_aux_footprints"
import { Fragment } from "react"
/**
 * Conditional XU316 USB-audio digital-core hardware source.
 * No firmware, XN, USB descriptor, or production board is generated here.
 * Parent supplies protected 5V_BUCK and connector/ESD nets USB_DP/USB_DN/VBUS_USB.
 */
export const CROW_DIGITAL_BOUNDARY_NETS = {
  powerInputs: ["5V_BUCK", "GND"], usbInputs: ["USB_DP", "USB_DN", "VBUS_USB"],
  analogInterface: ["ADC_BCLK", "ADC_FSYNC", "ADC_DOUT1", "ADC_I2C_SCL", "ADC_I2C_SDA", "3V3_ADC"],
  debug: ["JTAG_TDI", "JTAG_TDO", "JTAG_TMS", "JTAG_TCK", "XU_RESET_N"],
} as const
export interface CrowUsbDigitalProps { net?: (canonicalName: string) => string }
const defaultNet=(name:string)=>`net.${ /^\d/.test(name) ? `N${name}` : name }`
const supplier=(jlc:string)=>({jlcpcb:jlc?[jlc]:[]})
const sourced=(mpn:string,jlc="")=>jlc||({
 "XFL4015-471MEC":"C18221164","SX5M24.576M20F30TNN":"C2901534","CC0402KRX5R5BB105":"C106253","X322524MOB4SI":"C70590","FTSH-105-01-L-DV-K":"C5155080",
 "GRM1555C1H220JA01D":"C76960","GRM1555C1H102JA01D":"C76947","RC0402FR-0733RL":"C138002","RC0402FR-0710KL":"C60490","RC0402FR-07100KL":"C60491","RC0402FR-071ML":"C138033","RC0402FR-074K7L":"C105871","GRM155R71H103KA88D":"C77019","CL21A106KOQNNNE":"C1713","CRCW0402680RFKED":"C482224",
 "RT0402BRD07100KL":"C852472","RT0402BRD0749K9L":"C852808","RT0402BRD07200KL":"C728556","RT0402BRD07210KL":"C852631","ARG03BTC4533":"C2686428","RT0603BRD07100KL":"C122538","CC0402JRNPO9BN121":"C106996","SN74AUP3G34DCUR":"C2675543",
 "SN74AXC4T245PWR":"C2867798","SN74LVC1G04DCKR":"C8207","SN74LVC1G125DCKT":"C2675550","TCA9406DCUR":"C840107",
 "SN74LVC1G332DBVR":"C43368","SN74LVC2G74DCTR":"C79339","TPS3808G09DBVR":"C24584",
 "TPS62822DLCR":"C473385"
 } as Record<string,string>)[mpn]||""
const Chip=({jlc="",manufacturerPartNumber,...props}:any)=><chip manufacturerPartNumber={manufacturerPartNumber} supplierPartNumbers={supplier(sourced(manufacturerPartNumber,jlc))} {...props} />
const R=({name,value,a,b,mpn,jlc="",footprint="0402",n}:any)=><resistor name={name} resistance={value} footprint={footprint} manufacturerPartNumber={mpn} supplierPartNumbers={supplier(sourced(mpn,jlc))} connections={{pin1:n(a),pin2:n(b)}} />
const C=({name,value,a,b,mpn="CL05B104KO5NNNC",jlc="",footprint="0402",n}:any)=>{
 const exactJlc=sourced(mpn,jlc || (mpn==="CL05B104KO5NNNC" && value==="100nF" ? "C1525" : ""));
 return <capacitor name={name} capacitance={value} footprint={footprint} manufacturerPartNumber={mpn} supplierPartNumbers={supplier(exactJlc)} connections={{pin1:n(a),pin2:n(b)}} />
}

const XU_NC_PINS=Object.freeze([6, 7, 9, 12, 13, 15, 16, 19, 21, 25, 26, 28, 29, 31, 32, 46, 47, 48, 49, 53, 55, 57, 58, 63, 64, 65, 66, 67, 69, 70, 71, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 86, 87, 88, 90, 91, 92, 96, 97, 98, 99, 100, 101, 102, 103, 108, 110, 111, 112, 114, 115, 116, 117, 118, 119, 120, 122, 123, 124, 125, 126])
const XU_CONNECTED_PINS=Object.freeze([1, 2, 3, 4, 5, 8, 10, 11, 14, 17, 18, 20, 22, 23, 24, 27, 30, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 50, 51, 52, 54, 56, 59, 60, 61, 62, 68, 72, 85, 89, 93, 94, 95, 104, 105, 106, 107, 109, 113, 121, 127, 128, 129])
function assertXUPinCoverage(){
 const all=[...XU_NC_PINS,...XU_CONNECTED_PINS];
 if(all.length!==129 || new Set(all).size!==129 || Math.min(...all)!==1 || Math.max(...all)!==129)
   throw new Error("XU316 coverage must classify every physical pin 1..128 and EP129 exactly once")
}

/** 14x14 mm, 0.4-mm pitch TQFP plus 4.7-mm exposed-pad land. No thermal vias are claimed here. */
function XU316TQ128EPFootprint(){
 const side=(start:number,axis:"x"|"y",fixed:number,reverse=false)=>Array.from({length:32},(_,i)=>{
   const along=(reverse?15.5-i:i-15.5)*0.4; const x=axis==="x"?along:fixed; const y=axis==="y"?along:fixed;
   return <Fragment key={start+i}><smtpad portHints={[String(start+i)]} pcbX={`${x}mm`} pcbY={`${y}mm`} width={axis==="x"?"0.22mm":"1.5mm"} height={axis==="y"?"0.22mm":"1.5mm"} shape="rect" /></Fragment>
 });
 return <footprint>
  {side(1,"x",-7.65)} {side(33,"y",7.65)} {side(65,"x",7.65,true)} {side(97,"y",-7.65,true)}
  <smtpad portHints={["129"]} pcbX="0mm" pcbY="0mm" width="4.7mm" height="4.7mm" shape="rect" />
 </footprint>
}

/** Source-owned lands for package names the pinned footprinter cannot expand. */
const P=({n,x,y,w,h}:any)=><smtpad portHints={[String(n)]} pcbX={`${x}mm`} pcbY={`${y}mm`} width={`${w}mm`} height={`${h}mm`} shape="rect" />
/** Coilcraft XFL4015 Document 769-2: 0.98 x 3.4-mm lands on 2.37-mm pitch. Pin 1 (left) is marked winding start and faces the high-dv/dt switch node. */
function CoilcraftXFL4015Land(){return <footprint><P n={1} x={-1.185} y={0} w={0.98} h={3.4}/><P n={2} x={1.185} y={0} w={0.98} h={3.4}/></footprint>}
// SCTF SCTF20215M027 p.4: 2.54 x 2.3 mm pad-center pitch, 1.8 x 1.3 mm lands.
// Source Y increases upward; physical top view has 4/3 above 1/2.
function Osc5032Land(){return <footprint><P n={1} x={-1.27} y={-1.15} w={1.8} h={1.3}/><P n={2} x={1.27} y={-1.15} w={1.8} h={1.3}/><P n={3} x={1.27} y={1.15} w={1.8} h={1.3}/><P n={4} x={-1.27} y={1.15} w={1.8} h={1.3}/></footprint>}
/** YXC YSX321SL top view: upper 4/3, lower 1/2. tscircuit Y is up;
 * circuit_json_to_kicad_pcb.py flips Y for the native KiCad Y-down footprint. */
function YxcYSX321SLLand(){return <footprint><P n={1} x={-1.1} y={-0.85} w={1.4} h={1.2}/><P n={2} x={1.1} y={-0.85} w={1.4} h={1.2}/><P n={3} x={1.1} y={0.85} w={1.4} h={1.2}/><P n={4} x={-1.1} y={0.85} w={1.4} h={1.2}/></footprint>}
/** TI SCES214AF DCK0005A land pattern example, PDF p.35: 0.95 x 0.40, 2.20 row spacing. TSX Y-up reflects native Y-down. */
function SC70_5Land(){return <footprint><P n={1} x={-1.1} y={0.65} w={0.95} h={0.4}/><P n={2} x={-1.1} y={0} w={0.95} h={0.4}/><P n={3} x={-1.1} y={-0.65} w={0.95} h={0.4}/><P n={4} x={1.1} y={-0.65} w={0.95} h={0.4}/><P n={5} x={1.1} y={0.65} w={0.95} h={0.4}/></footprint>}
/** TI SCES203Q DCT0008A land pattern example, PDF p.20: 1.10 x 0.40, 3.80 row spacing. TSX Y-up reflects native Y-down. */
function SM8_DCTLand(){return <footprint>{[1,2,3,4].map((n,i)=><P key={n} n={n} x={-1.9} y={(1.5-i)*0.65} w={1.1} h={0.4}/>)}{[5,6,7,8].map((n,i)=><P key={n} n={n} x={1.9} y={(i-1.5)*0.65} w={1.1} h={0.4}/>)}</footprint>}
/** Samtec FTSH-DV Rev H recommended PCB layout, sheet 1: 2.79 x 0.74, 4.07 row spacing. TSX Y-up reflects native Y-down. */
function FTSH2x5Land(){return <footprint>{Array.from({length:10},(_,i)=>{const row=Math.floor(i/2),col=i%2;return <P key={i+1} n={i+1} x={col?2.035:-2.035} y={(row-2)*1.27} w={2.79} h={0.74}/>})}</footprint>}
/** TI drawing 4220552/B: DSE0006A, 0.5-mm pitch, 0.25 x 0.7-mm lands. */
/** TI DSE0006A 4220552/B land pattern, TPS3890 PDF p.25: pin 1 is 0.8 x 0.25; other five are 0.7 x 0.25. */
function DSE0006ALand(){return <footprint>{[1,2,3].map((n,i)=><P key={n} n={n} x={n===1?-0.55:-0.6} y={(1-i)*0.5} w={n===1?0.8:0.7} h={0.25}/>)}{[4,5,6].map((n,i)=><P key={n} n={n} x={0.6} y={(i-1)*0.5} w={0.7} h={0.25}/>)}</footprint>}
/** TI TCA9406 DCU0008A drawing 4225266/A: 0.5-mm pitch,
 * 8×0.85×0.30-mm lands on 3.1-mm opposite pad-center lines. */
function Tca9406DcuLand(){return <footprint>{[1,2,3,4].map((n,i)=><P key={n} n={n} x={-1.55} y={(1.5-i)*0.5} w={0.85} h={0.3}/>)}{[5,6,7,8].map((n,i)=><P key={n} n={n} x={1.55} y={(i-1.5)*0.5} w={0.85} h={0.3}/>)}</footprint>}
/** TI SCES766C DCU0008A land pattern example, PDF p.24: 0.5-mm pitch, 0.85 x 0.30-mm lands, 3.1-mm row spacing. */
function Dcu0008ALand(){return <footprint>{[1,2,3,4].map((n,i)=><P key={n} n={n} x={-1.55} y={(1.5-i)*0.5} w={0.85} h={0.3}/>)}{[5,6,7,8].map((n,i)=><P key={n} n={n} x={1.55} y={(i-1.5)*0.5} w={0.85} h={0.3}/>)}</footprint>}
/** TI TPS6282x Rev C DLC0008B pp.29-31: 0.60 × 0.25-mm lands, 0.5-mm pitch. Source Y is up. */
function Dlc0008BLand(){return <footprint>{[1,2,3,4].map((n,i)=><P key={n} n={n} x={-0.65} y={0.75-i*0.5} w={0.6} h={0.25}/>)}{[5,6,7,8].map((n,i)=><P key={n} n={n} x={0.65} y={-0.75+i*0.5} w={0.6} h={0.25}/>)}</footprint>}

// TI TPS6282x Rev C: NC pin 4 and unused open-drain PG pin 8 stay open.
const buckPins={pin1:"EN",pin2:"FB",pin3:"AGND",pin4:"NC",pin5:"PGND",pin6:"SW",pin7:"VIN",pin8:"PG"}
function Buck({name,mpn,out,adjustable=false,en="5V_BUCK",n}:any){return <>
 <Chip name={name} manufacturerPartNumber={mpn} jlc="" footprint={<Dlc0008BLand/>} pinLabels={buckPins}
  connections={{pin1:n(en),pin2:n(adjustable?`${name}_FB`:out),pin3:n("GND"),pin5:n("GND"),pin6:n(`${name}_SW`),pin7:n("5V_BUCK")}} />
 <Chip name={`L_${name}`} manufacturerPartNumber="XFL4015-471MEC" jlc="" footprint={<CoilcraftXFL4015Land/>} pinLabels={{pin1:"1",pin2:"2"}} connections={{pin1:n(`${name}_SW`),pin2:n(out)}} />
 {[1,2].map(i=><C key={`in${i}`} name={`C_${name}_IN_${i}`} value="10uF" a="5V_BUCK" b="GND" mpn="CL21A106KOQNNNE" footprint="0805" n={n} />)}
 <C name={`C_${name}_OUT_1`} value="47uF" a={out} b="GND" mpn="GRM32ER71A476KE15L" jlc="C84494" footprint={<MurataGrm32e1210/>} n={n} />
 </>}

export function CrowUsbDigital({net=defaultNet}:CrowUsbDigitalProps={}){
 const n=net; assertXUPinCoverage();
 return <>
  <Buck name="U_3V3X" mpn="TPS62822DLCR" out="3V3X" adjustable n={n} />
  <R name="R_3V3X_FB_TOP" value="453k" a="3V3X" b="U_3V3X_FB" mpn="ARG03BTC4533" footprint="0603" n={n} />
  <R name="R_3V3X_FB_BOTTOM" value="100k" a="U_3V3X_FB" b="GND" mpn="RT0603BRD07100KL" footprint="0603" n={n} />
  <C name="C_3V3X_FF" value="120pF" a="3V3X" b="U_3V3X_FB" mpn="CC0402JRNPO9BN121" n={n} />
  <Buck name="U_1V8" mpn="TPS62822DLCR" out="1V8" adjustable n={n} />
  <R name="R_1V8_FB_TOP" value="210k" a="1V8" b="U_1V8_FB" mpn="RT0402BRD07210KL" n={n} />
  <R name="R_1V8_FB_BOTTOM" value="100k" a="U_1V8_FB" b="GND" mpn="RT0402BRD07100KL" n={n} />
  <C name="C_1V8_FF" value="120pF" a="1V8" b="U_1V8_FB" mpn="CC0402JRNPO9BN121" n={n} />
  <Buck name="U_CORE" mpn="TPS62822DLCR" out="0V9" adjustable en="CORE_EN" n={n} />
  <R name="R_CORE_FB_TOP" value="49.9k" a="0V9" b="U_CORE_FB" mpn="RT0402BRD0749K9L" n={n} />
  <R name="R_CORE_FB_BOTTOM" value="100k" a="U_CORE_FB" b="GND" mpn="RT0402BRD07100KL" n={n} />
  <C name="C_CORE_FF" value="120pF" a="0V9" b="U_CORE_FB" mpn="CC0402JRNPO9BN121" n={n} />
  <R name="R_1V8_OK_TOP" value="52.3k" a="1V8" b="U_1V8_OK_SENSE" mpn="RT0402BRD0752K3L" jlc="C852832" n={n} />
  <R name="R_1V8_OK_BOT" value="100k" a="U_1V8_OK_SENSE" b="GND" mpn="RT0402BRD07100KL" jlc="C852472" n={n} />
  <Chip name="U_1V8_OK" manufacturerPartNumber="TPS389001DSER" jlc="C1509297" footprint={<DSE0006ALand/>}
   pinLabels={{pin1:"SENSE",pin2:"GND",pin3:"MR_N",pin4:"VDD",pin5:"CT",pin6:"RESET_N"}}
   connections={{pin1:n("U_1V8_OK_SENSE"),pin2:n("GND"),pin3:n("5V_BUCK"),pin4:n("5V_BUCK"),pin5:n("CORE_EN_CT"),pin6:n("CORE_EN")}} />
  <C name="C_1V8_OK_VDD" value="100nF" a="5V_BUCK" b="GND" n={n} />
  <C name="C_CORE_EN_CT" value="10nF" a="CORE_EN_CT" b="GND" mpn="GRM155R71H103KA88D" jlc="" n={n} />
  <R name="R_CORE_EN_PU" value="10k" a="1V8" b="CORE_EN" mpn="RC0402FR-0710KL" n={n} />
  <Chip name="U_CORE_OK" manufacturerPartNumber="TPS3808G09DBVR" jlc="" footprint="sot23_6"
   pinLabels={{pin1:"RESET_N",pin2:"GND",pin3:"MR_N",pin4:"CT_NC",pin5:"SENSE",pin6:"VDD"}}
   connections={{pin1:n("XU_RESET_N"),pin2:n("GND"),pin3:n("1V8"),pin5:n("0V9"),pin6:n("1V8")}} />
  <C name="C_CORE_OK" value="100nF" a="1V8" b="GND" n={n} />
  {/* Wired-open-drain reset also qualifies the independently generated 3V3X USB rail.
      Core release remains downstream of U_1V8_OK, so its delay bounds flash readiness. */}
  <R name="R_XU_3V3_OK_TOP" value="169k" a="3V3X" b="U_XU_3V3_OK_SENSE" mpn="RT0402BRD07169KL" jlc="C852555" n={n} />
  <R name="R_XU_3V3_OK_BOT" value="100k" a="U_XU_3V3_OK_SENSE" b="GND" mpn="RT0402BRD07100KL" jlc="C852472" n={n} />
  <Chip name="U_XU_3V3_OK" manufacturerPartNumber="TPS389001DSER" jlc="C1509297" footprint={<DSE0006ALand/>}
   pinLabels={{pin1:"SENSE",pin2:"GND",pin3:"MR_N",pin4:"VDD",pin5:"CT",pin6:"RESET_N"}}
   connections={{pin1:n("U_XU_3V3_OK_SENSE"),pin2:n("GND"),pin3:n("5V_BUCK"),pin4:n("5V_BUCK"),pin5:n("XU_3V3_OK_CT"),pin6:n("XU_RESET_N")}} />
  <C name="C_XU_3V3_OK_VDD" value="100nF" a="5V_BUCK" b="GND" n={n} />
  <C name="C_XU_3V3_OK_CT" value="1nF" a="XU_3V3_OK_CT" b="GND" mpn="GRM1555C1H102JA01D" jlc="" n={n} />
  <R name="R_XU_RST_PU" value="10k" a="1V8" b="XU_RESET_N" mpn="RC0402FR-0710KL" n={n} />

  <Chip name="U_XU" manufacturerPartNumber="XU316-1024-TQ128-C24" jlc="C6362698" footprint={<XU316TQ128EPFootprint />}
   pinLabels={{
    pin1: "X0D06",
    pin2: "X0D01",
    pin3: "X0D07",
    pin4: "X0D10",
    pin5: "VDD",
    pin6: "X0D00_NC",
    pin7: "X0D11_NC",
    pin8: "X0D14",
    pin9: "X0D16_NC",
    pin10: "VDDIOL",
    pin11: "VDD",
    pin12: "X1D36_NC",
    pin13: "X1D37_NC",
    pin14: "VDD",
    pin15: "X1D38_NC",
    pin16: "X1D39_NC",
    pin17: "VDDIOL",
    pin18: "VDD",
    pin19: "X1D00_NC",
    pin20: "X1D01",
    pin21: "X1D09_NC",
    pin22: "X1D10",
    pin23: "X1D11",
    pin24: "MIPI_VDD18",
    pin25: "MIPI_DN2_NC",
    pin26: "MIPI_DP2_NC",
    pin27: "MIPI_VDD09",
    pin28: "MIPI_DN1_NC",
    pin29: "MIPI_DP1_NC",
    pin30: "VSS",
    pin31: "MIPI_DN0_NC",
    pin32: "MIPI_DP0_NC",
    pin33: "XOUT",
    pin34: "XIN",
    pin35: "VDDIOB18",
    pin36: "TDI",
    pin37: "TDO",
    pin38: "RST_N",
    pin39: "VDD",
    pin40: "LV_L_N",
    pin41: "PLL_AVDD",
    pin42: "PLL_AGND",
    pin43: "LV_T_N",
    pin44: "TMS",
    pin45: "VDD",
    pin46: "X0D12_NC",
    pin47: "X0D13_NC",
    pin48: "X0D22_NC",
    pin49: "X0D23_NC",
    pin50: "VDD",
    pin51: "TCK",
    pin52: "LV_R_N",
    pin53: "X1D12_NC",
    pin54: "VDD",
    pin55: "NC_NC",
    pin56: "VDDIOB18",
    pin57: "X1D23_NC",
    pin58: "USB_ID_NC",
    pin59: "USB_DN",
    pin60: "USB_DP",
    pin61: "USB_VDD33",
    pin62: "USB_VDD18",
    pin63: "X1D14_NC",
    pin64: "X1D13_NC",
    pin65: "X1D15_NC",
    pin66: "X1D16_NC",
    pin67: "X1D17_NC",
    pin68: "VDD",
    pin69: "X1D18_NC",
    pin70: "X1D19_NC",
    pin71: "X1D20_NC",
    pin72: "VDDIOR",
    pin73: "X1D21_NC",
    pin74: "X1D22_NC",
    pin75: "X1D49_NC",
    pin76: "X1D50_NC",
    pin77: "X1D51_NC",
    pin78: "X1D52_NC",
    pin79: "X1D53_NC",
    pin80: "X1D54_NC",
    pin81: "X1D55_NC",
    pin82: "X1D56_NC",
    pin83: "X1D57_NC",
    pin84: "X1D58_NC",
    pin85: "VDD",
    pin86: "X0D24_NC",
    pin87: "X0D25_NC",
    pin88: "X0D26_NC",
    pin89: "VDDIOR",
    pin90: "X0D27_NC",
    pin91: "X0D28_NC",
    pin92: "X0D29_NC",
    pin93: "X0D35_I2C_SCL",
    pin94: "X0D36_I2C_SDA",
    pin95: "VDD",
    pin96: "X0D37_NC",
    pin97: "X0D38_NC",
    pin98: "X0D40_NC",
    pin99: "X0D39_NC",
    pin100: "X0D42_NC",
    pin101: "X0D41_NC",
    pin102: "X1D43_NC",
    pin103: "X0D43_NC",
    pin104: "VDD",
    pin105: "VDD",
    pin106: "VDD",
    pin107: "X1D24",
    pin108: "X1D25_NC",
    pin109: "VDDIOT",
    pin110: "X1D26_NC",
    pin111: "X1D27_NC",
    pin112: "X1D28_NC",
    pin113: "VDD",
    pin114: "X1D29_NC",
    pin115: "X1D30_NC",
    pin116: "X1D31_NC",
    pin117: "X1D32_NC",
    pin118: "X1D33_NC",
    pin119: "X1D34_NC",
    pin120: "X1D35_NC",
    pin121: "VDDIOT",
    pin122: "X0D30_NC",
    pin123: "X0D32_NC",
    pin124: "X0D31_NC",
    pin125: "X0D34_NC",
    pin126: "X0D33_NC",
    pin127: "X0D04",
    pin128: "X0D05",
    pin129: "EP"
   }}
   connections={{
    pin1: n("QSPI_D2"),
    pin2: n("QSPI_CS_N"),
    pin3: n("QSPI_D3"),
    pin4: n("QSPI_CLK"),
    pin5: n("0V9"),
    pin8: n("VBUS_PRESENT_N"),
    pin10: n("1V8"),
    pin11: n("0V9"),
    pin14: n("0V9"),
    pin17: n("1V8"),
    pin18: n("0V9"),
    pin20: n("TDM_FSYNC_1V8"),
    pin22: n("TDM_BCLK_1V8"),
    pin23: n("AUDIO_MCLK_1V8"),
    pin24: n("GND"),
    pin27: n("GND"),
    pin30: n("GND"),
    pin33: n("XTAL_OUT"),
    pin34: n("XTAL_IN"),
    pin35: n("1V8"),
    pin36: n("JTAG_TDI"),
    pin37: n("JTAG_TDO"),
    pin38: n("XU_RESET_N"),
    pin39: n("0V9"),
    pin40: n("GND"),
    pin41: n("PLL_0V9"),
    pin42: n("GND"),
    pin43: n("GND"),
    pin44: n("JTAG_TMS"),
    pin45: n("0V9"),
    pin50: n("0V9"),
    pin51: n("JTAG_TCK"),
    pin52: n("GND"),
    pin54: n("0V9"),
    pin56: n("1V8"),
    pin59: n("USB_DN"),
    pin60: n("USB_DP"),
    pin61: n("3V3X"),
    pin62: n("1V8"),
    pin68: n("0V9"),
    pin72: n("1V8"),
    pin85: n("0V9"),
    pin89: n("1V8"),
    pin93: n("XU_I2C_SCL_1V8"),
    pin94: n("XU_I2C_SDA_1V8"),
    pin95: n("0V9"),
    pin104: n("0V9"),
    pin105: n("0V9"),
    pin106: n("0V9"),
    pin107: n("TDM_DATA_1V8"),
    pin109: n("1V8"),
    pin113: n("0V9"),
    pin121: n("1V8"),
    pin127: n("QSPI_D0"),
    pin128: n("QSPI_D1"),
    pin129: n("GND")
   }} />

  {[5,11,14,18,39,45,50,54,68,85,95,104,105,106,113].map(p=><C key={`core${p}`} name={`C_XU_VDD_${p}`} value="100nF" a="0V9" b="GND" n={n} />)}
  {[10,17,35,56,72,89,109,121].map(p=><C key={`io${p}`} name={`C_XU_VDDIO_${p}`} value="100nF" a="1V8" b="GND" n={n} />)}
  <C name="C_XU_USB33" value="100nF" a="3V3X" b="GND" n={n} /><C name="C_XU_USB18" value="100nF" a="1V8" b="GND" n={n} />
  <Chip name="FB_PLL" manufacturerPartNumber="BLM15AG601SN1D" jlc="C76884" footprint="0402" pinLabels={{pin1:"1",pin2:"2"}} connections={{pin1:n("0V9"),pin2:n("PLL_0V9")}} />
  <C name="C_PLL_1U" value="1uF" a="PLL_0V9" b="GND" mpn="CC0402KRX5R5BB105" n={n} /><C name="C_PLL_100N" value="100nF" a="PLL_0V9" b="GND" n={n} />

  <Chip name="Y_XU" manufacturerPartNumber="X322524MOB4SI" jlc="C70590" footprint={<YxcYSX321SLLand/>}
   pinLabels={{pin1:"X1",pin2:"CASE",pin3:"X2",pin4:"CASE"}} connections={{pin1:n("XTAL_IN_R"),pin2:n("GND"),pin3:n("XTAL_OUT"),pin4:n("GND")}} />
  <R name="R_XTAL_DRIVE" value="680" a="XTAL_IN" b="XTAL_IN_R" mpn="CRCW0402680RFKED" n={n} />
  <R name="R_XTAL_FB" value="1M" a="XTAL_IN" b="XTAL_OUT" mpn="RC0402FR-071ML" n={n} />
  <C name="C_XTAL_IN" value="22pF" a="XTAL_IN_R" b="GND" mpn="GRM1555C1H220JA01D" n={n} /><C name="C_XTAL_OUT" value="22pF" a="XTAL_OUT" b="GND" mpn="GRM1555C1H220JA01D" n={n} />

  <Chip name="U_FLASH" manufacturerPartNumber="W25Q128JWSIQ" jlc="C2763561" footprint="soic8_208mil"
   pinLabels={{pin1:"CE_N",pin2:"SO_IO1",pin3:"WP_N_IO2",pin4:"GND",pin5:"SI_IO0",pin6:"SCK",pin7:"HOLD_N_IO3",pin8:"VCC"}}
   connections={{pin1:n("QSPI_CS_N"),pin2:n("QSPI_D1"),pin3:n("QSPI_D2"),pin4:n("GND"),pin5:n("QSPI_D0"),pin6:n("QSPI_CLK"),pin7:n("QSPI_D3"),pin8:n("1V8")}} />
  <R name="R_QSPI_CS" value="4.7k" a="1V8" b="QSPI_CS_N" mpn="RC0402FR-074K7L" n={n} /><C name="C_FLASH" value="100nF" a="1V8" b="GND" n={n} />

  <Chip name="Y_AUDIO" manufacturerPartNumber="SX5M24.576M20F30TNN" jlc="C2901534" footprint={<Osc5032Land/>}
   pinLabels={{pin1:"OE",pin2:"GND",pin3:"OUT",pin4:"VDD"}} connections={{pin1:n("3V3X"),pin2:n("GND"),pin3:n("AUDIO_24M576"),pin4:n("3V3X")}} />
  <C name="C_AUDIO_OSC" value="10nF" a="3V3X" b="GND" mpn="GRM155R71H103KA88D" n={n} />
  {/* TCA9406 OE is 5.5-V tolerant: ADC_READY may directly enable the
      1V8/3V3_ADC bus after analog POR and both digital rail qualifiers.
      Both ports become high-Z if OE is low or either supply is absent. */}
  <Chip name="U_ADC_I2C_XLATE" manufacturerPartNumber="TCA9406DCUR" footprint={<Tca9406DcuLand/>}
   pinLabels={{pin1:"SDA_B",pin2:"GND",pin3:"VCCA",pin4:"SDA_A",pin5:"SCL_A",pin6:"OE",pin7:"VCCB",pin8:"SCL_B"}}
   connections={{pin1:n("ADC_I2C_SDA"),pin2:n("GND"),pin3:n("1V8"),pin4:n("XU_I2C_SDA_1V8"),pin5:n("XU_I2C_SCL_1V8"),pin6:n("ADC_READY"),pin7:n("3V3_ADC"),pin8:n("ADC_I2C_SCL")}} />
  <C name="C_ADC_I2C_A" value="100nF" a="1V8" b="GND" n={n} />
  <C name="C_ADC_I2C_B" value="100nF" a="3V3_ADC" b="GND" n={n} />
  <R name="R_ADC_I2C_SCL_A_PU" value="4.7k" a="XU_I2C_SCL_1V8" b="1V8" mpn="RC0402FR-074K7L" n={n} />
  <R name="R_ADC_I2C_SDA_A_PU" value="4.7k" a="XU_I2C_SDA_1V8" b="1V8" mpn="RC0402FR-074K7L" n={n} />
  <R name="R_ADC_I2C_SCL_B_PU" value="4.7k" a="ADC_I2C_SCL" b="3V3_ADC" mpn="RC0402FR-074K7L" n={n} />
  <R name="R_ADC_I2C_SDA_B_PU" value="4.7k" a="ADC_I2C_SDA" b="3V3_ADC" mpn="RC0402FR-074K7L" n={n} />
  <Chip name="U_TDM_XLATE" manufacturerPartNumber="SN74AXC4T245PWR" jlc="" footprint="tssop16"
   pinLabels={{pin1:"VCCA",pin2:"1DIR",pin3:"2DIR",pin4:"1A1",pin5:"1A2",pin6:"2A1",pin7:"2A2",pin8:"GND1",pin9:"GND2",pin10:"2B2",pin11:"2B1",pin12:"1B2",pin13:"1B1",pin14:"2OE_N",pin15:"1OE_N",pin16:"VCCB"}}
   connections={{pin1:n("1V8"),pin2:n("1V8"),pin3:n("GND"),pin4:n("TDM_BCLK_1V8"),pin5:n("TDM_FSYNC_1V8"),pin6:n("AUDIO_MCLK_1V8"),pin7:n("TDM_DATA_1V8"),pin8:n("GND"),pin9:n("GND"),pin10:n("ADC_DOUT1"),pin11:n("AUDIO_24M576"),pin12:n("ADC_FSYNC_RAW"),pin13:n("ADC_BCLK_RAW"),pin14:n("GND"),pin15:n("TDM_OE_N"),pin16:n("3V3X")}} />
  <C name="C_XLATE_A" value="100nF" a="1V8" b="GND" n={n} /><C name="C_XLATE_B" value="100nF" a="3V3X" b="GND" n={n} />
  <R name="R_ADC_DATA_PD" value="100k" a="ADC_DOUT1" b="GND" mpn="RC0402FR-07100KL" n={n} />
  <R name="R_BCLK_RAW_PD" value="100k" a="ADC_BCLK_RAW" b="GND" mpn="RC0402FR-07100KL" n={n} /><R name="R_FSYNC_RAW_PD" value="100k" a="ADC_FSYNC_RAW" b="GND" mpn="RC0402FR-07100KL" n={n} />
  {/* U_ADC_OUT remains powered when 3V3X is absent. Define every input at its
      actual held-domain pin; R_FSYNC_RAW_PD alone cannot define the post-OR net. */}
  <R name="R_FSYNC_EXT_PD" value="100k" a="ADC_FSYNC_EXT" b="GND" mpn="RC0402FR-07100KL" n={n} />
  {/* 3V3X processing stops before the ADC pins.  U_ADC_OUT is powered by
      3V3_ADC so its outputs can never exceed the ADC input rail by a fixed
      3V3X/quiet-rail mismatch.  Ioff makes its inputs safe while 3V3_ADC=0. */}
  {/* Preserve raw FSYNC leading edge while synchronously extending its trailing edge.
      Q1 samples on BCLK rising; Q2 samples Q1 on BCLK falling via U_BCLK_INV.
      OR(raw,Q1,Q2) is nominally two BCLK periods high and falls near a BCLK falling edge. */}
  <Chip name="U_FSYNC_FF1" manufacturerPartNumber="SN74LVC2G74DCTR" jlc="" footprint={<SM8_DCTLand/>}
   pinLabels={{pin1:"CLK",pin2:"D",pin3:"Q_N",pin4:"GND",pin5:"Q",pin6:"CLR_N",pin7:"PRE_N",pin8:"VCC"}}
   connections={{pin1:n("ADC_BCLK_RAW"),pin2:n("ADC_FSYNC_RAW"),pin4:n("GND"),pin5:n("FSYNC_Q1"),pin6:n("ADC_OK"),pin7:n("3V3X"),pin8:n("3V3X")}} />
  <Chip name="U_BCLK_INV" manufacturerPartNumber="SN74LVC1G04DCKR" jlc="" footprint={<SC70_5Land/>}
   pinLabels={{pin1:"NC",pin2:"A",pin3:"GND",pin4:"Y",pin5:"VCC"}}
   connections={{pin2:n("ADC_BCLK_RAW"),pin3:n("GND"),pin4:n("ADC_BCLK_INV"),pin5:n("3V3X")}} />
  <Chip name="U_FSYNC_FF2" manufacturerPartNumber="SN74LVC2G74DCTR" jlc="" footprint={<SM8_DCTLand/>}
   pinLabels={{pin1:"CLK",pin2:"D",pin3:"Q_N",pin4:"GND",pin5:"Q",pin6:"CLR_N",pin7:"PRE_N",pin8:"VCC"}}
   connections={{pin1:n("ADC_BCLK_INV"),pin2:n("FSYNC_Q1"),pin4:n("GND"),pin5:n("FSYNC_Q2"),pin6:n("ADC_OK"),pin7:n("3V3X"),pin8:n("3V3X")}} />
  <Chip name="U_FSYNC_OR" manufacturerPartNumber="SN74LVC1G332DBVR" jlc="" footprint="sot23_6"
   pinLabels={{pin1:"A",pin2:"GND",pin3:"B",pin4:"Y",pin5:"VCC",pin6:"C"}}
   connections={{pin1:n("ADC_FSYNC_RAW"),pin2:n("GND"),pin3:n("FSYNC_Q1"),pin4:n("ADC_FSYNC_EXT"),pin5:n("3V3X"),pin6:n("FSYNC_Q2")}} />
  <C name="C_FSYNC_FF1" value="100nF" a="3V3X" b="GND" n={n} /><C name="C_FSYNC_FF2" value="100nF" a="3V3X" b="GND" n={n} /><C name="C_FSYNC_INV" value="100nF" a="3V3X" b="GND" n={n} /><C name="C_FSYNC_OR" value="100nF" a="3V3X" b="GND" n={n} />
  <Chip name="U_ADC_OUT" manufacturerPartNumber="SN74AUP3G34DCUR" jlc="" footprint={<Dcu0008ALand/>}
   pinLabels={{pin1:"1A",pin2:"3Y",pin3:"2A",pin4:"GND",pin5:"2Y",pin6:"3A",pin7:"1Y",pin8:"VCC"}}
   connections={{pin1:n("GND"),pin2:n("ADC_FSYNC_SAFE"),pin3:n("ADC_BCLK_RAW"),pin4:n("GND"),pin5:n("ADC_BCLK_SAFE"),pin6:n("ADC_FSYNC_EXT"),pin8:n("3V3_ADC")}} />
  <C name="C_ADC_OUT" value="100nF" a="3V3_ADC" b="GND" n={n} />
  <R name="R_BCLK" value="33" a="ADC_BCLK_SAFE" b="ADC_BCLK" mpn="RC0402FR-0733RL" n={n} />
  <R name="R_FSYNC" value="33" a="ADC_FSYNC_SAFE" b="ADC_FSYNC" mpn="RC0402FR-0733RL" n={n} />
  <R name="R_ADC_OK_TOP" value="169k" a="3V3_ADC" b="U_ADC_OK_SENSE" mpn="RT0402BRD07169KL" jlc="C852555" n={n} />
  <R name="R_ADC_OK_BOT" value="100k" a="U_ADC_OK_SENSE" b="GND" mpn="RT0402BRD07100KL" jlc="C852472" n={n} />
  <Chip name="U_ADC_OK" manufacturerPartNumber="TPS389001DSER" jlc="C1509297" footprint={<DSE0006ALand/>}
   pinLabels={{pin1:"SENSE",pin2:"GND",pin3:"MR_N",pin4:"VDD",pin5:"CT",pin6:"RESET_N"}}
   connections={{pin1:n("U_ADC_OK_SENSE"),pin2:n("GND"),pin3:n("3V3X"),pin4:n("3V3X"),pin5:n("ADC_OK_CT"),pin6:n("ADC_OK")}} />
  <C name="C_ADC_OK_VDD" value="100nF" a="3V3X" b="GND" n={n} />
  <C name="C_ADC_OK_CT" value="1nF" a="ADC_OK_CT" b="GND" mpn="GRM1555C1H102JA01D" jlc="" n={n} />
  <R name="R_ADC_OK_PU" value="10k" a="3V3X" b="ADC_OK" mpn="RC0402FR-0710KL" n={n} />
  {/* A held-domain tri-state buffer implements ADC_OK AND ADC_DIGITAL_OK.
      Its disabled output is pulled low, so either bad state turns both
      open-drain MOSFETs off without a B-C injection path into 1V8. */}
  <Chip name="U_ADC_CLOCK_OK" manufacturerPartNumber="SN74LVC1G125DCKT" jlc="" footprint={<SC70_5Land/>}
   pinLabels={{pin1:"OE_N",pin2:"A",pin3:"GND",pin4:"Y",pin5:"VCC"}}
   connections={{pin1:n("ADC_DIGITAL_BAD"),pin2:n("ADC_OK"),pin3:n("GND"),pin4:n("ADC_CLOCK_OK"),pin5:n("3V3_ADC")}} />
  <C name="C_ADC_CLOCK_OK" value="100nF" a="3V3_ADC" b="GND" n={n} />
  <R name="R_ADC_CLOCK_OK_PD" value="100k" a="ADC_CLOCK_OK" b="GND" mpn="RC0402FR-07100KL" n={n} />
  <Chip name="Q_TDM_GATE" manufacturerPartNumber="AO3400A" jlc="C20917" footprint="sot23"
   pinLabels={{pin1:"G",pin2:"S",pin3:"D"}} connections={{pin1:n("ADC_CLOCK_OK"),pin2:n("GND"),pin3:n("TDM_OE_N")}} />
  <R name="R_TDM_OE_PU" value="10k" a="1V8" b="TDM_OE_N" mpn="RC0402FR-0710KL" n={n} />

  <Chip name="Q_VBUS" manufacturerPartNumber="AO3400A" jlc="C20917" footprint="sot23" pinLabels={{pin1:"G",pin2:"S",pin3:"D"}} connections={{pin1:n("VBUS_B"),pin2:n("GND"),pin3:n("VBUS_PRESENT_N")}} />
  <R name="R_VBUS_B" value="100k" a="VBUS_USB" b="VBUS_B" mpn="RC0402FR-07100KL" n={n} /><R name="R_VBUS_BE" value="1M" a="VBUS_B" b="GND" mpn="RC0402FR-071ML" n={n} /><R name="R_VBUS_PU" value="10k" a="1V8" b="VBUS_PRESENT_N" mpn="RC0402FR-0710KL" n={n} />

  <Chip name="J_JTAG" manufacturerPartNumber="FTSH-105-01-L-DV-K" jlc="" footprint={<FTSH2x5Land/>}
   pinLabels={{pin1:"VREF",pin2:"TMS",pin3:"GND1",pin4:"TCK",pin5:"GND2",pin6:"TDO",pin7:"KEY_NC",pin8:"TDI",pin9:"GND3",pin10:"RESET_N"}}
   connections={{pin1:n("1V8"),pin2:n("JTAG_TMS"),pin3:n("GND"),pin4:n("JTAG_TCK"),pin5:n("GND"),pin6:n("JTAG_TDO"),pin8:n("JTAG_TDI"),pin9:n("GND"),pin10:n("XU_RESET_N")}} />
 </>
}
