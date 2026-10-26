"""Supply and loaded-divider arithmetic without inventing missing inputs."""

from __future__ import annotations

import math


def loaded_divider_voltage(source_v: float, top_ohm: float, bottom_ohm: float,
                           pin_source_a: float | None = None) -> float | None:
    """Midpoint voltage; positive pin current injects into the divider node.

    Unknown pin current leaves the loaded voltage unknown. This numerical
    calculation does not qualify a device current or provide a PASS verdict.
    """
    values = {"source_v": source_v, "top_ohm": top_ohm,
              "bottom_ohm": bottom_ohm, "pin_source_a": pin_source_a}
    for name, value in values.items():
        if value is None and name == "pin_source_a":
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite number")
        try:
            finite = math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite or (name in {"top_ohm", "bottom_ohm"} and value <= 0):
            raise ValueError(f"{name} must be finite and resistances positive")
    if pin_source_a is None:
        return None
    total_ohm = top_ohm + bottom_ohm
    if not math.isfinite(total_ohm):
        raise ValueError("calculated resistance is not finite")
    voltage = source_v * (bottom_ohm / total_ohm) + pin_source_a * (
        top_ohm / total_ohm) * bottom_ohm
    if not math.isfinite(voltage):
        raise ValueError("calculated voltage is not finite")
    return voltage


def supply_margin(*, source_min_v: float | None, loop_ohm: float | None,
                  current_max_a: float | None, extra_drop_v: float | None,
                  device_min_v: float | None, assumed: bool = False) -> dict[str, float | str | None]:
    """Return UNKNOWN until every bound is known; assumptions cannot yield PASS."""
    values = {
        "source_min_v": source_min_v,
        "loop_ohm": loop_ohm,
        "current_max_a": current_max_a,
        "extra_drop_v": extra_drop_v,
        "device_min_v": device_min_v,
    }
    if not isinstance(assumed, bool):
        raise ValueError("assumed must be boolean")
    for name, value in values.items():
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number or None")
        if name in {"loop_ohm", "current_max_a", "extra_drop_v"} and value < 0:
            raise ValueError(f"{name} must be nonnegative")
    if any(value is None for value in values.values()):
        return {"status": "UNKNOWN", "node_min_v": None, "margin_v": None}
    node_min_v = source_min_v - loop_ohm * current_max_a - extra_drop_v
    margin_v = node_min_v - device_min_v
    if not math.isfinite(node_min_v) or not math.isfinite(margin_v):
        raise ValueError("calculated voltage is not finite")
    status = "FAIL" if margin_v < 0 else ("CONDITIONAL" if assumed else "PASS")
    return {"status": status, "node_min_v": node_min_v, "margin_v": margin_v}
