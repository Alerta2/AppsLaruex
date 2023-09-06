/*-----------------------------------------------------------------------
# DEFINO LAS CAPAS DE MARCADORES 
(Estaciones Spida, Estaciones Saih Tajo, Estaciones Saih Guadiana, Embalses, Alarmas animadas y Subcuenca)
------------------------------------------------------------------------*/

var layer_extremadura = L.geoJson(extremadura, {
    opacity: 1,
    fillOpacity: 0.5,
    //fillOpacity: fillOpacityExtremadura,
    fillColor: '#1B1C1C',
    color: 'rgba(27,27,28,0.2)',//'#009CDD',
    invert: true
}).addTo(map);


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








