from faultline.evaluation.scoring import score_predictions


def test_denominator_includes_abstentions_errors_and_wrong_answers():
    rows = [dict(expected='config:a', selected='config:a', status='supported'),
            dict(expected='config:a', selected='config:b', status='supported'),
            dict(expected='config:a', selected=None, status='ambiguous'),
            dict(expected='config:a', selected=None, status='insufficient_evidence'),
            dict(expected='config:a', selected=None, status='error')]
    result = score_predictions(rows)
    assert result == dict(correct=1, total=5, accuracy=0.2, abstentions=2, errors=1, wrong=1)


def test_empty_is_unmeasured_not_zero_accuracy():
    assert score_predictions([])['accuracy'] is None
