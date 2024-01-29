var ColoresPersonal = undefined;

$.ajax({    //obtengo un listado que identifica a cada usuario dado de alta en el calendario de guardias con un color aleatorio
    type: 'get',
    url: "../../../../private/calendario/guardias/datos/colores/personal/?a=" + area[0].id_area,
    dataType: "json",
    cache: false,
    success: function (data) {
        ColoresPersonal = data
    }
})


/* Oculto el div movil con los accesos directos de festivos no fijos cuando no tiene ningun acceso directo */
$('#external-events').bind('DOMNodeRemoved', function () {
    if ($('#external-events div.fc-event.fc-h-event.fc-daygrid-event.fc-daygrid-block-event').length == 1) {
        $('#external-events').css('display', 'none');
    }
});


/*PERMITO QUE SE PUEDAN ARRASTRAR ACCESOS DIRECTOS DE FESTIVOS AL CALENDARIO*/
$(function () {
    $(".draggable-by-jquery-ui").draggable({ cancel: ".fc-event", containment: '#content-calendar' });
});



/*$(function () {
    var contentHtmlUsers = '<div class="col-lg-3 col-md-6" style="align-items: left; justify-content: left;vertical-align:middle; text-align:left; border-radius:30px; background:#fff">' +
        '<h2 class="cursive-brush" style="color:black">Personal</h2><hr>';
    for (var usuario of personal) {

        contentHtmlUsers = contentHtmlUsers + '<p>' +
            '<i class="fa-solid fa-circle" style="color:' + usuario.color + '; float:right; width:20px; height:20px;"></i>' +
            '<img  src="' + usuario.avatar + '" alt=""  style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover;"/>   ' + usuario.nombre + '</p>'
    }
    contentHtmlUsers = contentHtmlUsers + '</div';
    $("#infoCalendar").html(contentHtmlUsers);
});*/



var fechaLimitStart = moment().isoWeekYear(year).isoWeek(1).startOf('week').format('YYYY-MM-DD');
var fechaLimitEnd = moment().isoWeekYear(year).isoWeek(52).endOf('week').add(1, 'days').format('YYYY-MM-DD');
var calendar = undefined;
var clickAddFestivo = false;

/* CALENDARIO */
$(function () {
    var Calendar = FullCalendar.Calendar;
    var Draggable = FullCalendar.Draggable;

    var containerEl = document.getElementById('external-events');
    var calendarEl = document.getElementById('calendar');

    // initialize the external events
    // -----------------------------------------------------------------

    new Draggable(containerEl, {
        itemSelector: '.fc-event',
        eventData: function (eventEl) {
            /* Oculto el div movil con los accesos directos de festivos no fijos cuando no tiene ningun acceso directo */
            $('#external-events').bind('DOMNodeRemoved', function () {
                if ($('#external-events div.fc-event.fc-h-event.fc-daygrid-event.fc-daygrid-block-event').length == 1) {
                    $('#external-events').css('display', 'none');
                }
            });
            return {
                title: eventEl.innerText,
                color: '#00FF7F',
                textColor: 'black',
                allDay: true,
                add: true,
                group: 'festivos'
            };
        }
    });

    // initialize the calendar
    // -----------------------------------------------------------------

    calendar = new Calendar(calendarEl, {
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
        droppable: true, //Doy permiso para insertar eventos fuera del calendario
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
            right: "validarFestivos",
        },
        drop: function (info) {
            info.draggedEl.parentNode.removeChild(info.draggedEl);
        },
        eventDataTransform: function (arg) {
            if(arg.group=='guardias'){
                const color = ColoresPersonal.filter(function(element){
                    return element.idUser == arg.idUser;
                });
                if(color.length>0){
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
                if(e.dayNumberText=="1"){
                    e.dayNumberText = e.dayNumberText.replace('1', moment(e.date).format('MMM').toUpperCase()+" 1");
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
                case 'festivos':
                    return {
                        html: info.event.title
                    };
                default:
                    return {
                        html: ''
                    }
            }
        },
        dateClick: function (info) { //Permito añadir una nueva guardia haciendo click sobre la fecha de interés

            if (clickAddFestivo) { //Si estoy en el proceso de añadir los dias festivos al calendario de guardias...
                Swal.fire({
                    title: 'Añadir día festivo',
                    text: '(' + moment(info.dateStr).format('ll') + ')',
                    input: 'text',
                    showCancelButton: true,
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Guardar',
                    cancelButtonText: 'Cancelar',
                    reverseButtons: true,
                    inputPlaceholder: 'Introduce el título del festivo',
                }).then((result) => {
                    if (result.isConfirmed) {
                        var newFestivo = calendar.addEvent({
                            title: result.value,
                            start: info.dateStr,
                            color: '#00FF7F',
                            textColor: 'black',
                        });

                        newFestivo.setExtendedProp('group', 'festivos')

                        createAlert(' Festivos ' + year, result.value + ' (' + moment(info.dateStr).format('ll') + ')', 'Se ha añadido un nuevo día festivo al calendario.', 'info', true, true, 'pageMessages');
                    }
                })
            }
            else {
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
            }

        },
        eventClick: function (info) { //Permito eliminar una guardia

            if (clickAddFestivo) { //Si estoy en el proceso de añadir los dias festivos al calendario de guardias...
                festivoDelete = info.event

                Swal.fire({
                    html: '<h3><b>' + info.event.title + '</b></h3>(' + moment(info.event.start).format('ll') + ')' +
                        "<br>" +
                        '<button type="button" role="button" tabindex="0" class="btnDeleteFestivo customSwalBtn ">Eliminar</button><br>',
                    showConfirmButton: false,
                    timer: 100000,
                    timerProgressBar: true,
                    didOpen: (toast) => {
                        toast.addEventListener('mouseenter', Swal.stopTimer)
                        toast.addEventListener('mouseleave', Swal.resumeTimer)
                    }
                })
            }
            else {
                if (info.event.extendedProps.group == "guardias") {

                    eventDelete = info.event

                    Swal.fire({
                        html: '<img src="' + info.event.extendedProps.avatar + '" alt="" style="width:100px; height:100px; border-radius:50%; object-fit: cover;margin-bottom:10px"/>' +
                            '<h3><b>' + info.event.extendedProps.nameUser + '</b></h3>' +
                            'Analista de guardia' +
                            ' desde el ' + moment(info.event.start).format('dddd, ll') +
                            ' hasta el ' + moment(info.event.end).add(-1, 'days').format('dddd, ll') +
                            ' en el área de <b><i class="' + area[0].icono + '"></i>&nbsp' + area[0].nombre + '</b>' +
                            "<br>" +
                            '<button type="button" role="button" tabindex="0" class="btnDeleteGuardia customSwalBtn ">Eliminar</button><br>',
                        showConfirmButton: false,
                        timer: 100000,
                        timerProgressBar: true,
                        didOpen: (toast) => {
                            toast.addEventListener('mouseenter', Swal.stopTimer)
                            toast.addEventListener('mouseleave', Swal.resumeTimer)
                        }
                    })
                }
            }
        },
        customButtons: {
            validarFestivos: {
                text: 'Validar Festivos',
                click: function () {
                    showPreloaderAlerta2();
                    var answ = ValidarFestivosCalendario();
                    if (answ) { //Si el calendario de festivos es valido

                        createAlert('', ' Festivos ' + year, ' Los días festivos del calendario de guardias ' + year + ' han sido validados', 'success', true, true, 'pageMessages');

                        //Obtengo un JSON con los dias festivos señalados
                        var festivos = calendar.getEvents() //obtengo todos los días festivos señalados en el calendario
                        var jsonFestivos = (JSON.parse(JSON.stringify(festivos))).map((element) => ({
                            fecha_local: element.start,
                            nombre: element.title
                        }))

                        $.ajax({ //inserto todos los días festivos señalados en el calendario en la base de datos
                            type: 'get',
                            url: "../../../../private/calendario/guardias/datos/upd/festivos/?y=" + year + "&f=" + JSON.stringify(jsonFestivos),
                            dataType: "json",
                            cache: false,
                            success: function (data) {
                                if (data.icon == 'error') { //Si se ha producido un error
                                    createAlert(' Opps! ...', data.title, data.text, 'danger', true, false, 'pageMessages')
                                }
                                else { //Si se han insertado todos los festivos de forma correcta, procedo a generar el calendario de forma automática
                                    createAlert(' Festivos ' + year, data.title, data.text, 'info', true, true, 'pageMessages');

                                    //GENERO EL NUEVO CALENDARIO DE GUARDIAS RAREX DE FORMA AUTOMATICA
                                    var data = (JSON.parse(JSON.stringify(festivos))).map((element) => ({
                                        start: element.start,
                                        title: element.title
                                    }))
                                    GenerarCalendarioRarex(data);
                                }
                            }
                        })
                    }
                    else {
                        showPreloaderAlerta2();
                        createAlert(' Opps! ...', 'Festivos no válidos', 'Revisa que no haya en un día dos días festivos definidos.', 'danger', true, false, 'pageMessages')
                    }
                }
            },
            validarCalendario: {
                text: 'Validar Calendario',
                click: function () {
                    showPreloaderAlerta2();
                    var answ = ValidarDiasCalendario();
                    if (answ) {

                        createAlert('', ' Calendario ' + year + ', ' + area[0].nombre, ' El Calendario de guardias ha sido validado.', 'success', true, true, 'pageMessages');
                        createAlert(' Mensaje informativo', 'Generando Calendario de Guardias '+year+', '+area[0].nombre+'...', 'No abandone la página hasta que el proceso no haya terminado.', 'info', true, true, 'pageMessages');
                        
                        setTimeout(function () {
                            // FINALMENTE OBTENGO TODAS LAS GUARDIAS PARA INSERTARLAS EN LA BASE DE DATOS
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
                                url: "../../../../private/calendario/guardias/nuevo/upd/calendario/rarex/?g=" + JSON.stringify(jsonGuardias) + "&y=" + year + "&t=" + turno + "&a=" + area[0].id_area,
                                dataType: "json",
                                cache: false,
                                success: function (data) {
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


    TitleCalendario(); /*Cambio el titulo del calendario por el nombre del Area + Año */

    /*Evento click para poder eliminar una guardia*/
    $(document).on('click', '.btnDeleteFestivo', function () {
        Swal.fire({
            title: '¿Estas seguro?',
            html: '<p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i>  El día festivo <b>' + festivoDelete.title + '</b> (' + moment(festivoDelete.start).format('ll') + ') será eliminado del calendario. </p>',
            icon: 'question',
            showCancelButton: true,
            cancelButtonColor: '#d33',
            confirmButtonText: 'Eliminar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        }).then((result) => {
            //Si confirmo que deseo eliminar la guardia del calendario...
            if (result.isConfirmed) {
                festivoDelete.remove();
                Swal.close();
                createAlert(' Festivos ' + year, 'Festivo eliminado', 'Se ha eliminado un día festivo del calendario.', 'info', true, true, 'pageMessages');
            }
        })
    })

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

    //Al cargar este js lo primero que hago es comprobar si hay dias festivos registrados en la base de datos para el año seleccionado
    //Si los hubiera, pido confirmación para o bien añadir los días festivos ya registrados, o bien para modificar dichos destivos
    $(async function () {
        showPreloaderAlerta2();
        $.ajax({
            type: 'get',
            url: "../../../../private/calendario/guardias/datos/festivos/?y=" + year,
            dataType: "json",
            cache: false,
            success: function (data) {
                showPreloaderAlerta2();

                if (data.length > 0) { //Si hay festivos registrados en la base de datos
                    Swal.fire({
                        title: 'Días festivos',
                        html: '<p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i> '+
                            'En estos momentos tienes registrados en la base de datos los siguientes días festivos:</p><br>' +
                            '<div id="diasFestivos"></div>',
                        confirmButtonText: 'Si',
                        showCancelButton: true,
                        cancelButtonText: 'No',
                        reverseButtons: true,
                        didOpen: () => { //Listo los festivos que actualmente se encuentran registrados en la base de datos
                            var contentHtmlSwall = ''
                            for (var festivo of data) {
                                contentHtmlSwall = contentHtmlSwall + '<p style="font-size:14px">' + festivo.title + ' (' + moment(festivo.start).format('ll') + ')' + '</p>';
                            }
                            contentHtmlSwall = contentHtmlSwall + '<p><b>¿Deseas añadir/modificar los días festivos?</b></p>'
                            $("#diasFestivos").html(contentHtmlSwall);
                        },
                        stopKeydownPropagation: false,
                        allowOutsideClick: () => {
                            return false
                        }
                    }).then(function (result) {
                        if (result.isConfirmed) { //Si deseo modificar los días festivos ...
                            AddFestivos();
                        }
                        else { //Si no quiero modificar los días festivos...
                            
                            //GENERO EL NUEVO CALENDARIO DE GUARDIAS RAREX DE FORMA AUTOMATICA
                            GenerarCalendarioRarex(data);
                        }
                    })

                }
                else { //Si NO hay festivos registrados en la base de datos
                    AddFestivos();
                }

            }
        })
    })
});







let currentStep
var result = null

/* FUNCION QUE MUESTRA EL PROCESO REQUERIDO PARA AÑADIR LOS DIAS FESTIVOS NECESARIOS PARA GENERAR EL CALENDARIO*/
async function AddFestivos() {
    showPreloaderAlerta2();

    clickAddFestivo = true;

    const steps = ['1', '2', '3', '4']
    const Queue = Swal.mixin({
        showCancelButton: true,
        confirmButtonText: 'Siguiente <i class="fa-solid fa-circle-arrow-right"></i>',
        cancelButtonText: '<i class="fa-solid fa-circle-left"></i> Atrás',
        stopKeydownPropagation: false,
        reverseButtons: true,
        progressSteps: steps,
        inputAttributes: {
            required: true
        },
        validationMessage: 'Este campo es requerido!',
        allowOutsideClick: () => {
            return false
        },
    })
    const values = []

    for (currentStep = 0; currentStep < steps.length;) {
        

        switch (currentStep) {
            case 0: //selecciono los dias festivos fijos que deseo añadir al calendario de forma automática
                result = await Queue.fire({
                    title: 'Días festivos',
                    html:
                        '<p>Desmarque los días festivos fijos de Extremadura que no desea añadir automáticamente al calendario</p><br>' +
                        '<div class="festivosFijos">' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch0" checked value="' + year + '-01-01">' +
                        '<label class="custom-control-label" for="customSwitch0">Año Nuevo</label><span> (1 de Enero)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch1" checked value="' + year + '-01-06">' +
                        '<label class="custom-control-label" for="customSwitch1">Epifanía del Señor</label><span> (6 de Enero)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch2" checked value="' + year + '-01-28">' +
                        '<label class="custom-control-label" for="customSwitch2">Santo Tomás de Aquino</label><span> (28 de Enero)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch3" checked value="' + year + '-03-' + PrimerViernesMarzo() + '">' +
                        '<label class="custom-control-label" for="customSwitch3">Servicios Centrales Uex</label><span> (' + PrimerViernesMarzo() + ' de Marzo)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch4" checked value="' + year + '-04-23">' +
                        '<label class="custom-control-label" for="customSwitch4">San Jorge</label><span> (23 de Abril)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch5" checked value="' + year + '-05-01">' +
                        '<label class="custom-control-label" for="customSwitch5">Día del Trabajador</label><span> (1 de Mayo)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch6" checked value="' + year + '-08-15">' +
                        '<label class="custom-control-label" for="customSwitch6">Asunción de la Virgen</label><span> (15 de Agosto)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch7" checked value="' + year + '-09-08">' +
                        '<label class="custom-control-label" for="customSwitch7">Día de Extremadura</label><span> (8 de Septiembre)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch8" checked value="' + year + '-10-12">' +
                        '<label class="custom-control-label" for="customSwitch8">Día de la Hispanidad</label><span> (12 de Octubre)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch9" checked value="' + year + '-11-01">' +
                        '<label class="custom-control-label" for="customSwitch9">Día de todos los Santos</label><span> (1 de Noviembre)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch10" checked value="' + year + '-12-06">' +
                        '<label class="custom-control-label" for="customSwitch10">Día de la Constitución Española</label><span> (6 de Diciembre)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch11" checked value="' + year + '-12-08">' +
                        '<label class="custom-control-label" for="customSwitch11">Día de la Inmaculada</label><span> (8 de Diciembre)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch12" checked value="' + year + '-12-24">' +
                        '<label class="custom-control-label" for="customSwitch12">Nochebuena</label><span> (24 de Diciembre)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch13" checked value="' + year + '-12-25">' +
                        '<label class="custom-control-label" for="customSwitch13">Navidad</label><span> (25 de Diciembre)</span>' +
                        '</div>' +
                        '<div class="custom-control custom-switch">' +
                        '<input type="checkbox" class="custom-control-input" id="customSwitch14" checked value="' + year + '-12-31">' +
                        '<label class="custom-control-label" for="customSwitch14">Nochevieja</label><span> (31 de Diciembre)</span>' +
                        '</div>' +
                        '</div>',
                    focusConfirm: false,
                    showCancelButton: currentStep > 0,
                    currentProgressStep: 0,
                    inputValue: values[currentStep],
                    allowOutsideClick: () => {
                        return false
                    },
                    preConfirm: () => {
                        return [{ 'start': $('#customSwitch0').val(), 'title': $("label[for='" + $('#customSwitch0').attr('id') + "']").text(), 'add': $('#customSwitch0').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch1').val(), 'title': $("label[for='" + $('#customSwitch1').attr('id') + "']").text(), 'add': $('#customSwitch1').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch2').val(), 'title': $("label[for='" + $('#customSwitch2').attr('id') + "']").text(), 'add': $('#customSwitch2').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch3').val(), 'title': $("label[for='" + $('#customSwitch3').attr('id') + "']").text(), 'add': $('#customSwitch3').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch4').val(), 'title': $("label[for='" + $('#customSwitch4').attr('id') + "']").text(), 'add': $('#customSwitch4').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch5').val(), 'title': $("label[for='" + $('#customSwitch5').attr('id') + "']").text(), 'add': $('#customSwitch5').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch6').val(), 'title': $("label[for='" + $('#customSwitch6').attr('id') + "']").text(), 'add': $('#customSwitch6').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch7').val(), 'title': $("label[for='" + $('#customSwitch7').attr('id') + "']").text(), 'add': $('#customSwitch7').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch8').val(), 'title': $("label[for='" + $('#customSwitch8').attr('id') + "']").text(), 'add': $('#customSwitch8').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch9').val(), 'title': $("label[for='" + $('#customSwitch9').attr('id') + "']").text(), 'add': $('#customSwitch9').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch10').val(), 'title': $("label[for='" + $('#customSwitch10').attr('id') + "']").text(), 'add': $('#customSwitch10').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch11').val(), 'title': $("label[for='" + $('#customSwitch11').attr('id') + "']").text(), 'add': $('#customSwitch11').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch12').val(), 'title': $("label[for='" + $('#customSwitch12').attr('id') + "']").text(), 'add': $('#customSwitch12').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch13').val(), 'title': $("label[for='" + $('#customSwitch13').attr('id') + "']").text(), 'add': $('#customSwitch13').is(':checked'), 'group': 'festivos' },
                        { 'start': $('#customSwitch14').val(), 'title': $("label[for='" + $('#customSwitch14').attr('id') + "']").text(), 'add': $('#customSwitch14').is(':checked'), 'group': 'festivos' }]
                    }
                });
                break;
            case 1: //Muestro un mensaje informativo
                result = await Queue.fire({
                    title: 'Días festivos',
                    html: '<p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i>  ' +
                        'Una vez añadidos los festivos fijos de forma automática, complete el calendario añadiendo los días ' +
                        'festivos no fijos, arrastrando los accesos directos que se mostrarán en el panel móvil. Finalmente ' +
                        'dale click <i class="fa-solid fa-arrow-pointer"></i> en el botón <b>Validar Festivos</b> para proceder ' +
                        'a generar el calendario de guardias.</p>' +
                        '<br>' +
                        '<img src="../../../../static/img/calendario_guardias/tutoriales/accesos_directos_festivos.gif" style="width:100%" /> ',
                    showCancelButton: currentStep > 0,
                    currentProgressStep: 1,
                    inputValue: values[currentStep],
                    footer: '<a href="#" onclick="OmitirTutorial()" style="text-size:12px">Omitir explicación</a>'
                });
                break;
            case 2: //Muestro un mensaje informativo
                result = await Queue.fire({
                    title: 'Días festivos',
                    html: '<p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i>  ' +
                        'Para añadir cualquier otro día festivo no contemplado haz click <i class="fa-solid fa-arrow-pointer"></i> ' +
                        'sobre la fecha de interés.</p><br>' +
                        '<img src="../../../../static/img/calendario_guardias/tutoriales/nuevo_festivo.gif" style="width:100%" /> ',
                    showCancelButton: currentStep > 0,
                    currentProgressStep: 2,
                    inputValue: values[currentStep],
                    footer: '<a href="#" onclick="OmitirTutorial()" style="text-size:12px">Omitir explicación</a>'
                });
                break;
            case 3: //Muestro un mensaje informativo
                result = await Queue.fire({
                    title: 'Días festivos',
                    html: '<p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i>  ' +
                        'Para modificar cualquier evento festivo de día basta con arrastrarlo hasta la nueva fecha de interés. ' +
                        'Si de lo contrario, desea eliminarlo haz click sobre dicho evento.</p><br>' +
                        '<img src="../../../../static/img/calendario_guardias/tutoriales/mover_eliminar_festivo.gif" style="width:100%" /> ',
                    showCancelButton: currentStep > 0,
                    currentProgressStep: 3,
                    inputValue: values[currentStep],
                    footer: '<a href="#" onclick="OmitirTutorial()" style="text-size:12px">Omitir explicación</a>'
                });
                break;
        }

        if (result.value) {
            values[currentStep] = result.value
            currentStep++
        } else if (result.dismiss === Swal.DismissReason.cancel) {
            currentStep--
        } else {
            break
        }

        if (currentStep === steps.length) {

            $('#external-events').css('display', 'block');//Muestro el div con los dias festivos no fijos que debo añadir al calendario

            //FINALMENTE:  
            var festivos = values[0].filter(element => element.add == true);//filtro los dias festivos que he seleccionado para añadir automáticamente al calendario

            //Si el día destivo cae en Domingo (day=0) entonces lo paso al lunes a excepción de nochebuena y nochevieja cuyo día después ya es festivo
            festivos.forEach(element => {
                const date = moment(element.start);
                const day = date.day();
                if (day == 0 && date.format('MM-DD') != '12-24' && date.format('MM-DD') != '12-31') {
                    element.start = moment(element.start).add(1, 'days').format('YYYY-MM-DD');
                }
            });

            calendar.addEventSource({ events: festivos, color: '#00FF7F', textColor: 'black' });//añado el json fltrado y corregido al calendario

            createAlert(' Festivos ' + year, '', 'Actualizados los días festivos para el año ' + year + '.', 'info', true, true, 'pageMessages');
        }
    }
}


function PrimerViernesMarzo(year) {
    let date = moment().set('year', parseInt(year)).set('month', 2).set('date', 1).isoWeekday(5)
    if (date.month() < 2) { // 
        date = date.add(7, 'days');
    }
    return date.format('DD')
}

function OmitirTutorial(){
    currentStep = 3;
    Swal.clickConfirm();
}

/* FUNCION QUE GENERA DE FORMA AUTOMATICA EL CALENDARIO DE GUARDIAS RAREX, TENIENDO EN CUENTA LOS FESTIVOS YA EXISTENTES*/
function GenerarCalendarioRarex(festivos) {
    calendar.removeAllEvents();
    clickAddFestivo = false;
    $('#external-events').css('display', 'none'); //Oculto el div con los festivos no fijos
    calendar.setOption('footerToolbar', { right: 'validarCalendario' }); //Cambio el tipo de botón de Validar Festivos a Validar Calendario
    calendar.addEventSource({ events: festivos, display: 'background', color: '#00FF7F', textColor: 'black' }) //Añado los festivos de la base de datos en el calendario
    TitleCalendario(); //Cambio el titulo del calendario por el nombre del Area + Año

    Swal.fire({
        title: 'Calendario de guardias',
        confirmButtonText: 'Generar Calendario',
        icon: 'info',
        html: '<p>A continuación se va a generar de forma automática el Calendario de guardias <b>' + year + '</b> para el área de <b><i class="' + area[0].icono + '"></i> ' + area[0].nombre + '</b>.</p>' +
            '<br>' +
            '<p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i>  Esta acción puede llevar unos minutos. Por favor espere hasta que haya terminado</p>',
        allowOutsideClick: false,
    }).then(() => {
        $.ajax({
            type: 'get',
            url: "../../../../private/calendario/guardias/nuevo/create/calendario/rarex/?a=" + area[0].id_area + "&y=" + year,
            dataType: "json",
            cache: false,
            success: function (answ) {
                showPreloaderAlerta2();
                if(answ.cambios.length>0){
                    createAlert(' Semanas continuas','','Las semanas '+answ.cambios+' deben ser revisadas para evitar la continuidad de guardias para un mismo analista.','warning',true,false,'pageMessages');
                }
                if (answ.guardias.length > 0) { //Si se ha generado el calendario de forma automática
                    calendar.addEventSource({ events: answ.guardias, borderColor: '#fff', textColor: '#fff' });
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
}