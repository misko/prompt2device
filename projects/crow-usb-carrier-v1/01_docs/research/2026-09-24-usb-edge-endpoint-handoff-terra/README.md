# USB edge endpoint/support handoff proposal

**Status: proposed research only.** This is a source-model repair plan, not a
canonical edit or a routing/connector acceptance claim.

The current source declares `J_USB` inside `UsbDeviceFrontend`: the import,
receptacle connection record, and JSX instantiation are all in
[`usb_device_frontend.tsx`](../../../03_tscircuit/src/usb_device_frontend.tsx).
The carrier therefore creates the entire connector/support block as one
`Presented domain="usb"` instance. The floorplan contradicts that ownership
boundary: `J_USB` is placed at `(230, 22.995, 180)`, while the declared
`usb_frontend` rectangle is `[200, 35, 236, 70]`. The connector's nominal
origin is 12.005 mm outside the region, on the edge side. The same file also
assigns `J_USB` to the `usb_frontend` region.

`proposal.yaml` names a new `usb_edge_connector` owner for the receptacle and
retains all seven supporting references under `usb_frontend`. It carries an
exact endpoint census rather than treating the duplicated Type-C contacts as a
single abstract port: J_USB has 17 physical ports, 15 connected net leaves and
two intentional SBU NC leaves. It also models the data and support nets as
trees, so the ESD pads remain shunt leaves rather than invented series
components.

The earlier research-only edge-region candidate `[220, 20, 240, 35]` is
withdrawn. On pinned native board `fbfb3bda`, extractor
`2026-09-24-usb-debug-courtyard-bbox-sol.py` measures the J_USB F.CrtYd bbox as
`[224.955, 19.450, 235.045, 27.800]` mm. The candidate starts at y=20 and
therefore excludes the courtyard by 0.550 mm at its north edge. This proposal
deliberately leaves the final edge region and any outline exception unresolved
until connector FULL evaluates that complete native envelope.

The paired data trees each have four endpoints: two connector contacts, one
ESD shunt pad and one XMOS PHY pin. `VBUS_USB` has eight declared endpoints:
four connector contacts, three local-support endpoints and the one VBUS-sense
endpoint. `USB_CC1` and `USB_CC2` each have three. These counts are deliberate
source invariants, not a claim that copper exists between them.

The separate reset branch is already fully enumerated in both the modular plan
and P1 corridor requirements: `J_JTAG.10`, `R_XU_RST_PU.2`, `U_CORE_OK.1`,
`U_XU_3V3_OK.6` and `U_XU.38`. That is five endpoints across three owners.
It must remain a wired-open-drain tree: the resistor is the one pull-up and
both supervisors and a service probe can only assert low. A point-to-point
handoff would lose either an assertion source or the pull-up.

## Concrete source change, if separately approved

1. Remove the `UsbReceptacle` import, `receptacle` connection entry and JSX
   call from `UsbDeviceFrontend`; narrow its input type so `shield` and
   `receptacleFootprint` cannot be silently accepted.
2. Instantiate `UsbReceptacle` once at carrier level in a new
   `usb_edge_connector` presentation/schematic sheet, using the same seven
   canonical nets. Keep the frontend support block separate.
3. Add `usb_edge_connector` to the modular plan and handoff records. Transfer
   every `J_USB.*` endpoint from `usb_frontend` to that owner, preserving the
   endpoint trees in the YAML proposal. Select its floorplan region and any
   outline exception only after connector FULL checks the complete native
   courtyard envelope.
4. Regenerate the native artifact and independently check the generated
   census, explicit SBU NC annotations, J_USB edge envelope, protection launch,
   USB differential routing/return, and native DRC.

## Evidence / blockers

- [`usb_receptacle.tsx`](../../../03_tscircuit/src/usb_receptacle.tsx) maps pins
  1--17 and intentionally leaves 6/14 unconnected. The numbered connection
  record has 15 entries.
- [`nets.yaml`](../../../03_src/rules/nets.yaml) already describes DP/DN as
  four-leaf trees, but its route contract only anchors A-side J_USB endpoints
  in `octilinear_endpoints`; this must not be mistaken for a complete launch
  proof.
- [`modular_plan.json`](../../../03_src/modular_plan.json) currently assigns the
  J_USB DP/DN and VBUS leaves to `usb_frontend`, so merely splitting TSX JSX
  would leave source ownership inconsistent.
- [`p1_corridor_requirements.yaml`](../../../03_src/rules/p1_corridor_requirements.yaml)
  already lists the exact five reset endpoints, but has null geometry. Its
  five-slot `jtag_reset` demand is a capacity declaration, not routed copper.
- The independent native review says the saved-board USB DP/DN copper stops at
  the ESD/XMOS portion and does not connect either pair to J_USB contacts;
  see [`2026-09-24-xu-usb-esd-route-independent-terra.md`](../../../08_reviews/2026-09-24-xu-usb-esd-route-independent-terra.md).
  Connector FULL, P1, route, impedance, return and DRC therefore remain
  blocked after this source-model proposal.
