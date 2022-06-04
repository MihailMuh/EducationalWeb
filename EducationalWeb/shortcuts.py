from typing import Type, Any

from channels.db import database_sync_to_async
from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404
from django.template import loader

from .models import Diary


def get_template(name: str) -> str:
    return loader.render_to_string(name)


def to_async(func):
    return database_sync_to_async(func, thread_sensitive=False)


async def asave(klass: Model):
    return await to_async(klass.save)()


async def afilter(klass: Type[Model], *args, **kwargs) -> QuerySet:
    return await to_async(klass.objects.filter)(*args, **kwargs)


async def aget(klass: Type[Model], *args, **kwargs):
    return await aget_query(klass.objects, *args, **kwargs)


async def aget_query(query: QuerySet, *args, **kwargs):
    try:
        return await to_async(query.get)(*args, **kwargs)
    except query.model.DoesNotExist:
        return None


async def aget_or_create(klass: Type[Model], **kwargs) -> tuple[Any, bool]:
    return await to_async(klass.objects.get_or_create)(**kwargs)


async def aget_schedule_from_db(school: str, clazz: str, week: str) -> Diary:
    return await aget(klass=Diary, school=school, clazz=clazz, week=week)


aget_object_or_404 = to_async(get_object_or_404)
