// Draft component-level source. No firmware or complete board is defined here.
// Native land/hole geometry is owned by the exact part dossier and KiCad library.
// Default TSX lands mirror the native footprint; sheet placement is independent.
export const usbReceptacleMpn = "USB4105-GF-A-120"
export const usbReceptacleContacts = {
  pin1: "A1_GND", pin2: "A4_VBUS", pin3: "A5_CC1", pin4: "A6_DP",
  pin5: "A7_DM", pin6: "A8_SBU1_NC", pin7: "A9_VBUS", pin8: "A12_GND",
  pin9: "B1_GND", pin10: "B4_VBUS", pin11: "B5_CC2", pin12: "B6_DP",
  pin13: "B7_DM", pin14: "B8_SBU2_NC", pin15: "B9_VBUS", pin16: "B12_GND",
  pin17: "SHIELD",
} as const

type UsbNets = { ground: string; vbus: string; dp: string; dm: string;
  cc1: string; cc2: string; shield: string }

export function usbReceptacleConnections(n: UsbNets) {
  if (n.cc1 === n.cc2 || n.dp === n.dm || n.vbus === n.ground)
    throw new Error("USB receptacle requires distinct CC, data and power nets")
  return {
    pin1: n.ground, pin2: n.vbus, pin3: n.cc1, pin4: n.dp, pin5: n.dm,
    pin7: n.vbus, pin8: n.ground, pin9: n.ground, pin10: n.vbus,
    pin11: n.cc2, pin12: n.dp, pin13: n.dm, pin15: n.vbus,
    pin16: n.ground, pin17: n.shield,
  }
}

// Native aliases map these numbered TSX ports to manufacturer contact names.
// Four manufacturer-defined power lands have two logical contacts each.
export const usbContactLands = [
  [-3.2, 0.6], [-2.4, 0.6], [-1.25, 0.3], [-0.25, 0.3],
  [0.25, 0.3], [1.25, 0.3], [2.4, 0.6], [3.2, 0.6],
  [3.2, 0.6], [2.4, 0.6], [1.75, 0.3], [0.75, 0.3],
  [-0.75, 0.3], [-1.75, 0.3], [-2.4, 0.6], [-3.2, 0.6],
] as const

export function UsbReceptacleFootprint() {
  return <footprint>
    {usbContactLands.map(([x, width], i) => <smtpad
      portHints={[String(i + 1)]} pcbX={x} pcbY={-3.68}
      width={width} height={1.15} shape="rect" />)}
    {[-4.32, 4.32].map(x => <platedhole portHints={["17"]}
      pcbX={x} pcbY={-3.105} shape="pill" outerWidth={1} outerHeight={2.1}
      holeWidth={0.6} holeHeight={1.7} />)}
    {[-4.32, 4.32].map(x => <platedhole portHints={["17"]}
      pcbX={x} pcbY={1.075} shape="pill" outerWidth={1} outerHeight={1.8}
      holeWidth={0.6} holeHeight={1.4} />)}
    {[-2.89, 2.89].map(x => <hole pcbX={x} pcbY={-2.605}
      diameter={0.65} />)}
  </footprint>
}

// Pins6/14 (SBU1/2) intentionally have no connection in USB2-only operation.
// The complete schematic must preserve explicit NC annotations in native output.
export function UsbReceptacle({ nets, footprint = UsbReceptacleFootprint(), schX = 0, schY = 0 }:
  { nets: UsbNets; footprint?: any; schX?: number; schY?: number }) {
  return <chip name="J_USB" manufacturerPartNumber={usbReceptacleMpn}
    supplierPartNumbers={{jlcpcb: ["C5184243"]}}
    pinLabels={usbReceptacleContacts} connections={usbReceptacleConnections(nets)}
    footprint={footprint} schSheetName="usb" schSectionName="USB interface"
    schX={schX} schY={schY} />
}
