# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AdjuntosEventos(models.Model):
    id_adjunto = models.AutoField(db_column='ID_ADJUNTO', primary_key=True)  # Field name made lowercase.
    id_evento = models.ForeignKey('Eventos', models.DO_NOTHING, db_column='ID_EVENTO')  # Field name made lowercase.
    titulo_adjunto = models.CharField(db_column='TITULO_ADJUNTO', max_length=50)  # Field name made lowercase.
    id_usuario = models.IntegerField(db_column='ID_USUARIO')  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL')  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'adjuntos_eventos'
        unique_together = (('id_adjunto', 'id_evento'),)


class AvisosMeteorologicosAemet(models.Model):
    nivel = models.CharField(db_column='NIVEL', primary_key=True, max_length=200)  # Field name made lowercase.
    id_zona_meteo_aemet = models.CharField(db_column='ID_ZONA_METEO_AEMET', max_length=200)  # Field name made lowercase.
    fecha_comienzo = models.DateTimeField(db_column='FECHA_COMIENZO')  # Field name made lowercase.
    fecha_fin = models.DateTimeField(db_column='FECHA_FIN')  # Field name made lowercase.
    tipo_aviso = models.CharField(db_column='TIPO_AVISO', max_length=200, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=200, blank=True, null=True)  # Field name made lowercase.
    instruccion = models.CharField(db_column='INSTRUCCION', max_length=200, blank=True, null=True)  # Field name made lowercase.
    probabilidad = models.CharField(db_column='PROBABILIDAD', max_length=200, blank=True, null=True)  # Field name made lowercase.
    valido_actual = models.IntegerField(db_column='VALIDO_ACTUAL', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'avisos_meteorologicos_aemet'
        unique_together = (('nivel', 'id_zona_meteo_aemet', 'fecha_comienzo', 'fecha_fin'),)


class Canales(models.Model):
    id_canal = models.AutoField(db_column='ID_CANAL', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    unidades = models.CharField(db_column='UNIDADES', max_length=20)  # Field name made lowercase.
    tabla_bd = models.CharField(db_column='TABLA_BD', max_length=100, blank=True, null=True)  # Field name made lowercase.
    id_canal_hist = models.IntegerField(db_column='ID_CANAL_HIST', blank=True, null=True)  # Field name made lowercase.
    tabla_bd_hist = models.CharField(db_column='TABLA_BD_HIST', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'canales'


class Credenciales(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_red = models.IntegerField(db_column='ID_RED')  # Field name made lowercase.
    clave = models.CharField(db_column='CLAVE', max_length=10000)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'credenciales'


class DocumentacionAdjunto(models.Model):
    id_documento = models.AutoField(db_column='ID_DOCUMENTO', primary_key=True)  # Field name made lowercase.
    id_adjunto = models.ForeignKey(AdjuntosEventos, models.DO_NOTHING, db_column='ID_ADJUNTO')  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    extension = models.CharField(db_column='EXTENSION', max_length=100)  # Field name made lowercase.
    size = models.IntegerField(db_column='SIZE')  # Field name made lowercase.
    ruta = models.CharField(db_column='RUTA', max_length=500)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'documentacion_adjunto'
        unique_together = (('id_documento', 'id_adjunto'),)


class Estaciones(models.Model):
    id_estacion = models.AutoField(db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=45)  # Field name made lowercase.
    id_tipo = models.ForeignKey('TipoEstaciones', models.DO_NOTHING, db_column='ID_TIPO', blank=True, null=True)  # Field name made lowercase.
    id_red = models.ForeignKey('Redes', models.DO_NOTHING, db_column='ID_RED')  # Field name made lowercase.
    id_subcuenca = models.ForeignKey('SubcuencasExtremadura', models.DO_NOTHING, db_column='ID_SUBCUENCA', blank=True, null=True)  # Field name made lowercase.
    monitorizar = models.IntegerField(db_column='MONITORIZAR')  # Field name made lowercase.
    visualizar = models.IntegerField(db_column='VISUALIZAR')  # Field name made lowercase.
    sensor_lat = models.FloatField(db_column='SENSOR_LAT', blank=True, null=True)  # Field name made lowercase.
    sensor_lon = models.FloatField(db_column='SENSOR_LON', blank=True, null=True)  # Field name made lowercase.
    estacion_lat = models.FloatField(db_column='ESTACION_LAT', blank=True, null=True)  # Field name made lowercase.
    estacion_lon = models.FloatField(db_column='ESTACION_LON', blank=True, null=True)  # Field name made lowercase.
    cod_externo = models.CharField(db_column='COD_EXTERNO', max_length=200, blank=True, null=True)  # Field name made lowercase.
    widget_aemet = models.CharField(db_column='WIDGET_AEMET', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'estaciones'


class Eventos(models.Model):
    id_evento = models.AutoField(db_column='ID_EVENTO', primary_key=True)  # Field name made lowercase.
    titulo = models.CharField(db_column='TITULO', max_length=100)  # Field name made lowercase.
    fecha_hora_inicio = models.DateTimeField(db_column='FECHA_HORA_INICIO')  # Field name made lowercase.
    fecha_hora_fin = models.DateTimeField(db_column='FECHA_HORA_FIN', blank=True, null=True)  # Field name made lowercase.
    estado = models.PositiveIntegerField(db_column='ESTADO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'eventos'


class FicherosPrediccionAemet48H(models.Model):
    hora_prediccion = models.IntegerField(db_column='HORA_PREDICCION', primary_key=True)  # Field name made lowercase.
    hora_simulacion = models.IntegerField(db_column='HORA_SIMULACION')  # Field name made lowercase.
    nombre_fichero = models.CharField(db_column='NOMBRE_FICHERO', max_length=100)  # Field name made lowercase.
    fecha_simulacion_utc = models.DateTimeField(db_column='FECHA_SIMULACION_UTC')  # Field name made lowercase.
    fecha_prediccion_utc = models.DateTimeField(db_column='FECHA_PREDICCION_UTC')  # Field name made lowercase.
    fichero = models.TextField(db_column='FICHERO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ficheros_prediccion_aemet_48h'
        unique_together = (('hora_prediccion', 'hora_simulacion'),)


class InformesTrimestrales(models.Model):
    id_informe = models.AutoField(db_column='ID_INFORME', primary_key=True)  # Field name made lowercase.
    id_cuatrimestre = models.IntegerField(db_column='ID_CUATRIMESTRE')  # Field name made lowercase.
    year = models.IntegerField(db_column='YEAR')  # Field name made lowercase.
    fecha_hora_local_inicio = models.DateTimeField(db_column='FECHA_HORA_LOCAL_INICIO')  # Field name made lowercase.
    fecha_hora_local_fin = models.DateTimeField(db_column='FECHA_HORA_LOCAL_FIN')  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=200)  # Field name made lowercase.
    size = models.IntegerField(db_column='SIZE')  # Field name made lowercase.
    ruta = models.CharField(db_column='RUTA', max_length=200)  # Field name made lowercase.
    fecha_hora_subida = models.DateTimeField(db_column='FECHA_HORA_SUBIDA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'informes_trimestrales'
        unique_together = (('id_informe', 'fecha_hora_local_inicio', 'fecha_hora_local_fin'),)


class OperatividadApps(models.Model):
    nombre = models.CharField(db_column='NOMBRE', primary_key=True, max_length=200)  # Field name made lowercase.
    ejecutar = models.IntegerField(db_column='EJECUTAR', blank=True, null=True)  # Field name made lowercase.
    nombre_ejecutable = models.CharField(db_column='NOMBRE_EJECUTABLE', max_length=100, blank=True, null=True)  # Field name made lowercase.
    periodo_ejecucion = models.IntegerField(db_column='PERIODO_EJECUCION')  # Field name made lowercase.
    num_periodos_alarma = models.IntegerField(db_column='NUM_PERIODOS_ALARMA')  # Field name made lowercase.
    ultima_ejecucion = models.DateTimeField(db_column='ULTIMA_EJECUCION', blank=True, null=True)  # Field name made lowercase.
    error = models.IntegerField(db_column='ERROR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'operatividad_apps'


class ParamsPredNivelCurvaRecesion(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    a = models.FloatField(db_column='A')  # Field name made lowercase.
    alpha = models.FloatField(db_column='ALPHA')  # Field name made lowercase.
    b = models.FloatField(db_column='B')  # Field name made lowercase.
    beta = models.FloatField(db_column='BETA')  # Field name made lowercase.
    h0 = models.FloatField(db_column='H0')  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'params_pred_nivel_curva_recesion'


class Prediccion24H(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_pred = models.IntegerField(db_column='ID_PRED')  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'prediccion_24h'
        unique_together = (('id_estacion', 'id_pred', 'id_canal'),)


class Redes(models.Model):
    id_red = models.AutoField(db_column='ID_RED', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'redes'


class RelacionEstacionCanales(models.Model):
    id_estacion = models.IntegerField(db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.IntegerField(db_column='ID_CANAL')  # Field name made lowercase.
    cod_externo_canal = models.CharField(db_column='COD_EXTERNO_CANAL', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_estacion_canales'
        unique_together = (('id_estacion', 'id_canal'),)


class RelacionEstacionSaih(models.Model):
    estacion_id = models.IntegerField(db_column='ESTACION_ID', primary_key=True)  # Field name made lowercase.
    id_saih = models.CharField(db_column='ID_SAIH', max_length=200)  # Field name made lowercase.
    monitorizar = models.IntegerField(db_column='MONITORIZAR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_estacion_saih'
        unique_together = (('estacion_id', 'id_saih'),)


class RelacionEstacionesMeteo(models.Model):
    id_estacion_hidro = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION_HIDRO', primary_key=True)  # Field name made lowercase.
    id_estacion_pluvio = models.IntegerField(db_column='ID_ESTACION_PLUVIO')  # Field name made lowercase.
    area_porcentual = models.FloatField(db_column='AREA_PORCENTUAL')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_estaciones_meteo'
        unique_together = (('id_estacion_hidro', 'id_estacion_pluvio'),)


class RelacionParametroCanal(models.Model):
    id_parametro = models.IntegerField(db_column='ID_PARAMETRO', primary_key=True)  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    tabla_bd = models.CharField(db_column='TABLA_BD', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_parametro_canal'


class SubcuencasExtremadura(models.Model):
    id_subcuenca = models.IntegerField(db_column='ID_SUBCUENCA', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    cuenca = models.CharField(db_column='CUENCA', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'subcuencas_extremadura'


class SucesosInundacion(models.Model):
    id_suceso = models.AutoField(db_column='ID_SUCESO', primary_key=True)  # Field name made lowercase.
    rotulo = models.CharField(db_column='ROTULO', max_length=100)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=500)  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL')  # Field name made lowercase.
    imagen = models.TextField(db_column='IMAGEN')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sucesos_inundacion'


class TipoEstaciones(models.Model):
    id_tipo = models.AutoField(db_column='ID_TIPO', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_estaciones'


class UltimasImagenes(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_camara = models.IntegerField(db_column='ID_CAMARA')  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL', blank=True, null=True)  # Field name made lowercase.
    imagen = models.TextField(db_column='IMAGEN', blank=True, null=True)  # Field name made lowercase.
    miniatura = models.TextField(db_column='MINIATURA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ultimas_imagenes'
        unique_together = (('id_estacion', 'id_camara'),)


class UltimosValores(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR')  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ultimos_valores'
        unique_together = (('id_estacion', 'id_canal'),)


class UmbralesRios(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    limite_n0 = models.IntegerField(db_column='LIMITE_N0')  # Field name made lowercase.
    limite_n1 = models.IntegerField(db_column='LIMITE_N1')  # Field name made lowercase.
    limite_n2 = models.IntegerField(db_column='LIMITE_N2')  # Field name made lowercase.
    limite_n3 = models.IntegerField(db_column='LIMITE_N3')  # Field name made lowercase.
    limite_desbordamiento = models.FloatField(db_column='LIMITE_DESBORDAMIENTO')  # Field name made lowercase.
    nivel_t10 = models.FloatField(db_column='NIVEL_T10', blank=True, null=True)  # Field name made lowercase.
    nivel_t100 = models.FloatField(db_column='NIVEL_T100', blank=True, null=True)  # Field name made lowercase.
    nivel_t500 = models.FloatField(db_column='NIVEL_T500', blank=True, null=True)  # Field name made lowercase.
    observaciones = models.CharField(db_column='OBSERVACIONES', max_length=200, blank=True, null=True)  # Field name made lowercase.
    id_arpsis = models.CharField(db_column='ID_ARPSIS', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'umbrales_rios'


class ValoresPrecipitacion10D(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR')  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'valores_precipitacion_10d'
        unique_together = (('id_estacion', 'id_canal', 'fecha_hora_utc'),)


class ValoresSpida10D(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR')  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'valores_spida_10d'
        unique_together = (('id_estacion', 'id_canal', 'fecha_hora_utc'),)


class ValoresVisualizados10D(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR')  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'valores_visualizados_10d'
        unique_together = (('id_estacion', 'id_canal', 'fecha_hora_utc'),)


class ZonaMeteoalertaAemet(models.Model):
    id_zona_meteo_aemet = models.IntegerField(db_column='ID_ZONA_METEO_AEMET', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=255)  # Field name made lowercase.
    estado = models.CharField(db_column='ESTADO', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'zona_meteoalerta_aemet'
        unique_together = (('id_zona_meteo_aemet', 'nombre'),)
