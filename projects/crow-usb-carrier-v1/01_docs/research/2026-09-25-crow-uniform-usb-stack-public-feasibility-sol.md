# Public feasibility screen: uniform narrow Crow USB pair

**Disposition (2026-09-25): promising geometry, unproved impedance and cost.**
A uniform narrow pair on a thinner L1–L2 dielectric is a cleaner SI hypothesis
than Crow's unsupported 0.150/0.250/0.410-mm stepped launch, but no official
90-ohm solve was obtained for either candidate stack. Keep the existing
4-layer JLC04161H-7628G rule and board unchanged. This is a public-only
research comparison, with no stock check or route/source/assembly decision.

| Candidate | Official/public stack fact | Geometry and process disposition |
|---|---|---|
| Current 4L `JLC04161H-7628G` | [Retained JLC response and solve](2026-09-22-usb-impedance-evidence.md): L1–L2 dielectric 0.5124 mm; 0.410/0.150-mm masked pair returned 89.611 Ω. | Full-width copper cannot depart Crow's 0.4-mm-pitch XU pads under the present clearance rule; six-track narrow scratch neck violates source width and has no SI model. |
| Alternative 4L `JLC04161H-3313A` | JLC's [public 4L template response retained here](2026-09-22-usb-impedance-evidence.md) and re-queried 2026-09-25: two 3313 dielectrics 0.107+0.0994 = **0.2064 mm** from L1 to L2, 1-oz outer/0.5-oz inner; vendor labels **special**, finished **1.58 mm ±10%**. | May allow a uniform pair at or below the pad-escape width ceiling while retaining four layers, but no solver width/gap or price is established. Special stack excludes Economic PCBA under JLC's table; Standard PCBA remains a possible review path. |
| Proposed 6L `JLC06161H-3313E` | [JLC stack table](https://jlcpcb.com/impedance) and live public template response: **0.0994 mm** 3313 from L1 to L2, 1-oz outer copper (0.035 mm base in stack table), 0.5-oz inner copper (0.0152 mm in table). Live template labels **special**, finished **1.65 mm ±10%**; inner L2–L3 and L4–L5 cores are 0.10 mm, central core 0.70 mm with 0.2104-mm 7628 on both sides. | Near XMOS's 0.10-mm example dielectric, so a uniform narrow pair is plausible. It is a six-layer redesign and a special-order assembly/cost case; no 90-ohm or fabricability-at-exact-gap result is established. |

The exact Crow XU316 pad centres are 0.400 mm apart, with 0.250-mm pad
width across the pitch. With the current 0.150-mm clearance to the neighbouring
pad, a centred uniform departing trace must be **no wider than 0.250 mm**:
`0.400 − 0.125 − W/2 ≥ 0.150`. This is a local native-geometry bound, not an
impedance result. XMOS's [TQ128 datasheet](https://www.xmos.com/documentation/XM-014532-PC/pdf/XU316-1024-TQ128.pdf)
gives a **90 Ω, W=0.12 mm, gap=0.10 mm, H=0.10 mm** four-layer *example* and
requires paired, matched USB routing with nearby continuous GND. It does not
state that 0.12/0.10 on JLC's 3313E, its 1-oz plated copper and mask, will be
90 Ω. A 0.12-mm centred trace would have 0.215-mm clearance to the next
0.25-mm pad, so it fits this one local copper screen. The pair must fan from
0.400-mm pad-centre spacing to the solved pair spacing; that finite geometry,
pad/mask/ESD discontinuity and plane return still need model and DRC review.

JLC's [rigid capabilities](https://jlcpcb.com/capabilities/Capab) list
multilayer 1-oz minimum **0.09/0.09-mm** trace/space, ±20% ordinary trace-width
tolerance, 6-layer controlled impedance at ±10%, LPI mask and a 0.09-mm
minimum clearance between mask openings and neighbouring traces. A nominal
0.10-mm gap is only 0.01 mm above the published bare-copper floor; that is
manufacturing *possibility*, not an impedance or yield allowance. The same
page says six-or-more-layer FR-4 does not support HASL, so finish/stencil
review is necessary. JLC's [calculator guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator)
specifies plated outer copper, soldermask thickness/Dk and the required
stackup, gap and target-impedance inputs; its generic mask parameters include
0.6-mil mask above copper, 1.2-mil base/between traces and Dk 3.8. The
earlier four-layer live configuration used different 1.0/0.6/1.0-mil mask
values, so neither model may be silently copied to 3313E.

**Solver check:** the public JLC template endpoint
`/api/jlcTools/impedance/selectPageImpedanceDefaultTemplate` returned the
above 4L and 6L named stacks on 2026-09-25. The public calculation endpoint
`/api/jlcTools/impedance/calc` returned HTTP 200 with `result: success` but
`body: null` for both an unchanged previously successful 4L request and a
0.12/0.10-mm, H=0.0994-mm 3313E trial. Therefore no current official
numeric solve or recommended 90-ohm width is claimed. Obtain a fresh JLC
calculator result with exact selected stack, artwork/base and plated/top
widths, actual mask, gap and target 90 Ω before choosing either source rule.
The JLC [6L web table](https://jlcpcb.com/impedance) also lists a generic
`JLC06161H-3313` with the same outer dielectric, but it was absent by that
name from this 1.6-mm/1-oz/0.5-oz live template query; it is not substituted
for the named 3313E. The selected 4L 3313A and 6L 3313E entries are both
explicitly special in the live template responses, so a quote is required.

JLC's [assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
admit 0.4-mm IC pitch on Economic and 0.35 mm on Standard, and list 6 layers
for both. Economic excludes special stackups; Standard lists all stackups.
This says the TQ128 pitch is within a published machine capability, not that
the exact pad, mask dams, ESD package and panel pass assembly review. The
expanded Crow board's 230×130 mm outline fits JLC's published 6L board-size
limit and Standard PCBA single-board limit, but the 1.65-mm ±10% stack and
six-hole hardware/connector fit must be checked against actual bodies and
mounting hardware.

**Revalidation if pursued:** freeze an official stack and mask/finish/price
quote; solve the full uniform L1 pair, then model the pad fan, ESD/connector
lands and continuous L2 return and verify skew/eye. Reassign all six copper
layers, recheck via spans/annulars, GND and power-plane continuity, analog
isolation, currents/thermal copper, regulator loops, and decoupling returns.
Regenerate KiCad stack-dependent rules and all TMUX POFV/protection-area
checks, then repeat pin/net parity, full native DRC and P1/P2/corridor proof.
Recheck connector service envelope, six-hole mechanical fit, stencil/mask,
finish and panel/assembly pathway. The 6L option is physically closer to
XMOS's example; the 4L special 3313A is less disruptive **if** a vendor solve
lands at W≤0.250 mm with a manufacturable gap and the required return. Neither
has passed those conditions, and neither carries release or route credit.

## Dated calculation correction — 2026-09-25

The later [public JLC fixed-geometry packet](2026-09-25-jlc-3313-uniform-usb-solve-sol/README.md)
records non-null backend outputs after this feasibility screen: 89.9172598796 Ω
for a 4L 3313A **hypothesis** at W/G=0.180/0.100 mm, and 87.4366551479 Ω
for a 6L 3313E **hypothesis** at W/G=0.120/0.100 mm. This updates the earlier
statement that no numeric calculation was obtained. It does **not** establish
an official 90-ohm width recommendation or authenticated named-stack solve:
the calculation `accessId` was reused from the prior 7628G trial, no current
frontend template-to-calculation mapping was captured, `HZ0=108.0` was
retained with unknown semantics, and the raw HTTP capture lacks a timestamp.
Both named templates are still special, and the 0.100-mm pair gap still
requires a separate source-rule and complete board/fabrication review. The
less disruptive 4L hypothesis merits verification first, without selection
or route/release credit.

### Additional public frontend finding — 2026-09-25

The [subsequent replay](2026-09-25-jlc-3313-uniform-usb-solve-sol/README.md#public-frontend-mapping-replay--2026-09-25)
captured JLC's public current template-to-numeric-argument flow and repeated
the 4L 3313A fixed-geometry output with a fresh UI-style UUID `accessId`.
It also found `HZ0=108` in the hidden picture definition and showed the
forward result unchanged when `HZ0` was set to 90. Its physical meaning
remains undocumented in the public material. The replay preserves HTTP Date
headers but is not a captured human UI session or fabrication commitment.
