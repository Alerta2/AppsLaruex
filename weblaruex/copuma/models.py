# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Analisis(models.Model):
    codanalisis = models.CharField(db_column='CodAnalisis', primary_key=True, max_length=2)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=45, blank=True, null=True)  # Field name made lowercase.
    unidades = models.CharField(db_column='Unidades', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Analisis'

class CalcularIsotopos(models.Model):
    analisis = models.CharField(db_column='ANALISIS', primary_key=True, max_length=255)  # Field name made lowercase.
    cod_isotopo = models.CharField(db_column='COD_ISOTOPO', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cod_analisis = models.CharField(db_column='COD_ANALISIS', max_length=255, blank=True, null=True)  # Field name made lowercase.
    masa = models.IntegerField(db_column='MASA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'calcular_isotopos'



class Instalacion(models.Model):
    codinstalacion = models.CharField(db_column='CodInstalacion', primary_key=True, max_length=3)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Instalacion'


class Isotopo(models.Model):
    codisotopo = models.CharField(db_column='CodIsotopo', primary_key=True, max_length=2)  # Field name made lowercase.
    analisis_codanalisis = models.CharField(db_column='Analisis_CodAnalisis', max_length=2)  # Field name made lowercase.
    masa = models.IntegerField(db_column='Masa')  # Field name made lowercase.
    metaestable = models.CharField(db_column='Metaestable', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Isotopo'
        unique_together = (('codisotopo', 'analisis_codanalisis', 'masa', 'metaestable'),)


class Laboratorio(models.Model):
    codlaboratorio = models.IntegerField(db_column='CodLaboratorio', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Laboratorio'

class Limites(models.Model):
    codmuestra = models.CharField(db_column='Muestra_CodMuestra', max_length=3)  # Field name made lowercase.
    codisotopo = models.CharField(db_column='Isotopo_CodIsotopo', max_length=10)  # Field name made lowercase.
    analisis_codanalisis = models.CharField(db_column='Isotopo_Analisis_CodAnalisis', max_length=2)  # Field name made lowercase.
    masa = models.IntegerField(db_column='Masa', primary_key=True)  # Field name made lowercase.
    limite_maximo = models.FloatField(db_column='Limite_Maximo', blank=True, null=True)  # Field name made lowercase.
    unidad = models.CharField(db_column='Unidad', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Limites_Maximos'
        unique_together = (('codmuestra', 'codisotopo', 'analisis_codanalisis'),)

class LimitesMaximos(models.Model):
    muestra_codmuestra = models.CharField(db_column='Muestra_CodMuestra', max_length=3)  # Field name made lowercase.
    isotopo_codisotopo = models.CharField(db_column='Isotopo_CodIsotopo', max_length=10)  # Field name made lowercase.
    isotopo_analisis_codanalisis = models.CharField(db_column='Isotopo_Analisis_CodAnalisis', primary_key=True, max_length=2)  # Field name made lowercase.
    masa = models.IntegerField(db_column='Masa')  # Field name made lowercase.
    limite_maximo = models.FloatField(db_column='Limite_Maximo', blank=True, null=True)  # Field name made lowercase.
    unidad = models.CharField(db_column='Unidad', max_length=45, blank=True, null=True)  # Field name made lowercase.
    medida = models.CharField(db_column='Medida', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Limites_Maximos'
        unique_together = (('isotopo_analisis_codanalisis', 'isotopo_codisotopo', 'muestra_codmuestra', 'masa'),)


class MotivoMuestreo(models.Model):
    codmuestreo = models.CharField(db_column='CodMuestreo', primary_key=True, max_length=1)  # Field name made lowercase.
    namemuestreo = models.CharField(db_column='NameMuestreo', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Motivo_Muestreo'

class Muestra(models.Model):
    codmuestra = models.CharField(db_column='CodMuestra', primary_key=True, max_length=3)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=45, blank=True, null=True)  # Field name made lowercase.
    unidades = models.CharField(db_column='Unidades', max_length=45, blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='Icono', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Muestra'


class Procedencia(models.Model):
    codprocedencia = models.IntegerField(db_column='CodProcedencia', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=45, blank=True, null=True)  # Field name made lowercase.
    map_lat = models.FloatField(db_column='MAP_LAT', blank=True, null=True)  # Field name made lowercase.
    map_lon = models.FloatField(db_column='MAP_LON', blank=True, null=True)  # Field name made lowercase.
    imagen = models.CharField(db_column='Imagen', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'procedencia'

class ProduccionAlmaraz(models.Model):
    fecha_consumo = models.DateField(db_column='Fecha_Consumo', primary_key=True)  # Field name made lowercase.
    modulo_1 = models.FloatField(db_column='Modulo_1', blank=True, null=True)  # Field name made lowercase.
    modulo_2 = models.FloatField(db_column='Modulo_2', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Produccion_Almaraz'


class LimitesDosis(models.Model):
    codprocedencia = models.IntegerField(db_column='CodProcedencia', primary_key=True)  # Field name made lowercase.
    dosismedia = models.FloatField(db_column='DosisMedia', blank=True, null=True)  # Field name made lowercase.
    dosismaxima = models.FloatField(db_column='DosisMaxima', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Limites_Dosis'


class ValorMuestra(models.Model):
    motivo_muestreo_codmuestreo = models.CharField(db_column='Motivo_Muestreo_CodMuestreo', primary_key=True, max_length=1)  # Field name made lowercase.
    fecha_recogida_inicial = models.DateField(db_column='Fecha_recogida_inicial')  # Field name made lowercase.
    fecha_recogida_final = models.DateField(db_column='Fecha_recogida_final')  # Field name made lowercase.
    fecha_analisis = models.DateField(db_column='Fecha_analisis')  # Field name made lowercase.
    instalacion_codinstalacion = models.CharField(db_column='Instalacion_CodInstalacion', max_length=3)  # Field name made lowercase.
    laboratorio_codlaboratorio = models.IntegerField(db_column='Laboratorio_CodLaboratorio')  # Field name made lowercase.
    muestra_codmuestra = models.CharField(db_column='Muestra_CodMuestra', max_length=3)  # Field name made lowercase.
    isotopo_codisotopo = models.CharField(db_column='Isotopo_CodIsotopo', max_length=2)  # Field name made lowercase.
    isotopo_analisis_codanalisis = models.CharField(db_column='Isotopo_Analisis_CodAnalisis', max_length=2)  # Field name made lowercase.
    estacion_codprocedencia = models.IntegerField(db_column='Estacion_CodProcedencia')  # Field name made lowercase.
    masa = models.IntegerField(db_column='Masa')  # Field name made lowercase.
    metaestable = models.CharField(db_column='Metaestable', max_length=1)  # Field name made lowercase.
    compartida = models.CharField(db_column='Compartida', max_length=1, blank=True, null=True)  # Field name made lowercase.
    actividad_medida = models.FloatField(db_column='Actividad_medida', blank=True, null=True)  # Field name made lowercase.
    error_actividad_medida = models.FloatField(db_column='Error_actividad_medida', blank=True, null=True)  # Field name made lowercase.
    lid_medida = models.FloatField(db_column='LID_medida', blank=True, null=True)  # Field name made lowercase.
    numero_muestras = models.IntegerField(db_column='Numero_muestras', blank=True, null=True)  # Field name made lowercase.
    tiempo_recuento = models.IntegerField(db_column='Tiempo_recuento', blank=True, null=True)  # Field name made lowercase.
    c_muestra_recogida = models.FloatField(db_column='C_Muestra_Recogida', blank=True, null=True)  # Field name made lowercase.
    c_muestra_analizada = models.FloatField(db_column='C_Muestra_Analizada', blank=True, null=True)  # Field name made lowercase.
    rendimiento_quimico = models.FloatField(db_column='Rendimiento_quimico', blank=True, null=True)  # Field name made lowercase.
    relac_ceni_pes_hum = models.FloatField(db_column='Relac_Ceni_/Pes_Hum', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    semana_recogida = models.IntegerField(db_column='Semana_Recogida', blank=True, null=True)  # Field name made lowercase.
    cod_laboratorio_prep = models.IntegerField(db_column='Cod_Laboratorio_Prep', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Valor_Muestra'
        unique_together = (('motivo_muestreo_codmuestreo', 'fecha_recogida_inicial', 'fecha_recogida_final', 'fecha_analisis', 'instalacion_codinstalacion', 'laboratorio_codlaboratorio', 'muestra_codmuestra', 'isotopo_codisotopo', 'isotopo_analisis_codanalisis', 'estacion_codprocedencia', 'masa', 'metaestable'),)


class ValorMuestraCopumaVolatil(models.Model):
    motivo_muestreo_codmuestreo = models.CharField(db_column='Motivo_Muestreo_CodMuestreo', max_length=1)  # Field name made lowercase.
    fecha_recogida_inicial = models.DateField(db_column='Fecha_recogida_inicial')  # Field name made lowercase.
    fecha_recogida_final = models.DateField(db_column='Fecha_recogida_final')  # Field name made lowercase.
    fecha_analisis = models.DateField(db_column='Fecha_analisis')  # Field name made lowercase.
    instalacion_codinstalacion = models.CharField(db_column='Instalacion_CodInstalacion', max_length=3)  # Field name made lowercase.
    laboratorio_codlaboratorio = models.IntegerField(db_column='Laboratorio_CodLaboratorio')  # Field name made lowercase.
    muestra_codmuestra = models.CharField(db_column='Muestra_CodMuestra', max_length=3)  # Field name made lowercase.
    isotopo_codisotopo = models.CharField(db_column='Isotopo_CodIsotopo', max_length=2)  # Field name made lowercase.
    isotopo_analisis_codanalisis = models.CharField(db_column='Isotopo_Analisis_CodAnalisis', max_length=2)  # Field name made lowercase.
    estacion_codprocedencia = models.IntegerField(db_column='Estacion_CodProcedencia')  # Field name made lowercase.
    masa = models.IntegerField(db_column='Masa')  # Field name made lowercase.
    metaestable = models.CharField(db_column='Metaestable', max_length=1)  # Field name made lowercase.
    compartida = models.CharField(db_column='Compartida', max_length=1, blank=True, null=True)  # Field name made lowercase.
    actividad_medida = models.FloatField(db_column='Actividad_medida', blank=True, null=True)  # Field name made lowercase.
    error_actividad_medida = models.FloatField(db_column='Error_actividad_medida', blank=True, null=True)  # Field name made lowercase.
    lid_medida = models.FloatField(db_column='LID_medida', blank=True, null=True)  # Field name made lowercase.
    numero_muestras = models.IntegerField(db_column='Numero_muestras', blank=True, null=True)  # Field name made lowercase.
    tiempo_recuento = models.IntegerField(db_column='Tiempo_recuento', blank=True, null=True)  # Field name made lowercase.
    c_muestra_recogida = models.FloatField(db_column='C_Muestra_Recogida', blank=True, null=True)  # Field name made lowercase.
    c_muestra_analizada = models.FloatField(db_column='C_Muestra_Analizada', blank=True, null=True)  # Field name made lowercase.
    rendimiento_quimico = models.FloatField(db_column='Rendimiento_quimico', blank=True, null=True)  # Field name made lowercase.
    relac_ceni_pes_hum = models.FloatField(db_column='Relac_Ceni_/Pes_Hum', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    semana_recogida = models.IntegerField(db_column='Semana_Recogida', blank=True, null=True)  # Field name made lowercase.
    cod_laboratorio_prep = models.IntegerField(db_column='Cod_Laboratorio_Prep', blank=True, null=True)  # Field name made lowercase.
    fecha_subida_fichero = models.CharField(db_column='Fecha_subida_fichero', max_length=45, blank=True, null=True)  # Field name made lowercase.
    verificado = models.IntegerField(db_column='Verificado')  # Field name made lowercase.
    csn = models.IntegerField(db_column='CSN')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Valor_Muestra_Copuma_Volatil'
        unique_together = (('motivo_muestreo_codmuestreo', 'fecha_recogida_inicial', 'fecha_recogida_final', 'instalacion_codinstalacion', 'laboratorio_codlaboratorio', 'muestra_codmuestra', 'isotopo_codisotopo', 'isotopo_analisis_codanalisis', 'masa', 'estacion_codprocedencia', 'csn'),)


class GestionMemoriaDocument(models.Model):
    filename = models.CharField(max_length=100)
    docfile = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'gestion_memoria_document'


class GestionMemoriaDocumentcopuma(models.Model):
    filename = models.CharField(max_length=100)
    docfile = models.FileField(upload_to='documents/copuma')
    fecha_subida = models.DateTimeField(blank=True, null=True)
