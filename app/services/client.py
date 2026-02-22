from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ClientStatus, UserRole
from app.db.models.user import User
from app.db.repositories.client import ClientRepository

PAGE_SIZE = 5


class ClientService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ClientRepository(session)

    async def create_client(self, user: User, data: dict) -> dict:
        client = await self._repo.create(
            name=data["name"],
            manager_id=user.id,
            team_id=user.team_id,
            phone=data.get("phone"),
            source=data.get("source"),
            budget=Decimal(str(data.get("budget", 0))),
        )
        return {"ok": True, "client": client}

    def _can_access(self, user: User, client) -> bool:
        if client.manager_id == user.id:
            return True
        if user.role == UserRole.OWNER and client.team_id == user.team_id:
            return True
        return False

    async def get_client_detail(self, user: User, client_id: int) -> dict:
        client = await self._repo.get_by_id(client_id)
        if client is None:
            return {"ok": False, "error": "client_not_found"}
        if not self._can_access(user, client):
            return {"ok": False, "error": "client_access_denied"}
        return {"ok": True, "client": client}

    async def update_client(self, user: User, client_id: int, data: dict) -> dict:
        client = await self._repo.get_by_id(client_id)
        if client is None:
            return {"ok": False, "error": "client_not_found"}
        if not self._can_access(user, client):
            return {"ok": False, "error": "client_access_denied"}

        await self._repo.update(client, **data)
        return {"ok": True, "client": client}

    async def change_status(self, user: User, client_id: int, status: str) -> dict:
        client = await self._repo.get_by_id(client_id)
        if client is None:
            return {"ok": False, "error": "client_not_found"}
        if not self._can_access(user, client):
            return {"ok": False, "error": "client_access_denied"}

        await self._repo.update(client, status=status)
        return {"ok": True, "client": client}

    async def delete_client(self, user: User, client_id: int) -> dict:
        client = await self._repo.get_by_id(client_id)
        if client is None:
            return {"ok": False, "error": "client_not_found"}
        if not self._can_access(user, client):
            return {"ok": False, "error": "client_access_denied"}

        await self._repo.delete(client)
        return {"ok": True}

    async def get_clients(
        self, user: User, status: str | None = None, page: int = 1
    ) -> dict:
        offset = (page - 1) * PAGE_SIZE

        if user.role == UserRole.OWNER and user.team_id is not None:
            clients = await self._repo.get_clients_for_user(
                team_id=user.team_id, status=status, offset=offset, limit=PAGE_SIZE
            )
            total = await self._repo.count_clients_for_user(
                team_id=user.team_id, status=status
            )
        else:
            clients = await self._repo.get_clients_for_user(
                manager_id=user.id, status=status, offset=offset, limit=PAGE_SIZE
            )
            total = await self._repo.count_clients_for_user(
                manager_id=user.id, status=status
            )

        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        return {
            "ok": True,
            "clients": clients,
            "page": page,
            "total_pages": total_pages,
            "total": total,
        }

    async def get_pipeline(self, user: User) -> dict:
        if user.role == UserRole.OWNER and user.team_id is not None:
            counts = await self._repo.get_status_counts(team_id=user.team_id)
        else:
            counts = await self._repo.get_status_counts(manager_id=user.id)

        pipeline = {s.value: counts.get(s.value, 0) for s in ClientStatus}
        return {"ok": True, "pipeline": pipeline}

    async def set_reminder(self, user: User, client_id: int, reminder_at) -> dict:
        client = await self._repo.get_by_id(client_id)
        if client is None:
            return {"ok": False, "error": "client_not_found"}
        if not self._can_access(user, client):
            return {"ok": False, "error": "client_access_denied"}

        await self._repo.update(client, reminder_at=reminder_at)
        return {"ok": True, "client": client}
