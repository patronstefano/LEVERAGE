from datetime import datetime
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class DisciplineEnum(str, enum.Enum):
    MAG = "MAG"
    WAG = "WAG"


class EventDisciplineEnum(str, enum.Enum):
    MAG = "MAG"
    WAG = "WAG"
    MAG_AND_WAG = "MAG and WAG"


class EventCategoryEnum(str, enum.Enum):
    JUNIOR = "junior"
    SENIOR = "senior"
    JUNIOR_AND_SENIOR = "junior and senior"


class ResultCategoryEnum(str, enum.Enum):
    JUNIOR = "junior"
    SENIOR = "senior"


CategoryEnum = EventCategoryEnum


class LevelEnum(str, enum.Enum):
    OLYMPIC_GAMES = "Olympic Games"
    WORLD_CHAMPIONSHIPS = "World Championships"
    CONTINENTAL_CHAMPIONSHIPS = "Continental Championships"
    WORLD_CUP = "World Cup"
    WORLD_CHALLENGE_CUP = "World Challenge Cup"
    INTERNATIONAL_EVENT = "International Event"
    NATIONAL_EVENT = "National Event"


class ApparatusMAGEnum(str, enum.Enum):
    FX = "FX"  # Floor Exercise
    PH = "PH"  # Pommel Horse
    SR = "SR"  # Still Rings
    VT = "VT"  # Vault
    PB = "PB"  # Parallel Bars
    HB = "HB"  # High Bar
    AA = "AA"  # All-Around
    VT_AVG = "VT AVG"  # Vault Average


class ApparatusWAGEnum(str, enum.Enum):
    VT = "VT"  # Vault
    UB = "UB"  # Uneven Bars
    BB = "BB"  # Balance Beam
    FX = "FX"  # Floor Exercise
    AA = "AA"  # All-Around
    VT_AVG = "VT AVG"  # Vault Average


class FormatEnum(str, enum.Enum):
    TEAM = "team"
    INDIVIDUAL = "individual"
    APPARATUS = "apparatus"


class RoundEnum(str, enum.Enum):
    QUALIFICATION = "qualification"
    FINAL = "final"


class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"


class LanguageEnum(str, enum.Enum):
    EN = "en"
    IT = "it"
    ES = "es"
    FR = "fr"


class SiteAnalyticsEventTypeEnum(str, enum.Enum):
    PAGE_VIEW = "page_view"
    SEARCH = "search"
    ATHLETE_VIEW = "athlete_view"
    EVENT_VIEW = "event_view"
    DASHBOARD_VIEW = "dashboard_view"
    SESSION_END = "session_end"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    email_verification_token_hash = Column(String(64), nullable=True, index=True)
    email_verification_expires_at = Column(DateTime, nullable=True)
    email_verification_sent_at = Column(DateTime, nullable=True)
    password_reset_token_hash = Column(String(64), nullable=True, index=True)
    password_reset_expires_at = Column(DateTime, nullable=True)
    password_reset_sent_at = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    login_locked_until = Column(DateTime, nullable=True)
    auth_version = Column(Integer, default=1, nullable=False)
    mfa_secret = Column(String(64), nullable=True)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_recovery_codes = Column(Text, nullable=True)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.USER, nullable=False)
    preferred_language = Column(SQLEnum(LanguageEnum), default=LanguageEnum.EN, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    followed_athletes = relationship("FollowedAthlete", back_populates="user", cascade="all, delete-orphan")
    saved_events = relationship("SavedEvent", back_populates="user", cascade="all, delete-orphan")
    saved_dashboard_views = relationship(
        "SavedDashboardView",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="SavedDashboardView.position, SavedDashboardView.created_at.desc()",
    )


class Athlete(Base):
    __tablename__ = "athletes"
    __table_args__ = (
        CheckConstraint("birth_year IS NULL OR (birth_year >= 1900 AND birth_year <= 2100)", name="ck_athletes_birth_year_valid"),
        Index("ix_athletes_lookup", "is_deleted", "last_name", "first_name"),
        Index("ix_athletes_country_discipline", "is_deleted", "country", "discipline"),
    )

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_year = Column(Integer, nullable=True)
    country = Column(String(100), nullable=True)
    discipline = Column(SQLEnum(DisciplineEnum), nullable=False)
    image_url = Column(String(255), nullable=True)
    world_gymnastics_athlete_id = Column(String(50), nullable=True)
    world_gymnastics_profile_url = Column(String(500), nullable=True)
    world_gymnastics_status = Column(String(100), nullable=True)
    world_gymnastics_verified_at = Column(DateTime, nullable=True)
    world_gymnastics_verified_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("Result", back_populates="athlete", cascade="all, delete-orphan")
    world_gymnastics_verified_by_admin = relationship("User", foreign_keys=[world_gymnastics_verified_by_admin_id])
    deleted_by_admin = relationship("User", foreign_keys=[deleted_by_admin_id])
    country_changes = relationship(
        "AthleteCountryChange",
        back_populates="athlete",
        cascade="all, delete-orphan",
        order_by="AthleteCountryChange.change_year",
    )


class AthleteCountryChange(Base):
    __tablename__ = "athlete_country_changes"
    __table_args__ = (
        CheckConstraint("change_year >= 1900 AND change_year <= 2100", name="ck_athlete_country_changes_year_valid"),
        UniqueConstraint(
            "athlete_id",
            "from_country",
            "to_country",
            "change_year",
            name="uq_athlete_country_change",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True)
    from_country = Column(String(100), nullable=True)
    to_country = Column(String(100), nullable=False)
    change_year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    athlete = relationship("Athlete", back_populates="country_changes")


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_calendar", "is_deleted", "start_date", "year"),
        Index("ix_events_year_level", "is_deleted", "year", "level"),
        Index("ix_events_domain", "is_deleted", "discipline", "category", "level"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    venue = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    year = Column(Integer, nullable=False)
    discipline = Column(SQLEnum(EventDisciplineEnum), nullable=False)
    category = Column(SQLEnum(EventCategoryEnum), nullable=False)
    level = Column(SQLEnum(LevelEnum), nullable=False)
    image_url = Column(String(255), nullable=True)
    world_gymnastics_event_id = Column(String(50), nullable=True)
    world_gymnastics_event_url = Column(String(500), nullable=True)
    world_gymnastics_status = Column(String(100), nullable=True)
    world_gymnastics_verified_at = Column(DateTime, nullable=True)
    world_gymnastics_verified_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("Result", back_populates="event", cascade="all, delete-orphan")
    world_gymnastics_verified_by_admin = relationship("User", foreign_keys=[world_gymnastics_verified_by_admin_id])
    deleted_by_admin = relationship("User", foreign_keys=[deleted_by_admin_id])


class Result(Base):
    __tablename__ = "results"
    __table_args__ = (
        CheckConstraint("score IS NULL OR score >= 0", name="ck_results_score_non_negative"),
        CheckConstraint("D_score IS NULL OR D_score >= 0", name="ck_results_d_score_non_negative"),
        CheckConstraint("E_score IS NULL OR E_score >= 0", name="ck_results_e_score_non_negative"),
        CheckConstraint("Penalty IS NULL OR Penalty >= 0", name="ck_results_penalty_non_negative"),
        CheckConstraint("Bonus IS NULL OR Bonus >= 0", name="ck_results_bonus_non_negative"),
        CheckConstraint("vt_attempt IS NULL OR vt_attempt IN (1, 2)", name="ck_results_vt_attempt_valid"),
        CheckConstraint("day IS NULL OR day >= 1", name="ck_results_day_positive"),
        Index("ix_results_event_rank_scope", "event_id", "is_deleted", "format", "round", "discipline", "category", "apparatus", "day"),
        Index("ix_results_event_metric", "event_id", "is_deleted", "rank", "score", "D_score"),
        Index("ix_results_athlete_event_scope", "athlete_id", "event_id", "is_deleted"),
        Index("ix_results_athlete_timeline", "athlete_id", "is_deleted", "apparatus", "format", "round", "day"),
        Index("ix_results_duplicate_lookup", "athlete_id", "event_id", "apparatus", "vt_attempt", "day", "format", "round", "discipline", "category", "is_deleted"),
        Index("ix_results_country_scope", "represented_country", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    represented_country = Column(String(100), nullable=True, index=True)
    discipline = Column(SQLEnum(DisciplineEnum), nullable=False)
    category = Column(SQLEnum(ResultCategoryEnum), nullable=False)
    apparatus = Column(String(50), nullable=True)
    vt_attempt = Column(Integer, nullable=True)
    day = Column(Integer, nullable=True)
    format = Column(SQLEnum(FormatEnum), nullable=False)
    round = Column(SQLEnum(RoundEnum), nullable=False)
    D_score = Column(Float, nullable=True)
    E_score = Column(Float, nullable=True)
    Penalty = Column(Float, nullable=True)
    Bonus = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)
    vault_attempt_order_uncertain = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    athlete = relationship("Athlete", back_populates="results")
    event = relationship("Event", back_populates="results")
    deleted_by_admin = relationship("User", foreign_keys=[deleted_by_admin_id])

    @property
    def bonus_status(self) -> str:
        if self.Bonus is not None:
            return "available"
        event_year = self.event.year if self.event else None
        if event_year is None or event_year < 2025:
            return "not_applicable"
        if self.discipline == DisciplineEnum.WAG and self.apparatus == "VT AVG":
            return "not_available"
        if self.discipline == DisciplineEnum.MAG and self.apparatus in {"FX", "SR", "VT", "PB", "HB"}:
            return "not_available"
        return "not_applicable"

    @property
    def e_score_status(self) -> str:
        if self.E_score is not None:
            return "available"
        return "not_available"

    @property
    def penalty_status(self) -> str:
        if self.Penalty is not None:
            return "available"
        return "not_available"


class FollowedAthlete(Base):
    __tablename__ = "followed_athletes"
    __table_args__ = (
        UniqueConstraint("user_id", "athlete_id", name="uq_followed_athletes_user_athlete"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="followed_athletes")
    athlete = relationship("Athlete")


class SavedEvent(Base):
    __tablename__ = "saved_events"
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_saved_events_user_event"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_events")
    event = relationship("Event")


class SavedDashboardView(Base):
    __tablename__ = "saved_dashboard_views"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_saved_dashboard_views_user_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    view_type = Column(String(50), nullable=False)
    chart_type = Column(String(50), nullable=True)
    metric = Column(String(20), nullable=True)
    filters_json = Column(Text, nullable=False, default="{}")
    is_default = Column(Boolean, default=False, nullable=False)
    position = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="saved_dashboard_views")


class SiteAnalyticsEvent(Base):
    __tablename__ = "site_analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(SQLEnum(SiteAnalyticsEventTypeEnum), nullable=False, index=True)
    visitor_id = Column(String(100), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    path = Column(String(500), nullable=True)
    search_query = Column(String(255), nullable=True)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User")


class ResultEntryContext(Base):
    __tablename__ = "result_entry_contexts"
    __table_args__ = (
        UniqueConstraint("event_id", "admin_id", name="uq_result_entry_context_event_admin"),
        CheckConstraint("day IS NULL OR day >= 1", name="ck_result_entry_contexts_day_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    apparatus = Column(String(50), nullable=True)
    day = Column(Integer, nullable=True)
    format = Column(SQLEnum(FormatEnum), nullable=True)
    round = Column(SQLEnum(RoundEnum), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    event = relationship("Event")
    admin = relationship("User")


class NotificationTypeEnum(str, enum.Enum):
    NEW_EVENT = "new_event"
    NEW_RESULT = "new_result"
    IMPORT_SUMMARY = "import_summary"
    DATA_ENTRY_SUMMARY = "data_entry_summary"
    EVENT_RESULTS_REMINDER = "event_results_reminder"
    SECURITY_ALERT = "security_alert"
    ADMIN_PROMOTION = "admin_promotion"
    ADMIN_DEMOTION = "admin_demotion"


class DataSuggestionEntityTypeEnum(str, enum.Enum):
    ATHLETE = "athlete"
    EVENT = "event"


class DataSuggestionStatusEnum(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EDITED = "edited"
    REJECTED = "rejected"


class DataSuggestion(Base):
    __tablename__ = "data_suggestions"
    __table_args__ = (
        CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="ck_data_suggestions_confidence_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(SQLEnum(DataSuggestionEntityTypeEnum), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    field_name = Column(String(100), nullable=False, index=True)
    suggested_value = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    source_url = Column(String(500), nullable=True)
    source_title = Column(String(255), nullable=True)
    evidence = Column(Text, nullable=True)
    status = Column(SQLEnum(DataSuggestionStatusEnum), default=DataSuggestionStatusEnum.PENDING, nullable=False, index=True)
    reviewed_value = Column(Text, nullable=True)
    created_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    created_by_admin = relationship("User", foreign_keys=[created_by_admin_id])
    reviewed_by_admin = relationship("User", foreign_keys=[reviewed_by_admin_id])


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SQLEnum(NotificationTypeEnum), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    related_event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    related_athlete_id = Column(Integer, ForeignKey("athletes.id", ondelete="SET NULL"), nullable=True)
    related_result_id = Column(Integer, ForeignKey("results.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    related_event = relationship("Event")
    related_athlete = relationship("Athlete")
    related_result = relationship("Result")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    before_json = Column(Text, nullable=True)
    after_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    admin = relationship("User")
