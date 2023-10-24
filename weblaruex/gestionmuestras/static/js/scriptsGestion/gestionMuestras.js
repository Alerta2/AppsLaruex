
function consultarInfoAlicuota(id){
    // call url /private/gestionmuestras/infoAlicuota/id/ using ajax
    $.ajax({
        url: '/private/gestionmuestras/infoAlicuota/'+id+'/',
        type: 'GET',
        success: function(response){
            $('#modalTratamientosAlicuota_titulo').html('Procesos de la alicuota ' + id + ' en el LARUEX');
            $('#modalTratamientosAlicuota_contenido').html('');
            let tabla = '<table class="table table-striped table-responsive"><thead><tr><th scope="col">Identificador</th><th scope="col">Codigo Reducido</th><th scope="col">Tratamiento</th><th scope="col">Fecha Inicio</th><th scope="col">Fecha Fin</th><th scope="col">Analista</th><th scope="col">Paso</th></tr></thead><tbody>';
            const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };

            for (let index = 0; index < response.length; index++) {
                const element = response[index];
                console.log(typeof element["fecha_fin"]);
                // convert string to date and time
                element["fecha_inicio"] = new Date(element["fecha_inicio"]);
                element["fecha_fin"] = new Date(element["fecha_fin"]);

                // informacion : 'identificador','cod_reducido','tratamiento__descripcion','fecha_inicio','fecha_fin','analista__nombre','paso_actual'
                tabla += '<tr><th scope="row">'+element["identificador"]+'</th><td>'+element["cod_reducido"]+'</td><td>'+element["tratamiento__descripcion"]+'</td><td>'+element["fecha_inicio"].toLocaleDateString('es-ES', options)+'</td><td>'+element["fecha_fin"].toLocaleDateString('es-ES', options)+'</td><td>'+element["analista__nombre"]+'</td><td>'+element["paso_actual"]+'</td></tr>';
                $('#modalTratamientosAlicuota_contenido').append('</tbody></table>');
            }
            tabla += '</tbody></table>';
            $('#modalTratamientosAlicuota_contenido').append(tabla);
        },
        error: function(error){
            console.log(error);
        }
    });
    
}

// funcion que borra los datos asociados a una alicuota y refresca la tabla en caso de ser necesario
function borrarAlicuota(id, tabla){
    
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