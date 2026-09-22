# W25Q128JWSIQ boot-memory adoption

Replaced unavailable IS25WP032D-JBLE at U_FLASH with exact Winbond W25Q128JWSIQ, 128 Mbit (16 MiB), 1.7–1.95 V, industrial SOIC-8 208 mil, with factory-fixed QE. The source pin connections and native footprint remain unchanged. The manufacturer Rev H datasheet is retained in the new dossier and its hash independently checked.

The older XU316 datasheet describes one dummy byte after the address, which initially raised an independent review concern. [XMOS XTC Tools](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tools-ref/libraries/libquadflash-included-devices/libquadflash-devices.html) explicitly specifies six post-address clocks for boot. Winbond consumes two mode clocks and four dummy clocks, then supplies data. XMOS verifies identically framed Winbond JV devices; this closes the source-protocol concern. Exact-part programmed boot is a first-article test, not an executed result. The [XMOS hardware guide](https://www.xmos.com/documentation/XM-014926-PC/html/modules/qspi_fast_read/doc/programming_guide/hardware_selection.html) independently specifies three address bytes and six cycles. Flash read-ready tVSL is at most 20 µs against the controller’s 300 µs allowance.

Root omitted the proposed unconsumed power-tree identity block and four unsupported dossier assertion types. Primary facts and the reviewed hardware/software contract own the boot compatibility evidence. The sourcing tool now normalizes the exact distributor spellings Winbond Elec and Winbond Electronics; it still rejects neighboring MPNs and unrelated manufacturer names. Its regression suite passes 27 tests, including 14 known-bad fixtures.

A root-run single-part Q-2SOURCE gate using the adopted dossier and current U_FLASH BOM row passes two authorized pools for five boards. This result covers only U_FLASH. It does not qualify the full carrier BOM, allocation, purchasing or fabrication. Dated distributor observations and machine-report provenance are recorded separately in the sourcing selection record.

Fresh electrical expansion: 485 components, 85 selected MPNs, 1615 ports, 1488 traces, zero source errors and 26 critical endpoint assertions. This is source evidence; native schematic, routing, full sourcing and physical verification remain open.

The source policy reader reports P-LAYOUT/P-PREC PASS, with one explicitly owed TPD2EUSB30ADRTR precedent record under its current non-ratcheted board ceiling. This does not close that unrelated evidence debt or imply complete layout review.
