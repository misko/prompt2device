# CS5308P-DNR moisture and reflow authority review

Observed 2026-09-22 in America/Los_Angeles. This is a primary-source review; it does not assign an MSL from another component or package.

## Result

Cirrus's current product page and current datasheet bind **CS5308P-DNR** to the **48-pin QFN, tape-and-reel** ordering option. They do **not** state an MSL, floor life, bake conditions, reflow profile, peak reflow temperature, or a J-STD-020/J-STD-033 classification for this orderable part.

The current manufacturer document is DS1314F2 (January 2026). A full-text search of its 94 pages found none of the relevant handling terms. The retained DS1314F1 and DS1314A5 revisions were searched as a cross-check and also contain no such statement. This is an absence finding, not evidence that the part has no moisture sensitivity requirement.

## Exact binding observed

- The official product-page ordering table names `CS5308P-DNR` and `Tape and Reel`; the page identifies a 48-pin QFN.
- DS1314F2 Section 12, Table 12-1 names `CS5308P-DNR`, package `48-pin QFN`, and container `Tape and Reel`.
- DS1314F2 Sections 10 and 11 provide the package drawing and package marking.

These facts establish the exact device/package/container identity only. They do not establish moisture classification or a safe handling/reflow process.

## Assembly implication

Planned professional secondary population remains honest at design stage, but physical reflow handling is **not closed** by the public manufacturer material found here. Before lot exposure or reflow, the assembler/procurement record needs exact-lot or exact-orderable authority such as the delivered moisture-barrier-bag label and humidity indicator/lot paperwork, a manufacturer packing specification explicitly covering CS5308P-DNR, or written manufacturer-authorized handling evidence. That evidence must supply the applicable MSL/floor-life controls and any required bake/reflow limits.

An IPC/JEDEC handling standard describes what to do after a manufacturer classification is known; it does not itself classify this device. MSL values published for other Cirrus parts or other QFN packages cannot be transferred to CS5308P-DNR.

## Retained evidence

- `CS5308P_Datasheet_DS1314F2.pdf`, SHA-256 `410a8b060d8daabbf7d4a541544049b6bc598a4ddcbd50aeaf50861e2069b6e4`
- `raw/product.html`, SHA-256 `0709c16062ff610696086787dbabe9c4bc236d651972405b19dc1c94fbc42754`
- Older revision cross-checks and extracted text are retained beside this report.
- `sources.yaml` records URLs, timestamps, exact observations, and unresolved fields.

Evidence packet location: `/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/adc-msl-handling/`. The paths in the retained-evidence list are relative to that packet, not this research directory.
