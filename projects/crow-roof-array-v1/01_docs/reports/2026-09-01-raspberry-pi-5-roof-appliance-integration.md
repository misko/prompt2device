---
schema: 1
kind: pcb-human-report
report_id: 2026-09-01-raspberry-pi-5-roof-appliance-integration
title: Crow roof array — Raspberry Pi 5 roof-appliance integration
subtitle: One networked recorder with shared-clock USB audio and a crash-recovery spool contract
project: crow-roof-array-v1
date: 2026-09-01
status: DRAFT
evidence_status: INCOMPLETE
---

> **Current-selection note:** ADR 0010 supersedes this report's four-stereo-ADC
> candidate with one hardware-controlled CS5308P feeding MCHStreamer TDM8.
> Interpret every multi-ADC/reset-phase row below as historical rationale; the
> active first-article obligation is single-die interchannel continuity, phase,
> slot/word interpretation and reset recovery.

## Executive conclusion

**CITED** — The user selected Raspberry Pi 5 for the local roof-appliance
computer and accepted one external PoE/Ethernet connection with a short
internal USB audio link.

**PROPOSED** — Use Raspberry Pi 5 Model B as a headless recorder and network
bridge. Four stereo ADCs remain synchronous on one local TDM clock; the
MCHStreamer converts that already synchronous stream to USB Audio Class 2; the
Pi records exact 120-second eight-channel files to local storage and uploads
them to the server over wired Ethernet. The server performs the planar source
track and within-file caller-label analysis. Ethernet packet timing is never an
acoustic timing source.

**PROPOSED** — The sensible bench configuration is a 4 GB Pi 5, official
Active Cooler, standard M.2 HAT+ and 512 GB or 1 TB NVMe. Those variants are
not yet accepted parts. Start on the official 27 W USB-C supply, measure the
complete load, then repeat under the exact proposed PoE path and longest cable.

**OWED** — Do not lock an official PoE HAT. Raspberry Pi's currently listed
PoE+ HAT says it is compatible with Pi 3B+ and Pi 4, while Raspberry Pi 5 moved
the PoE header. No current first-party Pi-5 PoE HAT part and datasheet were
found. The exact standards-compliant isolated PD or splitter, PoE type, USB-C
power advertisement, quiet audio rails, enclosure and thermal path remain open.

The project remains `PCB-COMMISSION INCOMPLETE`; this report advances the
system architecture but authorizes no schematic, layout, release or order.

## Question and scope

This report answers how the accepted Raspberry Pi 5 interfaces to the
multichannel recorder and the user's server. It defines the division of work,
data rate, file lifecycle, power qualification and mechanical evidence needed
before the custom carrier can be designed.

**OWED** — It does not select the final Pi RAM SKU, SSD, PoE PD, PSE, outdoor
connector, enclosure, microphone, ADC, or stationarity threshold. It does not
author the host capture application or claim a lightning-qualified roof system.

## Evidence boundary

**CITED** — [ADR 0005](../decisions/0005-poe-ethernet-roof-appliance.md)
owns the accepted external Ethernet/PoE and internal-USB boundary.
[ADR 0008](../decisions/0008-raspberry-pi-5-roof-appliance-host.md) owns the
accepted Pi 5 platform choice. The exact user directive is retained in the
[BRIEF](../BRIEF.md).

**DATASHEET** — Raspberry Pi 5 exposes Gigabit Ethernet, two USB 2.0 ports,
two USB 3.0 ports, PCIe and a microSD slot. Its product brief specifies a
5 V/5 A USB-C supply and a 0–70 °C operating range. The official mechanical
drawing gives an approximate 85 × 56 mm board and explicitly says not to use
the drawing to produce production data.

**DATASHEET** — miniDSP specifies MCHStreamer as Linux-compatible UAC2,
USB 2.0, and either USB-powered or externally powered at 5 V/300 mA. Its TDM8
firmware carries eight channels on one data line with module-generated MCLK,
BCLK and FSYNC.

**OWED** — No Pi 5, MCHStreamer, ADC carrier, PD, NVMe, or complete power stack
has yet been assembled and run as this eight-channel system. No retained ALSA
continuity, thermal, brownout, Ethernet outage or file-integrity result exists.

## Findings

### 1. The server sees one ordinary network node

```text
seven outer pods + one center pod
        │ balanced analog star
        ▼
four stereo ADCs on one TDM clock
        │ 8 channels / one local timing domain
        ▼
MCHStreamer UAC2 module
        │ short internal USB 2.0
        ▼
Raspberry Pi 5 Model B
        ├── local atomic 120-second file spool
        └── wired Gigabit Ethernet over the single PoE Cat6
                    │
                    ▼
          server storage + within-file tracking
```

**PROPOSED** — The Pi should be headless. From the server, it is one wired
Linux endpoint, not eight network microphones. It may obtain an address from a
reserved DHCP lease or a managed static assignment; the exact provisioning and
upload protocol remain host-software decisions.

**PROPOSED** — Capture locally first. Write to a same-filesystem temporary
file, require the exact channel/frame count, `fsync` the file, derive its
content identity, atomically rename it, `fsync` the parent directory, and add
it to a durable upload queue. Transport is at-least-once: a lost acknowledgement
causes a retry. The unique logical key is `(node_id, stream_epoch,
segment_index)`; the digest is its immutable asserted content, not part of the
key. The same key and digest is an idempotent success, while the same key with
a different digest is a hard conflict that must be quarantined and alerted,
never overwritten or admitted as another segment. Audio and sidecar must be
committed transactionally or covered by one manifest digest. Acknowledge only
the durably committed object and retain the local file until then. A network
outage must delay transfer rather than interrupt recording.

**PROPOSED** — The server receives raw audio plus sidecar metadata: node id,
stream epoch, segment index, first/last sample index, UTC start/end, monotonic
start/end, UTC clock-quality/NTP-synchronised state, sample rate, sample format,
channel-order contract id, exact frame count, overrun/underrun count, file
digest, software identity, temperature and power-warning state. UTC may be
invalid after an offline cold boot. Monotonic time and sample indices remain
authoritative within a stream epoch; network time only labels the event and
never establishes inter-microphone phase.

### 2. The Pi is not the sampling clock

**DATASHEET** — In the selected MCHStreamer TDM mode, the module supplies the
audio clocks and receives the eight-channel serial data. All microphone ADCs
must therefore share that MCLK/BCLK/FSYNC domain before the stream reaches USB.

**INFERRED** — USB and Ethernet may packetize or buffer the samples without
destroying their relative timing as long as the complete ordered stream has no
lost, duplicated or reordered frames. ALSA xruns and sample-count discontinuity
are failures, not timing uncertainty to average away.

**PROPOSED** — Open the exact ALSA `hw:` PCM device, not `default` or `plughw`,
with a frozen eight-channel, 48 ksample/s hardware format (`S24_3LE` or
`S32_LE`, whichever the admitted module exposes). Keep one PCM stream open and
segment it every 5,760,000 frames. A USB reset, PCM reopen, kernel device reset
or unexplained discontinuity ends the stream epoch and quarantines the partial
segment; software must never conceal it by padding, resampling or stitching.

**OWED** — Exact frame count and an empty xrun log alone cannot prove absence
of common frame slips, format conversion, reordered slots or a changed
inter-ADC filter/sample phase after reset. Admission requires a deterministic
frame-coded digital/TDM stimulus and a simultaneous common analog impulse
across all four ADCs, repeated through cold boots, deliberate USB resets and
the admitted temperature range. Relative delay and phase must remain within a
numeric limit derived before the test.

**PROPOSED** — Use one USB 2.0 host port for MCHStreamer and reserve the PCIe
interface for NVMe. Leave USB 3.0 free for diagnostic storage or service. Do
not move ADC data directly to Pi GPIO/TDM unless ADR 0008 is superseded and the
additional Linux clock/driver work is commissioned.

### 3. Data and storage are modest for Pi 5, but not negligible operationally

| Quantity | Eight-channel value | Basis |
|---|---:|---|
| Samples per channel per file | 5,760,000 | **INFERRED** — 48,000 × 120 |
| Packed 24-bit sample payload | 138.24 MB | **INFERRED** — 8 × 48,000 × 3 × 120 |
| 24-bit-in-32-bit payload | 184.32 MB | **INFERRED** — 8 × 48,000 × 4 × 120 |
| 32-bit-container audio rate | 12.288 Mbit/s | **INFERRED** — 8 × 48,000 × 32 |
| Continuous 32-bit payload | 5.5296 GB/h | **INFERRED** — sample payload only |
| Continuous 32-bit payload | 132.7104 GB/day | **INFERRED** — sample payload only |

**INFERRED** — Gigabit Ethernet and the official M.2 HAT+'s PCIe Gen 2 path
have ample throughput. Storage endurance, retention time, safe power loss and
outage backlog—not link speed—govern the design.

**PROPOSED** — A 512 GB NVMe is a practical first bench candidate; 1 TB buys
more outage and field-test margin. Do not claim a day count from nominal drive
capacity until filesystem reserve, actual recording cadence, metadata,
overprovisioning and retention policy are locked. Use standard PCIe Gen 2; the
official documentation says Pi 5 is not certified for Gen 3.

**PROPOSED** — Four GB RAM is the default candidate because raw capture and
spooling need little memory while leaving room for diagnostics. Two GB is
probably sufficient for capture-only; eight GB is justified only if material
local inference is later retained. The user's directive selected the Pi 5
family, not one of those SKUs.

### 4. Power must be proved as a whole appliance

**DATASHEET** — Pi 5 boots from 5 V/3 A, but without a detected 5 V/5 A
USB-PD source it limits the USB ports and fan header together to 600 mA. A
detected 5 V/5 A source raises that shared peripheral budget to 1.6 A and adds
board-power margin. miniDSP allocates as much as 300 mA for MCHStreamer.

**INFERRED** — MCHStreamer alone fits within the restricted peripheral budget,
but the Active Cooler shares that budget and the full system includes storage,
Ethernet, ADCs and pod power. A PoE converter that can source enough current
electrically may still leave the Pi in restricted mode if it does not present
the expected USB-PD contract.

**PROPOSED** — Qualify in this order:

1. Pi 5, Active Cooler, NVMe and MCHStreamer on the official 27 W USB-C supply.
2. Add the powered ADC carrier and all eight representative pod loads.
3. Freeze the exact PSE, PD/splitter, USB-C cable/advertisement, conversion
   topology, permitted Pi current mode and separate audio/pod-rail budget.
4. Replace only the power/network source with that candidate PoE chain.
5. Repeat at longest Cat6 length and worst admitted enclosure temperature,
   including cold start, PSE class fallback, brownout and hot reconnect.

**PROPOSED** — Prefer USB-C power input so the Pi's intended input path remains
in use. Do not adapt the older PoE HAT or feed the Pi through GPIO for the first
prototype. A Type 2 PoE+ solution may pass an audio-only measured budget; use
Type 3 if the NVMe, sustained compute, pod power or thermal margin does not fit.
The decision is made from retained voltage/current/temperature data, not the
PoE marketing class alone.

**OWED** — Instrument PoE input power and the Pi 5 V input externally. Pi
telemetry does not measure the complete USB, storage, fan, ADC and pod load.
The retained budget must include conversion loss, minimum output across cable
and temperature, inrush, class fallback and rail start-up order. Type 2's
25.5 W PD-input budget cannot by itself substantiate a 25 W Pi USB-PD contract
plus conversion loss and separate audio rails.

### 5. Mechanical and thermal CAD remain evidence-gated

**DATASHEET** — The official Pi 5 drawing is approximate and explicitly warns
against using it for production data. The official product-information portal
also provides current STEP models. The Active Cooler is the supported
Pi-5-specific heatsink/blower, and the standard M.2 HAT+ can mount above it.

**PROPOSED** — Import the current official STEP and measure one physical Pi,
cooler, HAT, SSD and cable assembly before enclosure floorplanning. Reserve
USB, Ethernet, power-button, SD/service, fan intake/exhaust and cable-bend
volumes. A fan recirculating air in a sealed solar-heated box is not a complete
thermal design; under-eave placement or a conductive enclosure heat path is
preferred.

**PROPOSED** — Content-address every imported Pi, cooler, HAT, SSD and cable
model and bind it to the measured physical board revision. A later vendor CAD
update is a new authority, not a silent replacement.

**OWED** — Solar load, ambient range, condensation, rain, inlet filtration,
roof mounting and service clearance remain unknown. Pi 5's cited 0–70 °C board
range does not qualify an enclosure or guarantee no CPU throttling.

### 6. Current component posture

| Function | Current status | Design consequence |
|---|---|---|
| Linux host | **CITED** — Raspberry Pi 5 Model B family, accepted by ADR 0008 | Exact RAM SKU and physical unit still owed |
| Audio-to-USB bridge | **PROPOSED** — MCHStreamer TDM8/UAC2 | Freeze exact vendor image and prove Linux channel order |
| Local storage | **PROPOSED** — standard M.2 HAT+ plus 512 GB/1 TB NVMe | Exact SSD/endurance/power dossier owed |
| Cooling | **PROPOSED** — Active Cooler for prototype | Whole-enclosure thermal path and fan reliability owed |
| PoE power | **OWED** — isolated standards-compliant PD or splitter | Do not use the Pi 3B+/4 PoE+ HAT as Pi 5 authority |
| ADC carrier | **PROPOSED** — four hardware-controlled stereo ADCs | Exact ADC, straps, clock fanout and interface contracts owed |
| Server protocol | **PROPOSED** — digest-acknowledged file upload | Exact authentication, retry and retention policy owed |

## Recommendations

1. **CITED — keep the ADR-accepted Pi 5 Model B as the host platform.** Do not replace
   it with Compute Module 5 or direct TDM without a superseding decision.
2. **PROPOSED — build the recorder bench before the custom carrier.** Obtain a
   Pi 5, Active Cooler, standard M.2 HAT+, candidate NVMe and MCHStreamer; prove
   direct-hardware eight-channel UAC2 continuity, inter-ADC phase stability and
   analog quality on the official PSU.
3. **PROPOSED — implement and prove crash-tolerant local spool-and-forward.** Never make an
   NFS/network mount the only recording sink. Finalize and durably queue locally,
   upload at least once in the background, use idempotent content-addressed
   server commits, and retain data until the server acknowledges the exact
   committed object.
4. **PROPOSED — keep DSP on the server for v1.** The Pi records, monitors and
   transfers; the server performs planar localization, track confidence and
   within-file caller labelling. This reduces roof power and thermal risk.
5. **OWED — select PoE from measurements.** Compare Type 2 and Type 3 only
   after measuring the complete appliance; require correct Pi USB power mode,
   no undervoltage/overcurrent events and margin at cable/thermal corners.
6. **OWED — close external-hardware facts before CAD.** Bind the current Pi
   STEP and physical measurements, then add the machine-readable mating record
   and exact module/service envelopes.

## Validation plan

| Test | Retained evidence | Pass boundary before architecture admission | Failure implication |
|---|---|---|---|
| Direct PCM enumeration and channel order | `lsusb`, exact ALSA `hw:` capabilities/parameters, module image identity, eight-channel impulse map | Exactly eight hardware channels at frozen 48 ksample/s format/order; no plug conversion | Reject image, wiring, module mode or host path |
| Sample continuity and reset phase | Frame-coded TDM stimulus, simultaneous analog impulse, kernel/USB logs and per-channel delay/phase over cold boots, deliberate resets and thermal cycles | No slips, duplicates or reordering; numeric inter-ADC delay/phase limit met in every new stream epoch | Reject clock/reset/capture architecture; never stitch failed epochs |
| 120-second segment integrity | Persistent-stream epoch, exact 5,760,000-frame segment census, channel/format/digest, xrun and device-reset logs | Every admitted segment is exact; partial/reset segments are quarantined rather than padded or concealed | Reject capture/storage path |
| Analog quality under concurrent load | Noise, SNR, crosstalk, coherent-spur and relative-delay spectra with fan off/on, NVMe write/hash, CPU load and saturated Ethernet, on official PSU and PoE | Frozen channel-quality limits met without load-correlated or fan/structure-borne interference | Rework grounding, power, mechanics, clocks or load allocation |
| Long-run capture | Derived duration covering thermal steady state, multiple segment boundaries, concurrent hash/upload, maximum admitted outage backlog and queue drain | Zero rejected continuity checks or channel-order drift; backlog drains within the frozen recovery objective | Rework USB, storage, scheduler, thermal or capacity design |
| Crash and network recovery | Inject process kill/hard power loss before and after file sync, rename, directory sync, queue update, upload, server commit, acknowledgement and local deletion; also corrupt partial upload, lost ACK, disk full and backlog overflow | No admitted object lost or misidentified; same logical key/digest retries are idempotent; a changed digest conflicts; high-water policy preserves the frozen recovery objective | Repair spool protocol, server commit or capacity policy |
| Official-PSU power baseline | External input/5 V current and voltage, Pi diagnostics, inrush, rail sequencing, temperature, throttling and complete appliance load | No undervoltage, overcurrent, reset, throttle or capture discontinuity with numeric margin | Reduce load or change cooling/power distribution |
| PoE substitution | Same evidence with exact PSE/PD/USB-C cable/topology, current mode, longest Cat6 and all pod loads; cold start/fallback/brownout/reconnect | Matches baseline behavior with documented minimum electrical and thermal margin | Raise PoE type or change PD/conversion architecture |
| UTC quality and offline boot | RTC/NTP state, UTC/monotonic/sample-index sidecars across connected and offline boots | Invalid UTC is flagged; stream epoch and sample indices remain unambiguous | Add RTC or repair time-quality reporting |
| Thermal corner | Representative enclosure at admitted ambient and concurrent worst-case load | No thermal throttle, reset, storage error, phase change or audio discontinuity; numeric margin frozen from evidence | Relocate, derate or redesign thermal path |
| Mechanical fit/service | Hash-bound current STEP/accessory models plus measured board revision in enclosure | All fasteners, mates, bends, airflow and service operations fit without load on connectors | Revise enclosure/carrier before PCB floorplan |

## Source register

### Repository evidence

- [Project BRIEF](../BRIEF.md) — **CITED**, exact Pi 5 directive and current
  commission boundary.
- [ADR 0005](../decisions/0005-poe-ethernet-roof-appliance.md) — **CITED**,
  accepted external PoE/Ethernet and internal USB boundary.
- [ADR 0008](../decisions/0008-raspberry-pi-5-roof-appliance-host.md) —
  **CITED**, accepted host-platform selection.
- [Architecture checkpoint](../ARCHITECTURE.md) — **PROPOSED**, current
  whole-system boundary with its remaining owed facts stated in that document.

### External primary sources

- [Raspberry Pi 5 product brief](https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008348-DS-4-raspberry-pi-5-product-brief.pdf) — **DATASHEET**, interfaces,
  supply, operating range and platform variants; accessed 2026-09-01.
- [Raspberry Pi 5 mechanical drawing](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf) and [official CAD portal](https://pip.raspberrypi.com/categories/892-raspberry-pi-5) — **DATASHEET**,
  approximate drawing, production-use warning and available STEP authority;
  accessed 2026-09-01.
- [Raspberry Pi power and USB documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html) and [Pi 5 USB-PD white paper](https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-009856-WP-1-USB%20Power%20delivery%20on%20Raspberry%20Pi%205.pdf) — **DATASHEET**, 5 V/3 A versus 5 V/5 A behavior and USB/fan current limit; accessed 2026-09-01.
- [Raspberry Pi Active Cooler](https://www.raspberrypi.com/products/active-cooler/) — **DATASHEET**, Pi-5-specific cooling assembly; accessed 2026-09-01.
- [Raspberry Pi M.2 HAT+ documentation](https://www.raspberrypi.com/documentation/accessories/m2-hat-plus.html) — **DATASHEET**, standard HAT/Active Cooler fit, 2230/2242 support, PCIe Gen 2 and NVMe boot; accessed 2026-09-01.
- [Current Raspberry Pi PoE+ HAT page](https://www.raspberrypi.com/products/poe-plus-hat/), [Pi 5 compatibility-break announcement](https://www.raspberrypi.com/news/introducing-raspberry-pi-5/), and [Pi-5 PoE HAT status](https://www.raspberrypi.com/news/raspberry-pi-poe-injector-on-sale-now-at-25/) — **CITED**, current listed compatibility and absence of a proven first-party Pi-5 HAT; accessed 2026-09-01.
- [miniDSP MCHStreamer product page](https://www.minidsp.com/products/usb-audio-interface/mchstreamer) and [user manual](https://www.minidsp.com/images/documents/MCHStreamer%20User%20Manual.pdf) — **DATASHEET**, UAC2/Linux support, power allocation and TDM8 clock/data interface; accessed 2026-09-01.
