import asyncio
from ..preprocessing.pipeline import get_processed_dataset
from ..services.raw_data import raw_data, RawData
from fastapi import Depends, Request
import pandas as pd
from ..training.trainer import dataframe_to_inputs


class RecommenderMovies:
    """
    Service used for call the recommender model.
    """

    def __init__(self, request: Request, service: RawData):
        """
        init method used for creating the variables.
        """
        self.model = request.app.state.recommender_model
        self.pipeline = get_processed_dataset
        self.service = service

    async def predict(self, user_id: int, movie_ids: list[int]) -> list[tuple]:
        """
        method used for mulitple works.
        steps: 1 get raw data 2 change type to dataframe 3 cleaning data
        4 change data to input of tensorflow recommendation model
        5 call the recommender model 6 return recommendation movies

        """
        data = await self.service.get_raw_data(user_id, movie_ids)  # step 1

        df = pd.DataFrame(data)  # step 2

        cleaned_data = self.pipeline(df)  # setp 3

        inputs = dataframe_to_inputs(cleaned_data)  # step 4

        scores = await asyncio.to_thread(
            self.model.predict,
            inputs
        )  # step 5

        return [
            (int(movie_id), float(format(float(score[0]), ".2f")))
            for movie_id, score in zip(movie_ids, scores)
        ]  # step 6


def get_recommender(request: Request, service: RawData = Depends(raw_data)):
    """
    function used for rutern RecommenderMovies instance.
    """
    return RecommenderMovies(request, service)
