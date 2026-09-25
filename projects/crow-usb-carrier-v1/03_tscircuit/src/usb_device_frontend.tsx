import { UsbReceptacle, usbReceptacleConnections } from "./usb_receptacle"

type Nets = Parameters<typeof usbReceptacleConnections>[0]

// Component-level source only. VBUS sense and shield bond
// are integration boundaries, not silently supplied by this module.
export function usbFrontendConnections(n: Nets) {
  const { shield, ...electrical } = n
  if (new Set(Object.values(electrical)).size !== 6 ||
      (shield !== n.ground && Object.values(electrical).includes(shield)))
    throw new Error("USB data, CC and power nets must be distinct; shield may bond only to ground")
  return {
    receptacle: usbReceptacleConnections(n),
    cc1: { pin1: n.cc1, pin2: n.ground },
    cc2: { pin1: n.cc2, pin2: n.ground },
    esd: { pin1: n.dp, pin2: n.dm, pin3: n.ground },
    ccEsd: { pin3: n.cc1, pin4: n.ground, pin5: n.cc2 },
    vbusEsd: { pin3: n.vbus, pin4: n.ground },
    vbusCap: { pin1: n.vbus, pin2: n.ground },
    vbusBleed: { pin1: n.vbus, pin2: n.ground },
  }
}

// Nexperia PESD2USB5UX-T Figure 14 exact SOT23 reflow lands in the
// tscircuit y-up frame; pins 1/2 form the paired side and common-anode pin 3
// is isolated. The land drawing is unlabeled; numbering follows Table 2 and
// Figure 13 after a rotation. No unverified generic STEP model is attached.
function dataEsdFootprint() { return <footprint>
  <smtpad portHints={["1"]} pcbX="-0.95mm" pcbY="0.85mm" width="0.6mm" height="0.7mm" shape="rect" />
  <smtpad portHints={["2"]} pcbX="0.95mm" pcbY="0.85mm" width="0.6mm" height="0.7mm" shape="rect" />
  <smtpad portHints={["3"]} pcbX="0mm" pcbY="-0.85mm" width="0.5mm" height="0.7mm" shape="rect" />
</footprint> }

// Explicit DRL lands: pinned footprinter does not recognize "sot553".
// TI DRL0005A centers and lands are reflected into tscircuit's y-up local frame.
function auxiliaryEsdFootprint() { return <footprint>
  {[[1,-0.74,0.5],[2,-0.74,0],[3,-0.74,-0.5],
    [4,0.74,-0.5],[5,0.74,0.5]].map(([pin,x,y]) =>
    <smtpad portHints={[String(pin)]} pcbX={x} pcbY={y}
      width={0.67} height={0.30} shape="rect" />)}
</footprint> }

export function UsbDeviceFrontend({ nets, receptacleFootprint }:
  { nets: Nets; receptacleFootprint?: any }) {
  const c = usbFrontendConnections(nets)
  return <>
    <UsbReceptacle nets={nets} footprint={receptacleFootprint} schX={-12} />
    <resistor name="R_USB_CC1" resistance="5.1k" footprint="0402"
      manufacturerPartNumber="RC0402FR-075K1L" supplierPartNumbers={{jlcpcb:["C105872"]}}
      connections={c.cc1} schSheetName="usb" schSectionName="USB interface" schX={-4} schY={-5} />
    <resistor name="R_USB_CC2" resistance="5.1k" footprint="0402"
      manufacturerPartNumber="RC0402FR-075K1L" supplierPartNumbers={{jlcpcb:["C105872"]}}
      connections={c.cc2} schSheetName="usb" schSectionName="USB interface" schX={-4} schY={-9} />
    <chip name="U_USB_ESD" manufacturerPartNumber="PESD2USB5UX-TR"
      supplierPartNumbers={{jlcpcb:["C3709087"]}} pinLabels={{pin1:"DP",pin2:"DM",pin3:"GND"}}
      connections={c.esd} footprint={dataEsdFootprint()}
      schSheetName="usb" schSectionName="USB interface" schX={1} schY={2} />
    <chip name="U_USB_CC_ESD" manufacturerPartNumber="TPD2E2U06DRLR"
      supplierPartNumbers={{jlcpcb:["C1972959"]}} footprint={auxiliaryEsdFootprint()}
      pinLabels={{pin1:"NC1",pin2:"NC2",pin3:"CC1",pin4:"GND",pin5:"CC2"}}
      connections={c.ccEsd} schSheetName="usb" schSectionName="USB interface" schX={1} schY={-6} />
    {/* Pins1/2 are package NC; unused second VBUS-array channel pin5 is NC. */}
    <chip name="U_USB_VBUS_ESD" manufacturerPartNumber="TPD2E2U06DRLR"
      supplierPartNumbers={{jlcpcb:["C1972959"]}} footprint={auxiliaryEsdFootprint()}
      pinLabels={{pin1:"NC1",pin2:"NC2",pin3:"VBUS",pin4:"GND",pin5:"UNUSED_NC"}}
      connections={c.vbusEsd} schSheetName="usb" schSectionName="USB interface" schX={1} schY={8} />
    {/* XMOS self-powered reference requires 1-10uF at connector VBUS and 47k
        discharge. Exact 4.7uF/16V/X7R/0805 identity is retained in its dossier. */}
    <capacitor name="C_USB_VBUS" capacitance="4.7uF" footprint="0805"
      manufacturerPartNumber="GCM21BR71C475KA73L" supplierPartNumbers={{jlcpcb:["C90791"]}}
      connections={c.vbusCap} schSheetName="usb" schSectionName="USB interface" schX={5} schY={8} />
    <resistor name="R_USB_VBUS_BLEED" resistance="47k" footprint="0402"
      manufacturerPartNumber="RC0402FR-0747KL" supplierPartNumbers={{jlcpcb:["C93943"]}}
      connections={c.vbusBleed} schSheetName="usb" schSectionName="USB interface" schX={5} schY={11} />
  </>
}
