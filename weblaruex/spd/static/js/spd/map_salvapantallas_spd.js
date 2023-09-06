/*----------------------------------------------------
  # VARIABLES SALVAPANTALLAS
  ----------------------------------------------------*/
  var salvapantallas_activo = false;
  var timerInactividad, timerSalvapantallas, timeoutOpensidebar, timeoutFunciones;

  /*----------------------------------------------------
  # EVENTO TEMPORIZADOR DE INACTIVIDAD SOBRE LA PANTALLA (PARA ABRIR,ACTIVAR EL SALVAPANTALLAS)
  ----------------------------------------------------*/
  function Inactividad(){
      timerInactividad=setInterval("OpenSalvaPantallas()",60000);
  }
  
  /*----------------------------------------------------
  # EVENTO ABRIR (ACTIVAR) EL SALVAPANTALAS
  ----------------------------------------------------*/
  function OpenSalvaPantallas(){
     
      var w = $(window).width();
      if ((w > 480)&&(salvapantallas_activo == false)){
          salvapantallas_activo = true;
          timerSalvapantallas=setInterval("AnimacionSalvapantallas()",30000);
          AnimacionSalvapantallas();
      }
    }


  /*----------------------------------------------------
  # FUNCIONES QUE HACER EL SALVAPANTALLAS CUANDO ESTA ABIERTO
  ----------------------------------------------------*/  

  function AnimacionSalvapantallas(){
    sidebar.close();
    $('#map').trigger('click');
    /*$('#modalUltimaImagen').modal().hide();*/

        var aleatorio = Math.ceil(Math.random() * layer_estaciones_spida.getLayers().length);
        map.flyTo(layer_estaciones_spida.getLayers()[aleatorio-1].getLatLng(), 14, {
            "animate": true,
            "duration": 6
        });
        timeoutOpensidebar = setTimeout(function(){
              layer_estaciones_spida.getLayers()[aleatorio-1].fire('click');    
              }, 10000);
        var funcs =[OpenUltimaFoto, OpenGraficoNivelRio];
        var i= Math.floor(Math.random() * funcs.length)
        timeoutFunciones = setTimeout(function(){   
              funcs[i]();
        },15000);

        timeoutClose=setTimeout(function(){  
            switch(i){
              case 0:
                $('#modalUltimaImagen').modal().hide();
                break;
              case 1:
                $('#graficoNivelRio').dblclick();
                break;
            } 
        },20000);
  }

  function OpenUltimaFoto(){
    $('#UltimaFoto').click();
  }

  function OpenGraficoNivelRio(){
    $('#graficoNivelRio').dblclick();
  }

  /*----------------------------------------------------
  # EVENTO CERRAR (DESACTIVAR) EL SALVAPANTALAS
  ----------------------------------------------------*/

  function CloseSalvaPantallas(){
    sidebar.close();
    $('#map').trigger('click');
    $('#modalUltimaImagen').modal().hide();
    console.log("He terminado");
    map.flyTo([39.1666700,-6.1666700],8,{
            "animate": true
        })
  }


  /*----------------------------------------------------
  # EVENTO CUANDO MUEVO EL RATON POR LA PANTALLA
  ----------------------------------------------------*/
  document.onmousemove = function(){
    
    clearTimeout(timerInactividad);
    Inactividad();

    if (salvapantallas_activo){ //Si el salvapantallas está abierto...
        /*Limpio todos los timers que van a ir abriendo cosas*/
        clearTimeout(timeoutOpensidebar);
        clearTimeout(timeoutFunciones);
        clearTimeout(timerSalvapantallas);
        salvapantallas_activo = false;//desactivo el salvapanatallas
        CloseSalvaPantallas();//cierro el salvapantallas
    }       
  }


  /*Inicio el temporizador de Inactividad al carga la página*/
  window.onload=Inactividad();