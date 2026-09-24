# USB region-envelope shared-zone measurement

**Research only; no source region, PCB, route, task, or P1 attempt changed.**
This measurement identifies a source-model requirement for the USB device
allocation.  It does not establish a route, pair capacity, pad access,
continuous GND reference, or P1/P2 acceptance.

## Subject and method

The source subject is `03_src/floorplan.yaml` SHA-256
`a882f87682484c37c5766a9e37c5a0d93b38a8e5a775fb1ab4425011da40a275` at
commit `e969f133`.  The native body/courtyard measurement used KiCad
`FOOTPRINT.GetBoundingBox(True, True)` on the isolated repaired-trial board,
SHA-256 `37b455203fcdae0c20880a94b17a4bcfb61103fa2b8b9df9ecf095c9c97aa519`.
That board predates the current Q_VBUS post-anchor.  Its Q_VBUS pose is
`[207.9,74.5,0]`; the current source pose is `[212.0,74.5,0]`.  I translated
only Q_VBUS's native full box by +4.100 mm in X.  The documented isolated
replay establishes that this post-anchor changes exactly that footprint pose;
all other envelopes below are native measurements from the board.

The current source rectangles are:

| Region | Current rectangle `[x0,y0,x1,y1]` mm | Full-footprint union envelope `[x0,y0,x1,y1]` mm |
| --- | --- | --- |
| `usb_frontend` | `[200,35,236,70]` | `[207.554822,19.470000,235.345000,59.161600]` |
| `usb_vbus_sense` | `[195,62,220,82]` | `[201.879822,66.538400,215.410715,77.961600]` |
| `xmos_core` | `[185,72,232,128]` | `[192.008571,82.138400,228.334287,116.684463]` |

The second envelope includes planned Q_VBUS.  Its translated full box is
`[208.589286,72.367000,215.410715,77.961600]`; the other three sense boxes
are R_VBUS_B `[204.270238,66.538400,209.329762,72.718250]`, R_VBUS_BE
`[206.394286,68.538400,211.605715,72.718250]`, and R_VBUS_PU
`[201.879822,71.505000,209.553572,74.018250]`.

Thus the member envelopes have a 7.376800-mm Y gap between frontend and
sense, and a 4.176800-mm Y gap between sense and XMOS.  The existing source
rectangles nevertheless overlap frontend/sense across `[200,62,220,70]` and
sense/XMOS across `[195,72,220,82]`.  The relevant native terminals are
U_USB_ESD.1/2 at `(214.950,50.725)` / `(215.650,50.725)`, U_XU.60/59 at
`(213.100,107.6625)` / `(212.700,107.6625)`, Q_VBUS.3 at
`(212.9375,74.5)` after the planned move, and U_XU.8 at `(200.8375,96.6)`.

## Concrete required adjustment: bounded USB transition shared zone

A single exclusive rectangular partition is not safe: a full-width frontend
trim at y=60.5 intersects fixed J_JTAG, and the current xmos top/side area is
occupied by channel-8 footprints.  Define a source-owned
`board_integration` **USB transition shared zone** with these only usable
virtual faces:

```yaml
usb_transition_shared:
  owner: board_integration
  members: [usb_frontend, usb_vbus_sense, xmos_core]
  transition_bbox_mm: [195.0, 60.5, 220.0, 81.0]
  virtual_faces:
    - {members: [usb_frontend, usb_vbus_sense], segment: [201.0, 60.5, 220.0, 60.5]}
    - {members: [usb_vbus_sense, xmos_core], segment: [195.0, 81.0, 220.0, 81.0]}
  status: P2_REQUIRED
```

This is deliberately a shared-zone requirement rather than an instruction to
add the YAML above to the current rectangle-only schema.  It must supersede
the two positive-area overlaps for USB virtual-face accounting: no USB pair
or VBUS_PRESENT_N virtual witness may be credited from either current
overlapping interior.  The two named segments are the only proposed faces.
Their widths are 19.0 mm and 25.0 mm; those are geometric face lengths, not
routing widths or capacity.

`transition_bbox_mm` is a bounded membership/accounting extent, **not** a
new exclusive physical rectangle whose vertical sides may slice occupants.
The future shared-zone schema must model those side extents as internal
membership limits (or supply a footprint-clear staggered polygon) and may
expose only the two audited horizontal faces.  This is why the adjustment
removes overlap from USB virtual-face accounting without pretending that a
single rectangle can repartition the whole placed board.

Native full-box intersection checks find **zero** footprints on both named
segments.  The exact 27-ref `p1_fixed_refs` authority was read from
`p1_corridor_requirements.yaml` (SHA-256
`9ef85e5f4918dea0378203a97fa631ce2e73a690170235902a97a6c8e30527d8`): zero
of its 27 refs intersects either segment.  This preserves J1..J8, J_PWR,
J_USB, J_JTAG, and C_HOLD1..16.

## Why a simple rectangle is rejected

At y=60.5, the full-width `[200,236]` cut intersects `C_FILTER8N1`
`[196.049049,57.839313,200.950952,62.428250]` and fixed J_JTAG
`[225.090000,38.307684,230.910000,61.692315]`.  Restricting the upper face
to x=201..220 clears both.  At y=81, the proposed lower x=195..220 segment
is clear, but a full x=185..232 cut intersects C_SPOKE_DVDT8,
C_SPOKE_OUT8, and R_SPOKE_UVLO8.  A direct x=195 sidewall through y=72..81
also crosses C_A8N, R_IN8N, and U_AFE8; U_AFE8 is
`[192.651191,73.540000,202.948810,80.648250]`.  These are full native
envelopes, so a rectilinear carve-out cannot be represented safely without a
staggered/polygon boundary and an owner model.

The shared-zone implementation must therefore record: (1) the two exact face
segments above; (2) each member endpoint and a P2 pad-to-face obligation for
USB_DP, USB_DN, and VBUS_PRESENT_N; (3) the local VBUS/current and continuous
native GND-return obligations; and (4) all foreign full-footprint occupants
of its transition bbox as retained obstacles, never as cleared capacity.  It
must update the modular owner/witness model before any coarse checker can use
these faces.  This observation does not authorize that implementation.
