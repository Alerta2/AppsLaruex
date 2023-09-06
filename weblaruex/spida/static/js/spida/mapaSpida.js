
//DEFINO EL MAPA LEAFLET
var map = L.map('map',{
    minZoom:5, //especifico zoom minimo del mapa
    attributionControl: false,
    timeDimension: true,
    timeDimensionOptions: {
        period: "PT1H",
    },
/*     dragging: !L.Browser.mobile, 
    tap: !L.Browser.mobile */
    /* gestureHandling: true */
});


/* AÑADO EL TIME DIMENSION PARA LAS IMAGENES DE PRECIPITACION ACUMULADA 1H AEMET (PREDICCIÓN) */
Date.prototype.format = function (mask, utc) {
    return dateFormat(this, mask, utc);
};

L.Control.TimeDimensionCustom = L.Control.TimeDimension.extend({
    _getDisplayDateFormat: function(date){
        /* console.log(date.getDate() + " de "+ date.toLocaleString('default', { month: 'short' })+ " a las "+('00' + (date.getHours())).substr(-2)+":"+('00' + (date.getMinutes())).substr(-2)); */
        return date.toLocaleString('es-ES',{ timeZone: 'UTC' }); // 08/19/2020 (month and day with two digits)/*new Date(date).toUTCString();*/
    }
});
var timeDimensionControl = new L.Control.TimeDimensionCustom({
    autoPlay: false,
    loopButton: true,
    playerOptions: {
        buffer: 10,
        transitionTime: 500,
        loop: true,
    }
});

/* map.addControl(this.timeDimensionControl); */


/* AÑADO LA LEGENDA DE LA PRECIPITACION ACUMULADA 1H AEMET (PREDICCION) */
/*var legendPreAcum1h = L.control({ position: "bottomleft" });

legendPreAcum1h.onAdd = function(map) {
  var div = L.DomUtil.create("div", "legendPreAcum1h");
  //div.innerHTML += "<h4>Precipitación (mm)</h4>";
  div.innerHTML += '<img src="../../static/img/spida/aemet/precipitacion1h.PNG" alt="Leyenda Precipitación 1h" style="max-width:100%">';
  //div.innerHTML += '<i style="background: #477AC2"></i><span>Water</span><br>';
  //div.innerHTML += '<i style="background: #448D40"></i><span>Forest</span><br>';
  //div.innerHTML += '<i style="background: #E6E696"></i><span>Land</span><br>';
  //div.innerHTML += '<i style="background: #E8E6E0"></i><span>Residential</span><br>';
  //div.innerHTML += '<i style="background: #FFFFFF"></i><span>Ice</span><br>';
  //div.innerHTML += '<i class="icon" style="background-image: url(https://d30y9cdsu7xlg0.cloudfront.net/png/194515-200.png);background-repeat: no-repeat;"></i><span>Grænse</span><br>';
  return div;
};*/

var legendPreMetedoNumericoAemet = L.control({position: 'bottomleft'});

legendPreMetedoNumericoAemet.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend');
    /*Funcion que obtiene los colores para la leyenda de la precipitacion acumulada 1 hora de aemet (Imagenes modelos numericos) */
    $.getJSON("/spida/legendMN/", 
    function(data){
        var objectsArray = [];
        /*Obtengo el numero de colores que tiene la leyenda*/
        var numColors=0;
        for (let i in data) {
            for (let j in data[i]) {
                if(data[i][j].Valores!=undefined){
                    numColors= data[i].length;
                    /*console.log(data[i][j])
                    console.log("Incio: ",data[i][j].Valores[0]);
                    console.log("Fin: ",data[i][j].Valores[1]);
                    console.log("Color: ",data[i][j].RGBA)*/
                    objectsArray.push( { "RangoIni": data[i][j].Valores[0], "RangoFin": data[i][j].Valores[1], "Color":data[i][j].RGBA } );
                }
            }
        }

        
        var ValuesLegend = objectsArray;
        div.innerHTML += '<p style="font-weight: bold; margin: 0px 0px 8px;">Precipitación en 1 hora (mm)</p>';
        for (var i = (ValuesLegend.length-1); i >= 0; i--) {
            div.innerHTML +=
                '<span style="background:rgba('+ValuesLegend[i].Color[0]+','+ValuesLegend[i].Color[1]+','+ValuesLegend[i].Color[2]+','+ValuesLegend[i].Color[3]+');">'+ValuesLegend[i].RangoIni+'</span> ';
        }

        
    })
    .fail(function() { 
        console.log('getJSON Legenda Modelos Numericos Aemet request failed! '); 
    });
    return div;
};

var legendPreRadarAemet = L.control({position: 'bottomleft'});

legendPreRadarAemet.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend');
    /*Funcion que obtiene los colores para la leyenda de la precipitacion acumulada 1 hora de aemet (Imagenes modelos numericos) */
    $.getJSON("/spida/legendRadar/", 
    function(data){
        var objectsArray = [];
        /*Obtengo el numero de colores que tiene la leyenda*/
        var numColors=0;
        for (let i in data) {
            for (let j in data[i]) {
                if(data[i][j].Valores!=undefined){
                    numColors= data[i].length;
                    objectsArray.push( { "RangoIni": data[i][j].Valores[0], "RangoFin": data[i][j].Valores[1], "Color":data[i][j].RGBA } );
                }
            }
        }

        
        var ValuesLegend = objectsArray;
        div.innerHTML += '<p style="font-weight: bold; margin: 0px 0px 8px;">Precipitación acumulada en 1 hora (mm)</p>';
        for (var i = (ValuesLegend.length-1); i >= 0; i--) {
            div.innerHTML +=
                '<span style="background:rgba('+ValuesLegend[i].Color[0]+','+ValuesLegend[i].Color[1]+','+ValuesLegend[i].Color[2]+','+ValuesLegend[i].Color[3]+'); color:white; font-weight: normal;">'+ValuesLegend[i].RangoIni+'</span> ';
        }     
    })
    .fail(function() { 
        console.log('getJSON Legenda Modelos Numericos Aemet request failed! '); 
    });
    return div;
};




/* AÑADO LA LEGENDA DE LA PRECIPITACION ACUMULADA 1H AEMET (PREDICCION) */
var progressBar = L.control({ position: "bottomleft" });

progressBar.onAdd = function(map) {
  var div = L.DomUtil.create("div", "progress");
  div.innerHTML += '<div id="bar" class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="300"></div>';
  return div;
};




//DEFINO EL CONTORNO DE LAS PROVINCIAS DE EXTREMADURA
var provincias=L.geoJson(provincias,{
    style: {
    fillColor: 'transparent',
    weight: 2,
    color: '#3CB371',
    dashArray: '2',
    fillOpacity: 0.3}
});

map.fitBounds(provincias.getBounds());//Ajusto el mapa al contorno de extremadura

map.createPane('left');
map.createPane('right');

//DEFINO LAS CAPAS BASE
var layer_ArcgisSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'); //satelite
var layer_OpenStreetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'); //calle
var layer_CartoDBDarkMatter = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png');
var layer_OpenStreetMapMunicipios = L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png');
var layer_OpenTopMap = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png');
var layer_StamenTerrain = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png');

/* AÑADO EL SIDE BY SIDE PARA PODER TENER DOS VISTAS DE MAPAS A LA VEZ */

var sidebyside = L.control.sideBySide(layer_ArcgisSat,layer_OpenStreetMap);  /*.addTo(map);*/


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


//DEFINO EL PANEL LATERAL SIDEBAR
var sidebar = L.control.sidebar('sidebar', {
    closeButton: true,
    position: 'left'
});

map.on('click', function () { //cuando hago click sobre el mapa escondo el sidebar si estuviera abierto
    sidebar.hide();
});

//DEFINO EL BOTOM HOME (CENTRA EL MAPA EN EXTREMADURA)
var botonHome = L.easyButton({
    states: [{
            stateName: 'zoom-to', // nombre del estado
            icon: '<i class="fas fa-home" style="font-size:20px;"></i>', // nombre del icono
            title: 'Ajustar mapa', // titulo del boton
            onClick: function(btn, map) { // evento del boton
                map.fitBounds(provincias.getBounds());
            }
    }]
});

//DEFINO EL BOTON INFO (MUESTRA EL MODA CON LA INFORMACION DE DATOS SUJETOS A VALIDACION)
var botonInfo = L.easyButton({
    position: 'topright',
    states: [{
            icon:'<span style="font-size:14px;">Datos provisionales sujetos a validación </span><i class="fas fa-exclamation-circle" style="color: #FF8C00; font-size:20px;padding-bottom: 4px; display: inline-flex; vertical-align: middle;"></i>',//'fa-info', // nombre del icono
            title: 'Datos sujetos a validacion', // titulo del boton
            position: 'topright',
            onClick: function(btn, map) { // evento del boton
/*                 $("#myModal").modal({
                    fadeDuration: 1000,
                    fadeDelay: 0.50
                  }); */
                  /* document.getElementById('myModal').style.display='none'; */
                  $('#myModal').modal('show');
            }
    }]
});

//DEFINO EL BOTON DE PANTALLA COMPLETA
var botonFullScreen = L.control.fullscreen({
    title: {
        'false': 'Ver modo Pantalla Completa',
        'true': 'Salir del modo Pantalla Completa'
    }
});

//BOTOM IMPRIMIR MAPA
var botonPrinter = L.easyPrint({
    title:'Imprimir mapa', //titulo del boton
    sizeModes: ['A4Landscape', 'A4Portrait'], //modos de impresion (tamaño original, A4 horizontal y A4 vertical)
    defaultSizeTitles: {A4Landscape: 'A4 Horizontal', A4Portrait: 'A4 Vertical'}, // titulos de los modos de impresion
    filename: 'mapa', // nombre del archivo impreso
    exportOnly: true, // indico que se exporta como png (si es false, me abre las opciones de impresion)
    hideControlContainer: true, //escondo los modos de impresion al cargar el mapa
});

//BOTON PARA CONOCER MI UBICACION ACTUAL
var botonUbicacionActual = L.control.locate({
    strings: {
        title: "Conocer mi ubicacion actual",
        popup: "Mi ubicacion actual"
    }
});


//BOTOM CREDITOS LARUEX
/* var credctrl = L.controlCredits({
    image: "{% static 'img/spida/logos/logo_alerta2.jpg' %}", //logo (ajustar el tamaño del icono utilizado)
    link: "https://www.laruex.com/", //direccion url a la que quiero ir
    text: "Mapa interactivo realizado por<br/> Laruex - Alerta2", //texto que quiero mostrar
    height:45, //altura del boton credito en funcion del tamaño del logo utilizado
    width:132 //anchura del boton credito en funcion del tamaño del logo utilizado
}).addTo(map); */


//ABRO EL MODAL INFORMATIVO DE LOS DATOS PROVISIONALES AL CARGAR LA PAGINA
/*$(function(){
 $("#myModal").modal();
}); */


//DEFINO EL PANEL INFO AVISOS (DESCRIPCION DE LOS DISTINTOS NIVELES DE RIESGO)
var contenido = '<p style="margin-bottom: 6pt; color:#00CED1; font-size:16px;">'+
                '<b id="cabecera-aviso">Tipos de Avisos por riesgo de inundación </b></p>'+
                '<p><i class="fas fa-exclamation-triangle" style="color:#000000"></i>'+
                ' SIN DATOS: Caracterizado por la falta de datos de nivel de río.</p>'+
                '<p><i class="fas fa-check" style="color:#90EE90"></i>'+
                ' NIVEL 0 o SIN AVISOS: Caracterizado por niveles de caudal muy bajos o casi inexistentes con ninguna significancia.</p>'+
                '<p><i class="fas fa-exclamation-triangle" style="color:#FFFF00"></i>'+
                ' NIVEL 1: Caracterizado por la existencia de información sobre un aumento del nivel de caudal a priori sin importancia.</p>'+
                '<p><i class="fas fa-exclamation-triangle" style="color:#FFA500"></i>'+
                ' NIVEL 2: Caracterizado por la posibilidad de ocurrencia de sucesos y/o situaciones capaces de dar lugar a un estado '+
                'de riesgo de inundación en funcion de la evolución de los fenómenos causantes del aumento de nivel de caudal.</p>'+
                '<p><i class="fas fa-exclamation-triangle" style="color:#CD5C5C"></i>'+
                ' NIVEL 3: Caracterizado por la posibilidad de ocurrencia de sucesos y/o situaciones capaces de '+
                'dar lugar a un estado de peligro, por inundación inminente o bien porque ésta ya ha comenzado.</p>'

var myInfoControl = L.control.info({
    position: 'topright',
    title: '<h1 id="title-aviso"> SIN AVISOS </h1>',
    titleTooltip: 'Avisos por riesgo de inundación',
    titleClass: 'titleStyle',
    contentClass: 'contentStyle'
});

myInfoControl.setContent(contenido);
    

//DEFINO EL CONTROL DE MINI MAPA
var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var osmAttrib='Map data &copy; OpenStreetMap contributors';
var osm2 = new L.TileLayer(osmUrl, {minZoom: 6, maxZoom: 6, attribution: osmAttrib });
var rect1 = {color: "#ff1100", weight: 3};
var rect2 = {color: "#0000AA", weight: 1, opacity:0, fillOpacity:0};
var miniMap = new L.Control.MiniMap(osm2, {
    toggleDisplay: true,
    position: 'bottomleft',
    aimingRectOptions : rect1,
    shadowRectOptions: rect2,
    width:300,
    height:300,
    minimized: true,
    //collapsedWidth: 40,
    //collapsedHeight: 40
});

var EventedMiniMap = L.Control.MiniMap.extend({ //Funciones del minimapa
    includes: L.Mixin.Events,
    _minimize: function () {
        L.Control.MiniMap.prototype._minimize.call(this);
        this.fire("minimized");
    },
    _restore: function () {
        L.Control.MiniMap.prototype._restore.call(this);
        this.fire("restore");
    },
});


//DEFINO LA CAPA DE IMAGENES SPIDA
var photoLayer = L.photo.cluster().on('click', function (evt) {//dblclick
    MarkerImagenSpida(evt.layer);
});

//DEFINO LA CAPA DE ESTACIONES SPIDA
var layer_alarmas_animadas=L.geoJson(null,{pointToLayer: createCustomIconAlarm }); //añado la capa de la alarmas animadas
var layer_estaciones_spida=L.geoJSON(null,{filter: function(feature) { return feature.properties.red == 1},pointToLayer: createCustomIconSPIDA}); //añado la capa de las estaciones spida
var layer_estaciones_saih_tajo=L.geoJSON(null,{filter: function(feature) { return feature.properties.red == 2}, pointToLayer: createCustomIconSPIDA}); //añado la capa de las estaciones del saih tajo
var layer_estaciones_saih_guadiana=L.geoJSON(null,{filter: function(feature) { return feature.properties.red == 3}, pointToLayer: createCustomIconSPIDA}); //añado la capa de las estaciones del saih guadiana
var layer_estado_cielo_aemet=L.geoJSON(null,{filter: function(feature) { return (feature.properties.znaComarcal).substring(0,2) == "70"}, pointToLayer: createCustomIconCieloAemet}); //añado la capa de las estaciones del saih guadiana

//DEFINO LAS VARIABLES NECESARIAS PARA FUNCIONES DE funcionesMapaSpida.js
var contEstacionesSinDatos=0;
var contEstacionesNivelVerde=0;
var contEstacionesNivelAmarillo=0;
var contEstacionesNivelNaranja=0;
var contEstacionesNivelRojo=0;

//DEFINO EL CONTROL DE CAPAS O PANEL LAYER
var baselayers = [];
var overLayers = []; //otras capas

var myLayersControl = L.control.panelLayers(baselayers, overLayers, {
    compact: true,
    collapsed: true,
    collapsibleGroups: true,
    buildItem: function(item) {
        /*console.log(item);*/

        /*console.log("WMS PARAMS "+item.layer.wmsParams); */
        if(item.layer._url!=undefined && item.layer.wmsParams==undefined){
           /*  console.log("Ha entrado -> "+item.layer._url) */
            var xyz = getXYZ(map.getCenter(), map.getZoom() );
            if (typeof item.layer._tileZoom === 'undefined') item.layer._tileZoom = map.getZoom();  // a hack for layers that are not active
            var url = item.layer.getTileUrl( xyz );
            node = L.DomUtil.create('div','panel-thumb');
            node.style.background = "url('"+url+"') no-repeat center";
            //node.innerHTML = item.name;
            return node;
        }
        else if(item.layer.wmsParams!=undefined){
            if(item.layer.wmsParams.layers=="NZ.RiskZone"){
                var $slider = $('<div class="layer-slider">');

                var $input = $('<input type="text" value="' + item.layer.options.opacity + '" />');
    
                $slider.append($input);
    
                $input.ionRangeSlider({
                    /*https://github.com/IonDen/ion.rangeSlider*/
                    min: 0.1,
                    max: 1,
                    step: 0.01,
                    hide_min_max: true,
                    hide_from_to: false,
                    from: item.layer.options.opacity,
                    onChange: function(o) {
                        item.layer.setOpacity(o.from);
                    }
                });
    
                return $slider[0];
            }
        }
        else
            return null;
            
    } 
});

function getXYZ(latlng, zoom) {
    function toRad(n) {
    return n * Math.PI / 180;
    }
    return {
        z: zoom,
        x: parseInt(Math.floor( (latlng.lng + 180) / 360 * (1<<zoom) )),
        y: parseInt(Math.floor( (1 - Math.log(Math.tan(toRad(latlng.lat)) + 1 / Math.cos(toRad(latlng.lat))) / Math.PI) / 2 * (1<<zoom) ))
    }
}


//DEFINO LA LEYENDA DE LAS CAPAS WMS
var legend = L.control({position: 'bottomleft'});

legend.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'legend');
    div.innerHTML =
        '<span><img src= "https://wms.mapama.gob.es/sig/Agua/Riesgo/RiesgoPob_10/Leyenda/RiesgoPob_10.png" style="border-radius:10px;"></span>'; /*Mapas de manchas de inundacion*/
       
        /* '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=farms&STYLE="+' height="40px" align="top";>&nbsp;&nbsp;&nbsp; Farms</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=Conservancy%20Outline&STYLE="+' height="40px" align="top";>&nbsp;&nbsp;&nbsp; Conservancy Outline</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=Land%20Use&STYLE="+' height="70px" align="top";>&nbsp;&nbsp;&nbsp; Land Use</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=Catchment%20Areas&STYLE="+' height="40px" align="top";>&nbsp;&nbsp;&nbsp; Catchment Areas</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=Ground%20Water&STYLE="+' height="40px" align="top";>&nbsp;&nbsp;&nbsp; Ground Water</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=Fish%20Sanctuaries&STYLE="+' height="60px" align="top";>&nbsp;&nbsp;&nbsp; Fish Sanctuaries</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=Mineral%20Rights&STYLE="+' height="60px" align="top";>&nbsp;&nbsp;&nbsp; Mineral Rights</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=Dams&STYLE="+' height="40px" align="top";>&nbsp;&nbsp;&nbsp; Dams</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=Rivers&STYLE="+' height="40px" align="top";>&nbsp;&nbsp;&nbsp; Rivers</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=wetland_clusters&STYLE="+' height="40px" align="top";>&nbsp;&nbsp;&nbsp; Wetlands</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=RSA&STYLE="+' height="40px" align="top";>&nbsp;&nbsp;&nbsp; RSA Boundary</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=Buffer&STYLE="+' height="40px" align="bottom">&nbsp;&nbsp;&nbsp;  Buffer</span></br>' +
        '<span><img src='+"https://maps.kartoza.com/web/?map=/web/CathkinConservancy/CathkinConservancy.qgz&&SERVICE=WMS&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetLegendGraphic&FORMAT=image/jpeg&LAYERTITLE=false&LAYER=Protected%20Areas&STYLE="+' height="100px" align="top">&nbsp;&nbsp;&nbsp;Protected Areas</span></br>' ; */
    return div;
};
var legendManchasInundacion = L.control({position: 'bottomleft'});

legendManchasInundacion.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend');    
    var numPersonas = ['0','1 - 101','101 - 1001','1001 - 5000','> 5000'];

    div.innerHTML += '<p style="font-weight: bold; margin: 0px 0px 8px;">Número de habitantes estimados en la zona inundable</p>';
    for (var i = 0; i < numPersonas.length; i++) {
        div.innerHTML +=
            '<span style="background:'+getColor(numPersonas[i])+'; width:80px; color:white; font-weight: normal;">'+numPersonas[i]+'</span> ';
    }
    return div;
};

function getColor(d) {
    return d == '> 5000' ? '#800026' :
           d == '1001 - 5000'  ? '#BD0026' :
           d == '101 - 1001' ? '#E31A1C' :
           d == '1 - 101'  ? '#FC4E2A' :
           d == '0'  ? '#FD8D3C' :
                      '#FFEDA0';
}


//DEFINO EL BUSCADOR DE ESTACIONES MONITORIZADAS
var searchEstaciones = L.control.search({
    initial: false,
    propertyName: 'nombre',
    marker: false,
    textPlaceholder: 'Buscar nombre de la estación...',
    zoom: 18
});


//DEFINO EL CONTROL DE BRUJULA
/* var comp = new L.Control.Compass({autoActive: true, position:'topleft'});*/

//DEFINO EL CONTROL DE BUSQUEDA DE DIRECCIONES
var searchDireccion = L.Control.geocoder({
    geocoder: L.Control.Geocoder.nominatim(),
    position: 'topleft',
    placeholder: 'Buscar...'
});


//DEFINO LA LAYENDA DE LOS MARCADORES
const legendaMarkers = L.control.Legend({
    position: "topleft",
    collapsed: true,
    symbolWidth: 60,
    opacity: 0.6,
    column: 2,
    legends: [{
        label: "Spida Sin Avisos",
        type: "image",
        url: "../../static/img/spida/markers/spida_verde.png",
    }, {
        label: "Spida Nivel 1",
        type: "image",
        url: "../../static/img/spida/markers/spida_amarillo.png"
    }, {
        label: "Spida Nivel 2",
        type: "image",
        url: "../../static/img/spida/markers/spida_naranja.png"
    }, {
        label: "Spida Nivel 3",
        type: "image",
        url: "../../static/img/spida/markers/spida_rojo.png"
    }, {
        label: "Spida Sin datos",
        type: "image",
        url: "../../static/img/spida/markers/spida_negro.png"
    },{
        label: "Saih Sin Avisos",
        type: "image",
        url: "../../static/img/spida/markers/saih_verde.png",
    }, {
        label: "Saih Nivel 1",
        type: "image",
        url: "../../static/img/spida/markers/saih_amarillo.png"
    }, {
        label: "Saih Nivel 2",
        type: "image",
        url: "../../static/img/spida/markers/saih_naranja.png"
    }, {
        label: "Saih Nivel 3",
        type: "image",
        url: "../../static/img/spida/markers/saih_rojo.png"
    }, {
        label: "Saih Sin datos",
        type: "image",
        url: "../../static/img/spida/markers/saih_negro.png"
    }]
});

//DEFINO EL BOTON DE CAMBIO RAPIDO DE LAYER SAT A STREET PARA MAPA PUBLICO
var iconLayersControl = new L.Control.IconLayers(
    [
        {
            title: 'Calle', // use any string
            layer: layer_OpenStreetMap, // any ILayer
            icon: '../../static/img/spida/icons/openstreetmap.png' // 80x80 icon
        },
        {
            title: 'Satellite',
            layer: layer_ArcgisSat,
            icon: '../../static/img/spida/icons/arcgis_sat.png'
        }
    ], {
        position: 'topright'
    }
);


/* ZONAS METEOROLOGICAS AEMET (AVISOS MET AEMET) */
console.log(aemet);
var zonas_met_aemet=L.geoJson(aemet,{
    style: styleZonaAemet,
    onEachFeature: function(feature, layer) {
        var div = L.DomUtil.create('div', 'highchart');
        layer.bindPopup('<img src="../../static/img/spida/logos/logo_aemet.jpg" style="max-width:100%;max-height:100%;object-fit: contain;">'
        +'<br/><br/>Zona: '+feature.properties.NOM_Z +'<br/>Provincia: '+feature.properties.NOM_PROV+ '<br/>'+ getAvisosAemet(feature.properties.fid)
        +'<br/><br/>Para más información haga click '+ '<a href="http://www.aemet.es/es/eltiempo/prediccion/avisos?w=hoy&a=pb" target="_blank">aquí</a>'
        //+'<br/>'+'<div id="container" style="height: 400px; min-width: 300px"></div>'
        );
}});//.addTo(map);

/*------------------------------------------------------------------------------
#LAYER ULTIMA IMAGEN RADAR AEMET
-------------------------------------------------------------------------------*/
var layer_radar = L.imageOverlay(null, [[47.590164999999985, -15.161928699999999], [31.236391685669023, 2.5890034440992875]], {opacity: 1});

/*------------------------------------------------------------------------------
#TIME DIMENSION: IMAGENES PRECIPITACION ACUMULADA 1 HORA DE AEMET
-------------------------------------------------------------------------------*/
/* TIME DIMENSION PRECIPITACION ACUMULADA 1 HORA AEMET */
L.TimeDimension.Layer.ImageOverlay = L.TimeDimension.Layer.extend({

    initialize: function(layer, options) {
        L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
        this._layers = {};
        this._defaultTime = 0;
        this._timeCacheBackward = this.options.cacheBackward || this.options.cache || 0;
        this._timeCacheForward = this.options.cacheForward || this.options.cache || 0;
        this._getUrlFunction = this.options.getUrlFunction;

        this._baseLayer.on('load', (function() {
            this._baseLayer.setLoaded(true);
            this.fire('timeload', {
                time: this._defaultTime
            });
        }).bind(this));
    },

    eachLayer: function(method, context) {
        for (var prop in this._layers) {
            if (this._layers.hasOwnProperty(prop)) {
                method.call(context, this._layers[prop]);
            }
        }
        return L.TimeDimension.Layer.prototype.eachLayer.call(this, method, context);
    },

    _onNewTimeLoading: function(ev) {
        var layer = this._getLayerForTime(ev.time);
        if (!this._map.hasLayer(layer)) {
            this._map.addLayer(layer);
        }
    },

    isReady: function(time) {
        var layer = this._getLayerForTime(time);
        return layer.isLoaded();
    },

    _update: function() {
        if (!this._map)
            return;
        var time = map.timeDimension.getCurrentTime();
        var layer = this._getLayerForTime(time);
        if (this._currentLayer == null) {
            this._currentLayer = layer;
        }
        if (!this._map.hasLayer(layer)) {
            this._map.addLayer(layer);
        } else {
            this._showLayer(layer, time);
        }
    },

    _showLayer: function(layer, time) {
        if (this._currentLayer && this._currentLayer !== layer) {
            this._currentLayer.hide();
            this._map.removeLayer(this._currentLayer);
        }
        layer.show();
        if (this._currentLayer && this._currentLayer === layer) {
            return;
        }
        this._currentLayer = layer;
        // Cache management
        var times = this._getLoadedTimes();
        var strTime = String(time);
        var index = times.indexOf(strTime);
        var remove = [];
        // remove times before current time
        if (this._timeCacheBackward > -1) {
            var objectsToRemove = index - this._timeCacheBackward;
            if (objectsToRemove > 0) {
                remove = times.splice(0, objectsToRemove);
                this._removeLayers(remove);
            }
        }
        if (this._timeCacheForward > -1) {
            index = times.indexOf(strTime);
            var objectsToRemove = times.length - index - this._timeCacheForward - 1;
            if (objectsToRemove > 0) {
                remove = times.splice(index + this._timeCacheForward + 1, objectsToRemove);
                this._removeLayers(remove);
            }
        }
    },

    _getLayerForTime: function(time) {
        if (time == 0 || time == this._defaultTime) {
            return this._baseLayer;
        }
        if (this._layers.hasOwnProperty(time)) {
            return this._layers[time];
        }
        var url = this._getUrlFunction(this._baseLayer.getURL(), time);
        imageBounds = this._baseLayer._bounds;

        var newLayer = L.imageOverlay(url, imageBounds, this._baseLayer.options);
        this._layers[time] = newLayer;
        newLayer.on('load', (function(layer, time) {
            layer.setLoaded(true);
            if (map.timeDimension && time == map.timeDimension.getCurrentTime() && !map.timeDimension.isLoading()) {
                this._showLayer(layer, time);
            }
            this.fire('timeload', {
                time: time
            });
        }).bind(this, newLayer, time));

        // Hack to hide the layer when added to the map.
        // It will be shown when timeload event is fired from the map (after all layers are loaded)
        newLayer.onAdd = (function(map) {
            Object.getPrototypeOf(this).onAdd.call(this, map);
            this.hide();
        }).bind(newLayer);
        return newLayer;
    },

    _getLoadedTimes: function() {
        var result = [];
        for (var prop in this._layers) {
            if (this._layers.hasOwnProperty(prop)) {
                result.push(prop);
            }
        }
        return result.sort();
    },

    _removeLayers: function(times) {
        for (var i = 0, l = times.length; i < l; i++) {
            this._map.removeLayer(this._layers[times[i]]);
            delete this._layers[times[i]];
        }
    },

});

L.timeDimension.layer.imageOverlay = function(layer, options) {
    return new L.TimeDimension.Layer.ImageOverlay(layer, options);
};

L.ImageOverlay.include({
    _visible: true,
    _loaded: false,

    _originalUpdate: L.imageOverlay.prototype._update,

    _update: function() {
        if (!this._visible && this._loaded) {
            return;
        }
        this._originalUpdate();
    },

    setLoaded: function(loaded) {
        this._loaded = loaded;
    },

    isLoaded: function() {
        return this._loaded;
    },

    hide: function() {
        this._visible = false;
        if (this._image && this._image.style)
            this._image.style.display = 'none';
    },

    show: function() {
        this._visible = true;
        if (this._image && this._image.style)
            this._image.style.display = 'block';
    },

    getURL: function() {
        return this._url;
    },

});

// Add image layer
var imageUrl='http://www.aemet.es/es/api-eltiempo/modelo-harmonie/imagen-modelo/61/PB/fc2021070306+001h00m_61_0-1_1HH_61_3857.tif_color.png',
    imageBounds = [
        [34.483878966725584, 4.992602158427742],
		[44.487500000000004, -11.0125]
    ];

var imageLayer = L.imageOverlay(imageUrl, imageBounds, {
    opacity: 0.5
});


var cod_url="06";
var getSirenaImageUrl = function(baseUrl, time) {
	fecha1=new Date(map.timeDimension.getAvailableTimes()[0]);
	fecha2=new Date(time);
	result=fecha2-fecha1;
	result=Math.floor(result / (1000 * 60 * 60));
    var beginUrl = baseUrl.substring(0, baseUrl.lastIndexOf("/") + 3);
    var strTime = fecha1.getFullYear()+("0" + (fecha1.getMonth()+1)).slice(-2)+("0" + fecha1.getDate()).slice(-2);
    var url=beginUrl+strTime+cod_url+'+'+('000' + (result+1)).substr(-3)+'h00m_61_'+result+'-'+(result+1)+'_1HH_61_3857.tif_color.png';
    return url;
};

var testImageTimeLayer = L.timeDimension.layer.imageOverlay(imageLayer, {
    getUrlFunction: getSirenaImageUrl
});
testImageTimeLayer.addTo(map);











