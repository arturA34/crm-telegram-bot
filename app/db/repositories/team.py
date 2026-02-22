from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.team import Team


class TeamRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, name: str, owner_id: int, invite_code: str) -> Team:
        team = Team(name=name, owner_id=owner_id, invite_code=invite_code)
        self._session.add(team)
        await self._session.flush()
        return team

    async def get_by_id(self, team_id: int) -> Team | None:
        stmt = select(Team).where(Team.id == team_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_invite_code(self, invite_code: str) -> Team | None:
        stmt = select(Team).where(Team.invite_code == invite_code)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_owner_id(self, owner_id: int) -> Team | None:
        stmt = select(Team).where(Team.owner_id == owner_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, team: Team) -> None:
        await self._session.delete(team)
        await self._session.flush()
