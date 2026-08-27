from sqlalchemy import text


class RecommendationRepository:

    def __init__(self, session):
        self.session = session

    async def get_user(self, user_id):
        result = await self.session.execute(
            text("""
                 SELECT id,
                        created
                 FROM account_filmbazuser
                 WHERE id = :id
                 """
                 ),
            {
                "id": user_id
            }
        )

        return result.mappings().first()

    async def get_interactions(self, user_id):
        result = await self.session.execute(
            text("""
                 SELECT movie_id,
                        interaction_type,
                        weight, timestamp
                 FROM interactions
                 WHERE user_id=:user_id
                 """),
            {
                "user_id": user_id
            }
        )

        return result.mappings().all()

    async def get_favorite_genres(self, user_id):
        result = await self.session.execute(
            text("""
                 SELECT genre_id
                 FROM account_user_favorite_genres
                 WHERE user_id = :user_id
                 """),
            {
                "user_id": user_id
            }
        )

        return result.scalars().all()

    async def get_movie_crews(self, movie_ids):
        result = await self.session.execute(
            text("""
                 SELECT movie_id,
                        crew_id,
                        role
                 FROM people_moviecrew
                 WHERE movie_id = ANY (:movie_ids)
                 """),
            {
                "movie_ids": movie_ids
            }
        )

        return result.mappings().all()
