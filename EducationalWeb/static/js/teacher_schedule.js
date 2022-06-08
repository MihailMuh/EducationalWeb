import {niceDate, setFuncForButton, str, success1500} from "./base.js"
import {setSwal} from './base_schedule.js'
import {onError, onMessage, post} from "./common.js"

function createLessonContainer(id, clazz, subject, classroom, homework) {
    const lessonContainer = document.createElement("tr")
    lessonContainer.id = id
    lessonContainer.innerHTML = `<td class="row" align="center" id="${str('class', id)}">
                                    <div style="width: 30px"><i>${clazz}</i></div>
                                </td>
                                <td class="row" align="center" id="${str('classroom', id)}">
                                    <div class="container" style="width: 75px"><i>${classroom}</i></div>
                                </td>                   
                                <td class="row" id="${str('subject', id)}">
                                    <div class="container" style="width: 200px"><i>${subject}</i></div>
                                </td>          
                                <td class="row" id="${str('homework', id)}">
                                    <div class="container" style="width: 200px"><i>${homework}</i></div>
                                </td>`

    if (clazz) {
        lessonContainer.innerHTML += `<td class="row">
                                          <button class="button_add_task" id="${str("button", id)}"><i>Добавить дз</i></button>
                                      </td>`
    } else {
        lessonContainer.innerHTML += `<td class="row">
                                          <div class="container" style="width: 140px"></div>
                                      </td>`
    }
    return lessonContainer
}

function setSwals(i, j, clazz, subject, classroom, homework) {
    const html = `</br><b>Класс: </b> ${clazz}</br>
                      <b>Кабинет: </b> ${classroom.split(" ").pop()}</br>
                      <b>Задание: </b> ${homework}</br>`
    setSwal(document.getElementById(str('class', i, j)), subject, html)
    setSwal(document.getElementById(str('classroom', i, j)), subject, html)
    setSwal(document.getElementById(str('subject', i, j)), subject, html)
    setSwal(document.getElementById(str('homework', i, j)), subject, html)

    setFuncForButton(str("button", i, j), () => addHomeworkSwal(homework, clazz, i, j))
}

function createSchedule(schedule) {
    for (let i = 0; i < 6; i++) {
        const day = document.getElementById(str(i))

        for (let j = 0; j < 8; j++) {
            const lesson = schedule[i][j]
            const clazz = lesson[0]
            const subject = lesson[1]
            const homework = lesson[3]
            const id = str(i, j)

            const lessonLine = document.getElementById(str(i, j))
            if (lessonLine) {
                lessonLine.remove()
            }

            day.append(createLessonContainer(id, clazz, subject, lesson[2], homework))
            setSwals(i, j, clazz, subject, lesson[2], homework)
        }
    }
}

function addHomeworkSwal(homework, clazz, dayId, subjectId) {
    Swal.mixin({
        customClass: {
            confirmButton: 'button',
        },
        buttonsStyling: false
    }).fire({
        title: "Домашнее задание",
        html: `<br><textarea class="homeworkInputArea" id="homeworkInputArea">${homework}</textarea>`,
        confirmButtonText: '<i>Сохранить</i>',
        showLoaderOnConfirm: true,
        backdrop: true,
        preConfirm: () => {
            const newHomework = document.getElementById("homeworkInputArea").value
            if (homework === newHomework) {
                return success1500("Сохранено!")
            }
            return postHomework(clazz, newHomework, dayId, subjectId)
                .then(() => {
                    success1500("Сохранено!")
                    updateTeacherSchedule()
                }).catch(message => Swal.showValidationMessage(message))
        },
        allowOutsideClick: () => !Swal.isLoading()
    })
}

const postHomework = (clazz, homework, dayId, subjectId) => {
    return new Promise((resolve, reject) => {
        onMessage(resolve)
        onError((event) => {
            console.log(event)
            reject("Попробуйте позже!")
        })

        post({
            "url": "post_homework",
            "class": clazz,
            "homework": homework,
            "week": weekBox.value,
            "day_id": dayId,
            "subject_id": subjectId
        })
    })
}

let weekBox

function updateTeacherSchedule() {
    onMessage(createSchedule)
    post({
        "url": "get_teacher_schedule",
        "week": weekBox.value
    })
}

export function runTeacherScheduleScript() {
    weekBox = document.querySelector('input[type="week"]')
    weekBox.value = niceDate(new Date())
    weekBox.addEventListener("input", updateTeacherSchedule)

    updateTeacherSchedule()
}
