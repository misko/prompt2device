#!/usr/bin/env node

// Render the exact schematic elements already present in Circuit JSON.
//
// tscircuit's stock schematic-svg export selects one declared sheet and draws
// its fixed worksheet in global schematic coordinates.  That is useful in the
// editor, but it can make a generated multi-sheet release unreadable when the
// automatic layout spans several global regions.  This renderer filters the
// exact Circuit JSON per declared sheet, fits each page independently, adds a
// traceable header, converts the pages to PDF, and merges them.  It never
// evaluates TSX and therefore cannot diverge electrically from the artifact
// consumed by the netlist and parity gates.

import crypto from "node:crypto"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"
import { execFileSync, spawnSync } from "node:child_process"
import { pathToFileURL } from "node:url"
import { createRequire } from "node:module"

// librsvg 2.58 ignores dominant-baseline. Materialize the SVG baseline in
// local text coordinates using the resolved font's metrics, leaving glyphs,
// rotations, symbols and wires unchanged. Offsets follow the SVG baseline
// fallback metrics: middle uses half x-height; central uses ascent/descent;
// hanging uses 80% of ascent; ideographic uses the descender.
export const materializeTextBaselines = (input, metricsForFont) => {
  const tree = structuredClone(input)
  let corrections = 0
  const walk = (node) => {
    const attrs = node.attributes ?? {}
    if (node.name === "text" && attrs["dominant-baseline"]) {
      const baseline = attrs["dominant-baseline"]
      if (!["auto", "alphabetic", "baseline"].includes(baseline)) {
        const font = metricsForFont(attrs["font-family"] ?? "sans-serif",
          attrs["font-weight"] ?? "normal", attrs["font-style"] ?? "normal")
        if (![font.unitsPerEm, font.ascender, font.descender, font.xHeight].every(Number.isFinite) ||
            font.unitsPerEm <= 0 || font.xHeight <= 0) {
          throw new Error("invalid font baseline metrics")
        }
        const offsets = {
          central: (font.ascender + font.descender) / 2,
          middle: font.xHeight / 2,
          hanging: font.ascender * 0.8,
          ideographic: font.descender,
          "text-before-edge": font.ascender,
          "text-after-edge": font.descender,
        }
        if (!(baseline in offsets)) throw new Error(`unsupported text baseline: ${baseline}`)
        const sizeText = attrs["font-size"] ?? ""
        if (!/^\d+(?:\.\d+)?(?:px)?$/.test(sizeText)) throw new Error(`unsupported font size: ${sizeText}`)
        const size = Number.parseFloat(sizeText)
        const prior = attrs.dy ?? "0"
        if (!/^-?\d+(?:\.\d+)?(?:px)?$/.test(prior)) throw new Error(`unsupported text dy: ${prior}`)
        attrs.dy = String(Number.parseFloat(prior) + size * offsets[baseline] / font.unitsPerEm)
        attrs["dominant-baseline"] = "alphabetic"
        corrections += 1
      }
    }
    for (const child of node.children ?? []) walk(child)
  }
  walk(tree)
  return { tree, corrections }
}

// Presentation-only workaround for circuit-to-svg's scaled-symbol transform.
// circuit-to-svg currently composes translate(a2-a1) then scale(s), which maps
// a terminal to a2 + (s-1)*a1 when s != 1.  Shift a display-only copy by the
// inverse error so the symbol lands on the original trace endpoints.
const pointDistance = (a, b) => Math.hypot(b.x - a.x, b.y - a.y)

const angularDifference = (angle1, angle2) => {
  const a1 = angle1 < 0 ? angle1 + 2 * Math.PI : angle1
  const a2 = angle2 < 0 ? angle2 + 2 * Math.PI : angle2
  const difference = Math.abs(a1 - a2)
  return difference > Math.PI ? 2 * Math.PI - difference : difference
}

// Keep this ordering identical to circuit-to-svg: its transform anchors on
// match[1] and derives scale using match[0].
const matchPorts = (schematicPorts, symbol, component) => {
  const schematicAngles = schematicPorts
    .map((port) => ({
      port,
      angle: Math.atan2(
        port.center.y - component.center.y,
        port.center.x - component.center.x,
      ),
    }))
    .sort((a, b) => a.angle - b.angle)
  const symbolAngles = symbol.ports
    .map((port) => ({
      port,
      angle: Math.atan2(
        port.y - symbol.center.y,
        port.x - symbol.center.x,
      ),
    }))
    .sort((a, b) => a.angle - b.angle)

  const matches = []
  const used = new Set()
  for (const schematic of schematicAngles) {
    let best = null
    for (const candidate of symbolAngles) {
      if (used.has(candidate.port)) continue
      const difference = angularDifference(schematic.angle, candidate.angle)
      if (best === null || difference < best.difference) {
        best = { port: candidate.port, difference }
      }
    }
    if (best !== null && best.difference < Math.PI / 4) {
      matches.push({ schematicPort: schematic.port, symbolPort: best.port })
      used.add(best.port)
    }
  }
  return matches
}

export const alignScaledTwoPortSymbols = (circuit, symbols) => {
  const portsByComponent = new Map()
  for (const element of circuit) {
    if (
      element.type !== "schematic_port" ||
      !element.schematic_component_id ||
      !element.center
    ) {
      continue
    }
    const ports = portsByComponent.get(element.schematic_component_id) ?? []
    ports.push(element)
    portsByComponent.set(element.schematic_component_id, ports)
  }

  const replacements = new Map()
  let correctionCount = 0
  let maximumResidual = 0

  for (const component of circuit) {
    if (
      component.type !== "schematic_component" ||
      !component.symbol_name ||
      !component.center
    ) {
      continue
    }
    const symbol = symbols[component.symbol_name]
    const schematicPorts =
      portsByComponent.get(component.schematic_component_id) ?? []
    if (
      !symbol ||
      !symbol.center ||
      symbol.ports?.length !== 2 ||
      schematicPorts.length !== 2
    ) {
      continue
    }

    const matches = matchPorts(schematicPorts, symbol, component)
    if (matches.length !== 2) continue
    const originalDistance = pointDistance(
      matches[1].symbolPort,
      matches[0].symbolPort,
    )
    const renderedDistance = pointDistance(
      matches[1].schematicPort.center,
      matches[0].schematicPort.center,
    )
    if (originalDistance <= 1e-12) continue
    const scale = renderedDistance / originalDistance
    if (!Number.isFinite(scale) || Math.abs(scale - 1) <= 1e-9) continue

    const anchor = matches[1].symbolPort
    const anchorTarget = matches[1].schematicPort.center
    const delta = {
      x: (1 - scale) * anchor.x,
      y: (1 - scale) * anchor.y,
    }

    // Independently recreate the upstream transform and fail closed if symbol
    // library rounding leaves more than one micrometre of endpoint residual.
    for (const match of matches) {
      const transformed = {
        x: scale * match.symbolPort.x + anchorTarget.x + delta.x - anchor.x,
        y: scale * match.symbolPort.y + anchorTarget.y + delta.y - anchor.y,
      }
      const residual = pointDistance(transformed, match.schematicPort.center)
      maximumResidual = Math.max(maximumResidual, residual)
      if (residual > 1e-3) {
        throw new Error(
          `scaled-symbol correction residual ${residual} for ` +
            `${component.schematic_component_id}`,
        )
      }
    }

    replacements.set(component, {
      ...component,
      center: {
        x: component.center.x + delta.x,
        y: component.center.y + delta.y,
      },
    })
    for (const port of schematicPorts) {
      replacements.set(port, {
        ...port,
        center: {
          x: port.center.x + delta.x,
          y: port.center.y + delta.y,
        },
      })
    }
    correctionCount += 1
  }

  return {
    circuit: circuit.map((element) => replacements.get(element) ?? element),
    correctionCount,
    maximumResidual,
  }
}

const die = (message) => {
  process.stderr.write(`SCHEMATIC-RENDER FAIL: ${message}\n`)
  process.exit(2)
}

const usage = () => {
  process.stderr.write(
    "usage: render_schematic_pdf.mjs <circuit.json> <schematic.pdf> " +
      "[--title <title>] [--net-aliases <net_aliases.txt>] " +
      "[--sheet-text-scale <sheet>:<factor>:<pins|all>] " +
      "[--toolchain-package <package.json>]\n",
  )
}

const main = async () => {
const args = process.argv.slice(2)
if (args.length < 2) {
  usage()
  process.exit(2)
}

const circuitPath = path.resolve(args[0])
const outputPath = path.resolve(args[1])
let projectTitle = "SCHEMATIC"
let netAliasesPath = null
let toolchainPackage = null
const sheetTextScales = new Map()
for (let i = 2; i < args.length; i += 1) {
  if (args[i] === "--sheet-text-scale" && args[i + 1]) {
    const match = /^([a-z][a-z0-9_]*):([1-9]\d*(?:\.\d+)?):(pins|all)$/.exec(args[i + 1])
    const factor = match ? Number(match[2]) : NaN
    if (!match || !Number.isFinite(factor) || factor > 4 ||
        sheetTextScales.has(match[1])) die(`invalid or duplicate sheet text scale: ${args[i + 1]}`)
    sheetTextScales.set(match[1], { factor, mode: match[3] })
    i += 1
    continue
  }
  if (args[i] === "--toolchain-package" && args[i + 1]) {
    toolchainPackage = path.resolve(args[i + 1])
    i += 1
    continue
  }
  if (args[i] === "--title" && args[i + 1]) {
    projectTitle = args[i + 1]
    i += 1
    continue
  }
  if (args[i] === "--net-aliases" && args[i + 1]) {
    netAliasesPath = path.resolve(args[i + 1])
    i += 1
    continue
  }
  usage()
  die(`unknown or incomplete argument: ${args[i]}`)
}

if (!fs.existsSync(circuitPath)) die(`missing input: ${circuitPath}`)
let circuit
try {
  circuit = JSON.parse(fs.readFileSync(circuitPath, "utf8"))
} catch (error) {
  die(`cannot parse ${circuitPath}: ${error.message}`)
}
if (!Array.isArray(circuit)) die("Circuit JSON root must be an array")

// tscircuit requires an authoring net that starts with a digit to carry a
// leading N (for example N5V -> 5V).  The KiCad bridge removes that syntax and
// also accepts explicit per-board exceptions in net_aliases.txt.  A human PDF
// must show the same canonical names as the machine netlist.  Rewrite only a
// shallow copy of label records: source nets, connectivity keys,
// and the exact circuit.json bytes remain untouched.
const netAliases = new Map()
if (netAliasesPath !== null) {
  if (!fs.existsSync(netAliasesPath)) {
    die(`missing net-alias file: ${netAliasesPath}`)
  }
  const lines = fs.readFileSync(netAliasesPath, "utf8").split(/\r?\n/)
  for (const [index, raw] of lines.entries()) {
    const line = raw.replace(/#.*/, "").trim()
    if (!line) continue
    const fields = line.split(/\s+/)
    if (fields.length !== 2) {
      die(`${netAliasesPath}:${index + 1}: expected 'AUTHORING CANONICAL'`)
    }
    const [authoring, canonical] = fields
    const previous = netAliases.get(authoring)
    if (previous !== undefined && previous !== canonical) {
      die(
        `${netAliasesPath}:${index + 1}: conflicting aliases for ${authoring}: ` +
          `${previous} and ${canonical}`,
      )
    }
    netAliases.set(authoring, canonical)
  }
}

const canonicalNetName = (name) => {
  if (netAliases.has(name)) return netAliases.get(name)
  return /^N\d/.test(name) ? name.slice(1) : name
}

// Explicit wires in the pinned producer carry inline names as schematic_text.
// Only exact source-net names on an existing source trace qualify; component
// values, notes and custom trace annotations must remain verbatim.
const sourceNetNames = new Set(circuit.filter(e => e.type === "source_net").map(e => e.name))
const sourceTraceIds = new Set(circuit.filter(e => e.type === "source_trace").map(e => e.source_trace_id))
const canonicalDisplayCircuit = circuit.map((element) =>
  (element.type === "schematic_net_label" ||
    (element.type === "schematic_text" &&
      sourceTraceIds.has(element.source_trace_id) && sourceNetNames.has(element.text))) &&
    typeof element.text === "string"
    ? { ...element, text: canonicalNetName(element.text) }
    : element,
)

const sheets = circuit
  .filter((element) => element.type === "schematic_sheet")
  .slice()
  .sort(
    (a, b) =>
      (a.sheet_index ?? Number.MAX_SAFE_INTEGER) -
        (b.sheet_index ?? Number.MAX_SAFE_INTEGER) ||
      String(a.name ?? "").localeCompare(String(b.name ?? "")),
  )
for (const name of sheetTextScales.keys()) {
  if (!sheets.some((sheet) => sheet.name === name))
    die(`sheet text scale names unknown sheet ${name}`)
}

const components = circuit.filter(
  (element) => element.type === "schematic_component",
)
if (components.length === 0) die("input contains zero schematic components")

if (sheets.length > 0) {
  const sheetIds = new Set(sheets.map((sheet) => sheet.schematic_sheet_id))
  const unowned = components.filter(
    (component) =>
      !component.schematic_sheet_id ||
      !sheetIds.has(component.schematic_sheet_id),
  )
  if (unowned.length > 0) {
    const ids = unowned
      .slice(0, 8)
      .map((component) => component.schematic_component_id)
      .join(", ")
    die(
      `${unowned.length} schematic component(s) have no valid sheet owner: ${ids}`,
    )
  }
}

if (!toolchainPackage) {
  let cursor = path.dirname(circuitPath)
  while (cursor !== path.dirname(cursor)) {
    if (fs.existsSync(path.join(cursor, "package.json"))) {
      toolchainPackage = path.join(cursor, "package.json")
      break
    }
    cursor = path.dirname(cursor)
  }
}
if (!toolchainPackage || !fs.existsSync(toolchainPackage)) {
  die("no project-local toolchain package; supply --toolchain-package <package.json>")
}
const require = createRequire(toolchainPackage)
const localModules = fs.realpathSync(path.join(path.dirname(toolchainPackage), "node_modules"))
const resolveLocal = (name) => {
  const resolved = fs.realpathSync(require.resolve(name))
  const relative = path.relative(localModules, resolved)
  if (relative.startsWith(`..${path.sep}`) || relative === ".." || path.isAbsolute(relative)) {
    die(`dependency ${name} escaped project-local node_modules: ${resolved}`)
  }
  return resolved
}
const rendererPath = resolveLocal("circuit-to-svg")
const symbolsPath = resolveLocal("schematic-symbols")
const { parseSync, stringify } = require(resolveLocal("svgson"))
const opentype = require(resolveLocal("opentype.js"))
const fontMetrics = new Map()
const metricsForFont = (family, weight, style) => {
  const face = `${family}:weight=${weight === "bold" ? "bold" : "regular"}:slant=${style === "italic" ? "italic" : "roman"}`
  if (!fontMetrics.has(face)) {
    const fontPath = execFileSync("fc-match", ["-f", "%{file}", face], {
      encoding: "utf8", timeout: 5000,
    }).trim()
    const font = opentype.loadSync(fontPath)
    const metrics = { unitsPerEm: font.unitsPerEm, ascender: font.ascender,
      descender: font.descender,
      // Older OpenType OS/2 tables omit sxHeight. Derive it from the actual
      // font's x glyph, rather than substituting an arbitrary em fraction.
      xHeight: font.tables.os2?.sxHeight || font.charToGlyph("x").getBoundingBox().y2 }
    if (Object.values(metrics).some((value) => !Number.isFinite(value)) ||
        metrics.unitsPerEm <= 0 || metrics.xHeight <= 0) {
      die(`font lacks required baseline metrics: ${fontPath}`)
    }
    fontMetrics.set(face, metrics)
    process.stdout.write(`SCHEMATIC-RENDER font: ${fontPath} SHA-256 ${crypto.createHash("sha256").update(fs.readFileSync(fontPath)).digest("hex")}\n`)
  }
  return fontMetrics.get(face)
}
process.stdout.write(`SCHEMATIC-RENDER toolchain: ${toolchainPackage}\n`)
const { convertCircuitJsonToSchematicSvg } = await import(
  pathToFileURL(rendererPath).href
)
const { symbols } = await import(pathToFileURL(symbolsPath).href)
let alignment
try {
  alignment = alignScaledTwoPortSymbols(canonicalDisplayCircuit, symbols)
} catch (error) {
  die(`cannot align scaled schematic symbols: ${error.message}`)
}
const displayCircuit = alignment.circuit

const xmlEscape = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;")

const scaleSheetText = (input, sheet) => {
  const setting = sheetTextScales.get(sheet.name)
  if (!setting) return input
  const tree = structuredClone(input)
  let scaled = 0
  const walk = (node) => {
    const attrs = node.attributes ?? {}
    const classes = String(attrs.class ?? "").split(/\s+/)
    const pinText = classes.includes("sch-pin-number") || classes.includes("sch-pin-label")
    // Net-label text has a separately sized plate; changing only its font
    // would make the label overrun the plate. Let tighter source poses grow
    // the whole page scale instead.
    const platedNetLabel = classes.includes("sch-net-label-text") ||
      classes.includes("sch-net-label-symbol-text")
    if (node.name === "text" && !platedNetLabel &&
        (setting.mode === "all" || pinText)) {
      const match = /^([0-9]+(?:\.[0-9]+)?)px$/.exec(String(attrs["font-size"] ?? ""))
      if (match) {
        attrs["font-size"] = `${Number(match[1]) * setting.factor}px`
        scaled += 1
      }
    }
    for (const child of node.children ?? []) walk(child)
  }
  walk(tree)
  if (!scaled) die(`sheet ${sheet.name} has no matching text to scale`)
  process.stdout.write(`SCHEMATIC-RENDER sheet ${sheet.name}: scaled ${scaled} ${setting.mode} text item(s) by ${setting.factor}\n`)
  return tree
}

const hash = crypto
  .createHash("sha256")
  .update(fs.readFileSync(circuitPath))
  .digest("hex")
const pages =
  sheets.length > 0
    ? sheets
    : [
        {
          schematic_sheet_id: null,
          name: "root",
          display_name: "ROOT SCHEMATIC",
          sheet_index: 1,
        },
      ]

const HEADER_HEIGHT = 90
const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "schematic-render-"))
const pagePdfs = []
let baselineCorrections = 0

// Select the matching A-series orientation from the exact, unmodified
// schematic component bounds.  This is a page-fit decision only: unlike a
// coordinate stretch, it cannot detach ports or text from symbol bodies.
const pageGeometry = (pageComponents) => {
  const bounds = pageComponents.reduce(
    (box, component) => {
      const centre = component.center ?? {}
      const size = component.size ?? {}
      const halfWidth = Number.isFinite(size.width) ? size.width / 2 : 0
      const halfHeight = Number.isFinite(size.height) ? size.height / 2 : 0
      return {
        minX: Math.min(box.minX, centre.x - halfWidth),
        maxX: Math.max(box.maxX, centre.x + halfWidth),
        minY: Math.min(box.minY, centre.y - halfHeight),
        maxY: Math.max(box.maxY, centre.y + halfHeight),
      }
    },
    { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity },
  )
  const width = Math.max(bounds.maxX - bounds.minX, 0.001)
  const height = Math.max(bounds.maxY - bounds.minY, 0.001)
  if (width / height < 0.9) {
    return { width: 810, contentHeight: 1110, orientation: "portrait" }
  }
  return { width: 1200, contentHeight: 720, orientation: "landscape" }
}

const run = (command, commandArgs, label) => {
  const result = spawnSync(command, commandArgs, {
    encoding: "utf8",
    timeout: 30000,
  })
  if (result.error) die(`${label}: ${result.error.message}`)
  if (result.status !== 0) {
    die(`${label}: ${result.stderr || result.stdout || `exit ${result.status}`}`)
  }
}

try {
  for (const [index, sheet] of pages.entries()) {
    const pageCircuit = displayCircuit.filter((element) => {
      if (!element.type?.startsWith("schematic_")) return true
      if (element.type === "schematic_sheet") return false
      if (sheet.schematic_sheet_id === null) return true
      return element.schematic_sheet_id === sheet.schematic_sheet_id
    })
    const pageComponents = pageCircuit.filter(
      (element) => element.type === "schematic_component",
    )
    if (pageComponents.length === 0) {
      die(`sheet ${sheet.name ?? index + 1} contains zero schematic components`)
    }

    const geometry = pageGeometry(pageComponents)
    const pageHeight = geometry.contentHeight + HEADER_HEIGHT
    const renderedSvg = convertCircuitJsonToSchematicSvg(pageCircuit, {
      width: geometry.width,
      height: geometry.contentHeight,
      showErrorsInTextOverlay: true,
    })
    const normalized = materializeTextBaselines(
      scaleSheetText(parseSync(renderedSvg), sheet), metricsForFont)
    baselineCorrections += normalized.corrections
    const fitted = stringify(normalized.tree).replace(
      /^<svg /,
      `<svg x="0" y="${HEADER_HEIGHT}" `,
    )
    const pageNumber = index + 1
    const heading = sheet.display_name ?? sheet.name ?? `PAGE ${pageNumber}`
    const headingFontSize = Math.min(
      18,
      (geometry.width - 60) / Math.max(heading.length * 0.58, 1),
    )
    const pageSvg = [
      `<svg xmlns="http://www.w3.org/2000/svg" width="${geometry.width}" height="${pageHeight}" viewBox="0 0 ${geometry.width} ${pageHeight}">`,
      '<rect width="100%" height="100%" fill="rgb(245, 241, 237)"/>',
      `<text x="30" y="27" font-family="sans-serif" font-size="20px" font-weight="bold" fill="#840000">${xmlEscape(projectTitle)}</text>`,
      `<text x="30" y="53" font-family="sans-serif" font-size="${headingFontSize.toFixed(1)}px" font-weight="bold" fill="#840000">${xmlEscape(heading)}</text>`,
      `<text x="30" y="76" font-family="sans-serif" font-size="11px" fill="#555">Page ${pageNumber} of ${pages.length} • exact circuit.json SHA-256 ${hash.slice(0, 16)}… • ${pageComponents.length} components • ${geometry.orientation} page fit</text>`,
      fitted,
      "</svg>",
    ].join("\n")

    const stem = `page-${String(pageNumber).padStart(2, "0")}`
    const svgPath = path.join(tempDir, `${stem}.svg`)
    const pdfPath = path.join(tempDir, `${stem}.pdf`)
    fs.writeFileSync(svgPath, pageSvg)
    process.stdout.write(
      `SCHEMATIC-RENDER page ${pageNumber}/${pages.length}: ${
        sheet.display_name ?? sheet.name
      } (${pageComponents.length} components, ${geometry.orientation})\n`,
    )
    run("rsvg-convert", ["-f", "pdf", "-o", pdfPath, svgPath], stem)
    pagePdfs.push(pdfPath)
  }

  const mergedPath = path.join(tempDir, "schematic.pdf")
  if (pagePdfs.length === 1) {
    fs.copyFileSync(pagePdfs[0], mergedPath)
  } else {
    run("pdfunite", [...pagePdfs, mergedPath], "pdf merge")
  }
  const mergedSize = fs.statSync(mergedPath).size
  if (mergedSize < 1000) die(`renderer produced an implausible ${mergedSize}-byte PDF`)

  fs.mkdirSync(path.dirname(outputPath), { recursive: true })
  const atomicPath = `${outputPath}.tmp-${process.pid}`
  fs.copyFileSync(mergedPath, atomicPath)
  fs.renameSync(atomicPath, outputPath)
  process.stdout.write(
    `SCHEMATIC-RENDER PASS: ${pages.length} page(s), ${components.length} components, ` +
      `${netAliases.size} explicit net alias(es), ` +
      `${alignment.correctionCount} scaled two-port symbol alignment correction(s), ` +
      `${baselineCorrections} font-metric text baseline(s), ` +
      `maximum endpoint residual ${alignment.maximumResidual.toExponential(2)}, ` +
      `${outputPath}\n`,
  )
} finally {
  fs.rmSync(tempDir, { recursive: true, force: true })
}
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href
) {
  await main()
}
