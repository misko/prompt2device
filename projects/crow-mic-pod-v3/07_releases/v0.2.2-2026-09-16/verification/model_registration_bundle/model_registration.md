# Project native model physical registration

board_sha256: af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938
a-render_verdict: PASS
registration_kind: P-MODEL-REG
config_sha256: c54b1068479a3cec655e8ea2233ac58dd68489188a908ca8a46b1556d92ad55f
stage_receipt: 06_build/pre_route/model_registration.stage.json
accepted_bundle: 06_build/pre_route/model_registration_bundle/bundle.json

This aggregate is independent physical-registration evidence. Each group uses an origin-centred coupon and compares native-model pixels with mounted-side Fab/courtyard and each group's declared drilled-centre, all-pad-centre or SMD-overlap datum. Catalog-twin renderer fidelity is a separate gate.

| group | refs | tuple cache key | group report | result |
|---|---|---|---|---|
| j1_wurth_615008160221_official_step | J1 | `180dabc794bc224db68a28e2d9931f3a4b88ddafce1ff5213de7c1b9a167d91a` | `06_build/pre_route/native_registration/j1_wurth_615008160221_official_step/native_model_registration.md` | CACHE-HIT |
| u2_ti_dgn0008g_official_step | U2 | `c6a530d5fdd8b8e30dbd678573c3281110494f7b09de3d7288b39944c06273a6` | `06_build/pre_route/native_registration/u2_ti_dgn0008g_official_step/native_model_registration.md` | CACHE-HIT |
