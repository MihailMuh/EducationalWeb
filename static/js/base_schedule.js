const req = new XMLHttpRequest()

export function getSchedule(date, clazz, school, func) {
    const argument = arguments[arguments.length - 1]

    req.open("POST", "get_schedule", true)
    req.onload = function () {
        if (req.status === 200) {
            func(JSON.parse(req.responseText), argument)
        } else {
            console.log(req.response)
        }
    }
    req.send(JSON.stringify({
        "class": clazz,
        "school": school,
        "week": date
    }))
}

export function setSwal(element, title, html) {
    element.onclick = function () {
        Swal.mixin({
            customClass: {
                cancelButton: 'button'
            },
            buttonsStyling: false
        }).fire({
            titleText: title,
            html: html,
            showCancelButton: true,
            showConfirmButton: false,
            cancelButtonText: '<i>Закрыть</i>',
            icon: 'info',
            timer: 3500,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        })
        Swal.stopTimer()
    }
}