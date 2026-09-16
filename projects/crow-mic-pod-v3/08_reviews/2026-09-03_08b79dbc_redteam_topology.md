subject: crow-mic-pod-v3 exact routed board at 08b79dbce2857341632c5224263db60adb4274e5
date: 2026-09-03
review_stage: exact-final
review_kind: redteam-topology
reviewer: redteam-agent (Codex, topology/protection/ratings lens)
independence: independent-from-design-author; prior verdicts were not used as evidence
context-given: full-tree; exact immutable source checkpoint, routed board, schematic/netlist, part dossiers, rules, BOM and CPL independently reopened
source_commit: 08b79dbce2857341632c5224263db60adb4274e5
board_sha256: a932200e0976418383fae0c131dfe2a5768c00ef261b611762ccd3507f05ca8f
circuit_json_sha256: a073f897ff4fa968da80682bfa54afcdd3bb3b03f80512a78930d12fa75e39b0
schematic_pdf_sha256: 0fc7162ab6cfc2a390cfe621f2d839c7d0812adf9b4762da576103e537a805ac
kicad_schematic_sha256: 390fa3531348ac2d4f84097743ba0a6b84050dbbe33f059948dab6fe7d5b05d0
exact_netlist_sha256: 6cc0d6aec6fcaebba75cbf6a1e0dcc399251679ba084ed47d0a018046e775f80
netlist_sha256: 1162400995335356e0d940bbd0446ae62afc26bc09223c7c4621923a14b5006e
parts_sha256: a1c05519247eb085b7db7a90a49450bff774de3eccf83042aba64bc31689e860
design_rules_sha256: 0cbb7cab0be102a78062338cd69688b8d7de20728e9e3e40cd9907fa374ecf84
route_yaml_sha256: bbc146dcd6b1aa64d660981ce14734d66af3921abe312e5015a7387b4f60f056
prelayout_inputs_sha256: a662d56e1e32d38b22960cb37facfa29dd2fda9a3374556b98c7d4ed7b681aaa
prelayout_checkpoint_sha256: 9016b9f58a7ba8bacb16237e8d6ebdb38e3feed12b3b6ec27cd2e7e9831c8a08
native_drc_sha256: 52666334dc34f19355f0167dcea12fdf76e7da208ea153f9b49efd2cf9220d19
route_acceptance_receipt_sha256: c590e736ae947e60ef0f8fc0858f4c563bd2c73cc87cddf118bb9016f0d0c19d
realized_route_receipt_sha256: db2a88eb683583363c2011528aeb6afe8d42389af42465a025a56ef02765a3dc
bom_sha256: 905e78de505fa93aebf2c092371a62bedeb59b8cab9adc484108397f8089e49c
cpl_sha256: c310bc5e94e5689507a29849372d7103426253ad8b532c1729ace9c59eb3199e
design_verdict: SOUND
order_verdict: BLOCKED-SOURCING
p0_findings: 0
p1_findings: 0
p2_findings: 0

# Final routed-board topology, protection and ratings red-team review

## Verdict and claim boundary

The exact routed-board design is **SOUND** in this lens. I found no unresolved
P0, P1 or P2 topology, protection, component-rating, pin-membership or
population finding. The order verdict is independently
**BLOCKED-SOURCING**, and this board remains **DO-NOT-ORDER**.

I reopened the exact source, generated circuit, native KiCad schematic and
netlist, every part dossier, the routed PCB, the exact fabrication BOM/CPL and
the governing calculations. I also replayed the specialist electrical battery,
pin/count/parity checks, realized protection-path checks and the atomic route
receipt. This is a design review, not evidence of fabricated hardware,
measured analog performance, environmental qualification or an authenticated
JLCPCB allocation.

The final layout seal and agent handoff are intentionally not bound here.
Every dated review is itself a layout-seal input, so those receipts must be
issued after all four exact-board reviews are committed. The current board,
DRC, route-acceptance and prelayout evidence above are the immutable review
subject.

## Exact topology reconciliation

- The Circuit JSON, KiCad schematic, manifest, netlist and routed board agree
  on all 40 electrical references. Exact schematic-to-board parity is 19/19
  nets, 93/93 connected nodes and four/four intentional no-connects, with zero
  discrepancy. P-PINMAP independently grades 32 physical pin identities on
  the four multi-pin parts.
- J1 is straight through: pin 1 `12V_POD`, pin 2 GND, pin 3 `AUDIO_P` and pin
  4 `AUDIO_N`. It is an analog spoke connector, not Ethernet or PoE.
- The input chain is J1.1 -> F1 -> D1 -> `VIN_PROTECTED`. D1 pad 2/anode is on
  `12V_FUSED` and pad 1/cathode is on `VIN_PROTECTED`; D2 pad 1/cathode shunts
  that protected node to its pad 2/anode on GND. The exact copper proof places
  D2 before C1, C2, U2 IN/EN and R14, so no parallel pre-clamp branch evades
  the TVS.
- U2 is reconciled as OUT/FB/NC/GND/EN/NR/DNC/IN with its exposed pad grounded.
  DNC pin 7 and NC pin 3 remain open; EN is on the protected input. The
  324 kOhm / 100 kOhm feedback divider, 10 nF feed-forward part, NR capacitor
  and both input/output capacitance banks are present on the intended pins.
- The capsule bias and AC path retain R3 = 3.9 kOhm, C7 = 100 uF and R4 =
  2.2 kOhm. U1A buffers VREF; U1B produces `PRE_OUT`; U1C produces the
  complementary `OUTP_DRV`; U1D is a private VREF follower. No op-amp outputs
  are paralleled. U3 pins 3 and 5 clamp the two cable legs, pin 4 is GND and
  its two NC pins remain open.

## Protection and component ratings

- The 13.2 V maximum normal input remains below the SMBJ15A 15 V standoff.
  Its governed 24.4 V maximum 10/1000 us clamp, including the explicit 10%
  coordination factor, gives 26.84 V. This is below U2's 35 V recommended / 36
  V absolute input bounds, both 50 V input capacitors, the 60 V PTC and the
  1000 V series diode. The admitted pulse is limited to 10 A and 244 W; the
  dossier's +70 C linear-derating check retains about 384 W capability.
- That clamp claim is component-level only. It does not claim lightning,
  building-entry protection or an unbounded cable source. The exact carrier
  and installed-source transient bound remains a mandatory physical hold.
- At the hot reverse-leakage maximum, 50 uA through R14's +1% value of
  4.747 kOhm gives 0.23735 V, retaining margin to U2's -0.3 V absolute input
  floor. Hot reverse-hookup behavior still requires first-article testing.
- The independently recomputed LDO range is 4.7926-5.2295 V, contained by the
  declared 4.79-5.23 V window. Minimum input headroom is 5.27 V against a
  0.6 V dropout bound. The conservative 20 mA / high-input dissipation is
  168 mW against the project's 300 mW thermal ceiling, and the effective C5
  floor is 3.825 uF against the 2.2 uF stability minimum.
- The modeled static load is about 15.18 mA against the 20 mA first-article
  ceiling. The 0.10 A input class is deliberately a delivery/fault allocation,
  not a prediction of normal consumption.

## Analog transfer and margins

Let `x = MIC_AC - VREF` and `k = 18/22 = 9/11`. The exact feedback networks
give `PRE_OUT = VREF - k*x` and `OUTP_DRV = VREF + k*x`; therefore
`AUDIO_P - AUDIO_N = 18/11*x`. Equal 100 ohm source resistors preserve that
unloaded differential ratio and the intended polarity.

Independent 1% gain corners predict no more than 0.952 Vrms differential at
the modeled loud-input boundary, below the 1.2 Vrms pod contract. The larger
leg remains within about 1.669-3.331 V. At the 4.79 V minimum rail this clears
the OPA1679 guaranteed loaded-output boundary by more than 0.5 V; the 2.65 V
maximum VREF retains 0.14 V to the upper common-mode boundary. These are
analytic margins, not a clipping or distortion measurement.

The 15 m cable model contributes 1.353 nF differential capacitance. With the
two 100 ohm source resistors its first-order pole is about 588 kHz, which is
compatible with the intended audio band but does not establish stability,
noise, phase or EMC performance. Exact 4 m and 15 m harness measurements remain
required.

## Exact BOM/CPL and order boundary

The exact BOM has 22 coded rows expanding to 31 machine-fitted references; the
exact CPL has the same 31 references, all top-side. BOM-to-source identity is
complete, all 16 R/C rows are value-graded, and all 22 coded rows resolve to
retained part authority. J1, MK1 and TP1-TP7 are deliberately excluded under
the assembly contract; J1 and MK1 require controlled manual assembly.

No logged-in JLCPCB BOM resolution, allocation, economics result or rendered
placement preview exists. The order response remains blank. The operator must
confirm every exact code plus U1, U2 and D1 orientation in JLC's resolved
preview, then close connector, capsule, harness, power, audio, thermal, ESD/EMC
and roof-environment first-article evidence. Until then the design verdict is
**SOUND**, while the order verdict remains **BLOCKED-SOURCING / DO-NOT-ORDER**.
