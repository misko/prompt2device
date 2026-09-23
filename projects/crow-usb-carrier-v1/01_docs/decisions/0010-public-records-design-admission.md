---
id: 0010
date: 2026-09-23
status: accepted
---
# 0010 — Public records for Crow design admission

## Context

The design reached a pre-layout sourcing checkpoint that required a signed-in JLC BOM response. The user directs:

> Please only use public records and jlcsearch

## Options

- Authenticated JLC BOM matching before placement: not used under D11.
- Public records and jlcsearch with explicit design-only admission: selected. Public observations can screen exact parts and stock without proving supplier allocation or assembly acceptance.

## Decision

Use the existing public-catalog pre-layout admission path for Crow. Public exact-code observations remain the stock authority; jlcsearch remains a discovery and corroboration tool, not an authenticated assembly receipt. No login, account-specific inventory, private records, uploads, supplier messages or purchases are part of this workflow.

Preserve the five-board build, 150-unit surplus for each exact coded part except the D10 XMOS-only zero-surplus exception, and exactly24 D9 manual through-hole references. Missing, stale, mismatched or insufficient public evidence must fail the design screen; this is not a stock-shortage waiver.

## Consequences

A public screen permits schematic review, block placement and subsequent design work, subject to all existing engineering gates. It does not prove actual allocation, assembly attrition/minimum quantities, prices or fees. Procurement exposure is deferred rather than measured as zero. Keep DO-NOT-ORDER and ASSEMBLY FULFILLMENT: ORDER-TIME CHECK explicit in any eventual release; no order-ready claim follows from this decision. Do not request authenticated evidence as a prerequisite to the current design workflow. Any future ordering action is a separate user task.
