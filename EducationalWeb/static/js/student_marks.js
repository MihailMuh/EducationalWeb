import {arraySum, getTodayDate, str, round} from './base.js'
import {setSwal} from './base_schedule.js'
import {onMessage, post} from "./common.js"

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

function addTextIntoHtmlOfElem(value, text) {
    addHTML(value, `<td align="center" bgcolor="#ffffff"><i>${text}</i></td>`)
}

function addHTML(value, html) {
    if (typeof value === 'number') {
        value = document.getElementById(value)
    }
    value.insertAdjacentHTML("beforeend", html)
}

function getAverageScore(marks, weights) {
    if (!marks) return ""

    let sum = 0
    for (let i = 0; i < marks.length; i++) {
        sum += marks[i] * weights[i]
    }
    return round(sum / arraySum(weights), 3)
}

function setDaysAndMonths(jsonReport) {
    const hat = document.getElementById("hat")
    const tr = document.createElement("tr")
    const jsonMonths = {}
    hat.after(tr)

    for (let date in jsonReport) {
        // будет примерно ["2022", "06", "07"]
        date = date.split("-")
        const monthNumber = date[1]
        const dayNumber = date[2]

        // считаем, сколько колонок оценок в месяце будет занято
        if (!jsonMonths[monthNumber]) {
            jsonMonths[monthNumber] = 1
        } else {
            jsonMonths[monthNumber] += 1
        }

        // parseInt, чтобы 07 превратить в 7
        addHTML(tr, `<th bgcolor="#ffffff">${parseInt(dayNumber)}</th>`)
    }

    // создаем элемент, растягиваем его на подсчитанное количество колонок и подписываем месяц
    for (const month in jsonMonths) {
        addHTML(hat, `<th colspan="${jsonMonths[month]}" bgcolor="#ffffff"><i>${months[month]}</i></th>`)
    }
    addHTML(hat, `<td rowspan="2" bgcolor="#ffffff" align="center" width="100px"><i>Ср. балл</i></td>`)
}

function setSubjectsAndButtons(arrSubjects) {
    const table = document.getElementById("markTable")

    for (let i = 0; i < arrSubjects.length; i++) {
        const subject = arrSubjects[i]

        addHTML(table, `<tr id="${i}">
                                    <td align="center" bgcolor="#ffffff" width="10">
                                        <button class="button" style="width: 40px" id="${str("button-", i)}"></button>
                                    </td>
                                    <td bgcolor="#ffffff"><i>${subject}</i></td>
                                </tr>`)

        const subjectLine = document.getElementById(i)
        const button = document.getElementById(str("button-", i))
        button.onclick = () => {
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
    }
}

function setMarks(arrSubjects, jsonDays) {
    const numberSubjects = arrSubjects.length
    const average = {}
    const weights = {}

    for (const date in jsonDays) {
        const day = jsonDays[date]
        let settedMarks = []

        for (let i = 0; i < day.length; i++) {
            const infoAboutMark = day[i]
            const subject = infoAboutMark[1]
            const mark = infoAboutMark[0]
            const weight = infoAboutMark[2]
            const id = arrSubjects.indexOf(subject)

            // создаём примерно такой элемент <td align="center" bgcolor="#ffffff"><i>5</i></td>
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

        // создаём пустые клетки
        for (let i = 0; i < numberSubjects; i++) {
            if (settedMarks.indexOf(i) === -1) {
                addTextIntoHtmlOfElem(i, '')
            }
        }
    }

    // подсчитываем средние баллы
    for (let i = 0; i < numberSubjects; i++) {
        const subject = arrSubjects[i]
        addTextIntoHtmlOfElem(i, getAverageScore(average[subject], weights[subject]))
    }
}

function createReport(jsonReport) {
    const days = jsonReport["days"]
    const subjects = jsonReport["subjects"]

    setDaysAndMonths(days)
    setSubjectsAndButtons(subjects)
    setMarks(subjects, days)
}

export function runMarks() {
    function getMarks() {
        onMessage((json) => createReport(json))
        post({
            "url": "get_mark_report",
            "start_date": dateStart.value,
            "end_date": dateEnd.value
        })
    }

    const dateStart = document.getElementById("start")
    const dateEnd = document.getElementById("end")

    dateStart.value = "2022-01-10"
    dateEnd.value = getTodayDate()

    dateStart.addEventListener("input", getMarks)
    dateEnd.addEventListener("input", getMarks)
    getMarks()
}

const months = {
    "01": 'Январь',
    "02": 'Февраль',
    "03": 'Март',
    "04": 'Апрель',
    "05": 'Май',
    "06": 'Июнь',
    "07": 'Июль',
    "08": 'Август',
    "09": 'Сентябрь',
    "10": 'Октябрь',
    "11": 'Ноябрь',
    "12": 'Декабрь'
}
