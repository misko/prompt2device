"""Ideal matched-op-amp calculations; not an electrical design guarantee."""

from __future__ import annotations

import math
from numbers import Real


def adc_inverting_filter(f_hz: float, input_ohm: float, feedback_ohm: float,
                         isolation_ohm: float, feedback_f: float,
                         differential_f: float,
                         adc_differential_ohm: float) -> complex:
    """Return differential ADC-pin voltage divided by differential input voltage.

    Model: each feedback resistor senses its ADC pin (after the isolation
    resistor); each feedback capacitor connects the op-amp output (before
    isolation) to its summing node. The ADC resistance and capacitor bridge
    the pins. Op amps are ideal/matched and ADC resistance is constant.
    Source coupling, bias, op-amp limits, parasitics, and ADC dynamics are
    excluded; this is only the linear small-signal transfer of that topology.
    """
    values = {
        "f_hz": f_hz,
        "input_ohm": input_ohm,
        "feedback_ohm": feedback_ohm,
        "isolation_ohm": isolation_ohm,
        "feedback_f": feedback_f,
        "differential_f": differential_f,
        "adc_differential_ohm": adc_differential_ohm,
    }
    for name, value in values.items():
        if (isinstance(value, bool) or not isinstance(value, Real)
                or not math.isfinite(value)
                or (value < 0 if name == "f_hz" else value <= 0)):
            raise ValueError(f"{name} must be finite and "
                             + ("nonnegative" if name == "f_hz" else "positive"))

    s = 2j * math.pi * f_hz
    rf, rout, radc = feedback_ohm, isolation_ohm, adc_differential_ohm
    denominator = (1 + s * feedback_f * (rf + rout + 2 * rf * rout / radc)
                   + s * s * 2 * rf * rout * feedback_f * differential_f)
    return -(rf / input_ohm) / denominator
