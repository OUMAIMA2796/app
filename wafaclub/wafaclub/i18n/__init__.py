"""Internationalisation : français et arabe (RTL)."""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

TRANSLATIONS_DIR = Path(__file__).resolve().parent
SUPPORTED_LANGUAGES = ("fr", "ar")
DEFAULT_LANGUAGE = "fr"
RTL_LANGUAGES = {"ar"}


@lru_cache(maxsize=8)
def _load(language: str) -> dict[str, str]:
    path = TRANSLATIONS_DIR / f"{language}.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def normalize_language(language: str | None) -> str:
    return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs: object) -> str:
    """Traduit une clé avec repli français puis affichage de la clé (jamais d'erreur)."""
    language = normalize_language(lang)
    value = _load(language).get(key)
    if value is None:
        value = _load(DEFAULT_LANGUAGE).get(key, key)
    if kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return value
    return value


def has_translation(key: str, lang: str) -> bool:
    return key in _load(normalize_language(lang))


def is_rtl(lang: str) -> bool:
    return normalize_language(lang) in RTL_LANGUAGES


def language_label(lang: str) -> str:
    return {
        "fr": "Français",
        "ar": "العربية",
    }.get(normalize_language(lang), "Français")


def _group_number(value: Decimal, lang: str) -> str:
    if lang == "ar":
        return f"{value:,.2f}"
    return f"{value:,.2f}".replace(",", "\u202f").replace(".", ",")


def format_mad(amount: Decimal | float | int | str, lang: str = DEFAULT_LANGUAGE) -> str:
    try:
        value = Decimal(str(amount))
    except Exception:
        value = Decimal("0")
    return f"{_group_number(value, normalize_language(lang))} MAD"


def format_points(points: int, lang: str = DEFAULT_LANGUAGE) -> str:
    if normalize_language(lang) == "ar":
        return f"{int(points):,}".replace(",", "،")
    return f"{int(points):,}".replace(",", "\u202f")


def format_date(value: date | datetime | None, lang: str = DEFAULT_LANGUAGE) -> str:
    if not value:
        return "—"
    return value.strftime("%d/%m/%Y")


def format_datetime(value: datetime | None, lang: str = DEFAULT_LANGUAGE) -> str:
    if not value:
        return "—"
    return value.strftime("%d/%m/%Y · %H:%M")


def status_key(status: object) -> str:
    value = getattr(status, "value", status)
    return f"status.{str(value).upper()}"


def transaction_type_key(transaction_type: object) -> str:
    value = getattr(transaction_type, "value", transaction_type)
    return f"transaction.{str(value).upper()}"


def reward_type_key(reward_type: object) -> str:
    value = getattr(reward_type, "value", reward_type)
    return f"reward_type.{str(value).upper()}"
