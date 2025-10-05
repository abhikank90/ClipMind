from fastapi import Depends
from fastapi.security import HTTPBearer

security = HTTPBearer(auto_error=False)

async def get_current_user():
    return {"id": "user-1", "email": "demo@clipmind.com"}
