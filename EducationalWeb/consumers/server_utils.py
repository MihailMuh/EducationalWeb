import logging
import datetime
from functools import lru_cache

import orjson
from channels.generic.websocket import AsyncWebsocketConsumer

error = logging.getLogger("systemd").error
base_student_schedule: list = [[["", ""] for i in range(8)] for j in range(6)]
groups = (" 1 гр.", " 2 гр.", " ест.", " эк.")


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


def get_value_or_none(dictionary: dict, key: str):
    if dictionary.get(key):
        return dictionary[key]


def join_schedules(old_schedule: list, new_schedule: list) -> list:
    for i in range(6):
        day: list = old_schedule[i]

        for j in range(8):
            new_subj: str = new_schedule[i][j]

            if day[j][0] != new_subj:
                arr = [new_subj, "Не задано"]
                if not new_subj:
                    arr = ["", ""]
                old_schedule[i][j] = arr

    return old_schedule


def contains_subject_by_date(schedule: list, subject: str, weekday: int) -> bool:
    contains_subject = False
    for lesson in schedule[weekday]:
        if subject in lesson[0]:
            contains_subject = True
            break

    return contains_subject


def incompatible_group(subject: str, day_subjects: tuple, student_group: str) -> bool:
    for i in day_subjects:
        if subject == i:
            return False

        if ("/" in i) and (student_group in i):
            return False
    return True


def get_theme_and_weight_from_marks(marks: tuple) -> tuple:
    if not marks:
        return "", 6
    return marks[0].theme, marks[0].weight


@lru_cache(maxsize=1024, typed=True)
def strdate_to_datetime(date: str):
    return datetime.date(*list(map(int, date.split("-"))))


@lru_cache(maxsize=2048, typed=True)
def get_subject(string: str, group: str) -> str:
    return string[:string.index(group)]


@lru_cache(maxsize=2048, typed=True)
def get_classroom(string: str, base_classroom: str) -> str:
    if "(" in string:
        return string[string.index("(") + 1: string.index(")")]
    return base_classroom


def get_subject_group_classroom(subjects_where_found: str, subjects: list, base_classroom: str) -> tuple[str, str, str]:
    for subject in subjects:
        for subject_and_group in subjects_where_found.split("/"):
            if subject in subject_and_group:
                for group in groups:
                    if group in subject_and_group:
                        return get_subject(subject_and_group, group), group, \
                               get_classroom(subject_and_group, base_classroom)
    return "", "", ""
