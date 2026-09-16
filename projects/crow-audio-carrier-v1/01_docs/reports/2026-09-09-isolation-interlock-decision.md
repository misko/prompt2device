---
schema: 1
kind: pcb-human-report
report_id: 2026-09-09-isolation-interlock-decision
title: Isolation decision and a bounded optical interlock correction
subtitle: Eighteen contacts, two separately sequenced LED-return groups, no protection adoption
project: crow-audio-carrier-v1
date: 2026-09-09
status: DRAFT
evidence_status: INCOMPLETE
---

## Executive conclusion

**INFERRED:** Prefer the normally-open optical architecture for the next bounded
source correction. A direct TMUX7412FRRPR substitution on the held 5 V rail is
outside its 8 V minimum single-supply operating range. Moving it to the existing
12 V feed also does not make the present 5 V supervisor an adequate early-loss
detector for that switch supply. This disqualifies those two concrete wiring
arrangements, not the whole TMUX family or every possible higher-rail redesign.

**PROPOSED:** Use eighteen AQY221R2SZ contacts, driven by nine independent
two-LED strings on `5V_OPA`. Eight strings serve the differential ADC pairs;
one serves both reference reservoirs. Two separately qualified, physical
LED-return switches implement `AUDIO_EN` and `PWR_EN` sequencing. The exact
proposed circuit is below. PWM alone is not its off-state safety element.

**OWED:** Do not yet adopt this protection circuit. The deciding condition is
end-to-end transition containment: the LED interruption and contact transition
must occur while retained ADC/reference/input charge cannot push an ADC or OPA
pin outside its applicable voltage/current limits, including a correlated
restart. This is not a requirement to reach 10 nA in 0.2 ms. Maintained rails
and bounded transition current are legitimate ways to satisfy it. No physical
failure of the proposed optical circuit has been demonstrated.

**CITED:** A smaller supported source correction is implemented: remove the
duplicate, inherited OPA1656 sourcing override from the OPA2320 dossier and
replace its stale layout authority with the exact OPA2320 primary. Five new
regressions protect this identity boundary. Focused tests passed 22/22 and the
full carrier source suite passed 272/272. No electrical topology, value,
acceptance limit or native file was changed.

## Question and scope

**CITED:** This commission compares precisely the TMUX7412F and AQY221R2S
arrangements for sixteen ADC legs and two buffered-reference reservoirs.
OPA2320, eight channels, 1.2 Vrms differential, eight 0.10 A spokes, header
voltage at least 10.8 V, no hot plug, unchanged microphone pod and no firmware
remain fixed. Audio need not remain valid during shutdown.

**CITED:** The 0.30 A local 5 V allocation and 1.0 A upstream screen are existing
engineering budgets, not additional user requirements. They remain unchanged
in source. A candidate can rederive the allocation but cannot call the old
5 mA/channel allowance an exact OPA2320 quiescent load.

## Evidence boundary

**CITED:** Initial source authority is commit
`88863614fe373bf4c3f5d8dc5609cc5e104873b5`; frozen native subject is raw
`527c825e91023717782f9f7b55e0993ce831e9da941418541575b45b2aae5bbf`, semantic
`4a60bca1a1f9809279cb73503b7f7cf3acc73616bbabd6aa5d844c38058452fa`.
The task envelope canonical-JSON SHA256 is
`5116f7b9c871ca2b6639f9f2df8448ad91f2d2812d49cf271cbb4acb28dd7823`;
all five input sizes and hashes were checked before task work. Later
administrative commits do not replace that frozen engineering authority.

**CITED:** Primary PDFs were reopened, including the unchanged pod's TPS7A49
and OPA1679. The pod has its own LDO start and filtered midpoint, so its output
and reference cannot be treated as independent instantaneous voltage steps.
No new numerical experiment was launched. CAR-F12 remains REASSESS 4/6, one
non-improving attempt, no pending launch and no new source-correction credit.
Existing routine regressions are not a new investigation launch.

**OWED:** Native is stale and unrouted. Source-only geometry/library tests do
not constitute a fresh saved-native review, routed-board proof, stability
qualification or release admission. No new candidate MPN is adopted by this
report, and no full-board sourcing pass is claimed.

## Findings

### Exact switch comparison

| Arrangement | Evidence and consequence |
|---|---|
| TMUX7412FRRPR on `5V_LDO_HOLD` | **DATASHEET:** SCDS404B p5 specifies 8 V minimum single-supply operation. Its full-temperature UVLO thresholds are not a 5 V operating qualification. **INFERRED:** Reject this direct substitution. |
| TMUX7412FRRPR on existing 12 V | **DATASHEET:** UVLO rising is 5.1–6.4 V and falling 5.0–6.3 V, while operation starts at 8 V. Drain terminals must remain between its rails; source protection cannot be assigned to both ends. **INFERRED:** During a slow 12 V fall through 7 V the AP63205 can still regulate 5 V and the existing `U_PWR` may stay released. The switch is outside its functional range before that detector necessarily reacts. A separately retained higher switch rail and its own earlier detector would be a different, larger correction. |
| AQY221R2SZ contacts | **DATASHEET:** Normally open, bilateral contact without an analog-supply pin. At 25 C the catalog gives 1.25 ohm maximum on-resistance at 5 mA LED current, 18 pF maximum output capacitance, 10 nA maximum off leakage with zero LED current, and 0.2 ms maximum turn-off under the stated 10 V/40 ohm test. **INFERRED:** Removes the particular switch-supply/analog-terminal dependency; does not remove the control or stored-charge problem. |

**DATASHEET:** Panasonic specifies LED operate current up to 3 mA and release
current down to 0.1 mA at its stated 25 C load test; the present product page
recommends 5–30 mA LED drive. These are not full-temperature timing guarantees.
The catalog timing waveform and separate leakage test do not establish a
carrier-specific time to the leakage limit. This report does not interpret the
waveform as a guaranteed 25 mA residual current or require an invented leakage
endpoint. [Panasonic primary catalog](https://mediap.industry.panasonic.eu/assets/download-files/import/ca_semiconductor1154_en.pdf)
and [terminology](https://tp.industry.panasonic.com/en/products/control/relay/photomos/term).

### Concrete optical circuit delta, not yet adopted

**PROPOSED:** Replace each `U_SIGn` dual switch with two AQY221R2SZ SOP4
contacts: pin3/pin4 connects `FILTERnP` to `ADCnP` and `FILTERnN` to `ADCnN`.
Retain the ADC-side 100k pulldowns and 1 nF capacitors. For each reference,
insert one contact after the existing 1k output isolation resistor and before
`VMIDn_BUF`/its 4.7 uF reservoir; OPA feedback remains at `VMIDn_RAW`, before
the resistor/contact. Retain the 10k reference-input current limiters and
existing divider, bias and coupling networks.

**PROPOSED:** Pins1/2 of each optical package are LED anode/cathode. Each ADC
pair forms one series LED string; the two reference packages form the ninth.
Use one TPS92612DBVR current driver per string: pin1 ground, pin3 `5V_OPA`,
18 ohm 1% sense resistance between pins3/4, pin5 to the first LED anode;
the first cathode connects only to the second anode. Pin2 PWM may be held high
from the same raw rail: it is not relied upon for safety interruption. Provide
local supply bypass as in the primary application, and do not put a capacitor
across an interrupting return switch. The 18 ohm exact resistor identity and
final current-driver sourcing need adoption screening; no anonymous resistor
is added to source by this proposal.

**PROPOSED:** All eight ADC-string final cathodes join `LED_ADC_RET`; the
reference-string final cathode is `LED_REF_RET`. Each return has its own
AO3400A: pin3 drain to return, pin2 source to ground, pin1 gate to
`LED_ADC_GATE` or `LED_REF_GATE`. With a return open, a driver's retry has no
intended DC path through either LED to ground. Do not merge these return
domains or connect a midpoint to ground. This topology makes the interruption
independent of PWM behavior, not independent of MOSFET leakage/parasitics.

**DATASHEET:** The DBVR driver regulates 93.5–102.5 mV across its sense
resistance under the specified conditions; 18 ohm at 1% gives 5.14–5.75 mA.
Its fault-retry current is 0.64–1.528 mA and can ignore PWM. Thus PWM-low alone
is not an unconditional off-current argument. That fact does not demonstrate
that this carrier actually enters the fault state. [TPS92612 primary](https://www.ti.com/lit/ds/symlink/tps92612.pdf), pp4/8–9.

**PROPOSED:** Add one TPS389001DSER guard per return group. Both guards use
pin4=`5V_OPA`, pin2=ground, local 100 nF bypass, pin5=100 nF to ground and
pin6=the corresponding AO3400A gate. Pull pin6 up with 100k to `5V_OPA` and
down with two series 100k to ground. Feed each pin1 SENSE from its own divider:
two series 100k from `5V_LDO_HOLD`, one 100k to ground. This is a nominal
3.45 V held-rail threshold, well above the existing supervisors' 1.5 V
functional minimum; resistor tolerance, hysteresis and sense current must be
included in its final bound. Reuse existing RC0402FR-07100KL and
CL05B104KO5NNNC identities for these proposed passives.

**PROPOSED:** Do not wire held `PWR_EN`/`AUDIO_EN` directly to a raw-powered
guard's MR input. For each group, use two 2N7002K-7 common-source stages:
first gate to the existing group enable, source ground, drain `LED_x_INV`
with 100k pullup to `5V_OPA`; second gate to `LED_x_INV`, source ground,
drain to guard pin3 MR with 100k pullup to `5V_OPA`. Thus high qualified
enable permits MR high, while low enable pulls MR low. Only the first
insulated MOSFET gate crosses from the held control domain. All drain
pullups and guard output pullups belong to the raw LED supply domain.
This adds four 2N7002K-7 devices, not an unqualified logic-IC power-off input.

**DATASHEET:** TPS3890 section8.3.4 explicitly permits SENSE from 0 to 5.5 V
regardless of its supply voltage. The proposed 200k series top path also
limits a hypothetical held-to-dead-domain path to 27.8 uA per guard at 5.5 V
and 1% resistance tolerance; this is a conservative circuit current bound,
not a newly invented input-injection rating. MR does not receive that same
independent-input authority, motivating the MOSFET translation. Its output
is forced low above its 0.8 V maximum POR boundary subject to the stated
15 uA load condition; below POR it is undefined. The 100k pullup respects
that 15 uA condition at 1.5 V. [TPS3890 primary](https://www.ti.com/lit/ds/symlink/tps3890.pdf), pp5/12/14.

**INFERRED:** On cold start, raw-powered guards are operational before their
held-rail sense threshold can be met. On removal or brownout the group enable
and held-rail threshold can each request interruption. On restart with retained
held charge, the group-enable chain must requalify; a high held voltage alone
cannot command a return on. Below guard POR the driver is also below its
published POR thresholds, but unspecified off leakage and stored parasitic
charge are still part of the deciding containment condition, not declared
zero. The extra guard delay must be counted; it is not a free safety margin.

### Loading, charge and geometry are still in the circuit boundary

**INFERRED:** Existing `check_power_source.py` bookkeeping is approximately
278.9 mA: 150 mA ADC allocation, 4 mA LDO allowance, 90 mA amplifier allowance,
20.25 mA audio-output charging/load screen, 1.04 mA switch allowance, 2 mA
control allowance and 11.58 mA maximum bleed. Replacing only 90 mA with the
exact OPA2320 30.6 mA total maximum quiescent term, removing 1.04 mA TMUX,
and adding nine 5.75 mA LED strings plus nine 0.25 mA DBVR driver allowances
gives approximately 272.5 mA before the new guard/translation loads. These
are algebraic comparisons, not a new simulation or complete supply proof.

**OWED:** The approximately 27.5 mA apparent headroom is not spendable until
reference/bias DC load, guard pullups and gate leakage, output loading,
reservoir charging and transient overlap are counted consistently. The DBVR
0.25 mA condition includes a supply-range boundary that must be reconciled
with the actual low rail. The Q1 suffix has different tabulated test conditions
and is not silently substituted. Existing 0.30 A and 1.0 A limits are unchanged.

**INFERRED:** Nine strings add about 52 mA to the raw held reservoir while
enabled; this changes its decay. The current 320 us/4.5 V screen is an
engineering screen, not an OPA2320 absolute minimum or proof of damage after
4.5 V. The OPA minimum operating supply is 1.8 V, but functional supply
alone does not license output backdrive. Keep the entire coupled state:
sixteen 1 uF input capacitors, eight two-leg bias paths, two approximately
11 uF external reference reservoirs, the two 4.7 uF buffer reservoirs, ADC
input capacitors/pulldowns, raw/held bulk banks, delayed LDO/dump sequence
and unchanged pod ramps. In particular, optical reservoir isolation does
not erase the reference's separate noninverting-input current path.

**PROPOSED:** Layout has eighteen SOP4 contacts in place of eight WQFN signal
switches, plus nine SOT23-5 drivers, two WSON guards and six SOT23 MOSFETs.
Place each ADC contact at its existing filtered ADC boundary, reference
contacts beside their 1k/reservoir nodes, and LED/control routing away from
high-impedance inputs. This is a nontrivial floorplan change; no current
clearance or area acceptance is claimed by the smaller dossier patch.

### Implemented source-author correction

**CITED:** The OPA2320 dossier had two explicit top-level `sourcing` keys.
Its trailing inherited key selected C1849431, the earlier OPA1656 catalog
identity, despite the intended C2863402 key near the beginning. Ordinary
PyYAML kept the trailing value. The same tail cited SBOS901C/OPA1656 layout.
The correction retains the original OPA2320 sourcing mapping and replaces
only the stale layout-reference tail with SBOS513F pp19/28. Figure49 is
identified as a family example, not exact carrier copper or loop proof.

**CITED:** Five new tests check unique effective identity, the exact primary
layout reference, a reintroduced duplicate, a unique wrong catalog code and
an inherited layout reference. Before repair the positive checks failed on
actual duplicate/layout semantics, not environment setup. After repair:
22/22 focused tests, 272/272 full source tests. Existing KiCad library stderr
assertion notices and unclosed-file ResourceWarnings did not fail the suite.

## Recommendations

**PROPOSED:** Review and accept only the OPA dossier/test correction now.
Do not promote this optical proposal to source/native acceptance through
report prose. The immediate next bounded correction is the two-reference
contact/LED-return interlock cell specified above, with one representative
ADC return load representing all eight strings; do not reopen amplifier
selection or start another unrestricted switch search.

**OWED:** The single deciding condition for that cell is transition
containment: from loss assertion through any low-held/raw restart, the
measured or otherwise justified LED-current/contact-conductance trajectory
must keep the actual ADC and OPA pins within their applicable limits until
stored charge is harmless. Count guard delay, return-gate decay, contact
transition, all continuing loads and possible sense/gate leakage in that
same interval. If containment fails specifically at a retained VMID output,
the smaller next delta is two resistor/AO3400A discharge branches from
`VMID1_BUF`/`VMID2_BUF` to ground controlled by existing `DUMP_GATE`, with
OPA current and reservoir charge bounded before choosing discharge values.
That fallback is not implemented or prequalified here.

**DATASHEET / PROPOSED:** In concrete terms, require the time at which contact
coupling becomes harmless to precede the first loss of the protected pin
margin, and preserve that margin throughout the transition. CS5308P DS1314F1
Table3-3 gives analog-input limits of -0.3 V to `VDD_A + 0.3 V` and +/-10 mA;
the current limit does not waive its voltage limit. OPA2320 SBOS513F6.1
permits current-limited input overdrive at no more than 10 mA, but supplies no
equivalent output-backdrive allowance. Thus keeping `5V_OPA` above 1.8 V is
useful only when the coupled output/reference node is also safe; do not
substitute a supply-only timing check for this condition. These are primary
limits applied to the proposed waveform, not newly tightened project limits.

## Validation plan

**PROPOSED:** First review the above exact node/part delta and source
invariants, then commission one bounded test of the deciding condition.
Exercise cold start, input removal, slow brownout and correlated restart
with retained reservoir charge and unchanged pod behavior. Observe LED
current, both return gates, raw/held/ADC rails, both VMID raw/buffer/input
nodes and a representative ADC leg; include the load contribution of all
eighteen amplifiers and eighteen contacts. A violated pin bound or an
uncommanded contact reclosure while that bound is vulnerable falsifies the
proposal. A missing typical-curve endpoint alone does not.

**CITED:** This commission launches none of those new experiments. A later
numerical launch requires reviewed reassessment and the existing investigation
runner; a physical qualification requires its own authorized setup. Subsequent
source adoption needs an ADR, exact dossiers/sourcing, topology and hostile
tests, then regeneration and a fresh native review. Those are downstream
boundaries, not evidence already obtained here.

## Source register

- **CITED:** [Task](../../06_build/handoffs/2026-09-09-isolation-source-author/TASK.md),
  [source](../../03_tscircuit/src/crow_audio_carrier_v1.tsx),
  [power screen](../../03_src/check_power_source.py),
  [OPA dossier](../../02_parts/OPA2320AIDR/part.yaml),
  [focused regressions](../../03_src/tests/test_reference_protection.py).
- **DATASHEET:** [TI TMUX7412F SCDS404B](https://www.ti.com/lit/ds/symlink/tmux7412f.pdf),
  pp4–6/33–35; [Panasonic exact SZ product](https://industry.panasonic.com/global/en/products/control/relay/photomos/number/aqy221r2sz),
  catalog printed pp203–206 (PDF pp178–181), ds_x615_en_aqy221_2s:010611J.
- **DATASHEET:** [OPA2320 SBOS513F](../../02_parts/OPA2320AIDR/OPA2320_SBOS513F.pdf),
  [CS5308P DS1314F1](../../02_parts/CS5308P-DN/CS5308P_DS1314F1.pdf),
  [TPS3890 SLVSD65A](../../02_parts/TPS389001DSER/TPS3890_SLVSD65A.pdf),
  [AO3400A Rev3.1](../../02_parts/AO3400A/AO3400A_Rev3.1.pdf).
- **CITED:** Candidate primary cache is
  `06_build/cache/isolation-source-author-20260909/`; hashes are in the observed
  outcome. These research copies are not adopted part dossiers.
- **CITED:** [Dated sourcing observations](../sourcing/parts-selection-2026-09-09.md)
  distinguish exact product pages, suffixes and observed pools. No allocation,
  contact, login, upload, order or whole-board sourcing pass occurred.
