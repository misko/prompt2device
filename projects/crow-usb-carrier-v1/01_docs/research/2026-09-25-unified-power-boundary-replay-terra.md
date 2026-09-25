# Unified power-boundary replay (research only)

**Result: no P1 credit.**  The five local virtual-face substitutions can remove
five of the nine power diagnostics on the unified packet.  The remaining four
can be made to disappear with the present `shared_transition_port` grammar,
but that result is not admissible: the grammar does not preserve the power
net's complete endpoint denominator or prove a relationship between the named
pad and the empty port point.

## Inputs and replay

The replay used unified diagnostic packet commit `9f8ca953`, its exact board
`01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb`,
SHA-256 `d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fc7`,
and the packet's source/floorplan/interface hashes:

| input | SHA-256 |
| --- | --- |
| requirements | `f6f132891712bfcb1cec4d1df6714748337040ba5c42ae3fecd14fb9c35d1222` |
| floorplan | `7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0` |
| modular plan | `02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8` |

The baseline has nine power-window diagnostics: the five local candidates
`GND`, `N0V9`, `N12V_PROTECTED`, `N5V_LDO_HOLD`, and `PWR_EN`, followed by
`N1V8`, `N3V3X`, `N3V3_ADC`, and `N5V_BUCK`.

In an untracked overlay at `/tmp/crow-unified-power-overlay-terra`, I replaced
the first five legacy strips with `virtual_block_face` records and their exact
`P2_REQUIRED` pad-to-face obligations.  The local source-face/reservation
pairs were:

| net | owning face bbox (mm) | exterior reservation bbox (mm) |
| --- | --- | --- |
| GND | `[117.9,85,118.3,85.5]` | `[117.9,84,118.3,85]` |
| N0V9 | `[184.5,116.5,185,117.3]` | `[185,116.5,190,117.3]` |
| N12V_PROTECTED | `[36.3,83.5,37.4,84]` | `[36.3,84,37.4,85]` |
| N5V_LDO_HOLD | `[33.6,83.5,34.3,84]` | `[33.6,84,34.3,85]` |
| PWR_EN | `[100,85,100.5,85.4]` | `[100,84,100.5,85]` |

`GND` and `PWR_EN` cannot use the previously considered westward rectangles:
they enter `quiet_power`.  The southward one-millimetre-free-edge reservations
above are accepted by the current virtual-face clearance test.  The replay
therefore reduced the power diagnostics from 9 to 4.  It did not measure a
route, current, temperature, copper capacity, or filled return.

## Shared-port probe and deficiency

I then placed four separate 0.10 mm empty probe points across the
`adc_reference`/`digital_power` boundary at `x=145.00..145.10`, with matching
0.10 mm reservations immediately to the west.  The candidate locations were
at y=`114.40`, `114.70`, `115.00`, and `115.30` mm for `N1V8`, `N3V3X`,
`N3V3_ADC`, and `N5V_BUCK`, respectively.  Each was screened against native
footprint/pad envelopes and rule areas.  The checker reported zero remaining
power diagnostics; its output SHA-256 was
`9238cb2cd2b83eaa0d6fff869ad90eb41f83d63431c8204517142ce9e2071b45`.
The overall result remained `FAIL`, with nine unrelated timing branch
denominator errors, and `power_boundary_windows` remained `INCOMPLETE`.

That apparent success is a negative result.  The probe listed only its one
legacy witness endpoint per net, while the modular endpoint denominators are:

| net | all native source endpoints | owners |
| --- | ---: | ---: |
| N1V8 | 42 | 7 |
| N3V3X | 27 | 4 |
| N3V3_ADC | 68 | 11 |
| N5V_BUCK | 34 | 3 |

The checker validates that `affected` endpoints are valid members of a port,
then only checks that every declared `affected` endpoint is used.  It does not
require `affected` to equal the source/modular endpoint set for its net.
It also accepts a port bbox that is empty and located at the region boundary
without a pad-to-port path; that path is merely a one-pad P2 obligation.  See
`p1_corridor_capacity.py` lines 199--217, 554--593, and 1864--1868.  Thus the
probe would silently replace 171 endpoint debts with four selected debts.  It
must not be promoted.

## Fail-closed repair ledger

1. Retain the five local virtual witnesses only with their exact P2
   pad-to-face obligations and unmeasured `power_or_mechanical` reservations.
   They are source reservations, not local copper or return proof.
2. Keep the four cross-region nets out of `shared_transition_ports` until the
   schema binds each net's complete modular endpoint denominator and requires
   a P2 debt record for every terminal, separate from the small set of physical
   port-entry pads.
3. The minimal current-schema representation for those four is an
   `unresolved_multiterminal_branch`: it already requires the exact full
   native/source endpoint set, leaves geometry and capacity absent, requires
   per-terminal P2 route debt, and keeps P3 tree/filled-reference debt.  It
   does not claim a handoff window.
4. A later power-transition extension may add a shared physical port only if
   it names (a) the full per-net endpoint denominator, (b) exact entry-pad
   subset and P2 native-pad-to-port proofs, (c) each P2 local-entry debt for
   the remaining endpoints, and (d) a P2 filled-return/current/thermal proof.
   The port must remain `INCOMPLETE` until those receipts exist.

No canonical requirements, board, stock, or dispatch state was changed.
