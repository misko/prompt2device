# XU PLL post-anchor refdes ownership review (Terra)

## Scope and retained evidence

Read-only review of SOL current-source probe commit `fee67e27`, in particular
`01_docs/research/2026-09-24-xu-pll-current-source-post-anchor-probe-sol.md`,
and its isolated source copy `/tmp/crow-xu-pll-current-post-sol`. This note
does not admit the PLL probe or change Crow placement/routing.

The three newly degraded fields in that probe are
`C_XU_VDDIO_10`, `C_XU_VDD_39`, and `C_XU_VDD_45`. The baseline reported
there is 259 owned / 266 degraded / 44 unplaced; the probe's existing
`C_XU_VDD_39: [[10.0, 0.0]]` trial remains degraded.

## Generator fact

`skills/kicad-pcb/scripts/generate_board_generic.py:2623-2662` defines the
only present per-reference refdes controls. `priority_refs` changes placement
order. `preferred_offsets` accepts finite exact-ref `[dx,dy]` pairs within
the existing search radius, but prepends them to the ordinary `OFF` search;
it is not a forced coordinate or a waiver. At lines 2705-2716 every
candidate still must pass collision and nearer-to-own-part ownership before it
is retained; otherwise the least-bad candidate is reported as degraded.

Therefore an override must never be represented as a way to suppress either
test. The existing source semantics are sufficient where an owned clear
candidate exists.

## Isolated reproducible result

I regenerated the isolated source with only this `silk.refdes` variation:

```yaml
priority_refs: [C_XU_VDDIO_10, C_XU_VDD_45, C_XU_VDD_39]
preferred_offsets:
  C_XU_VDD_45: [[2.2, -0.8]]
```

The generator output was
`/tmp/crow-xu-pll-current-post-sol/label_two_generate.log`; the saved board
was `04_kicad/crow_carrier_labels_two.kicad_pcb`. It produces 259 owned /
266 degraded / 44 unplaced: `C_XU_VDDIO_10` is owned at `(203.5,112.3)`, and
`C_XU_VDD_45` is owned at `(220.2,99.8)`, 90 degrees, 0.45-mm text.
`C_XU_VDD_39` remains degraded (at `(222.0,99.2)`, against the nearby PLL
cluster). This test changes neither placed parts nor copper.

A separate source-level slot scan used the generator's actual footprint/body
obstacles, its 0.16-mm refdes clearance, and its ownership calculation before
any refdes were emitted. In a 0.1-mm grid extending 7 mm from each target,
there were 1,360 owned clear C10 candidates, 50 C45 candidates, and zero C39
candidates. The generator's own four-pose/84-offset search likewise found
no C39 slot. This is evidence about the current post-anchor geometry only;
it is not a manufacturing spacing requirement.

## Recommendation and release gate

Use the existing declarative controls for C10/C45 only, accompanied by a
native regeneration and an ownership-report assertion naming both refs.
Do not add an exact-position escape hatch: it could bypass the two properties
that make the label safe.

There is no source-only silk-coordinate resolution for C39 in this geometry.
Before admitting the placement probe, either create physical label space by a
reviewed placement/topology revision and rerun the ownership report, or add a
separate, explicit exact-ref F.Fab-only waiver capability. Such a future
waiver must validate the reference exists, retain the matching F.Fab copy,
list the ref in `refdes_waiver.json`, and require assembly-drawing evidence;
it must not classify a degraded F.Silk field as accepted. No such capability
exists or is proposed for implementation in this review.
