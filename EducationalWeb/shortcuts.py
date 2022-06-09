from typing import Type, Any

from channels.db import database_sync_to_async
from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404
from django.template import loader

from .models import Diary, People


def get_template(name: str) -> str:
    return loader.render_to_string(name)


def to_async(func):
    return database_sync_to_async(func, thread_sensitive=False)


async def asave(klass: Model):
    return await to_async(klass.save)()


async def afilter(klass: Type[Model], *args, **kwargs) -> tuple:
    return await to_async(tuple)(klass.objects.filter(*args, **kwargs))


async def aget(klass: Type[Model], *args, **kwargs):
    return await aget_query(klass.objects, *args, **kwargs)


async def aget_query(query: QuerySet, *args, **kwargs):
    try:
        return await to_async(query.get)(*args, **kwargs)
    except query.model.DoesNotExist:
        return None


async def acreate(klass: Type[Model], **kwargs) -> Any:
    return await to_async(klass.objects.create)(**kwargs)


async def aget_schedule_from_db(school: str, clazz: str, week: str) -> Diary:
    return await aget(klass=Diary, school=school, clazz=clazz, week=week)


async def aget_user_character(character: str, nickname: str, school: str) -> People:
    return await to_async(People.objects.select_related(character).get)(nickname=nickname,
                                                                        school=school)


async def afilter_user_character(klass: Type[Model], table: str, **kwargs) -> tuple:
    return await to_async(tuple)(klass.objects.select_related(table).filter(**kwargs))


aget_object_or_404 = to_async(get_object_or_404)
