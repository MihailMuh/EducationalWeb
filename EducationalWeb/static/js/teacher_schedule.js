import {niceDate, str} from "./base.js"
import {setSwal} from './base_schedule.js'

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

    const buttonHomework = document.getElementById(str("button", i, j))
    if (buttonHomework) {
        buttonHomework.onclick = () => addHomeworkSwal(homework, clazz, i, j)
    }
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

function addHomeworkSwal(homework, clazz, dayId, subject_id) {
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
        preConfirm: () => {
            return xmlHttpRequest(clazz, document.getElementById("homeworkInputArea").value, dayId, subject_id)
                .then(function (text) {
                    getSchedule()
                    Swal.fire({
                        title: text,
                        icon: 'success',
                        timer: 1500,
                        showConfirmButton: false,
                        toast: true,
                        position: "top"
                    })
                }).catch(function (err) {
                    Swal.showValidationMessage(err)
                })
        },
        allowOutsideClick: () => !Swal.isLoading()
    })
}

const xmlHttpRequest = function (clazz, homework, dayId, subject_id) {
    return new Promise(function (resolve, reject) {
        const req = new XMLHttpRequest()
        req.open("POST", "post_homework", true)
        req.onload = function () {
            if (req.status === 200) {
                resolve("Сохранено!")
            } else {
                console.log(req.response)
                reject("Ошибка обращения к серверу!")
            }
        }
        req.send(JSON.stringify({
            "class": clazz,
            "homework": homework,
            "week": weekBox.value,
            "day_id": dayId,
            "subject_id": subject_id,
            "school": school
        }))
    })
}

function getSchedule() {
    const req = new XMLHttpRequest()
    req.open("POST", "get_teacher_schedule", true)
    req.onload = function () {
        if (req.status === 200) {
            createSchedule(JSON.parse(req.responseText), school, weekBox.value)
        } else {
            console.log(req.response)
        }
    }
    req.send(JSON.stringify({
        "fixed_classes": fixed_classes,
        "week": weekBox.value,
        "school": school
    }))
}

let school
let fixed_classes
let weekBox

export function runTeacherSchedule(Fixed_classes, School) {
    weekBox = document.querySelector('input[type="week"]')
    weekBox.value = niceDate(new Date())
    weekBox.addEventListener("input", getSchedule)

    school = School
    fixed_classes = Fixed_classes

    getSchedule()
}
