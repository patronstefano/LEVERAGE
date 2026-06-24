from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx

from app import models
from app.config import settings


class AISuggestionError(Exception):
    pass


class AISuggestionProviderNotConfigured(AISuggestionError):
    pass


@dataclass
class AISuggestionCandidate:
    field_name: str
    suggested_value: str
    confidence: float | None = None
    source_url: str | None = None
    source_title: str | None = None
    evidence: str | None = None


def serialize_value(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    return value


def build_entity_context(entity: models.Athlete | models.Event) -> dict[str, Any]:
    if isinstance(entity, models.Athlete):
        return {
            "id": entity.id,
            "first_name": entity.first_name,
            "last_name": entity.last_name,
            "birth_year": entity.birth_year,
            "country": entity.country,
            "discipline": serialize_value(entity.discipline),
            "image_url": entity.image_url,
            "world_gymnastics_athlete_id": entity.world_gymnastics_athlete_id,
            "world_gymnastics_profile_url": entity.world_gymnastics_profile_url,
            "world_gymnastics_status": entity.world_gymnastics_status,
            "world_gymnastics_verified_at": serialize_value(entity.world_gymnastics_verified_at),
            "country_changes": [
                {
                    "from_country": change.from_country,
                    "to_country": change.to_country,
                    "change_year": change.change_year,
                }
                for change in entity.country_changes
            ],
        }

    return {
        "id": entity.id,
        "name": entity.name,
        "location": entity.location,
        "venue": entity.venue,
        "start_date": serialize_value(entity.start_date),
        "end_date": serialize_value(entity.end_date),
        "year": entity.year,
        "discipline": serialize_value(entity.discipline),
        "category": serialize_value(entity.category),
        "level": serialize_value(entity.level),
        "image_url": entity.image_url,
        "world_gymnastics_event_id": entity.world_gymnastics_event_id,
        "world_gymnastics_event_url": entity.world_gymnastics_event_url,
        "world_gymnastics_status": entity.world_gymnastics_status,
        "world_gymnastics_verified_at": serialize_value(entity.world_gymnastics_verified_at),
    }


def build_prompt(
    entity_type: models.DataSuggestionEntityTypeEnum,
    entity: models.Athlete | models.Event,
    fields: list[str],
) -> str:
    context = build_entity_context(entity)
    return (
        "Find official or highly reliable web sources for missing LEVERAGE data.\n"
        "Return suggestions only for the requested fields and only when a source supports the value.\n"
        "Prefer official competition pages, federation pages, FIG profiles, or organizer pages.\n"
        "Do not invent values. If a field cannot be verified, omit it.\n"
        "Use ISO date format YYYY-MM-DD for date fields.\n"
        "Use a four-digit year for birth_year.\n"
        "For image_url, suggest only a direct public image URL or a profile page URL that clearly contains the image.\n"
        "For event level, use exactly one LEVERAGE level value.\n"
        f"Entity type: {entity_type.value}\n"
        f"Requested fields: {json.dumps(fields)}\n"
        f"LEVERAGE event levels: {json.dumps([level.value for level in models.LevelEnum])}\n"
        f"Entity context: {json.dumps(context, ensure_ascii=False)}"
    )


def build_response_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "suggestions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "field_name": {"type": "string"},
                        "suggested_value": {"type": "string"},
                        "confidence": {"type": "number"},
                        "source_url": {"type": "string"},
                        "source_title": {"type": "string"},
                        "evidence": {"type": "string"},
                    },
                    "required": [
                        "field_name",
                        "suggested_value",
                        "confidence",
                        "source_url",
                        "source_title",
                        "evidence",
                    ],
                },
            }
        },
        "required": ["suggestions"],
    }


def extract_output_text(response_payload: dict[str, Any]) -> str:
    output_text = response_payload.get("output_text")
    if output_text:
        return output_text

    for item in response_payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                return content["text"]

    raise AISuggestionError("AI provider returned no output text")


def parse_candidates(raw_payload: dict[str, Any], requested_fields: set[str]) -> list[AISuggestionCandidate]:
    candidates = []
    for item in raw_payload.get("suggestions", []):
        field_name = str(item.get("field_name", "")).strip()
        suggested_value = str(item.get("suggested_value", "")).strip()
        if field_name not in requested_fields or not suggested_value:
            continue
        confidence = item.get("confidence")
        if confidence is not None:
            try:
                confidence = float(confidence)
            except (TypeError, ValueError):
                confidence = None
        candidates.append(
            AISuggestionCandidate(
                field_name=field_name,
                suggested_value=suggested_value,
                confidence=confidence,
                source_url=str(item.get("source_url", "")).strip() or None,
                source_title=str(item.get("source_title", "")).strip() or None,
                evidence=str(item.get("evidence", "")).strip() or None,
            )
        )
    return candidates


def call_openai_provider(
    entity_type: models.DataSuggestionEntityTypeEnum,
    entity: models.Athlete | models.Event,
    fields: list[str],
) -> list[AISuggestionCandidate]:
    if not settings.openai_api_key:
        raise AISuggestionProviderNotConfigured("OPENAI_API_KEY is not configured")

    request_payload: dict[str, Any] = {
        "model": settings.openai_model,
        "instructions": (
            "You are an assistant for LEVERAGE, an artistic gymnastics database. "
            "You may only suggest candidate values for an admin to review. "
            "Never claim a value is official unless the cited source supports it."
        ),
        "tools": [{"type": "web_search"}],
        "tool_choice": "auto",
        "include": ["web_search_call.action.sources"],
        "input": build_prompt(entity_type, entity, fields),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "leverage_data_suggestions",
                "strict": False,
                "schema": build_response_schema(),
            }
        },
    }
    if settings.openai_model.startswith(("gpt-5", "o")):
        request_payload["reasoning"] = {"effort": "low"}

    try:
        response = httpx.post(
            f"{settings.openai_base_url.rstrip('/')}/responses",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=request_payload,
            timeout=settings.ai_suggestions_timeout_seconds,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise AISuggestionError(f"AI provider error: {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise AISuggestionError("AI provider request failed") from exc

    try:
        raw_response = json.loads(extract_output_text(response.json()))
    except (json.JSONDecodeError, ValueError) as exc:
        raise AISuggestionError("AI provider returned invalid JSON") from exc

    return parse_candidates(raw_response, set(fields))


def generate_suggestions(
    entity_type: models.DataSuggestionEntityTypeEnum,
    entity: models.Athlete | models.Event,
    fields: list[str],
) -> list[AISuggestionCandidate]:
    provider = settings.ai_suggestions_provider.lower()
    if provider in {"", "disabled", "none"}:
        raise AISuggestionProviderNotConfigured("AI_SUGGESTIONS_PROVIDER is disabled")
    if provider == "openai":
        return call_openai_provider(entity_type, entity, fields)
    raise AISuggestionProviderNotConfigured(f"Unsupported AI suggestions provider: {settings.ai_suggestions_provider}")
