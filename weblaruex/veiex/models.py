# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Canales(models.Model):
    id_canal = models.IntegerField(db_column='ID_CANAL', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100, blank=True, null=True)  # Field name made lowercase.
    acronimo = models.CharField(db_column='ACRONIMO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    unidades = models.CharField(db_column='UNIDADES', max_length=50, blank=True, null=True)  # Field name made lowercase.
    contaminante = models.IntegerField(db_column='CONTAMINANTE', blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'canales'


class CanalesCopia(models.Model):
    id_canal = models.IntegerField(db_column='ID_CANAL', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100, blank=True, null=True)  # Field name made lowercase.
    unidades = models.CharField(db_column='UNIDADES', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'canales_copia'


class Directorios(models.Model):
    id_estacion = models.OneToOneField('Estaciones', models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    directorio_ftp = models.CharField(db_column='DIRECTORIO_FTP', max_length=500)  # Field name made lowercase.
    cabecera = models.CharField(db_column='CABECERA', max_length=500)  # Field name made lowercase.
    linea = models.IntegerField(db_column='LINEA')  # Field name made lowercase.
    tipo_fichero = models.CharField(db_column='TIPO_FICHERO', max_length=11)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'directorios'


class Estaciones(models.Model):
    id_estacion = models.IntegerField(db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    foco = models.CharField(db_column='FOCO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    estacion_lat = models.FloatField(db_column='ESTACION_LAT', blank=True, null=True)  # Field name made lowercase.
    estacion_lon = models.FloatField(db_column='ESTACION_LON', blank=True, null=True)  # Field name made lowercase.
    monitorizar = models.IntegerField(db_column='MONITORIZAR')  # Field name made lowercase.
    visualizar = models.IntegerField(db_column='VISUALIZAR')  # Field name made lowercase.
    denominacion = models.CharField(db_column='DENOMINACION', max_length=100, blank=True, null=True)  # Field name made lowercase.
    proceso_asociado = models.CharField(db_column='PROCESO_ASOCIADO', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'estaciones'


class Flags(models.Model):
    codificacion = models.CharField(db_column='CODIFICACION', primary_key=True, max_length=1)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=200)  # Field name made lowercase.
    color = models.CharField(db_column='COLOR', max_length=50, blank=True, null=True)  # Field name made lowercase.
    validacion = models.IntegerField(db_column='VALIDACION')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'flags'


class Focos(models.Model):
    id_foco = models.AutoField(db_column='ID_FOCO', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    monitorizar = models.IntegerField(db_column='MONITORIZAR')  # Field name made lowercase.
    visualizar = models.IntegerField(db_column='VISUALIZAR')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'focos'


class IndicesCalidadAire(models.Model):
    nombre = models.CharField(db_column='NOMBRE', primary_key=True, max_length=50)  # Field name made lowercase.
    minimo = models.IntegerField(db_column='MINIMO', blank=True, null=True)  # Field name made lowercase.
    maximo = models.IntegerField(db_column='MAXIMO', blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=200)  # Field name made lowercase.
    instruccion = models.CharField(db_column='INSTRUCCION', max_length=500, blank=True, null=True)  # Field name made lowercase.
    color = models.CharField(db_column='COLOR', max_length=50)  # Field name made lowercase.
    icono = models.CharField(db_column='ICONO', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'indices_calidad_aire'

class PromediosVeiex(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    contaminante = models.FloatField(db_column='CONTAMINANTE')  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR')  # Field name made lowercase.
    porcentaje = models.FloatField(db_column='PORCENTAJE')  # Field name made lowercase.
    #codificacion = models.CharField(db_column='CODIFICACION', max_length=11, blank=True, null=True)  # Field name made lowercase.
    codificacion = models.ForeignKey(Flags, models.DO_NOTHING, db_column='CODIFICACION')
    valido = models.IntegerField(db_column='VALIDO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'promedios_veiex'
        unique_together = (('id_estacion', 'id_canal', 'contaminante', 'fecha_hora_local'),)


class UltimosValores(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR')  # Field name made lowercase.
    #codificacion = models.CharField(db_column='CODIFICACION', max_length=1, blank=True, null=True)  # Field name made lowercase.
    codificacion = models.ForeignKey(Flags, models.DO_NOTHING, db_column='CODIFICACION')
    valido = models.IntegerField(db_column='VALIDO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ultimos_valores'
        unique_together = (('id_estacion', 'id_canal'),)


class UmbralesVle(models.Model):
    id_estacion = models.OneToOneField(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    vle = models.FloatField(db_column='VLE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'umbrales_vle'
        unique_together = (('id_estacion', 'id_canal'),)


class ValoresVeiex(models.Model):
    id_estacion = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='ID_ESTACION', primary_key=True)  # Field name made lowercase.
    id_canal = models.ForeignKey(Canales, models.DO_NOTHING, db_column='ID_CANAL')  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase.
    fecha_hora_local = models.DateTimeField(db_column='FECHA_HORA_LOCAL')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR')  # Field name made lowercase.
    #codificacion = models.CharField(db_column='CODIFICACION', max_length=11, blank=True, null=True)  # Field name made lowercase.
    codificacion = models.ForeignKey(Flags, models.DO_NOTHING, db_column='CODIFICACION')
    valido = models.IntegerField(db_column='VALIDO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'valores_veiex'
        unique_together = (('id_estacion', 'id_canal', 'fecha_hora_utc', 'fecha_hora_local'),)
