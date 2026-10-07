from app.gymternet_import import prepare_import_source_rows
from app.gymternet_import import apply_athlete_match_decisions


def prepare(decisions=None):
    sources, issues, stats = {}, [], {'corrected': 0, 'excluded': 0}
    rows = prepare_import_source_rows('MAG', [{'Country': 'ESP', 'Score': '14.2'}],
                                      decisions, sources, issues, stats)
    return rows, sources, issues, stats


def test_country_correction_preserves_score_and_source():
    _, sources, _, _ = prepare()
    source = sources[('MAG', 2)]
    decision = {**source, 'action': 'edit', 'values': {'Country': 'ITA', 'Score': '14.3'}}
    rows, original, issues, stats = prepare([decision])
    assert not issues
    assert rows == [{'Country': 'ITA', 'Score': 14.3}]
    assert original[('MAG', 2)]['values']['Country'] == 'ESP'
    assert stats['corrected'] == 1


def test_country_correction_rejects_stale_or_invalid_decisions():
    _, sources, _, _ = prepare()
    source = sources[('MAG', 2)]
    for override in ({'fingerprint': 'stale'}, {'values': {'Country': ''}},
                     {'values': {'Country': 'not a country'}}, {'values': {'Name': 'Other'}}):
        rows, _, issues, stats = prepare([{**source, 'action': 'edit', 'values': {'Country': 'ITA'}, **override}])
        assert issues
        assert rows[0]['Country'] == 'ESP'
        assert stats['corrected'] == 0


def test_country_review_rejects_unlisted_country_and_ambiguous_identity():
    review = {'review_id': 'test', 'problem_type': 'possible_athlete_identity_collision',
              'imported_athlete': {'first_name': 'A', 'last_name': 'B', 'discipline': 'MAG', 'year': 2026},
              'country_variants': [{'country': 'ITA'}, {'country': 'ESP'}], 'suggestions': []}
    for selected, suggestions in [('USA', []), ('ITA', [
        {'target_athlete': {'athlete_id': 1, 'country': 'ITA'}},
        {'target_athlete': {'athlete_id': 2, 'country': 'ESP'}}])]:
        issues = []
        *maps, stats = apply_athlete_match_decisions(None, [{**review, 'suggestions': suggestions}],
            [{'review_id': 'test', 'action': 'country_correction', 'canonical_country': selected}], issues)
        assert stats['invalid_decisions'] == 1 and stats['unresolved'] == 1
        assert all(not mapping for mapping in maps)
        assert issues[0]['severity'] == 'error'
