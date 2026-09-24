# P1 USB and TDM sub-lane proposal

Follow-up: the [isolated native measurement](2026-09-24-p1-isolated-native-sublane-measurement-terra.md)
found the USB screening strip clear of foreign F.Cu body/pad obstacles but
rejected the single TDM lane proposal because its four XU endpoints do not
share one usable reservation. Neither result admits P1.

This is a source-geometry proposal, not routed copper, a P1 receipt, or permission to run a previous P1 attempt. The current source declares no `geometry` for any P1 allocation, and `04_kicad/crow_carrier.kicad_pcb` is absent. Consequently no current-board clearance, outline, rule-area, pour, or reference-plane measurement is available yet.

The USB device allocation has one F.Cu pair slot: 0.97 mm required width, 0.56 mm pair centre spacing, and endpoints J_USB.12/J_USB.4/U_USB_ESD.1 to U_XU.60 for DP and J_USB.13/J_USB.5/U_USB_ESD.2 to U_XU.59 for DN. The present source anchors U_USB_ESD at (217.0, 36.0, 0) and U_XU at (208.5, 100.0, 90). A board-bound next probe should reserve a vertical F.Cu strip centred near x=216.75 mm, with the 1.30 mm screening envelope x=216.10..217.40 mm, from immediately above the ESD footprint exit to immediately below the XU USB-pad escape. The strip is deliberately wider than the stated 0.97 mm pair demand: it leaves a 0.165 mm side allowance on each side for endpoint necks and later proof. It is not a claim that a route may pass through either footprint.

The required native measurement is the contiguous free F.Cu interval between the two endpoint pockets, after subtracting footprint courtyards, rule areas, outline margin and foreign pads. It must record the four exact ESD/XU pad centres, connector-side ESD entries, strip centre/width, and a filled In1 GND sample below every segment. The short isolated U_XU launch experiment named by the requirements cannot substitute for this measurement; it did not prove J_USB-to-ESD-to-XU capacity or the return.

For a second critical bundle, measure the four-track `tdm_to_xmos` lane before attempting the broader ADC bundle. Its declared demand is AUDIO_MCLK_1V8, TDM_BCLK_1V8, TDM_DATA_1V8 and TDM_FSYNC_1V8, four F.Cu slots at 0.45 mm, hence 1.80 mm. Its XU endpoints are U_XU.23/.22/.107/.20 and its translator endpoints are U_TDM_XLATE.6/.4/.7/.5. The concrete proposal is a single 2.20 mm F.Cu reservation between the perimeter-facing TDM side of U_XU and the U_TDM_XLATE cell, giving 0.20 mm aggregate screening allowance beyond the declared 1.80 mm. Keep it separate from the USB strip and from the ADC analog boundary; do not combine it with the unmeasured I2C/READY/AUDIO_EN control window.

The next isolated board probe may place only these two reservations and run the declared `p1_corridor_capacity.py` measurement. Its receipt must include board SHA, contract SHA, all named endpoint pad/net pockets, outline/rule-area/pour results, and continuous filled-reference evidence. P1 remains false until those facts and the independent semantic packet review exist.
