"""Private aggregation; errors and abstentions always stay in denominator."""
def score_predictions(rows):
    correct = sum(r['status'] == 'supported' and r['selected'] == r['expected'] for r in rows)
    abstentions = sum(r['status'] in ('ambiguous', 'insufficient_evidence') for r in rows)
    errors = sum(r['status'] == 'error' for r in rows)
    return dict(correct=correct, total=len(rows), accuracy=correct / len(rows) if rows else None,
                abstentions=abstentions, errors=errors, wrong=len(rows) - correct - abstentions - errors)
