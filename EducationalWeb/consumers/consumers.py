import logging

from .db_queries import aget_student_schedule
from .server_utils import get_value_or_none, AsyncOrjsonWebsocketConsumer

logger = logging.getLogger("django")


class SessionConsumer(AsyncOrjsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nickname: str = ""
        self.school: str = ""
        self.character: str = ""
        self.clazz: str = ""
        self.grouping: str = ""
        self.fixed_classes: list = []

    async def receive_json(self, content: dict, **kwargs):
        match content["url"]:
            case "cash":
                if not self.nickname:
                    self.nickname = get_value_or_none(content, "nickname")
                    self.school = get_value_or_none(content, "school")
                    self.character = get_value_or_none(content, "character")
                    self.clazz = get_value_or_none(content, "clazz")
                    self.grouping = get_value_or_none(content, "grouping")
                    self.fixed_classes = get_value_or_none(content, "fixed_classes")

            case "get_student_schedule":
                await self.send_json(await aget_student_schedule(content["week"],
                                                                 self.nickname, self.school, self.clazz))

        # if self.nickname:
        #     return await self.send_json(self.people_data)
        #
        # nickname: str = content["nickname"]
        # password: str = content["password"]
        # school: str = content["school"]
        # character: str = "student"
        #
        # people: Peoples = await aget(Peoples, nickname=nickname, password=password, school=school)
        #
        # if not people:
        #     return await self.send_json(None)
        #
        # if people.is_student:
        #     student = await aget(Students, nickname=nickname)
        #     content |= {"class": student.clazz, "grouping": student.grouping}
        # else:
        #     teacher = await aget(Teachers, nickname=nickname)
        #     character = teacher.character
        #     content["fixed_classes"] = teacher.fixed_classes
        #
        # content["character"] = [character, get_template(character + "_main.html")]
        #
        # self.nickname = nickname
        # self.password = password
        # self.school = school
        # self.character = character
        # self.people_data = content
        #
        # await self.send_json(content)
