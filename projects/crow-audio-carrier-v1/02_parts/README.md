# Carrier key-part dossier status

These dossiers are first-article engineering authority, not a purchase release.
Exact package, pin, limit, and layout facts are extracted from cited
manufacturer documents or retained primary-source records. Every non-null
`datasheet.local` now names a PDF in the same dossier whose bytes match the
declared SHA-256; a Markdown fact record is never presented as datasheet
bytes. A null local field explicitly means that the cited remote source is not
yet reproducible from this project alone.

The 2026-09-08 source correction locally binds all 58 used MPNs covering
299 authored refs: 33 pre-existing bindings (108 refs) are unchanged, and
25 independently inspected captured authorities cover the remaining 191 refs.
This includes the exact manufacturer-supported F_IN ordering correction to
2920L260/33DR; it does not claim independent P-AUTH acceptance. The CS5308P
dossier also retains Cirrus AN0556R1 as a separate
SHA-bound supporting application note; it does not replace the component
datasheet binding. Every JLC/LCSC allocation remains unresolved independently.
The assembly owner must choose and record either a proven JLC allocation or an
explicit manual/consign disposition before manufacture. Nothing here claims
turnkey availability, current stock, price, or order readiness.

## Deviations and open closure

- On 2026-09-08 at13:44Z, the fresh full conductor stopped at P-PREC with
  two reference-record defects: the AP63205 unavailable-CAD reason was under
  advisory `note` instead of required `why`, and the CS5308P record omitted
  an explicit unreached entry for the already documented exact-DN CAD gap.
  Correcting these research records is a documented repair exception to
  revision-only dossier editing. No datasheet, pin map, rating, layout rule,
  component selection or physical qualification changed; no new reference
  retrieval or manufacturer revision is claimed. Original failed output and
  exact pre-edit dossiers are retained in
  /tmp/carrier-fresh-build-20260908.4RBsSy before the fresh retry.

- On 2026-09-07, TOP-BDF-001 required correction of an incomplete extraction
  from the unchanged DMP6023LFG DS37204 Rev.2-2 primary. The dossier now retains
  all eight manufacturer identities and explicitly aliases fused drain
  positions6-8 to schematic/footprint identity5. This is a documented repair
  exception to revision-only dossier editing, not a claim of a revised PDF or
  newly qualified package. Existing net connectivity and the KiCad composite
  drain pad are unchanged; independent re-review remains required.

- All used BOM MPNs now have actual local SHA-bound manufacturer PDFs.
  Unused/supporting mating-hardware dossiers can still lack binaries; none is
  silently promoted to standalone authority. Independent pin/footprint,
  field-extraction and exact-subject review remain separate obligations.

- The official Cirrus layout-guide ZIP and inner-PDF hashes are retained in
  `01_docs/evidence/cs530x-effective-capacitance-source.md`, but those layout
  guide binary files are not committed. Cirrus AN0556R1 is now committed and
  hash-bound in the CS5308P dossier, closing the Figure 2 receive-topology
  source gap only; it does not close the effective-capacitance evidence gap.

- The 1812L and 2920L manufacturer-authored PDFs were adopted from public
  Megastar and Promelec mirrors respectively, with original endpoints and
  access-failure provenance retained. The 1812L binding explicitly replaces
  the old unavailable digest with newly inspected bytes. The 2920L GD02/13/25
  p5 identifies DR/1500-per-reel, not the former unsupported MR suffix.
  Public C22870534 is only a candidate: F_IN remains manually fitted/consigned,
  excluded from turnkey assembly with an empty authored supplier list.
- Molex SD-43650-001 D8 and Littelfuse SMBJ v4 are copied unchanged into the
  carrier from captured official PDFs and independently inspected here.
  Related 43645, 43030 and harness documentation/physical service evidence
  remain separate; historical Markdown records are not PDF bytes.
- The four newly bound Murata documents and five Samsung documents are
  reference sheets; order-specific manufacturer approval and application
  qualification remain owed. Samsung CL10A475KO8NNNC is NRND in the captured
  product record. Kyocera 12105C106K4Z2A is identified as a historical PN;
  no alternate is substituted. Typical plots are not guaranteed capacitance.
- Nine exact Yageo generated sheets render and parse despite a nonfatal
  optional Suspects metadata warning; original bytes are retained. The exact
  FR zero-ohm identity is not changed to JR or treated as zero resistance at
  unrestricted current.
- `TMM-106-01-L-D` is an unshrouded header. Two exact Samtec
  `TCSD-06-D-04.50-01` socket-to-socket assemblies are selected, but miniDSP
  does not publish its module-header MPN. Module-side post fit, cable
  continuity/rotation, strain relief, labeling and simultaneous service remain
  first-article holds even though both official Samtec drawings are now local
  and SHA-bound.
- The project-local CS5308P, Molex 43650 and Coilcraft XGL4020 footprints
  require independent footprint/pin review on the realized board. A dossier
  binding is not that review.
- Diodes' non-Q and Q AP63205 evaluation boards use different inductances. The
  converter data-sheet table controls this design; the evaluation layout is
  retained only as topology precedent. The stocked XGL4020-332MEC uses the
  same exact land; its 3.3 uH value is separately admitted by the AP63205
  section-10 ripple/current calculation and remains a first-article test item.

The first-article status must remain **DO-NOT-ORDER** until these items and the
project assembly/sourcing rules close independently.


## Cat5e harness additions — 2026-09-12

Belden 7939A and 8503 have decoded, hash-bound manufacturer PDFs beside
their fact records. WAGO 221-415 currently has a retained manufacturer
product/family page-fact record; its standalone raw datasheet is not vendored.
The record supports the selected five-port join and conductor range only.
Obtain the exact installation/strip instructions and qualify the joins before
harness assembly acceptance. No resistance, weather seal or installed fit
claim follows from that page record. All three items are off-board harness
components, so they do not appear as placed parts in the PCB BOM/CPL.

## Weidmuller 8909650150 factory cord

Exact off-board service mate is source-owned. Manufacturer PDF was viewed through the browser but direct retrieval returned403; primary-source-record.md preserves facts and URLs, and native STEP is retained under03_src/lib/3dmodels/weidmueller. No local PDF hash is fabricated. Obtain the exact PDF or equivalent manufacturer qualification before bring-up. UV and installed cable/connector qualification remain owed, with no outdoor or order authorization.
