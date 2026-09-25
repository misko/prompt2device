# Expanded-locked USB edge ownership proposal — 2026-09-25

This is a source-ownership feasibility result only. It creates no canonical
source or board change, route, P1/P2 credit, connector FULL result, or release
claim.

## Minimal source model

The smallest checker-expressible model keeps the frozen board unchanged and
splits the fixed connector from its support circuitry:

- `usb_edge_connector` owns only `J_USB`, in `[224.9,20,235.1,28]` mm.
- `usb_frontend` keeps the seven USB support references, in
  `[200,29,238.5,40]` mm.
- A disjoint `board_integration_usb_edge` region `[229,28,231,29]` mm carries
  the F.Cu `usb_edge_access` stage between the connector south face
  `[229,27.8,231,28]` and frontend north face `[229,29,231,29.2]`.

The stage owns exact fixed accesses for `J_USB.B6`, `A6`, `B7`, and `A7`:
respectively `[229.1,27.25,229.4,28]`, `[230.1,27.25,230.4,28]`,
`[230.6,27.25,230.9,28]`, and `[229.6,27.25,229.9,28]` mm. Its affected
endpoint denominator also includes `U_USB_ESD.1/.2` and explicit P2
pad-to-face plus In1.Cu filled-return obligations. Omitting those affected
endpoints fails closed with `integration affected endpoint/layer denominator
mismatch`; the earlier edge-owner probe records that failure.

## Replayed current checker result

The following direct current-checker invocation returns `INCOMPLETE` with zero
errors and zero diagnostics. `usb_device_pair` is `INCOMPLETE`; both
`p1_accepted` and `routing_realized` are false.

```sh
python3 skills/kicad-pcb/scripts/p1_corridor_capacity.py \
  projects/crow-usb-carrier-v1/06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb \
  projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-expanded-locked-p1-sol/coarse.json \
  /tmp/usb-edge-owner-current-check.json \
  --expected-contract-sha256 9faaed39333c0db45c188003d2ac6bacc69562f259f8332d0d6a79db7d25037f \
  --source-requirements projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-expanded-locked-p1-sol/p1_requirements.yaml \
  --expected-source-sha256 e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92 \
  --interfaces projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-expanded-locked-p1-sol/modular_plan.json \
  --expected-interface-sha256 02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8 \
  --aliases projects/crow-usb-carrier-v1/02_parts/USB4215-03-A/part.yaml \
  --expected-alias-sha256 a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e \
  --floorplan projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-expanded-locked-p1-sol/floorplan.yaml \
  --expected-floorplan-sha256 8a805d92d4f57c3a0db00a45d1c9aef57958eb0c219d44f9ca89e5531021d8b4 \
  --diagnose-all
```

The board input is
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`.
The current checker is
`fdbf97c70a105205423a7b4430f584344346a2250ddb63a0f71260e7cb284dd0`.

## Replay qualification and boundaries

The packet's historical `build_trial.py` expects checker hash
`5c4eba1e1286c6dd69e8f553e99117ba70acdd5c45740eb9678bdf5b5a529e10`.
It now stops at `checker: pinned input SHA drift`; it cannot serve as a current
replay receipt until that historical pin is deliberately rebased and reviewed.
The direct check above is therefore current-checker feasibility evidence only.

No checker result supplies physical pad escape, four-leaf DP/DN merge,
ESD-to-XU transition, effective-rule clearance, a connected route, skew,
filled In1.Cu return, connector qualification, P1 admission, or P2 placement
acceptance.
