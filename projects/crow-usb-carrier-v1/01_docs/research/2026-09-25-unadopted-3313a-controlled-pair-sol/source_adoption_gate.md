# 3313A source adoption gate — supplemental review, 2026-09-25

**Disposition: keep the existing four-file proposal unadopted.** The packet's
[`source_diff.patch`](source_diff.patch) and [`replay.py`](replay.py) already
form the bounded source/rule/stack trial. A second trial would duplicate the
same hypothesis. This addendum closes the input-identity omission in the
replay narrative and states the remaining source-selection gate; it changes
neither the reviewed proposal nor D15's historical `FAILED_RESEARCH` result.
It authorizes no further native Crow board generation. D15's one allowed
generation was consumed; D18's private route prerequisites remain unmet.

## Exact input identity and replay

The frozen expanded-locked board is SHA-256
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`.
Its **input** KiCad project sidecar `.kicad_pro` is
`7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094`
and rule sidecar `.kicad_dru` is
`00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a`.
Those are the bytes copied by the updated `replay.py`, which asserts the board,
four source files and both sidecars before creating any scratch copy. The
`--verify-inputs-only` mode performs just that check. The D15 derivative's **output**
sidecars, `.kicad_pro` `2d0bf4d9c14fedee82e1ba22f06d05a4ba97e7b7fe39a66e086ec1c48b408c1a`
and `.kicad_dru` `ddb17c62f3beb2e0a03cf18acbb1148c36f60d516937c96660cfb44d146520a3`,
are different artifacts and must not substitute for the frozen inputs.

The proposal patch is
`707d8b94075190bf601aba410738b5fbefbd7036ca539ff967c9ae1fd90f7d82`;
the replay program is
`e1473de36945a3852934a163817ae0eac7e72892f279c2ca118b081321b9a2d1`.
On this worktree, `/usr/bin/python3 replay.py` returned `PASS` with ten KiCad
controls and generated exact-pair rule SHA-256
`e37b434e38b8683b9b3f8e21e92f82931647bfc388aae1861d1849cda046ebf5`.
Both deliberately substituted D15 sidecars were individually rejected by
`--verify-inputs-only` with `base hash drift` at their exact paths. The older
capture JSON remains historical and names the prior replay script hash;
fresh coupon board and DRC byte hashes vary across runs, so compare the
semantic assertions and pinned inputs/rule hash.
The full generated sidecars accepted F.Cu USB_DP/USB_DN at 0.100 mm and
rejected 0.099 mm; they rejected F.Cu USB_DP/FOREIGN at 0.140 mm and
USB_DP/USB_DN at 0.140 mm on In1.Cu, In2.Cu and B.Cu against the 0.150-mm
floor. The generator also rejected a widened selector, second pair and B.Cu
scope. These are synthetic rule controls, not a Crow route.

The frozen board's endpoint check in the
[`pair-footprint` research capture](../2026-09-25-early-pair-preflight/replay.json)
has SHA-256 `fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`
as its board input and checks eight terminals. The proposal's read-only
endpoint screen reported necessary centered 0.180-mm fit at those eight pads;
it does not establish all four leaf merges, ESD tap, XU launch fan, mask or
return path. D15's separately generated, unrouted native board had exact
pose/object parity, 799 mapped pin identities, zero native DRC violations,
499 opens and zero *performed* schematic-parity issues, but its V-PROCESS
failure retains `FAILED_RESEARCH`. That evidence cannot be reassigned to a
future source or route candidate. KiCad counted 1,872 raw pads on non-hole
footprints in both frozen and D15 boards; D15's 1,810 "electrical pads"
phrase used a different denominator and is not a raw pad-parity target.

## Stack calculation limit and smallest next gate

The public JLC template names special `JLC04161H-3313A`, finished thickness
1.58 mm ±10%, L1–L2 and L3–L4 3313 composite 0.2064 mm/Er 4.1, and
1.065-mm core/Er 4.38. The retained public fixed-geometry calculation is
89.9172598796 Ω at 0.180/0.100 mm; the
[`frontend binding capture`](../2026-09-25-jlc-3313-uniform-usb-solve-sol/frontend_binding_capture.json)
is SHA-256 `71ec96168517575b0896011f63d52ec5fcb66c67641a4d85dab12483c2d182b3`.
It is a template-derived numeric research output, not an authenticated
production impedance. A current JLC calculator-guide description of mask
and top-width reduction appears to differ from the retained public live
configuration (`1.0/0.6/1.0` mil mask and `0.5` mil reduction); the guide
figures reported for review are `1.2/0.6/1.2` and `0.7` mil. This packet
does not resolve which set a production order would use. The source-adoption
decision therefore needs a current, correctly bound JLC calculation or
written stack/geometry confirmation that reconciles those inputs, followed
by exact-order and coupon/TDR review. No 90-Ω production guarantee follows
from the retained number.

The smallest additional engineering artifact is a hash-bound sensitivity
receipt for **both** mask/reduction input sets against the named template,
with the resulting artwork/finished-width interpretation and an explicit
source-selection decision. Before any Crow native candidate is promoted,
independent review must also bind the exact sidecar input hashes above, the
full connector–ESD–XU endpoint and return envelope, and performed native
parity. D18 P1/P2, connector FULL, route, fabrication, assembly, release and
order credit remain false. This addendum makes no stack-order, route or
source-adoption claim.
The TI ESD remains prototype-only, with no ESD qualification credit.
