export function setSwal(element, title, html) {
    element.onclick = () => {
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