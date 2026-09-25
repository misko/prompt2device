# TI USB data ESD candidate reinstatement under initial stock lock

Crow returns `U_USB_ESD` to TI `TPD2EUSB30ADRTR` / JLC `C94934`
because D12 locks a selected part to its initial exact public stock screen.
The retained 2026-09-24T00:45:18Z direct public JLC receipt measured 307
units against the five-board plus-150 threshold of 155 and passed the full
88-line screen. The later 29-unit count is an inventory event, not an
electrical-source change. The receipt, raw capture and independent review
remain in `01_docs/research/2026-09-24-public-stock-569/`.

The source reuses the original three-pad TI DRT identity and the published
[TI TPD2EUSB30A datasheet](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf),
retained in `02_parts/TPD2EUSB30ADRTR/`. The selected source, floorplan,
route and RF port are restored to the exact pre-UV source revision. This
reinstatement is **not** independent electrical protection acceptance: the
XU316 powered/rail-off USB-pin transient envelope and exact-board clamp,
return and USB eye remain to be established. The previous 5UX and 3UV
files stay as historical substitution research, not current source.

The current generated circuit, native schematic, PDF and review checkpoint
have not been regenerated or accepted against this restored source. The
critical selection gate must continue to report INCOMPLETE until a separate
TI/XU suitability decision closes the tagged finding. No board release or
order claim follows from the initial stock lock.
