/*Creacion de los mapas de la pantalla home*/
 function init_map() {
		var var_location = new google.maps.LatLng(39.7931611,-5.6302012);
 
        var var_mapoptions = {
          center: var_location,
          zoom: 6
        };
 
		var var_marker = new google.maps.Marker({
			position: var_location,
			map: var_map,
			title:"Alerta2"});
 
        var var_map = new google.maps.Map(document.getElementById("map-container"),
            var_mapoptions);
 
		var_marker.setMap(var_map);	
 
      }
 
      google.maps.event.addDomListener(window, 'load', init_map);
