from .db_queries import get_student_schedule, get_schedule, save_schedule, \
    get_teacher_schedule, post_homework, get_students_and_marks, post_marks, get_mark_report
from .server_utils import get_value_or_none
from ..async_utils import AsyncOrjsonWebsocketConsumer


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
                    self.clazz = get_value_or_none(content, "class")
                    self.grouping = get_value_or_none(content, "grouping")
                    self.fixed_classes = get_value_or_none(content, "fixed_classes")

            case "get_student_schedule":
                await self.send_json(await get_student_schedule(content["week"],
                                                                self.nickname, self.school, self.clazz))
            case "get_schedule":
                await self.send_json(await get_schedule(self.school, content["class"], content["week"]))

            case "post_schedule":
                await self.send_json(await save_schedule(self.school, content["class"], content["week"],
                                                         tuple(map(tuple, content["schedule"]))))

            case "get_teacher_schedule":
                await self.send_json(await get_teacher_schedule(content["week"], self.fixed_classes, self.school))

            case "post_homework":
                await self.send_json(await post_homework(content["class"], self.school, content["week"],
                                                         content["day_id"], content["subject_id"], content["homework"]))

            case "get_students_and_marks":
                await self.send_json(await get_students_and_marks(content["class"], self.school,
                                                                  content["date"], content["subject"]))

            case "post_marks":
                await self.send_json(await post_marks(content["marks"], content["date"], content["theme"],
                                                      content["weight"], content["subject"]))

            case "get_mark_report":
                await self.send_json(await get_mark_report(self.nickname, self.clazz, self.school,
                                                           content["start_date"], content["end_date"]))
