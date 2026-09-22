# Independent five-capacitor implementation review

Verdict: **ACCEPT**

Reviewed exact commit `25f30eee58e5dc3ed50609c371f2f4a4df5595f8`
against baseline `72efaaefe2145814d029dc2e8a56615fbfbafce0`.

The five-reference source change is coherent:

- `C_USB_VBUS`, `C_LDO_A`, and `C_LDO_D` select exact
  `GCM21BR71C475KA73L`, JLC `C90791`, 4.7 uF, 16 V X7R, standard 0805.
- `C_VMID1_4U7` and `C_VMID2_4U7` select the already qualified exact
  `C0805C106K8RACTU`, JLC `C2167576`, 10 uF, 10 V X7R, standard 0805.
- All five source footprints, exact-parts rows, dossiers, and values agree.
  No electrical net or endpoint changes are introduced. The two retained VMID
  reference names remain historical refdes while their source values are now
  correctly 10 uF.

The conservative screens now compare directly with the manufacturer circuits
and include a separate 10% lifecycle reserve:

- USB VBUS: 1.164942 uF versus the XU316 1 uF minimum; no-bias high corner
  5.9455 uF versus the 10 uF maximum.
- LDO_A and LDO_D: separate banks, each 1.553256 uF versus the 1 uF capacitor
  shown at its own CS5308P filter pin.
- ADC_VMID1 and ADC_VMID2: separate banks, each 3.4425 uF versus the 2.2 uF
  bulk bypass shown at its own CS5308P VMID pin.

The per-pin banks prevent one electrically separate capacitor from hiding a
shortfall at another. Murata curves remain correctly labeled typical and the
multiplicative figures remain engineering screens rather than manufacturer
guarantees. Reference settling/ripple/THD, USB behavior, and the larger 0805
placement/escape geometry remain explicit first-article or native-layout
obligations.

Sourcing evidence retains two exact GCM pools (JLC stock 40,697 and DigiKey
stock 254,233 for a 15-piece five-board need). The pre-existing KEMET dossier
and exact JLC identity are preserved for the VMID parts.

Validation:

- `git diff HEAD^ HEAD --check`: pass.
- `early_design_check.py ... --capacitance`: pass, 15/15 displayed banks,
  including the five new independent rows.
- `contracts_audit.py --walk`: pass, 422 files and zero violations. The exact
  child contract authorizes only the three retained evidence JSON files.
- Worktree clean at the reviewed commit.

Selected exact artifact hashes:

- `power_tree.yaml`: `9f6366b6ee2eacac66d8c51c1ae81fd93af06f5aff787b089e24d3c4aaf5abb3`
- analog source: `398bdbb4381f02ab3156f5b91ed06996a4a9bb2dc2a901c29e669aaec76f6823`
- USB source: `1febdc6bedcae39fcab97a97a94c83b34993b8ba5b71bac746d24807b231fbae`
- GCM dossier: `8e3cc0a37a5da9b887d2974983d5d16e6ebbdaa22d47789915c778a173ada79b`
- KEMET dossier: `d5aca61386e367f084c1d3241f2d4e1b3307d0722a3a523dba83dcc46325fd87`
- evidence child contract: `17737768697cc4e1711c8123e06166d8869a18f963a0d527f5c634339a27a48d`

This accepts the source selection and engineering screen, not native placement,
routing, assembly allocation, or first-article performance.
