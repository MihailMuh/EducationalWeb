from fastapi import HTTPException, status
from psycopg.rows import dict_row
from uvicorn import run

from scripts.app_manager import *
from scripts.postgresgl import *
from scripts.server_utils import *


@app.post("/enter")
async def enter(request: Request):
    data = await request.json()
    nickname = data["nickname"]
    password = data["password"]
    school = data["school"]
    answer_dict: dict = {"nickname": nickname, "school": school}

    async with await connect() as connection:
        async with connection.cursor(row_factory=dict_row) as cursor:
            await cursor.execute(f"""SELECT name, database 
                                    FROM peoples 
                                    WHERE nickname='{nickname}' AND password='{password}' AND school='{school}'
                                    """)
            people: dict = await cursor.fetchone()

            if not people:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Incorrect PASSWORD / NAME")

            if people["database"] == "students":
                await cursor.execute(f"""SELECT class, grouping 
                                        FROM students 
                                        WHERE nickname='{nickname}'
                                        """)
                answer_dict["character"] = "student"
                answer_dict |= await cursor.fetchone()
            else:
                await cursor.execute(f"""SELECT fixed_classes, character 
                                        FROM teachers 
                                        WHERE nickname='{nickname}'
                                        """)
                data = await cursor.fetchone()
                data["fixed_classes"] = clean_fixed_teacher_classes(data["fixed_classes"])
                answer_dict |= data

            answer_dict["character"] = [answer_dict["character"],
                                        get_template(answer_dict["character"] + "_main", request).body]
            return answer_dict


@app.post("/get_schedule")
async def get_schedule(request: Request):
    data = await request.json()
    schedule = await get_schedule_from_bd(data["school"], data["class"], data["week"])
    if schedule:
        return schedule[0]
    else:
        return base_student_schedule


@app.post("/post_schedule")
async def post_schedule(info: Request):
    data = await info.json()
    school = data["school"]
    clazz = data["class"]
    week = data["week"]
    new_schedule = data["schedule"]

    old_schedule = await get_schedule_from_bd(school, clazz, week)

    async with await connect() as connection:
        async with connection.cursor() as cursor:
            if old_schedule:
                await cursor.execute(f"""UPDATE diary
                                        SET schedule = %s
                                        WHERE school='{school}' AND class='{clazz}' AND week='{week}'
                                        """, (join_schedules(old_schedule[0], new_schedule),))
            else:
                print("Создаю новое расписание")
                await cursor.execute("""INSERT INTO diary VALUES (%s, %s, %s, %s)""",
                                     (school, clazz, week,
                                      join_schedules([[["", ""] for _ in range(8)] for _ in range(6)], new_schedule)))


async def get_schedule_from_bd(school, clazz, week):
    async with await connect() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(f"""SELECT schedule
                                    FROM diary
                                    WHERE school='{school}' AND class='{clazz}' AND week='{week}'
                                    """)
            return await cursor.fetchone()


@app.post("/get_students")
async def get_students(info: Request):
    data = await info.json()
    school = data["school"]
    clazz = data["class"]
    date = data["date"]
    subject = data["subject"]
    calendar = tuple(map(str, strdate_to_datetime(date).isocalendar()))

    async with await connect() as connection:
        async with connection.cursor() as cursor:
            schedule = await get_schedule_from_bd(school, clazz, calendar[0] + "-W" + calendar[1])
            weekday = int(calendar[2]) - 1
            if not contains_subject_by_date(schedule, subject, weekday):
                return {}

            await cursor.execute(f"""SELECT student.nickname, name, student.grouping
                                    FROM peoples, (SELECT nickname, grouping
                                        FROM students
                                        WHERE class='{clazz}') AS student
                                    WHERE peoples.nickname = student.nickname and school='{school}'
                                    """)

            subjects_in_day = tuple(i[0] for i in schedule[0][weekday])
            students = await cursor.fetchall()
            students_to_post = []
            marks = []
            theme = ""
            weight = ""

            for student in students:
                if incompatible_group(subject, subjects_in_day, student[2]):
                    continue
                else:
                    students_to_post.append(student)

                student = student[0]
                await cursor.execute(f"""SELECT value
                                        FROM marks
                                        WHERE date='{date}' AND nickname='{student}' AND subject=%s
                                        """, (subject,))
                mark = await cursor.fetchone()
                if mark:
                    if len(theme) == 0:
                        await cursor.execute(f"""SELECT theme, weight
                                                FROM marks
                                                WHERE date='{date}' AND nickname='{student}'
                                                """)
                        theme, weight = await cursor.fetchone()
                    marks.append(mark[0])
                else:
                    marks.append("")

            return {"students": students_to_post, "marks": marks, "theme": theme, "weight": weight}


@app.post("/post_marks")
async def post_marks(info: Request):
    data = await info.json()
    date = data["date"]
    theme = data["theme"]
    weight = data["weight"]
    subject = data["subject"]

    async with await connect() as connection:
        async with connection.cursor() as cursor:
            for nickname, mark in data["marks"]:
                condition = f"WHERE Nickname='{nickname}' AND Date='{date}' AND Subject=%s"

                await cursor.execute(f"SELECT EXISTS (SELECT 100 FROM marks {condition})", (subject,))
                if (await cursor.fetchone())[0]:
                    if mark != 0:
                        await cursor.execute(f"""UPDATE marks 
                                                SET Value={mark}, Theme='{theme}', Weight={weight} 
                                                {condition}
                                                """, (subject,))
                    else:
                        await cursor.execute(f"DELETE FROM marks {condition}", (subject,))
                elif mark != 0:
                    await cursor.execute("""INSERT INTO marks
                                            VALUES (%s, %s, %s, %s, %s, %s)""",
                                         (nickname, date, weight, mark, theme, subject))


@app.post("/get_marks")
async def get_marks(info: Request):
    data = await info.json()
    week = data["week"]
    nickname = data["nickname"]

    date = datetime.datetime.strptime(week + '-1', "%Y-W%W-%w")
    marks = []

    async with await connect() as connection:
        async with connection.cursor() as cursor:
            for i in range(7):
                await cursor.execute(f"""SELECT value, weight, theme, subject
                                        FROM marks
                                        WHERE Date='{date.strftime('%Y-%m-%d')}' AND Nickname='{nickname}'
                                        """)
                marks.append(await cursor.fetchall())
                date += datetime.timedelta(days=1)

            return marks


@app.post("/get_mark_report")
async def get_mark_report(info: Request):
    data = await info.json()
    nickname = data["nickname"]
    clazz = data["class"]
    school = data["school"]
    start_date = strdate_to_datetime(data["start_date"])
    end_date = strdate_to_datetime(data["end_date"]) + datetime.timedelta(days=1)

    async with await connect() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(f"""SELECT subjects
                                    FROM classes
                                    WHERE class='{clazz}' AND school='{school}'
                                    """)
            report = {}
            subjects = [subject for subject in (await cursor.fetchone())[0] if subject]
            while start_date != end_date:
                await cursor.execute(f"""SELECT value, subject, weight, theme
                                        FROM marks
                                        WHERE nickname = '{nickname}'
                                        AND date = '{str(start_date)}'
                                        """)
                data = await cursor.fetchall()

                if data:
                    report[str(start_date)] = data
                    for elems in data:
                        if elems[1] not in subjects:
                            subjects.append(elems[1])

                start_date += datetime.timedelta(days=1)

            return {"days": report, "subjects": subjects}


@app.post("/get_teacher_schedule")
async def get_teacher_schedule(info: Request):
    data = await info.json()
    fixed_classes = data["fixed_classes"]
    week = data["week"]
    school = data["school"]
    schedule = [[["", "", "", "", i] for i in range(8)] for _ in range(6)]

    async with await connect() as connection:
        async with connection.cursor() as cursor:
            for class_and_subjects in fixed_classes:
                clazz = class_and_subjects[0]
                teacher_subjects = class_and_subjects[1:]

                await cursor.execute(f"""SELECT schedule, classroom 
                                        FROM diary, (SELECT classroom
                                                    FROM classes 
                                                    WHERE school='{school}' AND class='{clazz}') as classroom
                                        WHERE school='{school}' AND week='{week}' AND class='{clazz}'
                                        """)
                data = await cursor.fetchone()
                if data:
                    class_schedule = data[0]
                    classroom = data[1]
                else:
                    continue

                for i in range(len(class_schedule)):
                    day = class_schedule[i]

                    for j in range(len(day)):
                        subject = day[j][0]
                        group = ""

                        if "/" in subject:
                            subject, group, new_classroom = get_subject_group_classroom(subject,
                                                                                        teacher_subjects, classroom)
                        else:
                            new_classroom = get_classroom(subject, classroom)

                        if subject and ((subject in teacher_subjects) or ((subject + group) in teacher_subjects)):
                            schedule[i][j] = [clazz, subject + group, new_classroom, day[j][1], j]
                            # чтобы, когда встретили у класса такой же предмет, поставить другой номер урока
                            class_schedule[i][j] = ["", "", "", "", i]

    return [sorted(day, key=lambda x: x[-1]) for day in schedule]


@app.post("/post_homework")
async def post_homework(info: Request):
    data = await info.json()
    clazz = data["class"]
    school = data["school"]
    week = data["week"]
    day_id = data["day_id"]
    subject_id = data["subject_id"]
    homework = data["homework"]

    async with await connect() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(f"""SELECT schedule
                                    FROM diary
                                    WHERE week='{week}' AND class='{clazz}' AND school='{school}'
                                    """)
            schedule = (await cursor.fetchone())[0]
            schedule[day_id][subject_id][1] = homework
            await cursor.execute(f"""UPDATE diary
                                    SET schedule = %s
                                    WHERE school='{school}' AND class='{clazz}' AND week='{week}'
                                    """, (schedule,))


if __name__ == '__main__':
    run("server:app", host="0.0.0.0", port=49147)
