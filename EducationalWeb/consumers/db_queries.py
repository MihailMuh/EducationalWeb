import datetime

from django.db.models import QuerySet

from .server_utils import *
from ..models import Marks, Diary, Classes
from ..shortcuts import aget_schedule_from_db, afilter, aget_query, asave, aget_or_create, aget


async def get_marks(week: str, nickname: str) -> list:
    marks_query: QuerySet = await afilter(Marks, nickname=nickname)
    date: datetime = datetime.datetime.strptime(week + '-1', "%Y-W%W-%w")
    marks: list = []

    for _ in range(7):
        mark = await aget_query(marks_query, date=date.strftime('%Y-%m-%d'))

        marks.append([])

        date += datetime.timedelta(days=1)

    return marks


async def get_schedule(school: str, clazz: str, week: str) -> list:
    schedule: Diary = await aget_schedule_from_db(school, clazz, week)

    if not schedule:
        return base_student_schedule
    return schedule.schedule


async def get_student_schedule(week: str, nickname: str, school: str, clazz: str) -> dict:
    schedule: list = await get_schedule(school, clazz, week)
    marks: list = await get_marks(week, nickname)

    return {"schedule": schedule} | {"marks": marks}


async def save_schedule(school: str, clazz: str, week: str, new_schedule: list):
    old_schedule: Diary = await aget_schedule_from_db(school, clazz, week)

    if old_schedule:
        old_schedule.schedule = join_schedules(old_schedule.schedule, new_schedule)
        await asave(old_schedule)
    else:
        new_schedule = join_schedules([[["", ""] for _ in range(8)] for _ in range(6)], new_schedule)
        await aget_or_create(Diary, school=school, clazz=clazz, week=week, schedule=new_schedule)


async def get_teacher_schedule(week: str, fixed_classes: list, school: str) -> list:
    schedule: list = [[["", "", "", "", i] for i in range(8)] for _ in range(6)]

    for class_and_subjects in fixed_classes:
        clazz: str = class_and_subjects[0]
        teacher_subjects: list = class_and_subjects[1:]

        diary: Diary = await aget_schedule_from_db(school, clazz, week)
        if not diary:
            continue

        classes: Classes = await aget(Classes, school=school, clazz=clazz)
        if not classes:
            continue

        schedule_of_class: list = diary.schedule
        classroom: str = classes.classroom

        for i in range(6):
            day: list = schedule_of_class[i]

            for j in range(8):
                subject: str = day[j][0]
                group: str = ""

                if "/" in subject:
                    subject, group, new_classroom = get_subject_group_classroom(subject,
                                                                                teacher_subjects, classroom)
                else:
                    new_classroom: str = get_classroom(subject, classroom)

                if subject and ((subject in teacher_subjects) or ((subject + group) in teacher_subjects)):
                    schedule[i][j] = [clazz, subject + group, new_classroom, day[j][1], j]
                    # чтобы, когда встретили у класса такой же предмет, поставить другой номер урока
                    schedule_of_class[i][j] = ["", "", "", "", i]

    return [sorted(day, key=lambda x: x[-1]) for day in schedule]


async def post_homework(clazz: str, school: str, week: str, day_id: int, subject_id: int, homework: str):
    diary: Diary = await aget_schedule_from_db(school, clazz, week)
    diary.schedule[day_id][subject_id][1] = homework

    await asave(diary)
