export function getWeekNumber(d) {
    // Copy date so don't modify original
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
    // Set to nearest Thursday: current date + 4 - current day number
    // Make Sunday's day number 7
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7))
    // Get first day of year
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
    // Calculate full weeks to nearest Thursday
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
    setFuncForButton(htmlPage, function () {
        const req = new XMLHttpRequest()
        req.open("POST", "html", true)
        req.onload = function () {
            if (req.status === 200) {
                return openPage(req.response, true)
            }
            console.log(req.response)
        }
        req.send(JSON.stringify({"html": htmlPage}))
    })
}

export function setFuncForButton(buttonName, func) {
    const button = document.getElementById(buttonName)
    if (button) {
        button.onclick = func
    }
}
