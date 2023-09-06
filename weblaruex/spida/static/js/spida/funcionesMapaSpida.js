/*-----------------------------------------------------------------
# FUNCIONES RELACIONADAS CON EL DISEÑO DE LAS CAPAS DE ESTACIONES
-----------------------------------------------------------------*/

/*Funcion que carga los datos GeoJson de las estaciones monitorizadas y visualizadas en una capa */
function CargarEstaciones(){

    map.spin(true);//activo el spin de cargando mapa
    
    $.getJSON("/spida/estaciones/", 
    function(data){
        
        /* Layer de Alarmas animadas */
        layer_alarmas_animadas.clearLayers();
        layer_alarmas_animadas.addData(data);

        /* Layer Estaciones Saih Tajo */
        layer_estaciones_saih_tajo.clearLayers();
        layer_estaciones_saih_tajo.addData(data);

        /* Layer Estaciones Saih Guadiana */
        layer_estaciones_saih_guadiana.clearLayers();
        layer_estaciones_saih_guadiana.addData(data);

        /* Layer Estaciones Spida */
        layer_estaciones_spida.clearLayers();
        layer_estaciones_spida.addData(data);

        InfoAvisos(data);
       
    })
    .fail(function() { 
        console.log('getJSON Estaciones request failed! '); 
    })
    .always(function() { 
        map.spin(false);
    });
};

/*Funcion que asigna el tipo de marcador de una estacion en funcion de su estado de operatividad/alerta
los iconos blancos son para la red Spida y los Azules para los del SAIH*/
function IconMarker(feature){
    if(feature.properties.red==1){ /* Spida */
        switch(feature.properties.estado){
            case -1: /* Sin datos */
                return '../../../static/img/spida/markers/spida_negro.png';
            case 0: /* Verde */
                return '../../../static/img/spida/markers/spida_verde.png' ;
            case 1: /* Amarillo */
                return '../../../static/img/spida/markers/spida_amarillo.png';
            case 2: /* Naranja */
                return '../../../static/img/spida/markers/spida_naranja.png';
            case 3: /* Rojo */
                return '../../../static/img/spida/markers/spida_rojo.png';
            default: /* Error */
                return '../../../static/img/spida/markers/spida_malva.png';
        }
    }
    else { /* Saih */
        switch(feature.properties.estado){
            case -1: /* Sin datos */ 
                return '../../../static/img/spida/markers/saih_negro.png';
            case 0: /* Verde */
                return '../../../static/img/spida/markers/saih_verde.png' ;
            case 1: /* Amarillo */ 
                return '../../../static/img/spida/markers/saih_amarillo.png';
            case 2: /* Naranja */
                return '../../../static/img/spida/markers/saih_naranja.png';
            case 3: /* Rojo */
                return '../../../static/img/spida/markers/saih_rojo.png';
            default: /* Error */
                return '../../../static/img/spida/markers/saih_malva.png';
        }
    }
};

/* Diseño de los Markers de las estaciones SPIDA monitorizadas */ 
function createCustomIconSPIDA(feature, latlng){
    let myIcon = L.icon({
        iconUrl: IconMarker(feature),
        iconSize: [85, 60], // width and height of the image in pixels
    })
    return L.marker(latlng, {icon: myIcon}).bindTooltip(
            '<img src="' + logoTipoRed(feature) + '" style="max-width:100%;max-height:100%;object-fit: contain;">'
            +'<br/><br/>'
            +'<p><span style="font-weight: bold;">Estación: </span><span style="font-weight: normal;">'+feature.properties.nombre+'</span></p>'
            +'<p><span style="font-weight: bold;">Nivel de Río: </span><span style="font-weight: normal;">'+feature.properties.valor+'</span> m </p>'
            +'<p><span style="font-weight: bold;">Fecha: </span><span style="font-weight: normal;">'+feature.properties.fecha_local+'</span></p>'
            +'<p><span style="font-weight: bold;">Estado: </span></span>'+IconoEstadoEstacion(feature)+'<span style="font-weight: normal"> '+DescripcionEstadoEstacion(feature)+'. </span></p>',        
            {
                direction: 'right',
                className: 'leaflet-tooltip'
            }).on('click', function () {
                    ContenidoSidebarSPIDA(feature);//relleno el contenido del sidebar
            });
};

/*Funcion que asigna el logotipo de la info de la estacion en funcion de la red hidrologica 
a la que pertenece (SPIDA, SAIH TAJO O SAIH GUADIANA) */
function logoTipoRed(feature){
    switch(feature.properties.red){
        case 1: //spida
            return '../../../static/img/spida/logos/logo_spida.png';
        case 2: //tajo
            return '../../../static/img/spida/logos/confederacion_tajo.jpg';
        case 3: //guadiana
            return '../../../static/img/spida/logos/confederacion_guadiana.png';  
    }
};


/*-------------------------------------------------------------------
# FUNCIONES RELACIONADAS CON EL DISEÑO DE LA CAPA DE ALARMAS ANIMADAS
-------------------------------------------------------------------*/

/* Diseño de los Markers que indican las alarmas (N1, N2 y N3) */ 
function createCustomIconAlarm (feature, latlng) {
        let pulsingIcon = L.icon.pulse({
        iconSize:  [20, 20], /* ancho y alto del icono */
        color: colorAlert(feature), /* color en funcion del estado (N1, N2, N3) */
        fillColor: 'transparent' /* relleno del circulo */
        });
        return L.marker(latlng, { icon: pulsingIcon });
};

/* Color de los circulos animados (L.icon.pulse) de alerta */
function colorAlert(feature){
    switch(feature.properties.estado){
            case 1: /* N1: Nivel amarillo */
                return 'yellow';
            case 2: /* N2: Nivel naranja */
                return 'orange';
            case 3: /* N3: Nivel rojo */
                return 'red';
            default: /* El resto */
                return 'transparent';
        }
};


/*-------------------------------------------------------------------
# FUNCION RELACIONADA CON EL CUADRO DE INFO AVISOS (DESCRIPCION DE NIVELES DE ALERTA)
-------------------------------------------------------------------*/

/* Funcion que diseña el rotulo del cruadro de informacion de si hay avisos o no */
function InfoAvisos(geoJson){
    var contNegro = geoJson.features.filter(item => item.properties['estado'] == -1).length; /* Sin datos */
    var contVerde = geoJson.features.filter(item => item.properties['estado'] == 0).length; /* N0 o Sin avisos */
    var contAmarillo = geoJson.features.filter(item => item.properties['estado'] == 1).length; /* N1 */
    var contNaranja = geoJson.features.filter(item => item.properties['estado'] == 2).length; /* N2 */
    var contRojo = geoJson.features.filter(item => item.properties['estado'] == 3).length; /* N3 */

    var rotulo = '' ;
    var cont='';

    if(contNegro==0 && contAmarillo==0 && contNaranja==0 && contRojo==0 && contVerde>0)
    {
         cont=' <i class="fas fa-check" style="color:#90EE90"></i> '
         rotulo='<h1 id="title-aviso"> SIN AVISOS'+cont+'</h1>'
    }
    else
    {
        if(contNegro>0){
            cont= ' <i class="fas fa-exclamation-triangle" style="color:#000000"></i> '
        }
        if(contAmarillo>0){
            cont=cont+' <i class="fas fa-exclamation-triangle" style="color:#FFFF00"></i> '
        }
        if(contNaranja>0){
            cont=cont+' <i class="fas fa-exclamation-triangle" style="color:#FFA500"></i> '
        }
        if(contRojo>0){
            cont=cont+' <i class="fas fa-exclamation-triangle" style="color:#CD5C5C"></i> '
        }

        rotulo='<h1 id="title-aviso"> AVISOS '+cont+'</h1>'
    }

    myInfoControl.setTitle(rotulo);
};

/* En funcion del tamaño de pantalla escondo el sidebar en caso de estar abierto antes de mostrar el panel info avisos */
function MostrarPanelInfoAvisos(){
    var w = window.innerWidth;
    /*console.log("Tamaño de la pantalla "+w+"px");*/
    if(w<1000){
    sidebar.hide();// Hide sidebar
    }
    myInfoControl._showContent();//show panel info avisos
}




/*----------------------------------------------------------------------------------------------
# FUNCIONES RELACIONADAS CON EL PANEL LATERAL (SIDEBAR) QUE CONTIENE TODA LA INFO DE UNA ESTACION
----------------------------------------------------------------------------------------------*/

/* Diseño del contenido del panel lateral sidebar para estaciones tipo SPIDA */
function ContenidoSidebarSPIDA(feature){
    map.spin(true);
      
    $.getJSON("/spida/imagen/",{estacion: parseInt(feature.properties.id.toString().substr(-2)) + 7000, camara: "10"}, 
        function(data){
            //console.log("Prueba1",document.getElementById('sidebar').getBoundingClientRect().width);
            sidebar.setContent(
                '<div class="section-title">'
                +'<h2>'+feature.properties.nombre+'</h2>'
                +'</div>'
                +'<p><span style="font-weight: bold">Nombre de la estación: </span><span style="font-weight: normal">'+feature.properties.nombre+'</span></p>'
                +'<p><span style="font-weight: bold">Localización: </span><span style="font-weight: normal">'+feature.geometry.coordinates[1]+' '+feature.geometry.coordinates[0]+'. </span><a href="https://www.google.com/maps/place/'+feature.geometry.coordinates[1]+','+feature.geometry.coordinates[0]+'" target="_blank">Ir al sitio <i class="fas fa-location-arrow"></i></a></p>'
                //+'<p><span style="font-weight: bold">Río: </span><span style="font-weight: normal">'+feature.properties.rio+'</span><p>'
                //+'<p><span style="font-weight: bold">Subcuenca: </span><span style="font-weight: normal">'+feature.properties.subcuenca+'</span><p>'
                +'<p><span style="font-weight: bold">Nivel de Río: </span><span style="font-weight: normal">'+feature.properties.valor+' metros el '+feature.properties.fecha_local+'</span></p>'
                +'<div id="fluid-meter" style="text-align: center;"></div>'
                +'<p><span style="font-weight: bold">Estado: </span>'+IconoEstadoEstacion(feature)+'<span style="font-weight: normal"> '+DescripcionEstadoEstacion(feature)+'. </span><a href="#" onclick="MostrarPanelInfoAvisos();">+ Informacion <i class="fas fa-mouse-pointer"></i></a></p>'
                //+'<p><span style="font-weight: bold">Observación: </span><button><i class="fa fa-camera"></i></button><p>'
                + AddTiempoAemet(feature,data)
                + AddImagen(feature,data)
                //+'<p><span style="font-weight: bold">Ultima imagen capturada: </span><span style="font-weight: normal">'+data.fecha_hora+'</span><p>'
                //+'<img id="myImg" src="data:image/jpg;base64,'+data.imagen+'" alt="'+ data.estacion + ',' +data.fecha_hora+'" style="width:100%" onclick="AbrirImagenModal(this.src,this.alt)">'
                +'<figure class="highcharts-figure">'
                +'<div id="container" style="width:100%; margin: 0 auto; padding: 10px;"></div>'    
                //+'<p class="highcharts-description">'
                //+'Hola Descripcion del grafico si se quisiera'
                //+'</p>'
                +'</figure>'
		+'<figure class="highcharts-figure">'
                +'<div id="container2" style="width:100%; margin: 0 auto; padding: 10px;"></div>'    
                //+'<p class="highcharts-description">'
                //+'Hola Descripcion del grafico si se quisiera'
                //+'</p>'
                +'</figure>'
		+'<figure class="highcharts-figure">'
                +'<div id="plot_prediccion_rio" style="width:100%; margin: 0 auto; padding: 10px;"></div>'    
                //+'<p class="highcharts-description">'
                //+'Hola Descripcion del grafico si se quisiera'
                //+'</p>'
                +'</figure>'
		+'<figure class="highcharts-figure">'
                +'<div id="plot_prediccion_lluvia" style="width:100%; margin: 0 auto; padding: 10px;"></div>'    
                //+'<p class="highcharts-description">'
                //+'Hola Descripcion del grafico si se quisiera'
                //+'</p>'
                +'</figure>'
            );
            //console.log("Prueba2",document.getElementById('sidebar').getBoundingClientRect().width-80);
            
            if(feature.properties.red==1){//Solo para las estaciones Spida
                //Diseño el indicador animado del porcentaje de nivel de agua
                //https://www.cssscript.com/liquid-progress-indicator/
                var fm = new FluidMeter();
                fm.init({
                targetContainer: document.getElementById("fluid-meter"),
                fillPercentage: 45,
                options: {
                    fontSize: "30px",
                    fontFamily: "Roboto",
                    drawPercentageSign: true,
                    drawBubbles: true,
                    size: 250,
                    borderWidth: 19,
                    backgroundColor: "#e2e2e2",
                    foregroundColor: "#fafafa",
                    foregroundFluidLayer: {
                    fillStyle: "#16E1FF",
                    angularSpeed: 30,
                    maxAmplitude: 5,
                    frequency: 30,
                    horizontalSpeed: -20
                    },
                    backgroundFluidLayer: {
                    fillStyle: "#4F8FC6",
                    angularSpeed: 100,
                    maxAmplitude: 3,
                    frequency: 22,
                    horizontalSpeed: 20
                    }
                }
                });
                fm.setPercentage(Math.floor(feature.properties.valor*100/feature.properties.N3));
            }

        GraficoNivelRio(feature);
	    GraficoPrecipitacion(feature);
        const user_logged = JSON.parse(document.getElementById('user_logged').textContent);
        if(user_logged==true){
            GraficoNivelRioPrediccion(feature);
            GraficoPrecipitacionPrediccion(feature);
        }

	    
        if(sidebar.isVisible()==false){
            sidebar.toggle();
        }
    })
    .fail(function() { 
        console.log('Content Sidebar request failed! '); 
    })
    .always(function() { 
        map.spin(false);
    });
};

/* Tipo de icono que indica el estado de operatividad de una estacion para el sidebar */
function IconoEstadoEstacion(feature){
    switch(feature.properties.estado){
                case -1: /* Sin datos */
                    return '<i class="fas fa-exclamation-triangle" style="color:#000000"></i>';
                case 0: /* Verde */
                    return '<i class="fas fa-check" style="color:#90EE90"></i>' ;
                case 1: /* Amarillo */
                    return '<i class="fas fa-exclamation-triangle" style="color:#FFFF00"></i>';
                case 2: /* Naranja */
                    return '<i class="fas fa-exclamation-triangle" style="color:#FFA500"></i>';
                case 3: /* Rojo */
                    return '<i class="fas fa-exclamation-triangle" style="color:#CD5C5C"></i>';
                default: /* Error */
                    return '<i class="fas fa-times" style="color:#9400D3"></i>';
    }
};

/* Descripcion del estado de operatividad de una estacion para el sidebar */
function DescripcionEstadoEstacion(feature){
    switch(feature.properties.estado){
                case -1: /* Sin datos */
                    return 'Fuera de Servicio';
                case 0: /* Verde */
                    return 'Operativa, Sin avisos' ;
                case 1: /* Amarillo */
                    return 'Operativa, Aviso de Nivel Amarillo';
                case 2: /* Naranja */
                    return 'Operativa, Aviso de Nivel Naranja';
                case 3: /* Rojo */
                    return 'Operativa, Aviso de Nivel Rojo';
                default: /* Error */
                    return 'Error';
    }
};

/*Si la estacion es del tipo Spida, añade la última foto capturada de dicha estacion*/
function AddImagen(feature, data){
    if(feature.properties.red==1 && data.imagen!=undefined){
        return '<p><span style="font-weight: bold">Ultima imagen capturada: </span><span style="font-weight: normal">'+data.fecha_hora+'</span><p>'
        +'<img id="myImg" src="data:image/jpg;base64,'+data.imagen+'" alt="'+ data.estacion + ', ' +data.fecha_hora+'" style="width:100%" onclick="AbrirImagenModal(this.src,this.alt)">';
    }
    else if(feature.properties.red==1 && data.imagen==undefined){
        return '<p><span style="font-weight: bold">Ultima imagen capturada: </span><span style="font-weight: normal">Imagen no disponible</span><p>'
        +'<img id="myImg" src="../../../static/img/spida/mapa/imagen_no_disponible.png" style="display: block; margin-left: auto; margin-right: auto; max-width:300px; max-height:300px;"';
    }
    else{
        return '';
        //'<iframe id="Iframe" src="https://saihguadiana.com:32555/zm/index.php?action=login&view=postlogin&username=view&password=view&view=watch&mid=1" width = "100%" height = "500px"></iframe>';
    }
}

/*Si la estacion es del tipo Spida, añade la última foto capturada de dicha estacion*/
function AddTiempoAemet(feature, data){
    widget=feature.properties.widget
    if(widget !=undefined){    
        return '<p><span style="font-weight: bold">Tendencia de la evolución meteorológica en los próximos 3 días según Aemet:</span><p>'+
               '<div id="TiempoAemet" style="overflow: auto;text-align: center;padding-bottom: 15px;"><iframe id=\"iframe_aemet_id10024\" name=\"iframe_aemet_id10024\" src=\"http://www.aemet.es/es/eltiempo/prediccion/municipios/mostrarwidget/'+widget+'?w=g3p01110011ohmffffffw'+Math.floor(document.getElementById('sidebar').getBoundingClientRect().width-80)+'z251x4f86d9t95b6e9r1s8n2\" width=\"'+Math.floor(document.getElementById('sidebar').getBoundingClientRect().width-80)+'\" height=\"251\" frameborder=\"0\" scrolling=\"yes\"></iframe></div>';
    }
    else{
        return '';
    }
}



/*----------------------------------------------------------------------------------------
# FUNCIONES RELACIONADAS CON EL GRAFICO DE NIVEL DE RIO QUE VA A CONTENER EL PANEL SIDEBAR
-----------------------------------------------------------------------------------------*/

/*Funcion que carga los datos de nivel de rio de las ultimas 24 horas en formato Json de una estacion en un grafico */
function GraficoNivelRio(feature){
    map.spin(true);
    $.getJSON("/spida/valores24h/",{estacion: feature.properties.id, canal: 100}, function(data){
        var DatosSerie = [];
        $.each(data.valores, function(index, canal){
            element = [new Date(canal.fecha_hora_local).getTime(), canal.valor]
            DatosSerie.push(element);
        });

        /* console.log(DatosSerie) */
        PintarGraficoNivelRio(DatosSerie,feature.properties.N1,feature.properties.N2,feature.properties.N3);
    })
    .fail(function() { 
        console.log('Valores 24h Nivel de Rio request failed! '); 
    })
    .always(function() { 
        map.spin(false);
    }); 
};

/*Funcion que carga los datos de nivel de rio de las ultimas 24 horas en formato Json de una estacion en un grafico */
function GraficoNivelRioPrediccion(feature){
    map.spin(true);
    $.getJSON("/spida/prediccion24h/",{estacion: feature.properties.id, canal: 100}, function(data){
        var nivelrio = [];

        $.each(data.valores, function(index, canal){
            element = [new Date(canal.fecha_hora_local).getTime(), canal.valor]
            nivelrio.push(element);
        });

	var prednivelrio = [];

        $.each(data.prediccion, function(index, canal){
            element = [new Date(canal.fecha_hora_local).getTime(), canal.valor]
            prednivelrio.push(element);
        });

        PintarGraficoNivelRioPrediccion(nivelrio,
					prednivelrio,
					feature.properties.N1,
					feature.properties.N2,
					feature.properties.N3);
	// Actualizamos el titulo:
	var chart = $('#plot_prediccion_rio').highcharts();
	chart.setTitle({ text: 'SPIDA ' +  feature.properties.nombre + ': Nivel del río'});
    })
    .fail(function() { 
        console.log('Valores 24h Nivel de Rio request failed! '); 
    })
    .always(function() { 
        map.spin(false);
    }); 
};

function GraficoPrecipitacion(feature){
    map.spin(true);
    $.getJSON("/spida/valores24h/",{estacion: feature.properties.id, canal: 301}, function(data){
        var DatosSerie = [];
        $.each(data.valores, function(index, canal){
            element = [new Date(canal.fecha_hora_local).getTime(), canal.valor]
            DatosSerie.push(element);
        });

        /* console.log(DatosSerie) */
        PintarGraficoPrecipitacion(DatosSerie);
    })
    .fail(function() { 
        console.log('Valores 24h precipitacion request failed! '); 
    })
    .always(function() { 
        map.spin(false);
    }); 
};

function GraficoPrecipitacionPrediccion(feature){
    map.spin(true);
    $.getJSON("/spida/prediccion24h/",{estacion: feature.properties.id, canal: 302}, function(data){
        var precipitacion = [];

        $.each(data.valores, function(index, canal){
            element = [new Date(canal.fecha_hora_local).getTime(), canal.valor]
            precipitacion.push(element);
        });

	var predprecipitacion = [];

        $.each(data.prediccion, function(index, canal){
            element = [new Date(canal.fecha_hora_local).getTime(), canal.valor]
            predprecipitacion.push(element);
        });

        PintarGraficoPrecipitacionPrediccion(precipitacion, predprecipitacion);
	// Actualizamos el titulo:
	var chart = $('#plot_prediccion_lluvia').highcharts();
	chart.setTitle({ text: 'SPIDA ' +  feature.properties.nombre + ': ' + data.nombre});


    })
    .fail(function() { 
        console.log('Valores 24h Nivel de Rio request failed! '); 
    })
    .always(function() { 
        map.spin(false);
    }); 
};

/* Funcion que describe el diseño del grafico de nivel de rio */
function PintarGraficoNivelRio(DatosSerieNivelRio, N1, N2, N3){
    var valormax = Math.max.apply(Math, DatosSerieNivelRio.map(v => v[1]));
    var ymax = ((N3 > valormax) ? N3: valormax);
    ymax = 1.15*ymax
    
    Highcharts.setOptions({
        lang:{
            loading: 'Cargando...',
            months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            weekdays: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
            shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            exportButtonTitle: "Exportar",
            printButtonTitle: "Importar",
            rangeSelectorFrom: "Desde",
            rangeSelectorTo: "Hasta",
            rangeSelectorZoom: "Período",
            viewFullscreen: "Ver Modo Pantalla Completa",
            downloadPNG: 'Descargar imagen PNG',
            downloadJPEG: 'Descargar imagen JPEG',
            downloadPDF: 'Descargar imagen PDF',
            downloadSVG: 'Descargar imagen SVG',
            downloadCSV: 'Descargar CSV',
            downloadXLS: 'Descargar XLS', 
            viewData: 'Ver Tabla de Datos',
            printChart: 'Imprimir',
            resetZoom: 'Reiniciar zoom',
            resetZoomTitle: 'Reiniciar zoom',
            thousandsSep: ",",
            decimalPoint: '.'
        }
    });
    
    Highcharts.chart('container', {
        chart: {
            zoomType: 'x',
            style: {
                fontFamily: 'Roboto, sans-serif'
            }
        },
        title: {
            text: 'Grafico de Nivel de Río'
        },
        subtitle: {
            text: 'Representación gráfica de los datos registrados las últimas 24 horas'
        },
        credits: {
            enabled: false
        },
        tooltip: {
            shared : true,
            useHTML: true,
            formatter: function () {
                return 'Fecha: <b>' + Highcharts.dateFormat('%e %b %Y', this.x) + '</b><br>' +
                    'Hora: <b>' + Highcharts.dateFormat('%H:%M', this.x) +'</b><br>' +
                    '</b> Nivel río: <b>' + this.y + 'm </b><br>' +
                    '</b> Nivel N1: <b>' + N1 + 'm </b><br>' +
                    '</b> Nivel N2: <b>' + N2 + 'm </b><br>' +
                    '</b> Nivel N3: <b>' + N3 + 'm </b><br>';
            }
        },
        plotOptions: {
            series: {
                marker: {
                    enabled: false
                }
            },
            global: {
                useUTC: false,
                //timezoneOffset: 300 //UTC-5:00 time zone
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%b. %e',
                week: '%b. %e',
                month: '%b. %y',
                year: '%Y'
            },
            title: {
                text: 'Fecha/Hora'
            },
            labels:{
                format:'{value:%H:%M}'
            }
        },
        yAxis: [{
            min:0,
            max: ymax,
            labels: {
                format: '{value}',
                /*style: {
                  color: 'Black'
                  }*/
            },
            title: {
                text: '<b>Nivel de Río (metros) </b>',
                /*style: {
                  color: 'Black'
                  }*/
            },
            gridLineWidth: 0.1,
            plotBands: [
                { // Sin avisos
                    from: -Infinity,
                    to: N1,
                    color: {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgb(174, 243, 202)'],
                            [1, 'rgb(96, 240, 162)']
                        ]
                    },
                    label: {
                        text: 'Sin avisos',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Nivel N1: Amarillo
                    from: N1,
                    to: N2,
                    color: {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgb(255, 255, 188)'],
                            [1, 'rgb(255, 255, 116)']
                        ]
                    },
                    label: {
                        text: 'Nivel 1',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Light air
                    from: N2,
                    to: N3,
                    color:  {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgb(255, 197, 144)'],
                            [1, 'rgb(255, 181, 83)']
                        ]
                    },
                    label: {
                        text: 'Nivel 2',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Nivel N3: Rojo
                    from: N3,
                    to: Infinity,
                    color: {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgb(255, 136, 127)'],
                            [1, 'rgb(255, 84, 72)']
                        ]
                    },
                    label: {
                        text: 'Nivel 3',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                        
                    }
                }]
        }],
        navigator: {
            adaptToUpdatedData: false,
            series: {
                type: 'line',
                data: DatosSerieNivelRio
            }
        },
        series: [{
            name: "Nivel de Río",
            type: 'areaspline',
            data: DatosSerieNivelRio,
            lineColor: 'rgb(17, 43, 115)',
            showInNavigator: true
        }],
        exporting: {                   
            buttons: {
                contextButton: {
                    menuItems: menuChart /* variable definida en mapaSpida.html */
                }
            }
        },
        legend: {
            enabled: false
        },
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    plotOptions: {
                        series: {
                            marker: {
                                radius: 2.5
                            }
                        },
                        areaspline: {
                            fillOpacity: 0.5
                        }
                    }
                }
            }]
        }
    });
};

/* Funcion que describe el diseño del grafico de nivel de rio */
function PintarGraficoNivelRioPrediccion(NivelRio, PredNivelRio, N1, N2, N3){
    var valormax = Math.max.apply(Math, NivelRio.map(v => v[1]));
    var ymax = ((N3 > valormax) ? N3: valormax);
    ymax = 1.15*ymax
    
    Highcharts.setOptions({
        lang:{
            loading: 'Cargando...',
            months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            weekdays: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
            shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            exportButtonTitle: "Exportar",
            printButtonTitle: "Importar",
            rangeSelectorFrom: "Desde",
            rangeSelectorTo: "Hasta",
            rangeSelectorZoom: "Período",
            viewFullscreen: "Ver Modo Pantalla Completa",
            downloadPNG: 'Descargar imagen PNG',
            downloadJPEG: 'Descargar imagen JPEG',
            downloadPDF: 'Descargar imagen PDF',
            downloadSVG: 'Descargar imagen SVG',
            downloadCSV: 'Descargar CSV',
            downloadXLS: 'Descargar XLS', 
            viewData: 'Ver Tabla de Datos',
            printChart: 'Imprimir',
            resetZoom: 'Reiniciar zoom',
            resetZoomTitle: 'Reiniciar zoom',
            thousandsSep: ",",
            decimalPoint: '.'
        }
    });
    
    Highcharts.chart('plot_prediccion_rio', {
        chart: {
            zoomType: 'x',
            style: {
                fontFamily: 'Roboto, sans-serif'
            }
        },
        title: {
            text: 'Nivel de Río',
	    useHTML: true,
	    formatter: function () {
		return '<b> Nivel 1 = ' + N1 + ' m </b>';}
        },
        subtitle: {
            text: 'Valores registrados y de predicción para las últimas y próximas 24 horas respectivamente'
        },
        credits: {
            enabled: false
        },
        tooltip: {
            shared : true,
            useHTML: true,
            formatter: function () {
                return 'Fecha: <b>' + Highcharts.dateFormat('%e %b %Y', this.x) + '</b><br>' +
                    'Hora: <b>' + Highcharts.dateFormat('%H:%M', this.x) +'</b><br>' +
                    '<b> Nivel río: ' + this.y + ' m </b><br>';
            }
        },
        plotOptions: {
            series: {
                marker: {
                    enabled: false
                }
            },
            global: {
                useUTC: false,
                //timezoneOffset: 300 //UTC-5:00 time zone
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%b. %e',
                week: '%b. %e',
                month: '%b. %y',
                year: '%Y'
            },
            title: {
                text: 'Fecha/Hora'
            },
            labels:{
                format:'{value:%e %b %H:%M}'
            }
        },
        yAxis: [{
            min:0,
            max: ymax,
	    lineWidth: 1,
            labels: {
                format: '{value}',
                /*style: {
                  color: 'Black'
                  }*/
            },
            title: {
                text: '<b> m </b>',
                /*style: {
                  color: 'Black'
                  }*/
            },
            gridLineWidth: 0.1,
            plotBands: [
                { // Sin avisos
                    from: -Infinity,
                    to: N1,
                    color: {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgb(174, 243, 202)'],
                            [1, 'rgb(96, 240, 162)']
                        ]
                    },
                    label: {
                        text: 'Sin avisos',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Nivel N1: Amarillo
                    from: N1,
                    to: N2,
                    color: {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgb(255, 255, 188)'],
                            [1, 'rgb(255, 255, 116)']
                        ]
                    },
                    label: {
			useHTML: true,
			formatter: function () {
			    return '<b> Nivel 1 = ' + N1 + ' m </b><br>';},
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Light air
                    from: N2,
                    to: N3,
                    color:  {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgb(255, 197, 144)'],
                            [1, 'rgb(255, 181, 83)']
                        ]
                    },
                    label: {
			useHTML: true,
			formatter: function () {
			    return '<b> Nivel 2 = ' + N2 + ' m </b><br>';},
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Nivel N3: Rojo
                    from: N3,
                    to: Infinity,
                    color: {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgb(255, 136, 127)'],
                            [1, 'rgb(255, 84, 72)']
                        ]
                    },
                    label: {
			useHTML: true,
			formatter: function () {
			    return '<b> Nivel 3 = ' + N3 + ' m </b><br>';},
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                        
                    }
                }]
        }],
        navigator: {
            adaptToUpdatedData: false,
            series: {
                type: 'line',
                data: NivelRio
            }
        },
        series: [{
            name: "Valores registrados",
            type: 'areaspline',
            data: NivelRio,
            lineColor: 'rgb(17, 43, 115)',
            showInNavigator: true
        }, {
            name: "Prediccion",
            data: PredNivelRio,
	    dashStyle: 'Dash',
            lineColor: 'rgb(17, 43, 115)',
            showInNavigator: true
        }],
        exporting: {                   
            buttons: {
                contextButton: {
                    menuItems: menuChart /* variable definida en mapaSpida.html */
                }
            }
        },
        legend: {
            enabled: true
        },
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    plotOptions: {
                        series: {
                            marker: {
                                radius: 2.5
                            }
                        },
                        areaspline: {
                            fillOpacity: 0.5
                        }
                    }
                }
            }]
        }
    });
};


/* Funcion que describe el diseño del grafico de nivel de rio */
function PintarGraficoPrecipitacion(DatosSeriePrecipitacion){
    
    var pmax = 5;
    var valormax = Math.max.apply(Math, DatosSeriePrecipitacion.map(v => v[1]));
    var ymax = ((pmax > valormax) ? pmax: valormax);
    ymax = 1.15*ymax

    Highcharts.setOptions({
        lang:{
            loading: 'Cargando...',
            months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            weekdays: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
            shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            exportButtonTitle: "Exportar",
            printButtonTitle: "Importar",
            rangeSelectorFrom: "Desde",
            rangeSelectorTo: "Hasta",
            rangeSelectorZoom: "Período",
            viewFullscreen: "Ver Modo Pantalla Completa",
            downloadPNG: 'Descargar imagen PNG',
            downloadJPEG: 'Descargar imagen JPEG',
            downloadPDF: 'Descargar imagen PDF',
            downloadSVG: 'Descargar imagen SVG',
            downloadCSV: 'Descargar CSV',
            downloadXLS: 'Descargar XLS', 
            viewData: 'Ver Tabla de Datos',
            printChart: 'Imprimir',
            resetZoom: 'Reiniciar zoom',
            resetZoomTitle: 'Reiniciar zoom',
            thousandsSep: ",",
            decimalPoint: '.'
        }
    });
    
    Highcharts.chart('container2', {
        chart: {
            type: 'column',
            zoomType: 'x',
            style: {
                fontFamily: 'Roboto, sans-serif'
            }
        },
        title: {
            text: 'Precipitación acumulada en una hora'
        },
        subtitle: {
            text: 'Valores registrados las últimas 24 horas'
        },
        credits: {
            enabled: false
        },
        tooltip: {
            shared : true,
            useHTML: true,
            formatter: function () {
                return 'Fecha: <b>' + Highcharts.dateFormat('%e %b %Y', this.x) + '</b><br>' +
                    'Hora: <b>' + Highcharts.dateFormat('%H:%M', this.x) +'</b><br>' +
		    'prec. acumulada 1h: <b>' + this.y +'</b><br>';
            }
        },
        plotOptions: {
	    column: {
		borderWidth: 0.0
            },
            global: {
                useUTC: false,
                //timezoneOffset: 300 //UTC-5:00 time zone
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%b. %e',
                week: '%b. %e',
                month: '%b. %y',
                year: '%Y'
            },
            title: {
                text: 'Fecha/Hora'
            },
            labels:{
                format:'{value:%H:%M}'
            }
        },
        yAxis: [{
	    min: 0,
        max: ymax,
            labels: {
                format: '{value}',
                /*style: {
                  color: 'Black'
                  }*/
            },
            title: {
                text: '<b>Precipitacion Acum. 1h (mm) </b>',
                /*style: {
                  color: 'Black'
                  }*/
            },
            gridLineWidth: 0.1
        }],
        // navigator: {
        //     adaptToUpdatedData: false,
        //     series: {
        //         data: DatosSeriePrecipitacion
        //     }
        // },
        series: [{
            name: "Precipitación Acum. 1h",
            data: DatosSeriePrecipitacion,
	    pointPadding: 0,
            groupPadding: 0,
            borderWidth: 0,
            pointPlacement: -0.5
        }],
        exporting: {                   
            buttons: {
                contextButton: {
                    menuItems: menuChart /* variable definida en mapaSpida.html */
                }
            }
        },
        legend: {
            enabled: false
        },
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    plotOptions: {
                        series: {
                            marker: {
                                radius: 2.5
                            }
                        },
                        areaspline: {
                            fillOpacity: 0.5
                        }
                    }
                }
            }]
        }
    });
};

/* Funcion que describe el diseño del grafico de nivel de rio */
function PintarGraficoPrecipitacionPrediccion(precipitacion, predprecipitacion){

    var pmax = 5;
    var valormax = Math.max.apply(Math, predprecipitacion.map(v => v[1]));
    var ymax = ((pmax > valormax) ? pmax: valormax);
    ymax = 1.15*ymax

    
    Highcharts.setOptions({
        lang:{
            loading: 'Cargando...',
            months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
            weekdays: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
            shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            exportButtonTitle: "Exportar",
            printButtonTitle: "Importar",
            rangeSelectorFrom: "Desde",
            rangeSelectorTo: "Hasta",
            rangeSelectorZoom: "Período",
            viewFullscreen: "Ver Modo Pantalla Completa",
            downloadPNG: 'Descargar imagen PNG',
            downloadJPEG: 'Descargar imagen JPEG',
            downloadPDF: 'Descargar imagen PDF',
            downloadSVG: 'Descargar imagen SVG',
            downloadCSV: 'Descargar CSV',
            downloadXLS: 'Descargar XLS', 
            viewData: 'Ver Tabla de Datos',
            printChart: 'Imprimir',
            resetZoom: 'Reiniciar zoom',
            resetZoomTitle: 'Reiniciar zoom',
            thousandsSep: ",",
            decimalPoint: '.'
        }
    });
    
    Highcharts.chart('plot_prediccion_lluvia', {
        chart: {
            type: 'column',
            zoomType: 'x',
            style: {
                fontFamily: 'Roboto, sans-serif'
            }
        },
        title: {
            text: 'Precipitación acumulada en una hora en la cuenca'
        },
        subtitle: {
            text: 'Valores registrados y de predicción para las últimas y próximas 24 horas respectivamente'
        },
        credits: {
            enabled: false
        },
        tooltip: {
            shared : true,
            useHTML: true,
            formatter: function () {
                return 'Fecha: <b>' + Highcharts.dateFormat('%e %b %Y', this.x) + '</b><br>' +
                    'Hora: <b>' + Highcharts.dateFormat('%H:%M', this.x) +'</b><br>' +
		    'Valor: <b>' + this.y +' mm </b><br>';
            }
        },
        plotOptions: {
	     column: {
	     	groupPadding: -0.5
             },
            global: {
                useUTC: false,
                //timezoneOffset: 300 //UTC-5:00 time zone
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%b. %e',
                week: '%b. %e',
                month: '%b. %y',
                year: '%Y'
            },
            title: {
                text: 'Fecha/Hora'
            },
            labels:{
                format:'{value:%e %b %H:%M}'
            }
        },
        yAxis: [{
	    min: 0,
	    max: ymax,
	    lineWidth: 1,
            labels: {
                format: '{value}'
            },
            title: {
                text: '<b> mm </b>'
            },
            gridLineWidth: 0.1
        }],
        series: [{
            name: "Valores registrados",
            data: precipitacion,
	    pointPadding: 0,
            borderWidth: 0,
            pointPlacement: 0.0
        },{
            name: "Prediccion",
            data: predprecipitacion,
	    pointPadding: 0,
	    borderWidth: 0,
            pointPlacement: -1.0
        }],
        exporting: {                   
            buttons: {
                contextButton: {
                    menuItems: menuChart /* variable definida en mapaSpida.html */
                }
            }
        },
        legend: {
            enabled: true
        },
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    plotOptions: {
                        series: {
                            marker: {
                                radius: 2.5
                            }
                        },
                        areaspline: {
                            fillOpacity: 0.5
                        }
                    }
                }
            }]
        }
    });
};




//Funcion que carga las imagenes en una capa
function CargarImagenes(){
    map.spin(true);
    $.ajax({
        type: "GET",
        dataType: "json",
        url:"/spida/imagenesSpida/",
        success: function(data)
        {
            jsonImagenes=JSON.parse(data);
            var photos = [];
            for (var i = 0; i < jsonImagenes.length; i++) {
                if(jsonImagenes[i].id<8000){
                    photos.push({
                        lat: jsonImagenes[i].lat,
                        lng: jsonImagenes[i].lng,
                        url: jsonImagenes[i].imagen,
                        nombre: jsonImagenes[i].nombre,
                        caption: 'Ultima foto capturada el ' + jsonImagenes[i].fecha_hora +' en '+ jsonImagenes[i].nombre,
                        thumbnail: jsonImagenes[i].imagen,
                        id: jsonImagenes[i].id,
                        camara: jsonImagenes[i].camara
                    });
                }
            }

            photoLayer.clear();
            photoLayer.add(photos);
            map.spin(false);
            
            return jsonImagenes;
        }
    });
};

function AbrirImagenModal(imagen,descripcion){
    // Get the modal
    var modal = document.getElementById("myModalImagen");
    var modalImg = document.getElementById("img01");
    var captionText = document.getElementById("caption");
    modal.style.display = "block";
    modalImg.src = imagen;
    captionText.innerHTML = descripcion;
    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("closeImg")[0];

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
      modal.style.display = "none";
    }
}

/*Cuando pulso un marker de la miniatura de una imagen Spida, completo un Popup
con el nombre de la estacion, la imagen en tamaño original y la fecha/hora de la
imagen mostrada*/
function MarkerImagenSpida(layerphotos){
    map.spin(true);//activo el spin de cargando mapa
    var photo = layerphotos.photo;
    $.getJSON("/spida/imagen/",{estacion: photo.id, camara: photo.camara}, 
    function(data){

        template='<h5 id="titleBindPopUp">'+photo.nombre+'</h5>'
        +'<img id="myImg" src="data:image/jpg;base64,'+data.imagen+'" alt="'+photo.caption+'" style="width:100%" onclick="AbrirImagenModal(this.src,this.alt)">'
        +'<p id="contentBindPopUp">'+photo.caption+'</p>';
        
        layerphotos.bindPopup(L.Util.template(template, photo), {
            className: 'leaflet-popup-photo',
            maxWidth: 500
        }).openPopup(); 
    })
    .fail(function() { 
        console.log('Imagen request failed! '); 
    })
    .always(function() { 
        map.spin(false);
    });
};



/*----------------------------------------------------------------------------------------
#FUNCIONES RELACIONADAS CON EL DISEÑO DE LA CAPA QUE REPRESENTA EL ESTADO DEL CIELO (AEMET)
-----------------------------------------------------------------------------------------*/

/*Funcion que carga los datos GeoJson del estado del cielo de las estaciones Aemet en una capa*/
function MarkerCieloAemet(){
    map.spin(true);    
    $.getJSON("/spida/cielo/", 
    function(data){
        layer_estado_cielo_aemet.clearLayers();
        layer_estado_cielo_aemet.addData(data);

    })
    .fail(function() { 
        console.log('Estado del Cielo request failed! '); 
    })
    .always(function() { 
        map.spin(false);
    });  
};

/* Diseño de los Markers que indican el estado del cielo de las estaciones Aemet */ 
function createCustomIconCieloAemet(feature, latlng){
    let myIcon = L.icon({
        iconUrl: 'http://www.aemet.es/imagenes/png/estado_cielo/'+feature.properties.eCielo+'.png',
        iconSize: [40, 40], // width and height of the image in pixels*/
    })

    /* console.log(feature.properties.Municipio, feature.properties.eCielo); */
    return L.marker(latlng, {icon: myIcon}).bindPopup(
             '<img src="../../../static/img/spida/logos/logo_aemet.jpg" style="max-width:100%;max-height:100%;object-fit: contain;">'
            +'<br/><br/>'
            +'<p><span style="font-weight: bold;">Municipio: </span><span style="font-weight: normal;">'+feature.properties.Municipio+'</span></p>'
            +'<p><span style="font-weight: bold;">Estado: </span><span style="font-weight: normal;">'+EstadoCielo(feature)+'</span></p>',
            );
        
};

/*http://www.aemet.es/es/eltiempo/prediccion/espana/ayuda*/
/* Descripcion del estado del cielo Aemet */
function EstadoCielo(feature){
    switch(feature.properties.eCielo){
        case '11':
            return 'Cielo Despejado';
        case '11n':
            return 'Cielo Despejado';
        case '12':
            return 'Poco Nuboso';
        case '12n':
            return 'Poco Nuboso';
        case '13':
            return 'Intervalos Nubosos';
        case '13n':
            return 'Intervalos Nubosos';
        case '14':
            return 'Nuboso';
        case '14n':
            return 'Nuboso';
        case '15': 
            return 'Muy Nuboso';
        case '16':
            return 'Cubierto';
        case '17':
            return 'Nubes Altas';
        case '17n':
            return 'Nubes Altas';
        case '43':
            return 'Intervalos Nubosos con Lluvia escasa';
        case '44':
            return 'Nuboso con Lluvia escasa';
        case '44n':
            return 'Nuboso con Lluvia escasa';
        case '45':
            return 'Muy Nuboso con Lluvia escasa';
        case '46': 
            return 'Cubierto con Lluvia escasa';
        case '23':
            return 'Intervalos Nubosos con Lluvia';
        case '23n':
            return 'Intervalos Nubosos con Lluvia';
        case '24':
            return 'Nuboso con Lluvia';
        case '24n':
            return 'Nuboso con Lluvia';
        case '25': 
            return 'Muy Nuboso con Lluvia';
        case '26':
            return 'Cubierto con Lluvia';
        case '71':
            return 'Intervalos Nubosos con Nieve escasa';
        case '71n':
            return 'Intervalos Nubosos con Nieve escasa';
        case '17n':
            return 'Nubes Altas';
        case '72':
            return 'Nuboso con Nieve escasa';
        case '72n':
            return 'Nuboso con Nieve escasa';   
        case '73':
            return 'Muy Nuboso con Nieve escasa';
        case '74':
            return 'Cubierto con Nieve escasa';
        case '33':
            return 'Intervalos Nubosos con Nieve';
        case '33n':
            return 'Intervalos Nubosos con Nieve';
        case '34': 
            return 'Nuboso con Nieve';
        case '34n': 
            return 'Nuboso con Nieve';
        case '35':
            return 'Muy Nuboso con Nieve';
        case '36':
            return 'Cubierto con nieve';
        case '51':
            return 'Intervalos Nubosos con Tormenta';
        case '51n':
            return 'Intervalos Nubosos con Tormenta';
        case '52':
            return 'Nuboso con Tormenta';
        case '52n':
            return 'Nuboso con Tormenta';
        case '53':
            return 'Muy Nuboso con Tormenta';
        case '54': 
            return 'Cubierto con Tormenta';
        case '61': 
            return 'Intervalos Nubosos con Tormenta y Lluvia escasa';
        case '61n': 
            return 'Intervalos Nubosos con Tormenta y Lluvia escasa';
        case '62':
            return 'Nuboso con Tormenta y Lluvia escasa';
        case '62n':
            return 'Nuboso con Tormenta y Lluvia escasa';
        case '63':
            return 'Muy Nuboso con Tormenta y Lluvia escasa';
        case '64':
            return 'Cubierto con Tormenta y Lluvia escasa';
        case '81':
            return 'Niebla';
        case '82':
            return 'Bruma';
        case '83':
            return 'Calima';
        default:
            return '';
    };
};


/*----------------------------------------------------------------------------------------
#FUNCIONES RELACIONADAS CON EL DISEÑO DE LA CAPA QUE MUESTRA LA ULTIMA IMAGEN RADAR (AEMET)
-----------------------------------------------------------------------------------------*/

/* Funcion que carga la ultima imagen radar de Aemet */
function ImagenRadarAemet(){
    map.spin(true);    
    $.getJSON("/spida/radar/", 
    function(data){

        arr = data[0].Elementos;
        arr= arr.filter(innerArray => innerArray['Nombre radar'] == 'BAD');
        arr = arr.sort(function(a,b) { //ordeno el array con la primera columna (fecha/hora)
            return new Date(a["Fecha"][0]) - new Date(b["Fecha"][0]);
        });

        ultima_imagen=arr[arr.length-1]['Nombre fichero'];
        url='http://www.aemet.es/es/api-eltiempo/radar/imagen-radar/RN1/'+ultima_imagen;
        layer_radar.setUrl(url); 

    })
    .fail(function() { 
        console.log('Estado del Cielo request failed! '); 
    })
    .always(function() { 
        map.spin(false);
    }); 
};


/*----------------------------------------------------------------------------------------
#FUNCIONES RELACIONADAS CON EL DISEÑO DE LA CAPA QUE MUESTRA LAS IMAGENES DE PREDICCION DE PRECIPITACION (AEMET)
-----------------------------------------------------------------------------------------*/
/* Funcion que carga en el TimeDimension las imagenes de Precipitacion Acumulada 1 hora de Aemet */
function ImagenesPrecipitacionAcumulada1hAemet(){
    map.spin(true);
    $.getJSON("/spida/harmonie/", 
    function(data){

        arr=data[0]; //obtengo solo el array de datos
        arr = arr.sort(function(a,b) { //ordeno el array con la primera columna (fecha/hora)
            return new Date(a[0]) - new Date(b[0]);
        });

        date_from = arr[0][0];
        date_from = date_from.substring(0, date_from.length - 6)+"Z"; /* fecha comienzo */
        date_to = arr[arr.length-1][0];
        date_to = date_to.substring(0, date_to.length - 6)+"Z"; /* fecha fin */

        
        horaIni=(new Date(date_to)).getHours();
        switch(Math.floor(horaIni/6)){
            case 0:
                cod_url="00";
                break;
            case 1:
                cod_url="06";
                break;
            case 2:
                cod_url="12";
                break;
            case 3:
                cod_url="18";
                break;
            default:
                cod_url="00";
        };

        var ms = new Date().getTime() + 86400000/24*2;
        var msactual = new Date(ms);
        map.timeDimension.setAvailableTimes(date_from+"/"+date_to+"/PT1H",'replace');
        map.timeDimension.setCurrentTime(msactual); //establezco el valor actual de timeDimension (fecha_hora_actual)

    })
    .fail(function() { 
        console.log('Estado del Cielo request failed! '); 
    })
    .always(function() { 
        map.spin(false);
    }); 
};


/*----------------------------------------------------------------------------------------
#FUNCIONES RELACIONADAS CON EL DISEÑO DE LA CAPA QUE MUESTRA LOS AVISOS METEOROLOGICOS (AEMET)
-----------------------------------------------------------------------------------------*/

/* ZONAS METEOROLOGICAS AEMET (AVISOS MET AEMET) */
function styleZonaAemet(feature) {
    return {
    fillColor: getColorZonaAemet(feature.properties.fid),
    weight: 2,
    opacity: 0.5,
    color: getColorZonaAemet(feature.properties.fid),/*'black',*/
    dashArray: '2',
    fillOpacity: 0.5};
};

function getColorZonaAemet(d) {
    return d > 7 ? 'yellow' :
    d > 5 ? 'red' :
    d > 2 ? 'orange' :
    d > 0 ? 'transparent' :
    '#FFEDA0';
};

function getAvisosAemet(id) {
    return id > 5 ? 'Aviso Rojo por lluvias' :
    id > 2 ? 'Aviso Naranja por lluvias' :
    id > 0 ? 'Aviso Rojo por lluvias' :
    'Sin avisos';
};



/*----------------------------------------------------------------------------------------
#FUNCIONES RELACIONADAS CON LA CAPA BASE:
#-> layer_OpenStreetMap si es de dia
#-> layer_CartoDBDarkMatter si es de noche
-----------------------------------------------------------------------------------------*/

function HorariosSol(){
    $.ajax({
        type: "GET",
        dataType: "json",
        url:"/spida/solar/",
        success: function (data) {
            var result = checkIfTimeIsInRange(data.results.sunrise, data.results.sunset);
            /*console.log(result);*/
            if(result){
                map.addControl(layer_OpenStreetMap);
            }
            else{
                map.addControl(layer_CartoDBDarkMatter);
            }

        },
        error: function () {
            console.log("error al obtener el json de imagenes Precipitacion 1 h Aemet");
        }
    });
};

/* Devuelve True si La hora actual cae dentro de un rango de horas sin tener en cuenta la fecha */
function checkIfTimeIsInRange(salidaSol, puestaSol){
    
    var start=(new Date(salidaSol));/* Salida del Sol */
    /* console.log("Sunrise: "+sunrise); */

    var end=(new Date(puestaSol)); /* Puesta del Sol */
    /* console.log("Sunset: "+sunset) */

    var today = new Date();
    var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds(); 
    var d = today; /* Tiempo actual */


    if (start.getHours() < d.getHours() && d.getHours() < end.getHours()) {
        return true;
    } else if (start.getHours() == d.getHours()) {
        if (d.getHours() == end.getHours()) {
            if(start.getMinutes() <= d.getMinutes() && d.getMinutes() <= end.getMinutes()) {    
                return true
            } else {
                return false
            }
        } else if(start.getMinutes() <= d.getMinutes()) {
            return true
        } else {
            return false
        }
    } else if (d.getHours() == end.getHours()) {
        if(d.getMinutes() <= end.getMinutes()) {
            return true
        } else {
            return false
        }
    } else {
        return false
    }
}















