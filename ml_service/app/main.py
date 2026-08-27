from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel

app = FastAPI()


class UserIn(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    username: str
    email: str


@app.post("/home/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def index(user: UserIn):
    if user.username in ["admin", "Admin", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username can't be 'admin' .",
            headers={"X-Error": "UsernameError"}, )

    return user
