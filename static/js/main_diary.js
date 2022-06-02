import {setResponseForButton, setFuncForButton} from './base.js'
import {runSchedule} from "./schedule.js"
import {runScheduling} from "./admin_scheduling.js"
import {runGrading} from "./grading.js"
import {runMarks} from "./student_marks.js"
import {runTeacherSchedule} from "./teacher_schedule.js"

const mainTable = document.getElementById("table")
const json = JSON.parse(sessionStorage.getItem("user"))

if (!json) {
    window.location.href = "/"
}
const school = json["school"]
const nickname = json["nickname"]
const character = json["character"]

const clazz = json["class"]
const grouping = json["grouping"]

const fixed_classes = json["fixed_classes"]

function newPage(html) {
    let newTable = document.getElementById("optional_table")
    if (newTable) {
        newTable.remove()
    }

    newTable = document.createElement("table")
    newTable.id = "optional_table"
    newTable.className = "table"
    newTable.innerHTML = html
    mainTable.after(newTable)

    return newTable
}

function page(html, needHistory) {
    if (needHistory) {
        history.pushState(html, document.title, location.href)
    } else {
        history.replaceState(html, document.title, location.href)
    }

    newPage(html)

    setResponseForButton("ads", page)
    setFuncForButton("back", () => history.back())

    setResponseForButton("student_marks", page)
    setResponseForButton("student_schedule", page)

    setResponseForButton("admin_scheduling", page)
    setResponseForButton("teacher_diary", page)
    setResponseForButton("teacher_grading", page)

    const studentSchedule = document.getElementById("studentSchedule")
    if (studentSchedule) {
        return runSchedule(clazz, school, nickname, grouping)
    }

    const adminScheduling = document.getElementById("adminScheduling")
    if (adminScheduling) {
        return runScheduling(school)
    }

    const markWeight = document.getElementById("weight")
    if (markWeight) {
        return runGrading(school, fixed_classes)
    }

    const tableMarkReport = document.getElementById("markTable")
    if (tableMarkReport) {
        return runMarks(nickname, clazz, school)
    }

    const teacherTable = document.getElementById("teacherTable")
    if (teacherTable) {
        return runTeacherSchedule(fixed_classes, school)
    }
}

window.addEventListener('popstate', function (event) {
    page(event.state, false)
})

let pageToShow
if (history.state) {
    pageToShow = history.state
} else {
    pageToShow = character[1]
}

page(pageToShow, false)
