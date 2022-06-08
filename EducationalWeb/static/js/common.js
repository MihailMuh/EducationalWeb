const json = JSON.parse(sessionStorage.getItem("user"))

if (!json) {
    window.location.href = "/"
}

export const school = json["school"]
export const nickname = json["nickname"]
export const character = json["character"][0]
export const mainPage = json["character"][1]

export const clazz = json["class"]
export const grouping = json["grouping"]

export const fixedClasses = json["fixed_classes"]

function startWebSocket() {
    sessionSocket = new WebSocket(`ws://${window.location.host}/diary`)

    sessionSocket.onopen = () => {
        post({
            "url": "cash",
            "nickname": nickname,
            "school": school,
            "character": character,
            "class": clazz,
            "grouping": grouping,
            "fixed_classes": fixedClasses
        })
    }

    sessionSocket.onclose = () => {
        setTimeout(startWebSocket, 5000)
    }
    sessionSocket.onerror = (event) => {
        console.log(event)
    }
}

export function disconnect() {
    return sessionSocket.readyState !== WebSocket.OPEN
}

export function post(json) {
    if (disconnect()) {
        return setTimeout(() => {
            post(json)
        }, 500)
    }

    sessionSocket.send(JSON.stringify(json))
}

export function onMessage(func) {
    async function removeAfterComplete(event) {
        func(JSON.parse(await event.data.text()))
        sessionSocket.removeEventListener('message', removeAfterComplete)
    }

    sessionSocket.addEventListener('message', removeAfterComplete)
}

export function onError(func) {
    function removeAfterComplete(event) {
        func(event)
        sessionSocket.removeEventListener('error', removeAfterComplete)
    }

    sessionSocket.addEventListener('error', removeAfterComplete)
}

export let sessionSocket

startWebSocket()
