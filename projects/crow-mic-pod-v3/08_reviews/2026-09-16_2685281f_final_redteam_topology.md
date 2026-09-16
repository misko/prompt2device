subject: crow-mic-pod-v3 v0.2.0-2026-09-15
date: 2026-09-16
reviewer: redteam-agent (electrical topology, protection, and ratings lens)
context-given: release-archive-only plus frozen primary source
source_commit: 3fe3beb3fb221d73ea825644cdd5f2f5506dc6a2
board_sha256: 2685281fdb8dac636e16334c2d4eca679300bfa5322a368ac2685b59f48e3dd1
design_verdict: SOUND
order_verdict: DO-NOT-ORDER

# Independent final topology red-team review

I find no release-blocking electrical design defect in the frozen candidate. I used the fresh pre-route topology review as inherited evidence for the unchanged netlist and repeated the final integration judgment against the routed native board, primary part records, protection/power contracts, schematic PDF, DRC receipts, and realized-route receipt.

The electrical graph remains internally complete: 99/99 connected endpoints agree between source and native netlist, with only the four declared U2/U3 NC/DNC pins open. All 39 executable electrical invariants pass. Both native and independently opened standalone archive DRC reports contain zero violations, zero unconnected items, and zero schematic-parity issues. This is stronger evidence than the candidate's 158 ERC warnings, which are classified rather than silently treated as errors.

The input sequence is J1 -> F1 -> D1 -> `VIN_PROTECTED`, with D2 clamping the protected node and R14 bounding hot reverse leakage. The selected envelopes are coherent for the deliberately limited first article: J1 is rated 1.5 A/150 VAC by the exact manufacturer record; F1 is 60 V with a 10 A maximum fault-current envelope; D1 is a 1 A/1000 V S1M; D2 is a 15 V standoff SMBJ15A with 24.4 V clamp at the cited pulse point; U2 is exposed to the bounded 24.4 V transient versus 35 V recommended/36 V absolute input; and C1/C2 are 50 V. The route checker proves the D1-to-D2 protected prefix is 9.5 mm on F.Cu and that D2 precedes every U2/input-capacitor/R14 branch. The packet correctly limits this to a component 10/1000 us claim and retains carrier-source, waveform, hot, surge, and system EMC qualification.

The TPS7A4901 rail is also plausible within its declared boundary. At 10.5 V minimum input and 5.23 V maximum output it retains 5.27 V headroom against the recorded 0.6 V dropout maximum. At 13.2 V and 4.79 V/20 mA, the declared dissipation is 168 mW, 56% of the conservative 300 mW project limit. The feedback-corner calculation includes the +/-2.5% reference, 1% resistors, and -100..0 nA bias range. C5's conservative effective-capacitance floor remains above the 2.2 uF stability minimum, but physical capacitance and thermal behavior are correctly first-article measurements rather than release facts.

Policy S5 is accepted within this review's arithmetic lens: the stated regulator headroom/dissipation, S1M leakage times R14 (50 uA x 4.747 kohm = 0.23735 V), and SMBJ +70 C pulse derating arguments are dimensionally and numerically consistent with the pinned primary records. The analog chain remains a filtered electret bias, AC-coupled preamp, VREF-centered OPA1679 stages, 100 ohm output legs, and connector-first TPD2E2U06 clamp. U3 reaches both J1 signal contacts before probe/output branches; all four branch-after-clamp assertions pass. The 18/11 V/V differential gain, common mode, capacitive-cable stability, CMRR, noise, clipping, and acoustic polarity remain measurements, as they should.

Policy M1/M6 is accepted for this lens. Independent current pre-route judgments exist and are bound by normalized source identities; final routing was checked separately here. Exact manufacturer PDFs/records back the pin and rating claims for the primary active/protection/connector parts, and the 22/22 BOM cross-check is sourced rather than inferred from catalog text. The one known D1 rationale that still says 1N4007 is documentation debt only: the actual part, pin assertions, BOM, and primary record are S1M.

The blank authenticated PCBA receipt, cable/source transient proof, assembly decisions, and all physical tests prevent an order authorization. They do not invalidate the nominal engineering design. FIRST-ARTICLE-ONLY and DO-NOT-ORDER remain mandatory.
