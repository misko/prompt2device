# crow-roof-array-v1 — architecture checkpoint

The Raspberry Pi 5 compute/network boundary and the two-board custom-hardware
partition are adopted. This parent remains held at `PCB-COMMISSION` because it
owns the unproved whole-appliance boundary; the carrier and pod are developed
as separately governed PCB projects. This file keeps accepted system facts,
child-board contracts and still-owed physical evidence distinct so later work
does not accidentally promote archived boards or scaffold examples.
Rationale and alternatives are in the
[architecture study](reports/2026-09-01-star-array-architecture-study.md), the
[dimensionality/identity/PoE addendum](reports/2026-09-01-dimensionality-identity-and-poe-addendum.md),
[planar 8 m-diameter follow-up](reports/2026-09-01-planar-8m-diameter-120s-follow-up.md),
and the decision records in [`decisions/`](decisions/). ADR 0006 supersedes
the earlier neutral noncoplanar count study in ADR 0002; ADR 0007 supersedes
the cross-recording biological-identity proposal in ADR 0004. Accepted
[ADR 0005](decisions/0005-poe-ethernet-roof-appliance.md) and
[ADR 0008](decisions/0008-raspberry-pi-5-roof-appliance-host.md) own the
external network boundary and Pi 5 platform choice. [ADR 0009](decisions/0009-split-system-into-two-single-board-releases.md)
owns the two-board partition, and [ADR 0010](decisions/0010-single-cs5308p-audio-carrier.md)
selects the eight-channel ADC/MCHStreamer boundary. [ADR 0013](decisions/0013-factory-rj45-pod-spokes.md) supersedes the
spoke connector/cable choices in ADR0011/0012 with the factory RJ45 source.
Installed dry-zone entry, restraint and enclosure qualification remain owed.

## Accepted system boundary and child-board audio path

```text
weatherized analog microphone pods at surveyed coordinates
  -> one shielded balanced-audio/power home run per pod
  -> protected simultaneous-ADC carrier on one local clock
  -> unchanged vendor USB Audio Class 2 module
  -> short internal USB link to Raspberry Pi 5 Model B
  -> one standards-compliant Cat6 PoE/Ethernet building uplink
  -> server storage plus localization/tracking/filtering
```

The Pi 5, wired-Ethernet and short-internal-USB boundary is accepted. The
carrier uses one hardware-controlled CS5308P and MCHStreamer TDM8; their exact
assembly, vendor-image and first-article interoperability evidence remain
owed. The pod implementation is owned by its child PCB project; the PD,
storage and enclosure selections remain proposed or owed.
The Pi records, checksums, buffers and uploads; the server is the preferred v1
location for planar tracking and within-file caller labelling. The complete
integration evidence and open part choices are in the
[Pi 5 report](reports/2026-09-01-raspberry-pi-5-roof-appliance-integration.md).

The electrical wiring forms a physical star; the acoustic sample positions
need not form a perfect geometric star. [ADR 0006](decisions/0006-planar-signature-versus-3d.md)
records the active v1 target: eight
planar channels—seven mildly irregular perimeter points around a nominal 4 m
radius and one center reference. It supports a planar position signature,
source grouping and single-active-caller focusing, but no robust elevation or
3D claim. Four-outer/four-inner is the multiscale comparison; noncoplanar
8/12/16-channel layouts are reopened only if elevation or overlap separation
becomes required. Channel count and roles are locked; exact coordinates remain
blocked by the roof survey and BRIEF Q1/Q2/Q5.

## Power tree

The external source type is locked as genuine standards-compliant
PoE/Ethernet. The exact PSE/PD type and appliance rail implementation are not
locked. The carrier/pod interface is locked at 12 V nominal at the carrier
header, with independently protected spokes and quiet local 5 V regulation in
each pod. The candidate appliance uses an isolated PD or splitter, then
separately filtered compute/digital and quiet audio/pod rails. Raspberry Pi 5's
USB-C power advertisement and peripheral-current mode must be proved with the
exact PD; nominal wattage alone is insufficient. Voltage/current envelopes,
cable drop, conversion loss, thermal derating, entry protection, auxiliary
loads and off-state current remain commission facts OWED by Q3/Q6. No net
names are authoritative until `power_tree.yaml` replaces its scaffold.

## Net domains

The domain classes are locked: balanced low-level audio, MCLK/BCLK/FSYNC inside
the roof appliance, protected 12 V analog-spoke power, internal USB, genuine
PoE/Ethernet, chassis/shield, and circuit ground. Exact rail implementation
remains child/system work. Cable shields bond to chassis at the carrier entry
and connect to an isolated POD_SHIELD island at the pod; the exact chassis-to-circuit-ground network
must be selected with entry protection and cannot be inferred from archived
designs.

## Stackup

The pod and central carrier are separately commissioned board roles and may
use different stackups. Their child release projects own exact layer counts,
impedance and fabrication options; this system parent does not duplicate them.

## Ground strategy

Cable shields terminate to chassis at the carrier enclosure entry and remain
on an isolated POD_SHIELD island at each pod, separate from circuit GND. Exact entry bonding, chassis-to-circuit coupling and the
roof-appliance USB return require reviewed system-level implementation. A PCB
ground plane does not constitute a lightning or building-entry bond.

## Critical geometries

- Surveyed microphone membrane coordinates and height, not enclosure centers.
- A future surveyed roof polygon capable of admitting the 8 m-diameter study,
  including keep-outs, drainage paths, roof access and approximately 28 m
  minimum nominal perimeter-spoke cabling.
- Connector mate/grip/bend/service volumes at every pod and the roof appliance.
- Short, symmetric analog input paths and continuous return at each central ADC.
- One shared low-jitter MCLK/BCLK/FSYNC distribution inside the roof appliance.
- One sealed internal USB mate/service cell between audio module and SBC.
- One genuine PoE/Ethernet building-entry connector/PD/surge/bond boundary.
- Roof windscreen, drainage, boundary reflection and structure-borne vibration.

Every item remains unbound until the remaining BRIEF fact locks and the
external-hardware records close.

## Interfaces

Each distinct successor interface must have its own compiled contract checked
at every represented end. The archived custom-RJ45 boards are references only:
their power contacts conflict across the pod and central board, so a
straight-through cable is destructive. The new board-to-cable boundary is
fixed by [`../03_src/rules/spoke_interface.yaml`](../03_src/rules/spoke_interface.yaml):
The adopted source uses Würth 615008160221 nonmagnetic shielded 8P8C
jacks and complete Weidmüller 8909650150 factory 15 m Cat6A S/FTP PUR cords.
Pins 1/3/7 carry +12 V, 2/6/8 return, 5 AUDIO+ and 4 AUDIO−. Shell pads
9/10 join carrier CHASSIS or pod POD_SHIELD; neither net connects to circuit
GND. The pod shield island is isolated from circuit ground, not disconnected
from the cord shield. These ports carry custom analog audio and power;
label them “POD AUDIO +12V / NOT ETHERNET OR POE” and mate with power off.
No field crimps, splices or pigtails belong to this spoke assembly.

Exact manufacturer STEP establishes a nominal complete plug end of
57.98 × 13.70 × 18.456687 mm and a 22.986 mm nominal grip diameter.
These are nominal CAD envelopes, not manufacturing or installed-service
limits. Cable OD is 6.1–6.5 mm; retain the 67 mm bend planning floor.
The three parallel power pairs give the conditional hot-loop screen
`290 Ω/km × 0.015 km / 3 × 1.25 + 0.300 Ω = 2.1125 Ω`, hence
10.58875 V at 0.10 A from 10.8 V. Contact allowance, finished-loop resistance,
power sharing, fault behavior, mating/service and environmental performance
remain measured obligations. UV is unestablished; PUR alone is not evidence.
The source adoption is recorded in the carrier schematic journal at
2026-09-12 20:08 UTC. Native review, routing and release are separate gates.

`check_spoke_interface.py` requires agreement at the parent, carrier and pod.
Installed cable length, dry-zone entry, strain relief, chassis bond and full
service envelope remain enclosure/system obligations.

Protection is two-tier: carrier `1812L035/60MR` covers cable/pre-pod
faults; pod `0ZCJ0010FF2E` covers downstream-board faults. The carrier
0.70 A trip specification is a thermal PPTC characteristic, not a precision
current limit. Würth specifies 1.5 A per jack contact; the factory cord uses
26 AWG stranded conductors in three parallel positive/return pairs. Normal
0.10 A branch current would divide to about 33.3 mA per power contact with
equal paths. Neither equal sharing nor cable/plug fault ampacity is established
by those figures, and three contacts do not automatically triple the rating.
Do not inherit the former 22 AWG cable or Micro-Fit current ratings.
The COTS source's prospective short current must remain within the branch
PPTC's 10 A fault rating. Its 0.15 s trip point at 8 A does not authorize an
8 A installed-cord test. Hot resistance, source foldback, trip energy,
selectivity and one-fault/seven-healthy recovery remain first-article holds.

The separate building uplink is genuine standards-compliant PoE/Ethernet.
It also uses RJ45/Cat6 hardware, so physical connector compatibility cannot
identify the electrical function. Never connect a pod port to networking or
PoE equipment. Keep the two port groups clearly marked and separated.
PoE/Ethernet, internal USB and the MCHStreamer interfaces each retain their
own compiled contracts at every represented end.

## Audio and network timing boundary

All eight CS5308P channels sample from one local audio clock before any packet
is formed. Ethernet packet arrival time is not an acoustic timestamp and must
not be used for TDOA. The selected carrier uses one CS5308P in hardware
secondary TDM minimum-slot mode. MCHStreamer TDM8 supplies synchronized
24.576 MHz MCLK, 12.288 MHz BCLK and 48 kHz FSYNC; one CS5308P DOUT carries
eight 32-bit slots. MCHStreamer documents its input as 24-bit, so exact bit
selection, data edge, channel order and sign interpretation remain bench
obligations. No 12/16-channel compatibility claim is made for v1.

The host must open the frozen ALSA `hw:` endpoint directly and retain one PCM
stream across each set of 120-second segments. Any USB/PCM reset starts a new
stream epoch; no writer may pad or stitch around a reset. Exact frame counts
and xrun logs are necessary but not sufficient: a deterministic frame-coded
stimulus and simultaneous analog impulses must prove slot order, common-frame
continuity and stable relative ADC delay/phase across reboot, reset and thermal
corners. Noise, SNR, crosstalk and coherent spurs must also be checked while the
fan, NVMe, CPU and Ethernet are active.

At 48 ksample/s, the eight-channel raw 24-bit payload is 9.216 Mbit/s; 32-bit
PCM containers use 12.288 Mbit/s. One ordinary 100BASE-T uplink has capacity,
while Gigabit Ethernet is preferred for operational margin. These arithmetic
rates do not include packet overhead and are not measured throughput.

For the leading eight-channel branch, one 120-second recording contains
5,760,000 samples per channel and about 184.32 MB of sample payload in 32-bit
PCM containers. Continuous storage would be about 5.53 GB/hour before
filesystem/container overhead, so cadence, retention and outage buffering are
still commission facts rather than implementation assumptions.

## Raspberry Pi 5 host allocation

[ADR 0008](decisions/0008-raspberry-pi-5-roof-appliance-host.md) selects the
Raspberry Pi 5 Model B family, not a RAM or storage SKU. The leading bench
candidate is 4 GB RAM, the official Active Cooler, the standard M.2 HAT+ and a
512 GB or 1 TB NVMe. These are proposed integration parts rather than accepted
part dossiers.

Use one USB 2.0 port for the UAC2 module, the onboard Gigabit Ethernet port for
the building link, and PCIe Gen 2 for NVMe. The Pi's duties are exact
eight-channel capture, local atomic file finalization, digesting, outage
buffering, health telemetry and acknowledged upload. The server retains the
raw recording and performs the spatial estimator and caller-track analysis.
Each same-filesystem temporary file must be synced, atomically renamed and
followed by a parent-directory sync before a durable queue admits it. Upload is
at-least-once. The server uses `(node_id, stream_epoch, segment_index)` as the
unique logical key and the digest as its immutable content assertion: the same
key and digest is idempotent, while a changed digest is quarantined as a hard
conflict. Audio and sidecar are one transactional object or share one manifest
digest. The Pi must retain a finalized file until the server acknowledges that
durable object, and a network interruption must not interrupt capture. Lost ACK,
process-kill, hard-power-cut, corrupt-upload, disk-full and backlog-overflow
behavior remain mandatory bench tests.

The first power/thermal baseline uses the official 27 W USB-C supply. The same
load is then repeated with the exact PoE implementation, longest admitted Cat6
and worst admitted enclosure temperature. The currently listed Raspberry Pi
PoE+ HAT is not a Pi 5 mechanical authority; do not adapt it or feed the Pi
through GPIO merely to make the prototype fit. Exact RAM, SSD, PD/splitter,
power advertisement, cooling and service stack remain OWED.

The PoE proof must freeze the PSE, PD/splitter, USB-C cable/topology, permitted
Pi current mode and separate audio/pod-rail allocation. It must externally
measure input and 5 V voltage/current/inrush through cold start, class fallback,
brownout and hot reconnect. Pi telemetry and nominal PoE class alone are not a
whole-appliance power oracle.

## Firmware boundary

Project-authored embedded firmware is forbidden. The user permits a short
internal USB link, and the candidate may load a vendor-supplied USB-audio image
unchanged. Raspberry Pi 5 may run capture, file spooling, health monitoring and
Ethernet transfer; server-side localization, event detection, within-file
tracking and spatial filtering remain host-software proposals and are not PCB
acceptance evidence. A direct TDM-to-Linux carrier
can remove the internal USB module only by reopening this architecture for
ALSA/device-tree/clock bring-up.

## Identity boundary

The planar TDOA signature supplies an anonymous within-file source label, not a
biological identity. Under [ADR 0007](decisions/0007-within-file-stationary-caller-track.md),
the proposed host pipeline detects calls, groups/focuses the single active
source, and retains `caller-A` only while its calibrated position posterior is
sufficiently stationary. Every label expires at the end of the 120-second file.
Material movement, overlap or low confidence starts a new track or returns
`unknown`; track-switch and unresolved intervals are reported with the original
synchronized channels. No association across files, visits, days or changed
perches is required.

## Carrier channel-order identity — 2026-09-12

Carrier ADR0027 / `../crow-audio-carrier-v1/03_src/adc_channel_map.json`
fixes the adopted source mapping of TDM slots0..7 to logical pods4,3,2,1,5,6,7,8. Retain
map ID `crow-carrier-channel-map-20260912` and its source digest with each
surveyed pod-coordinate table and capture epoch. This is a fixed wiring
association with unchanged ADC hardware mode and COTS image; no custom
firmware or runtime reordering is required. The eight-channel impulse test
must verify actual TDM-to-USB enumeration before capture acceptance.
No immutable release or existing recording identity is retroactively changed.
