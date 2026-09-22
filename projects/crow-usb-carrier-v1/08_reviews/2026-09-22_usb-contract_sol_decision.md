# Independent USB net-contract rereview

Verdict: **ACCEPT**

Reviewed only commit `e75f73210286707b5e6a7b46be1c5ad0b5ac54d2`
against parent `14f2ef6d58780267d93ff4de63378a0b7999cbc6`. This
closes the sole provenance defect in the prior independent review (SHA-256
`2fd5713ffa4ba7feb7253127516f222bbd94d29d15ba9515f65a0914e2e5df51`).

ADR 0008 now explicitly owns the complete source policy represented by the
USB_DEVICE nets contract:

- USB_DP and USB_DN are single-net tree members, not chains split at the shunt
  ESD device.
- It names all three corresponding endpoint paths: Type-C A contacts, Type-C B
  contacts, and the ESD shunt leaves, each ending at XU316 pins 60/59.
- It requires no more than 1.0 mm realized P/N copper-length spread for each
  matching path.
- It requires F.Cu routing over continuous In1.Cu and prohibits USB signal
  vias.
- It rejects undeclared copper edges and explicitly declines a congruent-pad
  entry claim or total-copper substitute.

The nets change from the parent is only `adr: "0002"` to `adr: "0008"`.
Members, tree topology, six endpoint paths, nets, tolerances, no-via policy and
octilinear anchors are electrically unchanged. `route.yaml` is byte-identical
to the parent.

ADR 0008 also preserves the review boundary: it states this is source policy,
not placement acceptance, a routability proof, native-board approval, return
continuity or impedance certification, or replacement for order-time stackup
confirmation and first-article TDR/USB eye validation.

Exact reviewed artifact hashes:

- ADR 0008: `eff685b34df682d47c642a150d1daab75f84e8158460f36a6f8cac2f4955e9c5`
- Full candidate `nets.yaml`: `c2de0a8645d156eb219f9ebe65f6978b8123965f7e112d56ee91d12d2d06e109`
- Full candidate `route.yaml`: `8afedc38e5cb3583221c6f4adb48210049f805ce7e507029caae69988931075e`
- `admission-summary.json`: `e194094b33444b69577c75da004f3dd95685a9dd59bfc03d1002a6bc0e9bb79f`
- `admission-without-locks.json`: `ccb943136b14f63d960cbad912a99f31103841ffe01c06cef3aa0a83c6e7450d`

Checks: commit delta inspected; `git diff --check` passed; the authoritative
`copper_length_audit.py --schema` invocation exited 0. This acceptance covers
the source decision and full route/nets snapshot suitability only. Existing
admission findings remain separate and are not waived.
