from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.repositories.client import ClientRepository
from app.db.repositories.user import UserRepository


class StatsService:
    def __init__(self, session: AsyncSession) -> None:
        self._client_repo = ClientRepository(session)
        self._user_repo = UserRepository(session)

    async def get_personal_stats(self, user: User) -> dict:
        stats = await self._client_repo.get_user_stats(user.id)
        return {"ok": True, **stats}

    async def get_leaderboard(self, user: User) -> dict:
        if user.team_id is None:
            return {"ok": False, "error": "leaderboard_no_team"}

        raw_stats = await self._client_repo.get_team_stats(user.team_id)
        members = await self._user_repo.get_team_members(user.team_id)
        member_map = {m.id: m for m in members}

        leaderboard = []
        for row in raw_stats:
            total = row["total"]
            won = row["won"]
            revenue = float(row["revenue"])
            conversion = (won / total * 100) if total > 0 else 0.0

            score = revenue * 0.4 + won * 100 * 0.3 + conversion * 10 * 0.3
            member = member_map.get(row["manager_id"])
            name = member.first_name or member.username or str(member.telegram_id) if member else "Unknown"

            leaderboard.append({
                "name": name,
                "score": round(score, 1),
                "won": won,
                "revenue": revenue,
            })

        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        return {"ok": True, "leaderboard": leaderboard}
