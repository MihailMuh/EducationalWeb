import {arraySum, str} from './base.js'
import {setSwal} from './base_schedule.js'

function getMarkContainer(value, subject, theme, weight) {
    const td = document.createElement("td")
    const html = `<b>Тип работы: </b> ${theme}</br>
                    <b>Предмет: </b> ${subject}</br>
                    <b>Вес: </b> ${weight}</br>`

    td.align = "center"
    td.bgColor = "#ffffff"
    td.innerHTML = `<i>${value}</i>`
    setSwal(td, value, html)
    return td
}

function addTextIntoHTML(value, text) {
    addHTML(value, `<td align="center" bgcolor="#ffffff"><i>${text}</i></td>`)
}

function addHTML(value, html) {
    if (typeof value === 'number') {
        value = document.getElementById(value)
    }
    value.insertAdjacentHTML("beforeend", html)
}

function getAverageScore(marks, weights) {
    if (marks) {
        let sum = 0
        for (let i = 0; i < marks.length; i++) {
            sum += marks[i] * weights[i]
        }
        return (sum / arraySum(weights)).toFixed(2)
    }
    return ""
}

function setDays(hat, jsonReport) {
    const tr = document.createElement("tr")
    const json_months = {}
    hat.after(tr)

    for (let date in jsonReport) {
        date = date.split("-")
        const month_num = date[1]

        if (!json_months[month_num]) {
            json_months[month_num] = 1
        } else {
            json_months[month_num] += 1
        }

        addHTML(tr, `<th bgcolor="#ffffff">${parseInt(date[2])}</th>`)
    }

    for (const month in json_months) {
        addHTML(hat, `<th colspan="${json_months[month]}" bgcolor="#ffffff"><i>${months[month]}</i></th>`)
    }
    addHTML(hat, `<td rowspan="2" bgcolor="#ffffff" align="center" width="100px"><i>Ср. балл</i></td>`)
}

function setSubjects(table, arrSubjects) {
    const subjects = {}
    let id = 0

    for (let i = 0; i < arrSubjects.length; i++) {
        const subject = arrSubjects[i]

        if (!subjects[subject]) {
            addHTML(table, `<tr id="${id}">
                                    <td align="center" bgcolor="#ffffff" width="10">
                                        <button class="button" style="width: 40px" id="${str("button-", id)}"></button>
                                    </td>
                                    <td bgcolor="#ffffff"><i>${subject}</i></td>
                                </tr>`)

            const subjectLine = document.getElementById(id)
            const button = document.getElementById(str("button-", id))
            button.onclick = function () {
                const containers = subjectLine.querySelectorAll("td")

                if (containers[0].style.background !== 'rgb(249, 242, 220)') {
                    button.style.background = '#B7A295'
                    for (let j = 0; j < containers.length; j++) {
                        containers[j].style.background = '#F9F2DC'
                    }
                } else {
                    button.style.background = '#F9F2DC'
                    for (let j = 0; j < containers.length; j++) {
                        containers[j].style.background = '#ffffff'
                    }
                }
            }

            subjects[subject] = id++
        }
    }

    return subjects
}

function setMarks(jsonReport, subjects) {
    const arr_subjects = jsonReport["subjects"]
    const num_subjects = arr_subjects.length
    const days = jsonReport["days"]
    const average = {}
    const weights = {}

    for (const date in days) {
        const day = days[date]
        let settedMarks = []

        for (let i = 0; i < day.length; i++) {
            const infoAboutMark = day[i]
            const subject = infoAboutMark[1]
            const mark = infoAboutMark[0]
            const weight = infoAboutMark[2]
            const id = arr_subjects.indexOf(subject)

            document.getElementById(id).append(getMarkContainer(mark, subject, infoAboutMark[3], weight))
            settedMarks.push(id)

            if (average[subject]) {
                average[subject].push(mark)
                weights[subject].push(weight)
            } else {
                average[subject] = [mark]
                weights[subject] = [weight]
            }
        }

        for (let i = 0; i < num_subjects; i++) {
            if (settedMarks.indexOf(i) === -1) {
                addTextIntoHTML(subjects[arr_subjects[i]], '')
            }
        }
    }
    for (let i = 0; i < num_subjects; i++) {
        const subject = arr_subjects[i]
        addTextIntoHTML(subjects[subject], getAverageScore(average[subject], weights[subject]))
    }
}

function createReport(jsonReport) {
    const table = document.getElementById("markTable")
    table.innerHTML = `<tr id="hat">
                            <td rowspan="2" bgcolor="#ffffff"><i>Выделить</i></td>
                            <th rowspan="2" bgcolor="#ffffff"><i>Предмет</i></th>
                        <tr>`

    setDays(document.getElementById("hat"), jsonReport["days"])
    setMarks(jsonReport, setSubjects(table, jsonReport["subjects"]))
}

function getReport(dateStart, dateEnd, nickname, clazz, school) {
    req.open("POST", "get_mark_report", true)
    req.onload = function () {
        if (req.status === 200) {
            createReport(JSON.parse(req.responseText))
        } else {
            console.log(req.response)
        }
    }
    req.send(JSON.stringify({
        "nickname": nickname,
        "class": clazz,
        "school": school,
        "start_date": dateStart,
        "end_date": dateEnd
    }))
}

const req = new XMLHttpRequest()
const months = {
    "01": 'Январь', "02": 'Февраль', "03": 'Март', "04": 'Апрель', "05": 'Май',
    "06": 'Июнь', "07": 'Июль', "08": 'Август', "09": 'Сентябрь',
    "10": 'Октябрь', "11": 'Ноябрь', "12": 'Декабрь'
}

export function runMarks(nickname, clazz, school) {
    function getMarks() {
        getReport(dateStart.value, dateEnd.value, nickname, clazz, school)
    }

    const dateStart = document.getElementById("start")
    const dateEnd = document.getElementById("end")

    dateStart.value = "2022-01-10"
    dateEnd.value = "2022-05-30"

    dateStart.addEventListener("input", getMarks)
    dateEnd.addEventListener("input", getMarks)
    getMarks()
}
