from faultline.contracts import ExplanationPath


def explanation(endpoint, candidate, path):
    return ExplanationPath(endpoint_id=endpoint, candidate_id=candidate, **path)
