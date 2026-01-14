from typing import List

from fastapi import FastAPI
from openai import BaseModel

from app.interfaces.schemas.base import Response

app = FastAPI()


class User(BaseModel):
    id: int
    name: str


db_users = {
    1: User(id=1, name="Alice"),
    2: User(id=2, name="Bob"),
}


@app.get("/user/{user_id}", response_model=Response[User])
async def get_user(user_id: int):
    """根据用户ID获取用户信息"""
    user = db_users.get(user_id)
    if not user:
        return Response.fail(code=400, msg="用户不存在")
    return Response.success(user)

@app.get(("/users"), response_model=Response[List[User]])
async def get_all_users():
    """获取所有用户信息"""
    users = list(db_users.values())
    return Response.success(data=users)
