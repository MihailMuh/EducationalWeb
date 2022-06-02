import asyncio

import psycopg


async def connect():
    return await psycopg.AsyncConnection.connect(dbname="test", user="postgres", password="7604", autocommit=True)


asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)
