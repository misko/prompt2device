# DLC USB / external-source fault bridge re-review

## Engineering disposition: PASS — source-digest update justified

I reverified the current candidate SHA-256 as `416d4f78a8ae2e7040c51194d97dee7af424580e4acf8dc0e36d9c7b975a20da` and the preserved baseline as `cf78dcb8d8c1fc7f696d6f5eaad20a0175c6b27ae0c193d6e1b67bb8937e9193`. The current fault contract still binds the latter, so updating only `external_source_fuse.circuit_sha256` to the candidate is justified.

The independent source comparison remains unchanged: both circuits have 568 components, 282 identical source-net records, and identical internal connections. The exactly eleven identity changes are the three TPS62822 regulators, six input capacitors, one 3V3X feedback resistor, and `J_USB`. Only the three regulator port maps change: the documented TPS62822 pin mapping retains EN/FB/AGND/NC/PGND/SW/VIN/PG as 1/2/3/4/5/6/7/8, with FB/SW/VIN on their prior electrical nets, both grounds on GND, and NC/unused PG open. No bound source/fuse/PFET/spoke reference changes; the external input path and the XMOS ports are unchanged. USB retains its existing separate VBUS-sense, CC, DP/DM, ground, and open-SBU source connections.

The conditional source contract remains an obligation, not a waiver: 2.185 A one-fault delivery; 3.4 A instantaneous fault-episode peak; at most 10 ms cumulative above 2.85 A; then 2.85 A or off until the specified rearm. Supply/cable load-line and discharge/retry measurements, hot fuse/PFET behavior, aggregate fault/startup behavior, USB physical qualification, and all PCB/first-article/release holds remain open. No repin, source/PCB edit, ordering, or board acceptance follows.
