from functools import lru_cache

from django.db.models import QuerySet
from django.template import loader

from .async_utils import to_async
from .models import Diary


@lru_cache(maxsize=16)
def get_template(name: str) -> str:
    return loader.render_to_string(name)


async def aget_diary_from_db(school: str, clazz: str, week: str) -> Diary | None:
    return await Diary.objects.aget(school=school, clazz=clazz, week=week)


async def query_to_tuple(query: QuerySet):
    return await to_async(tuple)(query)
