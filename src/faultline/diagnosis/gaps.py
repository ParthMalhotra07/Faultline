def unresolved_services(public, endpoint_paths):
    failing = {o.endpoint_id for o in public.observations if o.status == 'failing'}
    services, evidenced = set(), set()
    for endpoint in failing:
        for path in endpoint_paths.get(endpoint, []):
            entities = path['entity_ids']
            services.update(x for x in entities if x.startswith('service:'))
            if entities[-1].startswith('config:'):
                evidenced.add(entities[-2])
    return services - evidenced
