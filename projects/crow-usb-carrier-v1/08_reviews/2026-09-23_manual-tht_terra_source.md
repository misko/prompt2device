# D9 manual-THT source review

Read-only review of the uncommitted authoritative worktree state, 2026-09-23.

## Result: PASS for the requested source-policy scope

The D9 edit has exactly the requested manual-THT population set and does not
introduce an SMD or J_PWR exemption. It is a source policy/result only. No
native PCB exists for this changed source, so this review makes no A-POP,
CPL-output, placement, or JLC process acceptance claim.

## Exact membership and policy

A YAML parse of 03_src/rules/assembly.yaml found exactly two not_assembled
entries, 24 unique references, no duplicates, and an exact match to:
J1-J8 plus C_A1N/C_A1P through C_A8N/C_A8P.

| Entry | Refs | reason | on_bom | retained historical code |
|---|---:|---|---|---|
| J1-J8 | 8 | user_supplied | false | C6461980 |
| C_A1N/P through C_A8N/P | 16 | user_supplied | false | C3778009 |

Evidence:
- assembly.yaml lines 132-176 provides the two exact entries, the manual
  disposition, and retains each MPN/code identity in its evidence.
- build_quantity 5 and public_stock_surplus 150 remain unchanged at
  assembly.yaml lines 44-45.
- board_attr_plan remains empty at lines 194-195. U_ADC is expressly retained
  on the JLC placement list there; no SMD exclusion was found.

## Position-file and source identity checks

A floorplan YAML parse found one exclude_from_pos_files pattern with exactly
the same 24-reference set: no missing and no extra references. The authored
list is floorplan.yaml lines 148-174.

The circuit source retains the exact components and MPNs while removing their
JLC supplier identity:
- crow_retained_analog.tsx lines 87-88: each J1-J8 remains
  manufacturerPartNumber 615008160221 with jlc empty.
- lines 109-110: each C_A[n]P/N remains MPN R82DC4100CK60J with jlc empty.
- exact-parts.csv retains both selected MPNs and complete reference groups,
  but has blank LCSC fields.
- J_PWR remains a selected, coded line: exact-parts.csv has
  43650-0200, J_PWR, LCSC C192562. It is absent from both D9
  not_assembled entries and the floorplan exclusion pattern.

Thus the manual parts stay in the circuit/full fitted population, but are
removed from JLC source/BOM/CPL inputs as D9 requests. No SMD reference occurs
in the exact manual sets.

## D7 quantity and dated external-source evidence

The reserve arithmetic remains five boards plus 150 per exact line:
- connectors: 8 per board, 40 build, threshold 190.
- film capacitors: 16 per board, 80 build, threshold 230.

The newly added dated record
01_docs/sourcing/tht-manual-source-2026-09-23.md lines 1-50 states:
- exact 615008160221: DigiKey observation 991, clearing 190 by 801;
- exact R82DC4100CK60J: DigiKey observation 969, clearing 230 by 739;
- direct LCSC observations remain 0 and 6 respectively, and do not claim JLC
  allocation.

Assembly evidence lines 145-148 and 171-174 reproduces the corresponding
991/190 and 969/230 statements. The record limits the conclusion to possible
manual-THT sourceability and retains an order-time refresh requirement.

## Boundary

The changed worktree has other unrelated uncommitted ADC/research work, and
BRIEF now reports a larger current source count. This review only verifies D9's
manual-THT change. The root diagnostic circuit, when generated, must verify the
actual emitted supplier records; this source-only review cannot substitute for
that receipt. Native PCB/CPL artifacts are absent and remain unaccepted.

