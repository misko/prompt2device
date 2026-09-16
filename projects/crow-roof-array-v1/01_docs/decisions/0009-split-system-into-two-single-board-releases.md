---
id: 0009
date: 2026-09-01
status: accepted
---
# 0009 — Split the array into two single-board releases

## Context
The accepted roof appliance needs two electrically different custom boards: a
central shared-clock audio carrier and a replicated microphone pod. The board
project contract permits one fabricable board per project. Treating the two as
one release would obscure their different quantities, fabrication tiers,
connector roles, first-article tests and change histories. The archived central
and pod boards also demonstrate why a shared cable contract must be checked at
both ends: their incompatible power-pin maps would short a straight-through
cable.

## Options
- **One multi-board release in this project** — fewer directories, but violates
  the single-board organizing contract and couples unrelated fabrication lots.
- **Make this project the central PCB and add only a pod project** — technically
  possible, but conflates the existing roof/system acceptance record with one
  board's release criteria.
- **Keep this project as the integration authority and commission two
  single-board projects** — more explicit coordination, with independent
  releases and one cross-board cable contract.

## Decision
Keep `crow-roof-array-v1` as the held system-integration record. Commission
`crow-audio-carrier-v1` for the central eight-channel ADC/MCHStreamer carrier
and `crow-mic-pod-v3` for the identical remote analog microphone pod. Each
child owns exactly one PCB and one release line.

## Consequences
The child projects must carry the same straight-through four-conductor spoke
pin map and a non-vacuous cross-board check. The central release does not claim
the pod, Pi, PoE path, roof geometry or acoustic system is complete. The pod
release does not claim central sampling, networking or localization. Whole-
appliance weather, lightning, acoustic, storage and identity tests remain in
this parent and cannot block an honestly scoped PCB design release; they do
block first-article and unattended-roof claims.
