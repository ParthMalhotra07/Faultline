def select_source(metadata, unresolved, inspected_hashes):
    candidates = [s for s in metadata if s.sha256 not in inspected_hashes and not s.inspected
                  and set(s.owner_service_ids) & set(unresolved)]
    candidates.sort(key=lambda s: (-len(set(s.owner_service_ids) & set(unresolved)), s.estimated_bytes, s.source_id))
    return candidates[0] if candidates else None
