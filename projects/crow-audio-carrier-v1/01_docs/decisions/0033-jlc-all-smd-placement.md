---
id: 0033
date: 2026-09-16
status: accepted
---
# 0033 — Require JLC placement of every carrier SMD part

## Context

The five-board first-article package excluded six top-side SMD references from
the JLC BOM/CPL: U_ADC, F_IN, C_FILT1_470U, C_FILT2_470U, C_HOLD1 and C_HOLD2.
The user can hand-solder the 27 through-hole references but does not want any
manual SMD placement or reflow. The existing geometry and top-side population
already support factory placement.

## Options

- **Retain the six manual SMD references** — rejected because U_ADC requires
  qualified QFN exposed-pad reflow and the result would violate the user's
  no-manual-SMD requirement.
- **Ask JLC to place the six parts without source identities** — rejected
  because an uncoded CPL line or prose-only request is not reproducible and
  can be silently unmatched by the uploader.
- **Bind the exact public catalog identities and require allocation or exact
  consignment** — selected. This preserves the electrical design and makes
  the BOM/CPL the assembly authority.

## Decision

JLC shall place all 306 fitted SMD references on the carrier top side. Bind
F_IN to exact Littelfuse 2920L260/33DR / C22870534, bind all four polarized
bulk capacitors to exact Panasonic EEEFK1A471P / C178530, and bind U_ADC to
C42457798 only when the resolved uploader row confirms Cirrus CS5308P-DN as
identified by DS1314F1 Table 12-1. If that exact ADC resolution is unavailable,
consign exact CS5308P-DN for JLC placement. Do not accept electrical or package
substitutions. The 27 fitted THT references remain a separate user-installed
work package.

## Consequences

Regenerate the source circuit, native board, BOM, CPL, assembly coverage,
rotation and polarity evidence, twin and immutable release. The CPL population
must increase from 300 to 306 and the declared not-assembled set must decrease
from 33 to the 27 THT references. Uploader allocation, exact resolved-part
echo, rotation/polarity preview and ADC exposed-pad process confirmation remain
order-time gates. No schematic connectivity, placement coordinate, routing,
Gerber copper or THT identity is intentionally changed.
