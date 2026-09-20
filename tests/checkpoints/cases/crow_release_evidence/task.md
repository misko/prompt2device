# Reconcile Crow v1.0 release evidence

Continue from the supplied mutable release candidate. Follow the current
`pcb-design` release review workflow and use `release_freshness_check.py` as
the final evidence gate. The archived Crow recorder central v1.0 manifest
claims 1,409 ERC warnings while its policy audit says 1,215, and claims a
48-line BOM check while the shipped BOM has 49 data rows. Reconcile the
staged audit, BOM-check record, and manifest summaries so every repeated
measurement agrees with the evidence in this candidate. Preserve the measured
counts; do not rewrite the underlying ERC or BOM evidence to fit stale prose.

Run `python3 <repository root from START.md>/skills/jlcpcb-fab/scripts/release_freshness_check.py
06_build/candidates/crow-recorder-v1.0` and stop when it reports FRESHNESS: PASS
for the mutable candidate. Record the command and result in `HANDOFF.md`. The
candidate is not a sealed release. The incident is documented in
`tests/t1_release_freshness.py` and the immutable original is
`archived_projects/crow-recorder-central-v2/07_releases/crow-recorder-central-v2-v1.0-2026-07-23/`
(`MANIFEST.txt`, `verification/policy_audit.md`, `verification/erc.json`,
`fab/bom.csv`, and `verification/bom_source_check.txt`). The workspace keeps
only the two inconsistent claims and their measured source artifacts.
