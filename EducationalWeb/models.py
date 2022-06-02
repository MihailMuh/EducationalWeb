from django.contrib.postgres.fields import ArrayField
from django.db.models import CharField, IntegerField, BooleanField
from django.db.models import Model


class Classes(Model):
    clazz = CharField(max_length=3)
    school = CharField(max_length=100)
    classroom = CharField(max_length=10)
    subjects = ArrayField(CharField(max_length=100))


class Peoples(Model):
    nickname = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100)
    password = CharField(max_length=300)
    school = CharField(max_length=100)
    is_student = BooleanField(default=True)


class Students(Model):
    nickname = CharField(max_length=100, primary_key=True)
    clazz = CharField(max_length=3)
    grouping = CharField(max_length=50)


class Teachers(Model):
    nickname = CharField(max_length=100, primary_key=True)
    character = CharField(max_length=7)
    fixed_classes = ArrayField(ArrayField(CharField(max_length=100)))


class Diary(Model):
    school = CharField(max_length=100)
    clazz = CharField(max_length=3)
    week = CharField(max_length=8)
    schedule = ArrayField(ArrayField(ArrayField(CharField(max_length=100))))


class Marks(Model):
    nickname = CharField(max_length=100, primary_key=True)
    date = CharField(max_length=20)
    weight = IntegerField()
    value = IntegerField()
    theme = CharField(max_length=5000)
    subject = CharField(max_length=100)
