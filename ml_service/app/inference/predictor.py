import asyncio
from ..preprocessing.pipeline import get_processed_dataset
from ..services.raw_data import raw_data, RawData
from fastapi import Depends, Request
import pandas as pd
from ..training.trainer import dataframe_to_inputs



class RecommenderMovies:
    def __init__(self, request: Request, service: RawData):
        self.model = request.app.state.recommender_model
        self.pipeline = get_processed_dataset
        self.service = service

    async def predict(self, user_id: int, movie_ids: list[int]):
        data = await self.service.get_raw_data(user_id, movie_ids)

        df = pd.DataFrame(data)

        cleaned_data = self.pipeline(df)

        inputs = dataframe_to_inputs(cleaned_data)

        scores = await asyncio.to_thread(
            self.model.predict,
            inputs
        )

        return scores.tolist()


def get_recommender(request: Request, service: RawData = Depends(raw_data)):
    return RecommenderMovies(request, service)
