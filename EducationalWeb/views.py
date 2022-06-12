import logging

import orjson
from async_lru import alru_cache
from channels.http import AsgiRequest
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render

from EducationalWeb.async_utils import to_async
from EducationalWeb.models import People
from EducationalWeb.shortcuts import get_template

logger = logging.getLogger("django")


async def sign(request: AsgiRequest) -> HttpResponse:
    return render(request, "sign_in.html")


async def diary(request: AsgiRequest) -> HttpResponse:
    return render(request, "main_diary.html")


async def get_html_page(request: AsgiRequest) -> HttpResponse:
    return render(request, orjson.loads(request.body)["html"] + ".html")


@alru_cache(maxsize=1024, typed=True)
async def __login(nickname: str, password: str, school: str) -> dict:
    character: str = "student"
    people_data: dict = {"nickname": nickname, "school": school}

    people: tuple = await to_async(tuple)(People.objects.
                                          select_related("student", "teacher").
                                          filter(nickname=nickname, school=school))

    if not people:
        return {"code": 404}

    people: People = people[0]
    if not check_password(password, people.password):
        return {"code": 405}

    if people.is_student:
        people_data |= {"class": people.student.clazz, "grouping": people.student.grouping}
    else:
        character = people.teacher.character
        classes: list = people.teacher.fixed_classes
        # Из-за того, что в бд хранятся списки фиксированной длины, массив с классами учителя в конце имеет несколько таких элементов: ['', '', '', '', ''], их стоит убрать
        people_data["fixed_classes"] = classes[:classes.index(['', '', '', '', ''])]

    return people_data | {"character": [character, get_template(character + "_main.html")], "code": 200}


async def enter(request: AsgiRequest):
    json: dict = orjson.loads(request.body)
    people_data = await __login(json["nickname"], json["password"], json["school"])

    match people_data["code"]:
        case 405:
            return HttpResponse(status=405)
        case 200:
            return JsonResponse(people_data)

    raise Http404("No such user!")
