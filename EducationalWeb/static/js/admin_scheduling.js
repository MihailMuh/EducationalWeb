import {niceDate, str, success1500} from './base.js'
import {onMessage, post} from "./common.js"

function getSubjectContainer(subject, id) {
    const tr = document.createElement('tr')
    tr.id = id
    tr.innerHTML = `<th style="border: #F9F2DC"><input type="text" value="${subject}"></th>`
    return tr
}

function createSchedule(schedule) {
    for (let i = 0; i <= 5; i++) {
        for (let j = 0; j < 8; j++) {
            const old = document.getElementById(str(i, j))
            if (old) {
                old.remove()
            }

            const subject = schedule[i][j][0]
            document.getElementById(str(i)).append(getSubjectContainer(subject, str(i, j)))
        }
    }
}

export function runScheduling() {
    function schedule() {
        onMessage(createSchedule)

        post({
            "url": "get_schedule",
            "class": classSelect.value,
            "week": weekNumber.value
        })
    }

    const inputs = document.getElementsByTagName("input")
    const classSelect = document.getElementById("class")
    const weekNumber = document.querySelector('input[type="week"]')
    weekNumber.value = niceDate(new Date())

    schedule()
    weekNumber.addEventListener("input", schedule)
    classSelect.addEventListener("input", schedule)

    document.getElementById("change").onclick = () => {
        const schedule = [[], [], [], [], [], []]
        let numSubj = 0
        let day = 0

        for (let i = 1; i < inputs.length; i++) {
            schedule[day][numSubj] = inputs[i].value

            numSubj += 1
            if (numSubj === 8) {
                day += 1
                numSubj = 0
            }
        }

        onMessage(() => success1500("Сохранено!"))

        post({
            "url": "post_schedule",
            "schedule": [schedule[0], schedule[2], schedule[4], schedule[1], schedule[3], schedule[5]],
            "class": classSelect.value,
            "week": weekNumber.value
        })
    }
}
