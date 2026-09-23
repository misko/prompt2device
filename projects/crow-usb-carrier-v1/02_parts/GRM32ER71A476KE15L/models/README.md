# Murata SimSurfing small-signal model captures

These are the model texts captured on 2026-09-23 from Murata SimSurfing (CRLF normalized to LF) for the base die `GRM32ER71A476KE15` at the stated temperature and DC bias. The exact selected `GRM32ER71A476KE15L` is the L reel-packaging code for that die. Source viewer: https://ds.murata.com/simsurfing/mlcc.html?oripartnumbers=%5B%22GRM32ER71A476KE15L%22%5D&partnumbers=%5B%22GRM32ER71A476KE15%22%5D. The files are *typical simulation models*, applicable to small-signal conditions over the stated model frequency range. They do not specify production min/max effective capacitance, ESR, or ESL. No physical-network ESL or regulator stability pass follows from them.

The files cover -55 C at 0.92, 1.818, 3.38, 5.05 and 5.099 V and 125 C at 3.38 V. The -55 C 5.099 V case explicitly screens the possible TPSM replacement's upper output limit. Verify each file SHA-256 using `sha256sum *.txt`; only CRLF line endings were normalized to LF; model coefficients and comments are unchanged. Independent review accepted model/reserve applicability for the source E-CAP engineering screen (`/tmp/crow-capbank-review-adjudication.md`, SHA-256 `de07b6ff59a6c68f3ca26b4fee823acfc760dd76d2fee0c96666ee4dd717afcf`). Production lot behavior remains unqualified and belongs to production/first-article qualification.

## Retained model SHA-256

These hashes identify the normalized model files committed with this source.

| File | SHA-256 |
|---|---|
| `netlist-0.92V--55C.txt` | `9d5dc68f1f6b4e7685de02b7731feaa18c7bb13553242758c71d701f2e0c1973` |
| `netlist-1.818V--55C.txt` | `41447ab648ccb51be9faf02581da05c2ace513df8fe47a60cac3d57011add72e` |
| `netlist-3.38V--55C.txt` | `3d316824d3bae294ac81bfa7b97f888c201f1a373ca6d602d11e58003ae2554d` |
| `netlist-3.38V-125C.txt` | `e10929b05701f9b73033c19635128fe7b4e069c18dd5a7727a0b28e7d1715ebc` |
| `netlist-5.05V--55C.txt` | `04e9de2fe00d633ccb9f71fac505819fa1fe222fdd8c4d8ccaecea99d276f699` |
| `netlist-5.099V--55C.txt` | `c0ab173508cb7e73350e07c45a517b51d0a0eaf86080f1e8b061cba8bcb9e987` |
