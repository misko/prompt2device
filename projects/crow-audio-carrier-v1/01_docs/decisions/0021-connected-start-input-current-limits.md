# ADR-0021 — Connected-start input current limits and damped OPA supply

Status: PROPOSED / INCOMPLETE source candidate; not accepted for regeneration
Date: 2026-09-09

## Fresh source closure update (ce2ea02c, 2026-09-09)

This supersedes the old verification census below, not its open physics.
Reconciled intermediate suite232/232 passed; final results and every failing
attempt are retained in06_build/verification/source-closure-20260909-ce2ea02c-r1.
Explicit historical delta projections preserve unrelated source and have
separate native geometry/topology/hostile coverage. Entries95/95 and all39
moved/new instances clear source tests. Copper-edge gaps: feed-to-OPA
ceramics2.366242/.953422mm, raw ceramic3.522694mm, reservoir-to-ceramic
2.794225mm. No measured10nH loop claim follows.

85 electrical invariants pin new limiter/feed/bleed/reservoir terminals and
values. The buck sheet explicitly labels3.3uH; dump sheet identifies both
gates as inverting Schmitt devices. Native PDF inspection remains owed.
First-article targets now name the actual feed. The old2.5A class is retained
legacy planning, NOT maximum feed current or4A ampacity. AP63205 HS
peak2.5/3.1A and LS valley2.5/3.9A are primary min/max; reservoir equalization
is separate.4A/.84W, current-duration/thermal authority and complete coupled
finite-L/repeated-start proof remain OPEN before generation.
Old zero-load<10mV precharge is withdrawn:2.104mA controls/leakage produce
near49mV loaded residual in the conservative RC screen.0.1ohm equalization
path minimum is an engineering assumption requiring qualification.
See DETAIL_DESIGN and strict INCOMPLETE handback; suite GREEN is not source
engineering closure. No user-envelope narrowing or physical waiver.

CS-01 is a real source defect: the100k bias tees did not limit current into
sixteen unpowered OPA1656 inputs. Connected cold power-up is included; the
spoke contract, immutable pod release and user signal envelope are unchanged.

Select16 existing exact RC0402FR-0710KL10k resistors AFTER the100k tees.
Each new AIN_Pn/AIN_Nn net joins exactly its resistor and OPA input. The
unchanged1uF PET caps and100k bias tees remain cable-side of these resistors.
Replace FB_OPA by exact WSLP1206R0500FEA50mOhm1W resistor, with manufacturer
1.65x1.93mm pads/1.80mm gap. Move C_RAW_HOLD470uF electrically AND physically
to5V_OPA. Add one existing47uF ceramic C_OPA_BULK2. A500ohm bleed uses existing
300+100+100ohm0402 parts in series so dissipation is shared.5V_OPA joins the
2.5A transient source class; its old0.35mm steady-only rule is not retained.

## Primary protection authority and bounded normal prototype envelope

[TI SBOS901C](https://www.ti.com/lit/ds/symlink/opa1656.pdf) p4 lists
input-current±10mA and input-voltage V−−0.5..V++0.5. Section7.3.2 pp16–17
describes current-steering protection, recommends limiting overrail input
current to10mA, and explicitly discusses power-off back-powering. This design
uses that recommended CURRENT-LIMITED overload mode; it does not invent an
exact diode voltage, prove the±0.5V absolute-voltage table from resistor value,
or promise valid audio while an amplifier is underpowered.

The existing pod TSX has its output opamps powered by nominal5V_QUIET and
100ohm output resistors, with DC coupling. Prototype engineering envelope:
each output0..5.5V, arbitrary ordering/slew/repetition; raw regulator0..5.15V
without overshoot; raw/held reservoir initial voltages at most5.15V; amplifier
outputs remain within their supply envelope; unexplained input leakage≤1uA.
These are explicit normal-circuit budgets, NOT manufacturer all-state maxima.
They include discharged starts, normal reachable precharge, shutdown and
rapid restart. No independent externally precharged capacitor fault is added.
The pre-existing destructive internal5V short exclusion remains unchanged.
Partial-supply output behavior, overshoot and all budgets require captures.

Let q=u−tee across each film capacitor. With supplies/bias outputs within
0..5.5V and≤1uA leakage, q remains within±(5.5+105k*1uA)=±5.605V:
at either boundary the bias resistor and passive steering current point back
into the interval. This covers repeated waveform history rather than granting
a new arbitrary precharge each cycle. Zero steering drop maximizes current;
no specific forward voltage is credited. With10k*0.95=9500ohm minimum,
positive/negative current bounds are1.168948/0.590000mA per input.

At a common5.4V raw/OPA/held RC-rail barrier, all16 inputs inject at most
9.608422mA. Bleed removes at least5.4/525=10.285715mA; reserve another18uA
for leakage, leaving0.659293mA. Raw buck cannot source above its5.15V envelope;
held reservoir/precharge/body-diode/reverse-leakage paths are passive and begin
below the barrier, so they cannot create a higher RC-node voltage. Stored
VMID/output charge and partial-supply rail-limited behavior are conditional
budgets, not independently measured guarantees.

The finite-L extension is NOT a solved nonlinear all-waveform theorem.
Complete feed-loop L≤10nH (part≤5nH plus PCB≤5nH) and normal feed peak≤4A
are explicit prototype/layout budgets. Only the94.9uF local and141uF raw HF
ceramics get damping credit: after0.34425 derating Ceq=19.526811uF, giving
critical R45.259977mOhm<47.5mOhm minimum. A single residual4A magnetic-energy
event has conservative local-HF voltage excursion0.069983V, below the0.1V
headroom to5.5V. This is an event reserve, not proof against recurrent magnetic
pumping; the fresh topology review and physical captures must assess the full
coupled nonlinear network. No source PASS is physical/release qualification.

## Tolerances, loading and remaining checks

RC family document PYU-RC_GROUP_51_ROHS_L rev14Nov2025 supplies100ppm/C,
1/16W@70C and linear derating to155C. A deliberately combined±5% prototype
reserve covers initial/TCR and selected qualification-test drifts; it is not
an unlimited-life guarantee. Vishay30122 rev09Sep2024 gives75ppm/C and1W@70C,
derating to170C. Its combined±5% prototype reserve is likewise explicit.
KEMET R82 rev19May2026 confirms PET1uF5%,+400±200ppm/C and the separately
conditioned storage/endurance/humidity/solder tests; capacitor value affects
time constants, not the pointwise rail barrier. No TVS standoff is a clamp.

MEASURED arithmetic: raw buck typical4ms startup2.475089A, LDO bank startup
2.487009A versus2.5A minimum limit;320us raw shutdown4.502764V versus4.5V;
steady local0.278878A versus0.30A. These inherit the engineering timing/drift
budgets from ADR0009. The small shutdown margin remains an explicit hold.
300ohm bleed worst dissipation42.233mW<51.471mW85C derated rating.
The4A feed event dissipates0.84W<0.85W85C rating: very little pulse margin.

Added10k per leg leaves100k cable loading unchanged to first order. At85C,
20kHz rectangular bandwidth,+5% resistance, differential resistor noise is
2.882231uVrms (~112.4dB relative to1.2Vrms). This is a noise tradeoff, not an
SNR measurement. With≤1uA leakage reserve, steady input maximum2.559029V
is below2.593618V common-mode ceiling; existing1.2Vrms differential range is
unchanged. Input capacitance/parasitic pole, distortion, noise and recovery
must be measured. Source tests cannot qualify cold/hot physical behavior.

## Verification boundary

The exclusive source attempt did not achieve a coherent full-project GREEN.
The initial complete run measured225 tests with22 failures. Historical exact
source-delta tests and real new power-entry/placement obligations remain open;
the handback records the final rerun. The manifest has322 component references
and the live-JSX inventory has917 pins/225 nets, but matching counts do not
close these failures. The detailed-design/electrical-invariant contracts still
need reconciliation to this proposal. DO NOT use this candidate for production
generation, ordering, or release until the source-owner boundary is closed.

The live-JSX source regression was observed RED on0885305f before correction;
bounded logs are in06_build/verification/damped-start-source-20260909-0885305f-r1.
The source-test inventory evaluates declarations without running tsci or writing
a native netlist/board. Existing generated PDFs/ink checks still grade only
the retained old checkpoint. All generated artifacts, old placement and
independent reviews are STALE. Root owns full regeneration and fresh review.


## 2026-09-09 amendment — provenance, not protection admission

This amendment preserves the historical argument above. ADR0023 subsequently
adopted OPA2320: the old OPA1656 common-mode ceiling and its comparison are
historical, not current amplifier authority. The existing power checker now
uses OPA2320. No paragraph here closes partial-power isolation, output
backdrive, coupled restart, current duration, or the CAR-F12 source hold.

The seven previously undeclared `<=`/Unicode-bound occurrences reduce to five
unique physical assumptions: leakage (three occurrences), complete loop L,
part L, PCB L, and feed peak current. All five are declared ESTIMATED below.
The optional evaluator answers only whether that assumed value satisfies a
specific existing scalar screen; it does not prove the assumption. In
particular, the two inductance allocations add to the complete-loop budget,
and passing resistor power is not proof of an actual current waveform.

The three resistor/damping comparisons are additionally expressed as solved,
rerunnable limits on the actual nominal part/network or current-budget choice.
Those CITED grades mean reproducible algebra under this document's model,
not manufacturer qualification of the model. Both sides of each calculated
limit are regression-tested; unsafe 100 nH, 4.1 A, 0.01 ohm, 300 ohm and
10 uA alternatives must fail their corresponding scalar screens.

| Historical comparison | Owning declaration / disposition |
|---|---|
| Critical damping resistance versus the 47.5 milliohm minimum feed resistance | CS_FEED_DAMPING_MIN_R; includes the nominal-to-minimum resistance reserve |
| 300 ohm bleed-member dissipation versus its 85 C rating | CS_BLEED_THERMAL_MIN_R; fixes the existing three-member topology |
| Feed dissipation versus its 85 C rating | CS_FEED_THERMAL_MAX_I; distinct from the unproved physical 4 A peak |
| OPA1656 common-mode comparison | Historical and superseded by ADR0023 / current OPA2320 checker; not reused as present evidence |

Other numerical outputs in the historical text remain conditional calculation
observations, not acceptance limits or a proof of recurrence. The single-event
magnetic-energy reserve in particular does not prove repeated-start safety.
The source of each evaluator is `03_src/check_power_source.py:adr0021_bound`;
it reuses `cold_start_screen` and changes no default design budget or source
value. No numerical investigation is launched by reproducing this fixed-source
algebra. The declared worst-case corner means the explicit tolerances within
this conditional model, not a guaranteed worst case of the physical circuit.

<!-- bound: CS_INPUT_LEAKAGE_BUDGET -->
```yaml
id: CS_INPUT_LEAKAGE_BUDGET
claim: "Assumed unexplained input leakage per path in the conditional rail-barrier screen; not measured device leakage."
relation: "<="
value: 1
unit: uA
corner: worst_case
grade: ESTIMATED
why_not_rerunnable: "The all-state leakage envelope has no independent guaranteed source or physical capture. The evaluator only checks the rail-current consequence if this budget holds; it cannot establish actual leakage."
governs:
  evaluate: "/usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound leakage_uA --evaluate {value}"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [1]
  series_why: "This is a physical engineering-budget case, not a purchasable E-series component. The explicit set contains only the existing assumed value; it does not establish a sourced or measured physical maximum."
chosen: 1
requires:
  - projects/crow-audio-carrier-v1/03_src/check_power_source.py
```

<!-- bound: CS_COMPLETE_LOOP_BUDGET -->
```yaml
id: CS_COMPLETE_LOOP_BUDGET
claim: "Assumed complete feed-loop inductance for the conditional ceramic-bank damping calculation."
relation: "<="
value: 10
unit: nH
corner: worst_case
grade: ESTIMATED
why_not_rerunnable: "No saved routed loop or impedance measurement establishes this physical maximum. The evaluator checks conditional damping with the existing derated ceramic banks, not actual loop inductance."
governs:
  evaluate: "/usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound loop_nH --evaluate {value}"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [10]
  series_why: "This is a physical engineering-budget case, not a purchasable E-series component. The explicit set contains only the existing assumed value; it does not establish a sourced or measured physical maximum."
chosen: 10
requires:
  - projects/crow-audio-carrier-v1/03_src/check_power_source.py
```

<!-- bound: CS_FEED_PART_L_BUDGET -->
```yaml
id: CS_FEED_PART_L_BUDGET
claim: "Assumed feed-part inductance allocation with the PCB contribution held at its separate five nH budget."
relation: "<="
value: 5
unit: nH
corner: worst_case
grade: ESTIMATED
why_not_rerunnable: "The adopted resistor's complete mounted parasitic inductance is not independently bounded here. Evaluation adds the separate PCB budget; a passing sum does not prove either physical contribution."
governs:
  evaluate: "/usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound part_nH --evaluate {value}"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [5]
  series_why: "This is a physical engineering-budget case, not a purchasable E-series component. The explicit set contains only the existing assumed value; it does not establish a sourced or measured physical maximum."
chosen: 5
requires:
  - projects/crow-audio-carrier-v1/03_src/check_power_source.py
```

<!-- bound: CS_PCB_LOOP_L_BUDGET -->
```yaml
id: CS_PCB_LOOP_L_BUDGET
claim: "Assumed PCB loop inductance allocation with the part contribution held at its separate five nH budget."
relation: "<="
value: 5
unit: nH
corner: worst_case
grade: ESTIMATED
why_not_rerunnable: "The carrier is unrouted and no realized copper inductance extraction exists. Evaluation adds the separate part budget; it cannot establish future PCB geometry or mounted-loop impedance."
governs:
  evaluate: "/usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound pcb_nH --evaluate {value}"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [5]
  series_why: "This is a physical engineering-budget case, not a purchasable E-series component. The explicit set contains only the existing assumed value; it does not establish a sourced or measured physical maximum."
chosen: 5
requires:
  - projects/crow-audio-carrier-v1/03_src/check_power_source.py
```

<!-- bound: CS_FEED_CURRENT_BUDGET -->
```yaml
id: CS_FEED_CURRENT_BUDGET
claim: "Assumed normal feed-current peak for the conditional resistor-power screen, not the buck's current-limit specification."
relation: "<="
value: 4
unit: A
corner: worst_case
grade: ESTIMATED
why_not_rerunnable: "No correlated startup/restart current-duration envelope establishes this peak. The evaluator checks instantaneous I-squared-R against the stated 85 C continuous rating only, not pulse or recurrent thermal safety."
governs:
  evaluate: "/usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound feed_current_A --evaluate {value}"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [4]
  series_why: "This is a physical engineering-budget case, not a purchasable E-series component. The explicit set contains only the existing assumed value; it does not establish a sourced or measured physical maximum."
chosen: 4
requires:
  - projects/crow-audio-carrier-v1/03_src/check_power_source.py
```

<!-- bound: CS_FEED_DAMPING_MIN_R -->
```yaml
id: CS_FEED_DAMPING_MIN_R
claim: "Minimum nominal feed resistance for critical damping at the assumed ten nH loop and the existing worst-case ceramic capacitances."
relation: ">="
value: 0.0476420810723668
unit: Ohm
corner: worst_case
grade: CITED
command: /usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound feed_resistance_ohm
governs:
  evaluate: "/usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound feed_resistance_ohm --evaluate {value}"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [0.05]
  series_why: "Only the adopted WSLP1206R0500FEA 0.05 ohm nominal resistor is selected. Its minus-five-percent engineering reserve is applied by the evaluator; this is not a catalogue-wide approved series."
chosen: 0.05
requires:
  - projects/crow-audio-carrier-v1/03_src/check_power_source.py
```

<!-- bound: CS_BLEED_THERMAL_MIN_R -->
```yaml
id: CS_BLEED_THERMAL_MIN_R
claim: "Minimum nominal total bleed resistance keeping the existing 300 ohm member within its stated 85 C rating at the assumed 5.5 V rail."
relation: ">="
value: 452.9130092035524
unit: Ohm
corner: worst_case
grade: CITED
command: /usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound bleed_resistance_ohm
governs:
  evaluate: "/usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound bleed_resistance_ohm --evaluate {value}"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [500]
  series_why: "The selected network is the existing exact 300 plus 100 plus 100 ohm RC0402 parts, totaling 500 ohms. Only that network is a sourcing option here; scaling it does not approve a different BOM."
chosen: 500
requires:
  - projects/crow-audio-carrier-v1/03_src/check_power_source.py
```

<!-- bound: CS_FEED_THERMAL_MAX_I -->
```yaml
id: CS_FEED_THERMAL_MAX_I
claim: "Conditional continuous-current arithmetic ceiling for the existing feed resistor at the assumed plus-five-percent resistance and stated 85 C rating."
relation: "<="
value: 4.023739080814782
unit: A
corner: worst_case
grade: CITED
command: /usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound feed_current_A
governs:
  evaluate: "/usr/bin/python3 -B projects/crow-audio-carrier-v1/03_src/check_power_source.py --adr0021-bound feed_current_A --evaluate {value}"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [4]
  series_why: "Current is not an E-series component. The only selected operating-budget case is 4 A through the exact adopted 0.05 ohm resistor; no additional part or operating allowance is adopted."
chosen: 4
requires:
  - projects/crow-audio-carrier-v1/03_src/check_power_source.py
```
