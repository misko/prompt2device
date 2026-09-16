# Cold-start input protection: source backtrack, not schematic acceptance

Date: 2026-09-09 UTC. Exact examined source:
`6cb756c92e34b7faa81544beb2b9a0d03c52ddb1`.

## Review execution outcome

Fresh readability completed all8 rows and was adopted verbatim. The topology
reviewer sent a substantiated candidate finding but did not return its final
review before the hard03:39:09Z deadline. Root observed the clock at03:39:11Z
and interrupted it; the tool reported previous status `running`. No completed
topology verdict or witness is inferred from progress messages. All8 unfinished
formal rows are INCOMPLETE in
`06_build/verification/schematic-review-20260909-c29cb85e/topology/timeout.json`.
No replacement was used: correct the independently confirmed bad source first.
The previous canonical topology review remains unchanged and stale, not accepted.

MEASURED461/461 frozen packet entries reverified after interruption. The owning
PR-REVIEW check, with the absolute native-netlist path, graded2/2 artifacts and
failed on the stale topology rule hash at03:40:39Z. Log SHA-256:
`d1890b01a3ba40ac0c298b77bf272cb54943367e9cedf60908e463bb909a7dd1`.
An earlier invocation used a repository-relative netlist path where the CLI
expects project-relative or absolute; it failed before grading and is retained
as a command error, not a design result.

## Root verification: CS-01, P1, confirmed source gap

MEASURED by reading exact TSX, current spoke contract and TI primary document:
J1–J8 pin1 receive protected12V through their branch fuses; the OPA1656s receive
`5V_OPA` downstream of the buck. Each audio leg reaches the corresponding
amplifier noninverting input directly through a1µF coupling capacitor. Its100kΩ
bias resistor is a shunt to VMID, not a series limiter. All8 channels share this.

The spoke contract specifies DC-coupled pod outputs,2.35–2.65V settled common
mode,100Ω nominal source resistance per leg, and no hot-plugging. It does not
bound pod-output cold-start slew or require that the carrier amplifier rail
rise first. A connected system's cold power-up is not hot-plugging.

TI SBOS901C page4 gives input-current absolute limits±10mA and input-voltage
limits V−−0.5V to V++0.5V. Root also reopened the current public
[TI OPA1656 datasheet](https://www.ti.com/lit/ds/symlink/opa1656.pdf) on this date;
it remains Rev.C with these limits. This is component authority, not measured
board damage or an actual pod waveform.

INFERENCE, explicit admitted counterexample: an initially discharged1µF
capacitor,100Ω source, and0→2.65V common-mode rise in10µs while the amplifier
rail is at most0.2V cannot satisfy both absolute limits. With current≤10mA,
capacitor charging over10µs is≤0.1V (the100kΩ branch adds negligibly). The
source resistor drops at most about1V, leaving at least about1.55V at the input,
above its0.7V upper limit. Alternatively, an illustrative0.5V steering-clamp
model at zero supply gives(2.65−0.5)/100=21.5mA initially. This is a model,
not a guaranteed diode drop. The missing envelope, not an assumed measured
failure, is the confirmed defect. Upstream5.5V ESD protection and downstream
ADC isolation do not establish protection at this amplifier input.

## Preserved reviewer messages: verbatim, not a completed review

These actual messages came from fresh read-only
`/root/carrier_schematic_topology_6cb756c9`. Their incomplete execution status
is not changed by the reviewer's stated intended final verdict.

> Independent topology candidate finding: ordinary cold startup can violate OPA1656 input current. J1–J8 pod12V is immediate protected input; 5V_OPA follows AP63205 soft-start. Allowed connected pod with100Ω/sourceleg, DC common mode0→2.65V fast whileOPA rail~0 drives through1uF C_AnP/N directly toU_AFEn.3/.5; ~21.5mA using0.5V steering clamp, aboveTI10mA limit. No pod output slew or relative power-up bound found in current spoke contract; upstreamTPD5.5V standoff and downstreamTMUX do not fix it. Checking exact primary limits and authority before final verdict; do not edit packet.

> Finding is substantiated against exact OPA1656 SBOS901C p4: input current±10mA absolute max, inputvoltage V−−0.5..V++0.5. No actual failure claimed: current source contract admits a connected-pod fast cold-start case. Even a10us0→2.65V common-mode rise through100Ω/1uF withAFErail≤0.2V cannot meet both inputabsolute limits (10mA maximum permits≤~0.1V capcharge, leaving~1.55V atinput versus0.7V allowed). Hotplug prohibition does not exclude coldpowerup. I will mark topology DEFECTIVE with one P1 finding and exact row evidence. AFTER packet verify clean461/461 at03:35:33Z.

> Final checks complete except requested MCH Figure3 visual if you can return it promptly. One P1 cold-start input-clamp finding will fail component_identity_and_ratings, eight_analog_signal_paths and sequencing_partial_power; remaining five rows have source/primary evidence. All461 packet hashes reverified again clean03:36:51Z. No project writes/builds or prior-review consumption. Will return final before03:39:09Z.

## Next work order and boundary

D-BACK destination: analog-input topology/protection source, not placement or
routing. The finding cannot be expressed as a placement correction. A fresh
exclusive source owner must independently verify the full admitted transient
envelope, choose a source-owned remedy from public primary information, and
assess polarity, tolerance, all16 legs, rail injection, noise, loading and
steady signal range. Do not silently narrow the pod contract or rely on an
unmeasured startup sequence. The immutable pod release must not be edited.

Add a known-bad regression that fails this source, then demonstrate correction
against the adopted bounds. Update source manifests, rules, annotations and
affected placement inputs coherently. Address both nonblocking readability
annotations in this revision where feasible. Never hand-edit generated PCB or
schematic files. Source changes invalidate dependent checkpoints/reviews;
regenerate and obtain fresh exact-subject reviews before placement.

The30-file supplemental cohort is
`06_build/verification/schematic-review-20260909-c29cb85e/capture-review-closeout/`,
9,300,548bytes, manifest SHA-256
`f66f6ee93e1d58bf60e4054d12a758f5956d4306be1b9cefe366c42112fb610d`.
It retains preparation/adoption attempts, timeout state, six requested native
PDF detail images, and the separate read-only silk diagnosis.

INHERITED: pod design release unchanged; carrier PCB unaccepted/unrouted;
physical and TOP77/0.20A first-power holds remain. Public52/52 at03:15:13Z is
not allocation or order approval. No main push or carrier release seal occurred.

## Fresh source-owner handback and independent root closeout

The source owner returned INCOMPLETE at04:17:05Z, before04:20:38Z deadline,
and explicitly released its writer lease. No production TSX, manifest, dossier,
checker, test, rule, schematic, PCB or checkpoint was changed. Neither SR-01
nor SR-02 was implemented. The initial generated handoff delta was preserved.
No corrected-design GREEN exists.

Root read the complete proposal/handback and independently reopened the strict
terminal, all472 immutable packet entries, all469 live baseline files, actual
logs and process states at04:19:08Z: zero indexed live changes, zero live owned
PIDs, HEAD still8e88e42b. This is observation of an incomplete author attempt,
not electrical acceptance or an independent schematic review.

| MEASURED check | Result | Log SHA-256 |
|---|---|---|
| Necessary-limit diagnostic on exact source | RED rc1,16/16 direct inputs; input lower bound1.543955V vs0.7V if current stays≤10mA, or required current≥17.635786mA | `433c30a84d5a8c2c5b222bfe5a0ce53dfbb8762217d905876a0ae102774cfe7f` |
| In-memory4.7k-only candidate | INCOMPLETE rc2; current screen3.273682mA, shared-rail screen5.841489V; NOT adopted | `72eb0a987e85e7eab67e9cee8038804cb172242cf4fe550d1fa807619ef51b9f` |
| Disposable diagnostic regression |5/5 PASS; proves diagnostic behavior, not corrected design | `84719d0482db55202347a5e57a36fdbbddaa5a4577aa19cd815cb80bf7411b80` |
| Unchanged full carrier source suite |224/224 PASS,80.411843s bounded command; baseline only | `aae6181562989b542fe47e4c5b05de65f8dff8d5234222f795d1a1bfbb6e167c` |

Working proposal, NOT adopted:16 existing4.7k resistors after the100k bias tees,
an explicit4.7k rail bleed, and relocation of existing470µF C_RAW_HOLD from
5V_BUCK to5V_OPA. The latter must be both electrical and physical. This would
add17 resistors,302→319 components, without adding total nominal reservoir
capacitance. It still changes charge paths and hold/startup behavior.

The proposed normal-pod0..5.5V envelope is an engineering assumption covering
the pod's nominal5V rail with margin, not a guaranteed transient waveform or
ESD clamp. Resistor all-condition and film-capacitance corners remain to be
closed. No narrowing of the present spoke contract has been adopted.

The proposal derives an isolated-local-rail storage bound by using
`S = C_R*V + sum(C_i*max(-v_i,0))` and finite bias-tee replenishment.
With its explicitly provisional passive corners and source envelope it gives
5.388237V, rather than granting a fresh arbitrary precharge on every cycle.
It excludes the real ferrite/raw-domain and other stored-energy interactions;
those exclusions prevent using it as a supply-rail PASS.

Root independently spot-checked a corresponding ideal-diode ODE in56 square-wave
scenarios, both0V/5.15V initial rails, with step sizes≤10µs. Its worst numerical
peak was5.216254V. This is conditional numerical corroboration, NOT a bound on
unexamined waveforms or the physical coupled rail. Root used a slightly higher
bleed resistance4847.75Ω than the proposal's4824.55Ω; neither is a newly proven
manufacturer corner. Script and command output are captured; log SHA-256
`62e9f70bdb146b0dcd3502156b0ccd7277d645014267bb61fa3a2d1876675cbf`.

Next engineering work: close exact passive corners and the complete coupled
raw/OPA/held-supply energy model; assess explicit resistive damping if the
ferrite transfer cannot be bounded. Recheck the inherited tight shutdown and
startup limits, then implement a coherent source correction and obtain actual
RED/GREEN plus regeneration and fresh reviews. No missing user choice was
identified; this is unfinished engineering, not a request for vendor contact,
an uploaded JLC worksheet, or a waiver of connected startup.

All43 closeout capture files,428,980bytes, are preserved under
`06_build/verification/cold-start-source-20260909-8e88e42b-r2/root-closeout-capture/`.
Manifest SHA-256:
`4f0fca79812357ac6b86fea9e0e313b6624ab0f6981294c7fa3dd482dd801c2a`.
Actual author terminal SHA-256:
`364f32d5038bad5ef95955de16411f0a4457f449fd909b6ce66ec4d989cb38a7`.
Actual handback SHA-256:
`33ff025a841e5799882ec17071e8e4520ef2742960d5355b1bc0484f8c6c15c8`.
