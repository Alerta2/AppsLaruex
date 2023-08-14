/* AÑADO EL SIDE BY SIDE PARA PODER TENER DOS VISTAS DE MAPAS A LA VEZ */
/*map.addControl(layer_OpenStreetMap);*/
/* sidebyside.setLeftLayers(layer_ArcgisSat);
sidebyside.setRightLayers(layer_OpenStreetMap); //bueno
map.addControl(sidebyside);*/


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
        CargarEstaciones();//cargo los markers de las estaciones   
        CargarImagenes();//cargo los markers de las imagenes    
        ImagenesPrecipitacionAcumulada1hAemet(); //Cargo las imagenes de Precipitacion Acumulada 1 hora Aemet 
        MarkerCieloAemet();//Cargo el estado del cielo de Aemet
        ImagenRadarAemet();//Cargo la ultima imagen radar
    }
},1000);

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

//console.log("Max width: ",document.getElementsByClassName('fas fa-exclamation-circle'));



//AGREGO EL BOTON PARA BUSCAR LOS MARCADORES DE LAS ESTACIONES QUE MONITORIZAMOS
map.addControl(searchEstaciones);
searchEstaciones.setLayer(layer_estaciones_spida);

//AGREGO EL BOTON INFO (MUESTRA EL MODAL CON LA INFORMACION DE DATOS SUJETOS A VALIDACION)
map.addControl(botonInfo);

//AGREGO EL BOTON DE PANTALLA COMPLETA (MUESTRA EL MAPA EN FULLSCREEN)
map.addControl(botonFullScreen);

//AGREGO EL MINI MAPA
/*map.addControl(miniMap);*/

//AGREGO LA LEYENDA DE LOS MARCADORES
map.addControl(legendaMarkers);

//AGREGO LAS CAPAS DE MARCADORES QUE DEBEN APARECER AL CARGAR LA PAGINA
map.addControl(layer_estado_cielo_aemet);
map.addControl(layer_estaciones_spida); //estaciones spida
map.addControl(layer_alarmas_animadas); //alarmas animada




//AGREGO LAS CAPAS QUE ME INTERESAN AL PANEL LAYER
myLayersControl.addOverlay({
    name: "Imagenes Spida",
    icon: '<i class="far fa-image" style="color: #650DC5; width:12px; height:12px;"></i>',
    layer: photoLayer
});

myLayersControl.addOverlay({
    name: "Estaciones Spida",
    icon: '<i class="fas fa-tint" style="color:blue; width:12px; height:12px;"></i>',
    layer: layer_estaciones_spida
});


myLayersControl.addOverlay({
    name: "Red Hidrográfica",
    icon: '<i class="fas fa-water" style="color: #0D6DC5; width:12px; height:12px;"></i>',  
    layer: rios
});


myLayersControl.addOverlay({
    name: "Estado del Cielo (Aemet)",
    icon: '<i class="fas fa-cloud-moon" style="color: #00FF7F; width:12px; height:12px;"></i>',  
    layer: layer_estado_cielo_aemet
});

myLayersControl.addOverlay({
    name: "Precipitacion en 1 h (Aemet)",
    icon: '<i class="fas fa-cloud-rain" style="color: #0D6DC5; width:12px; height:12px;"></i>',  
    layer: testImageTimeLayer 
});

myLayersControl.addOverlay({
    name: "Radar (Aemet)",
    icon: '<i class="fas fa-braille" style="color: #2F4F4F; width:12px; height:12px;"></i>',  
    layer: layer_radar 
});

myLayersControl.addOverlay({
    name: "Avisos Meteorologicos (Aemet)",
    icon: '<i class="fas fa-exclamation" style="color: #CD5C5C; width:12px; height:12px;"></i>',  
    layer: zonas_met_aemet
});
			
			
//SWIPE ENTRE CAPA SATELITE Y CAPA STREET
/* var range = document.getElementById('range');
var overlay = layer_ArcgisSat;
console.log('el rango es '+range.value);
function clip() {
    var nw = map.containerPointToLayerPoint([0, 0]),
        se = map.containerPointToLayerPoint(map.getSize()),
        clipX = nw.x + (se.x - nw.x) * range.value;

    overlay.getContainer().style.clip = 'rect(' + [nw.y, clipX, se.y, nw.x].join('px,') + 'px)';
};
range['oninput' in range ? 'oninput' : 'onchange'] = clip;
map.on('move', clip);
clip(); */

//AGREGO EL PANEL INFO AVISOS
map.addControl(myInfoControl);

//AGREGO EL CONTROL RAPIDO PARA CAMBIAR LAS CAPAS BASE
map.addControl( iconLayersControl);

//AGREGO EL CONTROL DE CAPAS O PANEL LAYER
map.addControl(myLayersControl);

//AÑADO EL CONTROL RAPIDO PARA CAMBIAR LAS CAPAS BASE
/*var range = document.getElementById('range');
map.addControl(iconLayersControl);*/
/*iconLayersControl.on('activelayerchange', function(e) {
    if(e.layer._url.includes("server.arcgisonline.com")){
       
    }
    else{
    }
});*/

//Para añadir una imagen al mapa
//1. Primera coordenada esquina inferior derecha
//2. Segunda coordenada esquina superior izquierda
//var oldmap = L.imageOverlay('http://www.aemet.es/es/api-eltiempo/radar/imagen-radar/compo/radw202107061130_3857.png', [[51.29999999999996, -16.079999999999995], [27.219999999999978, 12.139999999999997]], {opacity: 1}).addTo(map);







