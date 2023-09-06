/*-----------------------------------------------------------------------
# DEFINO LAS CAPAS DE MARCADORES 
(Estaciones Spida, Estaciones Saih Tajo, Estaciones Saih Guadiana, Embalses, Alarmas animadas y Subcuenca)
------------------------------------------------------------------------*/
var layer_alarmas_animadas = L.geoJson(null, { filter: function (feature) { return feature.properties.Estado > layer_alarmas_animadas_level }, pointToLayer: createCustomIconAlarm });
var layer_estaciones_spida = L.geoJSON(null, { filter: function (feature) { return feature.properties.Red == 1 }, pointToLayer: createCustomIconSpida }); //añado la capa de las estaciones spida
var layer_estaciones_saih_tajo = L.geoJSON(null, { filter: function (feature) { return feature.properties.Red == 2 }, pointToLayer: createCustomIconSaih }); //añado la capa de las estaciones del saih tajo
var layer_estaciones_saih_guadiana = L.geoJSON(null, { filter: function (feature) { return feature.properties.Red == 3 }, pointToLayer: createCustomIconSaih }); //añado la capa de las estaciones del saih guadiana
var layer_embalses = L.geoJSON(null, { pointToLayer: createCustomIconEmbalses }); //añado la capa de los embalses
var layer_estado_cielo_aemet = L.geoJSON(null, { filter: function (feature) { return (feature.properties.znaComarcal).substring(0, 2) == "70" }, pointToLayer: createCustomIconCieloAemet }); //añado la capa de las estaciones pluviometricas Aemet
var layer_temperatura_aemet = L.geoJSON(null, { filter: function (feature) { return (feature.properties.znaComarcal).substring(0, 2) == "70" }, pointToLayer: createCustomIconTemperaturaAemet }); //añado la capa de las estaciones pluviometricas Aemet
var layer_subcuenca = L.geoJSON(null, { style: { color: "#BA55D3", weight: 5, opacity: 0.65 } });
var layer_radar = L.imageOverlay('https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/HD_transparent_picture.png/1200px-HD_transparent_picture.png',
    L.latLngBounds([[47.590164999999985, -15.161928699999999], [31.236391685669023, 2.5890034440992875]]),
    {
        opacity: 1,
        errorOverlayUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/HD_transparent_picture.png/1200px-HD_transparent_picture.png',
    });


var fillOpacityZonasMetAemet = 0.5;
var layer_zonas_met_aemet = L.geoJson(aemet, {
    //style: styleZonaAemet,
    onEachFeature: function (feature, layer) {
        var div = L.DomUtil.create('div', 'highchart');
        layer.bindPopup(
            '<img src="../../../static/img/spd/logos/logo_aemet.jpg" style="max-width:100%;max-height:100%;object-fit: contain;">'
            + '<img src="../../../static/img/spd/logos/zona_' + feature.properties.fid + '.png" style="height:150px;left:50%;object-fit: contain;padding-top:10px">'
            //+ '<br/>'
            + '<p><span style="font-weight: bold;">Zona: </span><span style="font-weight: normal;">' + feature.properties.NOM_Z + '</span></p>'
            + '<p><span style="font-weight: bold;">Provincia: </span><span style="font-weight: normal;">' + feature.properties.NOM_PROV + '</span></p>'
            + '<p>Para más información haga click ' + '<a href="http://www.aemet.es/es/eltiempo/prediccion/avisos?w=hoy&a=pb" target="_blank">aquí</a></p>'
        );
    },
    opacity: 1,
    fillOpacity: fillOpacityZonasMetAemet,
    color: 'rgba(255,255,255,0)'
}).addTo(map);

var layer_extremadura = L.geoJson(extremadura, {
    opacity: 1,
    fillOpacity: 0.5,
    //fillOpacity: fillOpacityExtremadura,
    fillColor: '#1B1C1C',
    color: 'rgba(27,27,28,0.2)',//'#009CDD',
    invert: true
}).addTo(map);


/*var layer_imagenes_spida = L.photo.cluster().on('click', function (evt) {//dblclick
    //createCustomIconImagen(evt.layer);
});


/*----------------------------------------------------------------------------
# DEFINO COMO VAN A SER LOS MARCADORES EN FUNCION DE CADA CAPA DEFINIDA
---------------------------------------------------------------------------*/
/* Diseño de los Markers que indican las alarmas (N1, N2 y N3) */
function createCustomIconAlarm(feature, latlng) {
    let pulsingIcon = L.icon.pulse({
        iconSize: [20, 20], /* ancho y alto del icono */
        color: colorAlert(feature), /* color en funcion del estado (N1, N2, N3) */
        fillColor: 'transparent' /* relleno del circulo */
    });
    return L.marker(latlng, { icon: pulsingIcon });
};

/* Color de los circulos animados (L.icon.pulse) de alerta */
function colorAlert(feature) {
    switch (feature.properties.Estado) {
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

/* Diseño de los Markers de las estaciones SPIDA monitorizadas */
function createCustomIconEmbalses(feature, latlng) {

    //console.log("EMBALSE", feature)

    var html_marker = "<div class='marker-embalses'><i class='fas fa-water'></i><span>" + feature.properties.VolumenPorcentual + "%</span></div>";
    var html_tooltip = '<img src="' + logoTipoRed(feature) + '" style="max-width:100%;max-height:100%;object-fit: contain;">'
        + '<br/><br/>'
        + '<p><span style="font-weight: bold;">Embalse: </span><span style="font-weight: normal;">' + feature.properties.Nombre + '</span></p>'
        + '<p><span style="font-weight: bold;">Volumen porcentual: </span><span style="font-weight: normal;">' + feature.properties.VolumenPorcentual + '%</span>%</p>'
        + '<p><span style="font-weight: bold;">Fecha: </span><span style="font-weight: normal;">' + new Date(feature.properties.FechaHoraVP).toLocaleString() + '</span></p>';

    if (feature.properties.CaudalSalida != undefined && feature.properties.CaudalSalida > 0) {
        html_marker = "<div class='marker-embalses' style = 'border: 2px solid red'><i class='fas fa-water'></i><span>" + feature.properties.VolumenPorcentual + "%</span><span style='font-size:10px; font-weight: bold;'>" + Math.ceil(feature.properties.CaudalSalida) + "</span></div>";
        html_tooltip += '<p><span style="font-weight: bold;">Caudal aliviado: </span><span style="font-weight: normal;">' + feature.properties.CaudalSalida + ' m3/s ' + new Date(feature.properties.FechaHoraCS).toLocaleString() + '</span></p>';
    }

    var mymarker = L.divIcon({
        className: 'custom-div-icon',
        html: html_marker,
        iconSize: [60, 55],
        iconAnchor: [50, 50]
    });

    return L.marker(latlng, { icon: mymarker }
    ).bindTooltip(html_tooltip,
        {
            direction: 'left',
            className: 'leaflet-tooltip'
        }).on('click', function () {
            map.spin(true, spinner_options)
            $('#info-estacion').html('')
            //Abro el Sidebar y añado la informacion de la estacion
            $(".loader-info-estacion").fadeIn();
            document.getElementById("sidebar-contenido").scrollTop = 0;
            document.getElementById("sidebar-contenido").style.overflowY = 'hidden';
            //$(".loader-info-estacion").fadeIn();
            sidebar.open('estaciones')
            setTimeout(function () {
                InfoEstacion($("ul").find("li[data-value='" + feature.properties.Id + "']"));
            }, 1000);

        });;
};


var spinner_options = {
    color: '#ffffff',
    fadeColor: 'transparent',
    zIndex: 1999,
    top: '50%',
    left: '50%',
    position: 'absolute',
    animation: 'spinner-line-fade-more',

}


/* Diseño de los Markers de las estaciones SPIDA monitorizadas */
function createCustomIconSpida(feature, latlng) {
    //console.log("SPIDA", feature)

    if (feature.properties.Estado != 0 && feature.properties.Estado != 1 && feature.properties.Estado != 2 && feature.properties.Estado != 3) {
        var mymarker = L.ExtraMarkers.icon({
            prefix: 'fas',
            icon: iconMarkerEstacion(feature),
            iconColor: colorIconMarkerEstacion(feature.properties.Estado),
            markerColor: 'white'
            //extraClasses: classIconMarkerEstacion(feature)
        });
    }
    else {
        var mymarker = L.ExtraMarkers.icon({
            markerColor: 'white',
            innerHTML: iconMarkerLEDEstacion(feature)
        });
    }


    return L.marker(latlng, { icon: mymarker }
    ).bindTooltip(
        '<img src="' + logoTipoRed(feature) + '" style="max-width:100%;max-height:100%;object-fit: contain;">'
        + '<br/><br/>'
        + '<p><span style="font-weight: bold;">Estación: </span><span style="font-weight: normal;">' + feature.properties.Nombre + '</span></p>'
        + '<p><span style="font-weight: bold;">Nivel de Río: </span><span style="font-weight: normal;">' + feature.properties.NivelRio + '</span> m </p>'
        + '<p><span style="font-weight: bold;">Fecha: </span><span style="font-weight: normal;">' + new Date(feature.properties.FechaHora).toLocaleString() + '</span></p>'
        + '<p><span style="font-weight: bold;">Estado: </span></span>' + IconoEstadoEstacion(feature.properties.Estado) + '<span style="font-weight: normal"> ' + DescripcionEstadoEstacion(feature.properties.Estado) + '. </span></p>',
        {
            direction: 'left',
            className: 'leaflet-tooltip'
        }).on('click', function () {
            map.spin(true, spinner_options)
            $('#info-estacion').html('')
            //Abro el Sidebar y añado la informacion de la estacion
            $(".loader-info-estacion").fadeIn();
            document.getElementById("sidebar-contenido").scrollTop = 0;
            document.getElementById("sidebar-contenido").style.overflowY = 'hidden';
            //$(".loader-info-estacion").fadeIn();
            sidebar.open('estaciones')
            setTimeout(function () {
                InfoEstacion($("ul").find("li[data-value='" + feature.properties.Id + "']"));
            }, 1000);

        });
};

/* Diseño de los Markers de las estaciones SAIH monitorizadas */
function createCustomIconSaih(feature, latlng) {
    var mymarker = L.ExtraMarkers.icon({
        prefix: 'fas',
        icon: iconMarkerEstacion(feature),
        iconColor: colorIconMarkerEstacion(feature.properties.Estado),
        shape: 'penta',
        markerColor: '#1B1C1C', //'#7B68EE',//'#BA55D3',//'blue-dark'
        svg: true
    });

    return L.marker(latlng, { icon: mymarker }
    ).bindTooltip(
        '<img src="' + logoTipoRed(feature) + '" style="max-width:100%;max-height:100%;object-fit: contain;">'
        + '<br/><br/>'
        + '<p><span style="font-weight: bold;">Estación: </span><span style="font-weight: normal;">' + feature.properties.Nombre + '</span></p>'
        + '<p><span style="font-weight: bold;">Nivel de Río: </span><span style="font-weight: normal;">' + feature.properties.NivelRio + '</span> m </p>'
        + '<p><span style="font-weight: bold;">Fecha: </span><span style="font-weight: normal;">' + new Date(feature.properties.FechaHora).toLocaleString() + '</span></p>'
        + '<p><span style="font-weight: bold;">Estado: </span></span>' + IconoEstadoEstacion(feature.properties.Estado) + '<span style="font-weight: normal"> ' + DescripcionEstadoEstacion(feature.properties.Estado) + '. </span></p>',
        {
            direction: 'left',
            className: 'leaflet-tooltip'
        }).on('click', function () {
            map.spin(true, spinner_options)
            $('#info-estacion').html('')
            //Abro el Sidebar y añado la informacion de la estacion
            $(".loader-info-estacion").fadeIn();
            document.getElementById("sidebar-contenido").scrollTop = 0;
            document.getElementById("sidebar-contenido").style.overflowY = 'hidden';
            //$(".loader-info-estacion").fadeIn();
            sidebar.open('estaciones')
            setTimeout(function () {
                InfoEstacion($("ul").find("li[data-value='" + feature.properties.Id + "']"));
            }, 1000);

        });
};

/*Marcador como led*/
function iconMarkerLEDEstacion(feature) {
    switch (feature.properties.Estado) {
        case -1:
            return '<div class="led-box"><div class="led-black"></div></div>';
        case 0:
            return '<div class="led-box"><div class="led-green"></div></div>';
        case 1:
            return '<div class="led-box"><div class="led-yellow"></div></div>';
        case 2:
            return '<div class="led-box"><div class="led-orange"></div></div>';
        case 3:
            return '<div class="led-box"><div class="led-red"></div></div>';
        default:
            return '<div class="led-box"><div class="led-black"></div></div>';
    }
}

/*Tipo de icono en cada marcador en funcion de su estado*/
function iconMarkerEstacion(feature) {
    switch (feature.properties.Estado) {
        case -1:
            //return 'fa-exclamation-triangle';
            return 'fa-circle-x';
        case 0:
            return 'fa-check-circle';
        case 1:
            return 'fa-exclamation-triangle';
        case 2:
            return 'fa-exclamation-triangle';
        case 3:
            return 'fa-exclamation-triangle';
        default:
            return 'fa-exclamation';
    }
}

/*Color del icono en cada marcador en funcion de su estado*/
function colorIconMarkerEstacion(estado) {
    switch (estado) {
        case -1:
            //return '#000000';
            return '#7B68EE';
        case 0:
            //return '#90EE90';
            return '#abff00';
        case 1:
            //return 'yellow';
            return '#ff0';
        case 2:
            //return 'orange';
            return '#FFA500'
        case 3:
            //return '#CD5C5C';
            return '#FF0000'
        default:
            return 'violet';
    }
}

/*Funcion que añade una clase al marcador para el icono de dicho marcador darle un borde difuminado*/
function classIconMarkerEstacion(feature) {
    switch (feature.properties.Estado) {
        case -1:
            return 'icon-marker-estaciones-SinDatos';
        case 0:
            return 'icon-marker-estaciones-N0';
        case 1:
            return 'icon-marker-estaciones-N1';
        case 2:
            return 'icon-marker-estaciones-N2';
        case 3:
            return 'icon-marker-estaciones-N3';
        default:
            return '';
    }
}

/* Logo de la Red a la que pertenece una estacion */
function logoTipoRed(feature) {
    switch (feature.properties.Red) {
        case 1: //spida
            return '../../../static/img/spida/logos/logo_spida.png';
        case 2: //tajo
            return '../../../static/img/spida/logos/confederacion_tajo.jpg';
        case 3: //guadiana
            return '../../../static/img/spida/logos/confederacion_guadiana.png';
        default:
            return '';
    }
};

/* Icono que identifica el estado de operatividad de una estacion */
function IconoEstadoEstacion(estado) {
    switch (estado) {
        case -1: /* Sin datos */
            //return '<i class="fas fa-exclamation-triangle" style="color:#000000"></i>';
            return '<i class="fas fa-circle" style="color:#7B68EE;stroke: #1B1C1C;stroke-width: 20;"></i>';
        case 0: /* Verde */
            //return '<i class="fas fa-check" style="color:#90EE90"></i>';
            return '<i class="fas fa-circle" style="color:#abff00;stroke: #1B1C1C;stroke-width: 20;"></i>';
        case 1: /* Amarillo */
            //return '<i class="fas fa-exclamation-triangle" style="color:#FFFF00"></i>';
            return '<i class="fas fa-circle" style="color:#ff0;stroke: #1B1C1C;stroke-width: 20;"></i>';
        case 2: /* Naranja */
            //return '<i class="fas fa-exclamation-triangle" style="color:#FFA500"></i>';
            return '<i class="fas fa-circle" style="color:#FFA500;stroke: #1B1C1C;stroke-width: 20;"></i>';
        case 3: /* Rojo */
            //return '<i class="fas fa-exclamation-triangle" style="color:#CD5C5C"></i>';
            return '<i class="fas fa-circle" style="color:#FF0000;stroke: #1B1C1C;stroke-width: 20;"></i>';
        default: /* Error */
            return '<i class="fas fa-times" style="color:#9400D3;stroke: #1B1C1C;stroke-width: 20;"></i>';
    }
};

/* Descripcion del estado de operatividad de una estacion */
function DescripcionEstadoEstacion(estado) {
    switch (estado) {
        case -1: /* Sin datos */
            return 'Fuera de Servicio';
        case 0: /* Verde */
            return 'Operativa, Sin avisos';
        case 1: /* Amarillo */
            return 'Operativa, Aviso de Nivel Amarillo';
        case 2: /* Naranja */
            return 'Operativa, Aviso de Nivel Naranja';
        case 3: /* Rojo */
            return 'Operativa, Aviso de Nivel Rojo';
        default: /* Error */
            return 'No identificado';
    }
};

/*----------------------------------------------------------------------------------------
#FUNCIONES RELACIONADAS CON EL DISEÑO DE LA CAPA QUE REPRESENTA EL ESTADO DEL CIELO (AEMET)
-----------------------------------------------------------------------------------------*

/* Diseño de los Markers que indican el estado del cielo de las estaciones Aemet */
function createCustomIconCieloAemet(feature, latlng) {
    let myIcon = L.icon({
        iconUrl: 'http://www.aemet.es/imagenes/png/estado_cielo/' + feature.properties.eCielo + '.png',
        iconSize: [40, 40],
    })

    return L.marker(latlng, { icon: myIcon }).bindPopup(
        '<img src="../../../static/img/spd/logos/logo_aemet.jpg" style="max-width:100%;max-height:100%;object-fit: contain;">'
        + '<br/><br/>'
        + '<p><span style="font-weight: bold;">Municipio: </span><span style="font-weight: normal;">' + feature.properties.Municipio + '</span></p>'
        + '<p><span style="font-weight: bold;">Estado: </span><span style="font-weight: normal;">' + DescripcionEstadooCieloAemet(feature) + '</span></p>',
    );

};

/*http://www.aemet.es/es/eltiempo/prediccion/espana/ayuda*/
/* Descripcion del estado del cielo Aemet */
function DescripcionEstadooCieloAemet(feature) {
    switch (feature.properties.eCielo) {
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
        case '15n':
            return 'Muy Nuboso';
        case '16':
            return 'Cubierto';
        case '16n':
            return 'Cubierto';
        case '17':
            return 'Nubes Altas';
        case '17n':
            return 'Nubes Altas';
        case '43':
            return 'Intervalos Nubosos con Lluvia escasa';
        case '43n':
            return 'Intervalos Nubosos con Lluvia escasa';
        case '44':
            return 'Nuboso con Lluvia escasa';
        case '44n':
            return 'Nuboso con Lluvia escasa';
        case '45':
            return 'Muy Nuboso con Lluvia escasa';
        case '45n':
            return 'Muy Nuboso con Lluvia escasa';
        case '46':
            return 'Cubierto con Lluvia escasa';
        case '46n':
            return 'Muy Nuboso con Lluvia escasa';
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
        case '25n':
            return 'Muy Nuboso con Lluvia';
        case '26':
            return 'Cubierto con Lluvia';
        case '26n':
            return 'Cubierto con Lluvia';
        case '71':
            return 'Intervalos Nubosos con Nieve escasa';
        case '71n':
            return 'Intervalos Nubosos con Nieve escasa';
        case '17':
            return 'Nubes Altas';
        case '17n':
            return 'Nubes Altas';
        case '72':
            return 'Nuboso con Nieve escasa';
        case '72n':
            return 'Nuboso con Nieve escasa';
        case '73':
            return 'Muy Nuboso con Nieve escasa';
        case '73n':
            return 'Muy Nuboso con Nieve escasa';
        case '74':
            return 'Cubierto con Nieve escasa';
        case '74n':
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
        case '35n':
            return 'Muy Nuboso con Nieve';
        case '36':
            return 'Cubierto con nieve';
        case '36n':
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
        case '53n':
            return 'Muy Nuboso con Tormenta';
        case '54':
            return 'Cubierto con Tormenta';
        case '54n':
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
        case '63n':
            return 'Muy Nuboso con Tormenta y Lluvia escasa';
        case '64':
            return 'Cubierto con Tormenta y Lluvia escasa';
        case '64n':
            return 'Cubierto con Tormenta y Lluvia escasa';
        case '81':
            return 'Niebla';
        case '81n':
            return 'Niebla';
        case '82':
            return 'Bruma';
        case '82n':
            return 'Bruma';
        case '83':
            return 'Calima';
        case '83n':
            return 'Calima';

        default:
            console.log('NO IDENTIFICADO', feature.properties.eCielo, feature.properties.Municipio)
            return '';
    };
};

/*Cuando pulso un marker de la miniatura de una imagen Spida, completo un Popup
con el nombre de la estacion, la imagen en tamaño original y la fecha/hora de la
imagen mostrada*/
function createCustomIconImagen(layerphotos) {
    /*map.spin(true);*///activo el spin de cargando mapa
    var photo = layerphotos.photo;
    $.getJSON("/spida/imagen/", { estacion: photo.id, camara: photo.camara },
        function (data) {
            template = '<h5 id="titleBindPopUp">' + photo.nombre + '</h5>'
                + '<img id="myImg" src="data:image/jpg;base64,' + data.imagen + '" alt="' + photo.caption + '" style="width:100%" onclick="AbrirImagenModal(this.src,this.alt)">'
                + '<p id="contentBindPopUp">' + photo.caption + '</p>';

            layerphotos.bindPopup(L.Util.template(template, photo), {
                className: 'leaflet-popup-photo',
                maxWidth: 500
            }).openPopup();
        })
        .fail(function () {
            console.log('Imagen request failed! ');
        })
    /*.always(function() { 
        map.spin(false);
    });*/
};


/* Diseño de los Markers que indican la temperatura de las estaciones de Aemet */
function createCustomIconTemperaturaAemet(feature, latlng) {
    var mymarker = L.divIcon({
        className: 'custom-div-icon',
        html: "<div class='marker-temperature'><img src='https://cdn.pixabay.com/photo/2014/04/02/11/02/thermometer-305319__340.png' style='width:22px;'><span style='color: white; padding: 2px; border-radius: 10px; font-weight: bold; background:" + ColorTemperatura(feature) + ";'> " + feature.properties.Tempta + "°C </span></div>",
    });
    return L.marker(latlng, { icon: mymarker }
    ).bindPopup(
        '<img src="../../../static/img/spd/logos/logo_aemet.jpg" style="max-width:100%;max-height:100%;object-fit: contain;">'
        + '<br/><br/>'
        + '<p><span style="font-weight: bold;">Municipio: </span><span style="font-weight: normal;">' + feature.properties.Municipio + '</span></p>'
        + '<p><span style="font-weight: bold;">Temperatura: </span><span style="font-weight: normal;">' + feature.properties.Tempta + '</span> °C</p>',
    );
};

function ColorTemperatura(feature) {
    var temperatura = feature.properties.Tempta;
    if (temperatura <= -13) {
        return '#123e59';
    }
    if (-12 <= temperatura && temperatura <= -7) {
        return '#13628b';
    }
    if (-6 <= temperatura && temperatura <= -1) {
        return '#0096ce';
    }
    if (0 <= temperatura && temperatura <= 5) {
        return '#02b3c6';
    }
    if (6 <= temperatura && temperatura <= 11) {
        return '#66cfb7';
    }
    if (12 <= temperatura && temperatura <= 17) {
        return '#f4a239';
    }
    if (18 <= temperatura && temperatura <= 23) {
        return '#f06112';
    }
    if (24 <= temperatura && temperatura <= 29) {
        return '#ec350c';
    }
    if (30 <= temperatura && temperatura <= 35) {
        return '#c6300f';
    }
    if (temperatura >= 36) {
        return '#951008';
    }
    else {
        return 'yellow';
    }

};

/*----------------------------------------------------------------------------------------
#FUNCIONES RELACIONADAS CON EL DISEÑO DE LA CAPA QUE MUESTRA LOS AVISOS METEOROLOGICOS (AEMET)
-----------------------------------------------------------------------------------------*/

/* ZONAS METEOROLOGICAS AEMET (AVISOS MET AEMET) */
var estadoZonasMetAemet = []
function styleZonaAemet(feature) {
    var opacity = fillOpacityZonasMetAemet;
    return {
        fillColor: getColorZonaAemet(feature.properties.COD_Z),
        weight: 2,
        //opacity: 0.5,
        color: 'rgba(27,27,28,0.2)', //getColorZonaAemet(feature.properties.fid),//'black',
        //dashArray: '3',
        fillOpacity: opacity,
    };
};

function getColorZonaAemet(id) {
    var estadoZona = estadoZonasMetAemet.filter(item => String(item['id_zona_meteo_aemet']) == String(id))[0]

    if (estadoZona != undefined) {
        estadoZona = estadoZona['estado_aviso']
        //estadoZona = estadoZona[0].estado_aviso
    }

    switch (estadoZona) {
        case 1:
            return '#FFC300';
        case 2:
            return '#FF5733';
        case 3:
            return '#a70016';
        default:
            return 'transparent'
    }

    /*return estadoZona == 'Nivel amarillo' ? 'Aviso Amarillo por lluvias' :
        estadoZona == 'Nivel rojo' ? 'Aviso Rojo por lluvias' :
            estadoZona == 'Nivel naranja' ? 'Aviso naranja por lluvias' :
                estadoZona == 'Sin avisos' ? 'Sin avisos' :
                    'No identificado';*/
};

function getAvisosAemet(id) {
    var estadoZona = estadoZonasMetAemet.filter(item => item['id_zona_meteo_aemet'] == id)
    if (estadoZona != undefined) {
        estadoZona = estadoZona[0].estado_aviso
    }

    return estadoZona == 'Nivel amarillo' ? 'Aviso Amarillo por lluvias' :
        estadoZona == 'Nivel rojo' ? 'Aviso Rojo por lluvias' :
            estadoZona == 'Nivel naranja' ? 'Aviso naranja por lluvias' :
                estadoZona == 'Sin avisos' ? 'Sin avisos' :
                    'No identificado';
};
