def enum_value(value):
    return value.value if hasattr(value, "value") else value


def result_identity_key(
    athlete_id: int,
    event_id: int,
    discipline,
    category,
    apparatus,
    vt_attempt,
    day,
    format_value,
    round_value,
) -> tuple:
    return (
        athlete_id,
        event_id,
        enum_value(discipline),
        enum_value(category),
        apparatus,
        vt_attempt,
        day,
        enum_value(format_value),
        enum_value(round_value),
    )


def result_identity_from_result(result) -> tuple:
    return result_identity_key(
        result.athlete_id,
        result.event_id,
        result.discipline,
        result.category,
        result.apparatus,
        result.vt_attempt,
        result.day,
        result.format,
        result.round,
    )
