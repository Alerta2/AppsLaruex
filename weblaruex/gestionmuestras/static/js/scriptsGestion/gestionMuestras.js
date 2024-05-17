
function consultarInfoAlicuota(id){
    // call url /private/gestionmuestras/infoAlicuota/id/ using ajax
    $.ajax({
        url: '/private/gestionmuestras/infoAlicuota/'+id+'/',
        type: 'GET',
        success: function(response){
            $('#modalTratamientosAlicuotaContenido').html(response);
        },
        error: function(error){
            console.log(error);
        }
    });
    
}

function consultarInfoAlicuotaMuestras(id){
    // call url /private/gestionmuestras/infoAlicuota/id/ using ajax
    $.ajax({
        url: '/private/gestionmuestras/infoAlicuotaMedidas/'+id+'/',
        type: 'GET',
        success: function(response){
            $('#modalMedidasAlicuotaContenido').html(response);
        },
        error: function(error){
            console.log(error);
        }
    });
    
}

// funcion que borra los datos asociados a una alicuota y refresca la tabla en caso de ser necesario

function borrarAlicuota(id, tabla){
    rellenarModalGenerico("Borrar alicuota", "¿Está seguro que quiere borrar la alicuota de id " + id + "?", "borrarAlicuotaConfirmado("+id+",'"+tabla+"')", "Si", "No")
}

function borrarAlicuotaConfirmado(id, tabla){
    // call url /private/gestionmuestras/infoAlicuota/id/ using ajax
    $.ajax({
        url: '/private/gestionmuestras/borrarAlicuota/'+id+'/',
        type: 'GET',
        success: function(response){
            crearAviso(id, "Alicuota eliminada correctamente")
            $(tabla).bootstrapTable('refresh');
        },
        error: function(error){
            console.log(error);
        }
    });
}

// funcion que duplica una alicuota, el tratamiento y refresca la tabla en caso de ser necesario
function duplicarAlicuota(id, determinacion, usuario, tabla){
    rellenarModalGenerico("Duplicar alicuota", "¿Está seguro que quiere duplicar la alicuota de id " + id + "?", "duplicarAlicuotaConfirmado("+id+","+ determinacion+","+usuario+",'"+tabla+"')", "Si", "No")
}

function duplicarAlicuotaConfirmado(id, determinacion, usuario, tabla){
    $.ajax({
        url: '/private/gestionmuestras/duplicarAlicuota/',
        type: 'POST',
        data: {
            'id': id,
            'determinacion': determinacion,
            'usuario': usuario,
        },
        success: function(response){
            crearAviso(id, "Alicuota duplicada correctamente")
            $(tabla).bootstrapTable('refresh');
        },
        error: function(error){
            console.log(error);
        }
    });
}


function consultarEtiquetas(){

    $.ajax({  
        type: "GET",
        dataType: "html",
        url:"/private/gestionmuestras/consultarEtiquetas/",
        success: function(data)
            {
                // cambio el valor del div de id etiquetas_almacenadas por data
                $("#etiquetas_almacenadas").html(data);
                $("#etiquetas_almacenadas").css("height", "400px");

            }
        });

    }


function rellenarModalEtiquetas(id){
    $("#etiquetasSeleccionar").html("<p>Buscando etiquetas posibles...</p>");

    $.ajax({  
        type: "GET",
        dataType: "html",
        url:"/private/gestionmuestras/etiquetasSeleccionar/"+id+"/",
        success: function(data)
        {
            $("#etiquetasSeleccionar").html(data);
        }
    });
}

            
// if etiquetas is empty hide div hoja_etiquetas

function eliminarCodigo(codigo){
    $.ajax({  
        type: "GET",
        dataType: "json",
        url:"/private/gestionmuestras/eliminarCodigosExistentes/"+codigo+"/",
        success: function(data)
        {
        consultarEtiquetas();
        }
    });

}



function quitarEtiqueta(codigo){
    for (let index = 0; index < auxiliarJson.length; index++) {
        if (auxiliarJson[index].codigo == codigo) {
            auxiliarJson.splice(index, 1);
            break;
        }
    }
    // elimino el elemento etiqueta_+codigo
    document.getElementById("etiqueta_"+codigo).remove();
}

function disminuirEtiqueta(codigo){
    for (let index = 0; index < auxiliarJson.length; index++) {
        if (auxiliarJson[index].codigo == codigo) {
            auxiliarJson[index].cantidad = auxiliarJson[index].cantidad - 1;
            if (auxiliarJson[index].cantidad == 0) {
              quitarEtiqueta(codigo);
            }
            break;
        }
    }
}

function aumentarEtiqueta(codigo){
    for (let index = 0; index < auxiliarJson.length; index++) {
        if (auxiliarJson[index].codigo == codigo) {
            auxiliarJson[index].cantidad = auxiliarJson[index].cantidad + 1;
            break;
        }
    }
}

function rellenarModalGenerico(titulo, contenido, funcion, textoSi, textoNo){
    $('#modalConfirmGenericoLabel').html(titulo);
    $('#modalConfirmGenericoBody').html(contenido);
    $('#modalConfirmGenericoSi').html(textoSi);
    $('#modalConfirmGenericoNo').html(textoNo);
    console.log(funcion);
    $('#modalConfirmGenericoSi').attr('onclick', funcion+";$('#modalConfirmGenerico').modal('hide');");
    // muestro modal
    $('#modalConfirmGenerico').modal('show');
}

function eliminarDiv(id){
    document.getElementById(id).remove();
}