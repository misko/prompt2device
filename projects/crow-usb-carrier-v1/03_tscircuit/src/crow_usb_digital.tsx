import { Fragment } from "react"
/**
 * Conditional XU316 USB-audio digital-core hardware source.
 * No firmware, XN, USB descriptor, or production board is generated here.
 * Parent supplies protected 5V_BUCK and connector/ESD nets USB_DP/USB_DN/VBUS_USB.
 */
export const CROW_DIGITAL_BOUNDARY_NETS = {
  powerInputs: ["5V_BUCK", "GND"], usbInputs: ["USB_DP", "USB_DN", "VBUS_USB"],
  analogInterface: ["ADC_MCLK", "ADC_BCLK", "ADC_FSYNC", "ADC_DOUT1", "3V3_ADC"],
  debug: ["JTAG_TDI", "JTAG_TDO", "JTAG_TMS", "JTAG_TCK", "XU_RESET_N"],
} as const
export interface CrowUsbDigitalProps { net?: (canonicalName: string) => string }
const defaultNet=(name:string)=>`net.${ /^\d/.test(name) ? `N${name}` : name }`
const supplier=(jlc:string)=>({jlcpcb:jlc?[jlc]:[]})
const sourced=(mpn:string,jlc="")=>jlc||({
 "744373240047":"C19270343","ASFL1-24.576MHZ-EC-T":"C17566269","CC0402KRX5R5BB105":"C106253","FTSH-105-01-L-DV-K":"C5155080",
 "GRM1555C1H220JA01D":"C76960","RC0402FR-0733RL":"C138002","GRM155R71H103KA88D":"C77019","CL21A106KOCLRNC":"C318695","CRCW0402680RFKED":"C482224",
 "RT0402BRD07100KL":"C852472","RT0402BRD07200KL":"C728556","SN74AUP3G34DCUR":"C2675543",
 "SN74AXC4T245PWR":"C2867798","SN74LVC1G04DCKR":"C8207","SN74LVC1G125DCKT":"C2675550",
 "SN74LVC1G332DBVR":"C43368","SN74LVC2G74DCTR":"C79339","TPS3808G09DBVR":"C24584",
 "TPS389018DSER":"C2066910","TPS389030DSER":"C2066942","TPS6282518DMQR":"C2072356",
 "TPS6282533DMQR":"C3189971","TPS62825DMQR":"C2650334"
 } as Record<string,string>)[mpn]||""
const Chip=({jlc="",manufacturerPartNumber,...props}:any)=><chip manufacturerPartNumber={manufacturerPartNumber} supplierPartNumbers={supplier(sourced(manufacturerPartNumber,jlc))} {...props} />
const R=({name,value,a,b,mpn,jlc="",n}:any)=><resistor name={name} resistance={value} footprint="0402" manufacturerPartNumber={mpn} supplierPartNumbers={supplier(sourced(mpn,jlc))} connections={{pin1:n(a),pin2:n(b)}} />
const C=({name,value,a,b,mpn="CL05B104KO5NNNC",jlc="",footprint="0402",n}:any)=>{
 const exactJlc=sourced(mpn,jlc || (mpn==="CL05B104KO5NNNC" && value==="100nF" ? "C1525" : ""));
 return <capacitor name={name} capacitance={value} footprint={footprint} manufacturerPartNumber={mpn} supplierPartNumbers={supplier(exactJlc)} connections={{pin1:n(a),pin2:n(b)}} />
}

const XU_NC_PINS=Object.freeze([6, 7, 9, 12, 13, 15, 16, 19, 21, 25, 26, 28, 29, 31, 32, 46, 47, 48, 49, 53, 55, 57, 58, 63, 64, 65, 66, 67, 69, 70, 71, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 86, 87, 88, 90, 91, 92, 93, 94, 96, 97, 98, 99, 100, 101, 102, 103, 108, 110, 111, 112, 114, 115, 116, 117, 118, 119, 120, 122, 123, 124, 125, 126])
const XU_CONNECTED_PINS=Object.freeze([1, 2, 3, 4, 5, 8, 10, 11, 14, 17, 18, 20, 22, 23, 24, 27, 30, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 50, 51, 52, 54, 56, 59, 60, 61, 62, 68, 72, 85, 89, 95, 104, 105, 106, 107, 109, 113, 121, 127, 128, 129])
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
/** Würth 744373240047 primary drawing: 5.2-mm land span, 2.2-mm inner gap, 1.5 x 2.4-mm lands. */
function WurthLHMI4020Land(){return <footprint><P n={1} x={-1.85} y={0} w={1.5} h={2.4}/><P n={2} x={1.85} y={0} w={1.5} h={2.4}/></footprint>}
// ASFL1 primary drawing: 2.54 x 2.2 mm pad-center pitch, 1.7 x 1.5 mm lands.
function Osc5032Land(){return <footprint><P n={1} x={-1.27} y={-1.1} w={1.7} h={1.5}/><P n={2} x={1.27} y={-1.1} w={1.7} h={1.5}/><P n={3} x={1.27} y={1.1} w={1.7} h={1.5}/><P n={4} x={-1.27} y={1.1} w={1.7} h={1.5}/></footprint>}
function SC70_5Land(){return <footprint><P n={1} x={-1} y={0.65} w={0.6} h={1}/><P n={2} x={-1} y={0} w={0.6} h={1}/><P n={3} x={-1} y={-0.65} w={0.6} h={1}/><P n={4} x={1} y={-0.65} w={0.6} h={1}/><P n={5} x={1} y={0.65} w={0.6} h={1}/></footprint>}
function SM8_DCTLand(){return <footprint>{[1,2,3,4].map((n,i)=><P key={n} n={n} x={-1.45} y={(1.5-i)*0.65} w={0.6} h={1.2}/>)}{[5,6,7,8].map((n,i)=><P key={n} n={n} x={1.45} y={(i-1.5)*0.65} w={0.6} h={1.2}/>)}</footprint>}
function FTSH2x5Land(){return <footprint>{Array.from({length:10},(_,i)=>{const row=Math.floor(i/2),col=i%2;return <P key={i+1} n={i+1} x={col?0.635:-0.635} y={(2-row)*1.27} w={0.7} h={1.5}/>})}</footprint>}
/** TI drawing 4220552/B: DSE0006A, 0.5-mm pitch, 0.25 x 0.7-mm lands. */
function DSE0006ALand(){return <footprint>{[1,2,3].map((n,i)=><P key={n} n={n} x={-0.6} y={(1-i)*0.5} w={0.7} h={0.25}/>)}{[4,5,6].map((n,i)=><P key={n} n={n} x={0.6} y={(i-1)*0.5} w={0.7} h={0.25}/>)}</footprint>}
/** TI drawing 4222645/E: DMQ0006A asymmetric 0.5-mm-pitch VSON lands. */
function DMQ0006ALand(){return <footprint>{[1,2,3].map((n,i)=><P key={n} n={n} x={-0.55} y={(1-i)*0.5} w={0.6} h={0.25}/>)}{[4,5,6].map((n,i)=><P key={n} n={n} x={0.35} y={(i-1)*0.5} w={1.0} h={0.25}/>)}</footprint>}

// TI SLVSEF9I §7.4.2: unused open-drain PG is deliberately unconnected.
const buckPins={pin1:"EN",pin2:"PG_NC",pin3:"FB",pin4:"GND",pin5:"SW",pin6:"VIN"}
function Buck({name,mpn,out,adjustable=false,en="5V_BUCK",n}:any){return <>
 <Chip name={name} manufacturerPartNumber={mpn} jlc="" footprint={<DMQ0006ALand/>} pinLabels={buckPins}
  connections={{pin1:n(en),pin3:n(adjustable?`${name}_FB`:out),pin4:n("GND"),pin5:n(`${name}_SW`),pin6:n("5V_BUCK")}} />
 <Chip name={`L_${name}`} manufacturerPartNumber="744373240047" jlc="" footprint={<WurthLHMI4020Land/>} pinLabels={{pin1:"1",pin2:"2"}} connections={{pin1:n(`${name}_SW`),pin2:n(out)}} />
 {[1,2].map(i=><C key={`in${i}`} name={`C_${name}_IN_${i}`} value="10uF" a="5V_BUCK" b="GND" mpn="CL21A106KOCLRNC" footprint="0805" n={n} />)}
 <C name={`C_${name}_OUT_1`} value="47uF" a={out} b="GND" mpn="GRM32ER71A476KE15L" jlc="C84494" footprint="1210" n={n} />
 </>}

export function CrowUsbDigital({net=defaultNet}:CrowUsbDigitalProps={}){
 const n=net; assertXUPinCoverage();
 return <>
  <Buck name="U_3V3X" mpn="TPS6282533DMQR" out="3V3X" n={n} />
  <Buck name="U_1V8" mpn="TPS6282518DMQR" out="1V8" n={n} />
  <Buck name="U_CORE" mpn="TPS62825DMQR" out="0V9" adjustable en="CORE_EN" n={n} />
  <R name="R_CORE_FB_TOP" value="100k" a="0V9" b="U_CORE_FB" mpn="RT0402BRD07100KL" n={n} />
  <R name="R_CORE_FB_BOTTOM" value="200k" a="U_CORE_FB" b="GND" mpn="RT0402BRD07200KL" n={n} />
  <Chip name="U_1V8_OK" manufacturerPartNumber="TPS389018DSER" jlc="" footprint={<DSE0006ALand/>}
   pinLabels={{pin1:"SENSE",pin2:"GND",pin3:"MR_N",pin4:"VDD",pin5:"CT",pin6:"RESET_N"}}
   connections={{pin1:n("1V8"),pin2:n("GND"),pin3:n("5V_BUCK"),pin4:n("5V_BUCK"),pin5:n("CORE_EN_CT"),pin6:n("CORE_EN")}} />
  <C name="C_1V8_OK_VDD" value="100nF" a="5V_BUCK" b="GND" n={n} />
  <C name="C_CORE_EN_CT" value="10nF" a="CORE_EN_CT" b="GND" mpn="GRM155R71H103KA88D" jlc="" n={n} />
  <R name="R_CORE_EN_PU" value="10k" a="1V8" b="CORE_EN" mpn="RC0402FR-0710KL" n={n} />
  <Chip name="U_CORE_OK" manufacturerPartNumber="TPS3808G09DBVR" jlc="" footprint="sot23_6"
   pinLabels={{pin1:"RESET_N",pin2:"GND",pin3:"MR_N",pin4:"CT_NC",pin5:"SENSE",pin6:"VDD"}}
   connections={{pin1:n("XU_RESET_N"),pin2:n("GND"),pin3:n("1V8"),pin5:n("0V9"),pin6:n("1V8")}} />
  <C name="C_CORE_OK" value="100nF" a="1V8" b="GND" n={n} />
  {/* Wired-open-drain reset also qualifies the independently generated 3V3X USB rail.
      Core release remains downstream of U_1V8_OK, so its delay bounds flash readiness. */}
  <Chip name="U_XU_3V3_OK" manufacturerPartNumber="TPS389030DSER" jlc="" footprint={<DSE0006ALand/>}
   pinLabels={{pin1:"SENSE",pin2:"GND",pin3:"MR_N",pin4:"VDD",pin5:"CT",pin6:"RESET_N"}}
   connections={{pin1:n("3V3X"),pin2:n("GND"),pin3:n("5V_BUCK"),pin4:n("5V_BUCK"),pin5:n("XU_3V3_OK_CT"),pin6:n("XU_RESET_N")}} />
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
    pin93: "X0D35_NC",
    pin94: "X0D36_NC",
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

  <Chip name="Y_XU" manufacturerPartNumber="FA-238 24.0000MD30X-W5" jlc="" footprint="crystal_3225_4pin"
   pinLabels={{pin1:"X1",pin2:"CASE",pin3:"X2",pin4:"CASE"}} connections={{pin1:n("XTAL_IN_R"),pin2:n("GND"),pin3:n("XTAL_OUT"),pin4:n("GND")}} />
  <R name="R_XTAL_DRIVE" value="680" a="XTAL_IN" b="XTAL_IN_R" mpn="CRCW0402680RFKED" n={n} />
  <R name="R_XTAL_FB" value="1M" a="XTAL_IN" b="XTAL_OUT" mpn="RC0402FR-071ML" n={n} />
  <C name="C_XTAL_IN" value="22pF" a="XTAL_IN_R" b="GND" mpn="GRM1555C1H220JA01D" n={n} /><C name="C_XTAL_OUT" value="22pF" a="XTAL_OUT" b="GND" mpn="GRM1555C1H220JA01D" n={n} />

  <Chip name="U_FLASH" manufacturerPartNumber="W25Q128JWSIQ" jlc="C2763561" footprint="soic8_208mil"
   pinLabels={{pin1:"CE_N",pin2:"SO_IO1",pin3:"WP_N_IO2",pin4:"GND",pin5:"SI_IO0",pin6:"SCK",pin7:"HOLD_N_IO3",pin8:"VCC"}}
   connections={{pin1:n("QSPI_CS_N"),pin2:n("QSPI_D1"),pin3:n("QSPI_D2"),pin4:n("GND"),pin5:n("QSPI_D0"),pin6:n("QSPI_CLK"),pin7:n("QSPI_D3"),pin8:n("1V8")}} />
  <R name="R_QSPI_CS" value="4.7k" a="1V8" b="QSPI_CS_N" mpn="RC0402FR-074K7L" n={n} /><C name="C_FLASH" value="100nF" a="1V8" b="GND" n={n} />

  <Chip name="Y_AUDIO" manufacturerPartNumber="ASFL1-24.576MHZ-EC-T" jlc="" footprint={<Osc5032Land/>}
   pinLabels={{pin1:"OE",pin2:"GND",pin3:"OUT",pin4:"VDD"}} connections={{pin1:n("3V3X"),pin2:n("GND"),pin3:n("AUDIO_24M576"),pin4:n("3V3X")}} />
  <C name="C_AUDIO_OSC" value="10nF" a="3V3X" b="GND" mpn="GRM155R71H103KA88D" n={n} />
  <Chip name="U_TDM_XLATE" manufacturerPartNumber="SN74AXC4T245PWR" jlc="" footprint="tssop16"
   pinLabels={{pin1:"VCCA",pin2:"1DIR",pin3:"2DIR",pin4:"1A1",pin5:"1A2",pin6:"2A1",pin7:"2A2",pin8:"GND1",pin9:"GND2",pin10:"2B2",pin11:"2B1",pin12:"1B2",pin13:"1B1",pin14:"2OE_N",pin15:"1OE_N",pin16:"VCCB"}}
   connections={{pin1:n("1V8"),pin2:n("1V8"),pin3:n("GND"),pin4:n("TDM_BCLK_1V8"),pin5:n("TDM_FSYNC_1V8"),pin6:n("AUDIO_MCLK_1V8"),pin7:n("TDM_DATA_1V8"),pin8:n("GND"),pin9:n("GND"),pin10:n("ADC_DOUT1"),pin11:n("AUDIO_24M576"),pin12:n("ADC_FSYNC_RAW"),pin13:n("ADC_BCLK_RAW"),pin14:n("GND"),pin15:n("TDM_OE_N"),pin16:n("3V3X")}} />
  <C name="C_XLATE_A" value="100nF" a="1V8" b="GND" n={n} /><C name="C_XLATE_B" value="100nF" a="3V3X" b="GND" n={n} />
  <R name="R_ADC_DATA_PD" value="100k" a="ADC_DOUT1" b="GND" mpn="RC0402FR-07100KL" n={n} />
  <R name="R_BCLK_RAW_PD" value="100k" a="ADC_BCLK_RAW" b="GND" mpn="RC0402FR-07100KL" n={n} /><R name="R_FSYNC_RAW_PD" value="100k" a="ADC_FSYNC_RAW" b="GND" mpn="RC0402FR-07100KL" n={n} />
  {/* U_ADC_OUT remains powered when 3V3X is absent. Define every input at its
      actual held-domain pin; R_FSYNC_RAW_PD alone cannot define the post-OR net. */}
  <R name="R_MCLK_RAW_PD" value="100k" a="ADC_MCLK_RAW" b="GND" mpn="RC0402FR-07100KL" n={n} />
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
  <Chip name="U_MCLK_BUF" manufacturerPartNumber="SN74LVC1G125DCKT" jlc="" footprint={<SC70_5Land/>}
   pinLabels={{pin1:"OE_N",pin2:"A",pin3:"GND",pin4:"Y",pin5:"VCC"}} connections={{pin1:n("MCLK_OE_N"),pin2:n("AUDIO_24M576"),pin3:n("GND"),pin4:n("ADC_MCLK_RAW"),pin5:n("3V3X")}} />
  <C name="C_MCLK_BUF" value="100nF" a="3V3X" b="GND" n={n} />
  <Chip name="U_ADC_OUT" manufacturerPartNumber="SN74AUP3G34DCUR" jlc="" footprint="vssop8_dcu"
   pinLabels={{pin1:"1A",pin2:"3Y",pin3:"2A",pin4:"GND",pin5:"2Y",pin6:"3A",pin7:"1Y",pin8:"VCC"}}
   connections={{pin1:n("ADC_MCLK_RAW"),pin2:n("ADC_FSYNC_SAFE"),pin3:n("ADC_BCLK_RAW"),pin4:n("GND"),pin5:n("ADC_BCLK_SAFE"),pin6:n("ADC_FSYNC_EXT"),pin7:n("ADC_MCLK_SAFE"),pin8:n("3V3_ADC")}} />
  <C name="C_ADC_OUT" value="100nF" a="3V3_ADC" b="GND" n={n} />
  <R name="R_MCLK" value="33" a="ADC_MCLK_SAFE" b="ADC_MCLK" mpn="RC0402FR-0733RL" n={n} />
  <R name="R_BCLK" value="33" a="ADC_BCLK_SAFE" b="ADC_BCLK" mpn="RC0402FR-0733RL" n={n} />
  <R name="R_FSYNC" value="33" a="ADC_FSYNC_SAFE" b="ADC_FSYNC" mpn="RC0402FR-0733RL" n={n} />
  <Chip name="U_ADC_OK" manufacturerPartNumber="TPS389030DSER" jlc="" footprint={<DSE0006ALand/>}
   pinLabels={{pin1:"SENSE",pin2:"GND",pin3:"MR_N",pin4:"VDD",pin5:"CT",pin6:"RESET_N"}}
   connections={{pin1:n("3V3_ADC"),pin2:n("GND"),pin3:n("3V3X"),pin4:n("3V3X"),pin5:n("ADC_OK_CT"),pin6:n("ADC_OK")}} />
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
  <Chip name="Q_MCLK_GATE" manufacturerPartNumber="AO3400A" jlc="C20917" footprint="sot23"
   pinLabels={{pin1:"G",pin2:"S",pin3:"D"}} connections={{pin1:n("ADC_CLOCK_OK"),pin2:n("GND"),pin3:n("MCLK_OE_N")}} />
  <R name="R_MCLK_OE_PU" value="10k" a="3V3X" b="MCLK_OE_N" mpn="RC0402FR-0710KL" n={n} />

  <Chip name="Q_VBUS" manufacturerPartNumber="AO3400A" jlc="C20917" footprint="sot23" pinLabels={{pin1:"G",pin2:"S",pin3:"D"}} connections={{pin1:n("VBUS_B"),pin2:n("GND"),pin3:n("VBUS_PRESENT_N")}} />
  <R name="R_VBUS_B" value="100k" a="VBUS_USB" b="VBUS_B" mpn="RC0402FR-07100KL" n={n} /><R name="R_VBUS_BE" value="1M" a="VBUS_B" b="GND" mpn="RC0402FR-071ML" n={n} /><R name="R_VBUS_PU" value="10k" a="1V8" b="VBUS_PRESENT_N" mpn="RC0402FR-0710KL" n={n} />

  <Chip name="J_JTAG" manufacturerPartNumber="FTSH-105-01-L-DV-K" jlc="" footprint={<FTSH2x5Land/>}
   pinLabels={{pin1:"VREF",pin2:"TMS",pin3:"GND1",pin4:"TCK",pin5:"GND2",pin6:"TDO",pin7:"KEY_NC",pin8:"TDI",pin9:"GND3",pin10:"RESET_N"}}
   connections={{pin1:n("1V8"),pin2:n("JTAG_TMS"),pin3:n("GND"),pin4:n("JTAG_TCK"),pin5:n("GND"),pin6:n("JTAG_TDO"),pin8:n("JTAG_TDI"),pin9:n("GND"),pin10:n("XU_RESET_N")}} />
 </>
}
