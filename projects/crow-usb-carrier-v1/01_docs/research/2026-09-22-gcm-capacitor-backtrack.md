# 0805 capacitor sourcing backtrack

The five references formerly fitted with `GRM188Z71C475KE21D` retain their nets and two-terminal topology but move to 0805 footprints. `C_USB_VBUS`, `C_LDO_A`, and `C_LDO_D` use exact active Murata `GCM21BR71C475KA73L` / LCSC `C90791`. Fresh 2026-09-22 evidence records 40,697 JLC catalog units and 254,233 DigiKey cut-tape units for a five-board need of 15. Murata PIM binds the exact L packaging MPN to the primary 0805/X7R/4.7uF/16V family and its typical DC-bias and AC-amplitude curves.

The first review rejected that 4.7uF candidate at the two ADC_VMID bulk references: the conservative 3.6V screen retained only 1.553uF per part after the lifecycle reserve, below the 2.2uF capacitor shown at each ADC_VMID pin in Cirrus DS1314F1 Figure 2-1. Those two references therefore use the project's already-qualified exact `C0805C106K8RACTU` 10uF X7R 0805 part. Its existing 50% voltage, 10% tolerance, 15% temperature, and 10% lifecycle screen retains 3.4425uF per part, 56.5% above 2.2uF. The parallel 470nF parts remain unchanged.

The new power-tree checks make all affected capacitance obligations explicit:

- USB VBUS: 1.164942uF estimated minimum against 1uF, 16.5% margin; 5.9455uF high corner remains below 10uF.
- LDO_A and LDO_D: 1.553256uF each against the Cirrus shown 1uF, 55.3% margin.
- ADC_VMID1 and ADC_VMID2 bulk: 3.4425uF each against the Cirrus shown 2.2uF, 56.5% margin.

These are conservative engineering screens from typical curves and explicit reserves, not production guarantees. Product approval, native 0805 land/placement review, effective-capacitance measurement, reference ripple/settling/THD, and the normal order-time uploader allocation check remain required.
