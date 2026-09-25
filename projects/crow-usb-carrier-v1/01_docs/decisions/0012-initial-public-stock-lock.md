---
id: 0012
date: 2026-09-24
status: accepted
---
# 0012 — Lock Crow part selection to the initial public stock screen

## Direction

> once we do the stock check at the start lets not worry about it again. its locked in

## Decision

For Crow, screen each exact JLC-coded SMD part once at part selection against
the five-board quantity and the D7 150-extra-unit public-stock reserve (with
the existing exact XMOS exception). Bind that dated public result and exact
MPN/LCSC to the selected source. Later changes to public catalog counts do
not reopen an otherwise unchanged part selection or trigger a redesign.

For `U_USB_ESD`, the original TI `TPD2EUSB30ADRTR` / `C94934` met the rule:
the retained direct public JLC screen at 2026-09-24T00:45:18Z observed
307 units against 155 required. Its complete 88-line `public-stock.json`
has SHA-256 `aa9491bf6df447b646bb6985921cf489ed07c3d01893f2fd2829b13759acf142`.
The [independent public-record review](../research/2026-09-24-public-stock-569/terra-authoritative-public-review.md)
bound its raw responses and calculation. The later observation of 29 units
does not invalidate that selection screen. The earlier jlcsearch count of
5,439 disagreed with direct JLC observations and is not the lock authority.

## Boundaries

This locks a **design selection decision**, not physical inventory. The
initial count is not a reservation, and JLC may be unable to populate the
part when an order is eventually attempted. That is an order-fulfillment
issue, not an instruction to change the circuit every time stock moves.
No order, payment, allocation claim or stock-based substitution follows from
this decision. Electrical suitability, connector/route quality and physical
release gates still require their own evidence. A new MPN/LCSC or quantity
change needs a new initial screen for that new selection.
