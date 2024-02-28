//console.log("ACTUALIZAR CALENDARIO RAREX", idUser, supervisorUser)
//console.log("AREA", idArea, "FECHA", fechaAltaBaja, "ESTADO ALTA/BAJA", estadoAltaBaja, "ANALISTA", idUser, "SUPERVISOR", supervisorUser)
$.ajax({
    url: '../../../../private/calendario/guardias/modifi/calendario/rarex/?a=' + idArea + '&f='+fechaAltaBaja+'&e='+estadoAltaBaja+'&u='+idUser+'&s='+supervisorUser,
    type: "GET",
    dataType: "json",
    success: function (answ) {
        //showPreloaderAlerta2();
        console.log("SE HA TERMINADO EL PROCESO DE ACTUALIZACION DEL CALENDARIO RAREX")
        if(answ.cambios.length>0){
            createAlert(' Semanas continuas','','Las semanas '+answ.cambios+' deben ser revisadas para evitar la continuidad de guardias para un mismo analista.','warning',true,false,'pageMessages');
        }

        if (answ.mensaje.icon == "error") {
            Swal.fire({
                title: answ.mensaje.title,
                text: answ.mensaje.text,
                icon: answ.mensaje.icon,
                timer: 10000,
                timerProgressBar: true,
                willClose: () => {
                    location.reload();
                }
            })
        }
        else {
            console.log("ENTRO A ESCRIBIR EL MENSAJE")
            text_mensaje = answ.mensaje.sms
            icono = "10"
            area_men_telegram = idArea
            descripcion = answ.mensaje.descripcion
            
            $.ajax({
                type: 'get',
                url: "../../../../private/calendario/guardias/mensaje/?m=" + text_mensaje + "&i=" + icono + "&a=" + area_men_telegram + "&d=" + descripcion,
                dataType: "json",
                cache: false,
                success: function (data) {
                    if (data) {//Si se ha enviado el mensaje de forma correcta...
                        Swal.fire({
                            title: answ.mensaje.title,
                            html: '<p>'+ answ.mensaje.text +'</p><br><p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i> Ha sido notificado vía telegram la modificación del personal en el calendario de guardias.</p>',
                            icon: answ.mensaje.icon,
                            timer: 10000,
                            timerProgressBar: true,
                            willClose: () => {
                                location.reload();
                            }
                        })
                    }
                    else {
                        Swal.fire({
                            title: answ.mensaje.title,
                            html: '<p>'+ answ.mensaje.text +'</p><br><p style="font-size:15px"><i class="fa-solid fa-info fa-beat" style="--fa-beat-scale: 1.4;"></i> No ha sido posible notificar vía telegram la modificación del personal en el calendario de guardias.</p>',
                            icon: 'warning',
                            timer: 10000,
                            timerProgressBar: true,
                            willClose: () => {
                                location.reload();
                            }
                        })
                    }
                }
            })
        }
    } 
})