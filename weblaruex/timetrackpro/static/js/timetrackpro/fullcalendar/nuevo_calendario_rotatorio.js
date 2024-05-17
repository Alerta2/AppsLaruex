var ColoresPersonal = undefined;
$(function () {
    $.ajax({ //obtengo un listado que identifica a cada usuario dado de alta en el calendario de guardias con un color aleatorio
        type: 'get',
        url: "../../../../private/calendario/guardias/datos/colores/personal/?a=" + area[0].id_area,
        dataType: "json",
        cache: false,
        success: function (data) {
            ColoresPersonal = data
        }
    })
})

var fechaLimitStart = moment().isoWeekYear(year).isoWeek(1).startOf('week').format('YYYY-MM-DD');
var fechaLimitEnd = moment().isoWeekYear(year).isoWeek(52).endOf('week').add(1, 'days').format('YYYY-MM-DD');
var calendar = undefined;

$(function () {

    var calendarEl = document.getElementById('calendar');

    calendar = new FullCalendar.Calendar(calendarEl, {
        schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
        locale: 'es',
        timeZone: 'Europe/Madrid',
        initialView: 'vistaYear',
        fixedWeekCount: false,
        weekNumbers: true,
        displayEventTime: false,
        editable: true,
        eventDurationEditable: true,
        eventResizableFromStart: true,
        weekNumberFormat: {
            week: 'numeric',
        },
        validRange: {
            start: fechaLimitStart,
            end: fechaLimitEnd
        },
        views: {
            vistaYear: {
                type: 'dayGrid',
                duration: { year: 1 },
                buttonText: 'Año'
            }
        },
        headerToolbar: {
            left: '',
            center: 'title',
            right: ''
        },
        footerToolbar: {
            right: "validarCalendario",
        },
        eventSources: [
            // Evento que carga los dias festivos y los representa en color verde
            {
                url: "../../../../private/calendario/guardias/datos/festivos/?y=" + year,
                method: 'get',
                failure: function () {
                    createAlert(' Opps! ...', 'Días Festivos, ' + year, 'Se ha producido un error al consultar los días festivos para el año <b>' + year + '</b> en la base de datos, por lo que no serán mostrados en el calendario.', 'danger', true, false, 'pageMessages')
                },
                display: 'background',
                color: '#00FF7F',
                textColor: 'white'
            }
        ],
        eventDataTransform: function (arg) {
            if (arg.group == 'guardias') {
                const color = ColoresPersonal.filter(function (element) {
                    return element.idUser == arg.idUser;
                });
                if (color.length > 0) {
                    arg.backgroundColor = color[0].color;
                }
            }
        },
        eventResize: function (info) {
            $(".tooltip").css('visibility', 'hidden');
        },
        dayCellClassNames: function (arg) {
            if (arg.date.getMonth() % 2 == 0) {
                return ['mespar']
            } else {
                return ['mesimpar']
            }
        },
        dayCellContent: function (e) {
            if (calendar.view.type == 'vistaYear') {
                if (e.dayNumberText == "1") {
                    e.dayNumberText = e.dayNumberText.replace('1', moment(e.date).format('MMM').toUpperCase() + " 1");
                }
            }
        },
        eventDidMount: function (info) {
            if (info.event.extendedProps.group == "guardias") {
                var tooltip = new Tooltip(info.el, {
                    title: '<img src="' + info.event.extendedProps.avatar + '" alt="" style="width:70px; height:70px; border-radius:50%; object-fit: cover;"/><br>' + info.event.extendedProps.nameUser,
                    html: true,
                    placement: 'top',
                    trigger: 'hover',
                    container: 'body'
                });
            }
            else {
                var tooltip = new Tooltip(info.el, {
                    title: info.event.title,
                    placement: 'top',
                    trigger: 'hover',
                    container: 'body'
                });
            }
        },

        eventContent: function (info) { //Cambio el texto que se muestra en el evento por ICONO AREA + NOMBRE ANALISTA
            switch (info.event.extendedProps.group) {
                case 'guardias':
                    return {
                        html: '&nbsp<i class="' + area[0].icono + '"></i>&nbsp<img src="' + info.event.extendedProps.avatar + '" alt="" style="width:20px; height:20px; border-radius:50%; object-fit: cover;"/>&nbsp' + info.event.extendedProps.nameUser
                    };
                default:
                    return {
                        html: ''
                    }
            }
        },
        dateClick: function (info) { //Permito añadir una nueva guardia haciendo click sobre la fecha de interés
            Swal.fire({
                title: 'Añadir guardia',
                icon: 'question',
                html: '<p>¿Estás seguro de que deseas añadir una nueva guardia para el calendario <b>' + year + '</b> perteneciente al área de <b><i class="' + area[0].icono + '"></i> ' + area[0].nombre + '</b>?</p>',
                showCancelButton: true,
                cancelButtonColor: '#d33',
                confirmButtonText: 'Aceptar',
                cancelButtonText: 'Cancelar',
                reverseButtons: true
            }).then((result) => {
                if (result.isConfirmed) {
                    AddGuardia(info);
                }
            })
        },
        eventClick: function (info) { //Permito eliminar una guardia al hacer click sobre una guardia
            if (info.event.extendedProps.group == "guardias") {
                eventDelete = info.event

                Swal.fire({
                    html: '<img src="' + eventDelete.extendedProps.avatar + '" alt="" style="width:100px; height:100px; border-radius:50%; object-fit: cover;margin-bottom:10px"/>' +
                        '<h3><b>' + eventDelete.extendedProps.nameUser + '</b></h3>' +
                        'Analista de guardia' +
                        ' desde el ' + moment(eventDelete.start).format('dddd, ll') +
                        ' hasta el ' + moment(eventDelete.end).add(-1, 'days').format('dddd, ll') +
                        ' en el área de <b><i class="' + area[0].icono + '"></i>&nbsp' + area[0].nombre + '</b>' +
                        "<br>" +
                        '<button type="button" role="button" tabindex="0" class="btnDeleteGuardia customSwalBtn">Eliminar</button><br>',
                    showConfirmButton: false,
                    timer: 100000,
                    timerProgressBar: true,
                    didOpen: (toast) => {
                        toast.addEventListener('mouseenter', Swal.stopTimer)
                        toast.addEventListener('mouseleave', Swal.resumeTimer)
                    }
                })
            }
        },
        customButtons: {
            validarCalendario: { //Botón para Validar y hacer por tanto público el Calendario generado despues de realizar los cambios oportunos
                text: 'Validar Calendario',
                click: function () {
                    showPreloaderAlerta2();
                    var answ = ValidarDiasCalendario(); //En primer lugar valido el contenido del calendario
                    if (answ) { //Si el calendario esta bien hecho...
                        createAlert('', ' Calendario ' + year + ', ' + area[0].nombre, ' El Calendario de guardias ha sido validado.', 'success', true, true, 'pageMessages');
                        createAlert(' Mensaje informativo', 'Generando Calendario de Guardias ' + year + ', ' + area[0].nombre + '...', 'No abandone la página hasta que el proceso no haya terminado.', 'info', true, true, 'pageMessages');
                        setTimeout(function () {

                            // Finalmente obtengo el JSON todas las guardias contenidas en el calendario para registrarlas en la base de datos
                            // El formato de datos es...
                            //1. Id del Usuario/Analista
                            //2. Fecha local comienzo de la guardia
                            //3. Fecha local fin de la guardia
                            var guardias = calendar.getEvents()
                            guardias = guardias.filter(function (item) {
                                return item.extendedProps.group == "guardias";
                            })
                            var jsonGuardias = (JSON.parse(JSON.stringify(guardias))).map((element) => ({
                                id_user_analista: element.extendedProps.idUser,
                                fecha_local_start: element.start,
                                fecha_local_end: element.end
                            }))

                            $.ajax({
                                type: 'get',
                                url: "../../../../private/calendario/guardias/nuevo/upd/calendario/rotatorio/?g=" + JSON.stringify(jsonGuardias) + "&y=" + year + "&t=" + turno + "&a=" + area[0].id_area,
                                dataType: "json",
                                cache: false,
                                success: function (data) {
                                    Swal.fire({
                                        title: data.title,
                                        text: data.text,
                                        icon: data.icon,
                                        timer: 10000,
                                        timerProgressBar: true,
                                        willClose: () => {
                                            if (data.icon == 'success') {
                                                Swal.fire({
                                                    title: '',
                                                    icon: 'question',
                                                    html: '<p>¿Deseas notificar a los analistas la generación del nuevo calendario de guardias para el año <b>' + year + '</b> perteneciente al área de <b><i class="' + area[0].icono + '"></i> ' + area[0].nombre + '</b>?</p>',
                                                    showCancelButton: true,
                                                    cancelButtonColor: '#d33',
                                                    confirmButtonText: 'Si',
                                                    cancelButtonText: 'No',
                                                    reverseButtons: true
                                                }).then((result) => {
                                                    if (result.isConfirmed) {
                                                        text_mensaje = 'Ya se encuentra disponible el nuevo calendario de guardias ' + year + ' para el area de ' + area[0].nombre
                                                        icono = "19"
                                                        area_men_telegram = area[0].id_area
                                                        $.ajax({
                                                            type: 'get',
                                                            url: "../../../../private/calendario/guardias/mensaje/?m=" + text_mensaje + "&i=" + icono + "&a=" + area_men_telegram,
                                                            dataType: "json",
                                                            cache: false,
                                                            success: function (data) {
                                                                if (data) {//Si se ha enviado el mensaje de forma correcta...
                                                                    createAlert('', ' Calendario ' + year + ', ' + area[0].nombre, ' Notificado vía Telegram la generación del nuevo calendario de guardias.', 'success', true, true, 'pageMessages');
                                                                }
                                                                else {
                                                                    Swal.fire({
                                                                        title: 'Opps! ...',
                                                                        text: 'No se ha podido notificar a los analistas de la generacion del nuevo calendario de guardias.',
                                                                        icon: 'error',
                                                                        timer: 5000,
                                                                        timerProgressBar: true,
                                                                    })
                                                                }
                                                                window.location = "../../../../private/calendario/guardias/nuevo/";
                                                            }
                                                        })
                                                    }
                                                    else{
                                                        window.location = "../../../../private/calendario/guardias/nuevo/";
                                                    }
                                                })

                                            }
                                            else{
                                                Swal.fire({
                                                    title: data.title,
                                                    html: '<p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i> '+ data.text+'</p>',
                                                    icon: data.icon,
                                                    timer: 10000,
                                                    timerProgressBar: true,
                                                    willClose: () => {
                                                        window.location = "../../../../private/calendario/guardias/nuevo/";
                                                    }
                                                })
                                            }
                                            
                                        }
                                    })
                                }
                            })
                        }, 1000);

                    }
                    else {
                        showPreloaderAlerta2();
                        createAlert(' Opps! ...', 'Calendario no válido', 'Revisa que todos y cada uno de los días contienen exclusivamente una guardia asociada a un analista.', 'danger', true, false, 'pageMessages')
                    }
                }
            }
        },
    });

    calendar.render();

    /*Evento click para poder eliminar una guardia*/
    $(document).on('click', '.btnDeleteGuardia', function () {
        Swal.fire({
            title: '¿Estas seguro?',
            html: '<p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i>  La guardia será eliminada del calendario no pudiendo revertir los cambios. </p>',
            icon: 'question',
            showCancelButton: true,
            cancelButtonColor: '#d33',
            confirmButtonText: 'Eliminar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        }).then((result) => {
            //Si confirmo que deseo eliminar la guardia del calendario...
            if (result.isConfirmed) {
                eventDelete.remove();
                Swal.close();
                createAlert(' Calendario ' + year + ', ' + area[0].nombre, 'Guardia eliminada', 'Se ha eliminado una guardia del calendario.', 'info', true, true, 'pageMessages');
            }
        })
    })

    TitleCalendario(); /*Cambio el titulo del calendario por el nombre del Area + Año */

    showPreloaderAlerta2();

    Swal.fire({
        title: 'Calendario de guardias',
        confirmButtonText: 'Generar Calendario',
        icon: 'info',
        html: '<p>A continuación se va a generar de forma automática el Calendario de guardias <b>' + year + '</b> para el área de <b><i class="' + area[0].icono + '"></i> ' + area[0].nombre + '</b>.</p>' +
            '<br>' +
            '<p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i>  Esta acción puede llevar unos minutos. Por favor espere hasta que haya terminado</p>',
        allowOutsideClick: false,
    }).then(() => {
        showPreloaderAlerta2();
        $.ajax({
            type: 'get',
            url: "../../../../private/calendario/guardias/nuevo/create/calendario/rotatorio/?a=" + area[0].id_area + "&y=" + year,
            dataType: "json",
            cache: false,
            success: function (answ) {
                showPreloaderAlerta2();
                if (answ.length > 0) { //Si se ha generado el calendario de forma automática
                    calendar.addEventSource({ events: answ, borderColor: '#fff', textColor: '#fff' });
                    Swal.fire({
                        html: '<p>Se ha generado el nuevo calendario de guardias <b>' + year + '</b> para el área de <b><i class="' + area[0].icono + '"></i> ' + area[0].nombre + '</b></p>' +
                            '<p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i>  A continuación se importarán en el calendario las guardias establecidas automáticamente. Una vez hecho' +
                            ' los cambios oportunos dale click <i class="fa-solid fa-arrow-pointer"></i> en el botón <b>Validar Calendario</b> para concluir el proceso. De' +
                            ' no hacerlo no se implementará el calendario elaborado.</p>',
                        icon: 'success',
                        allowOutsideClick: false
                    })
                }
                else { //Si no se ha generado el calendario de forma automática
                    Swal.fire({
                        title: 'Opps! ...',
                        text: 'Se ha producido un error al generar el calendario de forma automática.',
                        icon: 'error',
                        timer: 5000,
                        timerProgressBar: true,
                        willClose: () => {
                            showPreloaderAlerta2();
                            window.location = "../../../../private/calendario/guardias/nuevo/";
                        }
                    })
                }
            }
        })
    })
});



























