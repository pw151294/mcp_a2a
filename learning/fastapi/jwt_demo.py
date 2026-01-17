import datetime
import logging
from datetime import timedelta, datetime
from typing import Optional

from fastapi import HTTPException, Depends, FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import api_jwt
from jwt.exceptions import JWTDecodeError

SECURITY_KEY = "123456789abcdef"
ALGORITHM = "HS256"
security = HTTPBearer()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fastapi.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(prefix="/api/v1/jwt", tags=["JWT演示"])


def create_jwt_token(data: dict, expires_delta: timedelta = None):
    """创建jwt令牌"""
    data_dict = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(hours=24)
    data_dict.update({"exp": expire})
    encoded_jwt = api_jwt.encode(data_dict, SECURITY_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str):
    """验证jwt令牌"""
    try:
        payload = api_jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTDecodeError as e:
        logger.error(f"JWT解码错误: {e}")
        raise HTTPException(status_code=401, detail="无效的令牌")


async def get_current_user(token: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """获取当前用户"""
    if token is None:
        raise HTTPException(status_code=401, detail="未提供令牌")
    payload = verify_jwt_token(token.credentials)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="无效的令牌")
    return {"username": username}


@app.get("/login")
async def login(username: str, password: str):
    if username == "admin" and password == "secret":
        token = create_jwt_token({"sub": username})
        return {"access_token": token, " token_type": "bearer"}
    raise HTTPException(status_code=401)


@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['username']}! This is a protected route."}
