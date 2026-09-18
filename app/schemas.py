from datetime import date as Date, datetime
from typing import Any, Optional
from enum import Enum
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, model_validator


MAG_APPARATUS = {"FX", "PH", "SR", "VT", "PB", "HB", "AA", "VT AVG"}
WAG_APPARATUS = {"VT", "UB", "BB", "FX", "AA", "VT AVG"}
MAG_BONUS_APPARATUS_2025 = {"FX", "SR", "VT", "PB", "HB"}
SCORE_FORMULA_TOLERANCE = 0.001
NON_AA_SCORE_UPPER_BOUND = 20.0
D_SCORE_UPPER_BOUND = 10.0
E_SCORE_UPPER_BOUND = 10.0
VAULT_ATTEMPT_ORDER_WARNING = "Please note that Vault 1 may refer to Vault 2 and vice versa."
EXECUTION_ESTIMATE_WARNING = (
    "Estimated execution from D score and Final score."
)
EXECUTION_ESTIMATE_WITH_PENALTY_WARNING = (
    "Estimated execution from D score and Final score, including possible unavailable Penalty data."
)
EXECUTION_ESTIMATE_WITH_BONUS_WARNING = (
    "Estimated execution from D score and Final score, including a possible unrecorded Bonus."
)
EXECUTION_ESTIMATE_WITH_PENALTY_AND_BONUS_WARNING = (
    "Estimated execution from D score and Final score, including possible unavailable Penalty data "
    "and a possible unrecorded Bonus."
)


def score_equal(value: float, expected: float) -> bool:
    return abs(value - expected) < 0.0001


def validate_result_scoring(
    discipline: Optional["DisciplineEnum"],
    apparatus: Optional[str],
    vt_attempt: Optional[int],
    score: Optional[float],
    D_score: Optional[float],
    E_score: Optional[float],
    Penalty: Optional[float],
    Bonus: Optional[float],
) -> None:
    for field_name, value in {
        "score": score,
        "D_score": D_score,
        "E_score": E_score,
        "Penalty": Penalty,
        "Bonus": Bonus,
    }.items():
        if value is not None and value < 0:
            raise ValueError(f"{field_name} must be greater than or equal to 0")
    if D_score is not None and D_score > D_SCORE_UPPER_BOUND:
        raise ValueError("D_score must be less than or equal to 10")
    if E_score is not None and E_score > E_SCORE_UPPER_BOUND:
        raise ValueError("E_score must be less than or equal to 10")
    if score is not None and D_score is not None and E_score is None:
        execution_estimate = round(score - D_score, 3)
        if execution_estimate < 0 or execution_estimate > E_SCORE_UPPER_BOUND:
            raise ValueError("execution_estimate must be between 0 and 10 when E_score is not available")

    if discipline and apparatus:
        allowed = MAG_APPARATUS if discipline == DisciplineEnum.MAG else WAG_APPARATUS
        if apparatus not in allowed:
            raise ValueError(f"apparatus {apparatus} is not valid for {discipline.value}")

    if vt_attempt is not None:
        if vt_attempt not in (1, 2):
            raise ValueError("vt_attempt must be 1 or 2")
        if apparatus and apparatus != "VT":
            raise ValueError("vt_attempt can only be provided for vault results")


def validate_result_score_upper_bound(apparatus: Optional[str], score: Optional[float]) -> None:
    if score is None:
        return
    if apparatus == "AA":
        return
    if score > NON_AA_SCORE_UPPER_BOUND:
        raise ValueError("score must be less than or equal to 20 for non-AA results")


def validate_result_bonus_policy(
    event_year: Optional[int],
    discipline: Optional["DisciplineEnum"],
    apparatus: Optional[str],
    Bonus: Optional[float],
) -> None:
    if Bonus is None:
        return

    if event_year is not None and event_year >= 2026 and score_equal(Bonus, 0.0):
        return

    if event_year is not None and event_year < 2025:
        raise ValueError("Bonus is only allowed from 2025 onward")

    discipline_value = discipline.value if hasattr(discipline, "value") else discipline

    if discipline_value == "WAG":
        if apparatus != "VT AVG":
            raise ValueError("WAG Bonus is only allowed for VT AVG")
        if not score_equal(Bonus, 0.2):
            raise ValueError("WAG Bonus must be 0.2 when provided")
        return

    if discipline_value == "MAG":
        if apparatus not in MAG_BONUS_APPARATUS_2025:
            raise ValueError("MAG Bonus is only allowed for FX, SR, VT, PB or HB")
        if not score_equal(Bonus, 0.1):
            raise ValueError("MAG Bonus must be 0.1 when provided")


def result_bonus_is_applicable(
    event_year: Optional[int],
    discipline: Optional["DisciplineEnum"],
    apparatus: Optional[str],
) -> bool:
    if event_year is None or event_year < 2025:
        return False

    discipline_value = discipline.value if hasattr(discipline, "value") else discipline
    if discipline_value == "WAG":
        return apparatus == "VT AVG"
    if discipline_value == "MAG":
        return apparatus in MAG_BONUS_APPARATUS_2025
    return False


def normalize_empty_execution_components(
    event_year: Optional[int],
    E_score: Optional[float],
    Penalty: Optional[float],
) -> tuple[Optional[float], Optional[float]]:
    if event_year is not None and event_year >= 2026:
        return (
            E_score,
            0.0 if Penalty is None else Penalty,
        )
    return E_score, Penalty


def normalize_empty_bonus_component(
    event_year: Optional[int],
    Bonus: Optional[float],
) -> Optional[float]:
    if event_year is not None and event_year >= 2026 and Bonus is None:
        return 0.0
    return Bonus


def calculate_expected_final_score(
    D_score: Optional[float],
    E_score: Optional[float],
    Penalty: Optional[float],
    Bonus: Optional[float],
) -> Optional[float]:
    if D_score is None or E_score is None:
        return None
    return round(D_score + E_score - (Penalty or 0.0) + (Bonus or 0.0), 3)


def validate_result_score_formula(
    event_year: Optional[int],
    score: Optional[float],
    D_score: Optional[float],
    E_score: Optional[float],
    Penalty: Optional[float],
    Bonus: Optional[float],
) -> None:
    if event_year is None or event_year < 2026 or score is None:
        return
    expected_score = calculate_expected_final_score(D_score, E_score, Penalty, Bonus)
    if expected_score is None:
        return
    if abs(round(score, 3) - expected_score) > SCORE_FORMULA_TOLERANCE:
        raise ValueError(
            f"Final score must equal D_score + E_score - Penalty + Bonus ({expected_score})"
        )


def validate_modern_required_score_components(
    event_year: Optional[int],
    E_score: Optional[float],
) -> None:
    if event_year is not None and event_year >= 2026 and E_score is None:
        raise ValueError("E_score is required from 2026 onward")


def validate_result_score_policy(
    event_year: Optional[int],
    discipline: Optional["DisciplineEnum"],
    apparatus: Optional[str],
    vt_attempt: Optional[int],
    score: Optional[float],
    D_score: Optional[float],
) -> None:
    if score is not None:
        return

    discipline_value = discipline.value if hasattr(discipline, "value") else discipline
    if (
        event_year is not None
        and event_year >= 2025
        and discipline_value == "WAG"
        and apparatus == "VT"
        and vt_attempt == 2
        and D_score is not None
    ):
        return

    raise ValueError("score is required except for WAG VT attempt 2 from 2025 onward with D_score")


def validate_result_day(day: Optional[int]) -> None:
    if day is not None and day < 1:
        raise ValueError("day must be greater than or equal to 1")


def validate_birth_year(birth_year: Optional[int]) -> None:
    current_year = Date.today().year
    if birth_year is not None and (birth_year < 1900 or birth_year > current_year):
        raise ValueError(f"birth_year must be between 1900 and {current_year}")


def calculate_execution_estimate(score: Optional[float], d_score: Optional[float]) -> Optional[float]:
    if score is None or d_score is None:
        return None
    execution_estimate = round(score - d_score, 3)
    if execution_estimate < 0 or execution_estimate > E_SCORE_UPPER_BOUND:
        return None
    return execution_estimate


def has_execution_estimate(score: Optional[float], d_score: Optional[float]) -> bool:
    return calculate_execution_estimate(score, d_score) is not None


def result_missing_fields(score: Optional[float], d_score: Optional[float]) -> list[str]:
    missing = []
    if score is None:
        missing.append("score")
    if d_score is None:
        missing.append("D_score")
    return missing


def result_is_complete(score: Optional[float], d_score: Optional[float]) -> bool:
    return not result_missing_fields(score, d_score)


def result_data_warnings(
    vault_attempt_order_uncertain: bool,
    execution_estimate_available: bool = False,
    execution_estimate_includes_unavailable_penalty: bool = False,
    execution_estimate_includes_unavailable_bonus: bool = False,
) -> list[str]:
    warnings = []
    if vault_attempt_order_uncertain:
        warnings.append(VAULT_ATTEMPT_ORDER_WARNING)
    if execution_estimate_available:
        if execution_estimate_includes_unavailable_penalty and execution_estimate_includes_unavailable_bonus:
            warnings.append(EXECUTION_ESTIMATE_WITH_PENALTY_AND_BONUS_WARNING)
        elif execution_estimate_includes_unavailable_penalty:
            warnings.append(EXECUTION_ESTIMATE_WITH_PENALTY_WARNING)
        elif execution_estimate_includes_unavailable_bonus:
            warnings.append(EXECUTION_ESTIMATE_WITH_BONUS_WARNING)
        else:
            warnings.append(EXECUTION_ESTIMATE_WARNING)
    return warnings


def validate_vault_attempt_order_uncertainty(
    apparatus: Optional[str],
    vt_attempt: Optional[int],
    vault_attempt_order_uncertain: bool,
) -> None:
    if vault_attempt_order_uncertain and (apparatus != "VT" or vt_attempt not in (1, 2)):
        raise ValueError("vault_attempt_order_uncertain can only be true for VT attempt 1 or 2")


class DisciplineEnum(str, Enum):
    MAG = "MAG"
    WAG = "WAG"


class EventDisciplineEnum(str, Enum):
    MAG = "MAG"
    WAG = "WAG"
    MAG_AND_WAG = "MAG and WAG"


class EventCategoryEnum(str, Enum):
    JUNIOR = "junior"
    SENIOR = "senior"
    JUNIOR_AND_SENIOR = "junior and senior"


class ResultCategoryEnum(str, Enum):
    JUNIOR = "junior"
    SENIOR = "senior"


CategoryEnum = EventCategoryEnum


class LevelEnum(str, Enum):
    OLYMPIC_GAMES = "Olympic Games"
    WORLD_CHAMPIONSHIPS = "World Championships"
    CONTINENTAL_CHAMPIONSHIPS = "Continental Championships"
    WORLD_CUP = "World Cup"
    WORLD_CHALLENGE_CUP = "World Challenge Cup"
    INTERNATIONAL_EVENT = "International Event"
    NATIONAL_EVENT = "National Event"


class EventCalendarStatusEnum(str, Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED_NO_RESULTS = "completed_no_results"
    COMPLETED_WITH_RESULTS = "completed_with_results"


class ApparatusMAGEnum(str, Enum):
    FX = "FX"  # Floor Exercise
    PH = "PH"  # Pommel Horse
    SR = "SR"  # Still Rings
    VT = "VT"  # Vault
    PB = "PB"  # Parallel Bars
    HB = "HB"  # High Bar
    AA = "AA"  # All-Around
    VT_AVG = "VT AVG"  # Vault Average


class ApparatusWAGEnum(str, Enum):
    VT = "VT"  # Vault
    UB = "UB"  # Uneven Bars
    BB = "BB"  # Balance Beam
    FX = "FX"  # Floor Exercise
    AA = "AA"  # All-Around
    VT_AVG = "VT AVG"  # Vault Average


class FormatEnum(str, Enum):
    TEAM = "team"
    INDIVIDUAL = "individual"
    APPARATUS = "apparatus"
    MIXED_TEAM = "mixed team"


class RoundEnum(str, Enum):
    QUALIFICATION = "qualification"
    FINAL = "final"


class ResultRankingMetricEnum(str, Enum):
    SCORE = "score"
    D_SCORE = "D_score"
    EXECUTION_ESTIMATE = "execution_estimate"
    E_SCORE = "E_score"
    PENALTY = "Penalty"
    BONUS = "Bonus"


class ResultDataQualityEnum(str, Enum):
    ALL = "all"
    COMPLETE = "complete"
    MISSING_D_SCORE = "missing_d_score"
    MISSING_SCORE = "missing_score"


class ScoreComponentStatusEnum(str, Enum):
    AVAILABLE = "available"
    NOT_AVAILABLE = "not_available"
    NOT_APPLICABLE = "not_applicable"


class ResultRankingScoreComponent(BaseModel):
    result_id: int
    apparatus: str
    vt_attempt: Optional[int] = None
    score: Optional[float] = None
    D_score: Optional[float] = None
    execution_estimate: Optional[float] = None
    E_score: Optional[float] = None
    Penalty: Optional[float] = None
    e_score_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    penalty_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    Bonus: Optional[float] = None
    bonus_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_APPLICABLE
    vault_attempt_order_uncertain: bool = False
    data_warnings: list[str] = Field(default_factory=list)


class RoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"


class LanguageEnum(str, Enum):
    EN = "en"
    IT = "it"
    ES = "es"
    FR = "fr"


class LanguagePreferenceSourceEnum(str, Enum):
    USER = "user"
    SELECTED = "selected"
    ACCEPT_LANGUAGE = "accept_language"
    DEFAULT = "default"


class DataSuggestionEntityTypeEnum(str, Enum):
    ATHLETE = "athlete"
    EVENT = "event"


class DataSuggestionStatusEnum(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EDITED = "edited"
    REJECTED = "rejected"


class AuditReviewStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REVERTED = "reverted"


class UserBase(BaseModel):
    email: EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    preferred_language: LanguageEnum = LanguageEnum.EN


class EmailTokenRequest(BaseModel):
    token: str = Field(min_length=20, max_length=512)


class EmailAddressRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    mfa_code: Optional[str] = Field(default=None, min_length=6, max_length=64)


class DemoLoginRequest(BaseModel):
    role: RoleEnum = RoleEnum.USER


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=20, max_length=512)
    new_password: str = Field(min_length=12, max_length=128)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)


class MFAConfirmRequest(BaseModel):
    code: str = Field(min_length=6, max_length=64)


class UserRead(UserBase):
    id: int
    role: RoleEnum
    preferred_language: LanguageEnum
    is_verified: bool
    is_active: bool
    mfa_enabled: bool
    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: RoleEnum


class UserRoleByEmailUpdate(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.ADMIN


class AuthMessage(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginResponse(BaseModel):
    access_token: Optional[str] = None
    token_type: str = "bearer"
    mfa_setup_required: bool = False
    mfa_required: bool = False
    mfa_setup_token: Optional[str] = None


class MFASetupResponse(BaseModel):
    secret: str
    provisioning_uri: str


class MFAConfirmResponse(Token):
    recovery_codes: list[str]


class TokenData(BaseModel):
    email: Optional[str] = None


class AthleteBase(BaseModel):
    first_name: str
    last_name: str
    birth_year: Optional[int] = None
    country: Optional[str] = None
    discipline: DisciplineEnum
    image_url: Optional[str] = None

    @model_validator(mode="after")
    def validate_year(self):
        validate_birth_year(self.birth_year)
        return self


class AthleteCreate(AthleteBase):
    pass


class AthleteCountryChangeBase(BaseModel):
    from_country: Optional[str] = None
    to_country: str
    change_year: int


class AthleteCountryChangeCreate(BaseModel):
    to_country: str
    change_year: int
    from_country: Optional[str] = None


class AthleteCountryChangeRead(AthleteCountryChangeBase):
    id: int
    athlete_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AthleteRead(AthleteBase):
    id: int
    is_profile_verified: bool = False
    world_gymnastics_athlete_id: Optional[str] = None
    world_gymnastics_profile_url: Optional[str] = None
    world_gymnastics_status: Optional[str] = None
    world_gymnastics_verified_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by_admin_id: Optional[int] = None
    country_changes: list[AthleteCountryChangeRead] = []
    model_config = ConfigDict(from_attributes=True)


class AthleteAdminRead(AthleteRead):
    world_gymnastics_verified_by_admin_id: Optional[int] = None


class AthleteUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_year: Optional[int] = None
    country: Optional[str] = None
    country_change_year: Optional[int] = None
    discipline: Optional[DisciplineEnum] = None
    image_url: Optional[str] = None

    @model_validator(mode="after")
    def validate_year(self):
        validate_birth_year(self.birth_year)
        return self


class AthleteWorldGymnasticsUpdate(BaseModel):
    world_gymnastics_athlete_id: Optional[str] = None
    world_gymnastics_profile_url: Optional[str] = None
    world_gymnastics_status: Optional[str] = None
    remove_verification_badge: bool = False

    @model_validator(mode="after")
    def validate_world_gymnastics_fields(self):
        fig_id = (self.world_gymnastics_athlete_id or "").strip()
        if fig_id and not fig_id.isdigit():
            raise ValueError("world_gymnastics_athlete_id must be numeric")

        profile_url = (self.world_gymnastics_profile_url or "").strip()
        if profile_url:
            parsed = urlparse(profile_url)
            if parsed.scheme not in {"http", "https"}:
                raise ValueError("world_gymnastics_profile_url must use http or https")
            hostname = (parsed.hostname or "").lower()
            if hostname != "gymnastics.sport" and not hostname.endswith(".gymnastics.sport"):
                raise ValueError("world_gymnastics_profile_url must use gymnastics.sport")
            profile_id = parse_qs(parsed.query).get("id", [None])[0]
            if not profile_id or not profile_id.isdigit():
                raise ValueError("world_gymnastics_profile_url must include a numeric id")
            if fig_id and profile_id != fig_id:
                raise ValueError("FIG ID and World Gymnastics profile URL id must match")

        status = (self.world_gymnastics_status or "").strip()
        if len(status) > 100:
            raise ValueError("world_gymnastics_status must be 100 characters or fewer")
        return self


class AthleteMergeRequest(BaseModel):
    target_athlete_id: int
    reason: Optional[str] = None


class AthleteMergeCommitRequest(AthleteMergeRequest):
    confirm: bool = False


class AthleteMergeResultConflict(BaseModel):
    source_result_id: int
    target_result_id: int
    event_id: int
    event_name: str
    event_year: int
    discipline: DisciplineEnum
    category: ResultCategoryEnum
    apparatus: Optional[str] = None
    vt_attempt: Optional[int] = None
    day: Optional[int] = None
    format: FormatEnum
    round: RoundEnum
    source_score: Optional[float] = None
    target_score: Optional[float] = None
    source_D_score: Optional[float] = None
    target_D_score: Optional[float] = None
    same_score: bool


class AthleteMergePreview(BaseModel):
    source_athlete: AthleteRead
    target_athlete: AthleteRead
    can_merge: bool
    blocking_reasons: list[str] = []
    result_conflicts: list[AthleteMergeResultConflict] = []
    source_result_count: int
    target_result_count: int
    followed_athletes_to_move: int = 0
    followed_athletes_duplicates_to_remove: int = 0
    country_changes_to_move: int = 0
    country_changes_duplicates_to_remove: int = 0
    data_suggestions_to_move: int = 0
    notifications_to_relink: int = 0
    metadata_to_copy: dict[str, str] = {}
    metadata_differences: dict[str, dict[str, Optional[str]]] = {}


class AthleteMergeCommitResponse(AthleteMergePreview):
    merged: bool
    moved_results: int = 0
    moved_followed_athletes: int = 0
    removed_duplicate_followed_athletes: int = 0
    moved_country_changes: int = 0
    removed_duplicate_country_changes: int = 0
    moved_data_suggestions: int = 0
    relinked_notifications: int = 0
    copied_metadata_fields: list[str] = []
    deleted_source_athlete_id: int


class EventBase(BaseModel):
    name: str
    location: Optional[str] = None
    venue: Optional[str] = None
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    year: int
    discipline: EventDisciplineEnum
    category: EventCategoryEnum
    level: LevelEnum
    image_url: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: int
    world_gymnastics_event_id: Optional[str] = None
    world_gymnastics_event_url: Optional[str] = None
    world_gymnastics_status: Optional[str] = None
    world_gymnastics_verified_at: Optional[datetime] = None
    world_gymnastics_verified_by_admin_id: Optional[int] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by_admin_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class EventUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    venue: Optional[str] = None
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    year: Optional[int] = None
    discipline: Optional[EventDisciplineEnum] = None
    category: Optional[EventCategoryEnum] = None
    level: Optional[LevelEnum] = None
    image_url: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class EventCalendarItem(EventBase):
    id: Optional[int] = None
    calendar_entry_id: Optional[int] = None
    calendar_source: Optional[str] = None
    is_calendar_only: bool = False
    world_gymnastics_event_id: Optional[str] = None
    world_gymnastics_event_url: Optional[str] = None
    world_gymnastics_status: Optional[str] = None
    world_gymnastics_verified_at: Optional[datetime] = None
    world_gymnastics_verified_by_admin_id: Optional[int] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by_admin_id: Optional[int] = None
    result_count: int
    has_results: bool
    calendar_status: EventCalendarStatusEnum


class EventResultReminder(BaseModel):
    event: EventCalendarItem
    days_since_end: int


class EventResultReminderNotificationResponse(BaseModel):
    created_notifications: int
    reminders: list[EventResultReminder]


class AdminEventCalendarSummary(BaseModel):
    total_events: int
    upcoming: int
    ongoing: int
    completed_no_results: int
    completed_with_results: int
    with_results: int
    without_results: int


class AdminEventCalendarView(BaseModel):
    events: list[EventCalendarItem]
    summary: AdminEventCalendarSummary
    reminders: list[EventResultReminder]


class AdminIncompleteAthlete(BaseModel):
    id: int
    first_name: str
    last_name: str
    discipline: DisciplineEnum
    country: Optional[str] = None
    birth_year: Optional[int] = None
    image_url: Optional[str] = None
    world_gymnastics_profile_url: Optional[str] = None
    world_gymnastics_status: Optional[str] = None
    created_at: datetime
    missing_fields: list[str]


class AdminIncompleteEvent(BaseModel):
    id: int
    name: str
    year: int
    discipline: EventDisciplineEnum
    category: EventCategoryEnum
    level: LevelEnum
    location: Optional[str] = None
    venue: Optional[str] = None
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    image_url: Optional[str] = None
    world_gymnastics_event_url: Optional[str] = None
    world_gymnastics_status: Optional[str] = None
    created_at: datetime
    missing_fields: list[str]


class AdminEntitiesToCompleteResponse(BaseModel):
    athletes: list[AdminIncompleteAthlete]
    events: list[AdminIncompleteEvent]
    total_athletes: int
    total_events: int


class DataSuggestionBase(BaseModel):
    entity_type: DataSuggestionEntityTypeEnum
    entity_id: int
    field_name: str
    suggested_value: str
    confidence: Optional[float] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    evidence: Optional[str] = None


class DataSuggestionCreate(DataSuggestionBase):
    pass


class DataSuggestionDecision(BaseModel):
    value: Optional[str] = None


class DataSuggestionGenerateRequest(BaseModel):
    entity_type: DataSuggestionEntityTypeEnum
    entity_id: int
    fields: Optional[list[str]] = None
    create_suggestions: bool = True


class DataSuggestionCandidate(BaseModel):
    field_name: str
    suggested_value: str
    confidence: Optional[float] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    evidence: Optional[str] = None


class DataSuggestionRead(DataSuggestionBase):
    id: int
    status: DataSuggestionStatusEnum
    reviewed_value: Optional[str] = None
    created_by_admin_id: Optional[int] = None
    reviewed_by_admin_id: Optional[int] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class AthleteAdminView(BaseModel):
    athlete: AthleteAdminRead
    pending_suggestions: list[DataSuggestionRead]


class EventAdminView(BaseModel):
    event: EventRead
    pending_suggestions: list[DataSuggestionRead]


class DataSuggestionGenerateResponse(BaseModel):
    entity_type: DataSuggestionEntityTypeEnum
    entity_id: int
    requested_fields: list[str]
    skipped_fields: list[str]
    candidates: list[DataSuggestionCandidate]
    created_suggestions: list[DataSuggestionRead]


class WorldGymnasticsWarning(BaseModel):
    type: str
    message: str


class WorldGymnasticsAthleteCandidate(BaseModel):
    fig_id: str
    first_name: str
    last_name: str
    country: Optional[str] = None
    discipline: Optional[str] = None
    status: Optional[str] = None
    profile_url: str
    match_score: float


class WorldGymnasticsAthleteSearchResponse(BaseModel):
    athlete_id: int
    query: dict
    candidates: list[WorldGymnasticsAthleteCandidate]
    warnings: list[WorldGymnasticsWarning] = []


class WorldGymnasticsAthleteSuggestionRequest(BaseModel):
    fig_athlete_id: Optional[str] = None
    fig_profile_url: Optional[str] = None
    fields: Optional[list[str]] = None
    create_suggestions: bool = True

    @model_validator(mode="after")
    def validate_source(self):
        if not self.fig_athlete_id and not self.fig_profile_url:
            raise ValueError("fig_athlete_id or fig_profile_url must be provided")
        return self


class WorldGymnasticsAthleteProfileRead(BaseModel):
    fig_id: str
    profile_url: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    birth_year: Optional[int] = None
    disciplines: list[str] = []
    image_url: Optional[str] = None
    status: Optional[str] = None


class WorldGymnasticsAthleteSuggestionResponse(BaseModel):
    athlete_id: int
    source_url: str
    matched_profile: WorldGymnasticsAthleteProfileRead
    requested_fields: list[str]
    skipped_fields: list[str]
    warnings: list[WorldGymnasticsWarning]
    suggestion_candidates: list[DataSuggestionCandidate]
    created_suggestions: list[DataSuggestionRead]


class WorldGymnasticsEventCandidate(BaseModel):
    event_id: str
    title: str
    city: Optional[str] = None
    country: Optional[str] = None
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    disciplines: list[str] = []
    status: Optional[str] = None
    event_url: str
    match_score: float


class WorldGymnasticsEventSearchResponse(BaseModel):
    event_id: int
    query: dict
    candidates: list[WorldGymnasticsEventCandidate]
    warnings: list[WorldGymnasticsWarning] = []


class WorldGymnasticsEventSuggestionRequest(BaseModel):
    fig_event_id: Optional[str] = None
    fig_event_url: Optional[str] = None
    fields: Optional[list[str]] = None
    create_suggestions: bool = True

    @model_validator(mode="after")
    def validate_source(self):
        if not self.fig_event_id and not self.fig_event_url:
            raise ValueError("fig_event_id or fig_event_url must be provided")
        return self


class WorldGymnasticsEventProfileRead(BaseModel):
    event_id: str
    event_url: str
    title: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    venue: Optional[str] = None
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    disciplines: list[str] = []
    discipline: Optional[EventDisciplineEnum] = None
    category: Optional[EventCategoryEnum] = None
    level: Optional[LevelEnum] = None
    status: Optional[str] = None


class WorldGymnasticsEventSuggestionResponse(BaseModel):
    event_id: int
    source_url: str
    matched_event: WorldGymnasticsEventProfileRead
    requested_fields: list[str]
    skipped_fields: list[str]
    warnings: list[WorldGymnasticsWarning]
    suggestion_candidates: list[DataSuggestionCandidate]
    created_suggestions: list[DataSuggestionRead]


class ResultBase(BaseModel):
    athlete_id: int
    event_id: int
    represented_country: Optional[str] = None
    discipline: DisciplineEnum
    category: ResultCategoryEnum
    apparatus: Optional[str] = None
    vt_attempt: Optional[int] = None
    day: Optional[int] = None
    format: FormatEnum
    round: RoundEnum
    D_score: Optional[float] = None
    E_score: Optional[float] = None
    Penalty: Optional[float] = None
    Bonus: Optional[float] = None
    score: Optional[float] = None
    rank: Optional[int] = None
    vault_attempt_order_uncertain: bool = False

    @model_validator(mode="after")
    def validate_result(self):
        validate_result_scoring(
            self.discipline,
            self.apparatus,
            self.vt_attempt,
            self.score,
            self.D_score,
            self.E_score,
            self.Penalty,
            self.Bonus,
        )
        validate_vault_attempt_order_uncertainty(
            self.apparatus,
            self.vt_attempt,
            self.vault_attempt_order_uncertain,
        )
        validate_result_day(self.day)
        return self


class ResultCreate(ResultBase):
    pass


class ResultUpdate(BaseModel):
    athlete_id: Optional[int] = None
    event_id: Optional[int] = None
    represented_country: Optional[str] = None
    discipline: Optional[DisciplineEnum] = None
    category: Optional[ResultCategoryEnum] = None
    apparatus: Optional[str] = None
    vt_attempt: Optional[int] = None
    day: Optional[int] = None
    format: Optional[FormatEnum] = None
    round: Optional[RoundEnum] = None
    D_score: Optional[float] = None
    E_score: Optional[float] = None
    Penalty: Optional[float] = None
    Bonus: Optional[float] = None
    score: Optional[float] = None
    rank: Optional[int] = None
    vault_attempt_order_uncertain: Optional[bool] = None

    @model_validator(mode="after")
    def validate_result(self):
        validate_result_scoring(
            self.discipline,
            self.apparatus,
            self.vt_attempt,
            self.score,
            self.D_score,
            self.E_score,
            self.Penalty,
            self.Bonus,
        )
        validate_result_day(self.day)
        return self


class ResultRead(ResultBase):
    id: int
    e_score_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    penalty_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    bonus_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_APPLICABLE
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by_admin_id: Optional[int] = None

    @computed_field
    @property
    def execution_estimate(self) -> Optional[float]:
        return calculate_execution_estimate(self.score, self.D_score)

    @computed_field
    @property
    def is_complete(self) -> bool:
        return result_is_complete(self.score, self.D_score)

    @computed_field
    @property
    def missing_fields(self) -> list[str]:
        return result_missing_fields(self.score, self.D_score)

    @computed_field
    @property
    def data_warnings(self) -> list[str]:
        return result_data_warnings(
            self.vault_attempt_order_uncertain,
            has_execution_estimate(self.score, self.D_score),
            self.penalty_status == ScoreComponentStatusEnum.NOT_AVAILABLE,
            self.bonus_status == ScoreComponentStatusEnum.NOT_AVAILABLE,
        )

    model_config = ConfigDict(from_attributes=True)


class FollowedAthleteBase(BaseModel):
    athlete_id: int


class FollowedAthleteCreate(FollowedAthleteBase):
    pass


class FollowedAthleteRead(FollowedAthleteBase):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FollowedAthleteDetail(FollowedAthleteRead):
    athlete: AthleteRead
    result_count: int
    latest_result: Optional[ResultRead] = None


class SavedEventBase(BaseModel):
    event_id: int


class SavedEventCreate(SavedEventBase):
    pass


class SavedEventRead(SavedEventBase):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SavedEventDetail(SavedEventRead):
    event: EventCalendarItem


class SavedDashboardViewBase(BaseModel):
    name: str
    description: Optional[str] = None
    view_type: str
    chart_type: Optional[str] = None
    metric: Optional[ResultRankingMetricEnum] = None
    filters: dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False
    position: int = 0


class SavedDashboardViewCreate(SavedDashboardViewBase):
    pass


class SavedDashboardViewUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    view_type: Optional[str] = None
    chart_type: Optional[str] = None
    metric: Optional[ResultRankingMetricEnum] = None
    filters: Optional[dict[str, Any]] = None
    is_default: Optional[bool] = None
    position: Optional[int] = None


class SavedDashboardViewRead(SavedDashboardViewBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class LanguageOption(BaseModel):
    code: LanguageEnum
    label: str


class LanguageOptions(BaseModel):
    default_language: LanguageEnum = LanguageEnum.EN
    supported_languages: list[LanguageOption]


class UserLanguagePreference(BaseModel):
    preferred_language: LanguageEnum
    source: LanguagePreferenceSourceEnum = LanguagePreferenceSourceEnum.USER
    is_authenticated: bool = True


class AthleteWithResults(BaseModel):
    athlete: AthleteRead
    results: list[ResultRead]
    model_config = ConfigDict(from_attributes=True)


class ScorePoint(BaseModel):
    date: Date
    represented_country: Optional[str] = None
    score: Optional[float] = None
    category: ResultCategoryEnum
    D_score: Optional[float] = None
    execution_estimate: Optional[float] = None
    E_score: Optional[float] = None
    Penalty: Optional[float] = None
    e_score_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    penalty_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    Bonus: Optional[float] = None
    bonus_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_APPLICABLE
    apparatus: Optional[str] = None
    day: Optional[int] = None
    event_name: str
    round: str
    rank: Optional[int] = None
    is_complete: bool = True
    missing_fields: list[str] = Field(default_factory=list)
    vault_attempt_order_uncertain: bool = False
    data_warnings: list[str] = Field(default_factory=list)


class AthleteScoresOverTime(BaseModel):
    athlete: AthleteRead
    scores: list[ScorePoint]


class ComparisonScorePoint(BaseModel):
    athlete_id: int
    athlete_name: str
    date: Date
    represented_country: Optional[str] = None
    score: Optional[float] = None
    category: ResultCategoryEnum
    D_score: Optional[float] = None
    execution_estimate: Optional[float] = None
    E_score: Optional[float] = None
    Penalty: Optional[float] = None
    e_score_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    penalty_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    Bonus: Optional[float] = None
    bonus_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_APPLICABLE
    apparatus: Optional[str] = None
    day: Optional[int] = None
    event_name: str
    is_complete: bool = True
    missing_fields: list[str] = Field(default_factory=list)
    vault_attempt_order_uncertain: bool = False
    data_warnings: list[str] = Field(default_factory=list)


class AthletesComparisonScores(BaseModel):
    comparison: list[ComparisonScorePoint]


class AthleteStats(BaseModel):
    athlete: AthleteRead
    total_results: int
    average_score: Optional[float] = None
    max_score: Optional[float] = None
    min_score: Optional[float] = None
    average_D_score: Optional[float] = None
    average_E_score: Optional[float] = None
    apparatus_stats: dict[str, dict]  # e.g., {"FX": {"average": 14.5, "count": 10}}


class ResultEntryContextBase(BaseModel):
    apparatus: Optional[str] = None
    day: Optional[int] = None
    format: Optional[FormatEnum] = None
    round: Optional[RoundEnum] = None

    @model_validator(mode="after")
    def validate_context(self):
        validate_result_day(self.day)
        return self


class ResultEntryContextCreate(ResultEntryContextBase):
    pass


class ResultEntryContextRead(ResultEntryContextBase):
    id: int
    event_id: int
    admin_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ResultEntryAthlete(BaseModel):
    first_name: str
    last_name: str
    birth_year: Optional[int] = None
    country: Optional[str] = None
    image_url: Optional[str] = None

    @model_validator(mode="after")
    def validate_year(self):
        validate_birth_year(self.birth_year)
        return self


class ResultEntryItem(BaseModel):
    athlete_id: Optional[int] = None
    athlete: Optional[ResultEntryAthlete] = None
    represented_country: Optional[str] = None
    discipline: DisciplineEnum
    category: ResultCategoryEnum
    apparatus: Optional[str] = None
    vt_attempt: Optional[int] = None
    day: Optional[int] = None
    format: Optional[FormatEnum] = None
    round: Optional[RoundEnum] = None
    D_score: Optional[float] = None
    E_score: Optional[float] = None
    Penalty: Optional[float] = None
    Bonus: Optional[float] = None
    score: Optional[float] = None
    rank: Optional[int] = None

    @model_validator(mode="after")
    def validate_result(self):
        if self.athlete_id is None and self.athlete is None:
            raise ValueError("athlete_id or athlete must be provided")
        validate_result_scoring(
            self.discipline,
            self.apparatus,
            self.vt_attempt,
            self.score,
            self.D_score,
            self.E_score,
            self.Penalty,
            self.Bonus,
        )
        validate_result_day(self.day)
        return self


class EventResultBulkCreate(BaseModel):
    results: list[ResultEntryItem]


class EventResultGroup(BaseModel):
    discipline: DisciplineEnum
    category: ResultCategoryEnum
    format: FormatEnum
    apparatus: Optional[str] = None
    day: Optional[int] = None
    round: RoundEnum
    count: int
    model_config = ConfigDict(from_attributes=True)


class EventResultFilterOptions(BaseModel):
    disciplines: list[DisciplineEnum]
    categories: list[ResultCategoryEnum]
    formats: list[FormatEnum]
    rounds: list[RoundEnum]
    apparatuses: list[str]
    days: list[int]
    ranking_metrics: list[ResultRankingMetricEnum]
    data_qualities: list[ResultDataQualityEnum]
    default_ranking_metric: ResultRankingMetricEnum = ResultRankingMetricEnum.SCORE
    default_data_quality: ResultDataQualityEnum = ResultDataQualityEnum.ALL


class ResultRankingEntry(BaseModel):
    result_id: int
    computed_rank: int
    official_rank: Optional[int] = None
    athlete_id: int
    athlete_name: str
    country: Optional[str] = None
    event_id: int
    event_name: str
    year: int
    date: Optional[Date] = None
    discipline: DisciplineEnum
    category: ResultCategoryEnum
    apparatus: Optional[str] = None
    vt_attempt: Optional[int] = None
    day: Optional[int] = None
    format: FormatEnum
    round: RoundEnum
    score: Optional[float] = None
    D_score: Optional[float] = None
    execution_estimate: Optional[float] = None
    E_score: Optional[float] = None
    Penalty: Optional[float] = None
    e_score_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    penalty_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    Bonus: Optional[float] = None
    bonus_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_APPLICABLE
    is_complete: bool = True
    missing_fields: list[str] = Field(default_factory=list)
    vault_attempt_order_uncertain: bool = False
    data_warnings: list[str] = Field(default_factory=list)
    apparatus_scores: list[ResultRankingScoreComponent] = Field(default_factory=list)


class ScoringCycleRead(BaseModel):
    label: str
    start_year: int
    end_year: int
    is_covid_extended: bool = False


class ResultRanking(BaseModel):
    ranking: list[ResultRankingEntry]
    discipline: Optional[DisciplineEnum] = None
    scoring_cycle: Optional[ScoringCycleRead] = None
    available_scoring_cycles: list[ScoringCycleRead] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GlobalSearchAthlete(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    discipline: DisciplineEnum
    result_count: int = 0


class GlobalSearchEvent(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    year: int
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    discipline: EventDisciplineEnum
    category: EventCategoryEnum
    result_count: int = 0


class GlobalSearchResult(BaseModel):
    result_id: int
    athlete_id: int
    athlete_name: str
    country: Optional[str] = None
    event_id: int
    event_name: str
    year: int
    date: Optional[Date] = None
    discipline: DisciplineEnum
    category: ResultCategoryEnum
    apparatus: Optional[str] = None
    format: FormatEnum
    round: RoundEnum
    score: Optional[float] = None
    D_score: Optional[float] = None


class GlobalSearchResponse(BaseModel):
    query: str
    total_count: int
    structured_result_search: bool = False
    athletes: list[GlobalSearchAthlete] = Field(default_factory=list)
    events: list[GlobalSearchEvent] = Field(default_factory=list)
    results: list[GlobalSearchResult] = Field(default_factory=list)
    related_results: list[GlobalSearchResult] = Field(default_factory=list)


class AnalyticsAggregationEnum(str, Enum):
    RAW = "raw"
    BEST_BY_EVENT = "best_by_event"
    AVERAGE_BY_YEAR = "average_by_year"
    AVERAGE_BY_APPARATUS = "average_by_apparatus"


class ApparatusProfileCriterionEnum(str, Enum):
    AVERAGE = "average"
    BEST = "best"
    LATEST = "latest"


class AnalyticsFilterOptions(BaseModel):
    years: list[int]
    disciplines: list[DisciplineEnum]
    categories: list[ResultCategoryEnum]
    formats: list[FormatEnum]
    rounds: list[RoundEnum]
    apparatuses: list[str]
    countries: list[str]
    event_levels: list[LevelEnum]
    ranking_metrics: list[ResultRankingMetricEnum]
    data_qualities: list[ResultDataQualityEnum]
    scoring_cycles: list[ScoringCycleRead] = Field(default_factory=list)
    default_ranking_metric: ResultRankingMetricEnum = ResultRankingMetricEnum.SCORE
    default_data_quality: ResultDataQualityEnum = ResultDataQualityEnum.ALL


class AnalyticsFilters(BaseModel):
    athlete_ids: list[int] = []
    event_id: Optional[int] = None
    discipline: Optional[DisciplineEnum] = None
    category: Optional[ResultCategoryEnum] = None
    format: Optional[FormatEnum] = None
    round: Optional[RoundEnum] = None
    apparatus: Optional[str] = None
    day: Optional[int] = None
    country: Optional[str] = None
    level: Optional[LevelEnum] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    metric: ResultRankingMetricEnum = ResultRankingMetricEnum.SCORE
    aggregation: Optional[AnalyticsAggregationEnum] = None
    data_quality: ResultDataQualityEnum = ResultDataQualityEnum.ALL


class AnalyticsChartPoint(BaseModel):
    x: str
    value: float
    score: Optional[float] = None
    D_score: Optional[float] = None
    year: Optional[int] = None
    date: Optional[Date] = None
    event_start_date: Optional[Date] = None
    event_end_date: Optional[Date] = None
    date_precision: Optional[str] = None
    result_id: Optional[int] = None
    event_id: Optional[int] = None
    event_name: Optional[str] = None
    athlete_id: Optional[int] = None
    athlete_name: Optional[str] = None
    country: Optional[str] = None
    discipline: Optional[DisciplineEnum] = None
    category: Optional[ResultCategoryEnum] = None
    apparatus: Optional[str] = None
    vt_attempt: Optional[int] = None
    day: Optional[int] = None
    format: Optional[FormatEnum] = None
    round: Optional[RoundEnum] = None
    result_count: int = 1
    complete_result_count: int = 0
    partial_result_count: int = 0
    execution_estimate: Optional[float] = None
    E_score: Optional[float] = None
    Penalty: Optional[float] = None
    e_score_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    penalty_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    Bonus: Optional[float] = None
    bonus_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_APPLICABLE
    is_complete: bool = True
    missing_fields: list[str] = Field(default_factory=list)
    vault_attempt_order_uncertain: bool = False
    data_warnings: list[str] = Field(default_factory=list)


class AnalyticsAthleteSeries(BaseModel):
    athlete_id: int
    athlete_name: str
    country: Optional[str] = None
    discipline: DisciplineEnum
    points: list[AnalyticsChartPoint]


class AnalyticsAthletesComparison(BaseModel):
    metric: ResultRankingMetricEnum
    aggregation: AnalyticsAggregationEnum
    filters: AnalyticsFilters
    series: list[AnalyticsAthleteSeries]


class AnalyticsSummary(BaseModel):
    total_results: int
    event_count: int
    average_value: Optional[float] = None
    best_value: Optional[float] = None
    worst_value: Optional[float] = None
    latest_value: Optional[float] = None


class AnalyticsGroupStat(BaseModel):
    key: str
    count: int
    average_value: Optional[float] = None
    best_value: Optional[float] = None
    worst_value: Optional[float] = None


class AnalyticsAthleteDashboard(BaseModel):
    athlete: AthleteRead
    metric: ResultRankingMetricEnum
    filters: AnalyticsFilters
    summary: AnalyticsSummary
    trend: list[AnalyticsChartPoint]
    by_year: list[AnalyticsGroupStat]
    by_apparatus: list[AnalyticsGroupStat]
    recent_results: list[AnalyticsChartPoint]


class ApparatusProfileVertex(BaseModel):
    apparatus: str
    value: Optional[float] = None
    normalized_value: Optional[float] = None
    result_count: int
    complete_result_count: int
    partial_result_count: int
    is_available: bool
    source_result_id: Optional[int] = None
    source_event_id: Optional[int] = None
    source_event_name: Optional[str] = None
    source_date: Optional[Date] = None
    missing_fields: list[str] = Field(default_factory=list)


class AthleteApparatusProfile(BaseModel):
    athlete: AthleteRead
    discipline: DisciplineEnum
    shape: str
    metric: ResultRankingMetricEnum
    metric_direction: str
    criterion: ApparatusProfileCriterionEnum
    filters: AnalyticsFilters
    apparatus_order: list[str]
    vertices: list[ApparatusProfileVertex]
    available_metrics: list[ResultRankingMetricEnum]
    available_data_qualities: list[ResultDataQualityEnum]


class AthleteProfileView(BaseModel):
    athlete: AthleteRead
    dashboard: AnalyticsAthleteDashboard
    apparatus_profile: AthleteApparatusProfile
    available_metrics: list[ResultRankingMetricEnum]
    available_data_qualities: list[ResultDataQualityEnum]
    available_apparatuses: list[str]


class AnalyticsAgePoint(BaseModel):
    athlete_id: int
    athlete_name: str
    country: Optional[str] = None
    birth_year: int
    age: int
    event_id: int
    event_name: str
    event_year: int
    event_date: Optional[Date] = None
    discipline: DisciplineEnum
    category: ResultCategoryEnum
    result_count: int
    apparatuses: list[str]


class AnalyticsCountryAgeAverage(BaseModel):
    country: str
    athlete_count: int
    athlete_event_count: int
    result_count: int
    average_age: float
    min_age: int
    max_age: int


class AnalyticsAgeByCountry(BaseModel):
    filters: AnalyticsFilters
    age_precision: str = "birth_year_vs_event_year"
    total_athlete_event_points: int
    missing_birth_year_count: int
    country_averages: list[AnalyticsCountryAgeAverage]
    points: list[AnalyticsAgePoint]


class ResultTrendPoint(BaseModel):
    result_id: int
    event_id: int
    event_name: str
    date: Date
    represented_country: Optional[str] = None
    category: ResultCategoryEnum
    apparatus: Optional[str] = None
    day: Optional[int] = None
    round: RoundEnum
    score: Optional[float] = None
    D_score: Optional[float] = None
    execution_estimate: Optional[float] = None
    E_score: Optional[float] = None
    Penalty: Optional[float] = None
    e_score_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    penalty_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_AVAILABLE
    Bonus: Optional[float] = None
    bonus_status: ScoreComponentStatusEnum = ScoreComponentStatusEnum.NOT_APPLICABLE
    rank: Optional[int] = None
    delta_from_previous: Optional[float] = None
    rolling_average: float
    is_complete: bool = True
    missing_fields: list[str] = Field(default_factory=list)
    vault_attempt_order_uncertain: bool = False
    data_warnings: list[str] = Field(default_factory=list)


class ResultTrend(BaseModel):
    athlete: AthleteRead
    points: list[ResultTrendPoint]


class AthleteSuggestion(BaseModel):
    id: int
    first_name: str
    last_name: str
    discipline: DisciplineEnum
    country: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class EventRankingFilters(BaseModel):
    discipline: Optional[DisciplineEnum] = None
    category: Optional[ResultCategoryEnum] = None
    format: Optional[FormatEnum] = None
    apparatus: Optional[str] = None
    round: Optional[RoundEnum] = None
    day: Optional[int] = None
    athlete: Optional[str] = None
    sort_by: ResultRankingMetricEnum = ResultRankingMetricEnum.SCORE
    data_quality: ResultDataQualityEnum = ResultDataQualityEnum.ALL


class EventRankingView(BaseModel):
    event: EventRead
    filter_options: EventResultFilterOptions
    athlete_suggestions: list[AthleteSuggestion]
    applied_filters: EventRankingFilters
    results: list[ResultRankingEntry]
    total_results: int


class EventProfileView(BaseModel):
    event: EventCalendarItem
    filter_options: EventResultFilterOptions
    result_groups: list[EventResultGroup]
    applied_filters: EventRankingFilters
    default_ranking: list[ResultRankingEntry]
    total_results: int
    empty_state: Optional[str] = None


class EventManualEntryOptions(BaseModel):
    event: EventRead
    disciplines: list[DisciplineEnum]
    categories: list[ResultCategoryEnum]
    apparatus_by_discipline: dict[DisciplineEnum, list[str]]
    formats: list[FormatEnum]
    rounds: list[RoundEnum]
    required_context_fields: list[str]
    optional_context_fields: list[str]
    required_result_fields: list[str]
    optional_result_fields: list[str]
    required_fields: list[str]
    optional_score_fields: list[str]
    current_context: Optional[ResultEntryContextRead] = None
    athlete_suggestions: list[AthleteSuggestion]
    can_create_missing_athlete: bool
    athlete_lookup_min_chars: int
    athlete_create_fields: list[str]


class EventAthleteResolveRequest(BaseModel):
    first_name: str
    last_name: str
    discipline: Optional[DisciplineEnum] = None
    birth_year: Optional[int] = None
    country: Optional[str] = None
    image_url: Optional[str] = None
    create_if_missing: bool = True

    @model_validator(mode="after")
    def validate_year(self):
        validate_birth_year(self.birth_year)
        return self


class EventAthleteResolveResponse(BaseModel):
    athlete: Optional[AthleteRead] = None
    created: bool
    suggestions: list[AthleteSuggestion]


class EventCreateManualOptions(BaseModel):
    disciplines: list[EventDisciplineEnum]
    categories: list[EventCategoryEnum]
    levels: list[LevelEnum]
    required_fields: list[str]
    optional_fields: list[str]
    next_step: str


class CalendarImportRowPreview(BaseModel):
    sheet: str
    row: int
    year: int
    date_label: str
    event_name: str
    start_date: Date
    end_date: Date
    matched_event_ids: list[int] = []
    matched_event_names: list[str] = []
    match_status: str
    action: str
    inferred_discipline: EventDisciplineEnum
    inferred_category: EventCategoryEnum
    inferred_level: LevelEnum


class CalendarImportPreview(BaseModel):
    filename: str
    create_missing_from_year: int
    parsed_rows: int
    years: list[int]
    matched_rows: int
    matched_events: int
    would_update_events: int
    already_up_to_date_events: int
    would_create_events: int
    unmatched_historical_rows: int
    duplicate_source_rows: list[dict]
    matched_event_source_conflicts: list[dict]
    issues: list[dict]
    sample_rows: list[CalendarImportRowPreview]
    rows: list[CalendarImportRowPreview]


class CalendarImportCommit(CalendarImportPreview):
    committed: bool
    updated_events: int
    created_events: int
    skipped_unmatched_historical_rows: int
    created_admin_notifications: int


class GymternetImportPreview(BaseModel):
    filename: str
    year_hint: Optional[int] = None
    parsed_rows: int
    importable_results: int
    would_create_athletes: int
    would_create_events: int
    duplicates: list[dict]
    conflicts: list[dict]
    issues: list[dict]
    sample_results: list[dict]
    orphan_dscore_review_count: int = 0
    orphan_dscore_review: list[dict] = []
    orphan_dscore_decision_stats: dict = {}
    athlete_match_review_count: int = 0
    athlete_match_review: list[dict] = []
    athlete_match_decision_stats: dict = {}


class GymternetImportCommit(GymternetImportPreview):
    committed: bool
    allow_partial: bool
    created_athletes: int
    created_events: int
    created_results: int
    updated_events: int
    updated_athlete_countries: int
    updated_athlete_names: int = 0
    corrected_represented_countries: int = 0
    created_complete_results: int = 0
    created_partial_results: int = 0
    orphan_dscore_review_uncommitted: int = 0
    athletes_with_new_results: int = 0
    events_with_new_results: int = 0
    created_admin_notifications: int
    skipped_duplicates: int
    skipped_conflicts: int


class GymternetImportTargetSuggestion(BaseModel):
    target_id: str
    label: str
    confidence: float
    event_name: str
    year: int
    athlete_name: str
    country: Optional[str] = None
    discipline: DisciplineEnum
    category: ResultCategoryEnum
    apparatus: str
    vt_attempt: Optional[int] = None
    day: Optional[int] = None
    format: FormatEnum
    round: RoundEnum
    score: Optional[float] = None
    D_score: Optional[float] = None
    source_sheet: str
    source_row: int


class GymternetImportTargetSuggestions(BaseModel):
    filename: str
    year_hint: Optional[int] = None
    query: Optional[str] = None
    review_id: Optional[str] = None
    total_candidates: int
    suggestions: list[GymternetImportTargetSuggestion]


class NotificationTypeEnum(str, Enum):
    NEW_EVENT = "new_event"
    NEW_RESULT = "new_result"
    IMPORT_SUMMARY = "import_summary"
    DATA_ENTRY_SUMMARY = "data_entry_summary"
    EVENT_RESULTS_REMINDER = "event_results_reminder"
    SECURITY_ALERT = "security_alert"
    ADMIN_PROMOTION = "admin_promotion"
    ADMIN_DEMOTION = "admin_demotion"


class NotificationBase(BaseModel):
    type: NotificationTypeEnum
    message: str
    is_read: bool = False
    related_event_id: Optional[int] = None
    related_athlete_id: Optional[int] = None
    related_result_id: Optional[int] = None


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationRead(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AuditLogRead(BaseModel):
    id: int
    admin_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    before_json: Optional[str] = None
    after_json: Optional[str] = None
    review_status: AuditReviewStatusEnum = AuditReviewStatusEnum.PENDING
    reviewed_by_super_admin_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_note: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AuditLogReviewDecision(BaseModel):
    note: Optional[str] = None


class SiteAnalyticsEventTypeEnum(str, Enum):
    PAGE_VIEW = "page_view"
    SEARCH = "search"
    ATHLETE_VIEW = "athlete_view"
    EVENT_VIEW = "event_view"
    DASHBOARD_VIEW = "dashboard_view"
    SESSION_END = "session_end"


def result_bonus_status(
    event_year: Optional[int],
    discipline: Optional[DisciplineEnum],
    apparatus: Optional[str],
    Bonus: Optional[float],
) -> ScoreComponentStatusEnum:
    if Bonus is not None:
        return ScoreComponentStatusEnum.AVAILABLE
    if result_bonus_is_applicable(event_year, discipline, apparatus):
        return ScoreComponentStatusEnum.NOT_AVAILABLE
    return ScoreComponentStatusEnum.NOT_APPLICABLE


def result_nullable_execution_component_status(
    event_year: Optional[int],
    value: Optional[float],
) -> ScoreComponentStatusEnum:
    if value is not None:
        return ScoreComponentStatusEnum.AVAILABLE
    return ScoreComponentStatusEnum.NOT_AVAILABLE


class SiteAnalyticsEventCreate(BaseModel):
    event_type: SiteAnalyticsEventTypeEnum
    visitor_id: Optional[str] = None
    session_id: Optional[str] = None
    path: Optional[str] = None
    search_query: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    duration_seconds: Optional[int] = None

    @model_validator(mode="after")
    def validate_event(self):
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError("duration_seconds must be greater than or equal to 0")
        if self.visitor_id is not None and len(self.visitor_id) > 100:
            raise ValueError("visitor_id must be 100 characters or fewer")
        if self.session_id is not None and len(self.session_id) > 100:
            raise ValueError("session_id must be 100 characters or fewer")
        return self


class SiteAnalyticsEventRead(BaseModel):
    id: int
    event_type: SiteAnalyticsEventTypeEnum
    visitor_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    path: Optional[str] = None
    search_query: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    duration_seconds: Optional[int] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SiteAnalyticsTopItem(BaseModel):
    id: Optional[int] = None
    label: str
    count: int


class SiteAnalyticsUserStats(BaseModel):
    registered_users: int
    verified_users: int
    unverified_users: int
    active_users: int
    inactive_users: int
    active_window_days: int


class SiteAnalyticsSummary(BaseModel):
    start_date: Date
    end_date: Date
    total_events: int
    visitors: int
    sessions: int
    page_views: int
    searches: int
    athlete_views: int
    event_views: int
    dashboard_views: int
    average_session_seconds: Optional[float] = None
    users: SiteAnalyticsUserStats
    top_searches: list[SiteAnalyticsTopItem]
    top_athletes: list[SiteAnalyticsTopItem]
    top_events: list[SiteAnalyticsTopItem]
