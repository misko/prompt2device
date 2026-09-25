# Expanded TDM DATA local-return P2 probe

**Research-only P2 geometry.** The probe binds the expanded locked board at SHA-256
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16` and changes
no canonical board, source, rules, status, P1-fixed reference, connector, or mounting hole.

It uses the board's existing coupled timing-neighbour placement: `U_XU.107` is
at `(200.8375,97.6)` and `C_XU_VDD_106` is at `(198.6,99.1,180°)`. The isolated
fixture adds a 1.0325-mm, 0.15-mm F.Cu `TDM_DATA_1V8` stub west to `(199.805,97.6)`.
It adds a 0.60/0.30-mm GND via at `(197.2,98.2)`, joined to `C_XU_VDD_106.2` by
two 0.15-mm segments through `(197.55,98.5)`. Native filling puts that via in
the existing In1.Cu GND polygon 8.

The measurement checks all 33 P1-fixed poses remain unchanged. In equivalent
scratch DRC contexts it adds no clearance, width, short, hole-clearance, or
via-dangling finding. The only new issue is the intentional dangling DATA stub.

This is a coordinate-level local-return opportunity only. It proves no completed
route, continuous final return, timing, impedance, crosstalk, via behavior,
source/receiver margin, P1/P2 capacity, or acceptance.

Reproduce from the worktree root:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-expanded-tdm-data-local-return-terra/probe.py > /tmp/crow-expanded-tdm-return.json
cmp /tmp/crow-expanded-tdm-return.json projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-expanded-tdm-data-local-return-terra/result.json
```

The default replay writes no repository file. To retain an additional result,
pass `--write-result NEW_PATH`; it refuses an existing path, including the
committed `result.json`.
