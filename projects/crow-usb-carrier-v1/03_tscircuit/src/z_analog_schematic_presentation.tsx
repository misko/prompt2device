// Source-owned schematic composition only. Electrical connections remain in
// crow_retained_analog.tsx; these values do not define PCB placement.
// A missing reference is fatal so adding a component cannot silently omit it.
type Pose = [string, number, number, number?]
const poses: Record<string, Pose> = {}
const own = (sheet: string, rows: Record<string, number[]>) => {
  for (const [ref, p] of Object.entries(rows)) {
    if (poses[ref]) throw new Error(`Duplicate schematic owner: ${ref}`)
    poses[ref] = [sheet, p[0], p[1], p[2]]
  }
}

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
  C_LDO_IN:[1,2,-90], U_LDO:[6,1], C_LDO_OUT:[12,1,-90],
  // SET leaves the top of U_LDO. Keep its resistor/capacitors above that
  // pin, so the primary wire does not loop through the chip reference.
  R_LDO_SET:[6,8,-90],
  C_LDO_NR4:[10,8,-90], C_LDO_NR5:[14,8,-90],
  R_LDO_ILIM:[5,-4,-90],
  R_LDO_PG_TOP:[12,5,-90], R_LDO_PG_BOT_A:[16,5,-90], R_LDO_PG_BOT_B:[20,5,-90],
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
  own(`spoke_protection_${n}`, {
    [`U_SPOKE${n}`]:[0,0],
    [`R_SPOKE_UVLO${n}`]:[-6,4],
    [`R_SPOKE_ILIM${n}`]:[5,-2,-90],
    [`C_SPOKE_DVDT${n}`]:[8,-2,-90],
    [`C_SPOKE_IN${n}`]:[-8,-2,-90],
    [`C_SPOKE_OUT${n}`]:[5,4,-90],
  })
  own(`analog_${n}`, {
    [`J${n}`]:[-10,0], [`U_ESD${n}`]:[-8.5,-4],
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
  U_ADC:[0,0], R_CFG1:[5,5], R_CFG2:[9,5],
  R_CFG4:[5,2], R_CFG5:[9,2],
  C_LDO_A:[5,-3,-90], C_LDO_D:[8,-3,-90],
  C_VDDA1_4U7:[-4,-10,-90], C_VDDA1_10N:[0,-10,-90],
  C_VDDA2_4U7:[4,-10,-90], C_VDDA2_10N:[8,-10,-90], C_VDDIO:[12,-10,-90],
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
own("reset_supervisors", {
  U_RST1:[-14,3], C_RST1:[-14,-1,-90],
  U_ADC_1V8_OK:[-8,3], U_ADC_3V3X_OK:[-1,3],
  R_ADC_DIGITAL_OK_PU:[4,6], C_ADC_DIGITAL_OK:[4,0,-90],
  U_ADC_DIGITAL_BAD:[9,5], C_ADC_DIGITAL_BAD:[13,6,-90], Q_ADC_DIG_RST:[17,5], R_ADC_DIG_RST_PD:[21,5,-90],
  U_ADC_READY:[9,0], C_ADC_READY:[13,1,-90], R_ADC_READY_PD:[17,0,-90],
})
own("reset_sequencer", {
  R_ADC_START_DELAY:[-10,3], C_ADC_START_DELAY:[-6,0,-90],
  U_ADC_READY_BAD:[-2,4], C_ADC_READY_BAD:[4,5,-90], R_ADC_DELAY_GATE_PD:[5,3], Q_ADC_DELAY_DISCH:[2,-2],
  U_RST2:[7,-2], C_RST2:[7,-6,-90], R_RST_T:[12,0,-90], C_RST_T:[12,-3,-90], Q_RST1:[17,-2],
  R_RESET_PU:[17,1,-90], R_RESET_GPD:[12,-6,-90],
})

export const poseFor = (ref: string) => {
  const p = poses[ref]
  if (!p) throw new Error(`No source-owned schematic pose: ${ref}`)
  return {schSheetName:p[0], schSectionName:p[0], schX:p[1], schY:p[2], schRotation:p[3] ?? 0}
}

// Pin functions are unchanged. Arrangement is explicitly human-flow oriented.
export const chipStyle = (ref: string): any => {
  if (/^U_SPOKE[1-8]$/.test(ref)) return {
    schWidth:3, schPinStyle:pinStyle(11,.5),
    schPinArrangement:{leftSide:[1,2,4],rightSide:[10,9,7,8],bottomSide:[3,5,11,6]},
  }
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
  if (["U_ADC_1V8_OK","U_ADC_3V3X_OK"].includes(ref)) return {
    schWidth:4.2, schHeight:3.2,
    schPinArrangement:{leftSide:[1,3],rightSide:[6],topSide:[4],bottomSide:[2,5]},
    schPinStyle:pinStyle(6,.35),
  }
  if (/^F[1-8]$/.test(ref) || ["F_IN","L_BUCK","FB_OPA"].includes(ref))
    return {schPinArrangement:{leftSide:[1],rightSide:[2]}}
  const arrangements: Record<string, any> = {
    J9:{rightSide:[1],bottomSide:[2]},
    Q_IN:{leftSide:[5],rightSide:[1,2,3],bottomSide:[4]},
    D_IN:{topSide:[1],bottomSide:[2]}, D_QIN_GS:{leftSide:[1],bottomSide:[2]},
    U_BUCK:{leftSide:[3,2],rightSide:[5,1],topSide:[6],bottomSide:[4]},
    D_BUCK_IN:{leftSide:[2],rightSide:[1]}, D_HOLD:{leftSide:[2],rightSide:[1]}, Q_PRE:{leftSide:[2],rightSide:[3],bottomSide:[1]},
    Q_PRE_EN:{leftSide:[1],topSide:[3],bottomSide:[2]},
    U_LDO:{leftSide:[1,2,3],rightSide:[10,9,6,4],topSide:[7],bottomSide:[5,8,11]},
    U_PWR:{leftSide:[1],rightSide:[6],topSide:[3,4],bottomSide:[2,5]},
    U_AUDIO:{leftSide:[1,3],rightSide:[6],topSide:[4],bottomSide:[2,5]},
    U_DUMP:{leftSide:[2,1],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_LDO_EN:{leftSide:[2,1],rightSide:[4],topSide:[5],bottomSide:[3]},
    Q_DUMP:{leftSide:[1],rightSide:[3],bottomSide:[2]},
    U_ADC:{leftSide:[40,39,42,41,46,45,48,47,14,13,16,15,20,19,22,21,1,12,43,18],
      rightSide:[5,9,31,38,4,35,36,37,6,8,17,30,44,49,2,3,10,11,7,32,33,23,24,25,26,27,28,29,34]},
    J10:{leftSide:[1,3,4,5,6,7,8],rightSide:[9,10,12,2],bottomSide:[11]},
    J11:{leftSide:[3,4,5,6,7],rightSide:[2,8,9,10,11,12],bottomSide:[1]},
    U_CLK:{leftSide:[1,3,6],rightSide:[7,5,2],topSide:[8],bottomSide:[4]},
    U_OE:{leftSide:[2,1],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_TDM_SCH:{leftSide:[2,1],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_TDM:{leftSide:[2,1],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_RST1:{rightSide:[2],topSide:[3],bottomSide:[1]},
    U_ADC_1V8_OK:{leftSide:[1,3],rightSide:[6],topSide:[4],bottomSide:[2,5]},
    U_ADC_3V3X_OK:{leftSide:[1,3],rightSide:[6],topSide:[4],bottomSide:[2,5]},
    U_ADC_DIGITAL_BAD:{leftSide:[2],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_ADC_READY:{leftSide:[1,2],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_ADC_READY_BAD:{leftSide:[2],rightSide:[4],topSide:[5],bottomSide:[3]},
    U_RST2:{leftSide:[3],rightSide:[5,6,7],topSide:[2,8],bottomSide:[1,4]},
    Q_RST1:{leftSide:[1],rightSide:[3],bottomSide:[2]},
    Q_ADC_DIG_RST:{leftSide:[1],rightSide:[3],bottomSide:[2]},
    Q_ADC_DELAY_DISCH:{leftSide:[1],rightSide:[3],bottomSide:[2]},
  }
  const arrangement = arrangements[ref]
  if (!arrangement) throw new Error(`No schematic chip arrangement: ${ref}`)
  return {schPinArrangement:arrangement,
    // Separate horizontal NC labels from the vertical ground/EP labels.
    ...(ref === "U_LDO" ? {schWidth:4.5,schHeight:3.8,schPinStyle:pinStyle(11,.35)} : {}),
    ...(ref === "U_ADC" ? {schWidth:3.5,schPinStyle:pinStyle(49,.18)} : {}),
    ...(["U_OE","U_TDM_SCH","U_TDM","U_ADC_DIGITAL_BAD","U_ADC_READY","U_ADC_READY_BAD"].includes(ref)
      ? {schWidth:3.5,schHeight:3,schPinStyle:pinStyle(5,.35)} : {}),
    ...(ref === "U_CLK" ? {schPinStyle:pinStyle(8,.5)} : {})}
}
const pinStyle = (count: number, margin: number) => Object.fromEntries(
  Array.from({length:count}, (_,i) => [`pin${i+1}`, {topMargin:margin,bottomMargin:margin}]),
)
