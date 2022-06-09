from django.db.models import QuerySet

from .server_utils import *
from ..models import Mark, Diary, ClassData, People
from ..shortcuts import aget_schedule_from_db, asave, acreate, afilter, to_async

logger = logging.getLogger("mihalis")


async def get_marks(week: str, nickname: str) -> list:
    date: datetime = datetime.datetime.strptime(week + '-1', "%Y-W%W-%w")
    date_list: list = []
    marks: list = []

    for _ in range(7):
        date_list.append(date.strftime('%Y-%m-%d'))
        date += datetime.timedelta(days=1)
        marks.append([])

    # marks_query: QuerySet = await to_async(Mark.objects.filter(nickname=nickname).filter)(date__in=date_list)

    return marks


async def get_schedule(school: str, clazz: str, week: str) -> list:
    schedule: Diary = await aget_schedule_from_db(school, clazz, week)

    if not schedule:
        return base_student_schedule
    return schedule.schedule


async def get_student_schedule(week: str, nickname: str, school: str, clazz: str) -> dict:
    schedule: list = await get_schedule(school, clazz, week)
    marks: list = await get_marks(week, nickname)

    return {"schedule": schedule, "marks": marks}


async def save_schedule(school: str, clazz: str, week: str, new_schedule: list):
    old_schedule: Diary = await aget_schedule_from_db(school, clazz, week)

    if old_schedule:
        old_schedule.schedule = join_schedules(old_schedule.schedule, new_schedule)
        await asave(old_schedule)
    else:
        new_schedule = join_schedules([[["", ""] for _ in range(8)] for _ in range(6)], new_schedule)
        await acreate(Diary, school=school, clazz=clazz, week=week, schedule=new_schedule)


async def get_teacher_schedule(week: str, fixed_classes: list, school: str) -> list:
    schedule: list = [[["", "", "", "", i] for i in range(8)] for _ in range(6)]
    classes_list: list = [class_and_subjects[0] for class_and_subjects in fixed_classes]
    schedules_list: tuple = await afilter(Diary, school=school, week=week, clazz__in=classes_list)

    if not schedules_list:
        return schedule

    classes_data_list: tuple = await afilter(ClassData, school=school, clazz__in=classes_list)
    iteration: int = 0

    for class_and_subjects in fixed_classes:
        clazz: str = class_and_subjects[0]
        teacher_subjects: list = class_and_subjects[1:]
        classroom: str = classes_data_list[iteration].classroom
        schedule_of_class: list = schedules_list[iteration].schedule

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

        iteration += 1

    return [sorted(day, key=lambda x: x[-1]) for day in schedule]


async def post_homework(clazz: str, school: str, week: str, day_id: int, subject_id: int, homework: str):
    diary: Diary = await aget_schedule_from_db(school, clazz, week)
    diary.schedule[day_id][subject_id][1] = homework

    await asave(diary)


async def get_students_and_marks(clazz: str, school: str, date: str, subject: str):
    calendar = tuple(map(str, strdate_to_datetime(date).isocalendar()))
    weekday = int(calendar[2]) - 1
    if weekday == 6:
        return {}

    diary: Diary = await aget_schedule_from_db(school=school, clazz=clazz, week=calendar[0] + "-W" + calendar[1])
    if (not diary) or (not contains_subject_by_date(diary.schedule, subject, weekday)):
        return {}

    peoples_query: QuerySet = People.objects.select_related("student").filter(school=school, is_student=True,
                                                                              student__clazz=clazz)
    peoples: tuple = await to_async(tuple)(peoples_query)
    marks: tuple = await afilter(Mark, nickname__in=tuple(people.nickname for people in peoples), date=date,
                                 subject=subject)

    subjects_in_day: tuple = tuple(i[0] for i in diary.schedule[weekday])
    students_to_post: list = []
    theme, weight = get_theme_and_weight_from_marks(marks)
    mark_counts: int = len(marks)

    for i in range(len(peoples)):
        people: People = peoples[i]

        # Если оценка - число, то в js, в элемент, вставляться будет 'null'
        mark_value: str = ""
        group: str = people.student.grouping

        if incompatible_group(subject, subjects_in_day, group):
            continue

        if i < mark_counts:
            mark: Mark = marks[i].mark
            logger.info(mark)

            if len(theme) == 0:
                theme = mark.theme
                weight = mark.weight
            mark_value = str(mark.value)

        students_to_post.append({
            "nickname": people.nickname,
            "name": people.name,
            "grouping": group,
            "mark": mark_value
        })

    return {"students": students_to_post, "theme": theme, "weight": weight}


async def post_marks(marks: list, date: str, theme: str, weight: str, subject: str):
    pass
    # for nickname, mark in marks:
