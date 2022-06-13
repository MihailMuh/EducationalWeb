from django.contrib.postgres.fields import ArrayField
from django.db.models import CharField, PositiveSmallIntegerField, OneToOneField, CASCADE, BooleanField
from django.db.models import Model

from .async_utils import AsyncModel


class ClassData(AsyncModel):
    clazz = CharField(max_length=3, primary_key=True)
    school = CharField(max_length=100)
    classroom = CharField(max_length=10)
    subjects = ArrayField(CharField(max_length=100))

    def __str__(self):
        return str({"class": self.clazz, "school": self.school, "classroom": self.classroom, "subjects": self.subjects})


class Diary(AsyncModel):
    clazz = CharField(max_length=3)
    school = CharField(max_length=100)
    week = CharField(max_length=8)
    schedule = ArrayField(ArrayField(ArrayField(CharField(max_length=100))))

    def __str__(self):
        return str({"class": self.clazz, "school": self.school, "week": self.week, "schedule": self.schedule})


class Mark(AsyncModel):
    nickname = CharField(max_length=100)
    date = CharField(max_length=20)
    weight = PositiveSmallIntegerField()
    value = PositiveSmallIntegerField()
    theme = CharField(max_length=5000)
    subject = CharField(max_length=100)

    def __str__(self):
        return str({"nickname": self.nickname, "date": self.date, "weight": self.weight, "value": self.value,
                    "theme": self.theme, "subject": self.subject})

    class Meta:
        ordering = ["nickname"]


class Student(AsyncModel):
    clazz = CharField(max_length=3)
    grouping = CharField(max_length=50)

    def __str__(self):
        return str({"class": self.clazz, "grouping": self.grouping})


class Teacher(AsyncModel):
    character = CharField(max_length=7)
    fixed_classes = ArrayField(ArrayField(CharField(max_length=100)))

    def __str__(self):
        return str({"character": self.character, "fixed_classes": self.fixed_classes})


class People(AsyncModel):
    nickname = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100)
    password = CharField(max_length=300)
    school = CharField(max_length=100)
    is_student = BooleanField(default=True)
    student = OneToOneField(Student, on_delete=CASCADE, null=True)
    teacher = OneToOneField(Teacher, on_delete=CASCADE, null=True)

    def __str__(self):
        return str({"nickname": self.nickname, "name": self.name, "password": self.password, "school": self.school,
                    "is_student": self.is_student, "student": str(self.student), "teacher": str(self.teacher)})
