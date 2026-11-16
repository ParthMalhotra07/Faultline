"""Conservative display rule for the shared interactive demo.

Frozen protocol v1 keeps its original ranking function and artifacts. The live
UI avoids presenting path length alone as evidence that one changed setting
caused an incident.
"""

from faultline.contracts import Diagnosis


def guard_live_diagnosis(raw: dict) -> dict:
    if raw['status'] != 'supported' or len(raw['ranked_candidates']) < 2:
        return raw
    first, second = raw['ranked_candidates'][:2]
    same_failure_pattern = (
        first['failing_coverage'] == second['failing_coverage']
        and first['healthy_contradictions'] == second['healthy_contradictions']
    )
    if not same_failure_pattern:
        return raw
    guarded = raw | {
        'status': 'ambiguous',
        'selected_origin_id': None,
        'gap_reason': (
            'Several changed settings explain the same failed checks; '
            'a shorter graph path alone cannot distinguish the cause'
        ),
    }
    return Diagnosis.model_validate(guarded).model_dump()
