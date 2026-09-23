#!/usr/bin/env python3
"""Executable checks for the exact-Circuit-JSON human schematic renderer."""

import json
import hashlib
import pathlib
import sys
import tempfile

from harness import check, contains, main, run, test


ROOT = pathlib.Path(__file__).resolve().parents[1]
RENDERER = ROOT / "skills/kicad-pcb/scripts/render_schematic_pdf.mjs"
ALIGNER = RENDERER
TOOLCHAIN = ROOT / 'projects/crow-audio-carrier-v1/03_tscircuit/package.json'


def component(number, sheet_id=None):
    source_id = f"source_component_{number}"
    schematic_id = f"schematic_component_{number}"
    source = {
        "type": "source_component",
        "source_component_id": source_id,
        "ftype": "simple_chip",
        "name": f"U{number + 1}",
    }
    schematic = {
        "type": "schematic_component",
        "schematic_component_id": schematic_id,
        "center": {"x": number * 3, "y": 0},
        "rotation": 0,
        "size": {"width": 2, "height": 1},
        "source_component_id": source_id,
    }
    if sheet_id is not None:
        schematic["schematic_sheet_id"] = sheet_id
    text = {
        "type": "schematic_text",
        "schematic_text_id": f"schematic_text_{number}",
        "schematic_component_id": schematic_id,
        "text": f"U{number + 1}",
        "anchor": "center",
        "rotation": 0,
        "position": {"x": number * 3, "y": 0},
        "font_size": 0.18,
    }
    if sheet_id is not None:
        text["schematic_sheet_id"] = sheet_id
    return [source, schematic, text]


def render(circuit, aliases=None, extra_args=None):
    tmp = tempfile.TemporaryDirectory()
    directory = pathlib.Path(tmp.name)
    source = directory / "circuit.json"
    output = directory / "schematic.pdf"
    source.write_text(json.dumps(circuit))
    source_before = hashlib.sha256(source.read_bytes()).hexdigest()
    command = ["node", str(RENDERER), str(source), str(output),
               "--title", "FIXTURE", "--toolchain-package", str(TOOLCHAIN)]
    if aliases is not None:
        alias_path = directory / "net_aliases.txt"
        alias_path.write_text(aliases)
        command += ["--net-aliases", str(alias_path)]
    command += extra_args or []
    result = run(command)
    source_after = hashlib.sha256(source.read_bytes()).hexdigest()
    return tmp, output, result, source_before, source_after


@test("opt-in detail tiles keep exact circuit bytes and labeled source-sheet coverage")
def t_detail_tiles():
    circuit = [
        {"type": "schematic_sheet", "schematic_sheet_id": "schematic_sheet_0",
         "name": "dense", "display_name": "DENSE", "sheet_index": 1},
        *component(0, "schematic_sheet_0"),
        *component(1, "schematic_sheet_0"),
    ]
    tmp, output, result, before, after = render(
        circuit, extra_args=["--detail-tiles", "dense:2"])
    try:
        check(result.rc == 0, result.out)
        check(before == after, "detail rendering modified authoritative Circuit JSON")
        info = run(["pdfinfo", str(output)])
        contains(info.out, "Pages:           5", "overview and four detail pages")
        detail = run(["pdftotext", "-f", "2", "-l", "5", str(output), "-"])
        contains(detail.out, "source sheet 1 schematic_sheet_0", "source-sheet caption")
        contains(detail.out, f"SHA-256 {before[:16]}", "exact input hash caption")
        contains(detail.out, "overview page 1", "overview continuation")
        contains(detail.out, "U1", "first source label in detail coverage")
        contains(detail.out, "U2", "second source label in detail coverage")
    finally:
        tmp.cleanup()


@test("detail tile options fail closed before publishing a PDF", kind="known_bad")
def t_detail_tiles_bad_options():
    circuit = [{"type": "schematic_sheet", "schematic_sheet_id": "schematic_sheet_0",
                "name": "dense", "sheet_index": 1},
               *component(0, "schematic_sheet_0")]
    for options in (["--detail-tiles", "missing:2"],
                    ["--detail-tiles", "dense:4"],
                    ["--detail-tiles", "dense:2", "--detail-tiles", "dense:2"]):
        tmp, output, result, _, _ = render(circuit, extra_args=options)
        try:
            check(result.rc != 0, f"bad options accepted: {options}")
            check(not output.exists(), "failed detail render published a PDF")
        finally:
            tmp.cleanup()


@test("scaled two-port alignment lands symbol terminals on original trace endpoints")
def t_scaled_symbol_alignment():
    script = f"""
      import {{ alignScaledTwoPortSymbols }} from {json.dumps(ALIGNER.as_uri())}
      const original = [
        {{
          type: "schematic_component",
          schematic_component_id: "schematic_component_0",
          symbol_name: "fixture",
          center: {{ x: 10, y: 20 }},
        }},
        {{
          type: "schematic_port",
          schematic_port_id: "schematic_port_0",
          schematic_component_id: "schematic_component_0",
          center: {{ x: 10, y: 19.7 }},
        }},
        {{
          type: "schematic_port",
          schematic_port_id: "schematic_port_1",
          schematic_component_id: "schematic_component_0",
          center: {{ x: 10, y: 20.3 }},
        }},
      ]
      const before = JSON.stringify(original)
      const symbols = {{
        fixture: {{
          center: {{ x: 0, y: 0 }},
          ports: [{{ x: 0, y: -0.5 }}, {{ x: 0, y: 0.5 }}],
        }},
      }}
      const result = alignScaledTwoPortSymbols(original, symbols)
      const component = result.circuit[0]
      const ports = result.circuit.slice(1)
      const scale = 0.6
      const anchor = symbols.fixture.ports[1]
      const translation = {{
        x: ports[1].center.x - anchor.x,
        y: ports[1].center.y - anchor.y,
      }}
      const projected = symbols.fixture.ports.map((port) => ({{
        x: scale * port.x + translation.x,
        y: scale * port.y + translation.y,
      }}))
      console.log(JSON.stringify({{
        count: result.correctionCount,
        residual: result.maximumResidual,
        inputUnchanged: before === JSON.stringify(original),
        component,
        projected,
      }}))
    """
    result = run(["node", "--input-type=module", "--eval", script])
    check(result.rc == 0, result.out)
    payload = json.loads(result.out)
    check(payload["count"] == 1, "expected one scaled-symbol correction")
    check(payload["inputUnchanged"], "alignment mutated authoritative input")
    check(payload["residual"] < 1e-9, "alignment residual was not negligible")
    check(abs(payload["projected"][0]["y"] - 19.7) < 1e-9,
          "lower symbol terminal missed original endpoint")
    check(abs(payload["projected"][1]["y"] - 20.3) < 1e-9,
          "upper symbol terminal missed original endpoint")


@test("multi-sheet renderer fits exact Circuit JSON into one PDF page per sheet")
def t_multi_sheet():
    circuit = [
        {
            "type": "schematic_sheet",
            "schematic_sheet_id": "schematic_sheet_0",
            "name": "input",
            "display_name": "INPUT",
            "sheet_index": 1,
        },
        {
            "type": "schematic_sheet",
            "schematic_sheet_id": "schematic_sheet_1",
            "name": "output",
            "display_name": "OUTPUT",
            "sheet_index": 2,
        },
        *component(0, "schematic_sheet_0"),
        *component(1, "schematic_sheet_1"),
    ]
    tmp, output, result, source_before, source_after = render(circuit)
    try:
        check(result.rc == 0, result.out)
        check(output.stat().st_size > 1000, "renderer did not create a real PDF")
        contains(result.out, "page 1/2: INPUT", "first-page progress")
        contains(result.out, "page 2/2: OUTPUT", "second-page progress")
        contains(result.out, "landscape", "page-fit disclosure")
        check(source_before == source_after, "renderer modified its exact input")
        info = run(["pdfinfo", str(output)])
        check(info.rc == 0, info.out)
        contains(info.out, "Pages:           2", "multi-page PDF page count")
    finally:
        tmp.cleanup()


@test("single-sheet legacy Circuit JSON remains renderable")
def t_legacy_single_sheet():
    tmp, output, result, _, _ = render(component(0))
    try:
        check(result.rc == 0, result.out)
        info = run(["pdfinfo", str(output)])
        contains(info.out, "Pages:           1", "legacy page count")
    finally:
        tmp.cleanup()


@test("human PDF uses canonical net names without modifying Circuit JSON")
def t_canonical_net_names():
    circuit = component(0)
    circuit += [
        {
            "type": "source_net",
            "source_net_id": "source_net_0",
            "name": "N5V_INTERNAL",
        },
        {
            "type": "schematic_net_label",
            "schematic_net_label_id": "schematic_net_label_0",
            "text": "N5V_INTERNAL",
            "source_net_id": "source_net_0",
            "anchor_position": {"x": 1, "y": 0},
            "center": {"x": 1.5, "y": 0},
            "anchor_side": "left",
        },
    ]
    tmp, output, result, source_before, source_after = render(
        circuit, "N5V_INTERNAL 5V_CANONICAL\n"
    )
    try:
        check(result.rc == 0, result.out)
        contains(result.out, "1 explicit net alias(es)", "alias disclosure")
        check(source_before == source_after, "alias render modified Circuit JSON")
        text = run(["pdftotext", str(output), "-"])
        check(text.rc == 0, text.out)
        contains(text.out, "5V_CANONICAL", "canonical label in PDF")
        check("N5V_INTERNAL" not in text.out,
              "authoring-only net name leaked into PDF")
    finally:
        tmp.cleanup()


@test("explicit-wire net text is canonicalized but notes and custom text are not")
def t_inline_net_names():
    circuit = component(0)
    circuit += [
        {"type": "source_net", "source_net_id": "source_net_0", "name": "N5V_INTERNAL"},
        {"type": "source_trace", "source_trace_id": "source_trace_0",
         "connected_source_port_ids": [], "connected_source_net_ids": ["source_net_0"]},
    ]
    for i, (value, trace) in enumerate([
        ("N5V_INTERNAL", "source_trace_0"),
        ("N5V_INTERNAL", None),
        ("N12V_CUSTOM_NOTE", "source_trace_0"),
        ("N5V_INTERNAL", "missing_trace"),
    ]):
        circuit.append({"type": "schematic_text", "schematic_text_id": f"inline_{i}",
                        "text": value, "source_trace_id": trace, "anchor": "center",
                        "position": {"x": 0, "y": 2 + i}, "rotation": 0, "font_size": 0.18})
    tmp, output, result, before, after = render(circuit, "N5V_INTERNAL 5V_CANONICAL\n")
    try:
        check(result.rc == 0, result.out)
        check(before == after, "inline render changed exact input")
        text = run(["pdftotext", str(output), "-"])
        check(text.rc == 0, text.out)
        check(text.out.count("5V_CANONICAL") == 1, "missing/overbroad inline alias")
        check(text.out.count("N5V_INTERNAL") == 2, "note/orphan trace was rewritten")
        contains(text.out, "N12V_CUSTOM_NOTE", "custom annotation preserved")
    finally:
        tmp.cleanup()


@test("leading-N digit convention is canonicalized without an explicit alias")
def t_implicit_digit_alias():
    circuit = component(0)
    circuit.append({
        "type": "schematic_net_label",
        "schematic_net_label_id": "schematic_net_label_0",
        "text": "N12V_AUX",
        "anchor_position": {"x": 1, "y": 0},
        "center": {"x": 1.5, "y": 0},
        "anchor_side": "left",
    })
    tmp, output, result, _, _ = render(circuit)
    try:
        check(result.rc == 0, result.out)
        text = run(["pdftotext", str(output), "-"])
        contains(text.out, "12V_AUX", "implicit canonical label")
        check("N12V_AUX" not in text.out,
              "leading-N authoring syntax leaked into PDF")
    finally:
        tmp.cleanup()


@test(
    "multi-sheet renderer rejects an unowned component instead of silently omitting it",
    kind="known_bad",
)
def t_unowned_component():
    circuit = [
        {
            "type": "schematic_sheet",
            "schematic_sheet_id": "schematic_sheet_0",
            "name": "input",
            "display_name": "INPUT",
            "sheet_index": 1,
        },
        *component(0),
    ]
    tmp, output, result, _, _ = render(circuit)
    try:
        check(result.rc != 0, "unowned component was silently accepted")
        contains(result.out, "no valid sheet owner", "ownership failure")
        check(not output.exists(), "failed render left a PDF behind")
    finally:
        tmp.cleanup()


@test("tall sheets select portrait fit without changing schematic coordinates")
def t_portrait_fit():
    circuit = component(0) + component(1)
    for element in circuit:
        if element.get("schematic_component_id") == "schematic_component_1":
            point = element.get("center") or element.get("position")
            if point:
                point["x"] = 0
                point["y"] = 10
    tmp, output, result, source_before, source_after = render(circuit)
    try:
        check(result.rc == 0, result.out)
        contains(result.out, "portrait", "portrait page-fit disclosure")
        check(source_before == source_after, "renderer modified portrait input")
        info = run(["pdfinfo", str(output)])
        contains(info.out, "607.5 x 900 pts", "portrait A-series aspect")
    finally:
        tmp.cleanup()


@test("zero-component input is a hard failure, never an empty pass", kind="known_bad")
def t_zero_components():
    tmp, output, result, _, _ = render([])
    try:
        check(result.rc != 0, "zero-component input passed")
        contains(result.out, "zero schematic components", "zero-component failure")
        check(not output.exists(), "failed render left a PDF behind")
    finally:
        tmp.cleanup()


@test("font-metric baselines preserve non-text geometry, content and rotated anchors")
def t_materialized_baselines():
    script = f'''
      import {{ materializeTextBaselines }} from {json.dumps(RENDERER.as_uri())};
      const metrics = {{unitsPerEm:1000, ascender:1069, descender:-293, xHeight:536}};
      const baselines = ["central","middle","hanging","ideographic","text-before-edge","text-after-edge"];
      const tree = {{name:"svg",attributes:{{}},children:[
        {{name:"path",attributes:{{d:"M 0 0 L 10 0",stroke:"green"}},children:[]}},
        ...baselines.map((b,i)=>({{name:"text",attributes:{{x:"100",y:"100",dy:"2",
          transform:`rotate(${{i*90}} 100 100)`,"font-size":"20px","dominant-baseline":b}},
          children:[{{type:"text",value:"ADC_MCLK 300Ω"}}]}}))]}};
      const before = JSON.stringify(tree);
      const normalized = materializeTextBaselines(tree, ()=>metrics);
      const deltas = normalized.tree.children.slice(1).map(n=>Number(n.attributes.dy)-2);
      const expected = [7.76,5.36,17.104,-5.86,21.38,-5.86];
      if (deltas.some((v,i)=>Math.abs(v-expected[i])>1e-9)) throw new Error("wrong metrics");
      if (before!==JSON.stringify(tree)) throw new Error("source AST mutated");
      normalized.tree.children.slice(1).forEach((n,i)=>{{
        if(n.attributes.x!=="100"||n.attributes.y!=="100"||
          n.attributes.transform!==`rotate(${{i*90}} 100 100)`||
          n.children[0].value!=="ADC_MCLK 300Ω") throw new Error("anchor/content changed");
      }});
      if(JSON.stringify(normalized.tree.children[0])!==JSON.stringify(tree.children[0])) throw new Error("wire changed");
      console.log(normalized.corrections);
    '''
    result = run(['node', '--input-type=module', '--eval', script])
    check(result.rc == 0, result.out)
    check(result.out.strip() == '6', 'missing baseline denominator')


@test("baseline conversion rejects unsupported units and invalid font metrics", kind="known_bad")
def t_bad_baseline_inputs():
    script = f'''
      import {{ materializeTextBaselines }} from {json.dumps(RENDERER.as_uri())};
      const good={{unitsPerEm:1000,ascender:1069,descender:-293,xHeight:536}};
      const fixtures=[
        [{{"font-size":"20%","dominant-baseline":"central"}},good],
        [{{"font-size":"20px","dominant-baseline":"unrecognized"}},good],
        [{{"font-size":"20px","dominant-baseline":"central",dy:"2em"}},good],
        [{{"font-size":"20px","dominant-baseline":"central"}},{{...good,xHeight:NaN}}],
      ];
      let rejected=0;
      for (const [attributes,metrics] of fixtures) {{
        try {{ materializeTextBaselines({{name:"text",attributes,children:[]}},()=>metrics); }}
        catch {{ rejected++; }}
      }}
      if(rejected!==4) throw new Error(`only ${{rejected}}/4 rejected`);
      console.log("4/4 rejected");
    '''
    result = run(['node', '--input-type=module', '--eval', script])
    check(result.rc == 0, result.out)


@test("rasterized label and passive value clear their graphic borders")
def t_rasterized_baselines():
    from PIL import Image
    with tempfile.TemporaryDirectory() as directory:
        base = pathlib.Path(directory)
        svg, png = base / 'fixture.svg', base / 'fixture.png'
        script = f'''
          import fs from "node:fs";
          import {{createRequire}} from "node:module";
          import {{ materializeTextBaselines }} from {json.dumps(RENDERER.as_uri())};
          const require=createRequire({json.dumps(str(TOOLCHAIN))});
          const {{parseSync,stringify}}=require("svgson");
          const input=`<svg xmlns="http://www.w3.org/2000/svg" width="500" height="260">
            <rect width="500" height="260" fill="white"/>
            <rect x="20" y="50" width="330" height="56" stroke="red" stroke-width="2" fill="none"/>
            <text x="40" y="78" font-family="Noto Sans" font-size="48" dominant-baseline="central">CLK_10kΩ</text>
            <rect x="200" y="193" width="45" height="14" stroke="red" stroke-width="2" fill="none"/>
            <text x="200" y="210" font-family="Noto Sans" font-size="20" dominant-baseline="hanging">300Ω</text>
          </svg>`;
          const {{tree}}=materializeTextBaselines(parseSync(input),()=>({{unitsPerEm:1000,ascender:1069,descender:-293,xHeight:536}}));
          fs.writeFileSync({json.dumps(str(svg))},stringify(tree));
        '''
        result = run(['node', '--input-type=module', '--eval', script])
        check(result.rc == 0, result.out)
        result = run(['rsvg-convert','-f','png','-o',str(png),str(svg)])
        check(result.rc == 0, result.out)
        with Image.open(png) as loaded:
            image = loaded.convert('RGB')
            label_y = [y for y in range(30,125) for x in range(30,345)
                       if max(image.getpixel((x,y))) < 80]
            value_y = [y for y in range(175,250) for x in range(190,290)
                       if max(image.getpixel((x,y))) < 80]
        check(bool(label_y) and min(label_y) > 51 and max(label_y) < 105,
              f'label touches outline: {min(label_y) if label_y else None}/{max(label_y) if label_y else None}')
        check(bool(value_y) and min(value_y) > 208, 'passive value collides with lower body')


@test("renderer refuses ambient toolchain fallback outside a project", kind="known_bad")
def t_no_ambient_toolchain():
    with tempfile.TemporaryDirectory() as directory:
        source = pathlib.Path(directory) / 'circuit.json'
        output = pathlib.Path(directory) / 'schematic.pdf'
        source.write_text(json.dumps(component(0)))
        result = run(['node',str(RENDERER),str(source),str(output)])
        check(result.rc != 0, 'renderer silently used ambient CLI')
        contains(result.out, 'no project-local toolchain package', 'toolchain diagnostic')
        check(not output.exists(), 'missing toolchain left output')


if __name__ == "__main__":
    sys.exit(main())
