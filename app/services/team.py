import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.db.models.user import User
from app.db.repositories.team import TeamRepository
from app.db.repositories.user import UserRepository


class TeamService:
    def __init__(self, session: AsyncSession) -> None:
        self._team_repo = TeamRepository(session)
        self._user_repo = UserRepository(session)

    async def create_team(self, user: User, name: str) -> dict:
        if user.team_id is not None:
            return {"ok": False, "error": "team_already_in"}

        invite_code = secrets.token_urlsafe(8)
        team = await self._team_repo.create(
            name=name,
            owner_id=user.telegram_id,
            invite_code=invite_code,
        )
        await self._user_repo.update_team(user, team.id)
        await self._user_repo.update_role(user, UserRole.OWNER)

        return {"ok": True, "team": team}

    async def join_team(self, user: User, invite_code: str) -> dict:
        if user.team_id is not None:
            return {"ok": False, "error": "team_already_in"}

        team = await self._team_repo.get_by_invite_code(invite_code)
        if team is None:
            return {"ok": False, "error": "team_invalid_code"}

        await self._user_repo.update_team(user, team.id)
        await self._user_repo.update_role(user, UserRole.MANAGER)

        return {"ok": True, "team": team}

    async def leave_team(self, user: User) -> dict:
        if user.team_id is None:
            return {"ok": False, "error": "team_not_in"}

        if user.role == UserRole.OWNER:
            return {"ok": False, "error": "team_owner_cant_leave"}

        await self._user_repo.remove_from_team(user)
        return {"ok": True}

    async def remove_member(self, owner: User, member_id: int) -> dict:
        if owner.role != UserRole.OWNER:
            return {"ok": False, "error": "client_access_denied"}

        member = await self._user_repo.get_by_id(member_id)
        if member is None or member.team_id != owner.team_id:
            return {"ok": False, "error": "team_member_not_found"}

        await self._user_repo.remove_from_team(member)
        return {"ok": True}

    async def get_members(self, user: User) -> dict:
        if user.team_id is None:
            return {"ok": False, "error": "team_not_in"}

        members = await self._user_repo.get_team_members(user.team_id)
        return {"ok": True, "members": members}

    async def get_team_info(self, user: User) -> dict:
        if user.team_id is None:
            return {"ok": False, "error": "team_not_in"}

        team = await self._team_repo.get_by_id(user.team_id)
        members = await self._user_repo.get_team_members(user.team_id)
        return {"ok": True, "team": team, "members": members, "count": len(members)}
