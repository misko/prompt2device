# Crow routing-intent adoption

The copied load-cell netclasses are replaced with Crow's USB, input trunk,
5 V parent, digital supply, spoke supply and quiet analog supply classes.
`jlc_4layer_standard` is the initial fabrication ceiling for the selected
four-layer 1 oz stack; ordinary through vias are intended. Package escape,
realized current capacity and voltage drop still require board evidence.
The power widths are preliminary design floors, not an ampacity/IR pass.

USB negative net is renamed from `USB_DM` to `USB_DN`. Device pin function
names remain D-/DM. Native KiCad BOARD.DpCoupledNet was tested on an in-memory
three-net fixture: USB_DP returns USB_DN; USB_DN returns USB_DP; USB_DM returns
no partner. The official naming contract is documented at
https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#routing-differential-pairs.

The existing generic rule generator emitted six classes, 23 exact patterns
and the USB differential width/gap of0.410/0.150mm in a scratch fixture.
All23members exist uniquely in current Circuit JSON. The source's422component
names and1276pin/net endpoints match the baseline after only the explicit
USB_DM-to-USB_DN alias substitution. TypeScript and RF-CONTRACT pass.

Actual board pairing, return paths, launches, skew and current margins remain
owed. The fixture is neither product board generation nor a release witness.
