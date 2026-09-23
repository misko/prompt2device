# Addendum — sourcing-contract membership correction

**PASS.** The pending tracked diff from adopted source commit `87ecfaa1` changes exactly one line in `projects/crow-usb-carrier-v1/01_docs/sourcing/contracts.md`. It adds `jlcsearch-dlc-screen-2026-09-23.md` to the allowed dated sourcing-observation table and states the correct narrow scope: dated exact-MPN public catalog observation with URLs and raw-response hashes; raw responses remain ignored cache; no build, allocation, or order authority.

This is truthful contract membership, not a relaxation of the parent `01_docs` rule. The parent contract permits a dated, provenance-stamped sourcing observation while requiring volatile raw responses to remain in `06_build/cache/`. The child contract had an explicit filename allowlist but lacked this new valid observation filename. The pending row aligns the two levels and does not grant source, release, purchasing, or physical acceptance.

The unrelated untracked `03_tscircuit/dist/` directory was not part of the tracked pending diff and is not assessed here. This addendum does not elevate the earlier source-adoption PASS to a full published/pre-route gate; native/generated CAD, physical, first-article, and order boundaries remain as previously recorded.
