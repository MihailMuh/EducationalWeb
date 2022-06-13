import {niceDate, str} from './base.js'
import {setSwal} from './base_schedule.js'
import {grouping, onMessage, post} from "./common.js"

function getSubject(subject, homework, mark, id) {
    let html = ""
    const tr = document.createElement('tr')
    tr.id = id

    if (homework) {
        html += `<b>Задание: </b> ${homework}</br>`
    }
    if (mark[0]) {
        html += `<br><b>Оценка: </b> ${mark[0]}</br>
                     <b>Тип работы: </b> ${mark[2]}</br>
                     <b>Вес: </b> ${mark[1]}</br>`
    }

    tr.insertAdjacentHTML("afterbegin", `<td class="row">
                                                        <div class="container" style="width: 150px"><i>${subject}</i></div>
                                                      </td>
                                                      <td class="row">
                                                        <div class="container" style="width: 250px"><i>${homework}</i></div>
                                                      </td>
                                                      <td class="row" align="center">
                                                        <div class="container" style="width: 35px"><i>${mark[0]}</i></div>
                                                      </td>`)

    if (subject) setSwal(tr, subject, html)
    return tr
}

function getSubjectByGroup(unfilterSubject) {
    // ['Английский язык эк. (каб. 27)', 'Химия ест.']
    const subjects = unfilterSubject.split("/")

    for (let i = 0; i < subjects.length; i++) {
        const subject = subjects[i]
        const index = subject.indexOf(grouping)
        if (index === -1) continue

        // пытаемся выковорить кабинет, если он есть
        const classroom = getClassroom(subject)

        // если из index не вычитать 1, будем захватывать лишний пробел
        return subject.slice(0, index - 1) + classroom
    }
}

function getClassroom(subject) {
    // ['Английский язык эк. ', 'каб. 27)']
    const data = subject.split("(")

    // после split строка не разбилась, сл-но кабинета там нет
    if (data.length === 1) return ""

    // добавляем пробел, чтобы при конкатенации с предметом строки не слиплись
    return " (" + data[1]
}

function addBlankSubject(i, j) {
    document.getElementById(str(i)).append(getSubject("", "", [""], str(i, j)))
}

function createSchedule(schedule, marks) {
    for (let i = 0; i < 6; i++) {
        for (let j = 0; j < 8; j++) {
            const old = document.getElementById(str(i, j))
            if (old) {
                old.remove()
            }

            let subject = schedule[i][j][0]
            let homework = schedule[i][j][1]
            let mark = [""]

            // Проверяем есть ли строка с группой: 'Английский язык эк. (каб. 27)/Химия ест.' и выковыриваем предмет, если ученик в этой группе
            if (subject.indexOf("/") !== -1) {
                const clearSubject = getSubjectByGroup(subject)
                subject = clearSubject

                if (!clearSubject) {
                    addBlankSubject(i, j)
                    continue
                }
            }

            // ищем оценку для текущего предмета
            for (let k = 0; k < marks[i].length; k++) {
                // каждый k - примерно такой массив [2, 10, 'ЕГЭ', 'Информатика']
                if (subject === marks[i][k][3]) {
                    mark = marks[i][k]

                    // удаляем найденный массив, т.к. больше не понадобится
                    marks[i].splice(k, 1)
                    break
                }
            }

            document.getElementById(str(i)).append(getSubject(subject, homework, mark, str(i, j)))
        }
    }
}

export function runSchedule() {
    const weekNumber = document.querySelector('input[type="week"]')
    weekNumber.value = niceDate(new Date())

    function schedule() {
        onMessage((json) => {
            const schedule = json["schedule"]
            const marks = json["marks"]

            createSchedule(schedule, marks)
        })

        post({
            "url": "get_student_schedule",
            "week": weekNumber.value
        })
    }

    schedule()
    weekNumber.addEventListener("input", schedule)
}
