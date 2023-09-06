/**************************************************************
    BUSCADOR DE UNA ESTACION EN EL MAPA
**************************************************************/
var searchEstaciones = L.control.search({
    initial: false,
    propertyName: 'Nombre',
    marker: false,
    textPlaceholder: 'Buscar estación...',
    zoom: 18,
    autoCollapse: true
}).addTo(map);
/*PAULA: COMPLETAR CON UN ARRAY DEL NOMBRE DE LAS CAPAS PARA BUSCAR [layer_estaciones_spida, layer_estaciones_saih_guadiana, layer_estaciones_saih_tajo, layer_embalses] */
var layergroupEstaciones = L.layerGroup([]);
searchEstaciones.setLayer(layergroupEstaciones);

/**************************************************************
    CONTROL FULLSCREEN (MAPA A PANTALLA COMPLETA)
**************************************************************/
var controlFullScreen = L.control.fullscreen({
    title: {
        'false': 'Ver modo Pantalla Completa',
        'true': 'Salir del modo Pantalla Completa'
    }
}).addTo(map);

/**************************************************************
    CONTROL HOME Y AVANZAR O RETROCEDER MOVIMIENTOS HISTORICOS
**************************************************************/
var controlHome = L.control.navbar().addTo(map);


/**************************************************************
    PROGRESSBAR (ACTUALIZACIÓN AUTOMÁTICA DEL MAPA)
**************************************************************/
var progressBar = L.control({ position: "bottomleft" });

progressBar.onAdd = function (map) {
    var div = L.DomUtil.create("div", "progress");
    div.innerHTML += '<div id="bar" class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="300"></div>';
    return div;
};

map.addControl(progressBar);


/**************************************************************
    PANEL LAYERS (CONTROL DE CAPAS DEL MAPA)
**************************************************************/

//DEFINO LAS CAPAS BASE
var layer_ArcgisSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'); //satelite
var layer_OpenStreetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'); //calle
var layer_CartoDBDarkMatter = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png');
var layer_OpenStreetMapMunicipios = L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png');
var layer_OpenTopMap = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png');
var layer_StamenTerrain = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png');
var layer_ICA = L.tileLayer('https://osm.airvisual.net/pm25_layer/{z}/{x}/{y}.webp');
//var layer_Satelite = L.tileLayer('https://sat.windy.com/satellite/tile/deg41e/202303301545/{z}/{x}/{y}/visir.jpg');
//var layer_1 = L.tileLayer('https://rdr.windy.com/radar2/composite/2023/03/30/1610/{z}/{x}/{y}/reflectivity.png')

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
}];

//DEFINO EL RESTO DE CAPAS DEL MAPA
var overlayers = [{
    group: '<i id = "icon-title" class="fa-solid fa-globe-stand"></i><span style="font-weight: bold;">INFORMACIÖN GEOGRÁFICA DE REFERENCIA</span>',
    collapsed: false,
    layers: [
        {
            name: "División administrativa <br> Comunidad Autónoma de Extremadura",
            layer: layer_extremadura
        },
        {
            name: "Calidad del aire",
            layer: layer_ICA
        }/*,
        {
            name: "Satelite",
            layer: layer_Satelite
        },
        {
            name: "1",
            layer: layer_1
        }*/
    ]
}];

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


function setParent(el, newParent) {
    newParent.appendChild(el);
}
//AÑADO EL CONTROL DE CAPAS AL SIDEBAR
var htmlObject = myLayersControl.getContainer();
var a = document.getElementById('loader-control-layers')
setParent(htmlObject, a);




