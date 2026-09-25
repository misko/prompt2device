# Public JLC fixed-geometry calculations for 3313 stack hypotheses

**Corrected result (2026-09-25): non-null public JLC fixed-geometry numeric
outputs were recovered, but they are not authenticated named-stack solves or
vendor recommendations.** For a 4-layer `JLC04161H-3313A` *hypothesis* using
its published H1/Er, a masked **0.180-mm artwork/base width, 0.100-mm gap**
request returned **89.9172598796 Ω**, `dResultValid=1`. For a 6-layer
`JLC06161H-3313E` *hypothesis*, **0.120/0.100 mm** returned
**87.4366551479 Ω**, also valid. The request retained `HZ0=108.0` from an
earlier 4-layer trial. Its physical meaning remains undocumented, while the
later controlled 108-to-90 replay left this forward result unchanged. These
numbers cannot yet select a 90-ohm rule. No source/board edit,
stock check, login, file upload or vendor contact was performed.

The exact unauthenticated public [JLC template endpoint](https://jlcpcb.com/api/jlcTools/impedance/selectPageImpedanceDefaultTemplate)
returns `JLC04161H-3313A` as **special, 1.58 mm ±10%** with two 3313 plies
totalling **H1=0.2064 mm** (0.107+0.0994 mm, Er=4.1), 1-oz outer and 0.5-oz
inner copper. It returns `JLC06161H-3313E` as **special, 1.65 mm ±10%** with
one 3313 ply **H1=0.0994 mm**, the same outer/inner copper weights. The
[JLC published stack table](https://jlcpcb.com/impedance) corroborates the
6-layer layer sequence. The current public [coverlay](https://jlcpcb.com/api/jlcTools/impedance/impedance-config/coverlay/list)
and [plated trace-width](https://jlcpcb.com/api/jlcTools/impedance/impedance-config/copper-trace-width/list)
configuration endpoints give, for 1-oz outer/0.5-oz inner, **1.0/0.6/1.0 mil**
mask above substrate/trace/between traces, mask Er=3.8 from the
[calculator guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator),
**1.6-mil finished trace copper** and **0.5-mil top-width reduction**. Both
requests use JLC's `DiffEdgeCoupledCoatedMicrostrip1B` model,
`dCalculateMode=3` and those exact values. However, the calculator `accessId`
was reused from the earlier 4-layer 7628G request for **both** hypotheses;
the current frontend's template-to-calculation mapping was not captured.
The named template data and calculated H1/Er were separately queried and then
manually assembled into the request. The public backend returned numeric
values, but the record does **not** prove that it associated either request
with the named special template. Their selected public template record,
config response, calculator request and raw result are in [4L JSON](4l_3313a.json) and
[6L JSON](6l_3313e.json). The JSON file SHA-256 values are respectively
`33d04b7f0991b5f3db5e289f3dc9687dc552859fa2dd0661af2a937930161bbb`
and `ac581ee19489c041ac2e9fe1418870a3d9edc4a292f649fe044d84e4c734b24b`.

The initial `/api/jlcTools/impedance/calc` HTTP 200 response can say
`{"result":"success","body":null}`. This happened for the unchanged
previously successful 4-layer request and rapid trial requests; repeating an
identical request after a short interval returned a non-null numeric body.
The current frontend still calls `/calc` with `accessId`, model mark,
`paramMd5`, argument object and UUID. The exact reason for the null body is
not exposed by the public API, so it should be treated as pending/indeterminate,
not as a zero or a failed solve. For the retained successful calls,
`paramMd5` was empty on input and JLC returned a populated hash in the body;
no stale prior-request hash was used as a result. This replay establishes a
reproducible **request shape and numeric output**, without claiming why the
first response was null. The raw capture also lacks an HTTP timestamp, so its
date is the research run date, not a server-authenticated transaction time.

The 4L *hypothesis* is the least disruptive geometry to investigate:
0.180-mm width leaves
`0.400−0.125−0.090=0.185 mm` from a centred trace to Crow's adjacent
0.250-mm XU pad, above its current 0.150-mm clearance. That is a local
geometric inference, not a native full-route DRC. The 0.100-mm *pair* gap is
below Crow's current 0.150-mm USB source clearance, so adopting it would
require a separately reviewed exact-net, pair-only rule and a complete native
route/return/SI revalidation. The gap is above JLC's published 0.09-mm
multilayer 1-oz copper floor by only 0.01 mm; [JLC capabilities](https://jlcpcb.com/capabilities/Capab)
do not turn that small margin into a yield guarantee. Since both stacks are
special, JLC's [PCBA table](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
excludes Economic assembly but allows special stacks in Standard, subject to
quote and exact-pad/stencil/finish review. The 6L alternative adds full power,
return, TMUX, via, assembly and cost revalidation without a demonstrated
advantage over the 4L cross-section for this USB escape. A correctly bound
frontend/vendor 90-ohm calculation and exact-board electrical/assembly
validation remain prerequisites to a source-rule proposal. Neither stack is
selected, and the unsupported six-track neck remains unqualified.

## Public frontend mapping replay — 2026-09-25

The new [replay verifier](replay_frontend_binding.py) fetches the unauthenticated
public calculator page, its current script, selected 4L template, outer-layer
picture definition, copper/mask configuration, and two numerical calculation
responses. It writes the exact request/response and HTTP `Date` headers to
[the capture](frontend_binding_capture.json). The captured frontend script
SHA-256 is `dd57ca32426d511d6fe392ae66c205c872601a9837a56763b78c6d334ad7aec5`.
The replay reproduced **89.9172598796 Ω** at 0.180/0.100 mm using a fresh
UUID `accessId`; this demonstrates that the old 7628G `accessId` was an
impedance-list instance key, not a stack identifier. The frontend constructs
its list from `templateList[n].basicDataList`, computes L1–L2 height from
that selected template index, and passes the resulting numeric argument
object to `/calc`. The script checks those frontend operations and the
selected 3313A template values before computing. This is a reproducible
public **template-derived request**, though it is not a captured human UI
click or a vendor production impedance commitment.

The public picture definition supplies `HZ0=108.0` as a **hidden** parameter
(`displayStatus=4`). No official public text found defines its physical
meaning. In this controlled `dCalculateMode=3` forward calculation,
changing only `HZ0` to 90.0 returned the *same* 89.9172598796 Ω; the earlier
120.0 trial also did. Thus its semantics remain unknown, but the fixed-width
output is empirically insensitive over those tested values. The capture's
HTTP dates now establish when these endpoint responses were received. These
findings narrow the prior provenance caveat; they do not select 3313A or
qualify a board route.
