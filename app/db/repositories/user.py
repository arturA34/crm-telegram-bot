from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language: str = "en",
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language=language,
        )
        self._session.add(user)
        await self._session.flush()
        return user

    async def update_language(self, user: User, language: str) -> User:
        user.language = language
        await self._session.flush()
        return user

    async def update_role(self, user: User, role: str) -> User:
        user.role = role
        await self._session.flush()
        return user

    async def update_team(self, user: User, team_id: int | None) -> User:
        user.team_id = team_id
        await self._session.flush()
        return user

    async def get_team_members(self, team_id: int) -> list[User]:
        stmt = select(User).where(User.team_id == team_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def remove_from_team(self, user: User) -> User:
        user.team_id = None
        user.role = "SOLO"
        await self._session.flush()
        return user
