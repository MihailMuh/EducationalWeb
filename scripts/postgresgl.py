import psycopg


async def connect():
    return await psycopg.AsyncConnection.connect(dbname="test", user="test", password="test", host="test",
                                                 autocommit=True)
