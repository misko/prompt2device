# Flash parts selection — 2026-09-22

These dated distributor observations go stale and are not present availability, reservation or purchase authority. They qualify the stated candidate only; re-read on order day.

Candidate: W25Q128JWSIQ, Winbond Electronics, U_FLASH, one per board, five boards. Exact dossier and candidate identity live in `02_parts/W25Q128JWSIQ/part.yaml` and `01_docs/sourcing/exact-parts.csv`.

- DigiKey exact product-page observation: [W25Q128JWSIQ](https://www.digikey.com/en/products/detail/winbond-electronics/W25Q128JWSIQ/12090690), read2026-09-22, exact Active Tube identity256-W25Q128JWSIQ-ND,809 in stock, min/multiple1. Grade: product-page observation, not allocation. Root independently reopened the exact page and confirmed the identity/Active/stock fields. Mutable quote input retains the read timestamp.
- JLC/LCSC [exact catalog identity](https://jlcpcb.com/partdetail/WinbondElec-W25Q128JWSIQ/C2763561), owning catalog checker: exactC2763561/W25Q128JWSIQ/Winbond Elec, generated2026-09-22T10:50:00Z, stock436 versus five needed. Grade: owning catalog observation; explicitly not JLC assembly allocation. Raw sidecar: `06_build/cache/flash-selection-20260922/jlc-stock-live.json`.

Root machine result: `06_build/verification/flash-selection-current/shopping-list.json`, COMPOSED-POOLS PASS,1/1 exact part meets two pools (JLC and DigiKey). Input candidate is extracted from the current full candidate BOM; all other parts are outside this single-part result. Mouser/Amazon missing evidence remains reported and does not substitute a pool. Full-carrier Q-2SOURCE remains incomplete.
