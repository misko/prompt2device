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

export const Pptc = () => <footprint>
  <smtpad portHints={["1"]} pcbX="-3.3875mm" pcbY="0mm" width="1.925mm" height="5.45mm" shape="rect" rectBorderRadius="0.25mm" />
  <smtpad portHints={["2"]} pcbX="3.3875mm" pcbY="0mm" width="1.925mm" height="5.45mm" shape="rect" rectBorderRadius="0.25mm" />
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
