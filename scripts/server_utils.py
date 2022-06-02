import datetime
from functools import lru_cache

base_student_schedule = [[["", ""] for i in range(8)] for j in range(6)]
groups = (" 1 гр.", " 2 гр.", " ест.", " эк.")


def join_schedules(old_schedule, new_schedule):
    for i in range(len(old_schedule)):
        day = old_schedule[i]

        for j in range(len(day)):
            new_subj = new_schedule[i][j]

            if day[j][0] != new_subj:
                arr = [new_subj, "Не задано"]
                if not new_subj:
                    arr = ["", ""]
                old_schedule[i][j] = arr

    return old_schedule


def contains_subject_by_date(schedule: list, subject: str, weekday: int):
    if (not schedule) or (weekday == 6):
        return False

    contains_subject = False
    for lesson in schedule[0][weekday]:
        if subject in lesson[0]:
            contains_subject = True
            break
    if not contains_subject:
        return False
    return True


@lru_cache(maxsize=2048, typed=True)
def incompatible_group(subject: str, day_subjects: tuple, student_group: str):
    for i in day_subjects:
        if subject == i:
            return False

        if "/" in i:
            if student_group in i:
                return False
    return True


@lru_cache(maxsize=1024, typed=True)
def strdate_to_datetime(date: str):
    return datetime.date(*list(map(int, date.split("-"))))


def clean_fixed_teacher_classes(input_classes):
    classes = [[]]
    index = 0
    for i in input_classes:
        if i[0] == "":
            classes.pop()
            break
        for j in i:
            if not j:
                break
            classes[index].append(j)

        index += 1
        classes.append([])
    return classes


@lru_cache(maxsize=2048, typed=True)
def __get_subject(string: str, group: str):
    return string[:string.index(group)]


@lru_cache(maxsize=2048, typed=True)
def get_classroom(string: str, base_classroom: str):
    if "(" in string:
        return string[string.index("(") + 1: string.index(")")]
    return base_classroom


def get_subject_group_classroom(subjects_where_found: str, subjects: list, base_classroom: str):
    for subject in subjects:
        for subject_and_group in subjects_where_found.split("/"):
            if subject in subject_and_group:
                for group in groups:
                    if group in subject_and_group:
                        return __get_subject(subject_and_group, group), group, \
                               get_classroom(subject_and_group, base_classroom)
    return "", "", ""
