"""Requêtes d'administration (lecture et actions modérées)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from ..models import (
    GiftCard,
    GiftCardStatus,
    Merchant,
    PointTransaction,
    Promotion,
    TransactionType,
    User,
    UserRole,
)
from . import merchants


def list_users(
    session: Session,
    *,
    role: UserRole | None = None,
    city: str | None = None,
    search: str | None = None,
) -> list[User]:
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    if city:
        stmt = stmt.where(User.city == city)
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                User.first_name.ilike(like),
                User.last_name.ilike(like),
                User.phone.ilike(like),
                User.email.ilike(like),
            )
        )
    return list(session.scalars(stmt.order_by(User.created_at.desc())))


def list_merchants(
    session: Session,
    *,
    city: str | None = None,
    active: bool | None = None,
    search: str | None = None,
) -> list[Merchant]:
    stmt = select(Merchant)
    if city:
        stmt = stmt.where(Merchant.city == city)
    if active is not None:
        stmt = stmt.where(Merchant.is_active.is_(active))
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Merchant.business_name.ilike(like),
                Merchant.category.ilike(like),
                Merchant.neighborhood.ilike(like),
            )
        )
    return list(session.scalars(stmt.order_by(Merchant.created_at.desc())))


def toggle_merchant(session: Session, *, merchant_id: int, active: bool, actor: User) -> Merchant:
    return merchants.set_active(session, merchant_id, active=active, actor=actor)


def list_transactions(
    session: Session,
    *,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    city: str | None = None,
    type_filter: TransactionType | None = None,
    limit: int = 500,
) -> list[PointTransaction]:
    stmt = (
        select(PointTransaction)
        .outerjoin(Merchant, PointTransaction.merchant_id == Merchant.id)
        .options(joinedload(PointTransaction.user), joinedload(PointTransaction.merchant))
        .order_by(PointTransaction.created_at.desc())
    )
    if date_from:
        stmt = stmt.where(PointTransaction.created_at >= date_from)
    if date_to:
        stmt = stmt.where(PointTransaction.created_at <= date_to)
    if city:
        stmt = stmt.where(Merchant.city == city)
    if type_filter:
        stmt = stmt.where(PointTransaction.type == type_filter)
    return list(session.scalars(stmt.limit(limit)).unique())


def list_gift_cards(
    session: Session,
    *,
    status: GiftCardStatus | None = None,
    limit: int = 500,
) -> list[GiftCard]:
    stmt = (
        select(GiftCard)
        .options(joinedload(GiftCard.sender), joinedload(GiftCard.merchant))
        .order_by(GiftCard.created_at.desc())
        .limit(limit)
    )
    if status:
        stmt = stmt.where(GiftCard.status == status)
    return list(session.scalars(stmt).unique())


def list_promotions(
    session: Session,
    *,
    city: str | None = None,
    active: bool | None = None,
    limit: int = 500,
) -> list[Promotion]:
    stmt = select(Promotion).options(joinedload(Promotion.merchant)).order_by(Promotion.created_at.desc()).limit(limit)
    if city:
        stmt = stmt.where(Promotion.city == city)
    if active is not None:
        stmt = stmt.where(Promotion.is_active.is_(active))
    return list(session.scalars(stmt).unique())
