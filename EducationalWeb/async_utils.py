import logging
from typing import Any

import orjson
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Manager, Model

error = logging.getLogger("systemd").error


class AsyncOrjsonWebsocketConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            await self.receive_json(self.decode_json(text_data), **kwargs)
        else:
            error("You sent empty TEXT DATA")

    async def receive_json(self, content, **kwargs):
        pass

    async def send_json(self, content, close=False):
        await super().send(bytes_data=self.encode_json(content), close=close)

    @classmethod
    def decode_json(cls, text_data):
        return orjson.loads(text_data)

    @classmethod
    def encode_json(cls, content) -> bytes:
        return orjson.dumps(content)


def to_async(func):
    return database_sync_to_async(func, thread_sensitive=False)


class AsyncManger(Manager):
    async def acreate(self, **kwargs):
        return await to_async(self.create)(**kwargs)

    async def aget(self, *args, **kwargs) -> Any | None:
        try:
            return await to_async(self.get)(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    async def afilter(self, *args, **kwargs):
        return await to_async(self.filter)(*args, **kwargs)

    async def to_tuple(self) -> tuple:
        return await to_async(tuple)(self.query)


class AsyncModel(Model):
    class Meta:
        abstract = True

    objects = AsyncManger()

    async def asave(self):
        await to_async(self.save)()
