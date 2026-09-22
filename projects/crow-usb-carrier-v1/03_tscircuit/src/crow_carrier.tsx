import { CrowRetainedAnalog } from "./crow_retained_analog"
import { CrowUsbDigital } from "./crow_usb_digital"
import { CrowUsbInputPowerHot } from "./crow_usb_input_power"
import { UsbDeviceFrontend } from "./usb_device_frontend"

// Full electrical source. Board geometry belongs to floorplan.yaml.
// ADR0004: USB shell is local GND; Crow spoke shells retain separate CHASSIS.
const net = (name: string) => `net.${/^\d/.test(name) ? `N${name}` : name}`

export default function CrowCarrier() {
  return <group name="crow_carrier">
    <CrowUsbInputPowerHot net={net} />
    <CrowRetainedAnalog net={net} />
    <CrowUsbDigital net={net} />
    <UsbDeviceFrontend nets={{
      ground: net("GND"), vbus: net("VBUS_USB"),
      dp: net("USB_DP"), dm: net("USB_DM"),
      cc1: net("USB_CC1"), cc2: net("USB_CC2"), shield: net("GND"),
    }} />
  </group>
}
