# contract: sourcing/evidence/

Purpose: retained primary manufacturer lifecycle pages, bound by URL, exact MPN, capture date and SHA-256 in manual_quotes.yaml. These are dated observations, not present availability or purchase authority.

## Allowed

| Pattern | Content | Rule |
|---|---|---|
| `*-ti.html` | Authentic TI response bytes | Preserve bytes and URL/date/identity/hash provenance. Superseding observations use a new filename. |
| `contracts.md` | This contract | No stock inference or order authority. |

Stock remains distributor-owned and cannot be inferred from these pages.
