import {str, toast} from "./base.js"
import {fixedClasses, onMessage, post} from "./common.js"

function getStudentsAndMarks(i = -1) {
    const studentsAndMarks = []

    while (true) {
        i += 1
        const markInput = document.getElementById("in" + i)
        if (!markInput) break

        const markValue = markInput.value
        if (!markValue) {
            // кладём ноль, чтобы бекенд понимал, что если у чела была пятерка, а стала ноль, значит, оценку просто убрали, и из бд её надо удалить
            studentsAndMarks.push([studentsNicks[i], 0])
            continue
        }

        if (markValue.length > 1 || !(/[2-5]/.test(markValue))) return null

        studentsAndMarks.push([studentsNicks[i], Number.parseInt(markValue)])
    }

    return studentsAndMarks
}

function postData(text, weight, date) {
    if (!text) {
        return toast("Некорректное название работы!", "error")
    }

    const studentsAndMarks = getStudentsAndMarks()
    if (!studentsAndMarks) {
        return toast("Некорректные оценки!", "error")
    }

    toast("Сохранено!", "success")

    post({
        "url": "post_marks",
        "marks": studentsAndMarks,
        "weight": weight,
        "theme": text,
        "date": date,
        "subject": currentSubject
    })
}

function deleteOldRowsWithStudents(i = 0) {
    while (true) {
        const tr = document.getElementById(str(i++))
        if (!tr) break

        tr.remove()
    }
}

function createStudentsTable(students) {
    const tr = document.getElementById("students")
    studentsNicks = []

    deleteOldRowsWithStudents()

    if (!students) return

    // Идем в обратном порядке, чтоб имена вывелись по возрастанию
    for (let i = students.length - 1; i >= 0; i--) {
        const student = students[i]
        studentsNicks.push(student["nickname"])

        tr.insertAdjacentHTML('afterend', `<tr id="${i}">
                                                            <td>
                                                                <i">${student["name"]}</i>
                                                            </td>
                                                            <td align="center">
                                                                <i">${student["grouping"]}</i>
                                                            </td>
                                                            <td align="center">
                                                                <label>
                                                                    <input type='text' size="1" id="in${i}" value="${str(student["mark"])}">
                                                                </label>
                                                            </td>
                                                        </tr>`)
    }

    // т.к. цикл был в обратном порядке, то ники в studentsNicks тоже в обратном порядке
    studentsNicks.reverse()
}

function removeAdditionalTeacherSubjectSelect() {
    const select = document.getElementById("trForSubjects")
    if (select) {
        select.remove()
        document.getElementById("textSubject").remove()
    }
}

function setSubjectsInSelect(subjects, getStudentsFromSocket) {
    removeAdditionalTeacherSubjectSelect()
    currentSubject = subjects[0]

    if (subjects.length <= 1) return

    let selectSubjects = document.getElementById("subject")
    if (selectSubjects) return setSubjectsInSelect(subjects, getStudentsFromSocket)

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
        getStudentsFromSocket()
    })
}

function setClassesInClassSelect() {
    let html = `<td id="classSelect"><label for="class"><select id="class">`
    for (let i = fixedClasses.length - 1; i >= 0; i--) {
        html += `<option>${fixedClasses[i][0]}</option>`
    }
    html += `</select></label></td>`
    document.getElementById("inputs").insertAdjacentHTML("afterbegin", html)
}

function getStudents(clazz, date, workTheme, markWeight) {
    onMessage((json) => {
        if (json["theme"]) {
            workTheme.value = json["theme"]
        } else {
            workTheme.value = ""
        }
        markWeight.value = json["weight"]

        createStudentsTable(json["students"])
    })
    post({
        "url": "get_students_and_marks",
        "class": clazz,
        "date": date,
        "subject": currentSubject
    })
}

let studentsNicks
let currentSubject

export function runGrading() {
    function getDate() {
        let yourDate = new Date()
        yourDate = new Date(yourDate.getTime() - (yourDate.getTimezoneOffset() * 60000))
        return yourDate.toISOString().split('T')[0]
    }

    function students() {
        getStudents(classSelect.value, dateInput.value, workName, markWeight)
    }

    function getNewStudentsAndSubjects() {
        const clazz = classSelect.value

        for (let i = 0; i < fixedClasses.length; i++) {
            if (fixedClasses[i][0] === clazz) {
                setSubjectsInSelect(fixedClasses[i].slice(1, fixedClasses[i].length), students)

                return students()
            }
        }
    }

    setClassesInClassSelect()

    const classSelect = document.getElementById("class")
    classSelect.addEventListener("input", getNewStudentsAndSubjects)

    const dateInput = document.querySelector('input[type="date"]')
    dateInput.value = getDate()
    dateInput.addEventListener("input", students)

    const workName = document.querySelector('input[type="text"]')
    const markWeight = document.getElementById("weight")

    document.getElementById("save").onclick = () => {
        postData(workName.value, markWeight.value, dateInput.value)
    }

    getNewStudentsAndSubjects()
}
