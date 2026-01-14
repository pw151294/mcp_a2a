from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/apps/{app_id}")
async def make_coffee(app_id: str, q: Union[str, None] = None):
    return {"app_id": app_id, "q": q}
