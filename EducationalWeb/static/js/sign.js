import {post} from "./base.js"

const nickname = document.getElementById("surname")
const password = document.getElementById("password")
const school = document.getElementById("schools")

function errorToast(text) {
    Swal.fire({
        title: text,
        icon: 'error',
        timer: 2700,
        showConfirmButton: false,
        toast: true,
        position: "top"
    })
}

document.getElementById("enter_button").onclick = function () {
    if (!nickname.value) {
        return errorToast("Введите логин!")
    }
    if (!password.value) {
        return errorToast("Введите пароль!")
    }

    const json = {"school": school.value, "nickname": nickname.value, "password": password.value}

    post("enter", json, (xhr) => {
        switch (xhr.status) {
            case 200:
                sessionStorage.setItem("user", xhr.responseText)
                window.location.href = "diary"
                return
            case 404:
                console.log(xhr.response)
                return errorToast("Неверные введённые данные!")
            case 405:
                return errorToast("Неверный ПАРОЛЬ!")
        }
    })
}

sessionStorage.clear()
