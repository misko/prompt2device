subject: crow-mic-pod-v3 exact routed-board pin, polarity, BOM and CPL review
date: 2026-09-03
reviewer: Codex independent exact-artifact physical-pin reviewer
independence: independent-from-design-author; prior verdicts were not used as evidence
context-given: exact board, schematic/netlist, Circuit JSON, part dossiers, manufacturer documents, assembly contract, BOM, CPL and JLC rotation authority
review_stage: exact-final
review_kind: pin
source_commit: 08b79dbce2857341632c5224263db60adb4274e5
board_sha256: a932200e0976418383fae0c131dfe2a5768c00ef261b611762ccd3507f05ca8f
schematic_sha256: 390fa3531348ac2d4f84097743ba0a6b84050dbbe33f059948dab6fe7d5b05d0
circuit_json_sha256: a073f897ff4fa968da80682bfa54afcdd3bb3b03f80512a78930d12fa75e39b0
exact_netlist_sha256: 6cc0d6aec6fcaebba75cbf6a1e0dcc399251679ba084ed47d0a018046e775f80
netlist_sha256: 1162400995335356e0d940bbd0446ae62afc26bc09223c7c4621923a14b5006e
parts_sha256: a1c05519247eb085b7db7a90a49450bff774de3eccf83042aba64bc31689e860
design_rules_sha256: 0cbb7cab0be102a78062338cd69688b8d7de20728e9e3e40cd9907fa374ecf84
assembly_contract_sha256: d82f18f953a8a3c2983ab67c1dc3916939a4ed86bf5381a99589c42bcea21b8a
bom_sha256: 905e78de505fa93aebf2c092371a62bedeb59b8cab9adc484108397f8089e49c
cpl_sha256: c310bc5e94e5689507a29849372d7103426253ad8b532c1729ace9c59eb3199e
rotation_authority_sha256: 43abdfd55864e664fb04b5d503ec3e2fde23219d26fffec69938f8bc1e5cbe5d
rotation_human_gate_sha256: d532d9e2cdc20072b18df376e60f4fd7d8bc944be47d47c7db15480144c709e1
bom_echo_gate_sha256: 9f5c616bc2f89777df818b51ffb738881ba41cb355a8632c6331e7824b2fd2ac
drc_gate_sha256: 52666334dc34f19355f0167dcea12fdf76e7da208ea153f9b49efd2cf9220d19
route_acceptance_receipt_sha256: c590e736ae947e60ef0f8fc0858f4c563bd2c73cc87cddf118bb9016f0d0c19d
prelayout_inputs_sha256: a662d56e1e32d38b22960cb37facfa29dd2fda9a3374556b98c7d4ed7b681aaa
prelayout_checkpoint_sha256: 9016b9f58a7ba8bacb16237e8d6ebdb38e3feed12b3b6ec27cd2e7e9831c8a08
design_verdict: SOUND
order_verdict: BLOCKED-SOURCING/DO-NOT-ORDER
p0_findings: 0
p1_findings: 0
p2_findings: 0

# Exact routed-board pin, polarity, BOM and CPL review

## Verdict and boundary

**SOUND / BLOCKED-SOURCING / DO-NOT-ORDER.** P0/P1/P2 findings are
**0/0/0** within the exact pin, polarity, footprint, population, BOM and CPL
lens. I reopened the hash-bound manufacturer documents and independently
joined the exact routed board to the schematic netlist, Circuit JSON, part
dossiers, assembly declaration and the fresh fabrication BOM/CPL. No pin
swap, mirror, package-winding error, polarity error, population omission,
catalog-code substitution, BOM merge, CPL datum error or locally decidable
rotation error remains.

This verdict is not an order authorization. No logged-in JLC allocation,
resolved BOM echo or placement preview has been supplied. It makes no claim
about physical assembly, connector continuity, microphone wiring, acoustic
polarity or first-article performance.

This review intentionally does not bind a layout-seal or agent-handoff hash.
Final reviews are themselves layout-seal source inputs, so the final seal and
handoff must be generated only after this review is committed. The exact DRC
gate and independently verified route-acceptance receipt used by this review
are bound above.

## Exact artifact and population joins

- The board, Circuit JSON, KiCad schematic, manifest and exported netlist
  agree on all 40 electrical references. Board-to-netlist parity covers 19
  nets, 93 connected nodes and four intentional no-connects with zero
  discrepancy. The exact hash-bound native KiCad DRC evidence reports zero
  violations, zero unconnected items and zero schematic-parity findings; the
  route-acceptance verifier reopens that evidence and returns PASS.
- The exact board contains those 40 electrical references plus four mounting
  holes. The declared non-assembly set is exactly `J1`, `MK1` and `TP1`-
  `TP7`; none appears in the BOM or CPL. The remaining 31 references appear
  exactly once in the CPL and exactly once after expanding the BOM groups.
  The four mounting holes are the only additional population exemptions.
- The 31 fitted references group into exactly 22 BOM rows. All 22 groups
  reproduce the source comment/value, footprint, manufacturer part number and
  LCSC code. The independent source gate finds every BOM LCSC equal to its
  per-reference Circuit JSON value; all 16 R/C groups are catalog-value
  graded. The legibility gate independently resolves 22/22 coded rows to the
  retained part authority.
- All 31 CPL rows match the board's package, board value, top-side population
  and pad-centre-bounding-box datum. The worst coordinate error is 0.00000 mm.
  The BOM, CPL and assembly population sets are therefore identical where
  they must be and disjoint from the nine declared manual/bare-pad references.
- Exact-board A-ROT resolves all 31 CPL rotations from a measured per-LCSC
  row or measured 180-degree footprint symmetry. The source rotation table
  passes 149/149 authority rows. No unsourced-rotation escape artifact is
  present.

## Manufacturer pin and polarity reconciliation

| reference | exact independent result | result |
|---|---|---|
| J1 | Molex drawing `436501000` rev D8 gives the component-side circuit order and peg geometry. A legal 180-degree rotation, not a reflection, aligns circuit 1 and the body/peg side to the project footprint. Board pads are `1=12V_POD`, `2=GND`, `3=AUDIO_P`, `4=AUDIO_N`. J1 is intentionally absent from BOM/CPL and is hand fitted. | PASS |
| U1 | TI SBOS855E Figure 5-5 confirms the top-view CCW SOIC-14 winding. Pads 1/2/3 form the VREF follower; 4 is `5V_QUIET`; 5/6/7 are the preamplifier; 8/9/10 are the complementary output section; 11 is GND; and 12/13/14 close the spare follower. Board rotation 0 degrees plus the measured C2878631 offset emits CPL 270 degrees. | PASS, preview held |
| U2 | TI SBVS121E confirms DGN top-view pins `1 OUT`, `2 FB`, `3 NC`, `4 GND`, `5 EN`, `6 NR/SS`, `7 DNC`, `8 IN`; project pad 9 is the grounded PowerPAD. Pins 3 and 7 are open. Board rotation 90 degrees plus the measured C16430 offset emits CPL 0 degrees. | PASS, preview held |
| U3 | TI SLLSEG9C confirms DRL pins `1/2 NC`, `3 IO1`, `4 GND`, `5 IO2`. The board realizes open/open/`AUDIO_P`/GND/`AUDIO_N`. Independent pad-number and numbering-free pad-cloud channels both select the C1972959 offset 0; CPL is 0 degrees. | PASS |
| D1 | The exact JKSEMI C2972759 SMA rectifier is board pad 1/cathode on `VIN_PROTECTED` and pad 2/anode on `12V_FUSED`, so forward current enters the protected rail. Board and CPL rotations are 0 degrees. Its two identical pads provide no numbering-free polarity channel. | PASS, preview held |
| D2 | Littelfuse's SMBJ15A drawing explicitly marks the unidirectional cathode band. Board pad 1/cathode is `VIN_PROTECTED` and pad 2/anode is GND. Board rotation -90 degrees becomes CPL 270 degrees; the independent JLC cathode-shape channel agrees with the pad-number result. | PASS |
| MK1 | The PUI AOM-5024L-HD-R drawing marks the positive terminal and its 2.2-kohm characterized-load circuit. Project pad 1 is the positive `MIC_RAW` wire landing and pad 2 is the negative/GND landing. The manufacturer drawing does not dimension terminal pitch, so this remains an off-board hand-wired capsule, absent from BOM/CPL. | PASS, manual assembly held |

All 25 R/C references retain their exact source values, manufacturer part
numbers, packages, two-pad identities and schematic nets. They are fixed
resistors or ceramic capacitors and are electrically non-polar. F1 is also
non-polar. Their otherwise immaterial body rotations are accepted only after
exact-board symmetry measurement, not from package-name guesses.

## Independent replay

- Fresh pin-audit generation produced seven exact critical-part dossiers for
  J1, U1, U2, U3, D1, D2 and MK1 without a board-pad/part-pin join gap.
- P-PINMAP passes all 32 declared physical identities on the four multi-pin
  parts. The project spoke checker independently reproduces J1's exact MPN,
  footprint and four-pad map on both board and schematic.
- S-COUNT passes all four artifact pairs over 40 references. Schematic/
  routed-board parity passes 19/19 nets, 93/93 connected nodes and four/four
  intentional no-connects.
- A-POP/A-POS passes over the exact 44-footprint board, 31-placement CPL and
  22-row BOM: 13 unpopulated footprints are exactly the nine declarations and
  four allowed mounting-hole exemptions; all 31 placements are top-side and
  their worst datum error is 0.00000 mm.
- The independent fabrication join passes 40/40 board/source/selection
  identities, 31/31 placed BOM/CPL references, 22/22 exact BOM groups and
  31/31 CPL datums.

## Mandatory external holds

The exact `rotation_human_gate.txt` names three single-channel placements.
Before payment, the logged-in JLC order preview must visibly confirm:

- U1/C2878631: pin 1 OUTA, pin 7 OUTB, pin 8 OUTC and pin 14 OUTD at CPL
  270 degrees;
- U2/C16430: pin 1 OUT, pin 8 IN and the PowerPAD/GND orientation at CPL
  0 degrees; and
- D1/C2972759: the physical cathode band on board pad 1 / `VIN_PROTECTED`,
  with the anode on pad 2 / `12V_FUSED`, at CPL 0 degrees.

The logged-in BOM interface must also echo every one of the 22 exact codes
without substitution. Public-catalog availability is not PCBA allocation and
is not credited here. J1 mate continuity, MK1 lead/acoustic polarity, exact
post-assembly diode/IC marks and the full electrical/acoustic first-article
plan remain required.

Accordingly, the design is locally **SOUND**, while the order remains
**BLOCKED-SOURCING/DO-NOT-ORDER**. This review does not infer a JLC preview,
authenticated allocation, physical assembly or successful first article.
