# LS38 source correction and assembly policy

Diagnostic successor, not accepted assembly. Supersedes the conflicting P011,
P029, P030 and P033 source assertions in retained LS37 notes; their historical
bytes remain unchanged. Independent engineering evidence:
`08_reviews/ls38-tolerance-engineer.md`. Maker PDFs remain authoritative.

- P011 CMA-4544PF-W: leads have orthogonal widths .45±.05 and .42±.05 mm,
  not a demonstrated round diameter. Radius .344 mm conservatively contains the
  maximum .50×.47 cross-section; projection max5.0 mm. Nominal lead centers and
  case polarity stay unchanged. This envelope does not represent a rigid
  worst-pitch insertion guarantee.
- P029 R-78E5.0-0.5: Rev9/2025 general tolerances xx.x±.50, xx.xx±.25.
  Reflect the drawing bottom view into native component-side view: local body
  X−3.46..9.14,Y−7.25..2.25,Z0..10.9 conservatively stacks size and datum
  tolerances. Lead max projection4.35, max-section circumscribed radius.336.
  Do not center the housing over its offset lead row. Pin1 Vin,2 GND,3 Vout.
- P030 RJHSE-5080: source title-block general inch tolerance must be applied
  to housing dimensions, not the BASIC recommended hole positions. The corrected
  housing bounds are recorded in the recipe and expert addendum. Pins/pegs still
  use maker recommended-hole occupancy, not undisclosed physical profiles.
  Peg Z−4 is illustrative only. No underboard enclosure/floor/hardware clearance
  is asserted; an independent below-board XY-column check remains required.
- P033 retained manufacturer.pdf already is Rev GD10/21/22. Its Dmax3.05
  excludes flash without a finite allowance. Existing 3.55 full Y envelope is
  a proposed incoming acceptance limit, not a manufacturer maximum. The same
  distinction applies to P026 flash and other designer-sized envelopes. No
  incoming measurement or supplier capability has been demonstrated.

Ordinary manual free-lead preparation for MIC/BZ/RECOM is a proposed assembly
process: align outside the package before soldering, support the free lead,
never bend at/load the seal or case, force insertion, damage plating or tilt a
body to conceal interference. Require free insertion, correct polarity and
proper seating. Reject/quarantine failed fits. Finished-hole minimum allowance,
case pose, solder fill/retention and workmanship remain explicitly reviewed;
contact-registration tolerances are not physical insertion allowances. This is
not manufacturer mechanical qualification or permission to trim plastic pegs.

No universal mounted-pose capability is inferred. The .10mm/1degree sensitivity
screen is diagnostic; no tighter limit is adopted to save current copper.
Existing LS33 module seating/relief and LS34 accessory constraints remain.
Known design contradictions cannot be transferred to physical qualification.
