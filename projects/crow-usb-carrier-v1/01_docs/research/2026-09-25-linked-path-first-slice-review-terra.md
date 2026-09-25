# Linked-path first-slice review

Scope: independent research review of the proposed `linked_paths` grammar and
TI USB probes. No checker, canonical Crow source, board, route, connector
status, or P1 result is changed here.

## Disposition

The proposed first vertical slice can be safe only as an opt-in result that is
always `INCOMPLETE`. It must not weaken the existing USB allocation's complete
coverage denominator. The current checker has no `linked_path` implementation;
this review is against the proposal in
`01_docs/research/2026-09-25-linked-multihop-corridor-contract-proposal-sol.md`.

The exact TI board is SHA
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
The native locations establish the intended first stage but do not qualify it:
J_USB data pads are y=26.1..27.25, U_USB_ESD pads y=36.275..36.575, and
U_XU.60/.59 pads y=95.275..95.925. The existing edge trunk
`[229,28,231,29]` cannot contact the XU face at y=84. The direct second
rectangle also enters `usb_vbus_sense`; the recorded ordinary checker result
correctly rejects same-net duplicate reservation credit.

## Required fail-closed checks

1. **Exact interface terminal denominator.** For each linked net, derive the
   unique terminal set from `modular_plan.json#/interfaces`, not only from
   `stage.affected`. For USB_DP it is J_USB.12, J_USB.4, U_USB_ESD.1 and
   U_XU.60; for USB_DN it is J_USB.13, J_USB.5, U_USB_ESD.2 and U_XU.59.
   Intermediate ESD pads may occur in both stages only as declared joins and
   must not increase terminal count. Reject any missing, extra, misowned,
   wrong-net, wrong-alias, or duplicated terminal.
2. **No coverage escape.** The linked path may substitute only for the two
   USB data net reservations. It must leave VBUS_USB and VBUS_PRESENT_N in
   the `usb_device_pair` denominator with their current unresolved witnesses
   and demands. A path that reduces allocation coverage to USB_DP/USB_DN, or
   permits another top-level same-net reservation, is a bypass.
3. **Stage graph and capacity.** Require one ordered owner sequence, exactly
   one join per intermediate ESD pad/net, no cycles/forks/parallel stage, and
   no capacity aggregation. A virtual stage/join must reject every geometry,
   segment, slot, or capacity field. Any virtual stage forces path and
   allocation `INCOMPLETE`; `p1_accepted` remains false.
4. **Physical first-stage proof.** Reuse integration-corridor checks for
   outline, positive source faces, foreign-region and native body/courtyard/
   pad/copper/rule-area clearance, exact fixed accesses for all four Type-C
   pads, native aliases (A6/B6, A7/B7), and fixed-connector pose/edge checks.
   The known J_USB edge/P-OUT mechanical question remains open and must not
   be masked by linked-path success.
5. **Return obligations per stage.** Require exact P2 signal access and one
   GND/In1.Cu continuous-filled-reference obligation for each stage and join.
   These are obligations only: they do not prove fill continuity, via return,
   pair impedance, skew, SI, ESD system performance, connector FULL, or
   routing.

## ADC shared-port limitation

The accepted research-only ADC shared-port run is a local screen, not a
complete two-sided interface proof. Its seven affected records cover only
one ADC-side member per net: U_ADC_A.22/.23/.21/.17/.18,
R_ADC_READY_PD.1 and Q_ADC_DIG_RST.1. The authoritative seven interface rows
also contain U_ADC_B terminals and additional ADC-side terminals, plus the
following audio-clock/TDM endpoints: R_BCLK.2, R_FSYNC.2,
R_ADC_DATA_PD.1 and U_TDM_XLATE.10, R_ADC_I2C_SCL_B_PU.1 and
U_ADC_I2C_XLATE.8, R_ADC_I2C_SDA_B_PU.1 and U_ADC_I2C_XLATE.1,
U_ADC_I2C_XLATE.6, and U_ADC_CLOCK_OK.1. The port model therefore cannot be
promoted as an authoritative endpoint-complete allocation proof.

## Priority regression order

1. Full USB two-net terminal-denominator positive case and one missing/one
   extra terminal negative case.
2. VBUS coverage preservation and same-net top-level duplicate-credit
   rejection.
3. ESD join cardinality, owner ordering, fork/cycle, and virtual-geometry
   negatives.
4. Physical stage obstruction, fixed Type-C access, and per-stage
   return-obligation negatives.
5. Legacy integration/shared-port byte-for-byte verdict tests, then an exact
   TI probe that remains `INCOMPLETE` with every existing USB and connector
   blocker visible.
