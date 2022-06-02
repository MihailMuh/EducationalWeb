import datetime

from django.db.models import QuerySet

from .server_utils import *
from ..models import Marks, Diary
from ..shortcuts import aget_schedule_from_db, afilter, aget_query


async def get_marks(week: str, nickname: str) -> list:
    marks_query: QuerySet = await afilter(Marks, nickname=nickname)
    date: datetime = datetime.datetime.strptime(week + '-1', "%Y-W%W-%w")
    marks: list = []

    for _ in range(7):
        mark = await aget_query(marks_query, date=date.strftime('%Y-%m-%d'))

        marks.append([])

        date += datetime.timedelta(days=1)

    return marks


async def aget_student_schedule(week: str, nickname: str, school: str, clazz: str) -> dict:
    schedule: Diary = await aget_schedule_from_db(school, clazz, week)
    marks: dict = {"marks": await get_marks(week, nickname)}

    if not schedule:
        return base_student_schedule | marks
    return {"schedule": schedule.schedule} | marks
