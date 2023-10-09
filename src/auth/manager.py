from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Request, Depends, BackgroundTasks, Header

from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users import exceptions, models, schemas

from src.auth.models import User, info
from src.auth.utils import get_user_db
from src.database import get_async_session
from src.config import SECRET_AUTH

from tasks.tasks import get_info

"""
RESET_PASSWORD_TOKEN_AUDIENCE = "fastapi-users:reset"
VERIFY_USER_TOKEN_AUDIENCE = "fastapi-users:verify"
"""


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_AUTH
    verification_token_secret = SECRET_AUTH

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        """
        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user)

        return created_user

    async def on_after_login(self, user: models.UP, request: Request,
                             background_task: BackgroundTasks,
                             user_agent: str = Header(None),
                             session: AsyncSession = Depends(get_async_session)
                             ) -> None:
        background_task.add_task(get_info, user.id, request, user_agent, session)

    """
    Perform logic after user login.

    *You should overload this method to add your own logic.*

    :param user: The user that is logging in
    :param request: Optional FastAPI request
    :param response: Optional response built by the transport.
    Defaults to None
    """

    async def on_before_delete(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        """
        Perform logic before user delete.

        *You should overload this method to add your own logic.*

        :param user: The user to be deleted
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover

    async def on_after_delete(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        """
        Perform logic before user delete.

        *You should overload this method to add your own logic.*

        :param user: The user to be deleted
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        """
        return  # pragma: no cover


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
