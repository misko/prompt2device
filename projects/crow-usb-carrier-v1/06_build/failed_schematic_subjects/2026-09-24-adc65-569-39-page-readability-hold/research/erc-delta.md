# Crow ERC baseline reconstruction (read-only)

## Historical source identity

Historical source used:

`/tmp/crow-adc65-root-prep-preserved/checkpoint-files/04_kicad/crow_carrier.kicad_sch`

SHA-256:

`9b4c8100d0a08284fe9f3858c8081d6117ca5f66fae0b1752ff7a85b7efd38e1`

This is the requested SHA-256 and agrees with the checkpoint's `SHA256SUMS`.  It
also agrees byte-for-byte with Git commit `925ce47dbedf0d52238585e2ad4f9812a7998151`,
path `projects/crow-usb-carrier-v1/04_kicad/crow_carrier.kicad_sch` (Git blob
`abd0d7b0eaf95580ac8e89c032d16bf42c44d17b`).  Therefore the exact accepted
historical native schematic is available and was used; no source was inferred.

The standalone SHA artifact is
`/tmp/crow-568-historical-schematic-sha256-terra.txt`.

## Reconstructed baseline

Command run against that preserved historical source, with output directed only
to `/tmp`:

```sh
kicad-cli sch erc --severity-all \
  --output /tmp/crow-568-erc-historical-terra.rpt \
  /tmp/crow-adc65-root-prep-preserved/checkpoint-files/04_kicad/crow_carrier.kicad_sch
```

Installed CLI: `kicad-cli 10.0.4`.  It completed with exit status 0 and printed
`Found 4216 violations`.  The regenerated raw report is
`/tmp/crow-568-erc-historical-terra.rpt` (SHA-256
`96bacd94fae85cf7d65690181461eb7289c13428ac05c92355ce783bd326c9be`), timestamped
`2026-09-23T19:29:52` by KiCad.

## Category reconciliation

| Warning category | Historical 568 baseline | Current raw `06_build/erc.rpt` | Current minus historical |
| --- | ---: | ---: | ---: |
| `endpoint_off_grid` | 2671 | 2625 | -46 |
| `lib_symbol_issues` | 977 | 979 | +2 |
| `footprint_link_issues` | 568 | 569 | +1 |
| **Total warnings** | **4216** | **4173** | **-43** |
| Errors | 0 | 0 | 0 |

The 43-warning difference is exactly the category arithmetic: 46 fewer
off-grid endpoint warnings, offset by two additional library-symbol warnings
and one additional footprint-link warning.  No new ERC warning category is
present: both reports contain only the three categories in the table.

## Locations and interpretation

An exact comparison of category plus reported location/description finds 370
current-only instances (176 `endpoint_off_grid`, 172 `lib_symbol_issues`, 22
`footprint_link_issues`) and 413 historical-only instances (222, 170, and 21
respectively).  Thus there are changed/new reported locations even though there
are no new warning types.  They are concentrated in the reworked ADC region
(approximately x=510--966 mm, y=942--1158 mm), including changed wire endpoints,
component positions, and `#PWR` instance numbering.  These location-set counts
are not additional net warning counts: moving or renumbering one schematic item
turns an otherwise comparable warning into one current-only and one
historical-only report entry.

The current raw report was generated at `2026-09-23T18:58:21` and has SHA-256
`227e24f82f4684a45803116aa0111cec07138a55f35ca93c21616ea2c12a8f38`.
The formal historical packet did not retain a raw categorized ERC report, so
the 4,216 baseline here is a regeneration.  It was run with the currently
installed KiCad 10.0.4 at the timestamp above; the original historical tool
version and run time are not established by this reconstruction.  Category and
location comparisons should therefore retain that tool-version/time caveat.

No project files were edited and this report makes no gate, review, or adoption
decision.
