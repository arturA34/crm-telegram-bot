from datetime import datetime
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.client import Client


class ClientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        name: str,
        manager_id: int,
        team_id: int | None = None,
        phone: str | None = None,
        source: str | None = None,
        budget: Decimal = Decimal("0"),
    ) -> Client:
        client = Client(
            name=name,
            manager_id=manager_id,
            team_id=team_id,
            phone=phone,
            source=source,
            budget=budget,
        )
        self._session.add(client)
        await self._session.flush()
        return client

    async def get_by_id(self, client_id: int) -> Client | None:
        stmt = select(Client).where(Client.id == client_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_clients_for_user(
        self,
        manager_id: int | None = None,
        team_id: int | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[Client]:
        stmt = select(Client)

        if manager_id is not None:
            stmt = stmt.where(Client.manager_id == manager_id)
        if team_id is not None:
            stmt = stmt.where(Client.team_id == team_id)
        if status is not None:
            stmt = stmt.where(Client.status == status)

        stmt = stmt.order_by(Client.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_clients_for_user(
        self,
        manager_id: int | None = None,
        team_id: int | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(Client.id))

        if manager_id is not None:
            stmt = stmt.where(Client.manager_id == manager_id)
        if team_id is not None:
            stmt = stmt.where(Client.team_id == team_id)
        if status is not None:
            stmt = stmt.where(Client.status == status)

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_status_counts(
        self,
        manager_id: int | None = None,
        team_id: int | None = None,
    ) -> dict[str, int]:
        stmt = select(Client.status, func.count(Client.id))

        if manager_id is not None:
            stmt = stmt.where(Client.manager_id == manager_id)
        if team_id is not None:
            stmt = stmt.where(Client.team_id == team_id)

        stmt = stmt.group_by(Client.status)
        result = await self._session.execute(stmt)
        return dict(result.all())

    async def update(self, client: Client, **fields: object) -> Client:
        for key, value in fields.items():
            setattr(client, key, value)
        await self._session.flush()
        return client

    async def delete(self, client: Client) -> None:
        await self._session.delete(client)
        await self._session.flush()

    async def get_due_reminders(self, now: datetime) -> list[Client]:
        stmt = (
            select(Client)
            .where(Client.reminder_at.isnot(None))
            .where(Client.reminder_at <= now)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_stats(self, manager_id: int) -> dict:
        total = await self.count_clients_for_user(manager_id=manager_id)
        counts = await self.get_status_counts(manager_id=manager_id)

        revenue_stmt = (
            select(func.coalesce(func.sum(Client.budget), 0))
            .where(Client.manager_id == manager_id)
            .where(Client.status == "WON")
        )
        result = await self._session.execute(revenue_stmt)
        revenue = result.scalar_one()

        won = counts.get("WON", 0)
        lost = counts.get("LOST", 0)
        in_progress = total - won - lost

        conversion = round(won / total * 100, 1) if total > 0 else 0.0

        return {
            "total": total,
            "won": won,
            "lost": lost,
            "in_progress": in_progress,
            "revenue": revenue,
            "conversion": conversion,
        }

    async def get_team_stats(self, team_id: int) -> list[dict]:
        stmt = (
            select(
                Client.manager_id,
                func.count(Client.id).label("total"),
                func.coalesce(
                    func.sum(case((Client.status == "WON", 1), else_=0)), 0
                ).label("won"),
                func.coalesce(
                    func.sum(
                        case((Client.status == "WON", Client.budget), else_=0)
                    ),
                    0,
                ).label("revenue"),
            )
            .where(Client.team_id == team_id)
            .group_by(Client.manager_id)
        )
        result = await self._session.execute(stmt)
        return [dict(row._mapping) for row in result.all()]
