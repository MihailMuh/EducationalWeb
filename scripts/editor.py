# -*- coding: utf-8 -*-
import datetime

from postgresgl import *


def primary_nick(array, nick):
    if nick not in array:
        array.append(nick)
        return nick
    return primary_nick(array, nick + "0")


def clear_strings(string):
    return string.replace("\ufeff", "").replace("\n", "")


class DB:
    def __init__(self):
        async def i():
            async with await connect() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("""CREATE TABLE IF NOT EXISTS diary
                                            (school TEXT, class TEXT, week TEXT, schedule TEXT[][][]);
                                            
                                            CREATE TABLE IF NOT EXISTS marks
                                            (nickname TEXT, date TEXT, weight INTEGER, value INTEGER, 
                                            theme TEXT, subject TEXT);

                                            CREATE TABLE IF NOT EXISTS peoples
                                            (nickname TEXT PRIMARY KEY, name TEXT, password TEXT, school TEXT, 
                                            database TEXT);

                                            CREATE TABLE IF NOT EXISTS teachers
                                            (nickname TEXT PRIMARY KEY, character TEXT, fixed_classes TEXT[][]);
                                            
                                            CREATE TABLE IF NOT EXISTS students
                                            (nickname TEXT PRIMARY KEY, class TEXT, grouping TEXT);     
                                                   
                                            CREATE TABLE IF NOT EXISTS classes
                                            (school TEXT, class TEXT PRIMARY KEY, classroom TEXT, subjects TEXT[]);                                        
                                        """)

        asyncio.run(i())

    async def __kill(self, name):
        async with await connect() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"DROP TABLE {name}")
                print(f"DB {name} dropped")

    async def add_people(self):
        async with await connect() as connection:
            async with connection.cursor() as cursor:
                with open("students.csv", encoding='utf-8') as file:
                    students = file.readlines()
                    students.reverse()
                    for student_and_class in students:
                        student, clazz, group = student_and_class.replace("\n", "").replace("\ufeff", "").split(";")
                        clazz = clear_strings(clazz)
                        student = clear_strings(student)

                        await self.__add_user(cursor, student, student, "0000", 'МАОУ "Лицей №6"', "students",
                                              (clazz, group))

                with open("teachers.csv", encoding='utf-8') as file:
                    for teacher_and_classes in file.readlines():
                        teacher_classes = []
                        teacher_and_classes = teacher_and_classes.replace("\n", "").replace("\ufeff", "").split(";")
                        teacher = teacher_and_classes[0]

                        for j in teacher_and_classes[1:]:
                            if j:
                                classes = j.split()
                                teacher_classes.append(
                                    [i.replace("-", " ") for i in classes] + ["" for _ in range(5 - len(classes))])

                        teacher_classes += [["" for _ in range(5)] for _ in range(16 - len(teacher_classes))]
                        await self.__add_user(cursor, teacher, teacher, "1111",
                                              'МАОУ "Лицей №6"', "teachers",
                                              ("teacher", teacher_classes))

    async def __add_user(self, cursor, nick, name, password, school, database, data: tuple):
        await cursor.execute("INSERT INTO peoples VALUES (%s, %s, %s, %s, %s)",
                             (nick, name, password, school, database))
        await cursor.execute(f"INSERT INTO {database} VALUES (%s, %s, %s)", (nick,) + data)

    async def add_diary(self):
        date = datetime.date.today().isocalendar()
        week = str(date[1])
        if len(week) == 1:
            week = "0" + week
        date = f"{date[0]}-W{week}"

        async with await connect() as connection:
            async with connection.cursor() as cursor:
                with open("schedule.csv", encoding='utf-8') as file:
                    schedule = []
                    day = []
                    classes = file.readline().replace("\n", "").replace("\ufeff", "").split(";")
                    current_class = 0
                    subjects_count = 0
                    all_schedule = file.readlines()

                    while current_class < len(classes):
                        for subject in all_schedule:
                            subject = subject.replace("\ufeff", "").replace("\n", "").split(";")[current_class]
                            if subject != "":
                                if subject == "---":
                                    day.append(["", ""])
                                else:
                                    day.append([subject, "Не задано"])
                            else:
                                schedule.append(day + [["", ""] for _ in range(8 - len(day))])
                                day = []
                                subjects_count += 1

                                if subjects_count == 6:
                                    break

                        await cursor.execute("INSERT INTO diary VALUES (%s, %s, %s, %s)",
                                             ('МАОУ "Лицей №6"', classes[current_class], date, schedule))

                        schedule = []
                        subjects_count = 0
                        current_class += 1

    async def add_classes(self):
        async with await connect() as connection:
            async with connection.cursor() as cursor:
                with open("classes.csv", encoding='utf-8') as file:
                    for i in file.readlines():
                        clazz = i.replace("\n", "").replace("\ufeff", "").split(";")
                        await cursor.execute("INSERT INTO classes VALUES (%s, %s, %s, %s)",
                                             ('МАОУ "Лицей №6"', clazz[0], clazz[1], clazz[2:]))

    def add_all(self):
        asyncio.run(self.add_people())
        asyncio.run(self.add_diary())
        asyncio.run(self.add_classes())

    def kill_all(self):
        asyncio.run(self.__kill("diary"))
        asyncio.run(self.__kill("peoples"))
        asyncio.run(self.__kill("teachers"))
        asyncio.run(self.__kill("students"))
        asyncio.run(self.__kill("marks"))
        asyncio.run(self.__kill("classes"))

    async def __print(self, cursor, name):
        await cursor.execute(f"SELECT * FROM {name}")
        print(f"---------------------------------------------------{name}")
        for i in await cursor.fetchall():
            print(i)
        print("    ")

    def print(self):
        async def p():
            async with await connect() as connection:
                async with connection.cursor() as cursor:
                    await self.__print(cursor, "peoples")
                    await self.__print(cursor, "teachers")
                    await self.__print(cursor, "students")
                    await self.__print(cursor, "classes")
                    await self.__print(cursor, "diary")
                    await self.__print(cursor, "marks")

        asyncio.run(p())

    def set_admin(self, name):
        async def s():
            async with await connect() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(f"""SELECT nickname FROM peoples WHERE name = '{name}'""")

                    await cursor.execute(f"""UPDATE teachers
                                            SET character = 'admin'
                                            WHERE nickname = '{(await cursor.fetchone())[0]}'
                                            """)

        asyncio.run(s())


db = DB()
# db.kill_all()

# db = DB()
# db.add_all()
# asyncio.run(db.add_diary())
# asyncio.run(db.kill_diary())
# db.set_admin("Учитель14")
# db.set_admin("Учитель16")
# db.set_admin("Учитель38")

db.print()
