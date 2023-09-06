# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Alcance(models.Model):
    muestra = models.OneToOneField('MuestrasChurros', models.DO_NOTHING, db_column='MUESTRA', primary_key=True)  # Field name made lowercase.
    analisis = models.ForeignKey('AnalisisChurros', models.DO_NOTHING, db_column='ANALISIS')  # Field name made lowercase.
    isotopo = models.ForeignKey('IsotoposChurros', models.DO_NOTHING, db_column='ISOTOPO')  # Field name made lowercase.
    alcance = models.FloatField(db_column='ALCANCE')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alcance'
        unique_together = (('muestra', 'analisis', 'isotopo'),)


class AnalisisChurros(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    churro = models.CharField(db_column='CHURRO', max_length=100)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'analisis'
        unique_together = (('id', 'churro'),)


class Churros(models.Model):
    memoria = models.OneToOneField('MemoriasChurros', models.DO_NOTHING, db_column='MEMORIA_ID', primary_key=True)  # Field name made lowercase.
    muestra = models.ForeignKey('MuestrasChurros', models.DO_NOTHING, db_column='MUESTRA')  # Field name made lowercase.
    analisis = models.ForeignKey(AnalisisChurros, models.DO_NOTHING, db_column='ANALISIS_ID')  # Field name made lowercase.
    isotopo = models.ForeignKey('IsotoposChurros', models.DO_NOTHING, db_column='ISOTOPO_ID')  # Field name made lowercase.
    f_rec_ini = models.DateField(db_column='F_REC_INI')  # Field name made lowercase.
    f_rec_fin = models.DateField(db_column='F_REC_FIN')  # Field name made lowercase.
    dias = models.IntegerField(db_column='DIAS')  # Field name made lowercase.
    f_analisis = models.DateField(db_column='F_ANALISIS')  # Field name made lowercase.
    muestra_compartida = models.CharField(db_column='MUESTRA_COMPARTIDA', max_length=1)  # Field name made lowercase.
    actividad = models.FloatField(db_column='ACTIVIDAD', blank=True, null=True)  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR', blank=True, null=True)  # Field name made lowercase.
    lid = models.FloatField(db_column='LID')  # Field name made lowercase.
    submuestras = models.IntegerField(db_column='SUBMUESTRAS')  # Field name made lowercase.
    tiempo_medida = models.IntegerField(db_column='TIEMPO_MEDIDA', blank=True, null=True)  # Field name made lowercase.
    cantidad_muestra_recogida = models.FloatField(db_column='CANTIDAD_MUESTRA_RECOGIDA', blank=True, null=True)  # Field name made lowercase.
    cantidad_muestra_analizada = models.FloatField(db_column='CANTIDAD_MUESTRA_ANALIZADA', blank=True, null=True)  # Field name made lowercase.
    rendimiento = models.FloatField(db_column='RENDIMIENTO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'churros'
        unique_together = (('memoria', 'muestra', 'analisis', 'isotopo', 'f_rec_ini', 'f_rec_fin', 'f_analisis'),)


class IsotoposChurros(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'isotopos'


class IsotoposCopy(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.
    orden = models.IntegerField(db_column='ORDEN', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'isotopos_copy'


class MemoriasChurros(models.Model):
    codigo_memoria = models.CharField(db_column='CODIGO_MEMORIA', primary_key=True, max_length=3)  # Field name made lowercase.
    memoria = models.CharField(db_column='MEMORIA', max_length=50)  # Field name made lowercase.
    base_datos_geslab = models.CharField(db_column='BASE_DATOS_GESLAB', max_length=50)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100)  # Field name made lowercase.
    longitud_linea = models.IntegerField(db_column='LONGITUD_LINEA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'memorias'


class MuestrasChurros(models.Model):
    codigo = models.CharField(db_column='CODIGO', primary_key=True, max_length=3)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'muestras'


class RelacionAnalisisIsotopos(models.Model):
    analisis = models.OneToOneField(AnalisisChurros, models.DO_NOTHING, db_column='ANALISIS_ID', primary_key=True)  # Field name made lowercase.
    isotopos = models.ForeignKey(IsotoposChurros, models.DO_NOTHING, db_column='ISOTOPOS_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_analisis_isotopos'
        unique_together = (('analisis', 'isotopos'),)
