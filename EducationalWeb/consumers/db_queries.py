import logging

from async_lru import alru_cache

from .server_utils import *
from ..models import Mark, Diary, ClassData, People
from ..shortcuts import aget_diary_from_db, query_to_tuple

logger = logging.getLogger("mihalis")


async def get_marks(week: str, nickname: str) -> list:
    date: datetime = datetime.datetime.strptime(week + '-1', "%Y-W%W-%w")
    marks_list_to_post: dict = {}

    for _ in range(7):
        marks_list_to_post[date.strftime('%Y-%m-%d')] = []
        date += datetime.timedelta(days=1)

    marks: tuple = await query_to_tuple(
        Mark.objects.filter(nickname=nickname, date__in=tuple(marks_list_to_post.keys())))

    for mark in marks:
        marks_list_to_post[mark.date].append([mark.value, mark.weight, mark.theme, mark.subject])

    return list(marks_list_to_post.values())


async def get_schedule(school: str, clazz: str, week: str) -> list:
    schedule: Diary = await aget_diary_from_db(school, clazz, week)

    if not schedule:
        return base_student_schedule
    return schedule.schedule


async def get_student_schedule(week: str, nickname: str, school: str, clazz: str) -> dict:
    schedule: list = await get_schedule(school, clazz, week)
    marks: list = await get_marks(week, nickname)

    return {"schedule": schedule, "marks": marks}


@alru_cache(maxsize=64, typed=True)
async def save_schedule(school: str, clazz: str, week: str, new_schedule: tuple):
    old_schedule: Diary = await aget_diary_from_db(school, clazz, week)

    if old_schedule:
        old_schedule.schedule = join_schedules(old_schedule.schedule, new_schedule)
        await old_schedule.asave()
    else:
        new_schedule = join_schedules([[["", ""] for _ in range(8)] for _ in range(6)], new_schedule)
        await Diary.objects.acreate(school=school, clazz=clazz, week=week, schedule=new_schedule)


async def get_teacher_schedule(week: str, fixed_classes: list, school: str) -> list:
    schedule: list = [[["", "", "", "", i] for i in range(8)] for _ in range(6)]
    classes_list: tuple = tuple(class_and_subjects[0] for class_and_subjects in fixed_classes)
    schedules_list: tuple = await query_to_tuple(Diary.objects.filter(school=school, week=week, clazz__in=classes_list))

    if not schedules_list:
        return schedule

    classes_data_list: tuple = await query_to_tuple(ClassData.objects.filter(school=school, clazz__in=classes_list))
    iteration: int = 0

    for class_and_subjects in fixed_classes:
        clazz: str = class_and_subjects[0]
        teacher_subjects: tuple = tuple(class_and_subjects[1:])
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
    diary: Diary = await aget_diary_from_db(school, clazz, week)
    diary.schedule[day_id][subject_id][1] = homework

    await diary.asave()


async def get_students_and_marks(clazz: str, school: str, date: str, subject: str):
    calendar = tuple(map(str, strdate_to_datetime(date).isocalendar()))
    weekday = int(calendar[2]) - 1
    if weekday == 6:
        return {}

    diary: Diary = await aget_diary_from_db(school=school, clazz=clazz, week=calendar[0] + "-W" + calendar[1])
    if (not diary) or (not contains_subject_by_date(diary.schedule, subject, weekday)):
        return {}

    peoples: tuple = await query_to_tuple(People.objects.
                                          select_related("student").
                                          filter(school=school, is_student=True, student__clazz=clazz))
    marks: tuple = await query_to_tuple(Mark.objects.filter(
        nickname__in=tuple(people.nickname for people in peoples), date=date,
        subject=subject))
    nicks_and_marks_dict: dict = {mark.nickname: mark for mark in marks}

    subjects_in_day: tuple = tuple(i[0] for i in diary.schedule[weekday])
    students_to_post: list = []
    theme, weight = get_theme_and_weight_from_marks(marks)

    for i in range(len(peoples)):
        people: People = peoples[i]
        nickname: str = people.nickname

        # Если оценка - число, то в js, в элемент, вставляться будет 'null'
        mark_value: str = ""
        group: str = people.student.grouping

        if incompatible_group(subject, subjects_in_day, group):
            continue

        if nicks_and_marks_dict.get(nickname):
            mark_value = str(nicks_and_marks_dict[nickname].value)

        students_to_post.append({
            "nickname": nickname,
            "name": people.name,
            "grouping": group,
            "mark": mark_value
        })

    return {"students": students_to_post, "theme": theme, "weight": weight}


async def post_marks(marks: list, date: str, theme: str, weight: str, subject: str):
    nicknames: tuple = tuple(nick_and_mark[0] for nick_and_mark in marks)
    marks_from_db: tuple = await query_to_tuple(Mark.objects.filter(nickname__in=nicknames,
                                                                    date=date, subject=subject))
    dict_marks_from_db: dict = {mark.nickname: mark for mark in marks_from_db}
    marks_to_create: list = []
    marks_to_update: list = []

    for nickname, mark_value in marks:
        # если оценки нет в бд
        if not dict_marks_from_db.get(nickname):
            if mark_value != 0:
                marks_to_create.append(Mark(nickname=nickname, date=date, weight=weight,
                                            theme=theme, subject=subject, value=mark_value))
        else:
            mark: Mark = dict_marks_from_db[nickname]

            if mark_value != 0:
                mark.value = mark_value
                mark.theme = theme
                mark.weight = weight

                marks_to_update.append(mark)
            else:
                await mark.adelete()

    await Mark.objects.abulk_update(marks_to_update, ["value", "theme", "weight"])
    await Mark.objects.abulk_create(marks_to_create)


async def get_mark_report(nickname: str, clazz: str, school: str, start_date: str, end_date: str):
    class_data: ClassData = await ClassData.objects.aget(clazz=clazz, school=school)

    # class_data.subjects примерно такой: ['Химия', 'Проект', 'Родной русский язык', '', '', '']
    # последние пустые строки не нужны
    subjects: tuple = tuple(subject for subject in class_data.subjects if subject)
    start_date: datetime = strdate_to_datetime(start_date)
    end_date: datetime = strdate_to_datetime(end_date)
    mark_report: dict = {}

    while start_date != end_date:
        mark_report[str(start_date)] = []
        start_date += datetime.timedelta(days=1)

    marks: tuple = await query_to_tuple(Mark.objects.filter(nickname=nickname, date__in=mark_report.keys()))

    for mark in marks:
        mark_report[mark.date].append([mark.value, mark.subject, mark.weight, mark.theme])

    # Будет много дат, где нет оценок. Чтобы не раздувать отчет пустыми датами, уберём их
    mark_report = dict([(date, mark_list) for date, mark_list in mark_report.items() if mark_list])

    return {"days": mark_report, "subjects": subjects}
