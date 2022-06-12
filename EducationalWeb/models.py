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
        return f"Class: {self.clazz}\nSchool: {self.school}\nClassroom: {self.classroom}\nSubjects: {self.subjects}\n"


class Diary(AsyncModel):
    clazz = CharField(max_length=3)
    school = CharField(max_length=100)
    week = CharField(max_length=8)
    schedule = ArrayField(ArrayField(ArrayField(CharField(max_length=100))))

    def __str__(self):
        return f"Class: {self.clazz}\nSchool: {self.school}\nWeek: {self.week}\nSchedule: {self.schedule}\n"


class Mark(AsyncModel):
    nickname = CharField(max_length=100)
    date = CharField(max_length=20)
    weight = PositiveSmallIntegerField()
    value = PositiveSmallIntegerField()
    theme = CharField(max_length=5000)
    subject = CharField(max_length=100)


class Student(AsyncModel):
    clazz = CharField(max_length=3)
    grouping = CharField(max_length=50)


class Teacher(AsyncModel):
    character = CharField(max_length=7)
    fixed_classes = ArrayField(ArrayField(CharField(max_length=100)))


class People(AsyncModel):
    nickname = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100)
    password = CharField(max_length=300)
    school = CharField(max_length=100)
    is_student = BooleanField(default=True)
    student = OneToOneField(Student, on_delete=CASCADE, null=True)
    teacher = OneToOneField(Teacher, on_delete=CASCADE, null=True)
