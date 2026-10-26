# Controlled prototype assembly and inspection plan

Design-stage instruction only, not authorization to assemble or evidence that
any test passed. AuthorAstra,2026-10-05. Exactsourcecohort and independent
sourcing review bind this plan. Quantity5carriers+40pods; no assumedyield/spares.

## Original Pico variant SC0915-CROW-D1OFF-R3

Incomingpart must be originalRP2040 PicoSC0915, notPicoH/W/2. Match actualPCB
revision/powersection to retained officialRev3 publicschematic
01_docs/evidence/reviews/ft-evidence/RPI-PICO-R3-PUBLIC-SCHEMATIC.pdf.
Record supplier/lot/modulemarking/revision and close-up before/afterphotos linked
to carrier serial. Ifrevision/identity/topology differs, quarantine and reopen
engineering review; do not apply these steps by silkscreen name alone.

A qualified assembler removes only the MODULE D1 MBR120VLSFT1G betweenVBUS
andVSYS. Do not confuse with carrierD1(TVS),D2(isolation) orD3(inputdiode).
Preserve allotherPico components, especially R10=5.6k1%,R1=10k1% GPIO24sense
divider, USBconnector/data parts andVSYScapacitor. Inspect pads forlifting,
bridges/debris/damage; verify no remainingdiode/solderpath betweenformerD1pads.
Retain modification record and label/segregate modifiedmodules; never allow an
unmodifiedSC0915to substitute silently. Verify before solderingmodule tocarrier.

Unpowered electrical inspection uses diode/ohms checks inbothpolarities for
VBUS-to-VSYS path, comparedwiththepublished circuit; capacitive/transientreadings
are notautomatically shorts. Do not claim infinite resistance orremoveVBUSsense
to force a reading. Unexpected steady low-impedance conduction is FAIL and
quarantine. Microscopicproof ofD1absence +electricalpathcheck arebothrequired.

Future first-article QA afterauthorizedassembly: USB-only with12Vabsent must not
operate acquisition/buzzers; logVSYS/3V3 voltage,current anddecay, notzero-leakage
assumptions.12V-only muststart localrails; bothinputsmustremainself-poweredwith
ordinaryUSBattach. Remove/reapply12V whileUSBremains; confirmno sustainedUSB
operatingbackfeed. TestVBUSsense andUSBdisconnect/reset/buzzerdefaultoff across
the specified source envelope. Actual testfixture/thresholds require owning
first-article review beforeexecution; no fabricated measuredresultor USBrail
injection limit is asserted. Firmware holds are separate, not hardwarepower fixes.

## Other controlled assemblies

ExactSMT identities/footprints are in sourcing/exact-parts.csv andpartdossiers.
Western-sourcedparts imply a supplied-part/manualroute, notautomaticJLCturnkey
availability. Confirm vendorprocess/quotes beforefabrication/purchase. Pico
castellations, RECOM/jacks, mic andbuzzer requireappropriate controlledmanual
assembly. No presentvendorcommitment orphysicalrework is claimed.

J1DCjack pad1centerpositive,2sleeveGND,3switchunused. Confirmactual matingplug
diameter/depth/polarity againstSameSky drawingandselectedadapter beforeconnection.
Polarity: VishaySS34SMCcathodebandpad1;1N5819SOD123pad1cathode;SMBJpad1cathode;
BZT52pad1cathode. BAT54Sseriespackage1loweranodeGND,2uppercathoderail,3midpoint.
Checkactualmaker pin1marksandviewconvention againstretainedprimary drawings.

CMA4544pin2ground/case hasgreenundersidemark; bodyoffsetfromleadmidpoint2mm
isretained. Hand solder, protect acousticport,noliquidwash; actualenclosure
membrane/cavity isnotselected. CPE203physicalplus-markedleadgoestoboardpad1/12V;
negativepad2switchedlow. Ifmarksabsent/ambiguousquarantine, donotinferpolarity
from symmetric12mmspacing. Handsolderonly,noreflow/wave/wash/IPclaim.

Verifycorrect330ohmhighpowerR14 presenton everypod; its rail-sinkfunctionis
essential.1kR9/R10 highpowerorderingmustnotbe replacedwith standard0.10W0603
withoutnewreview. Capacitor substitutions mustretainreviewedeffectivevalue/ESR
models,notjustnominalmarking. Differentlot/rework reopensprototypecapacitor
qualification. External3Dmodelsandfullmatingmechanicalclearancesarenotfrozen.

## Harness and deployment QA

All40cables mustpass100%continuity/pair/no-shortcheck withstraight-through1..8
mapping; noCCA/crossover/PoE/networkequipment. Pair1/2audio,3/6powerreturn,
4/5powerreturn,7/8buzzerreturn. Label eachcarrierport/pod/leadwithchannelID and
NON-ETHERNET/NO PoE. Measure actualhot-resistancecontract androutedlength before
use. Enclosedunshieldedjack, glands,strainrelief/driploops andweather/acoustic
qualificationremainmechanicaltasks. Powerofftomate; nolightningclaim.

These are futureinspection/qualificationrequirements. Schematicacceptance does
not authorize theirphysicalexecution orcertifythat actualvendor/parts/site comply.
