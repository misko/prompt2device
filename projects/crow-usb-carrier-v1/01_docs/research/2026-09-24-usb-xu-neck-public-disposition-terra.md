# Public disposition: XU USB launch necks — 2026-09-24

**Disposition: reject a source exception at this time.** The six scratch F.Cu
segments at 0.150 or 0.250 mm are physically within JLCPCB's published
multilayer 1-oz copper capability and do not introduce a new assembly-pitch
failure for the named packages.  That establishes *fabricability*, not a
90-ohm USB launch.  No public primary record found in this review supplies an
allowable stepped-width length, transition profile, reflection limit, or eye
mask result for the exact `0.410 -> 0.250 -> 0.150` geometry on
JLC04161H-7628G.  A waiver that turns those six tracks into accepted source
copper would therefore make an unsupported impedance claim.

This note uses public web records only; it makes no private JLC request,
uploads no Gerber, and uses no unpublished quotation/DFM response.  It does
not edit the canonical rule or route source.

## Exact subject and existing source authority

At `da1056a4`, `03_src/rules/nets.yaml` makes `USB_HS` canonical:
`USB_DP`/`USB_DN`, F.Cu, `min_width: 0.410 mm`, `clearance: 0.150 mm`,
`diff_pair.width: 0.410 mm`, `gap: 0.150 mm`, and `no_vias: true`.
`03_src/rules/rf.yaml` binds that full-width pair to masked F.Cu over In1.Cu
on JLC04161H-7628G and retains JLC's 89.611-ohm solve for 0.410/0.150 mm.
That source rule is the only impedance geometry presently supported by the
checked-in evidence.

The independent replay review
[`2026-09-24-xu-usb-esd-route-independent-terra.md`](../../08_reviews/2026-09-24-xu-usb-esd-route-independent-terra.md)
identifies exactly **six** launch tracks at 0.150 or 0.250 mm.  They pass only
when a scratch DRU area lowers the width floor; checking against the committed
native source produces six `track_width` violations.  The earlier isolated
launch diagnostic records the local geometry: two PHY pad departures begin at
the U_XU pad edges, reach 0.410 mm at x=217.425, and the stepped interval spans
only x=216.900 to x=217.425 (0.525 mm longitudinal envelope per line).
It is a two-line local envelope, **not** a measured taper length or an allowed
discontinuity length.  The later ESD-connected scratch route has 15 F.Cu
tracks, no USB via, and 0.150-mm pair gap, but that does not change the six
width exceptions into a qualified launch.

## What the public records establish

| Question | Public primary evidence | Result |
|---|---|---|
| Can 0.150-mm-wide masked F.Cu copper be fabricated on a four-layer, 1-oz JLC board? | JLC's [capability table](https://jlcpcb.com/capabilities/Capab) says 0.09-mm minimum trace/clearance for multilayer 0.5/1-oz copper; its [copper-weight guide](https://jlcpcb.com/help/article/jlcpcb-copper-weight) also gives 0.09 mm for >=4-layer FR-4 at 0.5/1 oz. | **Yes, as a bare-copper minimum.** 0.150 and 0.250 mm exceed 0.09 mm. This is not a controlled-impedance guarantee. |
| Is the narrow copper transition an assembly-pitch claim? | The exact clamp is TI TPD2EUSB30A in DRT-3; TI's [datasheet](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf) gives the package and requires connector-adjacent, straight protected traces. The XU316 is TQ128 at 0.40-mm pitch; the XMOS [XU316 datasheet](https://www.xmos.com/documentation/XM-015129-PC/pdf/XU316-1024.pdf) gives its package and USB routing requirements. JLC [PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) lists 0.35-mm minimum IC pin pitch for Standard PCBA. | **No new assembly exception is implied by trace width.** Assembly concerns pad/pitch and stencil, while these six items are copper leaving already-selected pads. This does not approve a changed pad, mask, or paste aperture. |
| Does a public primary record qualify a 0.525-mm stepped launch for 90-ohm USB? | XMOS specifies 90-ohm USB differential impedance and matched routing, while TI asks for the clamp close to the connector and straight protected traces. JLC's capability pages publish geometry floors, not an allowed local impedance-step length or exact transition model. | **No.** None gives a maximum 0.150/0.250-mm neck length, a flare/taper prescription, return-loss bound, or an eye result for this stack and package launches. |

The JLC records establish that the proposed widths are not below the published
etch floor.  They cannot be used to interpolate the impedance of a 0.150-mm
trace, the 0.150-to-0.250 or 0.250-to-0.410 transitions, or the combined XU
pad/trace/ESD-pad discontinuities.  Nor does a successful native DRC alter
that limitation: DRC proves the encoded geometric rules, not impedance.

## Length and discontinuity conditions

The only defensible numerical statements are measurements of the scratch
subject, not acceptance criteria:

| Item | Measured/checked-in fact | What it does **not** justify |
|---|---:|---|
| Narrow launch widths | six F.Cu tracks, 0.150 or 0.250 mm | continuing either width outside its exact local purpose |
| Narrow-envelope x extent | 0.525 mm per line in the isolated U_XU diagnostic | a maximum permitted neck length |
| Nominal full-pair geometry | 0.410-mm width / 0.150-mm gap; 89.611 ohm in the checked-in JLC solve | impedance of the narrow sections or their steps |
| Pair constraints | F.Cu only, no vias, 1.0-mm path-skew source budget | a waiver of the full endpoint-path/skew or continuous-In1-return obligation |

Consequently, do not apply a length-ratio heuristic, a fraction-of-rise-time
heuristic, or a generic "short enough" assertion here.  Public primary
evidence in scope does not supply the required electrical inputs or a
manufacturer-approved threshold.  The 0.525-mm envelope is useful only as a
fail-closed bounding box for a future qualification test.

## Required evidence before a bounded exception can be proposed

A future source change may propose an **exact-net, exact-pad, exact-layer,
exact-segment** exception only after all of the following are recorded:

1. A field-solver or 3-D EM model that includes the selected JLC stack,
   soldermask, XU pad/land, all six narrow segments, both width transitions,
   the ESD land, and the In1 return geometry. It must state differential
   impedance/reflection results and the modelled 0.525-mm-or-less extent.
2. A board-specific drawing that makes each exception segment finite: its
   net, endpoints, F.Cu-only location, width, length, adjacent gap, and a
   required transition shape. It must prohibit vias and all use outside the
   named six segments; the ordinary 0.410/0.150 `USB_HS` rule must remain in
   force everywhere else.
3. Fabrication-order confirmation of JLC04161H-7628G (or a newly solved and
   reviewed replacement), 1-oz outer copper, soldermask and 90-ohm controlled
   impedance. Any CAM width adjustment, stack substitution, mask change, or
   change to a narrow segment invalidates the model and exception.
4. First-article validation: coupon/TDR for the nominal pair and a USB 2.0
   high-speed eye test of the complete connector-to-XU path. This follows the
   already-checked-in `rf.yaml` first-article obligations; it is not replaced
   by the local model.

Until then, fail closed: retain the six `track_width` errors under the
canonical source rule, do not promote the scratch DRU or its copper, and do
not claim the U_XU-to-ESD path is impedance-qualified.  The viable engineering
directions are a qualified, explicitly bounded transition design or a
placement/package change that permits the nominal 0.410-mm launch; this record
does not choose between them.

## Primary public sources

* JLCPCB, [PCB Manufacturing & Assembly Capabilities](https://jlcpcb.com/capabilities/Capab), accessed 2026-09-24: multilayer 0.5/1-oz trace/space, outer copper and PCBA constraints.
* JLCPCB, [Copper Weight (Thickness) Guide](https://jlcpcb.com/help/article/jlcpcb-copper-weight), accessed 2026-09-24: >=4-layer 0.5/1-oz 0.09-mm trace/space entry.
* JLCPCB, [PCB Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities), accessed 2026-09-24: Standard-PCBA 0.35-mm minimum IC pin spacing.
* XMOS, [XU316 Product Series Datasheet](https://www.xmos.com/documentation/XM-015129-PC/pdf/XU316-1024.pdf), accessed 2026-09-24: package and USB 90-ohm/matched-routing requirements.
* Texas Instruments, [TPD2EUSB30A Datasheet (SLVSAC2)](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf), accessed 2026-09-24: DRT package and connector-adjacent/straight protected-trace layout guidance.
