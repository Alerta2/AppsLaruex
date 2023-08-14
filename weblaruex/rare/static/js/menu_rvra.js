

/*Creacion de la grafica de la pantalla home*/
new Morris.Line({
  element: 'chart',
  data: [
    { year: '2008', value: 20 },
    { year: '2009', value: 10 },
    { year: '2010', value: 5 },
    { year: '2011', value: 5 },
    { year: '2012', value: 20 }
  ],
  xkey: 'year',
  ykeys: ['value'],
  labels: ['Value']
});

/*Creacion de los mapas de la pantalla home*/
var var_location= new google.maps.LatLng(39.7931611,-5.6302012);
var var_map_row;
function init_map() {
        var var_mapoptions = {
          center: var_location,
          zoom: 5
        };
	var var_marker = new google.maps.Marker({
		position: var_location,
		map: var_map,
		title:"Alerta2"});
 
        var var_map = new google.maps.Map(document.getElementById("map-container"),
            var_mapoptions);



 	var_map_row = new google.maps.Map(document.getElementById("map-row"),
            var_mapoptions);
	var_map_row.setZoom(6);
	var_marker.setMap(var_map);	

      }
 

google.maps.event.addDomListener(window, 'load', init_map);


/**
*Control salvapantallas home
**/
document.onmousemove = function(){
      	borrar();
   };
function salvapantallas(){
	
	document.getElementById("salvapantallas").style.display='block'; 
	document.getElementById("container").style.display='none';
	var_map_row.setCenter(var_location);
}
function controlar(){
 	tempor=setTimeout("salvapantallas()",5000);
}

var dispositivo = navigator.userAgent.toLowerCase();
if( dispositivo.search(/iphone|ipod|ipad|android/) == -1 ){
	window.onload=controlar(); 
}else{
	document.getElementById("salvapantallas").style.display='none';
}

function borrar(){
	 clearTimeout(tempor);
	 document.getElementById("salvapantallas").style.display='none';
	 document.getElementById("container").style.display='block';
	 controlar();
} 

//document.getElementById("salvapantallas").style.display='none';




