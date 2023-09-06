/*--------------------------------------------------
# SEARCH BUSCADOR DE ESTACIONES MONITORIZADAS
---------------------------------------------------*/
var searchEstaciones = L.control.search({
    initial: false,
    propertyName: 'Nombre',
    marker: false,
    textPlaceholder: 'Buscar estación...',
    zoom: 18,
    autoCollapse: true
}).addTo(map);
var layergroupEstaciones = L.layerGroup([layer_estaciones_spida, layer_estaciones_saih_guadiana, layer_estaciones_saih_tajo, layer_embalses]);
searchEstaciones.setLayer(layergroupEstaciones);

/*--------------------------------------------------
# CONTROL ZOOM MAX/ZOOM MIN
--------------------------------------------------*/
//var controlZoom = new L.Control.Zoom({ position: 'topleft' }).addTo(map);

/*--------------------------------------------------
# CONTROL PANTALLA COMPLETA
--------------------------------------------------*/
var controlFullScreen = L.control.fullscreen({
    title: {
        'false': 'Ver modo Pantalla Completa',
        'true': 'Salir del modo Pantalla Completa'
    }
}).addTo(map);

/*-------------------------------------------------
# CONTROL HOME Y AVANZAR O RETROCEDER MOVIMIENTOS HISTORICOS
--------------------------------------------------*/
var controlHome = L.control.navbar().addTo(map);

/*-------------------------------------------------
# CONTROL EXPORTAR MAPA A IMAGEN (PRINT MAP)
--------------------------------------------------*/
/*var controlPrinter = L.easyPrint({
    title: 'Exportar mapa a imagen', //titulo del boton
    sizeModes: ['A4Landscape', 'A4Portrait'],//modos de impresion (tamaño original, A4 horizontal y A4 vertical)
    defaultSizeTitles: {A4Landscape: 'A4 Horizontal', A4Portrait: 'A4 Vertical'}, // titulos de los modos de impresion
    filename: 'mapa_spida',
    exportOnly: true, // indico que se exporta como png (si es false, me abre las opciones de impresion)
    hideControlContainer: true, //escondo los modos de impresion al cargar el mapa
    spinnerBgCOlor: '#0DC5C1',
    customSpinnerClass: 'epLoader',
      }).addTo(map);*/

/*var controlPrinter = L.control.bigImage({ position: 'topleft' }).addTo(map);*/

/********************************************************************
 PROGRESSBAR PARA RECARGA AUTOMATICA DE LA PAGINA
 *******************************************************************/
var progressBar = L.control({ position: "bottomleft" });

progressBar.onAdd = function (map) {
    var div = L.DomUtil.create("div", "progress");
    div.innerHTML += '<div id="bar" class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="300"></div>';
    return div;
};

map.addControl(progressBar);


/* -------------------------------------------------------------
# CONTROL TIMEDIMENSION
---------------------------------------------------------------*/
Date.prototype.format = function (mask, utc) {
    return dateFormat(this, mask, utc);
};

L.Control.TimeDimensionCustom = L.Control.TimeDimension.extend({
    _getDisplayDateFormat: function (date) {
        /* console.log(date.getDate() + " de "+ date.toLocaleString('default', { month: 'short' })+ " a las "+('00' + (date.getHours())).substr(-2)+":"+('00' + (date.getMinutes())).substr(-2)); */
        return date.toLocaleString('es-ES', { timeZone: 'UTC' }); // 08/19/2020 (month and day with two digits)/*new Date(date).toUTCString();*/
    }
});
var timeDimensionControl = new L.Control.TimeDimensionCustom({
    autoPlay: false,
    loopButton: true,
    compact: false,
    playerOptions: {
        buffer: 10,
        transitionTime: 500,
        loop: true,
    }
}).addTo(map);


/*--------------------------------------------------
# CONTROL DE CAPAS (PANEL LAYERS)
--------------------------------------------------*/

//DEFINO LAS CAPAS BASE
var layer_ArcgisSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'); //satelite
var layer_OpenStreetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'); //calle
var layer_CartoDBDarkMatter = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png');
var layer_OpenStreetMapMunicipios = L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png');
var layer_OpenTopMap = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png');
var layer_StamenTerrain = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png');

//DEFINO LA CAPA DE RIOS (HIDROGRAFIA DE EXTREMADURA)
var rios = L.tileLayer.wms("https://servicios.idee.es/wms-inspire/hidrografia", {
    layers: "HY.Network",
    format: 'image/png',
    transparent: true,
    opacity: 1,
    attribution: "IGN",
});

//DEFINO LAS CAPAS DE MANCHAS DE INUNDACION ARPSIS (T10, T100 , T500)
var T10 = L.tileLayer.wms("http://wms.mapama.es/sig/Agua/Riesgo/RiesgoPob_10/wms.aspx?", {
    layers: "NZ.RiskZone",
    format: 'image/png',
    transparent: true,
    opacity: 0.65,
    attribution: "IGN",
});
var T100 = L.tileLayer.wms("http://wms.mapama.es/sig/Agua/Riesgo/RiesgoPob_100/wms.aspx?", {
    layers: "NZ.RiskZone",
    format: 'image/png',
    transparent: true,
    opacity: 0.65,
    attribution: "IGN",
});
var T500 = L.tileLayer.wms("http://wms.mapama.es/sig/Agua/Riesgo/RiesgoPob_500/wms.aspx?", {
    layers: "NZ.RiskZone",
    format: 'image/png',
    transparent: true,
    opacity: 0.65,
    attribution: "IGN",
});



//  DEFINO LA CAPA DE IMAGENES DE PRECIPITACION ACUMULADA 1 HORA DE AEMET

var imageUrl1h = 'http://www.aemet.es/es/api-eltiempo/modelo-harmonie/imagen-modelo/61/PB/fc2021102900+001h00m_61_0-1_1HH_61_3857.tif_color.png',
    imageUrl3h = 'http://www.aemet.es/es/api-eltiempo/modelo-harmonie/imagen-modelo/61/PB/fc2021110300+003h00m_61_0-3_3HH_61_3857.tif_color.png',
    imageUrl6h = 'http://www.aemet.es/es/api-eltiempo/modelo-harmonie/imagen-modelo/61/PB/fc2021110300+006h00m_61_0-6_6HH_61_3857.tif_color.png',
    imageBounds = [
        [34.483878966725584, 4.992602158427742],
        [44.487500000000004, -11.0125]
    ];

var imageLayer1h = L.imageOverlay(imageUrl1h, imageBounds, { opacity: 0.5 }),
    imageLayer3h = L.imageOverlay(imageUrl3h, imageBounds, { opacity: 0.5 }),
    imageLayer6h = L.imageOverlay(imageUrl6h, imageBounds, { opacity: 0.5 });


var cod_url = "00";
var getImageUrlPrecipitacionAcumulada = function (baseUrl, time) {
    /*console.log("URL", baseUrl, new Date(time));*/
    fecha1 = new Date(map.timeDimension.getAvailableTimes()[0]);
    fecha2 = new Date(time);
    result = fecha2 - fecha1;
    result = Math.floor(result / (1000 * 60 * 60));
    var beginUrl = baseUrl.substring(0, baseUrl.lastIndexOf("/") + 3);
    var endUrl = baseUrl.substr(-24);
    var horaAcumulada = parseInt(baseUrl.substr(-25, 1));
    var strTime = fecha1.getFullYear() + ("0" + (fecha1.getMonth() + 1)).slice(-2) + ("0" + fecha1.getDate()).slice(-2);
    var url = beginUrl + strTime + cod_url + '+' + ('000' + (result + horaAcumulada)).substr(-3) + 'h00m_61_' + result + '-' + (result + horaAcumulada) + '_' + horaAcumulada + endUrl;
    return url;
};

var layer_precipitacion_acumulada_1h_aemet = L.timeDimension.layer.imageOverlay(imageLayer1h, {
    getUrlFunction: getImageUrlPrecipitacionAcumulada
});

var layer_precipitacion_acumulada_3h_aemet = L.timeDimension.layer.imageOverlay(imageLayer3h, {
    getUrlFunction: getImageUrlPrecipitacionAcumulada
});

var layer_precipitacion_acumulada_6h_aemet = L.timeDimension.layer.imageOverlay(imageLayer6h, {
    getUrlFunction: getImageUrlPrecipitacionAcumulada
});


// NOMBRO LAS CAPAS QUE VA A CONTENER EL MAPA 
var baselayers = [{
    group: '<i id="icon-title" class="fas fa-layer-group"></i><span style="font-weight: bold;">CAPAS BASE</span>',
    collapsed: false,
    collapsibleGroups: false,
    layers: [{
        active: true,
        name: "Open Street Map",
        layer: layer_OpenStreetMap
    }, {
        name: "ArcGIS Satelite",
        layer: layer_ArcgisSat
    }, {
        name: "CartoDB DarkMatter",
        layer: layer_CartoDBDarkMatter
    }, {
        name: "Open Street Map Municipios",
        layer: layer_OpenStreetMapMunicipios
    }, {
        name: "Open Top Map",
        layer: layer_OpenTopMap
    }, {
        name: "Stamen Terrain",
        layer: layer_StamenTerrain
    }
    ]
}]; //capas base


var overlayers = [{
    group: '<i id="icon-title" class="fas fa-tint"></i><span style="font-weight: bold;">SPIDA</span>',
    collapsed: false,
    layers: [{
        name: "Aforos en río - Spida",
        icon: '<i class=" fas fa-broadcast-tower" style="color:#8FBC8B; width:12px; height:12px;"></i>',
        layer: layer_estaciones_spida,
        radio: true,
        radiogroup: 'radio_spida',

    },
    {
        name: "Últimas imágenes - Spida",
        icon: '<i class="far fa-image" style="color:#9370DB; width:16px; height:16px;"></i>',
        layer: layer_imagenes_spida,
        radio: true,
        radiogroup: 'radio_spida'
    }
    ]
}, {
    group: '<i id="icon-title" class="fas fa-tint"></i><span style="font-weight: bold;">SAIHs</span>',
    collapsed: false,
    layers: [{
        name: "Aforos en río - Saih Tajo",
        icon: '<i class=" fas fa-broadcast-tower" style="color:#8FBC8B; width:12px; height:12px;"></i>',
        layer: layer_estaciones_saih_tajo
    },
    {
        name: "Aforos en río - Saih Guadiana",
        icon: '<i class=" fas fa-broadcast-tower" style="color:#8FBC8B; width:12px; height:12px;"></i>',
        layer: layer_estaciones_saih_guadiana,
    },
    {
        active: false,
        name: "Embalses",
        icon: '<i class="fa-solid fa-water-arrow-down" style="color:#8FBC8B; width:12px; height:12px;"></i>',
        layer: layer_embalses
    },
    {
        name: "Red Hidrográfica",
        icon: '<i class="fas fa-water" style="color: #0D6DC5; width:12px; height:12px;"></i>',
        layer: rios
    }
    ]
}, {
    group: '<i id = "icon-title" class="fa-solid fa-cloud"></i><span style="font-weight: bold;">AEMET</span>',
    collapsed: false,
    layers: [
        {
            active: true,
            name: "Estado del cielo",
            icon: '<i class="fa-regular fa-sun-bright" style="color:orange; width:12px; height:12px;"></i>',
            layer: layer_estado_cielo_aemet,
            radio: true,
            radiogroup: 'radio_temp_aemet'
        },
        {
            name: "Temperatura",
            icon: '<i class="fa-solid fa-temperature-high" style="color:red; width:12px; height:12px;"></i>',
            layer: layer_temperatura_aemet,
            radio: true,
            radiogroup: 'radio_temp_aemet'
        },
        {
            name: "Radar",
            icon: '<i class="fa-solid fas fa-braille" style="color:blue; width:12px; height:12px;"></i><br>',
            layer: layer_radar
        },
        {
            name: "Avisos Meteorologicos (Lluvias)",
            icon: '<i class="fa-solid fa-raindrops" style="color: #4682B4; width:12px; height:12px;"></i>',
            layer: layer_zonas_met_aemet,
        }
    ]
}, {
    group: controlLayerMapasPeligrosidad(),
    collapsed: false,
    layers: [
        {
            name: "T10",
            layer: T10
        }, {
            name: "T100",
            layer: T100
        }, {
            name: "T500",
            layer: T500
        }
    ]
}, {
    group: controlLayerPrecipitacionAcumuladaAemet(),
    collapsed: false,
    className: 'panel-yellow',
    layers: [
        {
            active: true,
            name: "En 1 hora - Aemet",
            //icon: '<i class="fas fa-cloud-showers-heavy" style="width:12px; height:12px;"></i>',
            layer: layer_precipitacion_acumulada_1h_aemet,
            radio: true,
            radiogroup: 'radio-precipitacion-acumulada-aemet',
            timedimension: true,
            hora: 1
        },
        {
            name: "En 3 horas - Aemet",
            //icon: '<i class="fas fa-cloud-showers-heavy" style="width:12px; height:12px;"></i>',
            layer: layer_precipitacion_acumulada_3h_aemet,
            radio: true,
            radiogroup: 'radio-precipitacion-acumulada-aemet',
            timedimension: true,
            hora: 3
        },
        {
            name: "En 6 horas - Aemet",
            //icon: '<i class="fas fa-cloud-showers-heavy" style="width:12px; height:12px;"></i>',
            layer: layer_precipitacion_acumulada_6h_aemet,
            radio: true,
            radiogroup: 'radio-precipitacion-acumulada-aemet',
            timedimension: true,
            hora: 6
        }
    ]
}, {
    group: '<i id = "icon-title" class="fa-solid fa-globe-stand"></i><span style="font-weight: bold;">INFORMACIÖN GEOGRÁFICA DE REFERENCIA</span>',
    collapsed: false,
    layers: [
        {
            name: "División administrativa <br> Comunidad Autónoma de Extremadura",
            layer: layer_extremadura
        }
    ]
}]; //otras capas

function controlLayerRadarAemet() {
    /*var div = L.DomUtil.create('div', 'info legend');
    var mm = ['0', '0.5', '1', '2', '5', '10', '20', '30', '40', '60', '80', '100', '120', '180', '250', '300'];

    div.innerHTML += '<p style="font-weight: bold; margin: 0px 0px 8px;">Precipitación Acumulada en 1h (mm)</p>';

    var legenda = "";
    for (var i = 0; i < mm.length; i++) {
        if (i == 0) {
            legenda +=
                '<p><span style="background:' + getColorPrecipitacion(mm[i]) + ';">' + mm[i] + '</span>';
        }
        else if (i == mm.length - 1) {
            legenda +=
                '<span style="background:' + getColorPrecipitacion(mm[i]) + '; ">' + mm[i] + '</span></p>';
        }
        else {
            legenda +=
                '<span style="background:' + getColorPrecipitacion(mm[i]) + '; ">' + mm[i] + '</span>';
        }
    }
    div.innerHTML += legenda;
    return div.outerHTML;*/
    var div = L.DomUtil.create('div', 'info legend especial');
    /*Funcion que obtiene los colores para la leyenda de la precipitacion acumulada 1 hora de aemet (Imagenes modelos numericos) */
    $.getJSON("/private/datos/radar/legend/",
        function (data) {
            var objectsArray = [];
            /*Obtengo el numero de colores que tiene la leyenda*/
            var numColors = 0;
            for (let i in data) {
                for (let j in data[i]) {
                    if (data[i][j].Valores != undefined) {
                        numColors = data[i].length;
                        objectsArray.push({ "RangoIni": data[i][j].Valores[0], "RangoFin": data[i][j].Valores[1], "Color": data[i][j].RGBA });
                    }
                }
            }
            var ValuesLegend = objectsArray;
            div.innerHTML += '<p style="font-weight: bold; margin: 0px 0px 8px;">Precipitación acumulada en 1 hora (mm)</p>';

            var legenda = "";
            for (var i = (ValuesLegend.length - 1); i >= 0; i--) {
                if (i == ValuesLegend.length - 1) {
                    legenda +=
                        '<p style="display: inline-table"><span style="text-align: center; background:rgba(' + ValuesLegend[i].Color[0] + ',' + ValuesLegend[i].Color[1] + ',' + ValuesLegend[i].Color[2] + ',' + ValuesLegend[i].Color[3] + '); color:white; font-weight: normal;">' + ValuesLegend[i].RangoIni + '</span> ';
                }
                else if (i == 0) {
                    legenda +=
                        '<span style="text-align: center; background:rgba(' + ValuesLegend[i].Color[0] + ',' + ValuesLegend[i].Color[1] + ',' + ValuesLegend[i].Color[2] + ',' + ValuesLegend[i].Color[3] + '); color:white; font-weight: normal;">' + ValuesLegend[i].RangoIni + '</span></p>';
                }
                else {
                    legenda +=
                        '<span style="text-align: center; background:rgba(' + ValuesLegend[i].Color[0] + ',' + ValuesLegend[i].Color[1] + ',' + ValuesLegend[i].Color[2] + ',' + ValuesLegend[i].Color[3] + '); color:white; font-weight: normal;">' + ValuesLegend[i].RangoIni + '</span> ';
                }
            }
            div.innerHTML += legenda;
            return div;
        })
        .fail(function () {
            console.log('getJSON Legenda Radar Aemet request failed! ');
            return '';
        });
    return div;
}

function controlLayerMapasPeligrosidad() {
    var cabecera = '<i id="icon-title" class="fas fa-house-damage"></i><span style="font-weight: bold;">MAPAS DE PELIGROSIDAD</span>';
    var div = L.DomUtil.create('div', 'info legend');
    var numPersonas = ['0', '1 - 101', '101 - 1001', '1001 - 5000', '> 5000'];

    div.innerHTML += '<p style="font-weight: bold; margin: 0px 0px 8px;">Número de habitantes estimados en la zona inundable</p>';

    var legenda = "";
    for (var i = 0; i < numPersonas.length; i++) {
        if (i == 0) {
            legenda +=
                '<p><span style="background:' + getColorMapasPeligrosidad(numPersonas[i]) + '; width:80px; color:white; font-weight: normal;">' + numPersonas[i] + '</span>';
        }
        else if (i == numPersonas.length - 1) {
            legenda +=
                '<span style="background:' + getColorMapasPeligrosidad(numPersonas[i]) + '; width:80px; color:white; font-weight: normal;">' + numPersonas[i] + '</span></p>';
        }
        else {
            legenda +=
                '<span style="background:' + getColorMapasPeligrosidad(numPersonas[i]) + '; width:80px; color:white; font-weight: normal;">' + numPersonas[i] + '</span>';
        }
    }
    div.innerHTML += legenda;
    return cabecera + div.outerHTML;
}

function getColorMapasPeligrosidad(d) {
    return d == '> 5000' ? '#800026' :
        d == '1001 - 5000' ? '#BD0026' :
            d == '101 - 1001' ? '#E31A1C' :
                d == '1 - 101' ? '#FC4E2A' :
                    d == '0' ? '#FD8D3C' :
                        '#FFEDA0';
}

function controlLayerPrecipitacionAcumuladaAemet() {
    var cabecera = '<i id="icon-title" class="fas fa-cloud-rain"></i><span style="font-weight: bold;">PRECIPITACIÓN</span>';
    var div = L.DomUtil.create('div', 'info legend');
    var mm = ['0', '0.5', '1', '2', '5', '10', '20', '30', '40', '60', '80', '100', '120', '180', '250', '300'];

    div.innerHTML += '<p style="font-weight: bold; margin: 0px 0px 8px;">Precipitación Acumulada (mm)</p>';

    var legenda = "";
    for (var i = 0; i < mm.length; i++) {
        if (i == 0) {
            legenda +=
                '<p><span style="background:' + getColorPrecipitacion(mm[i]) + ';">' + mm[i] + '</span>';
        }
        else if (i == mm.length - 1) {
            legenda +=
                '<span style="background:' + getColorPrecipitacion(mm[i]) + '; ">' + mm[i] + '</span></p>';
        }
        else {
            legenda +=
                '<span style="background:' + getColorPrecipitacion(mm[i]) + '; ">' + mm[i] + '</span>';
        }
    }
    div.innerHTML += legenda;
    return cabecera + div.outerHTML + '<div id="timeDimension-precipitacion"></div>';
}

function getColorPrecipitacion(d) {
    return d == '300' ? 'rgba(236,200,200,255)' :
        d == '250' ? 'rgba(219,141,140,255)' :
            d == '180' ? 'rgba(204,84,83,255)' :
                d == '120' ? 'rgba(255,0,0,255)' :
                    d == '100' ? 'rgba(255,61,3,255)' :
                        d == '80' ? 'rgba(255,122,8,255)' :
                            d == '60' ? 'rgba(255,186,15,255)' :
                                d == '40' ? 'rgba(255,255,0,255)' :
                                    d == '30' ? 'rgba(191,230,0,255)' :
                                        d == '20' ? 'rgba(128,204,0,255)' :
                                            d == '10' ? 'rgba(0,153,0,255)' :
                                                d == '5' ? 'rgba(0,178,64,255)' :
                                                    d == '2' ? 'rgba(0,204,128,255)' :
                                                        d == '1' ? 'rgba(51,245,222,255)' :
                                                            d == '0.5' ? 'rgba(176,224,230,255)' :
                                                                d == '0' ? 'rgba(19,49,52,0)' :
                                                                    '#FFEDA0';
}

var myLayersControl = L.control.panelLayers(baselayers, overlayers, {
    collapsed: false,
    collapsibleGroups: true,
    buildItem: function (item) {

        //console.log('ITEM', item.name)

        //Si se considera una capa base
        if (item.overlay == false) {
            var xyz = getXYZ(map.getCenter(), map.getZoom());
            if (typeof item.layer._tileZoom === 'undefined') item.layer._tileZoom = map.getZoom();  // a hack for layers that are not active
            var url = item.layer.getTileUrl(xyz);
            node = L.DomUtil.create('div', 'panel-thumb');
            node.style.background = "url('" + url + "')";

            return node;
        }


        //Si se trata de una capa wms
        if (item.layer.wmsParams != undefined) {
            if (item.layer.wmsParams.layers == "NZ.RiskZone") { //Si se trata de una capa wms de los mapas de peligrosidad
                var $slider = $('<div class="layer-slider">');

                var $input = $('<input type="text" value="' + item.layer.options.opacity + '" />');

                $slider.append($input);

                $input.ionRangeSlider({
                    //https://github.com/IonDen/ion.rangeSlider
                    min: 0.1,
                    max: 1,
                    step: 0.01,
                    hide_min_max: true,
                    hide_from_to: false,
                    from: item.layer.options.opacity,
                    onChange: function (o) {
                        item.layer.setOpacity(o.from);
                    }
                });

                return $slider[0];
            }
        }

        if (item.timedimension == true) {
            var $slider = $('<div class="layer-slider">');

            var $input = $('<input type="text" value="' + item.layer._baseLayer.options.opacity + '" />');

            $slider.append($input);

            $input.ionRangeSlider({
                //https://github.com/IonDen/ion.rangeSlider
                min: 0.1,
                max: 1,
                step: 0.01,
                hide_min_max: true,
                hide_from_to: false,
                from: item.layer._baseLayer.options.opacity,
                onChange: function (o) {
                    item.layer.setOpacity(o.from);
                }
            });

            return $slider[0];
        }

        //Si se trata de la imagen radar de Aemet
        if (item.name == 'Radar') {
            legend = controlLayerRadarAemet();
            //console.log(item);

            var $slider = $('<div class="layer-slider">');

            var $input = $('<input type="text" value="' + item.layer.options.opacity + '" />');

            $slider.append($input);

            $input.ionRangeSlider({
                //https://github.com/IonDen/ion.rangeSlider
                min: 0.1,
                max: 1,
                step: 0.01,
                hide_min_max: true,
                hide_from_to: false,
                from: item.layer.options.opacity,
                onChange: function (o) {
                    item.layer.setOpacity(o.from);
                }
            });

            $slider.append(legend);

            return $slider[0];

        }

        //Si se trata de los avisos de zonas meteorologicas aemet
        if (item.name == 'Avisos Meteorologicos (Lluvias)') {
            //$(layer_zonas_met_aemet.getContainer()).addClass('osmLayer');
            //Cargo el cuadro con los avisos pronosticados por aemet
            cuadroInfoAvisos = CargarCuadroInfoAvisosMetAemet(item);
            return cuadroInfoAvisos
        }

    }
}).addTo(map);


function CargarCuadroInfoAvisosMetAemet(item) {

    var $slider = $('<div class="layer-slider">');

    var $input = $('<input type="text" value="' + item.layer.options.fillOpacity + '" />');

    $slider.append($input);


    $input.ionRangeSlider({
        //https://github.com/IonDen/ion.rangeSlider
        min: 0,
        max: 1,
        step: 0.01,
        hide_min_max: true,
        hide_from_to: false,
        from: item.layer.options.fillOpacity,
        onChange: function (o) {
            //item.layer.options.fillOpacity=o.from;
            //layer_zonas_met_aemet.setOpacity(o.from)
            fillOpacityZonasMetAemet = o.from;
            layer_zonas_met_aemet.setStyle(styleZonaAemet);

        }
    });

    //return $slider[0];
    //return $slider[0];
    var $divAlertas = $('<div class="emergency-alerts">');

    CargarInfoAvisosMetAemet($divAlertas);

    var buttons = '<div class="emergency-alerts__cycle">'
        + '<input type="button" class="emergency-alerts__cycle--prev" value="Anterior">'
        + '<input type="button" class="emergency-alerts__cycle--next" value="Siguiente">'
        + '</div>'
    //+ '<div class="emergency-alerts__collapse">'
    //+ '<i class="fa-solid fa-chevron-up toggle"></i>'
    //+ '</div>'

    //$divAlertas.append($divContentAlertas);
    $divAlertas.append(buttons);
    $slider.append($divAlertas);


    /*console.log("PREVIO", avisos)
    if (avisos != null && length(avisos) > 0) {
        console.log("ENTRA")
        //Cargo tambien la capa shapefile zonas meteoalerta aemet
        estadoZonasMetAemet = data;
        layer_zonas_met_aemet.setStyle(styleZonaAemet);
    }*/
    var buttons = '<div class="emergency-alerts__cycle">'
        + '<input type="button" class="emergency-alerts__cycle--prev" value="Anterior">'
        + '<input type="button" class="emergency-alerts__cycle--next" value="Siguiente">'
        + '</div>'
    //+ '<div class="emergency-alerts__collapse">'
    //+ '<i class="fa-solid fa-chevron-up toggle"></i>'
    //+ '</div>'

    return $slider[0];
}


function CargarInfoAvisosMetAemet(divElement) {
    var $divContentAlertas = $('<div class="emergency-alerts__alert-group">');

    $.getJSON("../../../private/datos/avisos/meteorologicos/informacion/",
        function (data) {
            var contenido_html = '';
            avisos_met_aemet = data
            //Hay informacion de avisos meteorologicos
            if (data.length > 0) {
                for (var i = 0; i < data.length; i++) {

                    if (i == 0) {
                        contenido_html +=
                            '<div class="emergency-alert emergency-alert--' + (data[i].nivel).toLowerCase().replace(/\s+/g, '') + ' current">'
                            + '<div class="emergency-alert__content">'
                            + '<div class="emergency-alert__icon"><i class="fa-solid fa-raindrops"></i></div>'
                            + '<div class="emergency-alert__title">' + data[i].nivel + ' (' + String(i + 1) + '/' + String(data.length) + ')' + '</div>'
                            + '<div class="emergency-alert__zona">Zona: ' + data[i].nombre_zona_meteo_aemet + '</div>'
                            + '<div class="emergency-alert_probabilidad">Probabilidad: ' + data[i].probabilidad + '</div>'
                            + '<div class="emergency-alert__duracion">Duracion:  ' + data[i].infoDate + '</div>'
                            + '<div class="emergency-alert__link"><a href="#" onClick="a_onClick(\'' + data[i].nivel + '\',\'' + data[i].nombre_zona_meteo_aemet + '\',\'' + data[i].probabilidad + '\',\'' + data[i].infoDate + '\', \'' + data[i].descripcion + '\', \'' + data[i].instruccion + '\', \'emergency-alert--' + (data[i].nivel).toLowerCase().replace(/\s+/g, '') + '\')">+ información</a></div>'
                            + '</div>'
                            + '</div>'
                    }
                    else {
                        contenido_html +=
                            '<div class="emergency-alert emergency-alert--' + (data[i].nivel).toLowerCase().replace(/\s+/g, '') + '">'
                            + '<div class="emergency-alert__content">'
                            + '<div class="emergency-alert__icon"><i class="fa-solid fa-raindrops"></i></div>'
                            + '<div class="emergency-alert__title">' + data[i].nivel + ' (' + String(i + 1) + '/' + String(data.length) + ')' + '</div>'
                            + '<div class="emergency-alert__zona">Zona: ' + data[i].nombre_zona_meteo_aemet + '</div>'
                            + '<div class="emergency-alert_probabilidad">Probabilidad: ' + data[i].probabilidad + '</div>'
                            + '<div class="emergency-alert__duracion">Duracion:  ' + data[i].infoDate + '</div>'
                            + '<div class="emergency-alert__link"><a href="#" onClick="a_onClick(\'' + data[i].nivel + '\',\'' + data[i].nombre_zona_meteo_aemet + '\',\'' + data[i].probabilidad + '\',\'' + data[i].infoDate + '\', \'' + data[i].descripcion + '\', \'' + data[i].instruccion + '\', \'emergency-alert--' + (data[i].nivel).toLowerCase().replace(/\s+/g, '') + '\')">+ información</a></div>'
                            + '</div>'
                            + '</div>'
                    }
                }
                $('.emergency-alerts').show()
            } else {
                /*contenido_html +=
                    '<div class="emergency-alert emergency-alert--sinavisos current">'
                    + '<div class="emergency-alert__content">'
                    + '<div class="emergency-alert__icon"><i class="fa-solid fa-raindrops"></i></div>'
                    + '<div class="emergency-alert__title">No hay avisos meteorologicos</div>'
                    + '<div class="emergency-alert__link"><a href="https://www.aemet.es/es/eltiempo/prediccion/avisos">Para más información pulse aquí</a></div>'
                    + '</div>'
                    + '</div>'*/
                $('.emergency-alerts').hide()
                //const elements = document.getElementsByClassName('emergency-alerts');
                /*while (elements.length > 0) {
                    elements[0].parentNode.removeChild(elements[0]);
                }*/
            }

            estadoZonasMetAemet = data;
            layer_zonas_met_aemet.setStyle(styleZonaAemet);

            $divContentAlertas.append(contenido_html);

            if (divElement != undefined) {
                divElement.append($divContentAlertas)
            }
            else {
                const elements = document.getElementsByClassName('emergency-alerts__alert-group');
                while (elements.length > 0) {
                    elements[0].parentNode.removeChild(elements[0]);
                }
                $('.emergency-alerts').append($divContentAlertas)
            }
        })
        .fail(function () {
            console.log('getJSON Info Avisos Meteorologicos Aemet request failed! ');
        })
        .always(function () {
            CargarAvisosMetAemetPopup(avisos_met_aemet);
        });
}

function CargarAvisosMetAemetPopup() {


    $(".ZMA").each(function (index) {
        console.log('ZMA' + index + ": " + $(this).html());
    });
}


function a_onClick(nivel, zona, probabilidad, duracion, descripcion, instruccion, clase) {
    //console.log("ENTRA")
    //alert(prueba);
    Swal.fire({
        html: "<h3 class='text-bradley' style='font-size:30px'><b>Aviso meteorológico por lluvia</b></h3>" +
            "<div class='linea-divisoria'></div>" +
            "<br>" +
            "<p style='text-align:left; font-size:14px'><b>Nivel: </b>" + nivel + "</p>" +
            "<p style='text-align:left; font-size:14px'><b>Zona: </b>" + zona + "</p>" +
            "<p style='text-align:left; font-size:14px'><b>Probabilidad: </b>" + probabilidad + "</p>" +
            "<p style='text-align:left; font-size:14px'><b>Duración: </b>" + duracion + "</p>" +
            "<p style='text-align:left; font-size:14px'><b>Descripción: </b>" + descripcion + "</p>" +
            "<p style='text-align:left; font-size:14px'><b>Instrucción: </b>" + instruccion + "</p>",
        showConfirmButton: false,
        timer: 100000,
        timerProgressBar: true,
        customClass: {
            popup: clase,
            closeButton: 'buttonClose-swal'
        },
        focusConfirm: false,
        showCloseButton: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    })
}


function getXYZ(latlng, zoom) {
    function toRad(n) {
        return n * Math.PI / 180;
    }
    return {
        z: zoom,
        x: parseInt(Math.floor((latlng.lng + 180) / 360 * (1 << zoom))),
        y: parseInt(Math.floor((1 - Math.log(Math.tan(toRad(latlng.lat)) + 1 / Math.cos(toRad(latlng.lat))) / Math.PI) / 2 * (1 << zoom)))
    }
};


function setParent(el, newParent) {
    newParent.appendChild(el);
}
//AÑADO EL CONTROL DE CAPAS AL SIDEBAR
var htmlObject = myLayersControl.getContainer();
var a = document.getElementById('loader-control-layers')
setParent(htmlObject, a);




/*var legendPreMetedoNumericoAemet = L.control({position: 'bottomleft'});

legendPreMetedoNumericoAemet.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'pruebacontrol');
    
    return div;
};*/


var myInfoControl = L.control.info({
    position: 'topright',
    title: '<h1 id="title-aviso"> SIN AVISOS </h1>',
    titleTooltip: 'Avisos por riesgo de inundación',
    titleClass: 'titleStyle',
    contentClass: 'contentStyle'
})//.addTo(map);

//DEFINO EL PANEL INFO AVISOS (DESCRIPCION DE LOS DISTINTOS NIVELES DE RIESGO)
var contenido = '<p style="margin-bottom: 6pt; color:#00CED1; font-size:16px;">' +
    '<b id="cabecera-aviso">Tipos de Avisos por riesgo de inundación </b></p>' +
    '<p><i class="fas fa-exclamation-triangle" style="color:#000000"></i>' +
    ' SIN DATOS: Caracterizado por la falta de datos de nivel de río.</p>' +
    '<p><i class="fas fa-check" style="color:#90EE90"></i>' +
    ' NIVEL 0 o SIN AVISOS: Caracterizado por niveles de caudal muy bajos o casi inexistentes con ninguna significancia.</p>' +
    '<p><i class="fas fa-exclamation-triangle" style="color:#FFFF00"></i>' +
    ' NIVEL 1: Caracterizado por la existencia de información sobre un aumento del nivel de caudal a priori sin importancia.</p>' +
    '<p><i class="fas fa-exclamation-triangle" style="color:#FFA500"></i>' +
    ' NIVEL 2: Caracterizado por la posibilidad de ocurrencia de sucesos y/o situaciones capaces de dar lugar a un estado ' +
    'de riesgo de inundación en funcion de la evolución de los fenómenos causantes del aumento de nivel de caudal.</p>' +
    '<p><i class="fas fa-exclamation-triangle" style="color:#CD5C5C"></i>' +
    ' NIVEL 3: Caracterizado por la posibilidad de ocurrencia de sucesos y/o situaciones capaces de ' +
    'dar lugar a un estado de peligro, por inundación inminente o bien porque ésta ya ha comenzado.</p>'

myInfoControl.setContent(contenido);


/* Funcion que diseña el rotulo del cruadro de informacion de si hay avisos o no */
function InfoAvisosMap(geoJson) {

    var contNegro = geoJson.features.filter(item => item.properties['Estado'] == -1).length;
    var contVerde = geoJson.features.filter(item => item.properties['Estado'] == 0).length;
    var contAmarillo = geoJson.features.filter(item => item.properties['Estado'] == 1).length;
    var contNaranja = geoJson.features.filter(item => item.properties['Estado'] == 2).length;
    var contRojo = geoJson.features.filter(item => item.properties['Estado'] == 3).length;

    var html = '';

    if (contNegro > 0) {
        html += ' <i id="icon-aviso" class="fas fa-exclamation-triangle" style="color:#7B68EE"></i> '
    }
    if (contAmarillo > 0) {
        html += ' <i id="icon-aviso" class="fas fa-exclamation-triangle" style="color:#ff0"></i> '
    }
    if (contNaranja > 0) {
        html += ' <i id="icon-aviso" class="fas fa-exclamation-triangle" style="color:#FFA500"></i> '
    }
    if (contRojo > 0) {
        html += ' <i id="icon-aviso" class="fas fa-exclamation-triangle" style="color:#FF0000"></i> '
    }

    $('#avisos').html(html)
};


//AÑADO EL TIMEDIMENSION CONTROL AL CONTROL DE CAPAS SITUADO EN EL SIDEBAR
window.onload=function(){
    var htmlObject1 = timeDimensionControl.getContainer();
    document.getElementById('timeDimension-precipitacion').appendChild(htmlObject1)
    $(".looped").css("display", "none");
    $(".timecontrol-dateslider").css("display", "none");
    $(".timecontrol-speed").css("display", "none");
    $(".leaflet-bar-timecontrol ").css("margin-bottom", "5px");
    
}
