# ADR-0013 — Factory RJ45 analog/power spokes

Status: proposed integration under the user-approved RJ45 direction. Date:2026-09-12.

Supersedes the spoke termination selections in0011/0012; external roof-appliance Ethernet/PoE remains separate. Use exact Würth615008160221 nonmagnetic shielded8P8C jacks and Weidmüller8909650150 factory15m Cat6A S/FTP PUR cords. No field cutting, crimping, splices or WAGO/pigtail joins. The synchronized spoke_interface.yaml owns pin and pair allocation:5 AUDIO+,4 AUDIO−,1/3/7+12V,2/6/8return. Label every spoke port POD AUDIO+12V / NOT ETHERNET OR POE; poweroff mating only.

Carrier shell tabs9/10 form CHASSIS and require a proved panel bond. Pod shell tabs form isolated POD_SHIELD with no signal-ground connection. Plugs remain inside dry protected enclosures; cable glands, seal, restraint and all-connected service remain qualification obligations.

At15m, published290ohm/km pairloop, three parallel power pairs,1.25hot multiplier and unmeasured0.300ohm contactallocation yield2.1125ohm and10.58875V at100mA from10.8V. Original2.2ohm/10.5V/current/analog limits are unchanged. Exact installed length, transient contact behavior and finished cord qualification remain owed.

Manufacturer native model and independent containment establish nominal mate/grip geometry; installed tolerances and physical service remain unknown. UV resistance is not established: exact manufacturer/environmental qualification is required before outdoor deployment. Carrier ADR0007 governs its prototype timing; pod ADR0005 preserves only explicitly labeled first-article/nonorderable candidate scope and must be honored by its own conductor. No release, purchase or outdoor production authorization is created here.

## Source adoption follow-through — 2026-09-12

The independently accepted 95-file source was adopted at commit8a2d3620,
as recorded in the carrier schematic journal at20:08 UTC. The initial
proposed/pending wording above is the original handback. Exact native
schematic review and subsequent PCB/routing/release gates remain separate;
no stale generated board or prior sealed release gains acceptance here.
