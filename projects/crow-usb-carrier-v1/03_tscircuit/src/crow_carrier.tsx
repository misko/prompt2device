import { CrowRetainedAnalog } from "./crow_retained_analog"
import { CrowUsbDigital } from "./crow_usb_digital"
import { CrowUsbInputPowerHot } from "./crow_usb_input_power"
import { UsbDeviceFrontend } from "./usb_device_frontend"
import { Presented } from "./z_schematic_presentation"

const net = (name: string) => `net.${/^\d/.test(name) ? `N${name}` : name}`

const schematicPages = [
  "power_input", "power_buck", "analog_power_aux", "held_ldo", "supervisors", "dump",
  "spoke_protection_1", "spoke_protection_2", "spoke_protection_3", "spoke_protection_4",
  "spoke_protection_5", "spoke_protection_6", "spoke_protection_7", "spoke_protection_8",
  "analog_1", "analog_2", "analog_3", "analog_4", "analog_5", "analog_6", "analog_7", "analog_8",
  "adc", "vmid", "references", "reset_supervisors", "reset_sequencer",
  "digital_power_3v3x", "digital_power_1v8", "digital_power_core", "xmos_core",
  "xmos_decoupling", "flash_clock", "audio_oscillator", "tdm_translation", "fsync_shaping",
  "adc_clock_control", "usb_logic", "debug", "usb_frontend",
] as const

export default function CrowCarrier() {
  return <group name="crow_carrier">
    {schematicPages.map((name, index) => <schematicsheet key={name} name={name}
      displayName={name.replaceAll("_", " ").toUpperCase()} sheetIndex={index + 1} />)}
    <Presented domain="power"><CrowUsbInputPowerHot net={net} /></Presented>
    <Presented domain="analog"><CrowRetainedAnalog net={net} /></Presented>
    <Presented domain="digital"><CrowUsbDigital net={net} /></Presented>
    <Presented domain="usb"><UsbDeviceFrontend nets={{
      ground:net("GND"),vbus:net("VBUS_USB"),dp:net("USB_DP"),dm:net("USB_DN"),
      cc1:net("USB_CC1"),cc2:net("USB_CC2"),shield:net("GND"),
    }} /></Presented>
  </group>
}
