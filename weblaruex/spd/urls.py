from django.urls import path
from spd.views import *
from django.contrib.auth.views import LoginView

app_name = 'spd'


urlpatterns = [
    path('laruex/informes/semestrales/', InformesSemestrales,name='InformesSemestrales'),

    path('spida/', Spida,name='Spida'),
    path('redspida/prueba', Prueba,name='Prueba'),
    path('private/redspida/home/', HomeSpida,name='HomeSpida'),
    path('private/redspida/mapa/', MapaSpida,name='MapaSpida'),
    path('private/redspida/sucesos/', SucesosSpida,name='SucesosSpida'),
    path('private/redspida/documentacion/', DocumentacionSpida,name='DocumentacionSpida'),
    path('private/redspida/informes/', InformesTrimestralesSpida,name='InformesTrimestralesSpida'),
    path('private/redspida/eventos/', EventosInundacion,name='EventosInundacion'),
    path('private/redspida/contactos/', Contactos,name='Contactos'),
    path('private/redspida/login/', LoginView.as_view(template_name='login_spd.html'), name="LoginSpida"),
    path('private/redspida/perfil/', PerfilSpida, name="PerfilSpida"),
    path('private/redspida/alerta2/', Alerta2,name='Alerta2'),
    path('private/redspida/graficos/rio/', GraficosNivelRio,name='GraficosNivelRio'),

    path('private/datos/estaciones/', getEstaciones, name="getEstaciones"),
    path('private/datos/estaciones/pluvio/', getEstacionesPluvio, name="getEstacionesPluvio"),
    path('private/datos/infoestacion/', getInfoEstacion, name="getInfoEstacion"),
    path('private/datos/embalses/', getEmbalses, name="getEmbalses"),
    path('private/datos/informes/', getInformesTrimestrales, name="getInformesTrimestrales"),
    path('private/datos/contactos/', getContactos, name="getContactos"),
    path('private/datos/documentos/', getDocumentosAdjunto, name='getDocumentosAdjunto'),
    path('private/datos/adjuntos/', getAdjuntos, name='getAdjuntos'),
    path('private/datos/valores24h/', getValores24h, name='getValores24h'),
    path('private/datos/valoresprediccion24h/', getValoresPrediccion24h, name='getValoresPrediccion24h'),
    path('private/datos/valoresembalse/', getDatosEmbalse, name='getDatosEmbalse'),
    path('private/datos/imagen/captura/',  getCapturaImagen ,name='getCapturaImagen'),
    path('private/datos/imagen/streaming/',  getStreamingImagen ,name='getStreamingImagen'),
    path('private/datos/imagen/',  getUltimaImagen ,name='getUltimaImagen'),
    path('private/datos/imagen/camara',  getImagenSpida ,name='getImagenSpida'),
    path('private/datos/camaras/',  getImagenesCamaras ,name='getImagenesCamaras'),
    path('private/datos/miniaturas/', getMiniaturasSpida, name='getMiniaturasSpida'), #DATOS: listado de imagenes spida
    path('private/datos/cieloaemet/',  getEstadoCieloAemet ,name='getEstadoCieloAemet'),
    path('private/datos/temperatura/',  getTemperaturaAemet ,name='getTemperaturaAemet'),
    path('private/datos/modeloharmonie/',  getImagenesPreAcumAemet ,name='getImagenesPreAcumAemet'),
    path('private/datos/radar/',  getImagenesRadar ,name='getImagenesRadar'), #DATOS: imagenes Radar Precipitacion Acumulada 1 hora Aemet
    path('private/datos/radar/legend/',  getLegendaRadar ,name='getLegendaRadar'),
    path('private/datos/avisos/meteorologicos/',  getAvisosMeteorologicos ,name='getAvisosMeteorologicos'),
    path('private/datos/avisos/meteorologicos/informacion/',  getAvisosMeteorologicosInformacion ,name='getAvisosMeteorologicosInformacion'),
    path('private/legenda/modelosnumericos/',  getLegendaModelosNumericos ,name='getLegendaModelosNumericos'), #DATOS: colores de la leyeda de la Precipitacion Acum 1 h (Modelos Numericos Aemet)
    path('private/datos/upd/perfil/usuario/', updatePerfilUsuario, name="updatePerfilUsuario"),
    path('private/datos/rutina/', getValoresRutinaEstacion, name="getValoresRutinaEstacion"),

    path('private/donwload/documento/', DownloadDocumento, name="DownloadDocumento"),
    path('private/donwload/informe/', DownloadInformeTrimestral, name="DownloadInformeTrimestral"),
    path('private/view/documento/', ViewDocumento, name='ViewDocumento'), 
    path('private/view/informe/', ViewInformeTrimestral, name='ViewInformeTrimestral'), 
    path('private/view/protocolo/', ViewProtocolo, name="ViewProtocolo"),
    path('private/comprobacion/informe/', ExitsInformeTrimestral, name="ExitsInformeTrimestral"),
]

handler404 = "spd.views.page_not_found_view"
handler500 = "spd.views.custom_error_view"

