# Focused checker correction to the channel-8 multi-cell plan

This corrects two statements in `45fd8ac5`; it does not change a board,
canonical source, acceptance state, or route evidence.

## Occupied cells need not connect

The earlier plan incorrectly said every same-owner gap needs a transit cell to
make the partition connected.  In `_physical_cells`, `reached` is initialized
with **all occupied cells** (checker lines 1317--1320).  The subsequent
positive-edge walk adds only remaining cells, which can only be empty transit
cells by the row invariant `transit == (not refs)` (1283--1291).  Therefore
disconnected occupied `analog_ch8` pockets, such as a fixed `J8` connector
pocket and a remote cap-local pocket, are allowed by the current checker.

Only an explicitly declared empty transit cell must edge-connect to one or
more already reached same-owner cells; otherwise lines 1321--1329 reject it as
disconnected.  The corrected source plan is: create no transit cell merely to
join occupied pockets.  Add one only where a named corridor/witness needs that
region, then test its edge contact and all foreign-region exclusions.

## Unresolved-branch endpoints still use the functional region

The earlier plan also implied that adding a physical cell automatically makes
the ADC8N unresolved-tree endpoint region that pocket.  It does not.  Current
`_unresolved_multiterminal_branches` obtains
`owner_region = rectangle(regions.get(block), ...)` at checker line 481 and
tests each native pad against `regions[block]` at lines 482--485.  Its branch
endpoint rows have no `physical_cell_id` field.  Consequently the existing
`analog_adc8n_unplaced_tree` remains checked against `regions['analog_ch8']`,
even after a multi-cell declaration.

Physical-cell ids are already used for coarse witnesses and integration faces
when explicitly supplied (for example lines 149--157 and 657--665), but that
behavior does not extend to unresolved branches.  The corrected reject-first
order is:

1. Validate the source partition with `_physical_cells`; keep all 36 refs
   exactly once, and do not add transit solely for connectivity.
2. Preserve the unresolved ADC8N tree’s functional-block containment check
   against `regions['analog_ch8']`.  Reject if the primary functional region
   cannot contain its branch pads under current code.
3. If branch-level cell containment is required, first make a governed checker
   extension that adds and validates `physical_cell_id` on branch endpoints,
   then update the schema/receipt and independently review it.  Do not treat a
   prospective pocket as if the current branch checker had accepted it.
4. Separately, name physical-cell ids only on supported witnesses/corridor
   faces and retain their P2 pad-access and filled-return obligations.

This is a code-semantic correction only.  It supplies no pad entry, route,
return, capacity, P1, or P2 credit.
