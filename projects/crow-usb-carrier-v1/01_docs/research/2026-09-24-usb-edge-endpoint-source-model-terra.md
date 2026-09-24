# USB edge endpoint and support-cell source-model audit

**Disposition: source-model gap; no exception or acceptance.** This records the
smallest governed direction for a future USB/JTAG model. It changes no
canonical source, P1 result, connector state, or route status.

## What current authority says

`J_USB` is an anchored P1-fixed reference at `[230,22.995,180]`
([floorplan.yaml:314](../../03_src/floorplan.yaml#L314)); it is also listed in
`p1_fixed_refs` ([p1_corridor_requirements.yaml:9-20](../../03_src/rules/p1_corridor_requirements.yaml#L9-L20)).
Yet its `usb_frontend` pattern assignment ([floorplan.yaml:1043-1052](../../03_src/floorplan.yaml#L1043-L1052))
uses region `[200,35,236,70]` ([floorplan.yaml:401-405](../../03_src/floorplan.yaml#L401-L405)).
The fixed connector therefore already lies outside that support-region rectangle.

The schema-2 checker validates every fixed reference's declared source/native
pose ([p1_corridor_capacity.py:587-602](../../../../skills/kicad-pcb/scripts/p1_corridor_capacity.py#L587-L602)); it does **not** require pattern-member bodies or courtyards to be contained by their assigned region. Region containment is instead explicit for virtual faces
([p1_corridor_capacity.py:128-143](../../../../skills/kicad-pcb/scripts/p1_corridor_capacity.py#L128-L143))
and integration regions must be in-outline and disjoint
([p1_corridor_capacity.py:352-370](../../../../skills/kicad-pcb/scripts/p1_corridor_capacity.py#L352-L370)).
Thus a fixed edge connector distinct from an internal support cell is currently
unmodeled, not an approved physical exception.

The connector authority keeps USB physical interface evidence unknown, including
mating datum, exposure, setback and service clearance
([connector_assemblies.yaml:278-329](../../03_src/rules/connector_assemblies.yaml#L278-L329)).
ADR 0011 retains connector FULL with zero unknowns before routing, promotion,
release or order ([0011-p1-floorplan-and-p2-placement-admission.md:24-29](../decisions/0011-p1-floorplan-and-p2-placement-admission.md#L24-L29)).

## Required source split

The present `usb_frontend` ownership block includes `J_USB` plus seven support
references: `C_USB_VBUS`, `R_USB_CC1`, `R_USB_CC2`, `R_USB_VBUS_BLEED`,
`U_USB_CC_ESD`, `U_USB_ESD`, and `U_USB_VBUS_ESD`
([floorplan.yaml:1043-1052](../../03_src/floorplan.yaml#L1043-L1052); see also
[modular_plan.json:670-680](../../03_src/modular_plan.json#L670-L680)).
A future governed model should explicitly represent:

1. a fixed `usb_edge_connector` endpoint for `J_USB`, tied to its native
   envelope, board-edge condition and connector-FULL evidence;
2. one or more disjoint internal USB support cells for those seven references;
3. a separately owned JTAG integration corridor.

This cannot be silently represented as one new rectangular USB cell: the
measured support envelope conflicts with fixed `J8`; the current rectangle
schema needs separate support cells or an explicitly governed multi-rectangle
extension.

Four JTAG nets are two-party `debug_connector` ↔ `xmos_core` interfaces:
`JTAG_TCK`, `JTAG_TDI`, `JTAG_TDO`, and `JTAG_TMS`
([p1_corridor_requirements.yaml:76-79](../../03_src/rules/p1_corridor_requirements.yaml#L76-L79)).
They can be the first subject of a two-participant corridor. `XU_RESET_N` is
not: it additionally has `digital_power` endpoints
([p1_corridor_requirements.yaml:80](../../03_src/rules/p1_corridor_requirements.yaml#L80)).
It requires a separate owned branch/port model, because the current integration
corridor accepts exactly two participants
([p1_corridor_capacity.py:367-370](../../../../skills/kicad-pcb/scripts/p1_corridor_capacity.py#L367-L370)).
