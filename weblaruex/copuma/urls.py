from django.urls import path
from copuma.views import getPortadaJuntaex, getPortadaVraex, GetHomeMuestrasPublic, GetMuestrasPublic, GetGraficaPublic, GetGraficaPublicDose, GetHomeMuestras, GetMuestras, GetGrafica, Verificar, Verificada, EnviarMuestra, InsertarProduccion, ActualizarDB, MostrarLimites, MostrarSinLimites, UploadCopuma, GetMuestrasPublicNew

app_name = 'vraex'

urlpatterns = [
    path('juntaex/vraex/map/', GetHomeMuestrasPublic, name='juntaexMapPublicoVraex'),
    path('vraex/muestras/<slug:cod_muestra>/<slug:cod_analisis>/<slug:cod_procedencia>/', GetMuestrasPublic,
         name='consultaMuestrasPublico'),
    path('juntaex/vraex/muestras/<slug:cod_muestra>/', GetMuestrasPublicNew),
    path('vraex/getgrafica/<slug:cod_muestra>/<slug:cod_analisis>/<slug:cod_procedencia>/', GetGraficaPublic),
    path('juntaex/vraex/getgrafica/<slug:cod_muestra>/<slug:cod_analisis>/<slug:cod_procedencia>/', GetGraficaPublic),

    path('vraex/getgraficadose/<slug:cod_muestra>/<slug:cod_analisis>/<slug:cod_procedencia>/',
         GetGraficaPublicDose, name='graficaDosisPublico'),
    path('juntaex/vraex/getgraficadose/<slug:cod_muestra>/<slug:cod_analisis>/<slug:cod_procedencia>/',
         GetGraficaPublicDose, name='graficaDosisPublico'),

    path('private/vraex/', getPortadaVraex, name='vraexPortada'),
    path('private/vraex/map/', GetHomeMuestrasPublic, name='vraexMapaPublico'),
    path('private/vraex/mapPvt/', GetHomeMuestras, name='vraexMapaPrivado'),
    path('private/vraex/muestras/<slug:cod_muestra>/<slug:cod_analisis>/<slug:cod_procedencia>/', GetMuestras),
    path('private/vraex/getgrafica/<slug:cod_muestra>/<slug:cod_analisis>/<slug:cod_procedencia>/', GetGrafica),
    path('private/vraex/verificar/', Verificar, name='vraexVerificacion'),
    path('private/vraex/verificada/<slug:cod_muestra>/<slug:cod_analisis>/<slug:cod_procedencia>/', Verificada),
    path('private/vraex/subidacopuma/', UploadCopuma, name='vraexSubidaDatos'),
    path('private/vraex/enviar_muestra/<slug:motivo_muestreo_codmuestreo>/<slug:fecha_recogida_inicial>/<slug:fecha_recogida_final>/<slug:fecha_analisis>/<slug:instalacion_codinstalacion>/<slug:laboratorio_codlaboratorio>/<slug:muestra_codmuestra>/<slug:isotopo_codisotopo>/<slug:isotopo_analisis_codanalisis>/<slug:estacion_codprocedencia>/<slug:masa>/<slug:metaestable>/<slug:actividad_medida>/<slug:error_actividad_medida>/<slug:lid_medida>/', EnviarMuestra),
    path(r'^private/vraex/insertar_produccion/([\S]*)/([\S]*)/([\S]*)/$', InsertarProduccion),
    path('private/vraex/actualizarDB/', ActualizarDB, name='vraexActualizarDB'),
    path('private/vraex/limites_maximos/', MostrarLimites, name='vraexLimitesMaximos'),
    path('private/vraex/sin_limites_maximos/', MostrarSinLimites, name='vraexSinLimitesMaximos'),
]

