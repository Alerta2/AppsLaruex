# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AvisosMeteorologicosAemet(models.Model):
    nivel = models.CharField(db_column='NIVEL', primary_key=True, max_length=200)  # Field name made lowercase.
    zona_aemet = models.CharField(db_column='ZONA_AEMET', max_length=200)  # Field name made lowercase.
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
        unique_together = (('nivel', 'zona_aemet', 'fecha_comienzo', 'fecha_fin'),)


class Canales(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=45, blank=True, null=True)  # Field name made lowercase.
    unidades = models.CharField(db_column='UNIDADES', max_length=20, blank=True, null=True)  # Field name made lowercase.
    factor = models.FloatField(db_column='FACTOR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'canales'


class ControlConexiones(models.Model):
    estacion = models.IntegerField(db_column='ESTACION', primary_key=True)  # Field name made lowercase.
    conexion = models.IntegerField(db_column='CONEXION')  # Field name made lowercase.
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'control_conexiones'
        unique_together = (('estacion', 'conexion'),)


class ControlEstadoEstacion(models.Model):
    id_alertas = models.IntegerField(db_column='ID_ALERTAS', primary_key=True)  # Field name made lowercase.
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA')  # Field name made lowercase.
    estaciones = models.ForeignKey('Estaciones', models.DO_NOTHING, db_column='ESTACIONES_ID')  # Field name made lowercase.
    mensaje = models.TextField(db_column='MENSAJE')  # Field name made lowercase.
    tipo = models.IntegerField(db_column='TIPO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'control_estado_estacion'
        unique_together = (('id_alertas', 'fecha_hora', 'estaciones'),)


class DatosCorregidos(models.Model):
    id_datos_corregidos = models.IntegerField(primary_key=True)
    fecha_hora = models.DateTimeField()
    canal = models.IntegerField()
    estacion = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'datos_corregidos'


class DescripcionTablas(models.Model):
    id_entrada = models.IntegerField(primary_key=True)
    nombre_tabla = models.CharField(max_length=100)
    descripcion_tabla = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'descripcion_tablas'


class Detectores(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=30, blank=True, null=True)  # Field name made lowercase.
    unidades = models.CharField(db_column='UNIDADES', max_length=30, blank=True, null=True)  # Field name made lowercase.
    denom = models.CharField(db_column='DENOM', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'detectores'


class Dosis(models.Model):
    id = models.BigAutoField(primary_key=True)
    idgeopos = models.ForeignKey('Geopos', models.DO_NOTHING, db_column='idgeopos', blank=True, null=True)
    valor = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dosis'


class Esp3Minutos(models.Model):
    fecha_hora_inicial = models.DateTimeField(db_column='FECHA_HORA_INICIAL', primary_key=True)  # Field name made lowercase.
    relacion_detectores_estacion_id = models.IntegerField(db_column='RELACION_DETECTORES_ESTACION_ID')  # Field name made lowercase.
    tiempo_seg = models.IntegerField(db_column='TIEMPO_SEG', blank=True, null=True)  # Field name made lowercase.
    cnf = models.CharField(db_column='CNF', max_length=255, blank=True, null=True)  # Field name made lowercase.
    txt = models.CharField(db_column='TXT', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'esp_3_minutos'
        unique_together = (('fecha_hora_inicial', 'relacion_detectores_estacion_id'),)


class Espectros(models.Model):
    id = models.BigAutoField(primary_key=True)
    idgeopos = models.ForeignKey('Geopos', models.DO_NOTHING, db_column='idgeopos', blank=True, null=True)
    espectro = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'espectros'


class EspectrosAcumulados(models.Model):
    fecha_hora_inicial = models.DateTimeField(db_column='FECHA_HORA_INICIAL', primary_key=True)  # Field name made lowercase.
    relacion_detectores_estacion_id = models.IntegerField(db_column='RELACION_DETECTORES_ESTACION_ID')  # Field name made lowercase.
    tiempo_seg = models.IntegerField(db_column='TIEMPO_SEG', blank=True, null=True)  # Field name made lowercase.
    cnf = models.CharField(db_column='CNF', max_length=255, blank=True, null=True)  # Field name made lowercase.
    txt = models.CharField(db_column='TXT', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'espectros_acumulados'
        unique_together = (('fecha_hora_inicial', 'relacion_detectores_estacion_id'),)


class EspectrosDiarios(models.Model):
    fecha_hora_inicial = models.DateTimeField(db_column='FECHA_HORA_INICIAL', primary_key=True)  # Field name made lowercase.
    relacion_detectores_estacion_id = models.IntegerField(db_column='RELACION_DETECTORES_ESTACION_ID')  # Field name made lowercase.
    tiempo_seg = models.IntegerField(db_column='TIEMPO_SEG', blank=True, null=True)  # Field name made lowercase.
    cnf = models.CharField(db_column='CNF', max_length=255, blank=True, null=True)  # Field name made lowercase.
    txt = models.CharField(db_column='TXT', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'espectros_diarios'
        unique_together = (('fecha_hora_inicial', 'relacion_detectores_estacion_id'),)


class EstEspecGamma(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    relacion_detectores_estacion_id = models.IntegerField(db_column='RELACION_DETECTORES_ESTACION_ID')  # Field name made lowercase.
    isotopos_id = models.IntegerField(db_column='ISOTOPOS_ID')  # Field name made lowercase.
    actividad = models.FloatField(db_column='ACTIVIDAD', blank=True, null=True)  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR', blank=True, null=True)  # Field name made lowercase.
    amd = models.FloatField(db_column='AMD', blank=True, null=True)  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'est_espec_gamma'
        unique_together = (('fecha_hora', 'relacion_detectores_estacion_id', 'isotopos_id'),)


class EstEspecGammaAcumulados(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    relacion_detectores_estacion_id = models.IntegerField(db_column='RELACION_DETECTORES_ESTACION_ID')  # Field name made lowercase.
    isotopos_id = models.IntegerField(db_column='ISOTOPOS_ID')  # Field name made lowercase.
    actividad = models.FloatField(db_column='ACTIVIDAD', blank=True, null=True)  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR', blank=True, null=True)  # Field name made lowercase.
    amd = models.FloatField(db_column='AMD', blank=True, null=True)  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'est_espec_gamma_acumulados'
        unique_together = (('fecha_hora', 'relacion_detectores_estacion_id', 'isotopos_id'),)


class EstGamYRadioyodos(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estaciones = models.ForeignKey('Estaciones', models.DO_NOTHING, db_column='ESTACIONES_ID')  # Field name made lowercase.
    canales = models.ForeignKey(Canales, models.DO_NOTHING, db_column='CANALES_ID')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'est_gam_y_radioyodos'
        unique_together = (('fecha_hora', 'estaciones', 'canales'),)


class EstGamYRadioyodosAcumulados(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estaciones = models.ForeignKey('Estaciones', models.DO_NOTHING, db_column='ESTACIONES_ID')  # Field name made lowercase.
    canales = models.ForeignKey(Canales, models.DO_NOTHING, db_column='CANALES_ID')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'est_gam_y_radioyodos_acumulados'
        unique_together = (('fecha_hora', 'estaciones', 'canales'),)


class EstMeteorologicas(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estaciones = models.ForeignKey('Estaciones', models.DO_NOTHING, db_column='ESTACIONES_ID')  # Field name made lowercase.
    canales = models.ForeignKey(Canales, models.DO_NOTHING, db_column='CANALES_ID')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'est_meteorologicas'
        unique_together = (('fecha_hora', 'estaciones', 'canales'),)


class EstMeteorologicasPred(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estaciones = models.ForeignKey('Estaciones', models.DO_NOTHING, db_column='ESTACIONES_ID')  # Field name made lowercase.
    canales = models.ForeignKey(Canales, models.DO_NOTHING, db_column='CANALES_ID')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'est_meteorologicas_pred'
        unique_together = (('fecha_hora', 'estaciones', 'canales'),)


class Estaciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=45, blank=True, null=True)  # Field name made lowercase.
    map_lat = models.FloatField(db_column='MAP_LAT', blank=True, null=True)  # Field name made lowercase.
    map_lon = models.FloatField(db_column='MAP_LON', blank=True, null=True)  # Field name made lowercase.
    dir_fotos = models.CharField(db_column='DIR_FOTOS', max_length=255, blank=True, null=True)  # Field name made lowercase.
    visualizar = models.IntegerField(db_column='VISUALIZAR', blank=True, null=True)  # Field name made lowercase.
    id_subcuenca = models.ForeignKey('SubcuencasExtremadura', models.DO_NOTHING, db_column='ID_SUBCUENCA', blank=True, null=True)  # Field name made lowercase.
    monitorizar = models.IntegerField(db_column='MONITORIZAR', blank=True, null=True)  # Field name made lowercase.
    tipo_estacion = models.IntegerField(db_column='TIPO_ESTACION', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'estaciones'


class Geopos(models.Model):
    id = models.BigAutoField(primary_key=True)
    idsesion = models.ForeignKey('Sesion', models.DO_NOTHING, db_column='idsesion', blank=True, null=True)
    fechahora = models.DateTimeField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    northing = models.CharField(max_length=1, blank=True, null=True)
    westing = models.CharField(max_length=1, blank=True, null=True)
    altitud = models.FloatField(blank=True, null=True)
    velocidad = models.FloatField(blank=True, null=True)
    idestacionmovil = models.IntegerField(db_column='idEstacionMovil', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'geopos'


class HistoricoTotalDatos(models.Model):
    dia = models.DateField(db_column='DIA', primary_key=True)  # Field name made lowercase.
    estacion = models.IntegerField(db_column='ESTACION')  # Field name made lowercase.
    can_det_est = models.IntegerField(db_column='CAN_DET_EST')  # Field name made lowercase.
    isotopo = models.IntegerField(db_column='ISOTOPO')  # Field name made lowercase.
    datos_radio = models.IntegerField(db_column='DATOS_RADIO', blank=True, null=True)  # Field name made lowercase.
    errores_radio = models.IntegerField(db_column='ERRORES_RADIO', blank=True, null=True)  # Field name made lowercase.
    intranet = models.IntegerField(db_column='INTRANET', blank=True, null=True)  # Field name made lowercase.
    recuperados = models.IntegerField(db_column='RECUPERADOS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'historico_total_datos'
        unique_together = (('dia', 'estacion', 'can_det_est', 'isotopo'),)


class Imagenes(models.Model):
    id = models.BigAutoField(primary_key=True)
    idgeopos = models.ForeignKey(Geopos, models.DO_NOTHING, db_column='idgeopos', blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    imagen = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'imagenes'


class Incidencias(models.Model):
    id = models.BigAutoField(primary_key=True)
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', blank=True, null=True)  # Field name made lowercase.
    estacion_id = models.IntegerField(db_column='ESTACION_ID', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_apertura = models.DateTimeField(db_column='FECHA_HORA_APERTURA', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_cierre = models.DateTimeField(db_column='FECHA_HORA_CIERRE', blank=True, null=True)  # Field name made lowercase.
    comentario_apertura = models.CharField(db_column='COMENTARIO_APERTURA', max_length=160, blank=True, null=True)  # Field name made lowercase.
    comentario_cierre = models.CharField(db_column='COMENTARIO_CIERRE', max_length=160, blank=True, null=True)  # Field name made lowercase.
    estado = models.IntegerField(db_column='ESTADO', blank=True, null=True)  # Field name made lowercase.
    usuario = models.CharField(db_column='USUARIO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    enviado = models.IntegerField(db_column='ENVIADO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'incidencias'


class InformesConfirmados(models.Model):
    id_informes_confirmados = models.IntegerField(primary_key=True)
    id_usuario_informe = models.IntegerField()
    fecha_hora_informe = models.DateTimeField()
    id_usuario_vb = models.IntegerField()
    fecha_hora_confirmacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'informes_confirmados'


class InformesPendientesConfirmacion(models.Model):
    id_informes_pendientes_confirmacion = models.IntegerField(primary_key=True)
    id_usuario_informe = models.IntegerField()
    fecha_hora_informe = models.DateTimeField()
    id_usuario_vb = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'informes_pendientes_confirmacion'


class Isotopos(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    n_iso = models.CharField(db_column='N_ISO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    energia = models.FloatField(db_column='ENERGIA', blank=True, null=True)  # Field name made lowercase.
    c_izq = models.PositiveIntegerField(db_column='C_IZQ', blank=True, null=True)  # Field name made lowercase.
    c_der = models.PositiveIntegerField(db_column='C_DER', blank=True, null=True)  # Field name made lowercase.
    artificial = models.IntegerField(db_column='ARTIFICIAL', blank=True, null=True)  # Field name made lowercase.
    factor_nivel = models.FloatField(db_column='FACTOR_NIVEL', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'isotopos'


class LeerFicherosSpida(models.Model):
    estacion_id = models.IntegerField(db_column='ESTACION_ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=200)  # Field name made lowercase.
    directorio_ftp = models.CharField(db_column='DIRECTORIO_FTP', max_length=200)  # Field name made lowercase.
    procesar_dat = models.IntegerField(db_column='PROCESAR_DAT')  # Field name made lowercase.
    procesar_imagenes = models.IntegerField(db_column='PROCESAR_IMAGENES')  # Field name made lowercase.
    eliminar_dat = models.IntegerField(db_column='ELIMINAR_DAT')  # Field name made lowercase.
    eliminar_imagenes = models.IntegerField(db_column='ELIMINAR_IMAGENES')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'leer_ficheros_spida'


class MediasDiarias(models.Model):
    fecha = models.DateField(db_column='FECHA', primary_key=True)  # Field name made lowercase.
    id_estacion = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION')  # Field name made lowercase.
    id_detector = models.IntegerField(db_column='ID_DETECTOR')  # Field name made lowercase.
    id_canal = models.IntegerField(db_column='ID_CANAL')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR')  # Field name made lowercase.
    n1 = models.IntegerField(db_column='N1', blank=True, null=True)  # Field name made lowercase.
    n2 = models.IntegerField(db_column='N2', blank=True, null=True)  # Field name made lowercase.
    n3 = models.IntegerField(db_column='N3', blank=True, null=True)  # Field name made lowercase.
    operatividad = models.FloatField(db_column='OPERATIVIDAD', blank=True, null=True)  # Field name made lowercase.
    total_datos = models.IntegerField(db_column='TOTAL_DATOS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'medias_diarias'
        unique_together = (('fecha', 'id_estacion', 'id_detector', 'id_canal'),)


class MediasYLimitesEstacionCanal(models.Model):
    estaciones = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ESTACIONES_ID', primary_key=True)  # Field name made lowercase.
    canales = models.ForeignKey(Canales, models.DO_NOTHING, db_column='CANALES_ID')  # Field name made lowercase.
    tipo = models.IntegerField(db_column='TIPO')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'medias_y_limites_estacion_canal'
        unique_together = (('estaciones', 'canales', 'tipo'),)


class Menmovil(models.Model):
    id_mensaje = models.AutoField(db_column='ID_MENSAJE', primary_key=True)  # Field name made lowercase.
    usuario = models.CharField(db_column='USUARIO', max_length=50)  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=50)  # Field name made lowercase.
    mensaje = models.CharField(db_column='MENSAJE', max_length=160)  # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=2)  # Field name made lowercase.
    procesado = models.IntegerField(db_column='PROCESADO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'menmovil'


class Mensaje(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    enviado = models.IntegerField(db_column='ENVIADO')  # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=2)  # Field name made lowercase.
    mensaje = models.CharField(db_column='MENSAJE', max_length=160)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mensaje'
        unique_together = (('fecha_hora', 'enviado'),)


class MensajeHistoenvio(models.Model):
    fecha = models.DateField(db_column='FECHA', primary_key=True)  # Field name made lowercase.
    tipo = models.IntegerField(db_column='TIPO')  # Field name made lowercase.
    hora_envio = models.TimeField(db_column='HORA_ENVIO')  # Field name made lowercase.
    hora_confirmacion = models.TimeField(db_column='HORA_CONFIRMACION')  # Field name made lowercase.
    usuario = models.CharField(db_column='USUARIO', max_length=30)  # Field name made lowercase.
    remite = models.CharField(db_column='REMITE', max_length=30)  # Field name made lowercase.
    movil = models.CharField(db_column='MOVIL', max_length=12)  # Field name made lowercase.
    mensaje = models.CharField(db_column='MENSAJE', max_length=160)  # Field name made lowercase.
    intentos = models.IntegerField(db_column='INTENTOS')  # Field name made lowercase.
    confirmado = models.IntegerField(db_column='CONFIRMADO')  # Field name made lowercase.
    enviado = models.CharField(db_column='ENVIADO', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mensaje_histoenvio'
        unique_together = (('fecha', 'tipo', 'hora_envio', 'hora_confirmacion', 'movil'),)


class MensajesAlertas(models.Model):
    id_alertas = models.AutoField(db_column='ID_ALERTAS', primary_key=True)  # Field name made lowercase.
    f_h_inicial = models.DateTimeField(db_column='F_H_INICIAL')  # Field name made lowercase.
    estaciones = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='ESTACIONES_ID')  # Field name made lowercase.
    canales_id = models.IntegerField(db_column='CANALES_ID')  # Field name made lowercase.
    mensaje = models.TextField(db_column='MENSAJE')  # Field name made lowercase.
    tipo = models.IntegerField(db_column='TIPO')  # Field name made lowercase.
    enviado = models.IntegerField(db_column='ENVIADO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mensajes_alertas'
        unique_together = (('id_alertas', 'f_h_inicial', 'estaciones', 'canales_id'),)


class MensajesAnalista(models.Model):
    id_mensaje_analista = models.IntegerField(db_column='ID_MENSAJE_ANALISTA', primary_key=True)  # Field name made lowercase.
    descripcion = models.TextField(db_column='DESCRIPCION')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mensajes_analista'


class MensajesAyudaDecision(models.Model):
    id_ayuda = models.IntegerField(db_column='ID_AYUDA', primary_key=True)  # Field name made lowercase.
    id_mensaje_alerta = models.IntegerField(db_column='ID_MENSAJE_ALERTA')  # Field name made lowercase.
    mensaje_ayuda = models.TextField(db_column='MENSAJE_AYUDA')  # Field name made lowercase.
    tipo = models.IntegerField(db_column='TIPO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mensajes_ayuda_decision'
        unique_together = (('id_ayuda', 'id_mensaje_alerta'),)


class MensajesPredefinidos(models.Model):
    id_mensaje = models.IntegerField(db_column='ID_MENSAJE', primary_key=True)  # Field name made lowercase.
    descripcion_corta = models.CharField(db_column='DESCRIPCION_CORTA', max_length=250, blank=True, null=True)  # Field name made lowercase.
    descripcion_larga = models.TextField(db_column='DESCRIPCION_LARGA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mensajes_predefinidos'


class Meteo(models.Model):
    id = models.BigAutoField(primary_key=True)
    idgeopos = models.ForeignKey(Geopos, models.DO_NOTHING, db_column='idgeopos', blank=True, null=True)
    direccion_viento = models.FloatField(blank=True, null=True)
    velocidad_viento = models.FloatField(blank=True, null=True)
    temperatura = models.FloatField(blank=True, null=True)
    presion = models.FloatField(blank=True, null=True)
    humedad = models.FloatField(blank=True, null=True)
    lluvia = models.FloatField(blank=True, null=True)
    granizo = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'meteo'


class Monitoriza(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    id_estacion = models.IntegerField(db_column='ID_ESTACION')  # Field name made lowercase.
    id_canal = models.IntegerField(db_column='ID_CANAL')  # Field name made lowercase.
    mensaje = models.CharField(db_column='MENSAJE', max_length=20)  # Field name made lowercase.
    leido = models.IntegerField(db_column='LEIDO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'monitoriza'
        unique_together = (('fecha_hora', 'id_estacion', 'id_canal'),)


class MonitorizaSpida(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    comunicar_estado_sin_datos = models.IntegerField(db_column='COMUNICAR_ESTADO_SIN_DATOS')  # Field name made lowercase.
    monitorizacion_nocturna = models.IntegerField(db_column='MONITORIZACION_NOCTURNA')  # Field name made lowercase.
    monitorizacion_sin_datos = models.IntegerField(db_column='MONITORIZACION_SIN_DATOS')  # Field name made lowercase.
    monitoriza_lim_aviso = models.IntegerField(db_column='MONITORIZA_LIM_AVISO')  # Field name made lowercase.
    monitoriza_lim_medio = models.IntegerField(db_column='MONITORIZA_LIM_MEDIO')  # Field name made lowercase.
    monitoriza_lim_alarma = models.IntegerField(db_column='MONITORIZA_LIM_ALARMA')  # Field name made lowercase.
    monitoriza_nivel_rio = models.IntegerField(db_column='MONITORIZA_NIVEL_RIO')  # Field name made lowercase.
    contador = models.IntegerField(db_column='CONTADOR')  # Field name made lowercase.
    fecha_hora_penultimo_valor = models.DateTimeField(db_column='FECHA_HORA_PENULTIMO_VALOR')  # Field name made lowercase.
    estado_inicial = models.IntegerField(db_column='ESTADO_INICIAL')  # Field name made lowercase.
    estado_final = models.IntegerField(db_column='ESTADO_FINAL')  # Field name made lowercase.
    ultimo_sms = models.IntegerField(db_column='ULTIMO_SMS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'monitoriza_spida'
        unique_together = (('id_estacion', 'id_canal'),)


class Niveles(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estacion = models.IntegerField(db_column='ESTACION')  # Field name made lowercase.
    canal = models.IntegerField(db_column='CANAL')  # Field name made lowercase.
    detector = models.IntegerField(db_column='DETECTOR')  # Field name made lowercase.
    isotopo = models.IntegerField(db_column='ISOTOPO')  # Field name made lowercase.
    nivel = models.IntegerField(db_column='NIVEL')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'niveles'
        unique_together = (('fecha_hora', 'estacion', 'canal', 'detector', 'isotopo', 'nivel'),)


class OperatividadAppsSpida(models.Model):
    nombre_app = models.CharField(db_column='NOMBRE_APP', primary_key=True, max_length=200)  # Field name made lowercase.
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', blank=True, null=True)  # Field name made lowercase.
    minutos_actualizar = models.IntegerField(db_column='MINUTOS_ACTUALIZAR', blank=True, null=True)  # Field name made lowercase.
    ciclos_sin_datos = models.IntegerField(db_column='CICLOS_SIN_DATOS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'operatividad_apps_spida'


class ParamControl(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estaciones_id = models.IntegerField(db_column='ESTACIONES_ID')  # Field name made lowercase.
    canales = models.ForeignKey(Canales, models.DO_NOTHING, db_column='CANALES_ID')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'param_control'
        unique_together = (('fecha_hora', 'estaciones_id', 'canales'),)


class RadwinRvra(models.Model):
    ruta = models.CharField(db_column='RUTA', max_length=10, blank=True, null=True)  # Field name made lowercase.
    radwin = models.CharField(db_column='RADWIN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='CODIGO', max_length=10, blank=True, null=True)  # Field name made lowercase.
    d_ip = models.CharField(db_column='D_IP', primary_key=True, max_length=15)  # Field name made lowercase.
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', blank=True, null=True)  # Field name made lowercase.
    estado = models.IntegerField(db_column='ESTADO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'radwin_rvra'


class Relacion(models.Model):
    estac = models.IntegerField(db_column='ESTAC', primary_key=True)  # Field name made lowercase.
    canal = models.IntegerField(db_column='CANAL')  # Field name made lowercase.
    monitorizar = models.FloatField(db_column='MONITORIZAR')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion'
        unique_together = (('estac', 'canal'),)


class RelacionCanalesEstacion(models.Model):
    id_estacion = models.IntegerField(db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.IntegerField(db_column='ID_CANAL')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_canales_estacion'
        unique_together = (('id_estacion', 'id_canal'),)


class RelacionConexionesEstaciones(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_conexion = models.ForeignKey('TipoConexion', models.DO_NOTHING, db_column='ID_CONEXION')  # Field name made lowercase.
    limite_tiempo = models.IntegerField(db_column='LIMITE_TIEMPO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_conexiones_estaciones'
        unique_together = (('id_estacion', 'id_conexion'),)


class RelacionDetectoresEstacion(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_estacion = models.IntegerField(db_column='ID_ESTACION')  # Field name made lowercase.
    id_detector = models.IntegerField(db_column='ID_DETECTOR')  # Field name made lowercase.
    dir_datos = models.CharField(db_column='DIR_DATOS', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ref_id = models.CharField(db_column='REF_ID', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_detectores_estacion'


class RelacionDetectoresIsotopos(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    rel_det_est = models.ForeignKey(RelacionDetectoresEstacion, models.DO_NOTHING, db_column='REL_DET_EST_ID')  # Field name made lowercase.
    isototo = models.ForeignKey(Isotopos, models.DO_NOTHING, db_column='ISOTOTO_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_detectores_isotopos'


class RelacionEstacionAemet(models.Model):
    id_estacion = models.IntegerField(db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    idema = models.CharField(db_column='IDEMA', max_length=200)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_estacion_aemet'
        unique_together = (('id_estacion', 'idema'),)


class RelacionEstacionSaih(models.Model):
    estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ESTACION_ID', primary_key=True)  # Field name made lowercase.
    id_saih = models.CharField(db_column='ID_SAIH', max_length=200)  # Field name made lowercase.
    monitorizar = models.IntegerField(db_column='MONITORIZAR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_estacion_saih'
        unique_together = (('estacion', 'id_saih'),)


class RelacionEstacionesMeteo(models.Model):
    id_estacion_hidrologica = models.IntegerField(db_column='ID_ESTACION_HIDROLOGICA', primary_key=True)  # Field name made lowercase.
    id_estacion_pluviometrica = models.IntegerField(db_column='ID_ESTACION_PLUVIOMETRICA')  # Field name made lowercase.
    distancia_km = models.FloatField(db_column='DISTANCIA_KM')  # Field name made lowercase.
    w_thiessen_global = models.FloatField(db_column='W_THIESSEN_GLOBAL', blank=True, null=True)  # Field name made lowercase.
    w_thiessen_externo = models.FloatField(db_column='W_THIESSEN_EXTERNO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_estaciones_meteo'
        unique_together = (('id_estacion_hidrologica', 'id_estacion_pluviometrica'),)


class RelacionInformesDatosCorregidos(models.Model):
    id_informes = models.IntegerField(primary_key=True)
    id_datos_corregidos = models.IntegerField()
    id_mensaje = models.IntegerField()
    tipo_mensaje = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'relacion_informes_datos_corregidos'
        unique_together = (('id_informes', 'id_datos_corregidos'),)


class RelacionRoles(models.Model):
    rol_id = models.IntegerField(db_column='ROL_ID', primary_key=True)  # Field name made lowercase.
    tipo_rol = models.CharField(db_column='TIPO_ROL', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_roles'


class RelacionSubcuencasEstacionesCanales(models.Model):
    idsubcuenca = models.OneToOneField('Subcuencas', models.DO_NOTHING, db_column='idSubcuenca', primary_key=True)  # Field name made lowercase.
    idestacion = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='idEstacion')  # Field name made lowercase.
    idcanal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='idCanal')  # Field name made lowercase.
    limiteaviso = models.FloatField(db_column='limiteAviso', blank=True, null=True)  # Field name made lowercase.
    limitealarma = models.FloatField(db_column='limiteAlarma', blank=True, null=True)  # Field name made lowercase.
    limitemedio = models.FloatField(db_column='limiteMedio', blank=True, null=True)  # Field name made lowercase.
    observaciones = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'relacion_subcuencas_estaciones_canales'
        unique_together = (('idsubcuenca', 'idestacion', 'idcanal'),)


class RelacionSubcuencasZonameteoaemet(models.Model):
    id_subcuenca = models.OneToOneField('SubcuencasExtremadura', models.DO_NOTHING, db_column='ID_SUBCUENCA', primary_key=True)  # Field name made lowercase.
    id_zona_meteo_aemet = models.ForeignKey('ZonaMeteoalertaAemet', models.DO_NOTHING, db_column='ID_ZONA_METEO_AEMET')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_subcuencas_zonameteoaemet'
        unique_together = (('id_subcuenca', 'id_zona_meteo_aemet'),)


class RelacionVbResponsableCanal(models.Model):
    id_canal = models.IntegerField(primary_key=True)
    id_usuario_responsable = models.IntegerField()
    orden = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'relacion_vb_responsable_canal'
        unique_together = (('id_canal', 'id_usuario_responsable'),)


class ResultadosSimulacion(models.Model):
    id_simulacion = models.BigIntegerField(primary_key=True)
    id_canal = models.IntegerField()
    fecha_simulacion = models.DateTimeField()
    seccion = models.FloatField()
    valor = models.FloatField()
    unidades = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resultados_simulacion'
        unique_together = (('id_simulacion', 'id_canal', 'fecha_simulacion', 'seccion'),)


class Sesion(models.Model):
    fecha = models.DateTimeField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sesion'


class Simulaciones(models.Model):
    id_sim = models.BigAutoField(db_column='ID_SIM', primary_key=True)  # Field name made lowercase.
    usuario = models.CharField(db_column='USUARIO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fecha_solicitud = models.DateTimeField(db_column='FECHA_SOLICITUD', blank=True, null=True)  # Field name made lowercase.
    fecha_simulacion = models.DateTimeField(db_column='FECHA_SIMULACION', blank=True, null=True)  # Field name made lowercase.
    comentarios = models.CharField(db_column='COMENTARIOS', max_length=500, blank=True, null=True)  # Field name made lowercase.
    estado = models.IntegerField(db_column='ESTADO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'simulaciones'


class Subcuencas(models.Model):
    idsubcuenca = models.IntegerField(db_column='idSubcuenca', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'subcuencas'


class SubcuencasExtremadura(models.Model):
    id_subcuenca = models.IntegerField(db_column='ID_SUBCUENCA', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=200)  # Field name made lowercase.
    saih = models.CharField(db_column='SAIH', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'subcuencas_extremadura'


class TablaStatusUsuarios(models.Model):
    id_usuario = models.IntegerField(db_column='ID_USUARIO', primary_key=True)  # Field name made lowercase.
    status = models.IntegerField(db_column='STATUS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tabla_status_usuarios'


class TipoConexion(models.Model):
    id_conex = models.IntegerField(db_column='ID_CONEX', primary_key=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_conexion'


class TipoEstacionesSpida(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_estaciones_spida'


class TipoMensaje(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    tipo_mensaje = models.CharField(db_column='TIPO_MENSAJE', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_mensaje'


class UltimasImagenesSpida(models.Model):
    id_estacion = models.IntegerField(db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_camara = models.IntegerField(db_column='ID_CAMARA')  # Field name made lowercase.
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA')  # Field name made lowercase.
    imagen = models.TextField(db_column='IMAGEN', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ultimas_imagenes_spida'
        unique_together = (('id_estacion', 'id_camara'),)


class UltimosValoresRecibidos(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA')  # Field name made lowercase.
    estacion_id = models.IntegerField(db_column='ESTACION_ID', primary_key=True)  # Field name made lowercase.
    can_det_est = models.IntegerField(db_column='CAN_DET_EST')  # Field name made lowercase.
    isotopo_id = models.IntegerField(db_column='ISOTOPO_ID')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.
    color = models.IntegerField(db_column='COLOR', blank=True, null=True)  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR', blank=True, null=True)  # Field name made lowercase.
    amd = models.FloatField(db_column='AMD', blank=True, null=True)  # Field name made lowercase.
    unidades = models.CharField(db_column='UNIDADES', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ultimos_valores_recibidos'
        unique_together = (('estacion_id', 'can_det_est', 'isotopo_id'),)


class UmbralesNivelRios(models.Model):
    id_estacion = models.IntegerField(db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    limiteaviso = models.FloatField(db_column='limiteAviso')  # Field name made lowercase.
    limitemedio = models.FloatField(db_column='limiteMedio')  # Field name made lowercase.
    limitealarma = models.FloatField(db_column='limiteAlarma')  # Field name made lowercase.
    id_arpsis = models.CharField(db_column='ID_ARPSIS', max_length=200, blank=True, null=True)  # Field name made lowercase.
    tramo_arpsis = models.CharField(db_column='TRAMO_ARPSIS', max_length=200, blank=True, null=True)  # Field name made lowercase.
    url_ficha_arpsis = models.CharField(db_column='URL_FICHA_ARPSIS', max_length=200, blank=True, null=True)  # Field name made lowercase.
    url_pdf_ficha_arpsis = models.CharField(db_column='URL_PDF_FICHA_ARPSIS', max_length=200, blank=True, null=True)  # Field name made lowercase.
    nivel_rio_t10 = models.FloatField(db_column='NIVEL_RIO_T10', blank=True, null=True)  # Field name made lowercase.
    nivel_rio_t100 = models.FloatField(db_column='NIVEL_RIO_T100', blank=True, null=True)  # Field name made lowercase.
    nivel_rio_t500 = models.FloatField(db_column='NIVEL_RIO_T500', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'umbrales_nivel_rios'


class UsuariosRvra(models.Model):
    usuario_id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=80, blank=True, null=True)
    apellidos = models.CharField(max_length=250, blank=True, null=True)
    dni = models.CharField(max_length=10, blank=True, null=True)
    clave = models.CharField(max_length=50)
    nivel = models.IntegerField()
    tfno_1 = models.CharField(max_length=20, blank=True, null=True)
    tfno_2 = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuarios_rvra'


class ValoresSimulacion(models.Model):
    id_simulacion = models.OneToOneField(Simulaciones, models.DO_NOTHING, db_column='id_simulacion', primary_key=True)
    id_canales = models.ForeignKey(Canales, models.DO_NOTHING, db_column='id_canales')
    valor = models.FloatField()
    unidades = models.CharField(max_length=20, blank=True, null=True)
    adicional = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'valores_simulacion'
        unique_together = (('id_simulacion', 'id_canales'),)


class ZonaMeteoalertaAemet(models.Model):
    id_zona_meteo_aemet = models.IntegerField(db_column='ID_ZONA_METEO_AEMET', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=255)  # Field name made lowercase.
    estado = models.CharField(db_column='ESTADO', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'zona_meteoalerta_aemet'
        unique_together = (('id_zona_meteo_aemet', 'nombre'),)
