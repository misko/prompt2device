// Source-owned schematic composition only. Electrical connections remain in
// crow_audio_carrier_v1.tsx; the governed PCB placement remains floorplan.yaml.
// A missing reference is fatal so adding a component cannot silently omit it.
type Pose = [string, number, number, number?]
const poses: Record<string, Pose> = {}
const own = (sheet: string, rows: Record<string, number[]>) => {
  for (const [ref, p] of Object.entries(rows)) {
    if (poses[ref]) throw new Error(`Duplicate schematic owner: ${ref}`)
    poses[ref] = [sheet, p[0], p[1], p[2]]
  }
}
export const sheets = [
  ["input", "12 V INPUT / FUSE / REVERSE POLARITY / TRANSIENT CLAMP"],
  ["buck", "5 V BUCK / L_BUCK 3.3 uH"],
  ["held_ldo", "PRECHARGE / HELD ENERGY / 3.3 V ADC LDO"],
  ["supervisors", "RAW-RAIL AND ADC-RAIL SUPERVISION / AUDIO ENABLE"],
  ["dump", "DELAYED LDO ENABLE / ADC DISCHARGE / U_DUMP AND U_LDO_EN: INVERTING SCHMITT"],
  ...Array.from({length: 8}, (_, i) => [`analog_${i+1}`, `CHANNEL ${i+1} / SPOKE / BUFFER-FILTER / POWER-OFF ISOLATION`]),
  ["adc", "CS5308P / HARDWARE TDM8 / CONFIGURATION / LOCAL BYPASS"],
  ["vmid", "PASSIVE EXTERNAL HALF-SUPPLY BIAS / CHANNEL INPUT BUFFERS"],
  ["references", "ADC VMID DECOUPLING / INDEPENDENT REFERENCE FILTER BANKS"],
  ["clocks", "MCHSTREAMER INTERFACE / CLOCK BUFFERS / SOURCE TERMINATION"],
  ["tdm", "TDM RETURN / U_TDM_SCH: NONINVERTING SCHMITT / U_OE: INVERTING SCHMITT"],
  ["reset", "POWER-ON HIGH-LOW-HIGH ADC RESET SEQUENCE"],
]

own("input", {
  J9:[-5,2.5], F_IN:[-1.7,2.5], Q_IN:[2,2.5],
  R_QIN_G:[0,-1.5,-90], D_QIN_GS:[3,-.5], D_IN:[6,.5],
})
own("buck", {
  D_BUCK_IN:[-9,4], C_BUCK_IN:[-9,-2,-90], C_BUCK_IN2:[-6,-2,-90], C_BUCK_IN3:[-3,-2,-90],
  U_BUCK:[-3,1], C_BUCK_BST:[-2,4], L_BUCK:[1,1],
  C_BUCK_O1:[2,-.5,-90], C_BUCK_O2:[5,-.5,-90], C_BUCK_O3:[8,-.5,-90],
  C_OPA_BULK:[7,-4,-90],
  R_OPA_BLEED1:[-1,-4],
  R_OPA_BLEED2:[3,-4],
})
own("held_ldo", {
  D_HOLD:[-6,3], R_PRE:[-2,3], Q_PRE:[-2,0], R_PRE_G:[-5,-.5,-90],
  Q_PRE_EN:[-2,-3], C_HOLD1:[1,-3,-90], C_HOLD2:[4,-3,-90],
  C_LDO_IN:[1,2,-90], U_LDO:[5,2], C_LDO_OUT:[9,2,-90],
  // SET leaves the top of U_LDO. Keep its resistor/capacitors above that
  // pin, so the primary wire does not loop through the chip reference.
  R_LDO_SET:[5,7,-90],
  C_LDO_NR4:[7.5,7,-90], C_LDO_NR5:[10,7,-90],
})
own("supervisors", {
  U_PWR:[-3,2], R_PWR_TOP:[-7,3,-90], R_PWR_BOT:[-7,0,-90],
  C_PWR_CT:[-2,-1,-90], C_PWR:[-5,-2,-90], R_PWR_PU:[1,3,-90],
  U_AUDIO:[-3,-6], R_ADC_TOP:[-7,-5,-90], R_ADC_BOT:[-7,-8,-90],
  C_AUDIO_CT1:[-2,-9,-90], C_AUDIO_CT2:[1,-9,-90], C_AUDIO:[-5,-10,-90],
  R_AUDIO_PU:[1,-5,-90], R_AUDIO_PD:[4,-7,-90],
})
own("dump", {
  R_DUMP_TIME1:[-5,2], R_DUMP_TIME2:[-5,0], C_DUMP_TIME:[-2,-1,-90],
  U_DUMP:[1,1], U_LDO_EN:[5,1], Q_DUMP:[5,-4],
  C_DUMP_LOGIC:[0,-2,-90], C_LDO_EN:[8,-2,-90],
  R_DUMP:[8,-4,-90], R_DUMP_PD:[2,-5,-90],
})
for (let n=1; n<=8; n++) {
  own(`analog_${n}`, {
    [`J${n}`]:[-10,0], [`F${n}`]:[-8.5,4], [`U_ESD${n}`]:[-8.5,-4],
    [`C_A${n}P`]:[-6,1.6], [`C_A${n}N`]:[-6,-1.6],
    [`R_B${n}P`]:[-4.7,.7,-90], [`R_B${n}N`]:[-4.7,-2.5,-90],
    [`R_IN${n}P`]:[-3.1,1.6], [`R_IN${n}N`]:[-3.1,-1.6],
    [`U_AFE${n}`]:[-1,0], [`C_FB${n}P`]:[-.7,4.1], [`C_FB${n}N`]:[-.7,-4.1],
    [`R_X${n}P`]:[1.3,3.1], [`R_X${n}N`]:[1.3,-3.1],
    [`R_OUT${n}P`]:[1.5,.9], [`R_OUT${n}N`]:[2,-.9],
    [`C_FILTER${n}P1`]:[3.3,4,-90], [`C_FILTER${n}P2`]:[3.3,1.7,-90],
    [`C_FILTER${n}N1`]:[3.3,-2.2,-90], [`C_FILTER${n}N2`]:[3.3,-4.5,-90], [`U_ISO${n}`]:[5.8,0],
    [`R_ADC_PD${n}P`]:[7.7,4,-90], [`R_ADC_PD${n}N`]:[7.7,-2.7,-90],
    [`C_ADC_CM${n}P`]:[10.2,4,-90], [`C_ADC_CM${n}N`]:[10.2,-2.7,-90],
    [`C_ISO${n}`]:[6.8,-5,-90], [`C_OPA${n}`]:[-1,-6.3,-90],
  })
}
own("adc", {
  U_ADC:[0,0], R_CFG1:[5,3,-90], R_CFG2:[7.5,3,-90],
  R_CFG4:[5,0,-90], R_CFG5:[7.5,0,-90],
  C_LDO_A:[5,-3,-90], C_LDO_D:[8,-3,-90],
  C_VDDA1_4U7:[-3,-7,-90], C_VDDA1_10N:[0,-7,-90],
  C_VDDA2_4U7:[3,-7,-90], C_VDDA2_10N:[6,-7,-90], C_VDDIO:[9,-7,-90],
})
for (let n=1; n<=2; n++) {
  const y = n===1 ? 2.5 : -2.5
  own("vmid", {
    [`R_VMID${n}_TOP`]:[-9,y+1,-90], [`R_VMID${n}_BOT`]:[-9,y-1,-90],
    [`C_VMID${n}_EXT_10U`]:[-6,y-1,-90], [`C_VMID${n}_EXT_1U`]:[-3.5,y-1,-90],
  })
  own("references", {
    [`R_FILT${n}P`]:[-4,y], [`C_FILT${n}_470U`]:[-1,y-1,-90],
    [`C_FILT${n}_10U`]:[2,y-1,-90], [`C_FILT${n}_1U`]:[5,y-1,-90],
    [`C_VMID${n}_4U7`]:[8,y-1,-90], [`C_VMID${n}_470N`]:[11,y-1,-90],
  })
}
own("clocks", {
  J10:[-6,0], U_CLK:[1,0], C_CLK:[2,-4,-90],
  R_MCH_MCLK_PD:[-3,3,-90], R_MCH_BCLK_PD:[-3,-3], R_MCH_FSYNC_PD:[-5,-5],
  R_MCLK:[4,1.2], R_BCLK:[4,0], R_FSYNC:[4,-1.2],
})
own("tdm", {
  J11:[-6,1], R_MCH_SENSE:[-2,-1], R_MCH_SENSE_PD:[0,-3],
  U_OE:[3,-1], C_OE:[1.5,-4,-90], U_TDM:[7,1], C_TDM:[7,-2,-90], R_TDM:[10,1],
  U_TDM_SCH:[2,6], R_TDM_PD:[-2,5,-90], C_TDM_SCH:[2,3,-90],
})
own("reset", {
  U_RST1:[-5,1], C_RST1:[-5,-2,-90], U_RST2:[0,1], C_RST2:[0,-3,-90],
  R_RST_T:[3,4,-90], C_RST_T:[3,1,-90], Q_RST1:[6,-1.5],
  R_RESET_PU:[9,2,-90], R_RESET_GPD:[3.5,-3,-90],
})

export const poseFor = (ref: string) => {
  const p = poses[ref]
  if (!p) throw new Error(`No source-owned schematic pose: ${ref}`)
  return {schSheetName:p[0], schSectionName:p[0], schX:p[1], schY:p[2], schRotation:p[3] ?? 0}
}

// Pin functions are unchanged. Arrangement is explicitly human-flow oriented.
export const chipStyle = (ref: string): any => {
  if (/^U_AFE[1-8]$/.test(ref)) return {
    schWidth:1.8, schPinStyle:pinStyle(8,.3),
    schPinArrangement:{leftSide:[3,2,5,6],rightSide:[1,7],topSide:[8],bottomSide:[4]},
  }
  if (/^U_ISO[1-8]$/.test(ref)) return {
    schPinStyle:pinStyle(9,.3),
    schPinArrangement:{leftSide:[1,5],rightSide:[2,6,8],topSide:[3,7],bottomSide:[4,9]},
  }
  if (/^J[1-8]$/.test(ref)) return {
    // Tall vertical shield/return labels also set the local ground clearance.
    schHeight:3,
    schPinArrangement:{leftSide:[1,3,7],rightSide:[5,4],topSide:[9,10],bottomSide:[2,6,8]},
  }
  if (/^U_ESD[1-8]$/.test(ref)) return {schPinArrangement:{leftSide:[1,2],rightSide:[3,5],bottomSide:[4]}}
  if (/^F[1-8]$/.test(ref) || ["F_IN","L_BUCK","FB_OPA"].includes(ref))
    return {schPinArrangement:{leftSide:[1],rightSide:[2]}}
  const arrangements: Record<string, any> = {
    J9:{rightSide:[1],bottomSide:[2]},
    Q_IN:{leftSide:[5],rightSide:[1,2,3],bottomSide:[4]},
    D_IN:{topSide:[1],bottomSide:[2]}, D_QIN_GS:{leftSide:[1],bottomSide:[2]},
    U_BUCK:{leftSide:[3,2],rightSide:[5,1],topSide:[6],bottomSide:[4]},
    D_BUCK_IN:{leftSide:[2],rightSide:[1]}, D_HOLD:{leftSide:[2],rightSide:[1]}, Q_PRE:{leftSide:[2],rightSide:[3],bottomSide:[1]},
    Q_PRE_EN:{leftSide:[1],topSide:[3],bottomSide:[2]},
    U_LDO:{leftSide:[1,2,3,5,8],rightSide:[12,13,14,6,4],topSide:[9],bottomSide:[7,10,11,15]},
    U_PWR:{leftSide:[1],rightSide:[6],topSide:[3,4],bottomSide:[2,5]},
    U_AUDIO:{leftSide:[1,3],rightSide:[6],topSide:[4],bottomSide:[2,5]},
    U_DUMP:{leftSide:[2,1],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_LDO_EN:{leftSide:[2,1],rightSide:[4],topSide:[5],bottomSide:[3]},
    Q_DUMP:{leftSide:[1],rightSide:[3],bottomSide:[2]},
    U_ADC:{leftSide:[40,39,42,41,46,45,48,47,14,13,16,15,20,19,22,21,1,12,43,18],
      rightSide:[2,3,10,11,7,32,33,23,24,25,26,27,28,29,34],topSide:[5,9,31,38],bottomSide:[6,8,17,30,44,49,4,35,36,37]},
    J10:{leftSide:[1,3,4,5,6,7,8],rightSide:[9,10,12,2],bottomSide:[11]},
    J11:{leftSide:[3,4,5,6,7],rightSide:[2,8,9,10,11,12],bottomSide:[1]},
    U_CLK:{leftSide:[1,3,6],rightSide:[7,5,2],topSide:[8],bottomSide:[4]},
    U_OE:{leftSide:[2,1],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_TDM_SCH:{leftSide:[2,1],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_TDM:{leftSide:[2,1],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_RST1:{rightSide:[2],topSide:[3],bottomSide:[1]},
    U_RST2:{leftSide:[3],rightSide:[5,6,7],topSide:[2,8],bottomSide:[1,4]},
    Q_RST1:{leftSide:[1],rightSide:[3],bottomSide:[2]},
  }
  const arrangement = arrangements[ref]
  if (!arrangement) throw new Error(`No schematic chip arrangement: ${ref}`)
  return {schPinArrangement:arrangement,
    // Separate horizontal NC labels from the vertical ground/EP labels.
    ...(ref === "U_LDO" ? {schHeight:2.2} : {}),
    ...(ref === "U_ADC" ? {schPinStyle:pinStyle(49,.1)} : {}),
    ...(["U_OE","U_TDM_SCH","U_TDM"].includes(ref) ? {schPinStyle:pinStyle(5,.3)} : {}),
    ...(ref === "U_CLK" ? {schPinStyle:pinStyle(8,.5)} : {})}
}
const pinStyle = (count: number, margin: number) => Object.fromEntries(
  Array.from({length:count}, (_,i) => [`pin${i+1}`, {topMargin:margin,bottomMargin:margin}]),
)

// Local ground symbols remove the page-wide ground buses that previously
// crossed unrelated components. They connect to the same explicit source net.
export const Ground = ({refName, pins, passive=false}: any) => {
  if (!pins.length) return null
  const p = poseFor(refName)
  if (refName==="U_ADC") return <group schSheetName={p.schSheetName}>
    <netlabel net="GND" connectsTo={pins.map((pin:string)=>`.U_ADC > .${pin}`)} schX={0} schY={-4.9} anchorSide="top" />
  </group>
  const style = passive ? null : chipStyle(refName)
  const arrangement = style?.schPinArrangement
  const sideCount = arrangement ? Math.max(arrangement.leftSide?.length??0, arrangement.rightSide?.length??0, 1) : 1
  const pitch = refName === "U_CLK" ? 1.2 : /^U_AFE|^U_ISO|^U_OE$|^U_TDM_SCH$/.test(refName) ? .8 : refName === "U_ADC" ? .4 : .2
  const offset = passive ? .9 : Math.max(refName==="U_TDM"?1.5:1.2,
    sideCount*pitch/2+.9, Number(style?.schHeight??0)/2+.9)
  // The paired filter shunts share a vertical signal corridor. Their ground
  // bars and complete GND text live to its right, above the isolation input
  // wire, not on the next shunt's signal downleg.
  const filterShunt = /^C_FILTER[1-8][PN][12]$/.test(refName)
  // Keep the ground bar AND lettering clear of adjacent CT/OE/output routes.
  const groundDx = /^U_ISO[1-8]$/.test(refName) ? .5
    : ({U_PWR:-.6, U_AUDIO:-.6, U_TDM:.6, U_RST2:-.65} as Record<string,number>)[refName] ?? 0
  return <group schSheetName={p.schSheetName}>
    <netlabel net="GND" connectsTo={pins.map((pin: string) => `.${refName} > .${pin}`)}
      schX={p.schX + groundDx + (filterShunt ? .9 : passive && p.schRotation===0 ? .9 : 0)}
      schY={p.schY - (filterShunt ? .6 : passive && p.schRotation===0 ? 0 : offset)} anchorSide="top" />
  </group>
}

export const LocalBypassRail = ({refName, net, returnNet}: any) => {
  if (/^R_CFG[1245]$/.test(refName)) {
    const p=poseFor(refName)
    return <group schSheetName={p.schSheetName}>
      <netlabel net={net.slice(4)} connection={`.${refName} > .pin1`} schX={p.schX} schY={p.schY+.9} anchorSide="left" />
      {returnNet!=="net.GND" && <netlabel net={returnNet.slice(4)} connection={`.${refName} > .pin2`} schX={p.schX} schY={p.schY-.9} anchorSide="left" />}
    </group>
  }
  if (!/^C_(OPA\d|CLK$|TDM$|OE$|DUMP_LOGIC$|LDO_EN$|RST[12]$|PWR$|AUDIO$|VDDA|VDDIO$|LDO_[AD]$)/.test(refName) && !["R_RST_T","R_RESET_PU"].includes(refName)) return null
  const p=poseFor(refName)
  return <group schSheetName={p.schSheetName}>
    <netlabel net={net.slice(4)} connection={`.${refName} > .pin1`} schX={p.schX} schY={p.schY+.9} anchorSide="left" />
  </group>
}

export const LocalChipRail = ({refName, connections}: any) => {
  if (refName==="U_ADC") return <group schSheetName="adc">
    <netlabel net="N3V3_ADC" connectsTo={[5,9,31,38].map(pin=>`.U_ADC > .pin${pin}`)} schX={-1} schY={5} anchorSide="right" />
    {[2,3,10,11].map((pin,i)=><netlabel key={pin} net={connections[`pin${pin}`].slice(4)} connection={`.U_ADC > .pin${pin}`} schX={3.2} schY={2.8-.4*i} anchorSide="left" />)}
    <netlabel net={connections.pin7.slice(4)} connection=".U_ADC > .pin7" schX={3.2} schY={1.2} anchorSide="left" />
    <netlabel net={connections.pin32.slice(4)} connectsTo={[32,33].map(pin=>`.U_ADC > .pin${pin}`)} schX={3.2} schY={.6} anchorSide="left" />
  </group>
  const supplyPin = /^U_AFE[1-9]$/.test(refName) || ["U_CLK","U_RST2"].includes(refName) ? "pin8"
    : ["U_DUMP","U_LDO_EN","U_OE","U_TDM","U_TDM_SCH"].includes(refName) ? "pin5"
    : ["U_PWR","U_AUDIO"].includes(refName) ? "pin4" : refName==="U_RST1" ? "pin3" : null
  if (!supplyPin) return null
  const p=poseFor(refName), a=chipStyle(refName).schPinArrangement
  const pitch=refName === "U_CLK" ? 1.2 : /^U_AFE|^U_OE$|^U_TDM_SCH$/.test(refName) ? .8 : .2
  const h=Math.max(a.leftSide?.length??0,a.rightSide?.length??0,1)*pitch/2
  // Left-facing inputs/feedback own the left corridor. Supply plates grow
  // rightward from above the body, with their complete lettering clear.
  const rightPlate = /^U_AFE[1-8]$/.test(refName) || refName==="U_CLK"
  // U_AUDIO's supply downleg and PWR_EN elbow leave no horizontal plate
  // corridor immediately above VDD. Put the rail label above that elbow.
  const supplyRise = refName==="U_AUDIO" ? 2.3 : refName==="U_LDO_EN" ? 1.5 : refName==="U_CLK" ? 1.3 : .8
  return <group schSheetName={p.schSheetName}>
    <netlabel net={connections[supplyPin].slice(4)} connectsTo={(refName==="U_RST2" ? ["pin2","pin8"] : refName==="U_PWR" ? ["pin3","pin4"] : [supplyPin]).map(pin=>`.${refName} > .${pin}`)}
      schX={p.schX+(rightPlate?0:-.8)} schY={p.schY+h+supplyRise} anchorSide={rightPlate?"left":"right"} />
  </group>
}

type Path = string[]
const paths: Record<string, Path[]> = {}
export const presentationIntent = {poses, paths}
const wire = (sheet: string, ...rows: Path[]) => { paths[sheet] = [...(paths[sheet]??[]), ...rows] }
wire("input", ["J9.1","F_IN.1"], ["F_IN.2","Q_IN.5"],
  ["Q_IN.1","Q_IN.2","Q_IN.3","D_QIN_GS.1","D_IN.1"],
  ["Q_IN.4","D_QIN_GS.2","R_QIN_G.1"])
wire("buck", ["D_BUCK_IN.1","C_BUCK_IN.1","C_BUCK_IN2.1","C_BUCK_IN3.1","U_BUCK.2","U_BUCK.3"], ["U_BUCK.6","C_BUCK_BST.1"], ["U_BUCK.5","C_BUCK_BST.2","L_BUCK.1"],
  ["L_BUCK.2","U_BUCK.1","C_BUCK_O1.1","C_BUCK_O2.1","C_BUCK_O3.1"],
  ["C_OPA_BULK.1","R_OPA_BLEED1.1"],
  ["R_OPA_BLEED1.2","R_OPA_BLEED2.1"])
wire("held_ldo", ["D_HOLD.1","R_PRE.1","Q_PRE.2","R_PRE_G.2"],
  ["R_PRE.2","Q_PRE.3","C_HOLD1.1","C_HOLD2.1","C_LDO_IN.1","U_LDO.1","U_LDO.2","U_LDO.3","U_LDO.8"],
  ["Q_PRE.1","R_PRE_G.1","Q_PRE_EN.3"],
  ["U_LDO.12","U_LDO.13","U_LDO.14","C_LDO_OUT.1"],
  ["U_LDO.9","R_LDO_SET.1","C_LDO_NR4.1","C_LDO_NR5.1"])
wire("supervisors", ["R_PWR_TOP.2","R_PWR_BOT.1","U_PWR.1"], ["U_PWR.5","C_PWR_CT.1"],
  ["U_PWR.6","R_PWR_PU.2","U_AUDIO.3"], ["R_ADC_TOP.2","R_ADC_BOT.1","U_AUDIO.1"],
  ["U_AUDIO.5","C_AUDIO_CT1.1","C_AUDIO_CT2.1"], ["U_AUDIO.6","R_AUDIO_PU.2","R_AUDIO_PD.1"])
wire("dump", ["R_DUMP_TIME1.1","R_DUMP_TIME2.1"], ["R_DUMP_TIME1.2","R_DUMP_TIME2.2","C_DUMP_TIME.1","U_DUMP.2"],
  ["U_DUMP.4","U_LDO_EN.2","Q_DUMP.1","R_DUMP_PD.1"], ["Q_DUMP.3","R_DUMP.2"])
for(let n=1;n<=8;n++) wire(`analog_${n}`,
  [`F${n}.2`,`J${n}.1`,`J${n}.3`,`J${n}.7`], [`J${n}.5`,`U_ESD${n}.3`,`C_A${n}P.1`], [`J${n}.4`,`U_ESD${n}.5`,`C_A${n}N.1`],
  [`C_A${n}P.2`,`R_B${n}P.1`,`R_IN${n}P.1`], [`R_IN${n}P.2`,`U_AFE${n}.3`],
  [`C_A${n}N.2`,`R_B${n}N.1`,`R_IN${n}N.1`], [`R_IN${n}N.2`,`U_AFE${n}.5`],
  [`U_AFE${n}.2`,`C_FB${n}P.1`,`R_X${n}P.1`], [`U_AFE${n}.6`,`C_FB${n}N.1`,`R_X${n}N.1`],
  [`U_AFE${n}.1`,`C_FB${n}P.2`,`R_OUT${n}P.1`], [`U_AFE${n}.7`,`C_FB${n}N.2`,`R_OUT${n}N.1`],
  [`R_OUT${n}P.2`,`R_X${n}P.2`,`C_FILTER${n}P1.1`,`C_FILTER${n}P2.1`,`U_ISO${n}.1`],
  [`R_OUT${n}N.2`,`R_X${n}N.2`,`C_FILTER${n}N1.1`,`C_FILTER${n}N2.1`,`U_ISO${n}.5`],
  [`U_ISO${n}.2`,`R_ADC_PD${n}P.1`,`C_ADC_CM${n}P.1`], [`U_ISO${n}.6`,`R_ADC_PD${n}N.1`,`C_ADC_CM${n}N.1`],
  [`U_ISO${n}.8`,`C_ISO${n}.1`])
for(let n=1;n<=2;n++) {
  wire("vmid", [`R_VMID${n}_TOP.2`,`R_VMID${n}_BOT.1`,`C_VMID${n}_EXT_10U.1`,`C_VMID${n}_EXT_1U.1`])
  wire("references", [`R_FILT${n}P.2`,`C_FILT${n}_470U.1`,`C_FILT${n}_10U.1`,`C_FILT${n}_1U.1`],
    [`C_VMID${n}_4U7.1`,`C_VMID${n}_470N.1`])
}
wire("clocks", ["J10.9","R_MCH_MCLK_PD.1","U_CLK.1"], ["J10.10","R_MCH_BCLK_PD.1","U_CLK.3"],
  ["J10.12","R_MCH_FSYNC_PD.1","U_CLK.6"], ["U_CLK.7","R_MCLK.1"], ["U_CLK.5","R_BCLK.1"], ["U_CLK.2","R_FSYNC.1"])
wire("tdm", ["J11.2","R_MCH_SENSE.1"], ["R_MCH_SENSE.2","R_MCH_SENSE_PD.1","U_OE.2"],
  ["U_OE.4","U_TDM.1"], ["U_TDM.4","R_TDM.1"],
  ["R_TDM_PD.1","U_TDM_SCH.2"], ["U_TDM_SCH.4","U_TDM.2"])
wire("reset", ["U_RST1.2","U_RST2.3"], ["U_RST2.5","Q_RST1.1","R_RESET_GPD.1"],
  ["U_RST2.6","C_RST_T.1"], ["U_RST2.7","C_RST_T.2","R_RST_T.2"], ["Q_RST1.3","R_RESET_PU.2"])

export const SchematicWires = () => <>
  <net name="GND" isGroundNet />
  {/* Explicit output-net marker owns the producer's otherwise unmarked tail.
      Both endpoints remain connected by the continuous primary clock wire. */}
  <group schSheetName="clocks">
    {/* Own the TDM label below J10, clear of the clock input downlegs. */}
    <netlabel net="ADC_TDM" connection=".J10 > .pin2" schX={-4.7} schY={-1.8} anchorSide="right" />
    <netlabel net="MCH_BCLK" connection=".R_MCH_BCLK_PD > .pin1" schX={-3.8} schY={-2} anchorSide="left" />
    <netlabel net="MCH_FSYNC" connection=".R_MCH_FSYNC_PD > .pin1" schX={-6.5} schY={-5} anchorSide="right" />
    <netlabel net="MCLK_BUF" connectsTo={[".U_CLK > .pin7", ".R_MCLK > .pin1"]} schX={2.2} schY={1.8} anchorSide="left" />
    <netlabel net="BCLK_BUF" connectsTo={[".U_CLK > .pin5", ".R_BCLK > .pin1"]} schX={2.2} schY={.6} anchorSide="left" />
    <netlabel net="FSYNC_BUF" connectsTo={[".U_CLK > .pin2", ".R_FSYNC > .pin1"]} schX={2.2} schY={-1.8} anchorSide="left" />
  </group>
  <group schSheetName="tdm">
    {/* Keep the output identity above its wire, clear of U_TDM's ground return. */}
    <netlabel net="TDM_BUFFERED" connectsTo={[".U_TDM > .pin4", ".R_TDM > .pin1"]} schX={8.5} schY={1.8} anchorSide="left" />
  </group>
  {/* The ESD pins are only .2 apart; automatic input labels touch at that
      pitch. Give both complete label plates separate, source-owned rows. */}
  {Array.from({length:8}, (_, i) => i+1).map(n => <group key={`input-labels-${n}`} schSheetName={`analog_${n}`}>
    <netlabel net="CHASSIS" connectsTo={[`.J${n} > .pin9`, `.J${n} > .pin10`]}
      schX={-10} schY={2.8} anchorSide="right" />
    <netlabel net={`AUDIO_P${n}`} connection={`.U_ESD${n} > .pin3`} schX={-5.9} schY={-3.4} anchorSide="left" />
    <netlabel net={`AUDIO_N${n}`} connection={`.U_ESD${n} > .pin5`} schX={-5.9} schY={-4.6} anchorSide="left" />
    {/* The source net connects both selectors across sheets. A local wire
        joining those two pins alone does not display that shared identity. */}
    <netlabel net="AUDIO_EN" connectsTo={[`.U_ISO${n} > .pin3`, `.U_ISO${n} > .pin7`]} schX={5.8} schY={3.0} anchorSide="right" />
  </group>)}
  {Object.entries(paths).map(([sheet, rows]) => <group key={sheet} schSheetName={sheet} schMaxTraceDistance={40}>
    {rows.map((row,i) => <trace key={i} path={row.map(endpoint => {
      const [ref,pin] = endpoint.split(".")
      if(poseFor(ref).schSheetName!==sheet) throw new Error(`Cross-sheet primary wire: ${endpoint}`)
      return `.${ref} > .pin${pin}`
    })} />)}
  </group>)}
</>
