# XMOS D10 independent review — ACCEPT

Reviewed final implementation commit `bfe12486` (parent D10 authority `21523739`) in `/home/mouse9911/gits/circuits-worktrees/xmos-reserve-d10`. Worktree was clean after the commit. This accepts the narrow public-stock reserve exception and its policy propagation; it does not assert a sealed release, JLC PCBA allocation, purchasing readiness, or physical qualification.

## Authority and scope

`projects/crow-usb-carrier-v1/01_docs/BRIEF.md` D10 and accepted decision 0009 authorize zero extra public units only for XU316-1024-TQ128-C24 / C6362698 / U_XU. `03_src/rules/assembly.yaml` retains build quantity 5 and default surplus 150, adding one exact D10 override with surplus 0. `stock_surplus_policy.py` rejects a different MPN/code, nonzero or boolean surplus, duplicate overrides, a different project, missing Crow D10 BRIEF/accepted ADR, and non-U_XU refs. Crow's default 150 is also enforced.

## Consumer trace

`jlc_stock_check.py --assembly` loads that policy from its project path, grades each aggregate coded BOM line with `5 × qty + applied surplus`, and records the exact override and per-line applied surplus in JSON/CSV. `manufacturing_readiness.py` compares evidence override metadata against assembly policy, binds request quantities/designators and the override's exact source ref/MPN, and recalculates thresholds. `release_freshness_check.py` binds the override to actual placed fab BOM/CPL refs, the evidence MPN/designators, evidence policy metadata, and per-line arithmetic; it continues to grade releases without overrides using their prior policy. The default threshold remains quantity plus 150 for all other coded parts. These gates preserve public-catalog-only scope; JLC population and order-time allocation remain obligations.

## Real source and observation

Independent census of diagnostic circuit `b68fd99fad9092260c1e2fd2630cf1a63ce334057802e6c464aa6052b8ab307c` and exact-parts CSV `06cac75109bc3ef737d46d57da4bba8b871d666729143f854b628df1017526b2`: 568 source components and 568 unique CSV refs; 88 coded aggregate rows cover 544 refs; the remaining 24 are D9 manual through-hole refs. The XMOS row is exactly one U_XU, C6362698, XU316-1024-TQ128-C24.

The serial public catalog refresh's XMOS raw observation reports stock 41 against the D10 threshold 5. Its original report recorded 87/88 literal MPN matches. The corrected alias regrade covers C192562 at stock 3,886 against unchanged threshold 155. I verified SHA-256 of the original report, raw C192562 response, existing Molex part dossier, and prior independent population report against the corrected regrade; all four match. The raw response retains exact code C192562 and manufacturer MOLEX, with catalog spelling 436500200; the dossier documents that exact spelling as selected 43650-0200. Corrected coverage is 88/88; no other surplus was reduced. This report is dated public catalog evidence only.

## Verification

Reran `test_xmos_stock_exception.py` (4), `test_public_distributor_prelayout.py` (9), `tests/t1_assembly_gates.py` (51), and `tests/t1_release_freshness.py` (105): all passed. `git show --check bfe12486` passed. Focused tests include positive XMOS/ordinary thresholds, wrong code/MPN/ref/project/directive rejection, altered evidence/threshold rejection, and actual placed BOM/CPL ref mismatch. Existing assembly and release suites cover legacy behavior. I also constructed a temporary prelayout request and temporary fab BOM/CPL from the real 568-reference exact-parts CSV and the preserved 88-code observations (with the documented C192562 alias regrade): `manufacturing_readiness._catalog_prelayout_check` passed 88/88; `release_freshness_check.check_stock` returned zero failures and CLEAR with 88 graded lines. Mutating actual placed U_XU to U2 made the release check fail with `STOCK-SURPLUS-IDENTITY`. These temporary files were outside the repository. No review blocker found.
