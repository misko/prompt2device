import { Fragment } from "react"
/** Exact copper/drill helpers derived from the native FPIDs in the twelve dossiers. */
export const MicroFit2 = () => <footprint>
  <platedhole portHints={["1"]} pcbX="0mm" pcbY="0mm" shape="circular_hole_with_rect_pad"
    holeDiameter="1.02mm" rectPadWidth="1.5mm" rectPadHeight="2.02mm" rectBorderRadius="0.25mm" />
  <platedhole portHints={["2"]} pcbX="3mm" pcbY="0mm" shape="oval"
    outerWidth="1.5mm" outerHeight="2.02mm" holeWidth="1.02mm" holeHeight="1.02mm" />
  {/* KiCad +Y-down (-4.32 mm) becomes tscircuit +Y-up (+4.32 mm). */}
  <hole pcbX="1.5mm" pcbY="4.32mm" diameter="3mm" />
</footprint>

export const NanoFuse451 = () => <footprint>
  <smtpad portHints={["1"]} pcbX="-2.455mm" pcbY="0mm" width="1.96mm" height="3.15mm" shape="rect" rectBorderRadius="0.196mm" />
  <smtpad portHints={["2"]} pcbX="2.455mm" pcbY="0mm" width="1.96mm" height="3.15mm" shape="rect" rectBorderRadius="0.196mm" />
</footprint>

export const Pdi = () => <footprint>
  {[1,2,3,4].map((pin,index) => <Fragment key={pin}><smtpad portHints={[`${pin}`]}
    pcbX="-1.5mm" pcbY={`${0.975-index*0.65}mm`} width="0.7mm" height="0.42mm"
    shape="rect" rectBorderRadius="0.105mm" /></Fragment>)}
  {/* KiCad pad 5 is one fused copper land for manufacturer logical drain pins 5-8. */}
  <smtpad portHints={["5","6","7","8","DRAIN_COMMON"]} shape="polygon" points={[
    {x:-0.4,y:-1.185},{x:1.85,y:-1.185},{x:1.85,y:-0.765},{x:1.31,y:-0.765},
    {x:1.31,y:-0.535},{x:1.85,y:-0.535},{x:1.85,y:-0.115},{x:1.31,y:-0.115},
    {x:1.31,y:0.115},{x:1.85,y:0.115},{x:1.85,y:0.535},{x:1.31,y:0.535},
    {x:1.31,y:0.765},{x:1.85,y:0.765},{x:1.85,y:1.185},{x:-0.4,y:1.185},
  ]} />
</footprint>

export const Smbj = () => <footprint>
  <smtpad portHints={["1"]} pcbX="-2.15mm" pcbY="0mm" width="2.5mm" height="2.3mm" shape="rect" rectBorderRadius="0.25mm" />
  <smtpad portHints={["2"]} pcbX="2.15mm" pcbY="0mm" width="2.5mm" height="2.3mm" shape="rect" rectBorderRadius="0.25mm" />
</footprint>

/** TDK CKG57K MEGACAP 5750 metal-frame recommended land, exact primary ranges:
 * PA 3.90..4.30 mm, PB 1.50..2.00 mm, PC 4.50..5.00 mm. Mid-range land used;
 * body is 6.00 x 5.00 x 3.35 mm. This is not an EIA-2220 chip land. */
export const TdkCkg57KJLead = () => <footprint>
  <smtpad portHints={["1"]} pcbX="-2.925mm" pcbY="0mm" width="1.75mm" height="4.75mm" shape="rect" rectBorderRadius="0.175mm" />
  <smtpad portHints={["2"]} pcbX="2.925mm" pcbY="0mm" width="1.75mm" height="4.75mm" shape="rect" rectBorderRadius="0.175mm" />
  {/* TDK drawing maximum body is 6.5 x 5.5 mm. The courtyard contains that
      body and the 7.60 mm pad span with 0.25 mm outward clearance. */}
  <fabricationnoterect pcbX="0mm" pcbY="0mm" width="6.5mm" height="5.5mm" strokeWidth="0.1mm" />
  <courtyardrect pcbX="0mm" pcbY="0mm" width="8.1mm" height="6.0mm" />
</footprint>
