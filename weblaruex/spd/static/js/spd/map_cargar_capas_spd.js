   
   
 /*------------------------------------------------------------------------------
    Funcion que carga las estaciones SAIH y SPIDA
 ------------------------------------------------------------------------------*/
 async function CargarEstaciones() {
    map.spin(true,spinner_options);

    $.getJSON(url_cargar_estaciones,
      function (data) {

        estaciones = data;
        /* Layer de Alarmas animadas */
        layer_alarmas_animadas.clearLayers();
        layer_alarmas_animadas.addData(data);

        //Layer Estaciones Saih Tajo
        layer_estaciones_saih_tajo.clearLayers();
        layer_estaciones_saih_tajo.addData(data);

        //Layer Estaciones Saih Guadiana
        layer_estaciones_saih_guadiana.clearLayers();
        layer_estaciones_saih_guadiana.addData(data);

        //Layer Estaciones Spida
        layer_estaciones_spida.clearLayers();
        layer_estaciones_spida.addData(data);

        //Actualizo en el mapa el indicador de si hay avisos o no
        InfoAvisosMap(data)
      })
      .fail(function () {
        console.log('getJSON Estaciones de Control request failed! ');
      })
    .always(function () {
      map.spin(false);
    });
  };


  /*------------------------------------------------------------------------------
      Funcion que carga los embalses
      ------------------------------------------------------------------------------*/
  async function CargarEmbalses() {
    map.spin(true,spinner_options);

    $.getJSON(url_cargar_embalses,
      function (data) {
        embalses = data;
        layer_embalses.clearLayers();
        layer_embalses.addData(data);
      })
      .fail(function () {
        console.log('getJSON Embalses request failed! ');
      })
    .always(function () {
      map.spin(false);
    });
  };


  
    /*------------------------------------------------------------------------------
    Funcion que carga los datos GeoJson del estado del cielo de las estaciones Aemet
    ------------------------------------------------------------------------------*/
    async function CargarCieloAemet() {
      map.spin(true,spinner_options);  
      $.getJSON(url_cargar_cieloAemet + "?h=" + new Date().getHours(),
        function (data) {

          layer_estado_cielo_aemet.clearLayers();
          layer_estado_cielo_aemet.addData(data);

        })
        .fail(function () {
          console.log('getJSON Estaciones Meteorológicas Aemet (Estado del cielo) request failed! ');
        })
      .always(function () {
        map.spin(false);
      });
    };

    /*------------------------------------------------------------------------------
    Funcion que carga los datos GeoJson de la temperatura de las estaciones Aemet
    ------------------------------------------------------------------------------*/
    async function CargarTemperaturaAemet() {
      map.spin(true,spinner_options);
      $.getJSON(url_cargar_temperaturaAemet + "?h=" + new Date().getHours(),
        function (data) {

          layer_temperatura_aemet.clearLayers();
          layer_temperatura_aemet.addData(data);

        })
        .fail(function () {
          console.log('getJSON Estaciones Meteorológicas Aemet (Temperatura) request failed! ');
        })
        .always(function () {
          map.spin(false);
        });
    }


        /* ------------------------------------------------------------------------------
        Funcion que carga la ultima imagen radar de Aemet 
        ------------------------------------------------------------------------------*/
        async function CargarRadarAemet() {
          map.spin(true,spinner_options);
          $.getJSON(url_cargar_radarAemet,
            function (data) {
    
              arr = data[0].Elementos;
              arr = arr.filter(innerArray => innerArray['Nombre radar'] == 'BAD');
              arr = arr.sort(function (a, b) { //ordeno el array con la primera columna (fecha/hora)
                return new Date(a["Fecha"][0]) - new Date(b["Fecha"][0]);
              });
    
              ultima_imagen = arr[arr.length - 1]['Nombre fichero'];
              url = 'http://www.aemet.es/es/api-eltiempo/radar/imagen-radar/RN1/' + ultima_imagen;
              layer_radar.setUrl(url);
    
            })
            .fail(function () {
              console.log('getJSON Radar Aemet request failed! ');
            })
          .always(function () {
            map.spin(false);
          });
        };



    /* ------------------------------------------------------------------------------
    Funcion que carga los avisos meteorologicos por zona de Aemet 
    ------------------------------------------------------------------------------*/

    /*function CargarZonasMetAemet() {
      $.getJSON("{% url 'spd:getAvisosMeteorologicos'%}",
        function (data) {
          console.log("AEMET", data)
          estadoZonasMetAemet = data;
          layer_zonas_met_aemet.setStyle(styleZonaAemet);
        })
        .fail(function () {
          console.log('getJSON Avisos Meteorologicos Aemet request failed! ');
        })
    };*/