import {setFuncForButton, setResponseForButton} from './base.js'
import {runSchedule} from "./schedule.js"
import {mainPage} from "./common.js"
import {runScheduling} from "./admin_scheduling.js"
import {runTeacherScheduleScript} from "./teacher_schedule.js"
import {runGrading} from "./grading.js"
import {runMarks} from "./student_marks.js"

const mainTable = document.getElementById("table")

let resizeObserver = new ResizeObserver(() => {
})

function renderNewPage(html) {
    let newTable = document.getElementById("optional_table")
    if (newTable) {
        newTable.remove()
    }

    newTable = document.createElement("table")
    newTable.id = "optional_table"
    newTable.className = "table"
    newTable.innerHTML = html
    mainTable.after(newTable)

    resizeObserver.disconnect()
    resizeObserver = new ResizeObserver(() => mainTable.style.width = newTable.offsetWidth + 'px')
    resizeObserver.observe(newTable)

    return newTable
}

function page(html, needHistory) {
    if (needHistory) {
        history.pushState(html, document.title, location.href)
    } else {
        history.replaceState(html, document.title, location.href)
    }

    renderNewPage(html)

    setResponseForButton("ads", page)
    setFuncForButton("back", () => history.back())

    setResponseForButton("student_marks", page)
    setResponseForButton("student_schedule", page)

    setResponseForButton("admin_scheduling", page)
    setResponseForButton("teacher_diary", page)
    setResponseForButton("teacher_grading", page)

    if (document.getElementById("studentSchedule")) {
        return runSchedule()
    }

    if (document.getElementById("adminScheduling")) {
        return runScheduling()
    }

    if (document.getElementById("weight")) {
        return runGrading()
    }

    if (document.getElementById("markTable")) {
        return runMarks()
    }

    if (document.getElementById("teacherTable")) {
        return runTeacherScheduleScript()
    }
}

window.addEventListener('popstate', (event) => {
    page(event.state, false)
})

if (history.state) {
    page(history.state, false)
} else {
    page(mainPage, false)
}
