import logging

import orjson
from channels.http import AsgiRequest
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from EducationalWeb.models import People
from EducationalWeb.shortcuts import aget_object_or_404, get_template, aget_user_character

logger = logging.getLogger("django")


async def sign(request: AsgiRequest) -> HttpResponse:
    return render(request, "sign_in.html")


async def diary(request: AsgiRequest) -> HttpResponse:
    return render(request, "main_diary.html")


async def get_html_page(request: AsgiRequest) -> HttpResponse:
    return render(request, orjson.loads(request.body)["html"] + ".html")


async def enter(request: AsgiRequest):
    people_data: dict = orjson.loads(request.body)
    nickname: str = people_data["nickname"]
    password: str = people_data["password"]
    school: str = people_data["school"]
    character: str = "student"

    people: People = await aget_object_or_404(People, nickname=nickname, school=school)

    if not check_password(password, people.password):
        return HttpResponse(status=405)

    if people.is_student:
        people = await aget_user_character("student", nickname=nickname, school=school)
        people_data |= {"class": people.student.clazz, "grouping": people.student.grouping}
    else:
        people = await aget_user_character("teacher", nickname=nickname, school=school)
        character = people.teacher.character
        classes: list = people.teacher.fixed_classes
        # Из-за того, что в бд хранятся списки фиксированной длины, массив с классами учителя в конце имеет несколько таких элементов: ['', '', '', '', ''], их стоит убрать
        people_data["fixed_classes"] = classes[:classes.index(['', '', '', '', ''])]

    return JsonResponse(people_data | {"character": [character, get_template(character + "_main.html")]})
