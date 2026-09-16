# Native complete classes execution report

Frozen packet SHA256: `b5d07ea0a94aecacac48e8b8275edb0f534379a9e412585846f064b0c7aaffd1`; verified 661/661 input members. Archive SHA256: `3aa78234c2007b00d366a4af041ae7725bb0379682f07dd1d186d62703abe6b9`, 5119 bytes; exactly three regular extracted producer files matched manifest hashes/sizes.

Exact command was executed once with the existing private parent. OUTPUT_DIRECTORY was emitted as the actual child `/tmp/pland-native-complete-classes-20260910T222644Z/native-interface-run-u2jowhbt`. Administrative wrapper PID 2183952, start 2026-09-10T22:28:24.533066+00:00, end 2026-09-10T22:28:26.445943+00:00, duration 1.912856652168557 s, rc 1, timeout false. All six producer children report reaped.

Child outcomes: fixture build rc 0; census rc 0; public base checker rc 1 (expected named X1.1 failure); public hostile checker rc 1 (expected); native base DRC rc 0; native hostile DRC rc 5. Producer stopped at the native-hostile assertion. Native hostile observed `{'clearance': 1}` with zero unconnected, while the frozen assertion required exactly `{'clearance': 2}`; this is the unresolved admission failure. Traceback is preserved in `admin.stderr` and complete child logs/results are preserved.

Observed native base DRC had zero physical violations and zero opens. The hostile result had one clearance category and zero opens: Track [TARGET] on F.Cu at (10.0, 10.0) was 0.2100 mm from Pad 3 [LEFT] of X1, against the 0.2500 mm clearance rule. No schematic/parity invocation occurred. No live project files were written; no maintained regression or production repair was installed. Original checker hash remained `cb0d0cf6cb593b5f231fa372920e7dc6adf10bce95c0d734fac0900d3fd3ddf3` before and after every child.

Unresolved rows: hostile native expected two clearance findings but measured one; therefore diagnostic admission is FAIL and no downstream acceptance follows.
