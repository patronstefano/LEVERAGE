from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_local_preview_uses_only_the_canonical_backend_port():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    fallback_block = source.split("const API_FALLBACK_BASES = [", 1)[1].split("];", 1)[0]

    assert '"http://127.0.0.1:8000"' in fallback_block
    assert '"http://localhost:8000"' in fallback_block
    assert ":8001" not in fallback_block
    assert ":8002" not in fallback_block
    assert "800[0-2]" in source


def test_verified_athlete_badge_is_rendered_in_the_profile_metadata():
    source = (PROJECT_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
    styles = (PROJECT_ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")

    assert "function renderAthleteProfileMeta(athlete)" in source
    assert "renderAthleteVerificationBadge(athlete)" in source
    assert 'aria-hidden="true">✓</span>' in source
    assert ".athlete-profile-meta" in styles
    assert ".athlete-verification-badge" in styles
    badge_styles = styles.split(".athlete-verification-badge {", 1)[1].split("}", 1)[0]
    assert "width: 16px" in badge_styles
    assert "margin-left: 3px" in badge_styles
    assert "clip-path: polygon(" in badge_styles
