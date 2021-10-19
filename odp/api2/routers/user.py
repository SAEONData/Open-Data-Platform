from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from odp.api2.models import UserIn, UserOut, UserSort
from odp.api2.routers import Pager, Paging
from odp.db import Session
from odp.db.models import User

router = APIRouter()


@router.get('/', response_model=List[UserOut])
async def list_users(
        pager: Pager = Depends(Paging(UserSort)),
):
    stmt = (
        select(User).
        order_by(getattr(User, pager.sort)).
        offset(pager.skip).
        limit(pager.limit)
    )

    users = [
        UserOut(
            id=row.User.id,
            email=row.User.email,
            active=row.User.active,
            verified=row.User.verified,
            name=row.User.name,
            picture=row.User.picture,
            role_ids=[role.id for role in row.User.roles],
        )
        for row in Session.execute(stmt)
    ]

    return users


@router.get('/{user_id}', response_model=UserOut)
async def get_user(
        user_id: str,
):
    if not (user := Session.get(User, user_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return UserOut(
        id=user.id,
        email=user.email,
        active=user.active,
        verified=user.verified,
        name=user.name,
        picture=user.picture,
        role_ids=[role.id for role in user.roles],
    )


@router.put('/')
async def update_user(
        user_in: UserIn,
):
    if not (user := Session.get(User, user_in.id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    user.active = user_in.active
    user.save()


@router.delete('/{user_id}')
async def delete_user(
        user_id: str,
):
    if not (user := Session.get(User, user_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    user.delete()
