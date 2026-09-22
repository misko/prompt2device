# Coordinator disposition of initial research

Both Sol reports are retained exactly as delivered. They are research evidence,
not new engineering authority. Their citations include the local working-copy
paths used in the research; immutable input snapshots remain in the isolated
research campaign.

The requirements task delivery passed its exact runtime packet/scope checks.
The USB research task delivery was INCOMPLETE because its result.json was
written beside the outputs directory instead of inside it. Preserve that
receipt. The research conclusions are independently considered on their source
evidence; the failed delivery is not retroactively changed to PASS.

The preferred continued-design candidate is XU316-1024-TQ128-C24. Root verified
its official package data identifies USB_DM pin 59, USB_DP pin 60, XIN pin 34 and XOUT pin 33 and that
bottom I/O (including crystal/JTAG) is always 1.8 V. Other I/O domains need their
exact voltage/strap decision. Reference:
https://www.xmos.com/documentation/XM-014532-PC/html/rst/XU316-1024-TQ128.html
No all-3.3 V GPIO assumption is permitted.

The USB research sentence asserting an additional asynchronous feedback endpoint
is not adopted as a capture-only descriptor requirement. Exact endpoint topology
must come from the selected input-only UAC2 implementation and its reviewed
configuration; do not add a playback feedback endpoint by analogy.

Likewise, physical evaluation-board capture is useful risk reduction and later
first-article evidence, not a newly imposed purchase requirement before hardware
source drafting. Hardware design acceptance, firmware source/build evidence and
physical validation remain distinct. No evaluation hardware was ordered.

Proceed with a conditional XU316 hardware dossier and selective retained-analog
source packet in separate Sol workspaces. Do not freeze the complete schematic
until firmware authorization/configuration ownership, pin/resource map and power
requirements are resolved. Q1 remains a documented existing-Crow default for
reversible hardware preparation; Q2 remains required before firmware work.
