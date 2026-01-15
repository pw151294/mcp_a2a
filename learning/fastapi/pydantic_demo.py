import json
from typing import Optional

from fastapi import FastAPI, Query, Path
from pydantic import BaseModel
from pydantic.v1 import Field
from dataclasses import dataclass

app = FastAPI()

class Item(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="商品名称，长度在3到50之间")
    price: float = Field(..., gt=0, description="商品价格，必须大于0")
    in_stock: bool


@app.post("/user/{user_id}/items")
async def create_item(
        user_id: int = Path(..., ge=1, description="用户ID，必须大于等于1"),
        q: Optional[str] = Query(None, max_length=100, description="查询字符串，最大长度为100"),
        item: Item = ...,
):
    return {"user_id": user_id, "q": q, "item": item}

class UserInfo(BaseModel):
    username: str
    password: str
    email: str

@dataclass() # 如果不添加dataclass装饰器，则User类不会自动生成__init__等方法
class User:
    username: str
    password: str
    email: str

if __name__ == '__main__':
    user = UserInfo(username="test", password="123456", email="")
    # model_dump()将模型转换为python字典
    user_dict = user.model_dump()
    print(user_dict)
    # model_dump_json()将模型转换为json字符串
    user_json = user.model_dump_json()
    print(user_json)
    # model_validate_json将json字符串直接转换为模型
    user_from_json = UserInfo.model_validate_json(user_json)
    print(user_from_json)
    # model_validate将python字典直接转换为模型
    user_from_dict = UserInfo.model_validate(user_dict)
    print(user_from_dict)
    # model_json_schema 生成模型的JSON Schema
    print(UserInfo.model_json_schema(True))
    print(UserInfo.model_json_schema(False))
    # model_copy 复制模型实例，可以修改部分字段的值
    print(UserInfo.model_copy(user_from_dict))

    # json.loads()将json字符串转换为python字典
    # json.dumps()将python字典转换为json字符串
    user_data = json.loads(user_json)
    user_obj = User(username=user_data["username"], password=user_data["password"], email=user_data["email"])
    print(json.dumps(user_data))
