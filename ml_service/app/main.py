from fastapi import FastAPI, status, HTTPException
from .api import recommendation

app = FastAPI()
app.include_router(recommendation.router, tags=["recommendation"])
