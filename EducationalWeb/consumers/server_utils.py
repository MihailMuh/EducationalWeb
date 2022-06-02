import orjson
from channels.generic.websocket import AsyncWebsocketConsumer


class AsyncOrjsonWebsocketConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            await self.receive_json(self.decode_json(text_data), **kwargs)

    async def receive_json(self, content, **kwargs):
        pass

    async def send_json(self, content, close=False):
        await super().send(bytes_data=self.encode_json(content), close=close)

    @classmethod
    def decode_json(cls, text_data):
        return orjson.loads(text_data)

    @classmethod
    def encode_json(cls, content):
        return orjson.dumps(content)


base_student_schedule: dict = {"schedule": [[["", ""] for i in range(8)] for j in range(6)]}
groups = (" 1 гр.", " 2 гр.", " ест.", " эк.")


def get_value_or_none(dictionary: dict, key: str):
    if dictionary.get(key):
        return dictionary[key]
