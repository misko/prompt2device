# Crow USB connector fact and selection record

Date: 2026-09-22. Scope: source-authority facts and bounded engineering
selections only. This record does not establish realized placement, enclosure
registration, populated-neighbor clearance, cross-vendor mating qualification,
or physical first-article acceptance.

## USB device

Primary authorities are the GCT USB4105 drawing rev B4 and product
specification rev A3, and the ASSMANN drawing ASS 7348 CA rev08. Captured local
copies accompany this record.

- GCT drawing: <https://gct.co/files/drawings/usb4105.pdf>
- GCT specification: <https://gct.co/files/specs/usb4105-spec.pdf>
- GCT product page: <https://gct.co/connector/usb4105>
- ASSMANN drawing: <https://www.assmann-wsw.com/uploads/datasheets/ASS_7348_CA.pdf>
- ASSMANN exact product page:
  <https://www.assmann-wsw.com/en/product/a-usb31c-20a-100/>

The receptacle drawing gives 7.35 mm body length, 8.94 mm overall width and
3.31 mm mounted profile. The candidate uses a conservative 7.73 x 9.32 x
3.69 mm body envelope by applying the drawing's ±0.38 mm whole-millimetre
general tolerance to all three dimensions. This is an intentionally containing
bound, not a new manufacturer dimension.

The ASSMANN Type-C end has a 24 mm body/boot axial extent, 6.65 ±0.15 mm
exposed shell, 11 mm moulded-body width and 6.5 mm thickness. Applying the
drawing tolerances yields a conservative complete plug envelope of 31.80 x
12.00 x 7.00 mm. The hand-grip bound uses 18.10 mm axial length and a 13.90 mm
circumscribed diameter around the 12 x 7 mm maximum transverse rectangle.
The GCT specification's explicit mating/unmating forces establish a friction
retention interface with no threaded tightening or torque tool.

Neither exact source gives operating bend radius or minimum straight service
run, and neither manufacturer names the other exact order number as a qualified
mate. Cable routing, complete-pair fit and populated service remain unknown.

## Eight RJ45 spoke connectors

Primary authorities are the Würth 615008160221 drawing rev 001.003 and the
Weidmüller exact item page for 8909650150 / IE-C6ES8UG0150A40A40-E.

- Würth drawing:
  <https://www.we-online.com/components/products/datasheet/615008160221.pdf>
- Weidmüller exact item:
  <https://eshop.weidmueller.com/en/ie-c6es8ug0150a40a40-e/p/8909650150>

The Weidmüller cable is a 15 m, straight, shielded RJ45-IP20-to-RJ45-IP20
S/FTP PUR assembly with 6.1–6.5 mm OD. Its repeated bend-radius floor is ten
times OD and its one-time floor is five times OD. The candidate conservatively
uses the maximum 6.5 mm OD, a 65 mm repeated bend radius, and a 65 mm straight
service run before bending. The straight run is a project service allowance,
not a manufacturer minimum.

The documents align at the generic 8P8C/RJ45 interface but do not qualify this
exact cross-manufacturer pair. Würth explicitly withholds reliability assurance
with other manufacturers' counterparts. The jack's free EMI fingers also
extend beyond its nominal body dimensions. Mate envelope, exact compatibility,
grip, latch clearance, reaction, populated operation and tolerance stack remain
unknown. No separate final tool or torque tightening is selected for the
push-in modular plug.

## External power

Primary authority is the Molex 43650 series drawing rev D8 and current Molex
part records.

- Header drawing:
  <https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/436/43650/436501000_sd.pdf>
- Exact mate housing:
  <https://www.molex.com/en-us/products/part-detail/436450200>
- Exact 18 AWG female terminal:
  <https://www.molex.com/en-us/products/part-detail/430300038>

The selected mate is Molex 43645-0200 populated with two 43030-0038 tin-plated
18 AWG female terminals. This is an exact compatible component set: the 43650
drawing states that the header mates with receptacle series 43645, and Molex
lists 43645-0200 as a polarized, positive-latching 2-circuit receptacle.
Wire length, insulation OD within the terminal limit, termination process,
rear strain relief and external supply termination are still system choices,
so the mate envelope, cable section and populated operation remain unknown.
The latch needs no final torque tool; insertion/extraction reaction and finger
clearance remain unqualified.

## Debug JTAG

Primary authorities are the Samtec FTSH vertical-SMT series print, the FFSD
series print and FFSD catalog. Captured local copies accompany this record.

- Exact header page:
  <https://www.samtec.com/products/ftsh-105-01-l-dv-k>
- Exact selected cable page:
  <https://www.samtec.com/products/ffsd-05-d-06.00-01-n>
- FFSD series print:
  <https://suddendocs.samtec.com/prints/ffsd-xx-x-xx.xx-01-x-x-xxx-mkt.pdf>
- FFSD catalog:
  <https://suddendocs.samtec.com/catalog_english/ffsd.pdf>

The selected direct mate is FFSD-05-D-06.00-01-N: five positions per row,
double ended, 6.00 inch assembled length, lead style 01 and notch polarization.
Samtec identifies FFSD as the cable mate for FTSH lead style -01 and the FTSH
`-K` option as specifically keyed for FFSD. The cable drawing gives ±0.125 inch
length tolerance below 12.5 inches. The connector body dimensions support a
conservative 5.38 x 10.84 x 3.35 mm envelope after adding 0.30 mm to the
nominal 5.08 x 10.54 x 3.05 mm extents. A circumscribed 11.35 mm grip diameter
contains the 10.84 x 3.35 mm transverse rectangle.

Samtec gives no minimum bend radius for this exact assembly, and the target
header identity does not select a debugger or prove end-to-end JTAG pin mapping.
Cable routing, probe-side adapter, populated operation and physical clearance
remain unknown. The polarized friction-fit socket uses no final tightening or
torque tool.

## Coordinator drawing review

The USB Type-C width is 11 mm (ASS 7348 CA page1 C6), not the candidate
14 mm transcription. Including its ±1 mm whole-number tolerance gives12 mm.
The complete plug includes the24mm body/boot plus6.65mm shell projection.
The JTAG candidate body/grip bounds above are withdrawn: the FFSD print
shows an additional -N protrusion (1.02mm REF). Full toleranced keyed extents
are owed, and the live contract marks mate/grip geometry unknown.

Runtime delivery closed INCOMPLETE because its handback included a failed or
incomplete check. Coordinator adoption is limited to the reviewed facts here;
it does not relabel the closed runtime or establish physical qualification.
