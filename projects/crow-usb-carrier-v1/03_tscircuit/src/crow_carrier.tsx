import { CrowRetainedAnalog } from "./crow_retained_analog"
import { CrowUsbDigital } from "./crow_usb_digital"
import { CrowUsbInputPowerHot } from "./crow_usb_input_power"
import { UsbDeviceFrontend } from "./usb_device_frontend"
import { Presented } from "./z_schematic_presentation"

const net = (name: string) => `net.${/^\d/.test(name) ? `N${name}` : name}`

export default function CrowCarrier() {
  return <group name="crow_carrier">
    <Presented domain="power"><CrowUsbInputPowerHot net={net} /></Presented>
    <Presented domain="analog"><CrowRetainedAnalog net={net} /></Presented>
    <Presented domain="digital"><CrowUsbDigital net={net} /></Presented>
    <Presented domain="usb"><UsbDeviceFrontend nets={{
      ground:net("GND"),vbus:net("VBUS_USB"),dp:net("USB_DP"),dm:net("USB_DN"),
      cc1:net("USB_CC1"),cc2:net("USB_CC2"),shield:net("GND"),
    }} /></Presented>
  </group>
}
