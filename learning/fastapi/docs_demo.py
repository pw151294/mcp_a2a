# 定义分组元数据
from typing import List

from fastapi import FastAPI, APIRouter
from learning.fastapi.pydantic_demo import BaseModel

tags_metadata = [
    {
        "name": "用户管理",
        "description": "与用户相关的操作，如创建、更新和删除用户。",
    },
    {
        "name": "订单管理",
        "description": "处理订单的创建、更新和查询。",
        "externalDocs": {
            "description": "订单管理文档",
            "url": "https://example.com/docs/orders",
        }
    }
]

# 初始化FastAPI
app = FastAPI(
    title="我的API文档",
    description="这是一个包含用户管理还有订单管理功能的API文档",
    version="1.0.0",
    openapi_tags=tags_metadata
)


class User(BaseModel):
    id: int
    name: str


class Order(BaseModel):
    id: int
    item: str
    price: float


# 用户相关路由
user_router = APIRouter(prefix="/user", tags=["用户相关"])

@user_router.get("/",response_model=List[User], summary="获取用户列表",description="获取所有用户的信息")
async def get_users():
    return [User(id=1, name="Alice"), User(id=2, name="Bob")]

@user_router.post("/", response_model=User, summary="创建用户", description="创建一个新的用户")
async def create_user(user: User):
    return user

# 订单相关的路由
order_router = APIRouter(prefix="/order", tags=["订单相关"])

@order_router.get("/",response_model=List[Order], summary="获取订单列表",description="获取所有订单的信息")
async def get_orders():
    return [Order(id=1, item="Laptop", price=999.99), Order(id=2, item="Phone", price=499.99)]

@order_router.post("/", response_model=Order, summary="创建订单", description="创建一个新的订单")
async def create_order(order: Order):
    return order

# 注册路由
app.include_router(user_router)
app.include_router(order_router)