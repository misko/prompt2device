# Third-party notices

The repository's [MIT License](LICENSE) applies to its original content.
Imported materials retain their respective copyright and license terms,
including when copied into a generated artifact, example, or release archive.
An MIT declaration in a project package does not relicense its dependencies
or bundled third-party assets.

This inventory identifies material families and known provenance records. It
is not a claim that every existing vendor file has verified redistribution
permission. Where permission has not been recorded, that question remains
unresolved; availability for download alone is not recorded permission.

## KiCad libraries

The vendored [KiCad 10.0.4 package-model subset](projects/pluto-rx2-8way-v5/03_src/lib/3dmodels/kicad-10.0.4/README.md)
contains eight unmodified STEP models from the KiCad library contributors.
Its README records upstream paths, the pinned tag, and SHA-256 hashes, and
the upstream [LICENSE.md](projects/pluto-rx2-8way-v5/03_src/lib/3dmodels/kicad-10.0.4/LICENSE.md)
is retained beside the models.

These libraries use CC-BY-SA 4.0 with KiCad's design exception. Consult the
retained license and [KiCad's library licensing statement](https://www.kicad.org/libraries/license/)
for the terms applicable to library redistribution and designs using library
data. The root MIT license does not replace those terms. Other copied KiCad
symbols, footprints, and models retain their upstream terms as well.

## EasyEDA, JLCPCB, LCSC, and component models

| Material and location | Provenance and licensing status |
|---|---|
| EasyEDA component JSON and OBJ/STEP files in archived project `.easyeda_cache/` directories, including `archived_projects/crow-array-pod/.easyeda_cache/` | Component codes and model identifiers identify imported catalog assets. Rights remain with the relevant creators or suppliers; no blanket MIT grant or verified per-asset redistribution permission is recorded here. |
| Imported component geometry under project `03_src/lib/3d/`, `03_src/lib/3dmodels/`, and footprint/symbol libraries | Use the associated part dossier, model-registration record, and any embedded notices to identify the source. These directories can mix original geometry with vendor imports; location or format does not determine ownership. |
| HRO TYPE-C-31-M-12 model in `projects/usb-controlled-debug-hub-2a-v1/03_src/lib/3d/TYPE-C-31-M-12.step` | The [model-registration record](projects/usb-controlled-debug-hub-2a-v1/03_src/rules/model_registration.yaml) identifies JLC component C165948. That engineering provenance does not establish redistribution permission; the imported model is not relicensed as MIT. |

Supplier models and library data can also appear in generated boards,
assemblies, verification bundles, and historical releases. Their existing
terms continue to apply there. Independently authored component envelopes
remain original project content; do not infer that all models are imported.

## Vendor datasheets and reference documents

Vendor PDFs are stored in `projects/*/02_parts/<MPN>/` and
`archived_projects/*/02_parts/<MPN>/`, with source URLs, revisions, and hashes
in the adjacent `part.yaml` dossiers where recorded. These documents remain
the material of their respective manufacturers or publishers, including
Texas Instruments, WCH, Espressif, Raspberry Pi, Littelfuse, and other
component suppliers. Distributor hosting does not make them repository-authored.

For example, the [CH224K dossier](projects/usb-controlled-debug-hub-2a-v1/02_parts/CH224K/part.yaml)
records WCH manual v2.1, its upstream download page, local PDF filename, and
checksum. It records engineering provenance, not an express redistribution
grant. This notice does not assert permission to redistribute that PDF or
other vendor documents whose terms have not been established.

External-device reference sources are also cited in
[`external_hardware/`](external_hardware/README.md), including the
[Pluto+ hardware record](external_hardware/plutoplus_hardware/README.md).
Linked upstream documents retain their own terms; original measurements and
notes in this repository fall under the root license.

## Dependencies and future imports

Packages referenced by `package.json` and lockfiles retain their own licenses.
The project-level `"license": "MIT"` field covers the original project content,
not every package installed by its build tools.

For new imports, follow [CONTRIBUTING.md](CONTRIBUTING.md): retain upstream
notices and record redistribution permission, or link to the upstream file
and use an untracked local cache. Existing vendor copies with unresolved
permission still need an asset-by-asset review and, where necessary, a
replacement with upstream links plus updates to affected build references.
This licensing documentation update does not remove those copies or rewrite
immutable release archives.
