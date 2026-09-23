# Crow USB carrier ambient-scope audit

Read-only ambient audit complete (no edits).

## Disposition

The PCM4204 rejection on “retained −40..+80°C spoke service envelope” is not supported as a binding carrier/ADC requirement. That range was imported from the *external 15 m spoke cable* source, not a board or pod ambient specification: `projects/crow-audio-carrier-v1/02_parts/8909650150/primary-source-record.md:3` says the exact Weidmüller cord is operating −40..80°C; `projects/crow-audio-carrier-v1/01_docs/journal/schematic.md:3608-3611` repeats it as a cable datasheet fact. It provides no carrier-board/component ambient requirement.

## Binding/current sources

`projects/crow-usb-carrier-v1/01_docs/BRIEF.md:75-82` records only the new USB-carrier directive and Q1 unanswered. `:89-95` makes retained audio/spokes/external power an A1/A2 assumption pending Q1, and `:99` explicitly escalates any enclosure requirement. The requirements handoff calls that the sole new hard directive and treats all else as inherited/provisional/owed (`01_docs/research/2026-09-22-crow-requirements.md:3-7`); its spoke interface is provisional (`:18`) and its closure list asks the user to confirm spokes/external power (`:78-84`). No source establishes a carrier min/max ambient.

## What actually exists

The carrier has a 70°C *engineering thermal screen* for the branch (`03_src/rules/power_tree.yaml:244-276`; especially `:276`), and first-article asks testing at intended extremes but does not name them (`01_docs/FIRST_ARTICLE_TEST_PLAN.md:54`); its 70°C calculation is a board thermal obligation (`:112-116`). None is a −40..+80 service requirement.

## Selected-XMOS consistency check

Exact selected `XU316-1024-TQ128-C24` is named at `02_parts/XU316-1024-TQ128-C24/part.yaml:1` and binds XM-014532-PC at `:12-19`. That local XMOS PDF p.5 states commercial qualification **0..70°C**, industrial **−40..85°C**. Thus a purported carrier −40..+80 requirement would already fail the selected C24; it cannot rationally be used only to eliminate PCM4204 (−10..+70).

The sole PCM statement is research-only (`01_docs/research/2026-09-23-stocked-adc-architecture.md:1-3`); its unsupported rejection is at `:52`. Recommend reclassify it as an unresolved environmental-qualification gate, not accept/relax PCM. Need explicit deployment ambient/enclosure/adoption before either PCM or C24 can be qualified; current facts do not authorize inferred relaxation. The imported scope is cable/spoke infrastructure rather than a verified pod/carrier requirement.
