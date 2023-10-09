import aiohttp
import requests
import json
import asyncio

from fastapi import Depends, Request, Header

from sqlalchemy import insert, update, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, async_session_maker
from src.auth.models import info, location_persentage


async def get_info(
        user_id,
        request: Request,
        user_agent: str = Header(None),
        session: AsyncSession = Depends(get_async_session)
) -> None:
    client_host = request.client.host
    userAG = user_agent
    cookies = request.cookies

    async with aiohttp.ClientSession() as client_session:
#       url = f"http://ip-api.com/json/{client_host}?lang=ru"
        url = "http://ip-api.com/json/144.53.65.7?lang=ru"
        async with client_session.get(url) as response:
            data = await response.json()
            country = data['country']
            region = data['regionName']
            city = data['city']
    incr = await session.scalar(select(info.c.auth_times).where(info.c.id == user_id))
    try:
        auth_times = incr + 1
        stmt = update(info).where(info.c.id == user_id).values(
            ip=client_host,
            cookies=cookies,
            user_ag=userAG,
            auth_times=auth_times,
            country=country,
            region=region,
            city=city
        )
    except TypeError:
        stmt = insert(info).values(
            id=user_id,
            ip=client_host,
            cookies=cookies,
            user_ag=userAG,
            auth_times=1,
            country=country,
            region=region,
            city=city
        )
    await main()
    await session.execute(stmt)
    await session.commit()


async def calculate_city_percentage(session: async_session_maker) -> None:
    async with session.begin():
        # Выполняем SQL-запрос для подсчета количества разных городов
        query = await session.execute(
            select(info.c.city, func.count(info.c.city).label('count'))
            .group_by(info.c.city)
            )

    # Выполняем SQL-запрос для получения общего количества записей
        total_count = await session.execute(
            select(func.count('*')).select_from(info)
        )
        total_count = total_count.scalar()

    # Выполняем SQL-запрос для подсчета процентного соотношения
        percentage_query = select(
            info.c.city,
            (func.count(info.c.city) / total_count * 100).label('percentage')
        ).group_by(info.c.city)

    # Получаем результаты запроса
        results = await session.execute(percentage_query)

    # Выводим результаты
        for city, percentage in results:
            percentage=str(percentage)
            print(f"City: {city}, Count: Percentage: {percentage}%")
        stmt = insert(location_persentage).values(
            city=city,
            persentage=percentage,
        )
        await session.execute(stmt)
        await session.commit()
async def main():

    async with async_session_maker() as session:
        await calculate_city_percentage(session)

await main()


