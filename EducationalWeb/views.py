import logging

import orjson
from channels.http import AsgiRequest
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from EducationalWeb.models import Peoples, Students, Teachers
from EducationalWeb.shortcuts import aget_object_or_404, aget, get_template

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

    people: Peoples = await aget_object_or_404(Peoples, nickname=nickname, school=school)

    if not check_password(password, people.password):
        return HttpResponse(status=405)

    if people.is_student:
        student = await aget(Students, nickname=nickname)
        people_data |= {"class": student.clazz, "grouping": student.grouping}
    else:
        teacher = await aget(Teachers, nickname=nickname)
        character = teacher.character
        people_data["fixed_classes"] = teacher.fixed_classes

    return JsonResponse(people_data | {"character": [character, get_template(character + "_main.html")]})
