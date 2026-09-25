# Current TI three-pose P1 diagnostic

**Research-only `INCOMPLETE`; P1/P2/P3 remain unaccepted.** This packet replays the prior unified TI P1 source against the current three-pose native board at SHA-256 `0bd3ac8dd8c80177958c009a0644f0bc723bcee7ad7085c2fb76c09c5df958f5`. The builder pins every upstream input, keeps the prior diagnostic integration regions, imports current floorplan poses, verifies each source/modular/native F.Cu terminal and the full native per-net pad set, and writes only this directory. The source and PCB remain untouched.

The timing denominator is **14/14 nets and 54/54 terminals**: ten exact unresolved multi-terminal branches, including the 11-terminal `AUDIO_EN` whose endpoints now lie in their declared owner regions, and four exact `unresolved_two_terminal_crossing` records (`AUDIO_MCLK_1V8`, `TDM_BCLK_1V8`, `TDM_DATA_1V8`, `TDM_FSYNC_1V8`). Three quiet-power `AUDIO_EN` pads still overlap the foreign `input_buck` planning region and remain physical blockers. The shared `integration_candidate.propose_native_witnesses` helper rebound unresolved witness boxes to the current native pads. Its one change is reset `U_XU.38`, from `[215.425, 104.075, 216.9, 104.325]` to `[215.425, 103.875, 216.9, 104.125]` mm. `native_witness_rebind.json` records that proposal.

The full `p1_corridor_capacity` evaluation with `diagnose_all=True` returns `INCOMPLETE`, `routing_realized=false`, `p1_accepted=false`, **zero global errors and nine independent item diagnostics**. All nine primary findings are inherited `power_boundary_windows` witnesses: eight nonlocal bridge boxes and one P2-movable owner lacking a virtual block-face witness. There are **zero derivative global denominator errors** after the timing branches are accounted for. All five allocations remain `INCOMPLETE`; the ADC7 access-only portal still has null capacity. Unplaced branches carry P2 local access/filled In1.Cu return and P3 connected route obligations; none grant physical route capacity or P1 credit. See `issues.json` and `result.json` for the exact findings.

The current board has no mounting-hole footprint; its NPTH pads belong only to connectors. Formal P1 admission and connector FULL therefore also depend on upstream mechanical mounting-hole/restraint geometry. This packet does not resolve that dependency.

Reproduce from the worktree root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-current-three-pose-p1-diagnostic-sol/build_trial.py
```

The builder asserts the exact current board hash, source/contract/floorplan/interfaces/portal/aliases/checker hashes, native branch admission, allocation states, zero global errors, nine power diagnostics, and P1 rejection. Output is deterministic at source SHA-256 `8bb5f71b36f6723005bf2a346ddba8acb00d530fd5cd5787128e0c27ca297749` and contract SHA-256 `cdf20223e49b6e491eec76ca3b95182bcc6b4b4fa67727af20e5ef1971e216cc`.
