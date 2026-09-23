subject: crow-usb-carrier-v1 Murata capacitor-bank source adjudication
date: 2026-09-23
reviewer: independent SOL agent /root/modular_review, source qualification
context-given: full-tree and controlling prior power-bounds disposition
source_commit: c9cc9db86d1f6aa8b9b343d32b22c784746e680a
board_sha256: not-generated (source-only)
design_verdict: SOUND (source engineering screen only)
order_verdict: BLOCKED-SOURCING

# Capbank review adjudication

Date: 2026-09-23
Candidate: `c9cc9db86d1f6aa8b9b343d32b22c784746e680a`

## Corrected verdict

**ACCEPT as a source-stage engineering candidate, with narrow disposition wording updates.** The initial independent review's requirement for a manufacturer-guaranteed production minimum or a new provisional E-CAP schema was stronger than the owning repository contract and is withdrawn.

## Contract interpretation

`03_src/rules/contracts.md` requires each effective-capacitance bank to name the IC requirement, exact fitted contributors, tolerance, DC-bias, temperature and lifecycle derating, plus evidence and basis. `early_design_check.py` multiplies those declared terms and rejects nameplate-only capacitance. Neither source requires a manufacturer-guaranteed minimum distribution or a physical lot measurement at `DESIGN_CLEAN`.

The code's docstring/error language calls the result “conservative” and “worst-case effective,” but the accepted project precedent defines that as a reviewed engineering bound over explicitly declared loss factors, not a production guarantee. The existing closed `USB-capacitance` finding says exactly that: reviewed conservative engineering derating closes the source screen while production and physical-stability qualification remain separate. The prior accepted CKG bank used a weaker cross-part typical proxy plus engineering reserves. The proposed Murata bound improves evidence quality by using exact-base-die combined DC-bias/temperature models, rounding retention downward, applying exact ±10% initial tolerance, and retaining an explicit 12.5% lifecycle reserve.

Therefore, E-CAP PASS legitimately means “the declared, independently reviewed source-stage derating screen exceeds the device minimum.” It does not mean guaranteed lot capacitance, regulator stability, allocation, or first-article performance. A new provisional schema is unnecessary for this candidate.

## Bound assessment

The arithmetic and inputs are acceptable as an engineering screen:

- 5.099 V/-55 C exact-base model: 14.7 uF, rounded down to 31% nominal retention before 0.90 tolerance and 0.875 lifecycle factors.
- 3.38 V/-55 C: 16.9 uF, bounded using 35% retention, again below the 35.96% model ratio.
- 1.818 V and 0.92 V models are higher, while the candidate conservatively reuses the 35% retention bound.
- The tightest TPS62825 result is 12.954 uF against 10 uF, and its nominal 47 uF/0.47 uH pair matches TI Table 8-3. The TPSM three-part result is 34.422 uF against 25 uF. LT3045 capacitance screens have wider margin.

These bounds are not silently upgraded to Murata guarantees. Model applicability, exact raw coefficients, chosen reserves and limitations remain visible in the dossier and research report.

## Required wording reconciliation

Before integration, replace stale phrases such as “review pending,” “pending independent review,” and “approval-sheet or measured lot data ... before acceptance” with the precise disposition:

- the exact-model/reserve calculation is independently accepted for the source-stage E-CAP screen;
- manufacturer approval data or representative-lot measurements remain recommended production/first-article qualification, not a prerequisite for authoring this source candidate;
- P3 must still realize and extract the LT3045 shared output network, Kelvin OUTS and return topology; its component model is typical, so assembled ESL below 2 nH remains unproven until physical evidence;
- startup/load-step behavior, TPS62825 replacement-inductor stability, TPSM bank behavior, stencil/paste, JLC placement and order allocation remain later mandatory receipts.

The gate output itself need not claim “production worst case.” A future general wording improvement from “effective”/“worst-case effective” to “declared derating screen” would make the boundary clearer, but it is not required to accept this isolated source candidate and should not be bundled as unrelated infrastructure.

## Remaining integration boundary

Compose the candidate onto the accepted OPA/YXC state (`5ea267d3` or its current descendant), rebuild the expected 490-component source, and verify exact ref/MPN/FPID census, zero source errors, deleted-ref absence, and intended net identity. The isolated candidate `dist` predates the YXC correction and is not integration evidence.

Physical board measurements are not required before source adoption. They remain required at their owning P3/native/first-article stages, and no release or PCBA-readiness claim follows from this corrected acceptance.

## Controlling prior disposition checked

After drafting this adjudication, I read `01_docs/research/2026-09-22-power-bounds-adoption.md` and `/tmp/crow-capbank-gate-semantics.md`. They confirm the same controlling rule: the earlier manufacturer-guarantee-only condition was explicitly superseded; exact-part typical data may support a deliberately adverse, independently reviewed source engineering allowance when operating conditions, added reserves and remaining physical uncertainty are explicit. This is not a waiver by the coordinator. My numerical review above independently accepts this candidate's exact combined-condition model, downward rounding and margins under that existing rule.

The integration receipt should therefore say: **E-CAP source engineering estimate PASS; production capacitance/ESR/ESL and regulator stability remain unqualified.** It must not close `USB-commission`, claim `DESIGN_CLEAN`, or remove P3/first-article obligations.
