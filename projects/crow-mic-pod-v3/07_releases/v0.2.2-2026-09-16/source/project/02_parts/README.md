# Exact-part evidence

These dossiers bind the first-article source to exact manufacturer identities,
pin maps, packages and critical limits. Every retained PDF is an actual PDF
payload (not HTML or a transfer-compression wrapper), and every retained byte
set is named and SHA-256-bound by its matching `part.yaml`.

The 2026-09-02 source-closure pass added exact Bel, Samsung, Yageo and Vishay
manufacturer PDFs, retained the previously captured exact Littelfuse sheet,
and corrected the Belden 6541PA file from a gzip transfer wrapper to the exact
decoded PDF payload. It also corrected the OPA1679 document identity from the
wrong `SBOS618` label to the actual pinned `SBOS855E` bytes. The three
previously weak TI multi-pin dossiers now cite their exact pin figure/table and
PDF page.

The following 12 byte authorities remain explicitly **OWED**:

- UNI-ROYAL series sheets for `0402WGF1000TCE`, `0402WGF1003TCE`,
  `0402WGF1802TCE`, `0402WGF2201TCE`, `0402WGF2202TCE`, and
  `0805W8F3901T5E`;
- official Molex PDF bytes for `43030-0007`, `43645-0400`, and `43650-0400`
  (the inspected facts are retained in each `primary-source-record.md`);
- the exact Yageo PDF for `CC0402KRX7R9BB104`; and
- the exact Murata PDF bytes for `GRM32ER61A107ME20L` and
  `GRM32ER71H106KA12L` (the official indexed document identities and revision
  dates are retained, but the direct manufacturer byte URLs did not return a
  PDF during this pass).

No digest is asserted for any of those 12 dossiers. This remains a hard release
block; catalog facts and web-rendered records are not substitutes for the owed
manufacturer bytes.

Passives are frozen by exact MPN and LCSC code. Their series-document identity
does not prove order-time stock. All catalog availability remains volatile and
must be revalidated through the governed JLCPCB flow.

`AOM-5024L-HD-R` is not mounted directly. Its official drawing omits terminal
pitch, so the board provides a separate project-owned two-wire landing and the
capsule/harness are manual first-article operations.


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
