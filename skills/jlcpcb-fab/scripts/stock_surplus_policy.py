"""Exact public-stock surplus policy shared by catalog and release gates."""

import re


_XMOS = ("C6362698", "XU316-1024-TQ128-C24")


def parse_policy(assembly, project=None):
    default = assembly.get("public_stock_surplus")
    if type(default) is not int or default < 0:
        raise ValueError("assembly public_stock_surplus must be a nonnegative integer")
    if project is not None and project.name == "crow-usb-carrier-v1" and default != 150:
        raise ValueError("Crow D7 requires 150 default public-stock surplus")
    rows = assembly.get("public_stock_surplus_overrides", [])
    if not isinstance(rows, list):
        raise ValueError("public_stock_surplus_overrides must be a list")
    overrides = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"lcsc", "mpn", "surplus", "directive"}:
            raise ValueError("stock surplus override requires exact lcsc/mpn/surplus/directive")
        code, mpn = row["lcsc"], row["mpn"]
        if (not isinstance(code, str) or not re.fullmatch(r"C\d+", code)
                or not isinstance(mpn, str) or not mpn):
            raise ValueError("stock surplus override has invalid exact identity")
        if (code, mpn) != _XMOS or row["directive"] != "D10":
            raise ValueError("stock surplus override is authorized only for D10 XMOS exact MPN/code")
        if type(row["surplus"]) is not int or row["surplus"] != 0:
            raise ValueError("D10 XMOS stock surplus override must be integer zero")
        if code in overrides:
            raise ValueError("duplicate stock surplus override")
        overrides[code] = {"mpn": mpn, "surplus": 0, "directive": "D10"}
    if overrides:
        if project is None or project.name != "crow-usb-carrier-v1":
            raise ValueError("D10 XMOS override requires the Crow USB carrier project")
        brief = project / "01_docs/BRIEF.md"
        decision = project / "01_docs/decisions/0009-xmos-public-stock-reserve-exception.md"
        if (not brief.is_file() or not decision.is_file() or
                "D10 —" not in brief.read_text() or
                "lets make an exception for xmos and keep going" not in brief.read_text() or
                "status: accepted" not in decision.read_text() or
                "XU316-1024-TQ128-C24, JLC C6362698, reference U_XU only" not in decision.read_text()):
            raise ValueError("D10 XMOS override lacks accepted Crow brief/decision authority")
    return default, overrides


def surplus_for(default, overrides, code, mpn, designators=None):
    override = overrides.get(code)
    if override is None:
        return default
    if mpn != override["mpn"]:
        raise ValueError(f"{code}: stock surplus override MPN identity mismatch")
    if designators is not None and sorted(designators) != ["U_XU"]:
        raise ValueError(f"{code}: D10 stock surplus override applies to U_XU only")
    return override["surplus"]
