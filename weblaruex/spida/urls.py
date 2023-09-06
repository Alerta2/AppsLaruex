from django.urls import path
from spida.views import *
from django.contrib.auth.views import LoginView



app_name = 'spida'


urlpatterns = [
    path('spida/presentacion/', presentacionSpida,name='PresentacionSpida'),
    path('spida/inicio/', inicioSpida,name='PortadaSpida'),
    path('spida/mapa/', getMapaSpida,name='MapaSpida'),
    path('spida/estaciones/', getEstaciones, name='EstacionesSpida'), #DATOS: listado de estaciones spida monitorizazdas y visualizadas
    path('spida/imagenesSpida/', getMiniaturasSpida, name='ImagenesSpida'), #DATOS: listado de imagenes spida
    path('spida/acceso/', getLoginSpida, name='LoginSpida'),
    path('spida/sucesos/', getSucesosSpida, name='SucesosSpida'),
    path('spida/documents/', getDocumentacionSpida, name='DocumentacionSpida'),
    path('spida/informes/', getInformesTrimestrales, name='InformesTrimestrales'),
    path('spida/docu-eventos/', getDocumentsEventos, name='DocumentsEventos'),
    path('spida/docu-evento/', getListadoDocEvento, name='ListadoDocEvento'), #DATOS: listado de documentacion adjuntada del evento
    path('spida/adjuntos-evento/', getListadoAdjuntosEvento, name='ListadoAdjuntosEvento'), #DATOS: listado de documentacion adjuntada del evento
    path('spida/documentos-adjunto-evento/', getListadoDocumentosAdjuntoEvento, name='ListadoDocumentosAdjuntoEvento'), #DATOS: listado de documentacion adjuntada del evento
    # path('spida/prueba/', prueba, name='prueba'),
    path('spida/protocolo/', getProtocoloActuacion, name='ProtocoloActuacion'),
    path('spida/login/', LoginView.as_view(template_name='loginSpida.html'), name="login"),
    path('spida/valores24h/', getValores24h, name='Valores24h'), #DATOS: valores 24h canal
    path('spida/prediccion24h/', getPrediccion24h, name='Prediccion24h'), #DATOS: prediccion24h canal
    path('spida/informestrimestrales/', getListadoInformesTrimestrales, name='ListadoInformesTrimestrales'),
    path('spida/view_informe_trimestral_spida/', OpenInformeTrimestral, name='OpenInformeTrimestral'), 
    path('spida/download_informe_trimestral_spida/', DownloadInformeTrimestral, name='DownloadInformeTrimestral'),
    path('spida/download_docu-eventos/<slug:idDoc>/', DownloadDocuEventos, name='DownloadDocuEventos'), 
    path('spida/protocolo_SPIDA_INUNCAEX/', OpenProcoloto, name="OpenProtocolo"),
    path('spida/imagen/',  getImagenSpida ,name='getImagenSpida'),
    path('spida/cielo/',  getCieloAemet ,name='CieloAemet'), #DATOS: Estado Cielo Aemet
    path('spida/harmonie/',  getImagenesPreAcumAemet ,name='ImagenesPreAcumAemet'), #DATOS: imagenes Precipitacion Acumulada 1 hora Aemet
    path('spida/radar/',  getImagenesRadar ,name='ImagenesRadar'), #DATOS: imagenes Radar Precipitacion Acumulada 1 hora Aemet
    path('spida/solar/',  getHorariosSol ,name='HorariosSol'), #DATOS: horas de salida y puesta de sol 
    path('spida/legendMN/',  getLegendaModelosNumericos ,name='LegendModelosNumericos'), #DATOS: colores de la leyeda de la Precipitacion Acum 1 h (Modelos Numericos Aemet)
    path('spida/legendRadar/',  getLegendaRadar ,name='LegendRadar'), #DATOS: colores de la leyeda de la Precipitacion Acum 1 h (Radar Aemet)
]

