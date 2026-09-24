# Independent topology review handback — Crow 569

review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
circuit_json_sha256: 1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448
netlist_sha256: 7ab8c90f46ff4f25a9af50f43659a6b304e3c15932875519fa916fd018b1d8cc
parts_sha256: 833913d1c3d68cec43ab53f34e63b48cbf0e38bd3ec5a5115abfbaa5e23c2a0e
design_rules_sha256: 8211187b0a0bb0ab38799ade9459944f0226cdf0180a75bcfdb94ca385a1a0c1
helper_path: /tmp/crow-569-schematic-review-packet-20260924-terra-r1/review/pre_route_review_check.py
helper_sha256: b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e
packet_manifest_sha256: 4f0ab185237ba22b0b01de0b98241db332d0aad456cb1407d91f932c97cce991

This is an independent, noncanonical handback. It is not a canonical-witness
installation, acceptance, release authorization, placement/routing approval,
or order authorization.

## Artifact binding and coverage

I reviewed only the frozen packet at
`/tmp/crow-569-schematic-review-packet-20260924-terra-r1`. `sha256sum -c`
passes for the declared packet manifest itself. Its inventory manifest has the
expected self-reference limitation: checking `packet-sha256sums.txt` against
the list that contains its own digest changes that list's digest, while the
separately bound `packet-manifest.sha256` validates it. The helper's complete
112-dossier `part.yaml` digest, normalized netlist digest, semantic-rules
digest, and raw Circuit JSON digest above were recomputed locally.

Coverage: complete 569-component / 1,790-pin / 1,641 pin-net-edge frozen
Circuit JSON and its KiCad netlist were reviewed against the declared power,
protection, integration, electrical-invariant, assembly, connector, RF and
requirements rules; all selected part dossiers/values/footprints and the
complete old-to-new component/pin/net delta were considered. This review also
checked the source-side power and protection ownership, normal and conditional
external-source boundaries, and the exact 569 checkpoint products. I found no
electrical-topology defect in the reviewed frozen artifact.

The helper gate presently reports the prior canonical topology/render witnesses
stale for the new netlist/rules/PDF (five stale-field findings). That is the
expected negative control; this noncanonical report cannot satisfy or replace
the canonical two-witness gate.

## Exact 569 delta and supervisor review

The machine-readable semantic delta is exactly one added component,
`C_ADC_3V3X_OK_VDD`; no components changed or were removed, and no existing
pins or pin-net edges changed. Its only two added edges are:

| Item | Endpoint 1 | Endpoint 2 | Result |
| --- | --- | --- | --- |
| `C_ADC_3V3X_OK_VDD` | pin 1 → `N3V3_ADC` | pin 2 → `GND` | PASS |

The netlist identifies it as 100 nF, Samsung `CL05B104KO5NNNC`, 16 V X7R,
0402 (`Capacitor_SMD:C_0402_1005Metric`), with part assertion for 100 nF.
This is suitable as the local high-frequency bypass on the 3.22–3.38 V ADC
rail. The 16 V rating materially exceeds the rail envelope.

`U_ADC_3V3X_OK` is exact `TPS389001DSER`, in the documented TI DSE0006A
footprint. Its pin map is verified as SENSE=1, GND=2, MR_N=3, VDD=4, CT=5,
RESET_N=6. VDD pin 4 and GND pin 2 are on `N3V3_ADC` and `GND` respectively;
the added capacitor is therefore across its supply. SENSE remains pin 1 on its
unchanged divider net `U_ADC_3V3X_OK_SENSE`; MR_N remains pin 3 on the
unchanged `N3V3_ADC` net. No MR/SENSE node or endpoint was changed by 569.
RESET_N remains `ADC_DIGITAL_OK` with the existing open-drain/pull-up logic.
The TPS3890's 1.5–5.5 V VDD range and 1.15 V threshold are compatible with the
declared ADC rail and the retained 169 kΩ/100 kΩ sense divider.

## Rail, protection, and rule review

The rail owners and declared envelopes are coherent: protected 12 V input feeds
the adjustable 5 V buck, which feeds 3.3 V/1.8 V/0.9 V buck rails; `N3V3_ADC`
is the LT3045 linear rail with 4.1–5.13 V input, 3.22–3.38 V output, 720 mV
worst-case headroom, and a declared 477 mW versus 650 mW screen. The reviewed
producer log's stage calculations pass those rail envelopes and all declared
capacitor-bank screens. The source/pin/net delta adds no uncontrolled rail
owner, cross-domain short, reversed protection path, or rating mismatch.

The input protection contract remains conditional: the 11.4–13.2 V isolated
source, F_IN/Q_IN/D_IN path, bounded 3.4 A fault peak, 10 ms cumulative excess
criterion, and no-retry-before-power-cycle rule remain requirements, not a
qualified supplied system. The updated clauses explicitly include every fitted
downstream capacitor, including this new bypass, in the required source/output
capacitance-discharge qualification.

ERC evidence is 0 errors and 4,173 warnings, matching the stated retained
warning baseline. The new capacitor does not add an ERC error. Warnings remain
debt and are not waived by this verdict.

## Producer status and retained holds

The original 569 producer attempt is `status: ERROR`, return code 1, with the
input-packet post-execution freshness failure and incomplete empty
`source-invariance.txt`; it remains ERROR. The separate artifact-observation
result says `scope: artifact observation only; not schematic acceptance or
retroactive producer PASS` and is recorded only as a byte-identical 7/7
checkpoint observation. Neither observation nor this review promotes the
producer.

`DO-NOT-ORDER` remains required. Retained holds are: exact isolated source and
cable selection plus whole-episode load-line/discharge/repeated-fault evidence;
firmware configuration/readback and interface integration; thermal analysis and
measurement; an independently reviewed routed physical board with actual
returns/escapes/clearances; first-article electrical, hot four-wire and
waveform qualification; final sourcing/allocation and assembly checks; and
release-gate completion. The E-FAULT clarification is conditional source
eligibility only and does not clear any of these holds.
