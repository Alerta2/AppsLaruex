# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthUser(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'

class StructureProfile(models.Model):
    image = models.CharField(max_length=100)
    user = models.OneToOneField(AuthUser, models.DO_NOTHING)
    telefono = models.CharField(unique=True, max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'structure_profile'

class Drone(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA')  # Field name made lowercase.
    cadena = models.CharField(db_column='CADENA', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'drone'
        unique_together = (('id', 'fecha_hora'),)

class HistoricoSucesosEstaciones(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estaciones_id = models.IntegerField(db_column='ESTACIONES_ID')  # Field name made lowercase.
    relacion_detectores_estaciones_id = models.IntegerField(db_column='RELACION_DETECTORES_ESTACIONES_ID')  # Field name made lowercase.
    fecha_hora_inicial = models.DateTimeField(db_column='FECHA_HORA_INICIAL')  # Field name made lowercase.
    fecha_hora_final = models.DateTimeField(db_column='FECHA_HORA_FINAL', blank=True, null=True)  # Field name made lowercase.
    motivo_id = models.IntegerField(db_column='MOTIVO_ID', blank=True, null=True)  # Field name made lowercase.
    observaciones = models.CharField(db_column='OBSERVACIONES', max_length=100, blank=True, null=True)  # Field name made lowercase.
    procesada = models.IntegerField(db_column='PROCESADA', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_cierre = models.DateTimeField(db_column='FECHA_HORA_CIERRE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'historico_sucesos_estaciones'
        unique_together = (('fecha_hora', 'estaciones_id', 'relacion_detectores_estaciones_id', 'fecha_hora_inicial'),)


class Motivos(models.Model):
    motivo_id = models.IntegerField(db_column='MOTIVO_ID', primary_key=True)  # Field name made lowercase.
    accion = models.CharField(db_column='ACCION', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'motivos'

class UMovil(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA')  # Field name made lowercase.
    cadena = models.CharField(db_column='CADENA', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'u_movil'
        unique_together = (('id', 'fecha_hora'),)

class Canales(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=45, blank=True, null=True)  # Field name made lowercase.
    unidades = models.CharField(db_column='UNIDADES', max_length=20, blank=True, null=True)  # Field name made lowercase.
    factor = models.FloatField(db_column='FACTOR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'canales'

class ConfigEstacionWebrarex(models.Model):
    id_estacion = models.IntegerField(db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_detector = models.IntegerField(db_column='ID_DETECTOR')  # Field name made lowercase.
    tipo_detector = models.CharField(db_column='TIPO_DETECTOR', max_length=30)  # Field name made lowercase.
    isotopo = models.IntegerField(db_column='ISOTOPO')  # Field name made lowercase.
    decimales = models.IntegerField(db_column='DECIMALES')  # Field name made lowercase.
    unidades = models.CharField(db_column='UNIDADES', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'config_estacion_webrarex'
        unique_together = (('id_estacion', 'id_detector', 'isotopo'),)

class ConfigGraficasRare(models.Model):
    id_boton = models.IntegerField()
    nombre_boton = models.CharField(max_length=90, blank=True, null=True)
    id_subseccion = models.IntegerField()
    nombre_subseccion = models.CharField(max_length=90, blank=True, null=True)
    id_estacion = models.IntegerField()
    detector = models.IntegerField(blank=True, null=True)
    series = models.CharField(max_length=200, blank=True, null=True)
    tamanio = models.IntegerField(blank=True, null=True)
    dias = models.IntegerField(blank=True, null=True)
    red = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'config_graficas_rare'


class ConfigSerieGrafica(models.Model):
    tipodato = models.CharField(db_column='tipoDato', max_length=30, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=30, blank=True, null=True)
    eje = models.CharField(max_length=30, blank=True, null=True)
    ejemain = models.IntegerField(blank=True, null=True)
    tabla = models.CharField(max_length=30, blank=True, null=True)
    canal = models.IntegerField(blank=True, null=True)
    textoeje = models.CharField(db_column='textoEje', max_length=30, blank=True, null=True)  # Field name made lowercase.
    color = models.CharField(max_length=30, blank=True, null=True)
    tipografica = models.CharField(db_column='tipoGrafica', max_length=30, blank=True, null=True)  # Field name made lowercase.
    redondeo = models.IntegerField(db_column='redondeo', blank=True, null=True)
    horasAviso = models.IntegerField(db_column='horasAviso', blank=True, null=True)
    horasAlerta = models.IntegerField(db_column='horasAlerta', blank=True, null=True)
    horasIncidencia = models.IntegerField(db_column='horasIncidencia', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'config_serie_grafica'


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


class DatosCorregidosGraficas(models.Model):
    usuario = models.CharField(max_length=90)
    fecha = models.DateTimeField()
    tabla = models.CharField(max_length=255)
    elemento = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'datos_corregidos_graficas'

class ConfigMonitoriza(models.Model):
    estacion = models.OneToOneField('Estaciones', models.DO_NOTHING, db_column='ESTACION_ID', primary_key=True)  # Field name made lowercase.
    can_det_est = models.IntegerField(db_column='CAN_DET_EST')  # Field name made lowercase.
    isotopo = models.ForeignKey('Isotopos', models.DO_NOTHING, db_column='ISOTOPO_ID')  # Field name made lowercase.
    csn = models.IntegerField(db_column='CSN', blank=True, null=True)  # Field name made lowercase.
    min_sd_csn = models.IntegerField(db_column='MIN_SD_CSN', blank=True, null=True)  # Field name made lowercase.
    csn_f_ult_valor = models.DateTimeField(db_column='CSN_F_ULT_VALOR', blank=True, null=True)  # Field name made lowercase.
    sd_activo = models.IntegerField(db_column='SD_ACTIVO', blank=True, null=True)  # Field name made lowercase.
    minutos_sd = models.IntegerField(db_column='MINUTOS_SD', blank=True, null=True)  # Field name made lowercase.
    f_ini_sin_datos = models.DateTimeField(db_column='F_INI_SIN_DATOS', blank=True, null=True)  # Field name made lowercase.
    sd_sms_env = models.IntegerField(db_column='SD_SMS_ENV', blank=True, null=True)  # Field name made lowercase.
    med_anio_ant = models.FloatField(db_column='MED_ANIO_ANT', blank=True, null=True)  # Field name made lowercase.
    med_amd_anio_ant = models.FloatField(db_column='MED_AMD_ANIO_ANT', blank=True, null=True)  # Field name made lowercase.
    niveles_activo = models.IntegerField(db_column='NIVELES_ACTIVO', blank=True, null=True)  # Field name made lowercase.
    sms_enviado = models.IntegerField(db_column='SMS_ENVIADO', blank=True, null=True)  # Field name made lowercase.
    f_ini_nivel = models.DateTimeField(db_column='F_INI_NIVEL', blank=True, null=True)  # Field name made lowercase.
    factor_n1 = models.FloatField(db_column='FACTOR_N1', blank=True, null=True)  # Field name made lowercase.
    factor_n2 = models.FloatField(db_column='FACTOR_N2', blank=True, null=True)  # Field name made lowercase.
    factor_n3 = models.FloatField(db_column='FACTOR_N3', blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        managed = False
        db_table = 'config_monitoriza'
        unique_together = (('estacion', 'can_det_est', 'isotopo'),)

class ConfigMonitorizaCanales(models.Model):
    estacion = models.OneToOneField('Estaciones', models.DO_NOTHING, db_column='ESTACION_ID', primary_key=True)  # Field name made lowercase.
    can_det_est = models.ForeignKey('Canales', models.DO_NOTHING, db_column='CAN_DET_EST')  # Field name made lowercase.
    isotopo = models.ForeignKey('Isotopos', models.DO_NOTHING, db_column='ISOTOPO_ID')  # Field name made lowercase.
    csn = models.IntegerField(db_column='CSN', blank=True, null=True)  # Field name made lowercase.
    min_sd_csn = models.IntegerField(db_column='MIN_SD_CSN', blank=True, null=True)  # Field name made lowercase.
    csn_f_ult_valor = models.DateTimeField(db_column='CSN_F_ULT_VALOR', blank=True, null=True)  # Field name made lowercase.
    sd_activo = models.IntegerField(db_column='SD_ACTIVO', blank=True, null=True)  # Field name made lowercase.
    minutos_sd = models.IntegerField(db_column='MINUTOS_SD', blank=True, null=True)  # Field name made lowercase.
    f_ini_sin_datos = models.DateTimeField(db_column='F_INI_SIN_DATOS', blank=True, null=True)  # Field name made lowercase.
    sd_sms_env = models.IntegerField(db_column='SD_SMS_ENV', blank=True, null=True)  # Field name made lowercase.
    med_anio_ant = models.FloatField(db_column='MED_ANIO_ANT', blank=True, null=True)  # Field name made lowercase.
    med_amd_anio_ant = models.FloatField(db_column='MED_AMD_ANIO_ANT', blank=True, null=True)  # Field name made lowercase.
    niveles_activo = models.IntegerField(db_column='NIVELES_ACTIVO', blank=True, null=True)  # Field name made lowercase.
    sms_enviado = models.IntegerField(db_column='SMS_ENVIADO', blank=True, null=True)  # Field name made lowercase.
    f_ini_nivel = models.DateTimeField(db_column='F_INI_NIVEL', blank=True, null=True)  # Field name made lowercase.
    factor_n1 = models.FloatField(db_column='FACTOR_N1', blank=True, null=True)  # Field name made lowercase.
    factor_n2 = models.FloatField(db_column='FACTOR_N2', blank=True, null=True)  # Field name made lowercase.
    factor_n3 = models.FloatField(db_column='FACTOR_N3', blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        managed = False
        db_table = 'config_monitoriza'
        unique_together = (('estacion', 'can_det_est', 'isotopo'),)

class ConfigMonitorizaDetectores(models.Model):
    estacion = models.OneToOneField('Estaciones', models.DO_NOTHING, db_column='ESTACION_ID', primary_key=True)  # Field name made lowercase.
    can_det_est = models.ForeignKey('RelacionDetectoresEstacion', models.DO_NOTHING,db_column='CAN_DET_EST')  # Field name made lowercase.
    isotopo = models.ForeignKey('Isotopos', models.DO_NOTHING, db_column='ISOTOPO_ID')  # Field name made lowercase.
    csn = models.IntegerField(db_column='CSN', blank=True, null=True)  # Field name made lowercase.
    min_sd_csn = models.IntegerField(db_column='MIN_SD_CSN', blank=True, null=True)  # Field name made lowercase.
    csn_f_ult_valor = models.DateTimeField(db_column='CSN_F_ULT_VALOR', blank=True, null=True)  # Field name made lowercase.
    sd_activo = models.IntegerField(db_column='SD_ACTIVO', blank=True, null=True)  # Field name made lowercase.
    minutos_sd = models.IntegerField(db_column='MINUTOS_SD', blank=True, null=True)  # Field name made lowercase.
    f_ini_sin_datos = models.DateTimeField(db_column='F_INI_SIN_DATOS', blank=True, null=True)  # Field name made lowercase.
    sd_sms_env = models.IntegerField(db_column='SD_SMS_ENV', blank=True, null=True)  # Field name made lowercase.
    med_anio_ant = models.FloatField(db_column='MED_ANIO_ANT', blank=True, null=True)  # Field name made lowercase.
    med_amd_anio_ant = models.FloatField(db_column='MED_AMD_ANIO_ANT', blank=True, null=True)  # Field name made lowercase.
    niveles_activo = models.IntegerField(db_column='NIVELES_ACTIVO', blank=True, null=True)  # Field name made lowercase.
    sms_enviado = models.IntegerField(db_column='SMS_ENVIADO', blank=True, null=True)  # Field name made lowercase.
    f_ini_nivel = models.DateTimeField(db_column='F_INI_NIVEL', blank=True, null=True)  # Field name made lowercase.
    factor_n1 = models.FloatField(db_column='FACTOR_N1', blank=True, null=True)  # Field name made lowercase.
    factor_n2 = models.FloatField(db_column='FACTOR_N2', blank=True, null=True)  # Field name made lowercase.
    factor_n3 = models.FloatField(db_column='FACTOR_N3', blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        managed = False
        db_table = 'config_monitoriza'
        unique_together = (('estacion', 'can_det_est', 'isotopo'),)
        
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


class DispositivosMoviles(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_estacion = models.IntegerField(db_column='ID_ESTACION')  # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=20)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=20)  # Field name made lowercase.
    activo = models.IntegerField(db_column='ACTIVO', blank=True, null=True)  # Field name made lowercase.
    base_lat = models.FloatField(db_column='BASE_LAT', blank=True, null=True)  # Field name made lowercase.
    base_lon = models.FloatField(db_column='BASE_LON', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dispositivos_moviles'



class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Dosis(models.Model):
    id = models.BigAutoField(primary_key=True)
    idgeopos = models.ForeignKey('Geopos', models.DO_NOTHING, db_column='idgeopos', blank=True, null=True)
    valor = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dosis'


class Entregasestaciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_estacion = models.ForeignKey('Estaciones', models.DO_NOTHING, db_column='ID_ESTACION')  # Field name made lowercase.
    clave = models.CharField(db_column='CLAVE', max_length=200, blank=True, null=True)  # Field name made lowercase.
    red = models.CharField(db_column='RED', max_length=100, blank=True, null=True)  # Field name made lowercase.
    conexion = models.ForeignKey('TipoConexion', models.DO_NOTHING, db_column='CONEXION', blank=True, null=True)
    hashcalculado = models.CharField(db_column='HASHCALCULADO', max_length=300, blank=True, null=True)  # Field name made lowercase.
    hashrecibido = models.CharField(db_column='HASHRECIBIDO', max_length=300, blank=True, null=True)  # Field name made lowercase.
    tamaniofichero = models.IntegerField(db_column='TAMANIOFICHERO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'entregasestaciones'

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
    estaciones = models.IntegerField(db_column='ESTACIONES_ID')  # Field name made lowercase.
    canales = models.IntegerField(db_column='CANALES_ID')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'est_gam_y_radioyodos'
        unique_together = (('fecha_hora', 'estaciones', 'canales'),)

class EstGamYRadioyodosFK(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estaciones =  models.ForeignKey('Estaciones', models.DO_NOTHING, db_column='ESTACIONES_ID')  # Field name made lowercase.
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


class Estaciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=45, blank=True, null=True)  # Field name made lowercase.
    map_lat = models.FloatField(db_column='MAP_LAT', blank=True, null=True)  # Field name made lowercase.
    map_lon = models.FloatField(db_column='MAP_LON', blank=True, null=True)  # Field name made lowercase.
    dir_fotos = models.CharField(db_column='DIR_FOTOS', max_length=255, blank=True, null=True)  # Field name made lowercase.
    visualizar = models.IntegerField(db_column='VISUALIZAR', blank=True, null=True)  # Field name made lowercase.

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


class InformacionesEstaciones(models.Model):
    id_estacion = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    red = models.CharField(db_column='RED', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    ubicacion_riesgo = models.IntegerField(db_column='UBICACION_RIESGO', blank=True, null=True)  # Field name made lowercase.
    angulo_riesgo = models.IntegerField(db_column='ANGULO_RIESGO', blank=True, null=True)  # Field name made lowercase.
    angulo_riesgo_min = models.IntegerField(db_column='ANGULO_RIESGO_MIN', blank=True, null=True)  # Field name made lowercase.
    angulo_riesgo_max = models.IntegerField(db_column='ANGULO_RIESGO_MAX', blank=True, null=True)  # Field name made lowercase.
    distancia = models.IntegerField(db_column='DISTANCIA', blank=True, null=True)  # Field name made lowercase.
    tiempo_consulta = models.IntegerField(db_column='TIEMPO_CONSULTA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'informaciones_estaciones'


class InformacionVncExportar(models.Model):
    id_usuario = models.OneToOneField(AuthUser, models.DO_NOTHING, db_column='ID_USUARIO', primary_key=True)  # Field name made lowercase.
    pass_vnc_plana = models.CharField(db_column='PASS_VNC_PLANA', max_length=64, blank=True, null=True)  # Field name made lowercase.
    pass_vnc_exportar = models.CharField(db_column='PASS_VNC_EXPORTAR', max_length=64, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'informacion_vnc_exportar'
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


class MediasDiarias(models.Model):
    fecha = models.DateField(db_column='FECHA', primary_key=True)  # Field name made lowercase.
    id_estacion = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION')  # Field name made lowercase.
    id_detector = models.IntegerField(db_column='ID_DETECTOR')  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
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

class MedidasEstacionMovil(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_estacion = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION')  # Field name made lowercase.
    detector = models.CharField(db_column='DETECTOR', max_length=30)  # Field name made lowercase.
    fecha_medida = models.DateTimeField(db_column='FECHA_MEDIDA', blank=True, null=True)  # Field name made lowercase.
    tiempo_real = models.IntegerField(db_column='TIEMPO_REAL', blank=True, null=True)  # Field name made lowercase.
    tiempo_life = models.IntegerField(db_column='TIEMPO_LIFE', blank=True, null=True)  # Field name made lowercase.
    cuentas_totales = models.IntegerField(db_column='CUENTAS_TOTALES', blank=True, null=True)  # Field name made lowercase.
    cuentas = models.CharField(db_column='CUENTAS', max_length=9999, blank=True, null=True)  # Field name made lowercase.
    dosis = models.FloatField(db_column='DOSIS', blank=True, null=True)  # Field name made lowercase.
    lat = models.FloatField(db_column='LAT', blank=True, null=True)  # Field name made lowercase.
    lon = models.FloatField(db_column='LON', blank=True, null=True)  # Field name made lowercase.
    distancia = models.IntegerField(db_column='DISTANCIA', blank=True, null=True)  # Field name made lowercase.
    altura = models.IntegerField(db_column='ALTURA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'medidas_estacion_movil'


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
        unique_together = (('fecha_hora', 'enviado', 'mensaje'),)


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


class ParamControl(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estaciones = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='ESTACIONES_ID')  # Field name made lowercase.
    canales = models.ForeignKey(Canales, models.DO_NOTHING, db_column='CANALES_ID')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'param_control'
        unique_together = (('fecha_hora', 'estaciones', 'canales'),)


class ParamControlAVG(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estaciones = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='ESTACIONES_ID')  # Field name made lowercase.
    canales = models.ForeignKey(Canales, models.DO_NOTHING, db_column='CANALES_ID')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'param_control'


class PosicionamientoMedida(models.Model):
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', primary_key=True)  # Field name made lowercase.
    estaciones_id = models.IntegerField(db_column='ESTACIONES_ID')  # Field name made lowercase.
    latitud = models.FloatField(db_column='LATITUD', blank=True, null=True)  # Field name made lowercase.
    longitud = models.FloatField(db_column='LONGITUD', blank=True, null=True)  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'posicionamiento_medida'
        unique_together = (('fecha_hora', 'estaciones_id'),)


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

class RelacionIpOrdenadores(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    equipo = models.CharField(db_column='EQUIPO', max_length=120, blank=True, null=True)  # Field name made lowercase.
    ip = models.CharField(db_column='IP', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ip_intranet = models.CharField(db_column='IP_INTRANET', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ip_radwin = models.CharField(db_column='IP_RADWIN', max_length=20, blank=True, null=True)  # Field name made lowercase.
    usuario = models.CharField(db_column='USUARIO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    password = models.CharField(db_column='PASSWORD', max_length=20, blank=True, null=True)  # Field name made lowercase.
    puerto_vnc = models.CharField(db_column='PUERTO_VNC', max_length=10, blank=True, null=True)  # Field name made lowercase.
    usuario_vnc = models.CharField(db_column='USUARIO_VNC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    password_vnc = models.CharField(db_column='PASSWORD_VNC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    host = models.CharField(db_column='HOST', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comentario = models.CharField(db_column='COMENTARIO', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_ip_ordenadores'


class RelacionPersonalPcsRemoto(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_ordenador = models.ForeignKey(RelacionIpOrdenadores, models.DO_NOTHING, db_column='ID_ORDENADOR')  # Field name made lowercase.
    usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='USUARIO')  # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'relacion_personal_pcs_remoto'

class RelacionDetectoresIsotopos(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    rel_det_est = models.ForeignKey(RelacionDetectoresEstacion, models.DO_NOTHING, db_column='REL_DET_EST_ID')  # Field name made lowercase.
    isototo = models.ForeignKey(Isotopos, models.DO_NOTHING, db_column='ISOTOTO_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_detectores_isotopos'


class RelacionInformesDatosCorregidos(models.Model):
    id_informes = models.IntegerField(primary_key=True)
    id_datos_corregidos = models.IntegerField()
    id_mensaje = models.IntegerField()
    tipo_mensaje = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'relacion_informes_datos_corregidos'
        unique_together = (('id_informes', 'id_datos_corregidos'),)

class RelacionPermisoUsuarioEstacion(models.Model):
    id_usuario = models.IntegerField(primary_key=True)
    id_estacion = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'relacion_permiso_usuario_estacion'
        unique_together = (('id_usuario', 'id_estacion'),)

class RelacionRoles(models.Model):
    rol_id = models.IntegerField(db_column='ROL_ID', primary_key=True)  # Field name made lowercase.
    tipo_rol = models.CharField(db_column='TIPO_ROL', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_roles'


class RelacionVbResponsableCanal(models.Model):
    id_canal = models.IntegerField(primary_key=True)
    id_usuario_responsable = models.IntegerField()
    orden = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'relacion_vb_responsable_canal'
        unique_together = (('id_canal', 'id_usuario_responsable'),)

class RevisionGraficas(models.Model):
    usuario = models.CharField(max_length=90)
    fecha = models.DateTimeField()
    comentarios = models.CharField(max_length=40000)
    operatividad = models.CharField(max_length=300)
    niveles = models.CharField(max_length=300)
    integridad = models.CharField(max_length=300)
    grafica = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'revision_graficas'

class Sesion(models.Model):
    fecha = models.DateTimeField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sesion'

class SesionesMoviles(models.Model):
    id = models.IntegerField(primary_key=True, db_column="id")
    fecha_inicio = models.DateTimeField(blank=True, null=True, db_column="fecha_inicio")
    fecha_fin = models.DateTimeField(blank=True, null=True, db_column="fecha_fin")
    nombre_sesion = models.CharField(max_length=30, blank=True, null=True, db_column="nombre_sesion")
    descripcion = models.CharField(max_length=300, blank=True, null=True, db_column="descripcion")
    id_disp_movil = models.ForeignKey(DispositivosMoviles, models.DO_NOTHING, db_column='id_disp_movil')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sesiones_moviles'



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


class TipoMensaje(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    tipo_mensaje = models.CharField(db_column='TIPO_MENSAJE', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_mensaje'


class UbicacionesInteres(models.Model):
    id_ubicacion = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=120, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    tipo = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ubicaciones_interes'


class UsuariosMenmovil(models.Model):
    codigo = models.CharField(db_column='CODIGO', primary_key=True, max_length=2)  # Field name made lowercase.
    usuario = models.CharField(db_column='USUARIO', max_length=100)  # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=1)  # Field name made lowercase.
    spida = models.IntegerField(db_column='SPIDA')  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=12)  # Field name made lowercase.
    guardia = models.IntegerField(db_column='GUARDIA')  # Field name made lowercase.
    finde = models.IntegerField(db_column='FINDE')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuarios_menmovil'
        unique_together = (('codigo', 'usuario'),)


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


class PosicionesProyectosMedida(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    npos = models.IntegerField(db_column='N_POS')  # Field name made lowercase.
    proyecto = models.CharField(db_column='PROYECTO', max_length=60)  # Field name made lowercase.
    lat = models.CharField(db_column='LAT', max_length=60) # Field name made lowercase.
    lon = models.CharField(db_column='LON', max_length=60)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'posiciones_proyectos_medida'


class RelacionPosicionesMedidas(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_punto = models.IntegerField(db_column='ID_PUNTO')  # Field name made lowercase.
    analista = models.CharField(db_column='ANALISTA', max_length=30, blank=True, null=True)  # Field name made lowercase.
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA', blank=True, null=True)  # Field name made lowercase.
    dosis = models.CharField(db_column='DOSIS', max_length=60, blank=True, null=True)  # Field name made lowercase.
    cuentas = models.IntegerField(db_column='CUENTAS', blank=True, null=True)  # Field name made lowercase.
    tiempo_medida = models.IntegerField(db_column='TIEMPO_MEDIDA', blank=True, null=True)  # Field name made lowercase.
    tiempo_medida_unidad = models.CharField(db_column='UNIDAD_TIEMPO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    comentario = models.CharField(db_column='COMENTARIO', max_length=300, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_posiciones_medidas'


# ------------------------------
# MODELS GESLAB CHURROS
# ------------------------------


class ModelGeslabAlcance(models.Model):
    muestra = models.OneToOneField('ModelGeslabMuestras', models.DO_NOTHING, db_column='MUESTRA', primary_key=True)  # Field name made lowercase.
    analisis = models.ForeignKey('ModelGeslabAnalisis', models.DO_NOTHING, db_column='ANALISIS')  # Field name made lowercase.
    isotopo = models.ForeignKey('ModelGeslabIsotopos', models.DO_NOTHING, db_column='ISOTOPO')  # Field name made lowercase.
    alcance = models.FloatField(db_column='ALCANCE')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alcance'
        unique_together = (('muestra', 'analisis', 'isotopo'),)


class ModelGeslabAnalisis(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    churro = models.CharField(db_column='CHURRO', max_length=100)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'analisis'
        unique_together = (('id', 'churro'),)



class ModelGeslabIsotopos(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'isotopos'


class ModelGeslabIsotoposCopy(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.
    orden = models.IntegerField(db_column='ORDEN', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'isotopos_copy'


class ModelGeslabMemorias(models.Model):
    codigo_memoria = models.CharField(db_column='CODIGO_MEMORIA', primary_key=True, max_length=3)  # Field name made lowercase.
    memoria = models.CharField(db_column='MEMORIA', max_length=50)  # Field name made lowercase.
    base_datos_geslab = models.CharField(db_column='BASE_DATOS_GESLAB', max_length=50)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100)  # Field name made lowercase.
    longitud_linea = models.IntegerField(db_column='LONGITUD_LINEA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'memorias'


class ModelGeslabMuestras(models.Model):
    codigo = models.CharField(db_column='CODIGO', primary_key=True, max_length=3)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'muestras'


class ModelGeslabRelacionAnalisisIsotopos(models.Model):
    analisis = models.OneToOneField(ModelGeslabAnalisis, models.DO_NOTHING, db_column='ANALISIS_ID', primary_key=True)  # Field name made lowercase.
    isotopos = models.ForeignKey(ModelGeslabIsotopos, models.DO_NOTHING, db_column='ISOTOPOS_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_analisis_isotopos'
        unique_together = (('analisis', 'isotopos'),)

class ModelGeslabChurros(models.Model):
    memoria = models.OneToOneField('ModelGeslabMemorias', models.DO_NOTHING, db_column='MEMORIA_ID', primary_key=True)  # Field name made lowercase.
    muestra = models.ForeignKey('ModelGeslabMuestras', models.DO_NOTHING, db_column='MUESTRA')  # Field name made lowercase.
    analisis = models.ForeignKey(ModelGeslabAnalisis, models.DO_NOTHING, db_column='ANALISIS_ID')  # Field name made lowercase.
    isotopo = models.ForeignKey('ModelGeslabIsotopos', models.DO_NOTHING, db_column='ISOTOPO_ID')  # Field name made lowercase.
    f_rec_ini = models.DateField(db_column='F_REC_INI')  # Field name made lowercase.
    f_rec_fin = models.DateField(db_column='F_REC_FIN')  # Field name made lowercase.
    dias = models.IntegerField(db_column='DIAS')  # Field name made lowercase.
    f_analisis = models.DateField(db_column='F_ANALISIS')  # Field name made lowercase.
    muestra_compartida = models.CharField(db_column='MUESTRA_COMPARTIDA', max_length=1)  # Field name made lowercase.
    actividad = models.FloatField(db_column='ACTIVIDAD')  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR')  # Field name made lowercase.
    lid = models.FloatField(db_column='LID')  # Field name made lowercase.
    submuestras = models.IntegerField(db_column='SUBMUESTRAS')  # Field name made lowercase.
    tiempo_medida = models.IntegerField(db_column='TIEMPO_MEDIDA')  # Field name made lowercase.
    cantidad_muestra_recogida = models.FloatField(db_column='CANTIDAD_MUESTRA_RECOGIDA')  # Field name made lowercase.
    cantidad_muestra_analizada = models.FloatField(db_column='CANTIDAD_MUESTRA_ANALIZADA')  # Field name made lowercase.
    rendimiento = models.FloatField(db_column='RENDIMIENTO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'churros'
        unique_together = (('memoria', 'muestra', 'analisis', 'isotopo', 'f_rec_ini', 'f_rec_fin', 'f_analisis'),)


class MensajesTelegram(models.Model): 
    id_mensaje = models.AutoField(db_column='ID_MENSAJE', primary_key=True)  # Field name made lowercase. 
    id_area = models.IntegerField(db_column='ID_AREA', blank=True, null=True)  # Field name made lowercase. 
    id_estacion = models.IntegerField(db_column='ID_ESTACION', blank=True, null=True)  # Field name made lowercase. 
    id_canal = models.IntegerField(db_column='ID_CANAL', blank=True, null=True)  # Field name made lowercase. 
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase. 
    mensaje = models.CharField(db_column='MENSAJE', max_length=200)  # Field name made lowercase. 
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=2000, blank=True, null=True)  # Field name made lowercase. 
    icono = models.CharField(db_column='ICONO', max_length=100, blank=True, null=True)  # Field name made lowercase. 
    estado = models.IntegerField(db_column='ESTADO')  # Field name made lowercase. 
    id_telegram = models.CharField(db_column='ID_TELEGRAM', max_length=100)  # Field name made lowercase. 
    silenciar = models.IntegerField(db_column='SILENCIAR', blank=True, null=True)  # Field name made lowercase. 
    confirmar = models.IntegerField(db_column='CONFIRMAR', blank=True, null=True)  # Field name made lowercase. 
    tipo_mensaje_enviado = models.IntegerField(db_column='TIPO_MENSAJE_ENVIADO', blank=True, null=True)  # Field name made lowercase. 
    enviado = models.IntegerField(db_column='ENVIADO', blank=True, null=True)  # Field name made lowercase. 
 
    class Meta: 
        managed = False 
        db_table = 'mensajes_telegram'
        
class MensajesTelegramHistorico(models.Model):
    id_mensaje = models.IntegerField(db_column='ID_MENSAJE', primary_key=True)  # Field name made lowercase.
    id_area = models.IntegerField(db_column='ID_AREA', blank=True, null=True)  # Field name made lowercase.
    id_estacion = models.IntegerField(db_column='ID_ESTACION', blank=True, null=True)  # Field name made lowercase.
    id_canal = models.IntegerField(db_column='ID_CANAL', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase.
    mensaje = models.CharField(db_column='MENSAJE', max_length=200)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='ICONO', max_length=100, blank=True, null=True)  # Field name made lowercase.
    estado = models.IntegerField(db_column='ESTADO')  # Field name made lowercase.
    id_telegram = models.CharField(db_column='ID_TELEGRAM', max_length=100)  # Field name made lowercase.
    id_mensaje_telegram = models.IntegerField(db_column='ID_MENSAJE_TELEGRAM')  # Field name made lowercase.
    silenciar = models.IntegerField(db_column='SILENCIAR', blank=True, null=True)  # Field name made lowercase.
    confirmar = models.IntegerField(db_column='CONFIRMAR', blank=True, null=True)  # Field name made lowercase.
    tipo_mensaje_enviado = models.IntegerField(db_column='TIPO_MENSAJE_ENVIADO', blank=True, null=True)  # Field name made lowercase.
    enviado = models.IntegerField(db_column='ENVIADO', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_utc_envio = models.DateTimeField(db_column='FECHA_HORA_UTC_ENVIO', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_utc_confirmacion = models.DateTimeField(db_column='FECHA_HORA_UTC_CONFIRMACION', blank=True, null=True)  # Field name made lowercase.
    analista = models.IntegerField(db_column='ANALISTA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mensajes_telegram_historico'
        
class MensajesSms(models.Model):
    id_mensaje = models.AutoField(db_column='ID_MENSAJE', primary_key=True)  # Field name made lowercase.
    id_area = models.IntegerField(db_column='ID_AREA', blank=True, null=True)  # Field name made lowercase.
    id_estacion = models.IntegerField(db_column='ID_ESTACION', blank=True, null=True)  # Field name made lowercase.
    id_canal = models.IntegerField(db_column='ID_CANAL', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase.
    mensaje = models.CharField(db_column='MENSAJE', max_length=200)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=500, blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='ICONO', max_length=100, blank=True, null=True)  # Field name made lowercase.
    estado = models.IntegerField(db_column='ESTADO')  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=100)  # Field name made lowercase.
    confirmar = models.IntegerField(db_column='CONFIRMAR')  # Field name made lowercase.
    enviado = models.IntegerField(db_column='ENVIADO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mensajes_sms'

class ConfigSimulador(models.Model):
    estacion_id = models.IntegerField(db_column='ESTACION_ID', primary_key=True)  # Field name made lowercase.
    det_1 = models.IntegerField(db_column='DET_1', blank=True, null=True)  # Field name made lowercase.
    det_2 = models.IntegerField(db_column='DET_2', blank=True, null=True)  # Field name made lowercase.
    dosis = models.IntegerField(db_column='DOSIS')  # Field name made lowercase.
    cs134 = models.IntegerField(db_column='CS134', blank=True, null=True)  # Field name made lowercase.
    cs1342 = models.IntegerField(db_column='CS1342', blank=True, null=True)  # Field name made lowercase.
    cs137 = models.IntegerField(db_column='CS137', blank=True, null=True)  # Field name made lowercase.
    cs1372 = models.IntegerField(db_column='CS1372', blank=True, null=True)  # Field name made lowercase.
    co = models.IntegerField(db_column='CO', blank=True, null=True)  # Field name made lowercase.
    co2 = models.IntegerField(db_column='CO2', blank=True, null=True)  # Field name made lowercase.
    yodo = models.IntegerField(db_column='YODO', blank=True, null=True)  # Field name made lowercase.
    yodo2 = models.IntegerField(db_column='YODO2', blank=True, null=True)  # Field name made lowercase.
    flow = models.IntegerField(db_column='FLOW', blank=True, null=True)  # Field name made lowercase.
    lluvia = models.IntegerField(db_column='LLUVIA', blank=True, null=True)  # Field name made lowercase.
    temperatura = models.IntegerField(db_column='TEMPERATURA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'config_simulador'



class SimulacrosRarex(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fecha = models.CharField(db_column='FECHA', max_length=50)  # Field name made lowercase.
    estacion = models.ForeignKey('Estaciones', models.DO_NOTHING, db_column='ESTACION')  # Field name made lowercase.
    estado = models.IntegerField(db_column='ESTADO', blank=True, null=True)  # Field name made lowercase.
    inicio_nivel1 = models.DateTimeField(db_column='INICIO_NIVEL1', blank=True, null=True)  # Field name made lowercase.
    minutos_nivel1 = models.IntegerField(db_column='MINUTOS_NIVEL1', blank=True, null=True)  # Field name made lowercase.
    inicio_nivel2 = models.DateTimeField(db_column='INICIO_NIVEL2', blank=True, null=True)  # Field name made lowercase.
    minutos_nivel2 = models.IntegerField(db_column='MINUTOS_NIVEL2', blank=True, null=True)  # Field name made lowercase.
    inicio_nivel3 = models.DateTimeField(db_column='INICIO_NIVEL3', blank=True, null=True)  # Field name made lowercase.
    minutos_nivel3 = models.IntegerField(db_column='MINUTOS_NIVEL3', blank=True, null=True)  # Field name made lowercase.
    exitoso = models.IntegerField(db_column='EXITOSO', blank=True, null=True)  # Field name made lowercase.
    analista_guardia = models.IntegerField(db_column='ANALISTA_GUARDIA', blank=True, null=True)  # Field name made lowercase.
    analista_confirmacion = models.IntegerField(db_column='ANALISTA_CONFIRMACION', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'simulacros_rarex'
        

# TABLAS CALENDARIO


class CalendarioAreas(models.Model):
    id_area = models.AutoField(db_column='ID_AREA', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    icono = models.CharField(db_column='ICONO', max_length=100)  # Field name made lowercase.
    color = models.CharField(db_column='COLOR', max_length=7)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=200, blank=True, null=True)  # Field name made lowercase.
    html_calendar = models.CharField(db_column='HTML_CALENDAR', max_length=100)  # Field name made lowercase.
    js_calendar = models.CharField(db_column='JS_CALENDAR', max_length=100)  # Field name made lowercase.
    css_calendar = models.CharField(db_column='CSS_CALENDAR', max_length=100)  # Field name made lowercase.
    js_refresh_calendar = models.CharField(db_column='JS_REFRESH_CALENDAR', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'calendario_areas'


class CalendarioCambiosGuardias(models.Model):
    id_cambio = models.AutoField(db_column='ID_CAMBIO', primary_key=True)  # Field name made lowercase.
    year_sem_guardia_emisor = models.IntegerField(db_column='YEAR_SEM_GUARDIA_EMISOR')  # Field name made lowercase.
    sem_guardia_emisor = models.IntegerField(db_column='SEM_GUARDIA_EMISOR')  # Field name made lowercase.
    id_user_emisor = models.IntegerField(db_column='ID_USER_EMISOR')  # Field name made lowercase.
    year_sem_guardia_receptor = models.IntegerField(db_column='YEAR_SEM_GUARDIA_RECEPTOR')  # Field name made lowercase.
    sem_guardia_receptor = models.IntegerField(db_column='SEM_GUARDIA_RECEPTOR')  # Field name made lowercase.
    id_user_receptor = models.IntegerField(db_column='ID_USER_RECEPTOR')  # Field name made lowercase.
    id_turno = models.ForeignKey('CalendarioTurnos', models.DO_NOTHING, db_column='ID_TURNO')  # Field name made lowercase.
    supervisado = models.IntegerField(db_column='SUPERVISADO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'calendario_cambios_guardias'


class CalendarioFestivos(models.Model):
    fecha_local = models.DateField(db_column='FECHA_LOCAL', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'calendario_festivos'


class CalendarioGuardiasGuardias(models.Model):
    id_guardia = models.AutoField(db_column='ID_GUARDIA', primary_key=True)  # Field name made lowercase.
    year = models.IntegerField(db_column='YEAR')  # Field name made lowercase.
    semana = models.IntegerField(db_column='SEMANA')  # Field name made lowercase.
    id_user_analista = models.IntegerField(db_column='ID_USER_ANALISTA')  # Field name made lowercase.
    id_turno = models.ForeignKey('CalendarioTurnos', models.DO_NOTHING, db_column='ID_TURNO')  # Field name made lowercase.
    fecha_local_start = models.DateField(db_column='FECHA_LOCAL_START')  # Field name made lowercase.
    fecha_local_end = models.DateField(db_column='FECHA_LOCAL_END')  # Field name made lowercase.
    tipo_semana = models.IntegerField(db_column='TIPO_SEMANA')  # Field name made lowercase.
    id_user_modificado = models.IntegerField(db_column='ID_USER_MODIFICADO')  # Field name made lowercase.
    tipo_guardia = models.IntegerField(db_column='TIPO_GUARDIA')  # Field name made lowercase.
    supervisado = models.IntegerField(db_column='SUPERVISADO')  # Field name made lowercase.
    valido = models.IntegerField(db_column='VALIDO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'calendario_guardias_guardias'


class CalendarioPersonal(models.Model):
    id_usuario = models.IntegerField(db_column='ID_USUARIO', primary_key=True)  # Field name made lowercase.
    id_area = models.ForeignKey(CalendarioAreas, models.DO_NOTHING, db_column='ID_AREA')  # Field name made lowercase.
    operativo = models.IntegerField(db_column='OPERATIVO')  # Field name made lowercase.
    supervisor = models.IntegerField(db_column='SUPERVISOR')  # Field name made lowercase.
    superinformado = models.IntegerField(db_column='SUPERINFORMADO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'calendario_personal'
        unique_together = (('id_usuario', 'id_area'),)


class CalendarioTurnos(models.Model):
    id_turno = models.AutoField(db_column='ID_TURNO', primary_key=True)  # Field name made lowercase.
    id_area = models.ForeignKey(CalendarioAreas, models.DO_NOTHING, db_column='ID_AREA')  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100)  # Field name made lowercase.
    color_fondo = models.CharField(db_column='COLOR_FONDO', max_length=7)  # Field name made lowercase.
    color_texto = models.CharField(db_column='COLOR_TEXTO', max_length=7)  # Field name made lowercase.
    hora_local_comienzo = models.TimeField(db_column='HORA_LOCAL_COMIENZO')  # Field name made lowercase.
    hora_local_fin = models.TimeField(db_column='HORA_LOCAL_FIN')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'calendario_turnos'

class MensajesIconos(models.Model):
    id_icono = models.AutoField(db_column='ID_ICONO', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=200)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=200, blank=True, null=True)  # Field name made lowercase.
    unicode = models.CharField(db_column='UNICODE', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'mensajes_iconos'


class UMovil(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fecha_hora = models.DateTimeField(db_column='FECHA_HORA')  # Field name made lowercase.
    cadena = models.CharField(db_column='CADENA', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'u_movil'
        unique_together = (('id', 'fecha_hora'),)
