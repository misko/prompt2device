"""Conditional prototype calculations; not device guarantees or acceptance."""
import cmath
import itertools
import math

S_MIN, S_MAX = -0.63, 4.23
P_MIN, P_MAX = -1.1, 4.4
VC_MIN, VC_MAX = S_MIN-P_MAX, S_MAX-P_MIN
RP, RC = 1000., 2700.
RC_MIN = .99*RC
# Ground shunts connect to carrier ground or pod return displaced +/-30mV.
G_MIN, G_MAX = -.03, .03
# Deliberately bounded prototype allowances, not all-temperature datasheet max.
LEAK_PER_DEVICE = 10e-6
ESD_CAP_PER_DEVICE = 100e-12
CABLE_PAIR_CAP = 336e-12

def bounds():
    t_min, t_max = P_MIN+VC_MIN, P_MAX+VC_MAX
    # X lies between the active sources S, T=P+Vc, and the two ground
    # references for any passive, memoryless connector shunt. Independent
    # previously charged cable capacitance starts inside the source envelope.
    excursion = max(S_MAX-t_min, t_max-S_MIN, G_MAX-t_min, t_max-G_MIN)
    branch = excursion/RC_MIN
    conservative = branch+2*LEAK_PER_DEVICE
    rail = 2*conservative*(330*1.01)
    assert conservative < .005
    assert rail < 3.6
    return dict(cap_history_V=(VC_MIN,VC_MAX), excursion_V=excursion,
                ADC_branch_A=branch, allowance_A=conservative,
                off_rail_V=rail)

def transfer(f, rc=RC, extra=2*ESD_CAP_PER_DEVICE):
    # Symmetric differential half-circuit: pair capacitance becomes 2*Cpair
    # to ground per leg. Typical ADC10k and nominal grounded2.2nF remain
    # conditional; this reports incremental port-loading, not THD/noise proof.
    w=2*math.pi*f
    zp=1/(1/10000+1j*w*2.2e-9)
    downstream=1/(1j*w*1e-6)+rc+zp
    zx=1/(1/downstream+1j*w*(2*CABLE_PAIR_CAP+extra))
    return zx/(RP+zx)*zp/downstream

def port(s,t,rp,rc,g,low,high,rd):
    x=(s/rp+t/rc)/(1/rp+1/rc)
    knee=g+low if x<g+low else g+high if x>g+high else None
    if knee is not None:
        x=(s/rp+t/rc+knee/rd)/(1/rp+1/rc+1/rd)
    return x

def invariant_check():
    # Corner checks corroborate, rather than replace, the scalar proof in
    # ROOF-INTERFACE.md. Thresholds deliberately vary widely; no5.5V knee.
    worst=0.
    for s,p,vc,rp,rc,g,low,high,rd in itertools.product(
            (S_MIN,0.,S_MAX),(P_MIN,0.,P_MAX),(VC_MIN,0.,VC_MAX),
            (.99*RP,1.01*RP),(.99*RC,1.01*RC),(G_MIN,G_MAX),
            (-1.2,-.05),(4.3,5.,8.5),(.5,10.)):
        t=p+vc;x=port(s,t,rp,rc,g,low,high,rd)
        i=(x-t)/rc;worst=max(worst,abs(i))
        assert abs(i)<=bounds()['ADC_branch_A']+1e-12
        if vc==VC_MIN: assert i>=-1e-12
        if vc==VC_MAX: assert i<=1e-12
    return worst

if __name__=='__main__':
    print(bounds());print('sampled branch max A',invariant_check())
    print('typical midband',10000/(10000+RP+RC),
          'delta_dB',20*math.log10((10000+RP+1800)/(10000+RP+RC)))
    for f in (300,1000,8000):
        h=transfer(f);old=transfer(f,1800,0.)
        esd_delta=h/transfer(f,RC,0.)
        print(f,'Hz gain_dB',20*math.log10(abs(h)),
              'phase_deg',math.degrees(cmath.phase(h)),
              'vs repair6_dB',20*math.log10(abs(h/old)),
              'ESD_only_phase_deg',math.degrees(cmath.phase(esd_delta)))
    thermal=math.sqrt(4*1.380649e-23*333.15*(8000-300)*2*(RP+RC))
    print('series-resistor open-circuit differential thermal V_RMS',thermal)
