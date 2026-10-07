from app.gymternet_import import apply_athlete_match_decisions


def test_duplicate_deferral_does_not_defer_country_reviews():
    reviews = [
        {'review_id': 'identity', 'problem_type': 'possible_duplicate'},
        {'review_id': 'country', 'problem_type': 'possible_athlete_country_change'},
        {'review_id': 'collision', 'problem_type': 'possible_athlete_identity_collision'},
    ]
    stats = apply_athlete_match_decisions(None, reviews, [], [], True)[-1]
    assert stats['deferred'] == 1 and stats['unresolved'] == 2
    assert reviews[0]['deferred']
    assert not reviews[1].get('deferred') and not reviews[2].get('deferred')


def test_country_deferral_does_not_defer_identity_reviews():
    reviews = [
        {'review_id': 'identity', 'problem_type': 'possible_duplicate'},
        {'review_id': 'country', 'problem_type': 'possible_athlete_country_change'},
    ]
    stats = apply_athlete_match_decisions(None, reviews, [{'review_id': 'country', 'action': 'defer'}], [])[-1]
    assert stats['deferred'] == 1 and stats['unresolved'] == 1
    assert not reviews[0].get('deferred') and reviews[1]['deferred']
