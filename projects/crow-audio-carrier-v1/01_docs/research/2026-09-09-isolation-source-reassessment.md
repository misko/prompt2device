# Isolation-source reassessment — 2026-09-09

Public-authority comparison, not part adoption, a new waveform experiment,
native review or source acceptance. CAR-F12 remains the same investigation
with four of six attempts spent and no pending reservation. No requirement,
acceptance limit, milestone or cumulative budget changes here.

## Independent review changes the next decision

The fresh read-only review of source commit `8e8a2910` completed before its
deadline. Its verdict was **INCOMPLETE source protection argument**, not a
demonstrated protection failure. The coordinator's retained summary and exact
38-file packet identity are in
`../SOURCE-CORRECTION-20260909-reference-divider-outcome.json`. This summary
does not claim to be the reviewer's verbatim report or a native PR-REVIEW
witness. The review predates the four precision-divider identity changes.

Two concrete dependencies survive:

- U_ISO1–8: an amplifier domain can be energized while the held switch rail
  passes through the interval between zero and its minimum operating supply.
  TMUX2821's zero-supply guarantee does not bound this whole interval. The
  pod's nominal 110 ms reference RC means a full 2.5 V pod output cannot
  simply be invented at the beginning of a cold start. This is an unresolved
  protection argument, not proof that an ADC limit is exceeded.
- U_AFE9: the reference input reservoir is correctly behind a 10k limiter,
  but a 1k output isolator is not itself an output-injection rating. The two
  buffered reservoirs also exchange charge with eight bias legs per bank;
  their ordinary 1.60–1.70 V acceptance band is not an all-state bound.

Keep OPA2320 as the candidate. First remove or authoritatively bound these
dependencies. Do not reject the new amplifier because an old OPA1656 model
left its domain; do not repeat supervisor-divider tuning or scalar delay
sweeps. Coupled restart, filter-loop behavior and feed-current duration still
need their own source argument after selecting the protection topology.

## Bounded alternative comparison

| Candidate | Public evidence | Disposition at this checkpoint |
|---|---|---|
| Current TMUX2821 | SCDS488 §7.3.3 specifies powered-off behavior at VDD=0; normal supply starts at 1.8 V. | Keep current source unaccepted; stronger SEL pulldown alone does not specify the analog channel below operating supply. |
| ADG4612 | The datasheet p17 describes isolation with floating supply or VDD at most 1 V; normal-on conditions require at least 2.7 V. | Headline power-off protection is insufficient to adopt it without resolving the intervening conditions and leakage. |
| TMUX1072 | SCDS382C p5 lists a typical 1.65 V UVLO, but pp4–6 give a 2.3 V operating minimum and microamp-level leakage with particular conditions. | Not selected: a typical UVLO entry alone is not the missing full-interval isolation/leakage bound; it is also not a drop-in SPST. |
| TMUX7462F | SCDS394B p1 explicitly includes supplies below UV threshold in the high-impedance state. | Not a direct substitute: this is a channel protector without the required independent AUDIO_EN select control. |
| TMUX7412F | SCDS404B pp6,32–33 provides bounded UVLO thresholds, selectable SPST channels and protection below UV threshold; single-supply operation starts at 8 V. Drain pins have supply diodes. | Credible powered-switch comparison candidate, not adopted. Requires an actual 12 V supply/retention and drain-voltage argument, including the UVLO-to-operating interval; not an assumed drop-in on the held 5 V rail. |
| AQY221R2S PhotoMOS | Panasonic's exact product table specifies a normally-open AC/DC contact with LED control and no analog supply pins. | Credible dependency-removal comparison candidate, not adopted. Must verify exact datasheet conditions, sourcing, LED drive/turn-off timing, load behavior and geometry before selection. |

Primary sources inspected on 2026-09-09:

- [TMUX2821](https://www.ti.com/lit/ds/symlink/tmux2821.pdf)
- [ADG4612/ADG4613](https://www.analog.com/media/en/technical-documentation/data-sheets/adg4612_4613.pdf)
- [TMUX1072](https://www.ti.com/lit/ds/symlink/tmux1072.pdf)
- [TMUX7462F](https://www.ti.com/lit/ds/symlink/tmux7462f.pdf)
- [TMUX7412F](https://www.ti.com/lit/ds/symlink/tmux7412f.pdf)
- [AQY221R2S exact manufacturer product specifications](https://industry.panasonic.com/global/en/products/control/relay/photomos/number/aqy221r2s)

The Panasonic product table reports 1.25 ohm maximum on-resistance, 18 pF
maximum output capacitance, 10 nA maximum off leakage, 0.2 ms maximum turn-off,
and recommended LED current 5–30 mA. These table entries are not yet adopted
as an all-temperature design envelope; their complete datasheet test
conditions must be captured. The download-center page did not expose the
PDF through this text browser. No authentication or access workaround was
attempted. The tube part and any reel suffix must not be conflated.

## Concrete next work

Compare only the selectable UVLO family and normally-open optical contacts.
The latter removes analog-supply partial-power behavior by construction,
but transfers the deciding work to a visible LED/control path and timing.
This is an engineering inference, not approval of the part or circuit.
Evaluate both all 16 ADC legs and the two reference-reservoir disconnects;
retain the filter's separate small capacitors and correlated charge history.

Before adopting either, bind exact primary conditions and public sourcing,
derive its full normal/shutdown/restart control path, include its additional
supply load, and check actual footprint/placement. An optical design needs
proven LED-off current under reset/undervoltage, maximum release time before
ADC dump/OPA undervoltage, and sufficient on-current at the lowest admitted
rail. A powered switch needs its actual supply and drain return paths covered.
No sweep should be admitted until these facts make its two outcomes decisive.

No extra waveform sample, perfect proprietary model, logged-in JLC result or
valid audio during shutdown is required by this reassessment. Physical audio,
timing and thermal qualification remain distinct later holds. No isolation
replacement has been applied to the circuit at this checkpoint.
