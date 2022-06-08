import {str} from "./base.js"
import {fixedClasses, onMessage, post, school} from "./common.js"

function getDate() {
    let yourDate = new Date()
    yourDate = new Date(yourDate.getTime() - (yourDate.getTimezoneOffset() * 60000))
    return yourDate.toISOString().split('T')[0]
}

function swal(title, icon) {
    Swal.fire({
        title: title,
        icon: icon,
        timer: 1500,
        showConfirmButton: false,
        toast: true,
        position: "top"
    })
}

function postData(text, weight, date) {
    const marksAndStudents = getMarksAndStudents()

    if (!marksAndStudents) {
        return swal("Некорректные оценки!", "error")
    }
    if (!text) {
        return swal("Некорректное название работы!", "error")
    }

    swal("Сохранено!", "success")

    post({
        "url": "post_marks",
        "marks": marksAndStudents,
        "weight": weight,
        "theme": text,
        "date": date,
        "subject": currentSubject
    })
}

function createStudentsTable(json) {
    const tr = document.getElementById("students")
    const students = json["students"]
    const marks = json["marks"]

    for (let i = 0; i < 666; i++) {
        let oldTr = document.getElementById(str(i))
        if (oldTr) {
            oldTr.remove()
        } else {
            break
        }
    }

    if (students) {
        for (let i = 0; i < students.length; i++) {
            studentsNicks.push(students[i][0])
            tr.insertAdjacentHTML('afterend', `<tr id="${i}">
                                                            <td>
                                                                <i">${students[i][1]}</i>
                                                            </td>
                                                            <td align="center">
                                                                <label>
                                                                    <input type='text' size="1" id="in${i}" value="${marks[i]}">
                                                                </label>
                                                            </td>
                                                        </tr>`)
        }
    }
}

function getMarksAndStudents() {
    const marks = []

    for (let i = 0; i < 666; i++) {
        const markInput = document.getElementById("in" + i)
        if (markInput) {
            const markValue = markInput.value
            if (markValue) {
                if (markValue.length === 1 && (/[2-5]/.test(markValue))) {
                    marks.push([studentsNicks[i], markValue])
                } else {
                    return null
                }
            } else {
                marks.push([studentsNicks[i], 0])
            }
        } else {
            return marks
        }
    }
}

function removeAdditionalTeacherSubjectSelect() {
    const select = document.getElementById("trForSubjects")
    if (select) {
        select.remove()
        document.getElementById("textSubject").remove()
    }
}

function setSubjectsInSelect(subjects, func) {
    removeAdditionalTeacherSubjectSelect()

    if (subjects.length > 1) {
        let selectSubjects = document.getElementById("subject")

        if (!selectSubjects) {
            document.getElementById("titles").insertAdjacentHTML("beforeend", `<td align="center" id="textSubject"><i>Предмет</i></td>`)

            let selectSubjectsHTML = `<td align="center" id="trForSubjects">
                                            <label for="subject">
                                                <select id="subject" style="width: 100%">`
            for (let i = 0; i < subjects.length; i++) {
                selectSubjectsHTML += `<option>${subjects[i]}</option>`
            }

            document.getElementById("inputs").insertAdjacentHTML("beforeend", selectSubjectsHTML + `</select></label></td>`)
            selectSubjects = document.getElementById("subject")
            selectSubjects.addEventListener("input", () => {
                currentSubject = selectSubjects.value
                func()
            })
        } else {
            setSubjectsInSelect(subjects, func)
        }
    }

    currentSubject = subjects[0]
}

function add_classes(teacher_list) {
    let selectClasses = document.getElementById("classSelect")
    if (selectClasses) {
        selectClasses.remove()
    }
    let html = `<td id="classSelect"><label for="class"><select id="class">`
    for (let i = teacher_list.length - 1; i >= 0; i--) {
        html += `<option>${teacher_list[i][0]}</option>`
    }
    html += `</select></label></td>`
    document.getElementById("inputs").insertAdjacentHTML("afterbegin", html)
    return document.getElementById("class")
}

function getStudents(clazz, school, date, workName, markWeight) {
    onMessage((json) => {
        console.log(json)
        if (json["theme"]) {
            workName.value = json["theme"]
            markWeight.value = json["weight"]
        } else {
            workName.value = ""
            markWeight.value = "6"
        }
        createStudentsTable(json)
    })
    post({
        "url": "get_students_and_marks",
        "class": clazz,
        "school": school,
        "date": date,
        "subject": currentSubject
    })
}

let studentsNicks
let currentSubject

export function runGrading() {
    function students(clazz) {
        getStudents(clazz, school, dateInput.value, workName, markWeight)
    }

    function getNewStudentsAndSubjects() {
        const clazz = classInput.value

        for (let i = 0; i < fixedClasses.length; i++) {
            if (fixedClasses[i][0] === clazz) {
                setSubjectsInSelect(fixedClasses[i].slice(1, fixedClasses[i].length), () => students(clazz))
                return students(clazz)
            }
        }
    }

    const classInput = add_classes(fixedClasses)
    const dateInput = document.querySelector('input[type="date"]')
    const workName = document.querySelector('input[type="text"]')
    const markWeight = document.getElementById("weight")

    document.getElementById("save").onclick = function () {
        postData(workName.value, markWeight.value, dateInput.value)
    }

    classInput.addEventListener("input", getNewStudentsAndSubjects)

    dateInput.value = getDate()
    dateInput.addEventListener("input", () => students(classInput.value))

    getNewStudentsAndSubjects()
}
