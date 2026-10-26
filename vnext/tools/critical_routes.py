"""Placement-time critical-route trials, not complete routing acceptance.

The coordinator owns scope; the independent reviewer owns its sufficiency and
electrical/thermal judgment. Native replay owns geometry and connectivity.
"""
from pathlib import Path
import tempfile

import placement as p


def tool_identities():
    import routing
    import routing_geometry
    return {Path(module.__file__).name: p.sha(Path(module.__file__))
            for module in (routing, routing_geometry)} | {Path(__file__).name: p.sha(Path(__file__))}


def connected(board, terminals):
    """Require every physical pad of each declared terminal in one copper cluster."""
    board.BuildConnectivity()
    pads = []
    for terminal in terminals:
        p.need(set(terminal) == {'ref', 'pin'}, 'critical terminal needs ref/pin')
        found = [pad for fp in board.GetFootprints()
                 if fp.GetReference() == terminal['ref'] for pad in fp.Pads()
                 if pad.GetNumber() == terminal['pin']]
        p.need(found, 'unknown critical terminal')
        pads.extend(found)
    p.need(len(pads) >= 2 and len({x.m_Uuid.AsString() for x in pads}) == len(pads),
           'critical duty needs distinct physical terminals')
    p.need(pads[0].GetNetCode() > 0 and
           all(x.GetNetCode() == pads[0].GetNetCode() for x in pads),
           'critical terminals have different or missing nets')
    # GetConnectedItems is immediate adjacency. Walk the actual connected copper,
    # rather than treating matching net names as physical connectivity.
    todo = [pads[0]]; seen = set()
    while todo:
        item = todo.pop(); uid = item.m_Uuid.AsString()
        if uid in seen:
            continue
        seen.add(uid)
        todo.extend(x for x in board.GetConnectivity().GetConnectedItems(item)
                    if x.GetNetCode() == pads[0].GetNetCode())
    p.need(all(x.m_Uuid.AsString() in seen for x in pads), 'critical duty is not routed')


def verify(project, review, placed_boards):
    import routing as r
    import routing_geometry
    contract = p.read(p.local(project, p.CONTRACT))
    p.need(contract.get('version') == 2 and contract.get('critical_routes'),
           'new placement acceptance requires version2 critical-route scope')
    scope_name = contract['critical_routes']
    trial_name = review.get('critical_routes')
    p.need(trial_name, 'critical-route trial manifest required')
    required = {}

    def bind(name):
        digest = p.sha(p.local(project, name))
        p.need(review['subjects'].get(name) == digest, 'unbound critical-route evidence: ' + name)
        required[name] = digest

    bind(scope_name); bind(trial_name)
    scope = p.read(p.local(project, scope_name)); trials = p.read(p.local(project, trial_name))
    p.need(scope.get('version') == trials.get('version') == 1,
           'unsupported critical-route manifest')
    p.need(set(scope['boards']) == set(trials['boards']) == set(placed_boards),
           'critical-route board coverage differs')
    for key, rules in scope['boards'].items():
        trial = trials['boards'][key]
        p.need(rules.get('reason', '').strip(), 'critical-route applicability reason required')
        duties = rules['duties']
        ids = [d['id'] for d in duties]
        p.need(all(isinstance(x, str) and x.strip() for x in ids) and len(set(ids)) == len(ids),
               'duplicate or empty critical duty')
        p.need(set(trial['duties']) == set(ids), 'critical duty coverage differs')
        for duty in duties:
            evidence = trial['duties'][duty['id']]
            p.need(duty.get('requirements') and
                   all(isinstance(x, str) and x.strip() for x in duty['requirements']),
                   'critical engineering requirements required')
            p.need(evidence.get('verdict') == 'PASS' and evidence.get('rationale', '').strip()
                   and evidence.get('evidence'), 'critical engineering review incomplete')
            for name in evidence['evidence']:
                bind(name)
        # No critical block is allowed only by explicit, independently reviewed
        # applicability. It is not a fake zero-row native-check success.
        if not duties:
            p.need(trial.get('not_applicable_reason', '').strip(),
                   'empty critical scope needs independent disposition')
            continue
        p.need(set(trial['native']) == {'source', 'project'}, 'critical native source/project required')
        for name in trial['native'].values():
            bind(name)
        source = p.local(project, trial['native']['source'])
        settings_path = p.local(project, trial['native']['project'])
        p.need(source.suffix == '.kicad_pcb' and settings_path.suffix == '.kicad_pro',
               'critical trial needs native board/project')
        settings = p.read(settings_path)['board']['design_settings']
        p.need(not settings.get('drc_exclusions'), 'critical trial DRC exclusions forbidden')
        p.need(not source.with_suffix('.kicad_dru').exists() and
               not settings_path.with_suffix('.kicad_dru').exists(), 'custom trial rules unsupported')
        p.need(r.identity(source) == r.identity(p.local(project, placed_boards[key])),
               'critical trial placement/pads/nets/outline differ')
        with tempfile.TemporaryDirectory(prefix='vnext-critical-route-') as tmp:
            out = Path(tmp)/'replay'
            checks = r.produce(project, {'boards': {key: trial['native']}}, out)[key]
            p.need(checks['physical_faults'] == 0, 'critical trial has physical DRC faults')
            native = out/(key+'.kicad_pcb')
            # Filled copper is part of the demonstrated subject, not an outline
            # that happens to become different copper during verification.
            p.need(r.normalized(native) == r.normalized(source), 'stale critical trial copper fill')
            geometry = routing_geometry.screen(native)
            p.need(not geometry['via_drill_smd_overlaps'], 'critical trial has via bore under solder land')
            board = p.pcb.LoadBoard(str(native))
            for duty in duties:
                connected(board, duty['terminals'])
    return required
