# Connector orientation review

machine_verdict: PASS
subject_sha256: ee066f412899580aff6d669d2dafa1adacd3b8479eb226cbe631b0e65d045c62
board_sha256: 2685281fdb8dac636e16334c2d4eca679300bfa5322a368ac2685b59f48e3dd1

| ref | board access axis | edge | edge distance mm | mating-plane edge offset mm | model/footprint alignment | verdict |
|---|---|---|---:|---:|---:|---|
| J1 | [0.0, -1.0, 0.0] | north | 5.86 | 0.5 | 1.000000 | PASS |

## Human-review representatives

| representative | machine-graded refs | tuple |
|---|---|---|
| J1 | J1 | `121c209ce888313d` |

## Machine findings

- none

## Machine notes

- none

## Human confirmation

Review every present image. Each ref requires `top`, `outside`, and `inside`; orthogonal profiles are included when the target is not occluded by another connector. Approve only when the visible mouth/access direction, mounting side, keying, and cable approach agree with the intended physical use.
