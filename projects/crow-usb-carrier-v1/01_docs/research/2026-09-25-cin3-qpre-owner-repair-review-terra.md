# Review: C_IN3 / Q_PRE source move

Reviewed `48a2538e` against the exact 15-part subject board
`d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`.
The source overlay moves only `Q_PRE` from `(46.00,106.85,0°)` to
`(46.00,107.15,0°)`.

I regenerated the frozen source twice in isolation.  The baseline reproduced
SHA-256 `612d319fdafd5b9eaa085f64c7752f94a0953a659f9b883cd5008b6504eeab71`;
the independent trial and checked-in candidate both reproduced
`e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef`.

The result is correct as a narrow geometry repair:

* The complete 569-reference census is unchanged.  All pad number, net,
  copper-layer membership, shape, size, drill, and relative pad position data
  match the subject; only Q_PRE's footprint pose differs.
* The 27 fixed P1 references are unchanged.
* The only removed full-envelope cross-owner pair is `C_IN3` / `Q_PRE`; no
  pair was added.  Body and inter-footprint pad overlap counts remain zero.
* Native DRC is identical: 699 violations, 499 unconnected items, and equal
  type/description/item-UUID identity sets.  This is a no-new-issue result,
  not a clean DRC result.
* Q_PRE remains fully contained by its functional `quiet_power` owner but
  remains in the broad `input_buck` planning rectangle.

The move increases Q_PRE.1-to-R_PRE_G.1 from 2.447040 to 2.741898 mm,
decreases Q_PRE.2-to-D_HOLD.1 from 3.561798 to 3.299455 mm, and changes the
hold pad distance Q_PRE.3-to-R_PRE.2 only from 7.039376 to 7.052681 mm.  The
nearest full-envelope gaps are exactly 0.260 mm to both C_IN3 and D_HOLD.

That 0.260 mm is enough to eliminate the observed envelope intersection.  It
is not enough to admit a next physical-cell experiment: the physical-cell
checker requires a cell not to overlap any foreign source region, while Q_PRE
still intersects the `input_buck` planning region.  The value is also only an
envelope measurement, without assembly tolerance, copper routing, current,
thermal, or filled-return proof.  The repair removes one native obstacle but
does not establish an exclusive cell or any P1/P2 credit.
