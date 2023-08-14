
        // inicio el mapa de leaflet
        var map = L.map('mapid',{
            minZoom:5, //especifico zoom minimo del mapa
            attributionControl: false,
            zoomControl: false,
            timeDimension: true,
            timeDimensionOptions: {
                period: "PT1H",
            },
        }).setView([39.4034522,-6.7628017], 8);
        //DEFINO EL CONTROL DE CAPAS O PANEL LAYER
        var baselayers = [];
        var overLayers = []; //otras capas
        var myLayersControl = L.control.panelLayers(baselayers, overLayers, {
            compact: true,
            collapsed: true,
            collapsibleGroups: true 
        });

        //DEFINO LAS CAPAS BASE
        var layer_ArcgisSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
          minZoom: 0,
          maxZoom: 20
        }); //satelite
        var layer_OpenStreetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          minZoom: 0,
          maxZoom: 20
        }); //calle
        var layer_OpenStreetMapMunicipios = L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
          minZoom: 0,
          maxZoom: 20
        });
        var layer_OpenTopMap = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
          minZoom: 0,
          maxZoom: 20
        });
        var layer_StamenTerrain = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png', {
          minZoom: 0,
          maxZoom: 20
        });

        myLayersControl.addBaseLayer({
            name:  "ArcGIS Satelite",
            layer: layer_ArcgisSat
        },'','<i id="icon-title" class="fas fa-layer-group"></i><span style="font-weight: bold;">Capas base del Mapa</span>',true);

        myLayersControl.addBaseLayer({
            name:  "Open Street Map",
            layer: layer_OpenStreetMap
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

        map.addControl(myLayersControl);

        L.control.zoom({ position: 'bottomleft' }).addTo(map);

        var ubicacionesInteres = L.layerGroup();
        map.addLayer(ubicacionesInteres);
  