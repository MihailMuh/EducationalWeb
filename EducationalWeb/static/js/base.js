export function getWeekNumber(d) {
    // Copy date so don't modify original
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
    // Set to the nearest Thursday: current date + 4 - current day number
    // Make Sunday's day number 7
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7))
    // Get first day of year
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
    // Calculate full weeks to the nearest Thursday
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
}

export function niceDate(d) {
    let weekNo = getWeekNumber(d)
    if (weekNo < 10) {
        weekNo = str(0, weekNo)
    }
    return str(d.getFullYear(), "-W", weekNo)
}

export function str() {
    let string = ""
    for (let i = 0; i < arguments.length; i++) {
        string += arguments[i]
    }
    return string
}

export function arraySum(array) {
    let sum = 0
    for (let i = 0; i < array.length; i++) {
        sum += array[i]
    }
    return sum
}

export function setResponseForButton(htmlPage, openPage) {
    setFuncForButton(htmlPage, () => {
        post("html", {"html": htmlPage}, (xhr) => {
            if (xhr.status === 200) {
                return openPage(xhr.response, true)
            }
            console.log(xhr.response)
        })
    })
}

export function setFuncForButton(buttonName, func) {
    const button = document.getElementById(buttonName)
    if (button) {
        button.onclick = func
    }
}

export function getCsrfToken() {
    return document.cookie.match(/csrftoken=([\w-]+)/)[1]
}

export function post(url, json, onloadFunc) {
    xhr.open("POST", url, true)
    xhr.setRequestHeader("X-CSRFToken", getCsrfToken())
    xhr.setRequestHeader("Content-Type", "application/json");
    // Use "application/x-www-form-urlencoded" to get json from request.POST

    xhr.onload = () => {
        onloadFunc(xhr)
    }

    xhr.send(JSON.stringify(json))
}

const xhr = new XMLHttpRequest()
