import assert from "node:assert/strict"
import test from "node:test"
import {
  assertPinIndexNativeParity,
  buildPinIndex,
  classifyXmosPin,
  PIN_INDEX_ROWS_PER_PAGE,
  parseNativePinMap,
} from "../render_schematic_pdf.mjs"

const fixture = () => [
  { type: "source_component", source_component_id: "c", name: "U_XU" },
  { type: "source_port", source_component_id: "c", source_port_id: "p1", pin_number: 1, name: "X0D00" },
  { type: "source_port", source_component_id: "c", source_port_id: "p2", pin_number: 2, name: "X0D01_NC" },
  { type: "source_net", source_net_id: "n1", name: "N1V8" },
  { type: "source_trace", source_trace_id: "t1", connected_source_port_ids: ["p1"], connected_source_net_ids: ["n1"] },
]
const netlist = (second = "unconnected-(U_XU-X0D01_NC-Pad2)") => `(export
 (net (code "1") (name "1V8") (node (ref "U_XU") (pin "1")))
 (net (code "2") (name "${second}") (node (ref "U_XU") (pin "2"))))`

test("pin index orders, aliases, hashes, and checks native NC spelling", () => {
  assert.equal(PIN_INDEX_ROWS_PER_PAGE, 26)
  assert.equal(Math.ceil(129 / PIN_INDEX_ROWS_PER_PAGE), 5)
  const rows = buildPinIndex(fixture(), "U_XU", (name) => name === "N1V8" ? "1V8" : name)
  assert.deepEqual(rows.map((row) => [row.pin, row.name, row.net, row.state]), [[1, "X0D00", "1V8", "CONNECTED"], [2, "X0D01_NC", "NC", "NC"]])
  const tuple = assertPinIndexNativeParity(rows, parseNativePinMap(netlist(), "U_XU"), "U_XU")
  assert.match(tuple, /^[a-f0-9]{64}$/)
  assert.throws(() => assertPinIndexNativeParity(rows, parseNativePinMap(netlist("unconnected-(U_XU-WRONG-Pad2)"), "U_XU"), "U_XU"), /expected/)
})

test("pin index rejects malformed source connectivity and native pin sets", () => {
  const missingPortId = fixture(); delete missingPortId[1].source_port_id
  assert.throws(() => buildPinIndex(missingPortId, "U_XU", String), /source_port_id/)
  const blankPortId = fixture(); blankPortId[1] = { ...blankPortId[1], source_port_id: "  " }
  assert.throws(() => buildPinIndex(blankPortId, "U_XU", String), /source_port_id/)
  const duplicatePortId = fixture(); duplicatePortId[2] = { ...duplicatePortId[2], source_port_id: "p1" }
  assert.throws(() => buildPinIndex(duplicatePortId, "U_XU", String), /duplicate source_port_id/)
  const duplicateTracePort = fixture(); duplicateTracePort[4] = { ...duplicateTracePort[4], connected_source_port_ids: ["p1", "p1"] }
  assert.throws(() => buildPinIndex(duplicateTracePort, "U_XU", String), /duplicate source-port reference/)
  const malformedTracePort = fixture(); malformedTracePort[4] = { ...malformedTracePort[4], connected_source_port_ids: ["p1", 7] }
  assert.throws(() => buildPinIndex(malformedTracePort, "U_XU", String), /malformed source-port reference/)
  const duplicate = fixture(); duplicate[2] = { ...duplicate[2], pin_number: 1 }
  assert.throws(() => buildPinIndex(duplicate, "U_XU", String), /duplicate/)
  const missing = fixture(); missing[2] = { ...missing[2], pin_number: 3 }
  assert.throws(() => buildPinIndex(missing, "U_XU", String), /contiguous/)
  const untraced = fixture(); untraced[2] = { ...untraced[2], name: "X0D01" }
  assert.throws(() => buildPinIndex(untraced, "U_XU", String), /untraced non-NC/)
  const multi = fixture(); multi.push({ type: "source_net", source_net_id: "n2", name: "GPIO" }, { type: "source_trace", source_trace_id: "t2", connected_source_port_ids: ["p1"], connected_source_net_ids: ["n2"] })
  assert.throws(() => buildPinIndex(multi, "U_XU", String), /multiple source nets/)
  const rows = buildPinIndex(fixture(), "U_XU", (name) => name === "N1V8" ? "1V8" : name)
  assert.throws(() => assertPinIndexNativeParity(rows, parseNativePinMap(netlist().replace('(node (ref "U_XU") (pin "2"))', '(node (ref "U_XU") (pin "3"))'), "U_XU"), "U_XU"), /missing pin|pin set/)
  assert.throws(() => parseNativePinMap(netlist().replace('(node (ref "U_XU") (pin "2"))', '(node (ref "U_XU") (pin "2")) (node (ref "U_XU") (pin "2"))'), "U_XU"), /duplicate native pin/)
  assert.throws(() => parseNativePinMap('(net (code "1")', "U_XU"), /malformed native netlist/)
})

test("unused MIPI supplies are explicitly documented and fail closed off ground", () => {
  const mipiRows = [
    { pin: 24, name: "MIPI_VDD18", net: "GND", state: "CONNECTED" },
    { pin: 27, name: "MIPI_VDD09", net: "GND", state: "CONNECTED" },
  ]
  const category = "unused MIPI supply — grounded per XMOS §14"
  const functions = mipiRows.map(classifyXmosPin)
  assert.deepEqual(functions, [category, category])
  const census = new Map()
  for (const label of functions) census.set(label, (census.get(label) ?? 0) + 1)
  assert.equal(census.get(category), 2)
  assert.throws(() => classifyXmosPin({ ...mipiRows[0], net: "N1V8" }), /must be GND/)
})
