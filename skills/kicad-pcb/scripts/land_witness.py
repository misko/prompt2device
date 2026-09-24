"""Finite declared-width native pad-launch witnesses (library only).

Language: complete version-1 S expressions; decimal mm quantities; exact
A/B NetName, NetClass, Type string comparisons, !/&&/|| and parentheses;
insideArea/intersectsArea literal names; optional exact copper-layer scope.
OR binds tighter than AND, as in native KiCad 10. NetName star/question-mark
patterns are certified; bracket characters are literal. Other property
wildcards and escapes are blocked. Width/clearance minima are modeled; a
hole_clearance minimum is validated and explicitly assigned to downstream
native DRC because this witness creates no holes. Structurally valid
diff_pair_gap is also explicitly outside scope.
One exact generated TMUX4827 via/Pad block is excluded only after its active
assembly, native areas/vias, rule text and process selector pass the same-board
via-process audit. All other rules retain the strict launch reader.

Geometry authority is pcbnew effective shapes and native Collide at
max(0, clearance - DRC epsilon). Raw gap/margin are reported independently.
Area outlines are deflated once by DRC epsilon. Drill/physical-hole geometry,
connectivity and routing remain downstream. Unsupported topology fails closed.
The fixed search is <=2 mm declared widths, adaptive bbox proposals (five
intervals per axis, <=37 proposals), 48 directions and 1 mm reach. Failure
means no witness validated in that finite search, never geometric impossibility.
"""
from dataclasses import dataclass
from decimal import Decimal
import json
import math
import os
from pathlib import Path
import re
import sys


class Unsupported(ValueError):
    """Input cannot be represented by the admitted launch language/geometry."""


@dataclass(frozen=True)
class Atom:
    text: str
    quoted: bool
    offset: int


def sexpressions(text, *, allow_escaped_strings=False):
    """Read the entire file without dropping unmatched or trailing tokens.

    Rule-language callers retain their strict no-escape default. Native board
    analysis may explicitly admit only quoted escapes shared by JSON and
    KiCad (quote, backslash, b/f/n/r/t). JSON-only unicode/slash spellings
    and other native escape dialects are refused, never reinterpreted.
    """
    tokens = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
        elif text[i] == '#':
            i = text.find('\n', i) if '\n' in text[i:] else len(text)
        elif text[i] in '()':
            tokens.append(text[i]); i += 1
        elif text[i] == '"':
            if allow_escaped_strings:
                start=i
                try:
                    value,end=json.JSONDecoder().raw_decode(text,i)
                except json.JSONDecodeError as exc:
                    raise Unsupported(f'offset {start}: invalid quoted string') from exc
                # JSON is only a scanner/decoder for this explicitly shared subset.
                # Native KiCad preserves unknown escapes such as \u and \/;
                # JSON would silently turn those into different identities.
                for match in re.finditer(r'\\(.)',text[start:end]):
                    if match.group(1) not in {'"','\\','b','f','n','r','t'}:
                        raise Unsupported(f'offset {start}: unsupported native string escape')
                tokens.append(Atom(value,True,start));i=end
                continue
            start = i; i += 1; end = text.find('"', i)
            if end < 0 or '\\' in text[i:end] or '\n' in text[i:end]:
                raise Unsupported(f"offset {start}: unsupported string/escape")
            tokens.append(Atom(text[i:end], True, start)); i = end + 1
        else:
            m = re.match(r'[^\s()"#]+', text[i:])
            if not m:
                raise Unsupported(f"offset {i}: invalid token")
            tokens.append(Atom(m[0], False, i)); i += len(m[0])
    stack = [[]]
    for tok in tokens:
        if tok == '(':
            stack.append([])
        elif tok == ')':
            if len(stack) == 1:
                raise Unsupported('unmatched closing parenthesis')
            stack[-2].append(stack.pop())
        else:
            stack[-1].append(tok)
    if len(stack) != 1:
        raise Unsupported('unclosed S expression')
    return stack[0]


def atom(value, *, quoted=None):
    if not isinstance(value, Atom) or (quoted is not None and value.quoted != quoted):
        raise Unsupported('expected ' + ('quoted string' if quoted else 'atom'))
    if not value.quoted and '\\' in value.text:
        raise Unsupported(f'offset {value.offset}: unsupported atom escape')
    return value.text


def quantity(value):
    s = atom(value, quoted=False)
    if not re.fullmatch(r'(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)mm', s):
        raise Unsupported(f'offset {value.offset}: unsupported quantity {s!r}')
    n = Decimal(s[:-2]) * 1000000
    if not n.is_finite() or n != n.to_integral_value() or n < 0:
        raise Unsupported(f'offset {value.offset}: quantity not finite integer IU')
    return int(n)


class Condition:
    """Small complete AST parser; never evaluate Python source or fold inputs."""
    token = re.compile(r"\s*(==|!=|&&|\|\||!|\(|\)|\.|'[^'\\\n]*'|[A-Za-z_][A-Za-z_0-9]*)")

    def __init__(self, text):
        self.tokens = []
        pos = 0
        while pos < len(text):
            if text[pos:].isspace(): break
            m = self.token.match(text, pos)
            if not m: raise Unsupported(f'condition offset {pos}: unsupported syntax')
            self.tokens.append(m[1]); pos = m.end()
        self.i = 0
        self.ast = self.parse_and() if self.tokens else ('bool', True)
        if self.i != len(self.tokens): raise Unsupported('condition has dangling tokens')

    def take(self, expected=None):
        if self.i >= len(self.tokens): raise Unsupported('incomplete condition')
        t = self.tokens[self.i]; self.i += 1
        if expected is not None and t != expected: raise Unsupported(f'expected {expected!r}, got {t!r}')
        return t

    def peek(self, token):
        return self.i < len(self.tokens) and self.tokens[self.i] == token

    def parse_and(self):
        n = self.parse_or()
        while self.peek('&&'):
            self.take(); n = ('and', n, self.parse_or())
        return n

    def parse_or(self):
        n = self.primary()
        while self.peek('||'):
            self.take(); n = ('or', n, self.primary())
        return n

    def primary(self):
        if self.peek('!'):
            self.take(); return ('not', self.primary())
        if self.peek('('):
            self.take(); n = self.parse_and(); self.take(')'); return n
        if self.peek('true') or self.peek('false'):
            return ('bool', self.take() == 'true')
        side = self.take()
        if side not in ('A', 'B'): raise Unsupported('condition object must be A or B')
        self.take('.'); prop = self.take()
        if prop in ('insideArea', 'intersectsArea'):
            self.take('('); value = self.literal(); self.take(')')
            if '*' in value or '?' in value: raise Unsupported('area wildcards not certified')
            return ('area', side, value)
        if prop not in ('NetName', 'NetClass', 'Type'): raise Unsupported(f'unsupported property {prop}')
        op = self.take()
        if op not in ('==', '!='): raise Unsupported(f'unsupported comparison {op}')
        value = self.literal()
        if prop != 'NetName' and ('*' in value or '?' in value): raise Unsupported('wildcards supported only for NetName')
        return ('compare', side, prop, op, value)

    def literal(self):
        t = self.take()
        if not t.startswith("'"): raise Unsupported('comparison requires literal string')
        return t[1:-1]


def depends_b(ast):
    return (ast[0] in ('compare', 'area') and ast[1] == 'B') or any(
        depends_b(x) for x in ast[1:] if isinstance(x, tuple))


@dataclass(frozen=True)
class Rule:
    name: str
    ast: tuple
    layer: str | None
    constraints: dict
    offset: int


def _verified_tmux_launch_exclusion(path, board_path, assembly=None):
    """Exclude only the exact, independently graded TMUX via/Pad rule block.

    The block constrains vias, holes and Pad-Pad/Via-Pad pairs; none can match
    this gate's hypothetical Track-Pad witness. Everything outside it stays
    in the strict launch reader. The native process audit must bind the same
    board and unmodified DRU bytes before the block is removed.
    """
    path, board_path = Path(path), Path(board_path)
    raw = path.read_bytes(); board_raw = board_path.read_bytes()
    text = raw.decode('utf-8-sig')
    start, end = '# BEGIN TMUX4827_YBH_B2_POFV', '# END TMUX4827_YBH_B2_POFV'
    fab_scripts = Path(__file__).resolve().parents[2] / 'jlcpcb-fab/scripts'
    sys.path.insert(0, str(fab_scripts))
    from tmux4827_pofv import contract as tmux_contract, dru_rules
    from via_process_check import (check as via_process_check,
                                   find_assembly, load_assembly)
    apath = find_assembly(board_path, assembly)
    try:
        data, _ = load_assembly(board_path, assembly)
        tmux_active = apath is not None and tmux_contract(data, apath) is not None
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise Unsupported('TMUX POFV assembly prerequisite invalid: ' + str(exc)) from exc
    if start not in text and end not in text and not tmux_active:
        return text, []
    if text.count(start) != 1 or text.count(end) != 1 or text.index(end) < text.index(start):
        raise Unsupported('TMUX POFV markers missing, duplicated or reversed')
    if not tmux_active:
        raise Unsupported('TMUX POFV block lacks active assembly contract')
    if path.resolve() != board_path.with_suffix('.kicad_dru').resolve():
        raise Unsupported('TMUX POFV verification requires the board companion DRU')
    expected = start + '\n' + '\n'.join(dru_rules()) + '\n' + end
    begin = text.index(start); finish = text.index(end) + len(end)
    if text[begin:finish] != expected:
        raise Unsupported('TMUX POFV block differs from exact generated rules')
    try:
        result = via_process_check(board_path, str(apath))
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        raise Unsupported('TMUX POFV/process prerequisite unreadable: ' + str(exc)) from exc
    if result.get('na') or result.get('fails') or not result.get('oks'):
        raise Unsupported('TMUX POFV/process prerequisite failed: '
                          + '; '.join(result.get('fails') or [str(result.get('na'))]))
    if path.read_bytes() != raw or board_path.read_bytes() != board_raw:
        raise Unsupported('TMUX POFV board/DRU changed during verification')
    return text[:begin] + text[finish:], [
        'exact TMUX POFV via/Pad block verified by via_process_check; '
        'native DRC owns excluded physical and Pad-Pad/Via-Pad constraints']


def read_rules(path, board_path=None, tmux_assembly=None):
    if board_path is None:
        content = Path(path).read_text(encoding='utf-8-sig'); excluded = []
    else:
        content, excluded = _verified_tmux_launch_exclusion(
            path, board_path, tmux_assembly)
    forms = sexpressions(content)
    if not forms or not isinstance(forms[0], list) or [atom(x, quoted=False) for x in forms[0]] != ['version', '1']:
        raise Unsupported('rules require exactly version 1 at the start')
    result = []; outside = list(excluded)
    for form in forms[1:]:
        name = '<unnamed>'
        try:
            if not isinstance(form, list) or len(form) < 3 or atom(form[0], quoted=False) != 'rule':
                raise Unsupported('expected complete rule')
            name = atom(form[1]); fields = {}; constraints = {}
            if not name: raise Unsupported('empty rule name')
            for field in form[2:]:
                if not isinstance(field, list) or len(field) < 2: raise Unsupported('malformed rule field')
                kind = atom(field[0], quoted=False)
                if kind == 'constraint':
                    c = atom(field[1], quoted=False)
                    if c in constraints: raise Unsupported('duplicate constraint ' + c)
                    values = {}
                    for v in field[2:]:
                        if not isinstance(v, list) or len(v) != 2: raise Unsupported('constraint value arity')
                        key = atom(v[0], quoted=False)
                        if key not in ('min', 'opt', 'max') or key in values: raise Unsupported('invalid/duplicate bound')
                        values[key] = quantity(v[1])
                    if not values: raise Unsupported('constraint requires bounds')
                    if ('min' in values and 'max' in values and values['min'] > values['max']): raise Unsupported('inverted bounds')
                    constraints[c] = values
                elif kind in ('condition', 'layer'):
                    if kind in fields or len(field) != 2: raise Unsupported('duplicate field or invalid arity')
                    fields[kind] = atom(field[1], quoted=True) if kind == 'condition' else atom(field[1])
                else: raise Unsupported('unsupported field ' + kind)
            ast = Condition(fields['condition']).ast if 'condition' in fields else ('bool', True)
            if not constraints: raise Unsupported('rule has no constraint')
            if 'track_width' in constraints and depends_b(ast): raise Unsupported('B-dependent track_width')
            # Validate EVERY condition and quantity before excluding a constraint.
            for kind, values in constraints.items():
                if kind == 'diff_pair_gap':
                    outside.append(name + ': diff_pair_gap outside copper-launch scope')
                elif kind == 'hole_clearance':
                    if set(values) != {'min'}:
                        raise Unsupported('hole_clearance supports exactly one minimum')
                    if not 0 < values['min'] <= 2000000:
                        raise Unsupported('hole_clearance outside (0, 2] mm')
                    outside.append(name + ': hole_clearance validated; physical-hole geometry owned by downstream native DRC')
                elif kind not in ('track_width', 'clearance'):
                    raise Unsupported('unsupported physical constraint ' + kind)
                elif set(values) != {'min'}:
                    raise Unsupported('launch constraints support exactly one minimum')
                elif kind == 'track_width' and not 0 < values['min'] <= 2000000:
                    raise Unsupported('declared width outside (0, 2] mm')
            result.append(Rule(name, ast, fields.get('layer'), constraints, form[0].offset))
        except Unsupported as e:
            raise Unsupported(f'rule {name}: {e}') from e
    return result, outside


def wrap_class(pointer):
    import pcbnew
    if isinstance(pointer, pcbnew.NETCLASS): return pointer
    c = pcbnew.NETCLASS.__new__(pcbnew.NETCLASS); c.this = pointer
    return c


class BoardContext:
    """Exact native board/project context, admitted before any grading."""
    def __init__(self, board_path, pro_path=None, dru_path=None):
        import pcbnew
        self.pcb = pcbnew
        self.path = Path(board_path).resolve()
        self.pro = Path(pro_path).resolve() if pro_path else self.path.with_suffix('.kicad_pro')
        self.dru = Path(dru_path).resolve() if dru_path else self.path.with_suffix('.kicad_dru')
        for f in (self.path, self.pro, self.dru):
            if not f.is_file(): raise Unsupported('missing explicit input ' + str(f))
        if self.pro != self.path.with_suffix('.kicad_pro'):
            raise Unsupported('--project must be the board companion project; override is incoherent')
        self.rules, self.outside = read_rules(self.dru, self.path)
        project = json.loads(self.pro.read_text(encoding='utf-8-sig'))
        if not isinstance(project, dict) or not isinstance(project.get('net_settings'), dict):
            raise Unsupported('malformed project/net_settings mapping')
        net_settings = project['net_settings']
        classes_input = net_settings.get('classes')
        if not isinstance(classes_input, list) or not classes_input:
            raise Unsupported('malformed or empty project classes')
        names_input = set()
        for item in classes_input:
            if not isinstance(item, dict) or not isinstance(item.get('name'), str):
                raise Unsupported('malformed project class entry')
            if item['name'] in names_input:
                raise Unsupported('duplicate project class name')
            names_input.add(item['name'])
            value = item.get('clearance')
            if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value) or value < 0:
                raise Unsupported('missing/nonfinite class clearance ' + item['name'])
        patterns = net_settings.get('netclass_patterns', [])
        if not isinstance(patterns, list) or any(not isinstance(x, dict) or not isinstance(x.get('pattern'), str) or not isinstance(x.get('netclass'), str) for x in patterns):
            raise Unsupported('malformed native assignment patterns')
        labels = net_settings.get('netclass_assignments') or {}
        if not isinstance(labels, dict) or any(not isinstance(k,str) or not isinstance(v,list) or any(not isinstance(n,str) or n not in names_input for n in v) for k,v in labels.items()):
            raise Unsupported('malformed/unknown native label class assignment')
        board_settings = project.get('board', {})
        if not isinstance(board_settings, dict) or not isinstance(board_settings.get('design_settings', {}), dict):
            raise Unsupported('malformed project board settings')
        self.board = pcbnew.LoadBoard(str(self.path))
        self.settings = self.board.GetDesignSettings()
        self.epsilon = int(self.settings.GetDRCEpsilon())
        config_root = Path(os.environ.get('KICAD_CONFIG_HOME') or
                           (Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')/'kicad'))
        self.native_config = config_root/'10.0'/'kicad_advanced'
        if self.native_config.exists():
            values = re.findall(r'^\s*DRCEpsilon\s*=\s*(.*?)\s*$', self.native_config.read_text(), re.M)
            if len(values) > 1:
                raise Unsupported('ambiguous native DRCEpsilon configuration')
            if values:
                try:
                    configured = Decimal(values[0]) * 1000000
                    coherent = configured.is_finite() and configured == self.epsilon
                except Exception:
                    coherent = False
                if not coherent:
                    raise Unsupported('native configuration mismatch: GetDRCEpsilon does not match ' + str(self.native_config) + '; initialize the native application context')
        self.minimum = int(self.settings.m_MinClearance)
        self.min_width = int(self.settings.m_TrackMinWidth)
        self.layers = frozenset(self.board.GetEnabledLayers().CuStack())
        ns = self.settings.m_NetSettings
        classes = project.get('net_settings', {}).get('classes')
        if not isinstance(classes, list) or not classes: raise Unsupported('project classes unavailable')
        native_classes = {str(k): v for k, v in self.board.GetAllNetClasses().items()}
        for c in classes:
            name = c.get('name')
            if name not in native_classes or 'clearance' not in c or c['clearance'] is None:
                raise Unsupported('incomplete class ' + str(name))
            n = native_classes[name]
            if not n.HasClearance() or n.GetClearance() != round(float(c['clearance']) * 1e6):
                raise Unsupported('native class clearance disagreement ' + name)
        for assignment in project.get('net_settings', {}).get('netclass_patterns', []):
            if assignment.get('netclass') not in native_classes: raise Unsupported('unknown assigned class')
        self.classes = {'': ns.GetDefaultNetclass()}
        for net in self.board.GetNetsByNetcode().values():
            if not net.GetNetname(): continue
            c = wrap_class(ns.GetEffectiveNetClass(net.GetNetname()))
            if not c.HasClearance(): raise Unsupported('unresolved class ' + net.GetNetname())
            if str(c.GetName()) != str(net.GetNetClassName()): raise Unsupported('native assignment disagreement ' + net.GetNetname())
            net.SetNetClass(c)
            self.classes[str(net.GetNetname())] = c
        self.class_members = {net: {str(v.GetName()).casefold() for v in native_classes.values() if c.ContainsNetclassWithName(str(v.GetName()))} | {str(c.GetName()).casefold()} for net, c in self.classes.items()}
        self.pads = []; self.unreadable = []; self.physical = 0; self.noncopper = 0
        for fp in self.board.GetFootprints():
            if hasattr(fp, 'IsNetTie') and fp.IsNetTie(): raise Unsupported('net ties unsupported')
            for p in fp.Pads():
                self.physical += 1
                if not p.IsOnCopperLayer(): self.noncopper += 1; continue
                record = {'native': p, 'id': p.m_Uuid.AsString(), 'ref': fp.GetReference(), 'num': p.GetNumber(), 'net': str(p.GetNetname()), 'cls': str(p.GetNetClassName()), 'layers': frozenset(p.GetLayerSet().CuStack()) & self.layers, 'shapes': {}, 'polys': {}}
                try:
                    if p.Padstack().Mode() != pcbnew.PADSTACK.MODE_NORMAL:
                        raise Unsupported('unvalidated padstack mode')
                    if not record['layers']: raise Unsupported('no enabled copper layer')
                    if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH: raise Unsupported('NPTH copper/hole proxy')
                    for layer in sorted(record['layers']):
                        poly = p.GetEffectivePolygon(layer)
                        self.admit_polygon(poly, 'pad')
                        record['polys'][layer] = poly
                        shape = p.GetEffectiveShape(layer)
                        if shape is None: raise Unsupported('unavailable effective shape')
                        record['shapes'][layer] = shape
                    if record['net'] and record['net'] not in self.classes: raise Unsupported('unknown effective class')
                    self.pads.append(record)
                except Exception as e:
                    record['why'] = str(e); self.unreadable.append(record)
        self.areas = {}; self.pours = []
        for z in self.board.Zones():
            if z.IsTeardropArea(): raise Unsupported('teardrop area geometry unsupported')
            poly = pcbnew.SHAPE_POLY_SET(z.Outline())
            self.admit_polygon(poly, 'area' if z.GetIsRuleArea() else 'pour')
            layers = frozenset(z.GetLayerSet().CuStack()) & self.layers
            if z.GetIsRuleArea():
                poly.ClearArcs()
                poly.Deflate(self.epsilon, pcbnew.CORNER_STRATEGY_ALLOW_ACUTE_CORNERS, round(pcbnew.ARC_LOW_DEF_MM * 1e6))
                self.admit_polygon(poly, 'deflated area')
                self.areas.setdefault(z.GetZoneName().casefold(), []).append((layers, poly))
            else: self.pours.append((str(z.GetNetname()), layers, poly))
        self.tracks = [t for t in self.board.GetTracks() if t.GetClass() != 'PCB_VIA']
        self.vias = [t for t in self.board.GetTracks() if t.GetClass() == 'PCB_VIA']
        names = {self.board.GetLayerName(l) for l in self.layers}
        for rule in self.rules:
            if rule.layer is not None and rule.layer not in names: raise Unsupported(f'rule {rule.name}: disabled/unsupported layer {rule.layer}')
            self.admit_areas(rule.ast, rule.name)
        self._prepared = {}
        self.widths = sorted({r.constraints['track_width']['min'] for r in self.rules if 'track_width' in r.constraints})

    @staticmethod
    def admit_polygon(poly, what):
        if poly.OutlineCount() != 1 or poly.HoleCount(0): raise Unsupported(what + ': holes or multiple outlines unsupported')
        if poly.Outline(0).PointCount() < 3: raise Unsupported(what + ': unreadable outline')

    def admit_areas(self, ast, name):
        if ast[0] == 'area' and ast[2].casefold() not in self.areas: raise Unsupported(f'rule {name}: unknown area {ast[2]}')
        for child in ast[1:]:
            if isinstance(child, tuple): self.admit_areas(child, name)

    def matches(self, ast, a, b, layer, possible=False):
        kind = ast[0]
        if kind == 'bool': return ast[1]
        if kind == 'not':
            val = self.matches(ast[1], a, b, layer, possible)
            return None if val is None else not val
        if kind in ('and', 'or'):
            x = self.matches(ast[1], a, b, layer, possible); y = self.matches(ast[2], a, b, layer, possible)
            if kind == 'and': return False if x is False or y is False else (None if x is None or y is None else True)
            return True if x is True or y is True else (None if x is None or y is None else False)
        item = a if ast[1] == 'A' else b
        if item is None: return False
        if kind == 'area':
            if possible: return None
            return any(layer in ls and poly.Collide(item.GetEffectiveShape(layer), 0) for ls, poly in self.areas[ast[2].casefold()])
        prop, op, value = ast[2:]
        if prop == 'Type': result = ('Pad' if item.GetClass() == 'PAD' else 'Track').casefold() == value.casefold()
        elif prop == 'NetName': result = re.fullmatch(re.escape(value).replace(r'\*', '.*').replace(r'\?', '.'), str(item.GetNetname()), re.IGNORECASE) is not None
        else:
            result = value.casefold() in self.class_members.get(str(item.GetNetname()), set())
        return result if op == '==' else not result

    def applicable_rules(self, kind, a, b, layer):
        # Only net/class/type and layer facts are cached. Area predicates are
        # unknown here and evaluated on every actual candidate below.
        key = (kind, str(a.GetNetname()), a.GetClass(),
               str(b.GetNetname()) if b else None, b.GetClass() if b else None, layer)
        if key not in self._prepared:
            self._prepared[key] = [r for r in self.rules if kind in r.constraints
                and (r.layer is None or self.board.GetLayerName(layer) == r.layer)
                and (self.matches(r.ast, a, b, layer, True) is not False
                     or (b is not None and self.matches(r.ast, b, a, layer, True) is not False))]
        return self._prepared[key]

    def resolve(self, kind, a, b, layer):
        value = None; winner = None
        for r in self.applicable_rules(kind, a, b, layer):
            if self.matches(r.ast, a, b, layer) or (b is not None and self.matches(r.ast, b, a, layer)):
                value = r.constraints[kind]['min']; winner = r.name
        return value, winner

    def track(self, source, start, end, width, layer):
        t = self.pcb.PCB_TRACK(self.board)
        t.SetNet(source['native'].GetNet()); t.SetLayer(layer); t.SetWidth(int(width))
        t.SetStart(self.pcb.VECTOR2I(*start)); t.SetEnd(self.pcb.VECTOR2I(*end))
        return t

    def declared(self, source):
        # Geometric predicates remain unknown here; this only removes proven
        # class/net/type invariant false conditions, never folds B-dependent ASTs.
        layer = min(source['layers']); p = source['native'].GetPosition()
        t = self.track(source, (p.x, p.y), (p.x+1000000, p.y), 200000, layer)
        return any('track_width' in r.constraints and any((r.layer is None or self.board.GetLayerName(l) == r.layer) and self.matches(r.ast, t, None, l, True) is not False for l in source['layers']) for r in self.rules)

    def clearance(self, track, obstacle, layer):
        p = obstacle['native']
        local = p.GetLocalClearance()
        if local is None: local = p.GetParentFootprint().GetLocalClearance()
        if local: return max(int(local), self.minimum), 'local override'
        explicit, rule = self.resolve('clearance', track, p, layer)
        if explicit is not None: return explicit, rule
        a = self.classes.get(str(track.GetNetname())); b = self.classes.get(str(p.GetNetname()))
        return max(self.minimum, a.GetClearance() if a else 0, b.GetClearance() if b else 0), 'native effective classes / board'

    def validate(self, source, start, end, width, layer, *, require_declared=True):
        if layer not in source['layers']: raise Unsupported('candidate source layer is disabled/absent')
        t = self.track(source, start, end, width, layer)
        if not source['shapes'][layer].Collide(t.GetStart(), 0): return {'valid': False, 'reason': 'start outside native source copper'}
        floor, rule = self.resolve('track_width', t, None, layer)
        if floor is None and require_declared: return {'valid': False, 'reason': 'no declared candidate floor'}
        required = self.min_width if floor is None else floor
        if width < required: return {'valid': False, 'reason': 'track_width', 'floor_iu': required, 'rule': rule}
        shape = t.GetEffectiveShape(layer); limiting = None; checked = 0
        # Ordering helps reject hostile candidates; no obstacle is pruned.
        obstacles = [q for q in self.pads if layer in q['layers'] and q is not source and (not q['net'] or q['net'] != source['net'])]
        obstacles.sort(key=lambda q: (q['native'].GetPosition().x-start[0])**2+(q['native'].GetPosition().y-start[1])**2)
        for q in obstacles:
            clearance, crule = self.clearance(t, q, layer)
            other = q['shapes'][layer]
            gap = self.pcb.SHAPE.GetClearance(other, shape)
            pair = {'pad': q['ref']+'.'+q['num'], 'uuid': q['id'], 'clearance_iu': clearance, 'rule': crule, 'gap_iu': gap, 'raw_margin_iu': gap-clearance, 'collision_threshold_iu': max(0, clearance-self.epsilon)}
            checked += 1
            if limiting is None or pair['raw_margin_iu'] < limiting['raw_margin_iu']: limiting = pair
            if other.Collide(shape, max(0, clearance-self.epsilon)):
                return {'valid': False, 'reason': 'clearance', 'limiting_pair': pair, 'pairs_checked': checked}
        return {'valid': True, 'status': 'VALIDATED_WITNESS', 'start_iu': list(start), 'end_iu': list(end), 'layer': self.board.GetLayerName(layer), 'width_iu': width, 'floor_iu': floor, 'width_rule': rule, 'limiting_pair': limiting, 'pairs_checked': checked}

    def starts(self, source, layer):
        outline = source['polys'][layer].Outline(0)
        points = [outline.CPoint(i) for i in range(outline.PointCount())]
        x0 = min(p.x for p in points); x1 = max(p.x for p in points)
        y0 = min(p.y for p in points); y1 = max(p.y for p in points)
        nx = max(1, min(round((x1-x0)/30000), 5)); ny = max(1, min(round((y1-y0)/30000), 5))
        proposals = [(round((x0+x1)/2), round((y0+y1)/2))]
        for i in range(nx+1):
            for j in range(ny+1):
                proposals.append((round(min(max(x0+(x1-x0)*i/nx, x0+1), x1-1)), round(min(max(y0+(y1-y0)*j/ny, y0+1), y1-1))))
        return [p for p in proposals if source['shapes'][layer].Collide(self.pcb.VECTOR2I(*p), 0)], len(proposals)

    def search(self, source):
        if self.unreadable: raise Unsupported('unreadable relevant obstacle/source blocks coverage')
        coverage = {'widths_iu': self.widths, 'layers': [], 'directions': 48, 'reach_iu': 1000000, 'attempted': 0, 'complete': False}
        last = None
        for layer in sorted(source['layers']):
            starts, proposals = self.starts(source, layer)
            coverage['layers'].append({'layer': self.board.GetLayerName(layer), 'proposals': proposals, 'admitted_starts_iu': starts})
            pos = source['native'].GetPosition()
            invariant_track = self.track(source, (pos.x,pos.y), (pos.x+1000000,pos.y), 200000, layer)
            possible = self.applicable_rules('track_width', invariant_track, None, layer)
            minimum = min((r.constraints['track_width']['min'] for r in possible), default=2000001)
            coverage['layers'][-1]['invariant_width_rejections_iu'] = [w for w in self.widths if w < minimum]
            for width in self.widths:
                if width < minimum:
                    coverage['attempted'] += len(starts) * 48
                    continue
                for start in starts:
                    for direction in range(48):
                        angle = 2*math.pi*direction/48
                        end = (start[0]+round(1000000*math.cos(angle)), start[1]+round(1000000*math.sin(angle)))
                        last = self.validate(source, start, end, width, layer)
                        coverage['attempted'] += 1
                        if last['valid']:
                            last['coverage'] = coverage
                            return last
        coverage['complete'] = True
        return {'valid': False, 'status': 'NO_VALIDATED_WITNESS', 'coverage': coverage, 'last_rejection': last}
