# Buck input isolation: source correction verified, engineering closure pending

Source base: `534658965562f0e07f3a986da27e910460edfca8`, plus the exact
carrier-only delta retained in the outcome below. This is a source-development
checkpoint, not a generated-board review, release seal or order authorization.

## Implemented correction

[ADR0022](../decisions/0022-buck-input-reverse-isolation.md) adds one
US1B-13-F input diode. Its anode is on `12V_PROTECTED`; its cathode feeds
`12V_BUCK_IN`, U_BUCK VIN/EN and all three 10 uF input ceramics. This isolates
the local converter input bank from the shared eight-spoke bus. Q_IN, the
spokes, 50 mOhm OPA feed, held-rail diode and signal components are unchanged.
Source census is now 323 components, 919 pins and 226 nets, including 41 NC nets.

The final diode pose clears all 322 foreign native footprint instances and
the existing authored power landings. Six local-VIN copper groups have 1.2 mm
entry witnesses. These are in-memory source geometry checks, not routed-board
clearance, inductance or current-transfer acceptance. Source polarity marks,
native pad assertions, route ownership, dossier and schematic intent agree.

The [manufacturer's exact family PDF](https://www.diodes.com/datasheet/download/US1A.pdf)
is vendored in the US1B dossier with SHA256
`d50b2773c0300d97a77f5125419098c8130ecaf967202a44be2b182de8a15c1f`.
The public exact JLC catalog identity was checked without an account or upload.
Its volatile response remains disposable evidence, not allocation or orderability.

## What the electrical study does and does not show

The previous direct-VIN topology exposed the buck reverse port to the shared
bus. The sealed pods' own M7 diodes mean ordinary removal from 11.16 V does
not immediately place eight pod loads on the carrier reservoir. A preceding
brownout can discharge those reservoirs first. The final balanced averaged
model, with explicitly assumed 12 mA/pod undervoltage draw, gives 4.476926389 V
OPA after the isolation budget from a 5.2 V pre-brownout state; forced
undervoltage load cutoff gives 4.513903712 V. This is a conditional design
counterexample, not measured AP63205 behavior or a universal silicon failure.

The retained 46-row sensitivity run includes three timesteps, 36 load/cap/ESR/
reverse-resistance cases and controls. Of the 36 brownout cases, 24 fail the
conditional 4.5 V target. Earlier model revisions are explicitly invalid or
superseded; their errors and corrections remain recorded. Already-disabled
initial states are ineligible, not credited as enabled-removal passes.

The corrected source screen includes a 1.3 V engineering input-diode drop:
9.86 V local VIN and 0.985345543 A total allocated input. Its shutdown screen
charges 100 uA diode leakage, 1 mA local reverse-port/control draw and 100 nC
recovery, giving 4.501285055 V: only 1.285 mV above the target. These are
conditional application budgets. In particular, neither the 1 mA nor the
100 nC is a manufacturer guarantee; 50 ns recovery time at its specified
test condition does not establish application recovery charge.

## Independent verification and retained evidence

The original live-source regression failed before the diode was added.
Focused final tests pass 5/5 and include wrong polarity, stranded capacitors,
extra local-VIN ownership, bad placement and excessive leakage/recovery/drop.
The worker's final full-source run passed 246/246 in 99.577 s.

Root independently reran all 246 tests: PASS in 99.232 s, finishing at
07:57:46.617918Z. Its log SHA256 is
`8754d6951c654e2e4423d44386834931921e12128ae08a0173c5c8148651c5ff`.
The separate production source-power check also returned zero, with
`status: PASS_CONDITIONAL_SCREENS` and `generation_admitted: false`.
Its log SHA256 is
`97d47f6e76afc9c4b6fe555084bf4a272a4345cd2bc6a8040faa779270ecf5eb`.
The frozen source inventory did not change during either run. Root reopened
all 352 final worker-input hashes before preserving the result.

The worker returned INCOMPLETE at 07:49:26.601304Z and released every writer
scope. Root captured it at 07:50:41.292864Z, before the 07:57:20Z deadline:
541/541 immutable packet items intact, 538 baseline paths compared, 30
Git-visible deltas within scope, and all 17 recorded child PIDs exited.
The worker's 29-entry delta listing omitted FIRST_ARTICLE_TEST_PLAN.md;
the root capture and final input manifest include and bind that change.

The [durable outcome](../SOURCE-CORRECTION-20260909-reverse-port-outcome.json)
retains that capture, actual tests and failed attempts, scripts, model results,
input identities, root checks and explicit limitations. It is 1,404,173 bytes;
SHA256 `5e515838cffce003a4ff57b9656e7577c923869d8230a1081d8617bc18350655`.
The first root verification wrapper failed before tests because an optional
parity file was absent; the corrected wrapper binds absence explicitly.
The first preservation attempt stopped on KiCad diagnostics before JSON and
wrote no outcome; the successful attempt validates that diagnostic prefix.

The repository contract audit still FAILS with the same 2,891 structural
findings as the preceding audit, including 16 in this carrier. Root compared
the actual structural finding lines, not just totals. No shared checker,
ratchet ceiling or historical fixture was relaxed. In-flight untracked-source
bookkeeping is separate from those inherited findings.

## Next engineering boundary

Extend the coupled reachable-state/current-duration account to include local
VIN capacitance and buck-inductor storage, or the signed buck-port energy
integral. Correlate partial CT reset, DUMP_RC/NR state and ADC recharge with
dynamic OPA loading. Do not assume every restart has a fully discharged CT
and 298.35 ms delay, or a uniform 112 mA OPA load. The previous 5.79 A / 20.5 uJ
event is not an instantaneous resistor failure and does not justify increasing
the feed resistance. Source engineering acceptance remains pending.

After that closure, regenerate from source and obtain fresh schematic/placement
reviews, routing and release evidence. Current carrier native bytes remain
unchanged and stale; no carrier release exists. The sealed pod, TOP77/0.20 A
bring-up, conditional TDM, sourcing and publication holds are unchanged.
Public information supports the next source analysis; no new user choice,
vendor coordination, upload, order or push is required or claimed here.
