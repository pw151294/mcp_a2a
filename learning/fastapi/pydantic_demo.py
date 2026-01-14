from typing import Optional

from fastapi import FastAPI, Query, Path
from pydantic import BaseModel
from pydantic.v1 import Field

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
