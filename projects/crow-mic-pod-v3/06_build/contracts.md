# contract: 06_build/

**Purpose** — generated build evidence. Most of the tree is disposable, but an
open J-PCBA prelayout checkpoint carries the exact nondeterministic design bytes
needed to continue in a clean checkout without silently rebuilding a different
subject. Deleting that allowlist deliberately reopens the checkpoint.

**Mutability** — free outside the explicit tracked prelayout allowlist. Frozen
inputs/request/checkpoints are immutable until deliberately archived together;
the response and future receipt are operator evidence and may change only via
the documented JLC workflow.

The new tracked portability exception is exactly six artifacts:
`../03_tscircuit/build/circuit.json`,
`../03_tscircuit/build/schematic.pdf`, `build_provenance.json`,
`netlists/crow_mic_pod_v3.net`, `sourcing/prelayout_request.json`, and
`sourcing/prelayout_response.csv`. The two checkpoint records bind that set
plus already-tracked source/schematic authority. The receipt path is visible
for future real operator evidence but no receipt exists at this checkpoint.

## Allowed

| Path | What | TTL |
|---|---|---|
| `renders/**` | PNG/SVG/PDF of schematic and board | regenerate |
| `netlists/**` | exported netlists | regenerate |
| `drc/**` | DRC/ERC/audit reports (`gate.json` = the current gate result) | regenerate |
| `route/**` | KRT routing chain inputs/outputs (`r0..rN`, `taps_*.kicad_pcb`) | regenerate (needs KiCadRoutingTools) |
| `fab/**` | JLC export: gerbers, `bom.csv` (carries LCSC codes between runs), `cpl.csv`, zip — the CONTRACT's names, so a seal COPIES rather than renames (07_releases/contracts.md requires `fab/bom.csv` + `fab/cpl.csv`) | regenerate; bom LCSC column is the seed store |
| `pdf/**` | release PDF set + PNG verification renders | regenerate |
| `cache/**` | **volatile market data**: stock, price, distributor attrs | hours |
| `proof/**` | regenerated candidate boards for comparison against the selected exact/current `04_kicad` reference (never written back) | regenerate |
| `twin/**` | jlc_twin fetch/compare workspace | regenerate |
| `mechanical/**` | generated PCB-interface snapshots, CAD/mesh exports, fit coupons, renders, verification reports and hash-bound candidate packages | regenerate from `03_src/mechanical/` plus the exact bound PCB subject |
| `tmp/**` | scratch workspace for in-flight stage work | regenerate |
| `pin_review/**` `pin_audit/**` | fresh-context pin-review dossiers + verdicts (either spelling; boards have used both) | regenerate |
| `verification/**` | **the SEAL STAGING AREA** — every gate's evidence, written here and COPIED into `07_releases/<ver>/verification/` at seal time. It had no row until 2026-07-31 despite being live on a shipping board (smc0985-cooksense carries 27 files here), because `--projects`' exit code was never read. Same names as the sealed copy, so the seal COPIES and never renames — see the `fab/**` row for what a rename costs | regenerate |
| `checkpoints/*.json` | tracked stage-boundary certificate over exact artifact/tool/source hashes; lets a later task resume without rerunning an expensive or human-reviewed producer | regenerate only by deliberately reopening that stage |
| `netlists/crow_mic_pod_v3.net` | tracked exact prelayout netlist named by the stage checkpoint | immutable while the prelayout checkpoint is open |
| `sourcing/prelayout_request.json` | tracked exact-code JLC operator checklist; subject/assembly/policy paths are request-relative so relocation does not change its bytes | immutable while the prelayout checkpoint is open |
| `sourcing/prelayout_response.csv` | tracked blank operator worksheet initially; only a real logged-in JLCPCB check may populate it | operator evidence |
| `sourcing/prelayout_receipt.json` | exposed by `.gitignore` but absent until the grader consumes a real response; never fabricate it | live operator-derived evidence |
| `sourcing/public_catalog_probe.csv` | exact request-derived public-catalog probe BOM; not an order BOM | regenerate when the frozen request changes |
| `sourcing/public_catalog_stock.json` | machine-readable public JLC/LCSC catalog negative filter; explicitly does not predict PCBA allocation | refresh within 24 hours of a public-only continuation |
| `sourcing/public_catalog_stock.txt` | human-readable companion to the public catalog JSON | refresh with the JSON |
| `audit_<date>/**` | a dated one-off audit workspace (`audit_2026-07-19/`, `pin_audit_fresh_<date>/`) — a snapshot of a re-gate, kept until its findings are dispositioned into `08_reviews/` | regenerate |
| `easyeda_cache/**` | easyeda2kicad model cache (tool drops it in CWD — keep it HERE, not project root; usb-hub-3s 2026-07-21) | regenerate |
| `reads_outside_root.log` | clean-room runs: every out-of-root read, path + reason (toolchain-only at the end) | keep for the run's audit |
| `rebuild.sh` `policy_audit.md` `policy_erc.json` `policy_drc.json` | orchestration + audit outputs at build root | regenerate |
| `render/**` | render outputs (either spelling; boards have used both) | regenerate |
| `*.log` `*.rpt` `*.csv` `*.json` `*.md` `*.net` `*.step` `*.png` `*.svg` `*.sh` | loose build-root artifacts — the tree is DISPOSABLE; structure lives in the subdirs above | regenerate |
| `build_provenance.json` | canon **M-FRESH**: the per-run build witness written by `build_provenance.py stamp` and completed by `verify` (`run_id`, `started_ns`, `src_fingerprint` + the file LIST behind it, `board`/`tsx`, then `artifact`/`artifact_sha256`/`producer`). Tracked only while named by the open prelayout checkpoint. | immutable while the prelayout checkpoint is open; otherwise regenerate |
| `contracts.md` | this file | |

## Why `cache/` matters

Volatile lookups (JLC stock, LCSC attributes, distributor pricing) are cheap
per call but add up: one session fetched attributes for 287 parts at ~1.2s
each and left them in a SESSION-scratch directory, so the next session would
pay all ~6 minutes again. Cache them here, keyed by query, with a
`fetched_at` — and **re-fetch before ordering regardless**, because stock
moves and a stale number is worse than no number.

Never promote anything from `cache/` into `02_parts/`. Facts are permanent;
market data is not.

## Forbidden

- Anything unregenerable outside the governed prelayout evidence allowlist. If
  deleting the rest of `06_build/` would lose information, that information is
  in the wrong folder.
- Committing anything here outside the exact prelayout allowlist above.
- Creating or populating `prelayout_receipt.json` without a real logged-in
  JLCPCB response graded by `jlc_pcba_availability.py`.
- Treating a cached stock number as truth at order time.
- Treating the public-catalog pre-layout exception as authenticated JLCPCB
  allocation, economics, release sourcing clearance, or order authority.

## Validate

- `.gitignore` covers `06_build/` and re-includes only `contracts.md`,
  `checkpoints/*.json`, the one named netlist, build provenance, and the three
  prelayout sourcing paths
- every file named by either prelayout checkpoint plus the blank response is
  tracked; the receipt path is visible but absent before the operator check
- every `cache/` entry carries a `fetched_at`
- deleting the allowlist is an explicit archive-and-restart operation; an
  ordinary rebuild must stop before the nondeterministic producer

## Repair

- Tracked file in `06_build/` → decide: regenerable (delete + gitignore) or not
  (move to `03_src/`, `01_docs/`, `02_parts/`, or `07_releases/`).
- Cache entry with no timestamp → delete; unknown age is unusable.
