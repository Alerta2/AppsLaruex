from django.urls import path
from .views import *

app_name = 'gestionmuestras'

urlpatterns = [
    path('private/gestionmuestras/', opcionesGestionMuestras, name='gestmuesOpciones'),
    path('private/gestionmuestras/listadoMuestras/', listadoMuestras, name='gestmuesListadoMuestras'),
    path('private/gestionmuestras/listadoMuestrasDatos/', listadoMuestrasDatos, name='gestmuesListadoMuestras2'),
    path('private/gestionmuestras/infoMuestra/<slug:id_muestra>/', getInfoMuestra, name='gestmuesGetInfoMuestra'),
    path('private/gestionmuestras/infoMuestraForm/', getInfoMuestraForm, name='gestmuesGetInfoMuestraForm'),
    path('private/gestionmuestras/insertarMuestra/', insertarMuestra, name='gestmuesInsertarMuestra'),
    path('private/gestionmuestras/insertarMuestra/consultarParametrosTipo/<slug:tipo>/', consultarParametrosTipo, name='gestmuesConsultarParametrosTipo'),
    path('private/gestionmuestras/insertarDeterminaciones/', insertarDeterminaciones, name='gestmuesInsertarDeterminaciones'),
    path('private/gestionmuestras/insertarTratamientos/', insertarTratamientos, name='gestmuesInsertarTratamientos'),
    path('private/gestionmuestras/infoMuestra/solicitarAlicuotas/<slug:id_muestra>/', getAlicuotasMuestra, name='gestmuesGetAlicuotasMuestra'),

    path('private/gestionmuestras/muestrasInforme/', muestrasInforme, name='gestmuesMuestrasInformes'),
    path('private/gestionmuestras/muestrasInformeDatos/', muestrasInformeDatos, name='gestmuesMuestrasInformesDatos'),

    
    path('private/gestionmuestras/listadoChurros/', listadoChurros, name='gestmuesListadoChurros'),
    path('private/gestionmuestras/listadoChurrosDatos/', listadoChurrosDatos, name='gestmuesListadoChurros2'),

    # consultor de medidas
    path('private/gestionmuestras/consultorMedidas/', consultorMedidas, name='gestmuesConsultorMedidas'),
    path('private/gestionmuestras/infoAlicuota/<slug:id_alicuota>/', infoAlicuota, name='gestmuesInfoAlicuota'),

    # finalizar muestras
    path('private/gestionmuestras/verificarMuestra/', verificarMuestra, name='gestmuesVerificarMuestra'),

    # alfa
    path('private/gestionmuestras/capturarInformeAlfa/', capturarInformeAlfa, name='gestmuesCapturarInformeAlfa'),
    # copuma
    path('private/gestionmuestras/capturarExcelCopuma/', capturarExcelCopuma, name='gestmuesCapturarExcelCopuma'),
    # capturar dbf
    path('private/gestionmuestras/capturarDBFgestmues/', capturarDBFgestmues, name='gestmuesCapturarDBFgestmues'),
    # Consulta duplicados alfa beta
    path('private/gestionmuestras/consultaDuplicados/', consultaDuplicados, name='gestmuesConsultaDuplicados'),

]
