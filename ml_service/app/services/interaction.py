from ..repositories.interaction import InteractionRepository, get_intraction_repository
from fastapi import Depends


class InteractionService:
    def __init__(self, repo: InteractionRepository):
        self.repo = repo

    async def get_interactions(self, user_id: int):
        interactions = await self.repo.get_user_interactions(user_id)
        return interactions


def get_interaction_service(repo: InteractionRepository = Depends(get_intraction_repository)):
    return InteractionService(repo)
