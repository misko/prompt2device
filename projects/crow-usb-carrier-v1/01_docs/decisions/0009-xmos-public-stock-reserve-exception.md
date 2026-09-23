---
id: 0009
date: 2026-09-23
status: accepted
---
# 0009 — XMOS-only public-stock reserve exception

## Context

D5 requires JLCPCB to stock and populate every non-through-hole component. D7 requires five board sets plus150 extra publicly stocked units per exact part. That reserve prevented admission of the selected XMOS controller. The user now directs:

> lets make an exception for xmos and keep going

## Decision

For XMOS XU316-1024-TQ128-C24, JLC C6362698, reference U_XU only, use a public-stock surplus of zero instead of150. Aggregate the actual per-board quantity and multiply by the unchanged five-board build quantity. All other parts retain the150-unit surplus. JLC stock and population remain mandatory for XMOS; D9 still permits manual assembly of the24 specified through-hole parts.

## Consequences

Refresh exact identity and stock, encode this exact-part exception in the owning assembly policy and downstream stock consumers, and independently regrade sourcing before admission. Preserve dated prior shortage observations as history. The exception authorizes continuation of engineering, not purchasing, firmware, supplier communication, private-stock substitution or reduced JLC assembly attrition. Actual allocation, attrition/minimum quantities and process acceptance remain order-stage obligations. A different XMOS ordering code or substituted controller requires renewed policy matching rather than inheriting this exception.
