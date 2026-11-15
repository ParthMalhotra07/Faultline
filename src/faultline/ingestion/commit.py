from faultline.ingestion.parser import validate_records


def ingest(store, catalog, records, round_number):
    validated = validate_records(catalog, records, store.version)
    for key, a, b, r in validated:
        if r.sha256 in store.manifest['sources']:
            continue
        store.commit_claim(key, a, 'READS_CONFIG', b, r.evidence_id, r.sha256, r.source_id, round_number)
        store.manifest['evidence'][r.evidence_id]['record'] = r.model_dump()
        store._save()
    # Make this source visible only after every claim and raw evidence is durable.
    for r in records:
        store.manifest['sources'][r.sha256] = dict(source_id=r.source_id, source_version=r.source_version)
    store.manifest['round'] = max(round_number, store.manifest['round'])
    store._save()
