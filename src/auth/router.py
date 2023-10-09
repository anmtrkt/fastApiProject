import uuid

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.base_config import auth_backend
from src.auth.manager import get_user_manager
from src.auth.models import info, User
from src.database import get_async_session

from fastapi_users import fastapi_users, FastAPIUsers

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)



@router.post("/login")
async def get_info(user: User = Depends(current_active_user), session: AsyncSession = Depends(get_async_session), user_agent: str = Header(None),
                   cookie: str = Header(None)):
    cookies = cookie
    host = Request.client.host
    userAG = user_agent
    stmt = insert(info).values(
        ip=host,
        cookies=cookies,
        user_ag=userAG
    )
    await session.execute(stmt)
    await session.commit()
    return {"user_agent": user_agent}
''''

# session.begin()
# try:
#     session.add(userAG)
# except:
#    session.rollback()
#    raise
# else:
#     session.commit()


#   return {"user_agent": head}

async def app(scope, receive, send):

    content = '%s %s' % (request.method, request.url.path)
    response = Response(content, media_type='text/plain')
    await response(scope, receive, send)

stmt = insert(info).values(
    ip=host,
    cookies=cookies,
    user_ag=userAG
)
await session.execute(stmt)
await session.commit()
'''