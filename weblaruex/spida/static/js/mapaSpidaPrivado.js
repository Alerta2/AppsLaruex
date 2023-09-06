//AGREGO EL PROGRESS BAR 
map.addControl(progressBar);

//AGREGO EL TIME DIMENSION (PLAY DE LAS IMAGENES DE PRECIPITACION ACUM 1 HORA AEMET)
map.addControl(timeDimensionControl);

//AGREGO LA LEYENDA DE VALORES DE PRECIPITACION ACUM 1 HORA AEMET
/*map.addControl(legendPreAcum1h);*/
map.addControl(legendPreMetedoNumericoAemet);


//BARRA DE PROGRESO (TIEMPO RESTANTE PARA ACTUALIZAR)
var jsonImagenes=[];
var tiempo_actualizar=300; //segundos (5 minutos)
var progreso = tiempo_actualizar;
var idIterval = setInterval(function(){
    progreso +=1;
    if(progreso >= tiempo_actualizar){
        progreso=0;
        $('#bar').css('width', progreso + '%');
        CargarEstaciones();//cargo los markers de las estaciones
        CargarImagenes();//cargo los markers de las imagenes
        ImagenesPrecipitacionAcumulada1hAemet(); //Cargo las imagenes de Precipitacion Acumulada 1 hora Aemet 
        MarkerCieloAemet();//Cargo el estado del cielo de Aemet
        ImagenRadarAemet();//Cargo la ultima imagen radar
        HorariosSol();//Obtengo los horarios solares para cambiar la capa base
    }
    else{      
        var valorAncho = (progreso/tiempo_actualizar) * 100;
        $('#bar').css('width', valorAncho + '%');
    }
},1000);

//AGREGO LA CAPA BASE DEL MAPA
HorariosSol();

//AGREGO EL CONTORNO DE LAS PROVINCIAS DE EXTREMADURA
map.addControl(provincias);

//AGREGO EL PANEL LATERAL SIDEBAR
map.addControl(sidebar);

//AGREGO EL BOTON HOME (CENTRA EL MAPA EN EXTREMADURA)
map.addControl(botonHome);
//Modifico el Tamaño
var ArrayTest2 = document.getElementsByClassName('easy-button-button leaflet-bar-part leaflet-interactive zoom-to-active');
ArrayTest2 = Array.prototype.slice.call(ArrayTest2);
ArrayTest2.forEach( function(element){
    element.style.width = '30px'; 
    element.style.height = '30px'; 
});

//AGREGO EL BOTON PARA BUSCAR LOS MARCADORES DE LAS ESTACIONES QUE MONITORIZAMOS
map.addControl(searchEstaciones);
var layergroupEstaciones=L.layerGroup([layer_estaciones_spida,layer_estaciones_saih_guadiana,layer_estaciones_saih_tajo]);
searchEstaciones.setLayer(layergroupEstaciones);

//AGREGO EL BOTON DE MI UBICACION
map.addControl(botonUbicacionActual);

//AGREGO EL BOTON DE PANTALLA COMPLETA (MUESTRA EL MAPA EN FULLSCREEN)
map.addControl(botonFullScreen);

//AGREDO EL BOTON DE IMPRIMIR MAPA
map.addControl(botonPrinter);

//AGREGO EL PANEL INFO AVISOS
map.addControl(myInfoControl);

//AGREGO EL MINI MAPA
/*map.addControl(miniMap);*/

//AGREGO LAS CAPAS DE MARCADORES QUE DEBEN APARECER AL CARGAR LA PAGINA
map.addControl(layer_estaciones_spida); //estaciones spida
map.addControl(layer_alarmas_animadas); //alarmas animadas




//AGREGO LAS CAPAS QUE ME INTERESAN AL PANEL LAYER
myLayersControl.addBaseLayer({
    name:  "Open Street Map",
    layer: layer_OpenStreetMap
},'','<i id="icon-title" class="fas fa-layer-group"></i><span style="font-weight: bold;">Capas base del Mapa</span>',true);

myLayersControl.addBaseLayer({
    name:  "ArcGIS Satelite",
    layer: layer_ArcgisSat
},'','<i id="icon-title" class="fas fa-layer-group"></i><span style="font-weight: bold;">Capas base del Mapa</span>');

myLayersControl.addBaseLayer({
    name: "CartoDB DarkMatter",
    layer: layer_CartoDBDarkMatter
},'','<i id="icon-title" class="fas fa-layer-group"></i><span style="font-weight: bold;">Capas base del Mapa</span>');

myLayersControl.addBaseLayer({
    name: "Open Street Map Municipios",
    layer: layer_OpenStreetMapMunicipios
},'','<i id="icon-title" class="fas fa-layer-group"></i><span style="font-weight: bold;">Capas base del Mapa</span>');

myLayersControl.addBaseLayer({
    name: "Open Top Map",
    layer: layer_OpenTopMap
},'','<i id="icon-title" class="fas fa-layer-group"></i><span style="font-weight: bold;">Capas base del Mapa</span>');

myLayersControl.addBaseLayer({
    name: "Stamen Terrain",
    layer: layer_StamenTerrain
},'','<i id="icon-title" class="fas fa-layer-group"></i><span style="font-weight: bold;">Capas base del Mapa</span>');



myLayersControl.addOverlay({
    name: "Estaciones Spida",
    icon: '<i class="fas fa-tint" style="color:blue; width:12px; height:12px;"></i>',
    layer: layer_estaciones_spida
},'','<i id="icon-title" class="fas fa-broadcast-tower"></i><span style="font-weight: bold;">Estaciones de Nivel de Río</span>', true);

myLayersControl.addOverlay({
    active: true,
    name: "Estaciones Saih Tajo",
    icon: '<img src="../../static/img/spida/icons/Icono_Provincia_Badajoz_trans.png" alt="Saih Tajo" style="width:15px; height:12px;">',
    layer: layer_estaciones_saih_tajo
},'','<i id="icon-title" class="fas fa-broadcast-tower"></i><span style="font-weight: bold;">Estaciones de Nivel de Río</span>');

myLayersControl.addOverlay({
    active: true,
    name: "Estaciones Saih Guadiana",
    icon: '<img src="../../static/img/spida/icons/Icono_Provincia_Caceres-trans.png" alt="Saih Guadiana" style="width:15px; height:12px;">',
    layer: layer_estaciones_saih_guadiana
},'','<i id="icon-title" class="fas fa-broadcast-tower"></i><span style="font-weight: bold;">Estaciones de Nivel de Río</span>');


myLayersControl.addOverlay({
    name: "Imagenes Spida",
    icon: '<i class="far fa-image" style="color: #650DC5; width:12px; height:12px;"></i>',
    layer: photoLayer
});

myLayersControl.addOverlay({
    name: "Red Hidrográfica",
    icon: '<i class="fas fa-water" style="color: #0D6DC5; width:12px; height:12px;"></i>',  
    layer: rios
});

myLayersControl.addOverlay({
    active: true,
    name: "Estado del Cielo",
    icon: '<i class="fas fa-cloud-moon" style="color: #00FF7F; width:12px; height:12px;"></i>',
    layer: layer_estado_cielo_aemet
},'','<i id="icon-title" class="fas fa-cloud-moon-rain"></i><span style="font-weight: bold;">Aemet</span>', true);

myLayersControl.addOverlay({
    name: "Precipitacion en 1 h",
    icon: '<i class="fas fa-cloud-rain" style="color: #0D6DC5; width:12px; height:12px;"></i>',
    layer: testImageTimeLayer
},'','<i id="icon-title" class="fas fa-cloud-moon-rain"></i><span style="font-weight: bold;">Aemet</span>');

myLayersControl.addOverlay({
    name: "Avisos Meteorologicos",
    icon: '<i class="fas fa-exclamation" style="color: #CD5C5C; width:12px; height:12px;"></i>',
    layer: zonas_met_aemet
},'','<i id="icon-title" class="fas fa-cloud-moon-rain"></i><span style="font-weight: bold;">Aemet</span>');

myLayersControl.addOverlay({
    name: "Radar",
    icon: '<i class="fas fa-braille" style="color: #2F4F4F; width:12px; height:12px;"></i>',
    layer: layer_radar
},'','<i id="icon-title" class="fas fa-cloud-moon-rain"></i><span style="font-weight: bold;">Aemet</span>');


myLayersControl.addOverlay({
    name: "T10",
    layer: T10
},'','<i id="icon-title" class="fas fa-house-damage"></i><span style="font-weight: bold;">Mapas de Peligrosidad</span>', true);

myLayersControl.addOverlay({
    name: "T100",
    layer: T100
},'','<i id="icon-title" class="fas fa-house-damage"></i><span style="font-weight: bold;">Mapas de Peligrosidad</span>');

myLayersControl.addOverlay({
    active: false,
    name: "T500",
    layer: T500
},'','<i id="icon-title" class="fas fa-house-damage"></i><span style="font-weight: bold;">Mapas de Peligrosidad</span>');


//AGREGO EL CONTROL DE CAPAS O PANEL LAYER
map.addControl(myLayersControl);



























    
/*     addWMSLegend(map, uri, position = "topright", layerId = NULL)
    L.wmsLegend("https://wms.mapama.gob.es/sig/Agua/Riesgo/RiesgoPob_10/Leyenda/RiesgoPob_10.png",{
        position: 'bottomleft', 
        format: 'image/png'
    }); */





   /*  var addLegend42 = (function() {
	var showLegend42 = new L.Control({position:'topright'});
	showLegend42.onAdd = function(map) {
			var show_legend42 = L.DomUtil.create('a','showlegend');
			show_legend42.innerHTML = '<i class="fa fa-road legend-icon" aria-hidden="true" ' +
                'title="Show Legend"></i>';
			L.DomEvent
				.disableClickPropagation(show_legend42)
				.addListener(show_legend42, 'click', function() {
					displayLegend42();
				},show_legend42);
			return show_legend42;
		};
        return showLegend42;
    }()).addTo(map);

    var removeLegend42 = (function() {
        var hideLegend42 = new L.Control({position:'topright'});
        hideLegend42.onAdd = function(map) {
                var hide_legend42 = L.DomUtil.create('a','hidelegend42');
                hide_legend42.innerHTML = '<i class="fa  fa-road legend-icon" aria-hidden="true" ' +
                    'title="Hide Legend"></i>';
                L.DomEvent
                    .disableClickPropagation(hide_legend42)
                    .addListener(hide_legend42, 'click', function() {
                        hidLegend42();
                    },hide_legend42);
                return hide_legend42;
            };
            return hideLegend42;
    }());

    function displayLegend42() {
        map.addControl(legend);
        map.removeControl(addLegend42);
        map.addControl(removeLegend42);
    }

    function hidLegend42() {
        map.removeControl(legend);
        map.removeControl(removeLegend42);
        map.addControl(addLegend42);
    }
 */
    

