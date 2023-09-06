# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AlmacenEmailInforme(models.Model):
    muestra = models.IntegerField(db_column='MUESTRA', primary_key=True)  # Field name made lowercase.
    informe = models.IntegerField(db_column='INFORME')  # Field name made lowercase.
    cliente = models.CharField(db_column='CLIENTE', max_length=255)  # Field name made lowercase.
    pdf = models.TextField(db_column='PDF', blank=True, null=True)  # Field name made lowercase.
    informado = models.IntegerField(db_column='INFORMADO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'almacen_email_informe'
        unique_together = (('muestra', 'informe'),)


class AlmacenEmailRecepcion(models.Model):
    muestra = models.IntegerField(db_column='MUESTRA', primary_key=True)  # Field name made lowercase.
    informe = models.IntegerField(db_column='INFORME')  # Field name made lowercase.
    procedencia = models.CharField(db_column='PROCEDENCIA', max_length=50)  # Field name made lowercase.
    cantidad = models.CharField(db_column='CANTIDAD', max_length=30)  # Field name made lowercase.
    analisis = models.CharField(db_column='ANALISIS', max_length=255)  # Field name made lowercase.
    memoria = models.CharField(db_column='MEMORIA', max_length=30)  # Field name made lowercase.
    cliente = models.CharField(db_column='CLIENTE', max_length=255)  # Field name made lowercase.
    recepcionador = models.CharField(db_column='RECEPCIONADOR', max_length=30)  # Field name made lowercase.
    fecha_recepcion = models.CharField(db_column='FECHA_RECEPCION', max_length=255)  # Field name made lowercase.
    fecha_recogida = models.CharField(db_column='FECHA_RECOGIDA', max_length=255)  # Field name made lowercase.
    referencia = models.CharField(db_column='REFERENCIA', max_length=255, blank=True, null=True)  # Field name made lowercase.
    observaciones = models.TextField(db_column='OBSERVACIONES', blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(db_column='ESTADO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    correccion = models.CharField(db_column='CORRECCION', max_length=1)  # Field name made lowercase.
    motivo = models.CharField(db_column='MOTIVO', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'almacen_email_recepcion'
        unique_together = (('muestra', 'informe', 'correccion'),)


class AnalisisMedido(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    analisis = models.CharField(db_column='ANALISIS', max_length=10, blank=True, null=True)  # Field name made lowercase.
    isotopo = models.CharField(db_column='ISOTOPO', max_length=10, blank=True, null=True)  # Field name made lowercase.
    masa = models.IntegerField(db_column='MASA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'analisis_medido'


class AnalisisTablas(models.Model):
    nombre = models.CharField(db_column='NOMBRE', primary_key=True, max_length=25)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'analisis_tablas'


class Analiticas(models.Model):
    analisis_id = models.IntegerField(db_column='ANALISIS_ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=50)  # Field name made lowercase.
    prefijo = models.CharField(db_column='PREFIJO', max_length=7)  # Field name made lowercase.
    observaciones = models.CharField(db_column='OBSERVACIONES', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'analiticas'


class Ausencias(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.DateField(db_column='DIA', blank=True, null=True)  # Field name made lowercase.
    id_user = models.IntegerField(db_column='ID_USER', blank=True, null=True)  # Field name made lowercase.
    motivo = models.CharField(db_column='MOTIVO', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ausencias'


class Balanzas(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='CODIGO', max_length=30)  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'balanzas'


class CalibracionQuantulus(models.Model):
    medida = models.CharField(db_column='MEDIDA', max_length=30)  # Field name made lowercase.
    quantulus = models.CharField(db_column='QUANTULUS', max_length=30)  # Field name made lowercase.
    valor1 = models.FloatField(db_column='VALOR1')  # Field name made lowercase.
    valor2 = models.FloatField(db_column='VALOR2')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'calibracion_quantulus'


class CantidadesAgregadasRadioDesecacion(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_alicuota = models.IntegerField(db_column='ID_ALICUOTA')  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='FECHA')  # Field name made lowercase.
    volumen = models.FloatField(db_column='VOLUMEN')  # Field name made lowercase.
    tecnico = models.CharField(db_column='TECNICO', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cantidades_agregadas_radio_desecacion'


class Clientes(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=255)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=300, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='DIRECCION', max_length=150, blank=True, null=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=15, blank=True, null=True)  # Field name made lowercase.
    fax = models.CharField(db_column='FAX', max_length=15, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    persona_contacto = models.CharField(db_column='PERSONA_CONTACTO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nif = models.CharField(db_column='NIF', max_length=15, blank=True, null=True)  # Field name made lowercase.
    idioma = models.CharField(db_column='IDIOMA', max_length=2, blank=True, null=True)  # Field name made lowercase.
    password = models.CharField(db_column='PASSWORD', max_length=300, blank=True, null=True)  # Field name made lowercase.
    informar = models.CharField(db_column='INFORMAR', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'clientes'


class CodMuestras(models.Model):
    mues_id = models.AutoField(db_column='MUES_ID', primary_key=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='CODIGO', max_length=3)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    tipo = models.IntegerField(db_column='TIPO')  # Field name made lowercase.
    etiquetas = models.IntegerField(db_column='ETIQUETAS')  # Field name made lowercase.
    nombre_pt = models.CharField(db_column='NOMBRE_PT', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cod_muestras'
        unique_together = (('mues_id', 'codigo'),)


class Conductivimetros(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='CODIGO', max_length=30)  # Field name made lowercase.
    error = models.IntegerField(db_column='ERROR')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'conductivimetros'


class DeterminacionElementosEstables(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'determinacion_elementos_estables'


class Determinaciones(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'determinaciones'


class DeterminacionesProgramadas(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    muestra_prog_id = models.IntegerField(db_column='MUESTRA_PROG_ID')  # Field name made lowercase.
    determinacion = models.IntegerField(db_column='DETERMINACION')  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'determinaciones_programadas'


class EstadoMuestras(models.Model):
    identificador_estado = models.IntegerField(db_column='IDENTIFICADOR_ESTADO', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'estado_muestras'


class FechasDeterminacionProgramada(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    dia_inicio = models.DateField(db_column='DIA_INICIO', blank=True, null=True)  # Field name made lowercase.
    dia_fin = models.DateField(db_column='DIA_FIN', blank=True, null=True)  # Field name made lowercase.
    dia_semana = models.CharField(db_column='DIA_SEMANA', max_length=30, blank=True, null=True)  # Field name made lowercase.
    meses = models.IntegerField(db_column='MESES', blank=True, null=True)  # Field name made lowercase.
    enero = models.IntegerField(db_column='ENERO', blank=True, null=True)  # Field name made lowercase.
    febrero = models.IntegerField(db_column='FEBRERO', blank=True, null=True)  # Field name made lowercase.
    marzo = models.IntegerField(db_column='MARZO', blank=True, null=True)  # Field name made lowercase.
    abril = models.IntegerField(db_column='ABRIL', blank=True, null=True)  # Field name made lowercase.
    mayo = models.IntegerField(db_column='MAYO', blank=True, null=True)  # Field name made lowercase.
    junio = models.IntegerField(db_column='JUNIO', blank=True, null=True)  # Field name made lowercase.
    julio = models.IntegerField(db_column='JULIO', blank=True, null=True)  # Field name made lowercase.
    agosto = models.IntegerField(db_column='AGOSTO', blank=True, null=True)  # Field name made lowercase.
    septiembre = models.IntegerField(db_column='SEPTIEMBRE', blank=True, null=True)  # Field name made lowercase.
    octubre = models.IntegerField(db_column='OCTUBRE', blank=True, null=True)  # Field name made lowercase.
    noviembre = models.IntegerField(db_column='NOVIEMBRE', blank=True, null=True)  # Field name made lowercase.
    diciembre = models.IntegerField(db_column='DICIEMBRE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'fechas_determinacion_programada'


class FrecuenciaRecogida(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'frecuencia_recogida'


class HistoricoAlicuotasControles(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    tipo_control = models.CharField(db_column='TIPO_CONTROL', max_length=10)  # Field name made lowercase.
    codigo = models.CharField(db_column='CODIGO', max_length=10)  # Field name made lowercase.
    id_alicuota = models.IntegerField(db_column='ID_ALICUOTA')  # Field name made lowercase.
    id_alicuota_generadora = models.IntegerField(db_column='ID_ALICUOTA_GENERADORA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'historico_alicuotas_controles'


class HistoricoRecogida(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    codigo_recogida = models.ForeignKey('RecogidaGeneral', models.DO_NOTHING, db_column='CODIGO_RECOGIDA')  # Field name made lowercase.
    codigo_barras = models.CharField(db_column='CODIGO_BARRAS', max_length=50, blank=True, null=True)  # Field name made lowercase.
    recepcionado_por = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='RECEPCIONADO_POR', blank=True, null=True)  # Field name made lowercase.
    cliente = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='CLIENTE', blank=True, null=True)  # Field name made lowercase.
    suministrador = models.ForeignKey('Suministradores', models.DO_NOTHING, db_column='SUMINISTRADOR')  # Field name made lowercase.
    fecha_hora_recogida = models.DateTimeField(db_column='FECHA_HORA_RECOGIDA')  # Field name made lowercase.
    fecha_hora_recogida_2 = models.DateTimeField(db_column='FECHA_HORA_RECOGIDA_2')  # Field name made lowercase.
    fecha_hora_recogida_ref = models.DateTimeField(db_column='FECHA_HORA_RECOGIDA_REF')  # Field name made lowercase.
    fecha_hora_recepcion = models.DateTimeField(db_column='FECHA_HORA_RECEPCION', blank=True, null=True)  # Field name made lowercase.
    estado_de_muestra = models.ForeignKey(EstadoMuestras, models.DO_NOTHING, db_column='ESTADO_DE_MUESTRA', blank=True, null=True)  # Field name made lowercase.
    referencia_cliente = models.CharField(db_column='REFERENCIA_CLIENTE', max_length=250, blank=True, null=True)  # Field name made lowercase.
    comentarios = models.TextField(db_column='COMENTARIOS', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_recepcion_prevista = models.DateTimeField(db_column='FECHA_HORA_RECEPCION_PREVISTA', blank=True, null=True)  # Field name made lowercase.
    programada = models.ForeignKey('MuestrasProgramadas', models.DO_NOTHING, db_column='PROGRAMADA', blank=True, null=True)  # Field name made lowercase.
    foto = models.CharField(db_column='FOTO', max_length=150, blank=True, null=True)  # Field name made lowercase.
    cod_antiguo = models.CharField(db_column='COD_ANTIGUO', max_length=60, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'historico_recogida'


class InfoPrograma(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    version = models.FloatField(db_column='VERSION')  # Field name made lowercase.
    cambios = models.CharField(db_column='CAMBIOS', max_length=5000, blank=True, null=True)  # Field name made lowercase.
    updater = models.CharField(db_column='UPDATER', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'info_programa'


class InformacionMemorias(models.Model):
    memoria = models.CharField(db_column='MEMORIA', primary_key=True, max_length=2)  # Field name made lowercase.
    codigo_csn = models.CharField(db_column='CODIGO_CSN', max_length=3)  # Field name made lowercase.
    analisis = models.CharField(db_column='ANALISIS', max_length=10)  # Field name made lowercase.
    nom_mues = models.CharField(db_column='NOM_MUES', max_length=50, blank=True, null=True)  # Field name made lowercase.
    unidad = models.CharField(db_column='UNIDAD', max_length=10, blank=True, null=True)  # Field name made lowercase.
    total = models.IntegerField(db_column='TOTAL', blank=True, null=True)  # Field name made lowercase.
    num_mues = models.IntegerField(db_column='NUM_MUES', blank=True, null=True)  # Field name made lowercase.
    procedencia = models.CharField(db_column='PROCEDENCIA', max_length=100)  # Field name made lowercase.
    fichero = models.CharField(db_column='FICHERO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    f_recogida = models.DateField(db_column='F_RECOGIDA')  # Field name made lowercase.
    comentario = models.CharField(db_column='COMENTARIO', max_length=100, blank=True, null=True)  # Field name made lowercase.
    f_fin = models.DateField(db_column='F_FIN', blank=True, null=True)  # Field name made lowercase.
    f_medida = models.DateField(db_column='F_MEDIDA', blank=True, null=True)  # Field name made lowercase.
    t_mues = models.IntegerField(db_column='T_MUES', blank=True, null=True)  # Field name made lowercase.
    deposito = models.FloatField(db_column='DEPOSITO', blank=True, null=True)  # Field name made lowercase.
    volumen = models.FloatField(db_column='VOLUMEN', blank=True, null=True)  # Field name made lowercase.
    ac_esp = models.FloatField(db_column='AC_ESP', blank=True, null=True)  # Field name made lowercase.
    error_ac = models.FloatField(db_column='ERROR_AC', blank=True, null=True)  # Field name made lowercase.
    ac_br_esp = models.FloatField(db_column='AC_BR_ESP', blank=True, null=True)  # Field name made lowercase.
    err_ac_br = models.FloatField(db_column='ERR_AC_BR', blank=True, null=True)  # Field name made lowercase.
    lid = models.FloatField(db_column='LID', blank=True, null=True)  # Field name made lowercase.
    rendimiento = models.FloatField(db_column='RENDIMIENTO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'informacion_memorias'
        unique_together = (('memoria', 'codigo_csn', 'analisis', 'procedencia', 'f_recogida'),)


class Isotopos(models.Model):
    identificador = models.IntegerField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    isotopo = models.CharField(db_column='ISOTOPO', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'isotopos'


class Laboratorios(models.Model):
    identificador = models.IntegerField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    laboratorio = models.CharField(db_column='LABORATORIO', max_length=50)  # Field name made lowercase.
    color = models.CharField(db_column='COLOR', max_length=30)  # Field name made lowercase.
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='ID_USUARIO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'laboratorios'


class MedidasPredefinidas(models.Model):
    paquetemedidas = models.CharField(db_column='paqueteMedidas', primary_key=True, max_length=30)  # Field name made lowercase.
    nombrepaquete = models.CharField(db_column='nombrePaquete', max_length=60, blank=True, null=True)  # Field name made lowercase.
    analisis = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'medidas_predefinidas'


class Memorias(models.Model):
    codigo_memoria = models.CharField(db_column='CODIGO_MEMORIA', primary_key=True, max_length=3)  # Field name made lowercase.
    memoria = models.CharField(db_column='MEMORIA', max_length=50)  # Field name made lowercase.
    base_datos_geslab = models.CharField(db_column='BASE_DATOS_GESLAB', max_length=50)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.
    ajuste_semana = models.IntegerField(db_column='AJUSTE_SEMANA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'memorias'
        unique_together = (('codigo_memoria', 'memoria'),)


class MuestraActualCodigo(models.Model):
    id_tratamiento = models.IntegerField(db_column='ID_TRATAMIENTO', primary_key=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='CODIGO', max_length=10)  # Field name made lowercase.
    posicion = models.IntegerField(db_column='POSICION')  # Field name made lowercase.
    duplicada = models.IntegerField(db_column='DUPLICADA')  # Field name made lowercase.
    duplicada_pos = models.IntegerField(db_column='DUPLICADA_POS')  # Field name made lowercase.
    control = models.IntegerField(db_column='CONTROL')  # Field name made lowercase.
    control_pos = models.IntegerField(db_column='CONTROL_POS')  # Field name made lowercase.
    blanco = models.IntegerField(db_column='BLANCO')  # Field name made lowercase.
    blanco_pos = models.IntegerField(db_column='BLANCO_POS')  # Field name made lowercase.
    tiempo_en_lab = models.IntegerField(db_column='TIEMPO_EN_LAB')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'muestra_actual_codigo'


class MuestrasProgramadas(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    memoria = models.CharField(db_column='MEMORIA', max_length=3)  # Field name made lowercase.
    cod_csn = models.IntegerField(db_column='COD_CSN', blank=True, null=True)  # Field name made lowercase.
    procedencia = models.IntegerField(db_column='PROCEDENCIA')  # Field name made lowercase.
    frecuencia = models.IntegerField(db_column='FRECUENCIA')  # Field name made lowercase.
    tipo_muestra = models.IntegerField(db_column='TIPO_MUESTRA')  # Field name made lowercase.
    referencia = models.CharField(db_column='REFERENCIA', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cliente = models.IntegerField(db_column='CLIENTE')  # Field name made lowercase.
    suministra = models.IntegerField(db_column='SUMINISTRA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'muestras_programadas'


class ParametrosAnaliticas(models.Model):
    identificador = models.IntegerField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=30)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'parametros_analiticas'


class ParametrosMuestra(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=50)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.
    muestra = models.IntegerField(db_column='MUESTRA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'parametros_muestra'


class PerfilesDeUsuarios(models.Model):
    identificador = models.IntegerField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'perfiles_de_usuarios'


class Phmetros(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='CODIGO', max_length=30)  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'phmetros'


class Presupuestos(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_cliente = models.IntegerField(db_column='ID_CLIENTE', blank=True, null=True)  # Field name made lowercase.
    fecha = models.DateField(db_column='FECHA', blank=True, null=True)  # Field name made lowercase.
    activo = models.IntegerField(db_column='ACTIVO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'presupuestos'


class Procedencias(models.Model):
    codigo = models.IntegerField(db_column='CODIGO', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'procedencias'


class RadionucleidosTrazadores(models.Model):
    codigo_trazador = models.CharField(db_column='CODIGO_TRAZADOR', primary_key=True, max_length=30)  # Field name made lowercase.
    radionucleido = models.CharField(db_column='RADIONUCLEIDO', max_length=10)  # Field name made lowercase.
    actividad = models.FloatField(db_column='ACTIVIDAD', blank=True, null=True)  # Field name made lowercase.
    fecha_referencia = models.DateTimeField(db_column='FECHA_REFERENCIA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'radionucleidos_trazadores'


class RecogidaGeneral(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    codigo_csn = models.ForeignKey(CodMuestras, models.DO_NOTHING, db_column='CODIGO_CSN')  # Field name made lowercase.
    codigo_procedencia = models.ForeignKey(Procedencias, models.DO_NOTHING, db_column='CODIGO_PROCEDENCIA')  # Field name made lowercase.
    codigo_memoria = models.ForeignKey(Memorias, models.DO_NOTHING, db_column='CODIGO_MEMORIA')  # Field name made lowercase.
    observaciones = models.CharField(db_column='OBSERVACIONES', max_length=150, blank=True, null=True)  # Field name made lowercase.
    frecuencia_de_recogida = models.ForeignKey(FrecuenciaRecogida, models.DO_NOTHING, db_column='FRECUENCIA_DE_RECOGIDA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'recogida_general'
        unique_together = (('identificador', 'codigo_csn', 'codigo_procedencia', 'codigo_memoria'),)


class RegistroAsistencia(models.Model):
    id_user = models.IntegerField(db_column='ID_USER', primary_key=True)  # Field name made lowercase.
    empresa = models.CharField(db_column='EMPRESA', max_length=20, blank=True, null=True)  # Field name made lowercase.
    dia = models.DateField(db_column='DIA', blank=True, null=True)  # Field name made lowercase.
    hora = models.DateTimeField(db_column='HORA')  # Field name made lowercase.
    registro = models.CharField(db_column='REGISTRO', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_carga = models.DateTimeField(db_column='FECHA_CARGA', blank=True, null=True)  # Field name made lowercase.
    horas_trabajadas = models.FloatField(db_column='HORAS_TRABAJADAS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'registro_asistencia'
        unique_together = (('id_user', 'hora'),)


class RelacionAlicuotasMedidas(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_muestra = models.IntegerField(db_column='ID_MUESTRA')  # Field name made lowercase.
    id_alicuota = models.IntegerField(db_column='ID_ALICUOTA')  # Field name made lowercase.
    determinacion = models.IntegerField(db_column='DETERMINACION')  # Field name made lowercase.
    fecha_analisis = models.DateTimeField(db_column='FECHA_ANALISIS')  # Field name made lowercase.
    actividad = models.FloatField(db_column='ACTIVIDAD', blank=True, null=True)  # Field name made lowercase.
    actividad_error = models.FloatField(db_column='ACTIVIDAD_ERROR', blank=True, null=True)  # Field name made lowercase.
    amd = models.FloatField(db_column='AMD', blank=True, null=True)  # Field name made lowercase.
    tiempo_medida = models.IntegerField(db_column='TIEMPO_MEDIDA', blank=True, null=True)  # Field name made lowercase.
    cantidad = models.FloatField(db_column='CANTIDAD', blank=True, null=True)  # Field name made lowercase.
    rendimiento = models.IntegerField(db_column='RENDIMIENTO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_alicuotas_medidas'


class RelacionAnalisisGamma(models.Model):
    id_histo_muestra_analitica = models.OneToOneField('RelacionHistoricoMuestraAnaliticas', models.DO_NOTHING, db_column='ID_HISTO_MUESTRA_ANALITICA', primary_key=True)  # Field name made lowercase.
    id_isotopo = models.ForeignKey(Isotopos, models.DO_NOTHING, db_column='ID_ISOTOPO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_analisis_gamma'
        unique_together = (('id_histo_muestra_analitica', 'id_isotopo'),)


class RelacionAnalisisTablas(models.Model):
    id_analisis = models.OneToOneField(Analiticas, models.DO_NOTHING, db_column='ID_ANALISIS', primary_key=True)  # Field name made lowercase.
    nombre_tabla = models.ForeignKey(AnalisisTablas, models.DO_NOTHING, db_column='NOMBRE_TABLA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_analisis_tablas'
        unique_together = (('id_analisis', 'nombre_tabla'),)


class RelacionAnaliticasTratamiento(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_muestra_analitica = models.IntegerField(db_column='ID_MUESTRA_ANALITICA')  # Field name made lowercase.
    tratamiento = models.IntegerField(db_column='TRATAMIENTO')  # Field name made lowercase.
    cod_reducido = models.CharField(db_column='COD_REDUCIDO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    fecha_inicio = models.DateTimeField(db_column='FECHA_INICIO')  # Field name made lowercase.
    fecha_fin = models.DateTimeField(db_column='FECHA_FIN', blank=True, null=True)  # Field name made lowercase.
    analista = models.IntegerField(db_column='ANALISTA', blank=True, null=True)  # Field name made lowercase.
    paso_actual = models.IntegerField(db_column='PASO_ACTUAL')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_analiticas_tratamiento'


class RelacionControlesTratamientos(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    tipo_control = models.CharField(db_column='TIPO_CONTROL', max_length=10)  # Field name made lowercase.
    codigo = models.CharField(db_column='CODIGO', max_length=10)  # Field name made lowercase.
    id_muestra_historico = models.IntegerField(db_column='ID_MUESTRA_HISTORICO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_controles_tratamientos'


class RelacionDetectoresAlfabeta(models.Model):
    id_detector = models.CharField(db_column='ID_DETECTOR', primary_key=True, max_length=3)  # Field name made lowercase.
    eficiencia = models.FloatField(db_column='EFICIENCIA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_detectores_alfabeta'


class RelacionDeterminacionesProgramadas(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    determinacion_destino = models.ForeignKey(DeterminacionesProgramadas, models.DO_NOTHING, db_column='DETERMINACION_DESTINO')  # Field name made lowercase.
    determinacion_origen = models.ForeignKey(DeterminacionesProgramadas, models.DO_NOTHING, db_column='DETERMINACION_ORIGEN')  # Field name made lowercase.
    compuesta_de_uni = models.IntegerField(db_column='COMPUESTA_DE_UNI')  # Field name made lowercase.
    compuesta_de_mes = models.IntegerField(db_column='COMPUESTA_DE_MES')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_determinaciones_programadas'


class RelacionDeterminacionesTratamientos(models.Model):
    id_determinacion = models.OneToOneField(Determinaciones, models.DO_NOTHING, db_column='ID_DETERMINACION', primary_key=True)  # Field name made lowercase.
    id_tratamiento = models.ForeignKey('Tratamiento', models.DO_NOTHING, db_column='ID_TRATAMIENTO')  # Field name made lowercase.
    por_defecto = models.IntegerField(db_column='POR_DEFECTO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_determinaciones_tratamientos'
        unique_together = (('id_determinacion', 'id_tratamiento'),)


class RelacionHistoricoAnaliticasCompuestas(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    determinacion_compuesta = models.ForeignKey('RelacionHistoricoMuestraAnaliticas', models.DO_NOTHING, db_column='DETERMINACION_COMPUESTA')  # Field name made lowercase.
    determinacion_parcial = models.ForeignKey('RelacionHistoricoMuestraAnaliticas', models.DO_NOTHING, db_column='DETERMINACION_PARCIAL')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_historico_analiticas_compuestas'


class RelacionHistoricoMuestraAnaliticas(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_historico_recogida = models.ForeignKey(HistoricoRecogida, models.DO_NOTHING, db_column='ID_HISTORICO_RECOGIDA')  # Field name made lowercase.
    codigo_barras = models.CharField(db_column='CODIGO_BARRAS', max_length=50, blank=True, null=True)  # Field name made lowercase.
    id_analiticas = models.ForeignKey(Determinaciones, models.DO_NOTHING, db_column='ID_ANALITICAS')  # Field name made lowercase.
    fecha_hora_entrega = models.DateTimeField(db_column='FECHA_HORA_ENTREGA', blank=True, null=True)  # Field name made lowercase.
    analista_tecnico = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='ANALISTA_TECNICO', blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.
    alicuota = models.CharField(db_column='ALICUOTA', max_length=30)  # Field name made lowercase.
    cantidad_muestra_analizada = models.FloatField(db_column='CANTIDAD_MUESTRA_ANALIZADA', blank=True, null=True)  # Field name made lowercase.
    estado_alicuota = models.ForeignKey(EstadoMuestras, models.DO_NOTHING, db_column='ESTADO_ALICUOTA')  # Field name made lowercase.
    duplicada_de = models.ForeignKey('self', models.DO_NOTHING, db_column='DUPLICADA_DE', blank=True, null=True)  # Field name made lowercase.
    incidencia = models.CharField(db_column='INCIDENCIA', max_length=200, blank=True, null=True)  # Field name made lowercase.
    tratamiento = models.ForeignKey('Tratamiento', models.DO_NOTHING, db_column='TRATAMIENTO', blank=True, null=True)  # Field name made lowercase.
    determ_programada = models.ForeignKey(DeterminacionesProgramadas, models.DO_NOTHING, db_column='DETERM_PROGRAMADA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_historico_muestra_analiticas'
        unique_together = (('identificador', 'id_historico_recogida', 'id_analiticas'),)


class RelacionHistoricoParametrosMuestra(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_historico_recogida = models.ForeignKey(HistoricoRecogida, models.DO_NOTHING, db_column='ID_HISTORICO_RECOGIDA')  # Field name made lowercase.
    id_parametro_muestra = models.ForeignKey(ParametrosMuestra, models.DO_NOTHING, db_column='ID_PARAMETRO_MUESTRA')  # Field name made lowercase.
    valor = models.CharField(db_column='VALOR', max_length=25)  # Field name made lowercase.
    comentarios = models.CharField(db_column='COMENTARIOS', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_historico_parametros_muestra'
        unique_together = (('identificador', 'id_historico_recogida', 'id_parametro_muestra'),)


class RelacionIncidencias(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_muestra = models.IntegerField(db_column='ID_MUESTRA', blank=True, null=True)  # Field name made lowercase.
    id_alicuota = models.IntegerField(db_column='ID_ALICUOTA')  # Field name made lowercase.
    medida = models.CharField(db_column='MEDIDA', max_length=30, blank=True, null=True)  # Field name made lowercase.
    motivo = models.CharField(db_column='MOTIVO', max_length=300, blank=True, null=True)  # Field name made lowercase.
    responsable = models.CharField(db_column='RESPONSABLE', max_length=30, blank=True, null=True)  # Field name made lowercase.
    fecha_incidencia = models.DateTimeField(db_column='FECHA_INCIDENCIA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_incidencias'


class RelacionInformesCorreccion(models.Model):
    informe_nuevo = models.IntegerField(db_column='INFORME_NUEVO', primary_key=True)  # Field name made lowercase.
    codigo_muestra_asociada = models.CharField(db_column='CODIGO_MUESTRA_ASOCIADA', max_length=50)  # Field name made lowercase.
    informe_antiguo = models.IntegerField(db_column='INFORME_ANTIGUO')  # Field name made lowercase.
    fecha_correccion = models.DateTimeField(db_column='FECHA_CORRECCION')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_informes_correccion'


class RelacionInformesGenerados(models.Model):
    id_muestra = models.CharField(db_column='ID_MUESTRA', primary_key=True, max_length=30)  # Field name made lowercase.
    informe = models.CharField(db_column='INFORME', max_length=30)  # Field name made lowercase.
    cliente = models.CharField(db_column='CLIENTE', max_length=255, blank=True, null=True)  # Field name made lowercase.
    referencia = models.CharField(db_column='REFERENCIA', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_emision = models.DateField(db_column='FECHA_EMISION', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_informes_generados'
        unique_together = (('id_muestra', 'informe'),)


class RelacionInformesMuestra(models.Model):
    identificador = models.IntegerField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    codigo_muestra_asociada = models.CharField(db_column='CODIGO_MUESTRA_ASOCIADA', max_length=50)  # Field name made lowercase.
    anio = models.IntegerField(db_column='ANIO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_informes_muestra'
        unique_together = (('identificador', 'anio'),)


class RelacionKBetaBetaresto(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_alicuota_br = models.IntegerField(db_column='ID_ALICUOTA_BR')  # Field name made lowercase.
    id_alicuota_k = models.IntegerField(db_column='ID_ALICUOTA_K')  # Field name made lowercase.
    id_alicuota_b = models.IntegerField(db_column='ID_ALICUOTA_B')  # Field name made lowercase.
    resultado = models.FloatField(db_column='RESULTADO')  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR', blank=True, null=True)  # Field name made lowercase.
    tiempo_cuenta = models.IntegerField(db_column='TIEMPO_CUENTA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_k_beta_betaresto'
        unique_together = (('identificador', 'id_alicuota_br', 'id_alicuota_k', 'id_alicuota_b', 'resultado'),)


class RelacionMuestraAsalvo(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    codigo_muestra = models.IntegerField(db_column='CODIGO_MUESTRA', blank=True, null=True)  # Field name made lowercase.
    codigo_fichero = models.CharField(db_column='CODIGO_FICHERO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    detector = models.IntegerField(db_column='DETECTOR', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_correccion = models.DateTimeField(db_column='FECHA_HORA_CORRECCION', blank=True, null=True)  # Field name made lowercase.
    fecha_rec_inicial = models.DateField(db_column='FECHA_REC_INICIAL', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_analisis = models.DateTimeField(db_column='FECHA_HORA_ANALISIS', blank=True, null=True)  # Field name made lowercase.
    fecha_rec_final = models.DateField(db_column='FECHA_REC_FINAL', blank=True, null=True)  # Field name made lowercase.
    cantidad = models.FloatField(db_column='CANTIDAD', blank=True, null=True)  # Field name made lowercase.
    unidades = models.CharField(db_column='UNIDADES', max_length=11, blank=True, null=True)  # Field name made lowercase.
    tiempo = models.IntegerField(db_column='TIEMPO', blank=True, null=True)  # Field name made lowercase.
    isotopo = models.CharField(db_column='ISOTOPO', max_length=11, blank=True, null=True)  # Field name made lowercase.
    actividad = models.FloatField(db_column='ACTIVIDAD', blank=True, null=True)  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR', blank=True, null=True)  # Field name made lowercase.
    lid = models.FloatField(db_column='LID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_muestra_asalvo'


class RelacionMuestraProgramadaFecha(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_muestra_prog = models.ForeignKey(MuestrasProgramadas, models.DO_NOTHING, db_column='ID_MUESTRA_PROG')  # Field name made lowercase.
    id_fecha_prog = models.ForeignKey(FechasDeterminacionProgramada, models.DO_NOTHING, db_column='ID_FECHA_PROG')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_muestra_programada_fecha'


class RelacionParametrosAnalitica(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_analitica = models.IntegerField(db_column='ID_ANALITICA')  # Field name made lowercase.
    id_parametro_analitica = models.IntegerField(db_column='ID_PARAMETRO_ANALITICA')  # Field name made lowercase.
    valor = models.CharField(db_column='VALOR', max_length=50)  # Field name made lowercase.
    comentarios = models.CharField(db_column='COMENTARIOS', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_parametros_analitica'


class RelacionPresupuestosAnalisis(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_presupuesto = models.IntegerField(db_column='ID_PRESUPUESTO', blank=True, null=True)  # Field name made lowercase.
    analisis = models.CharField(db_column='ANALISIS', max_length=30, blank=True, null=True)  # Field name made lowercase.
    num_muestras = models.IntegerField(db_column='NUM_MUESTRAS', blank=True, null=True)  # Field name made lowercase.
    precio = models.IntegerField(db_column='PRECIO', blank=True, null=True)  # Field name made lowercase.
    total = models.IntegerField(db_column='TOTAL', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_presupuestos_analisis'


class RelacionProcedimientosResponsables(models.Model):
    procedimiento = models.OneToOneField('Tratamiento', models.DO_NOTHING, db_column='PROCEDIMIENTO', primary_key=True)  # Field name made lowercase.
    responsable = models.CharField(db_column='RESPONSABLE', max_length=30)  # Field name made lowercase.
    sustituto_1 = models.CharField(db_column='SUSTITUTO_1', max_length=30)  # Field name made lowercase.
    sustituto_2 = models.CharField(db_column='SUSTITUTO_2', max_length=30, blank=True, null=True)  # Field name made lowercase.
    sustituto_3 = models.CharField(db_column='SUSTITUTO_3', max_length=30, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=300, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_procedimientos_responsables'


class RelacionResultadosSeleccionados(models.Model):
    id_historico_recogida = models.IntegerField(db_column='ID_HISTORICO_RECOGIDA', primary_key=True)  # Field name made lowercase.
    id_alicuota = models.IntegerField(db_column='ID_ALICUOTA')  # Field name made lowercase.
    resultado = models.CharField(db_column='RESULTADO', max_length=30)  # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=87, blank=True, null=True)  # Field name made lowercase.
    idasociado = models.IntegerField(db_column='IDASOCIADO')  # Field name made lowercase.
    usuario = models.CharField(db_column='USUARIO', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_resultados_seleccionados'
        unique_together = (('id_historico_recogida', 'id_alicuota', 'resultado', 'idasociado'),)


class RelacionResultadosSeleccionadosCorreccion(models.Model):
    id_historico_recogida = models.IntegerField(db_column='ID_HISTORICO_RECOGIDA', primary_key=True)  # Field name made lowercase.
    id_alicuota = models.IntegerField(db_column='ID_ALICUOTA')  # Field name made lowercase.
    resultado = models.CharField(db_column='RESULTADO', max_length=30)  # Field name made lowercase.
    tipo = models.CharField(db_column='TIPO', max_length=80, blank=True, null=True)  # Field name made lowercase.
    idasociado = models.IntegerField(db_column='IDASOCIADO')  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='FECHA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_resultados_seleccionados_correccion'
        unique_together = (('id_historico_recogida', 'id_alicuota', 'resultado', 'idasociado', 'fecha'),)


class RelacionSuministradorSuministro(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_suministrador = models.IntegerField(db_column='ID_SUMINISTRADOR')  # Field name made lowercase.
    id_tipo_suministro = models.IntegerField(db_column='ID_TIPO_SUMINISTRO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_suministrador_suministro'


class RelacionTipoDeterminacionParamRequer(models.Model):
    tipo_muestra = models.IntegerField(db_column='TIPO_MUESTRA', primary_key=True)  # Field name made lowercase.
    determinacion = models.IntegerField(db_column='DETERMINACION')  # Field name made lowercase.
    param_requerido_1 = models.IntegerField(db_column='PARAM_REQUERIDO_1', blank=True, null=True)  # Field name made lowercase.
    param_requerido_2 = models.IntegerField(db_column='PARAM_REQUERIDO_2', blank=True, null=True)  # Field name made lowercase.
    param_requerido_3 = models.IntegerField(db_column='PARAM_REQUERIDO_3', blank=True, null=True)  # Field name made lowercase.
    param_requerido_4 = models.IntegerField(db_column='PARAM_REQUERIDO_4', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_tipo_determinacion_param_requer'
        unique_together = (('tipo_muestra', 'determinacion'),)


class RelacionTipoDeterminacionParametros(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    tipo = models.ForeignKey('TipoDeMuestras', models.DO_NOTHING, db_column='TIPO', blank=True, null=True)  # Field name made lowercase.
    determinacion = models.ForeignKey(Determinaciones, models.DO_NOTHING, db_column='DETERMINACION', blank=True, null=True)  # Field name made lowercase.
    parametro = models.ForeignKey(ParametrosMuestra, models.DO_NOTHING, db_column='PARAMETRO', blank=True, null=True)  # Field name made lowercase.
    valor_recomendado = models.CharField(db_column='VALOR_RECOMENDADO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    formula = models.CharField(db_column='FORMULA', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_tipo_determinacion_parametros'


class RelacionTipoMuestraDeterminacionCantidad(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_tipo_muestra = models.IntegerField(db_column='ID_TIPO_MUESTRA')  # Field name made lowercase.
    id_determinacion = models.IntegerField(db_column='ID_DETERMINACION')  # Field name made lowercase.
    valor = models.FloatField(db_column='VALOR', blank=True, null=True)  # Field name made lowercase.
    unidad = models.CharField(db_column='UNIDAD', max_length=30)  # Field name made lowercase.
    formula = models.CharField(db_column='FORMULA', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_tipo_muestra_determinacion_cantidad'


class RelacionTratamientoAlfabetaResultado(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_alicuota = models.IntegerField(db_column='ID_ALICUOTA')  # Field name made lowercase.
    cod_reducido = models.CharField(db_column='COD_REDUCIDO', max_length=30)  # Field name made lowercase.
    parametro = models.CharField(db_column='PARAMETRO', max_length=23, blank=True, null=True)  # Field name made lowercase.
    actividad = models.FloatField(db_column='ACTIVIDAD')  # Field name made lowercase.
    amd = models.FloatField(db_column='AMD')  # Field name made lowercase.
    incertidumbre = models.FloatField(db_column='INCERTIDUMBRE')  # Field name made lowercase.
    detector = models.CharField(db_column='DETECTOR', max_length=3)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='FECHA', blank=True, null=True)  # Field name made lowercase.
    tiempo_cuenta = models.IntegerField(db_column='TIEMPO_CUENTA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_tratamiento_alfabeta_resultado'


class RelacionTratamientoRegistroResultado(models.Model):
    quantulus = models.CharField(db_column='QUANTULUS', max_length=30, blank=True, null=True)  # Field name made lowercase.
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_analitica = models.IntegerField(db_column='ID_ANALITICA')  # Field name made lowercase.
    fondo = models.CharField(db_column='FONDO', max_length=5, blank=True, null=True)  # Field name made lowercase.
    ctime = models.IntegerField(db_column='CTIME')  # Field name made lowercase.
    numciclos = models.IntegerField(db_column='NUMCICLOS')  # Field name made lowercase.
    numciclosleidos = models.IntegerField(db_column='NUMCICLOSLEIDOS')  # Field name made lowercase.
    codalicuota = models.CharField(db_column='CODALICUOTA', max_length=30)  # Field name made lowercase.
    numfuera = models.IntegerField(db_column='NUMFUERA')  # Field name made lowercase.
    factorcorreccion = models.FloatField(db_column='FACTORCORRECCION', blank=True, null=True)  # Field name made lowercase.
    cp0 = models.FloatField(db_column='CP0', blank=True, null=True)  # Field name made lowercase.
    sqp0 = models.FloatField(db_column='SQP0', blank=True, null=True)  # Field name made lowercase.
    fuera0 = models.IntegerField(db_column='FUERA0')  # Field name made lowercase.
    fecha0 = models.DateTimeField(db_column='FECHA0', blank=True, null=True)  # Field name made lowercase.
    cp1 = models.FloatField(db_column='CP1', blank=True, null=True)  # Field name made lowercase.
    sqp1 = models.FloatField(db_column='SQP1', blank=True, null=True)  # Field name made lowercase.
    fuera1 = models.IntegerField(db_column='FUERA1')  # Field name made lowercase.
    fecha1 = models.DateTimeField(db_column='FECHA1', blank=True, null=True)  # Field name made lowercase.
    cp2 = models.FloatField(db_column='CP2', blank=True, null=True)  # Field name made lowercase.
    sqp2 = models.FloatField(db_column='SQP2', blank=True, null=True)  # Field name made lowercase.
    fuera2 = models.IntegerField(db_column='FUERA2')  # Field name made lowercase.
    fecha2 = models.DateTimeField(db_column='FECHA2', blank=True, null=True)  # Field name made lowercase.
    cp3 = models.FloatField(db_column='CP3', blank=True, null=True)  # Field name made lowercase.
    sqp3 = models.FloatField(db_column='SQP3', blank=True, null=True)  # Field name made lowercase.
    fuera3 = models.IntegerField(db_column='FUERA3')  # Field name made lowercase.
    fecha3 = models.DateTimeField(db_column='FECHA3', blank=True, null=True)  # Field name made lowercase.
    cp4 = models.FloatField(db_column='CP4', blank=True, null=True)  # Field name made lowercase.
    sqp4 = models.FloatField(db_column='SQP4', blank=True, null=True)  # Field name made lowercase.
    fuera4 = models.IntegerField(db_column='FUERA4')  # Field name made lowercase.
    fecha4 = models.DateTimeField(db_column='FECHA4', blank=True, null=True)  # Field name made lowercase.
    cp5 = models.FloatField(db_column='CP5', blank=True, null=True)  # Field name made lowercase.
    sqp5 = models.FloatField(db_column='SQP5', blank=True, null=True)  # Field name made lowercase.
    fuera5 = models.IntegerField(db_column='FUERA5')  # Field name made lowercase.
    fecha5 = models.DateTimeField(db_column='FECHA5', blank=True, null=True)  # Field name made lowercase.
    cp6 = models.FloatField(db_column='CP6', blank=True, null=True)  # Field name made lowercase.
    sqp6 = models.FloatField(db_column='SQP6', blank=True, null=True)  # Field name made lowercase.
    fuera6 = models.IntegerField(db_column='FUERA6')  # Field name made lowercase.
    fecha6 = models.DateTimeField(db_column='FECHA6', blank=True, null=True)  # Field name made lowercase.
    cp7 = models.FloatField(db_column='CP7', blank=True, null=True)  # Field name made lowercase.
    sqp7 = models.FloatField(db_column='SQP7', blank=True, null=True)  # Field name made lowercase.
    fuera7 = models.IntegerField(db_column='FUERA7')  # Field name made lowercase.
    fecha7 = models.DateTimeField(db_column='FECHA7', blank=True, null=True)  # Field name made lowercase.
    cp8 = models.FloatField(db_column='CP8', blank=True, null=True)  # Field name made lowercase.
    sqp8 = models.FloatField(db_column='SQP8', blank=True, null=True)  # Field name made lowercase.
    fuera8 = models.IntegerField(db_column='FUERA8')  # Field name made lowercase.
    fecha8 = models.DateTimeField(db_column='FECHA8', blank=True, null=True)  # Field name made lowercase.
    cp9 = models.FloatField(db_column='CP9', blank=True, null=True)  # Field name made lowercase.
    sqp9 = models.FloatField(db_column='SQP9', blank=True, null=True)  # Field name made lowercase.
    fuera9 = models.IntegerField(db_column='FUERA9')  # Field name made lowercase.
    fecha9 = models.DateTimeField(db_column='FECHA9', blank=True, null=True)  # Field name made lowercase.
    cp10 = models.FloatField(db_column='CP10', blank=True, null=True)  # Field name made lowercase.
    sqp10 = models.FloatField(db_column='SQP10', blank=True, null=True)  # Field name made lowercase.
    fuera10 = models.IntegerField(db_column='FUERA10')  # Field name made lowercase.
    fecha10 = models.DateTimeField(db_column='FECHA10', blank=True, null=True)  # Field name made lowercase.
    cp11 = models.FloatField(db_column='CP11', blank=True, null=True)  # Field name made lowercase.
    sqp11 = models.FloatField(db_column='SQP11', blank=True, null=True)  # Field name made lowercase.
    fuera11 = models.IntegerField(db_column='FUERA11')  # Field name made lowercase.
    fecha11 = models.DateTimeField(db_column='FECHA11', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_tratamiento_registro_resultado'


class RelacionTratamientoResultadoIcp(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_analitica = models.IntegerField(db_column='ID_ANALITICA')  # Field name made lowercase.
    concentracion_muestra_icp = models.FloatField(db_column='CONCENTRACION_MUESTRA_ICP')  # Field name made lowercase.
    concentracion_muestra = models.FloatField(db_column='CONCENTRACION_MUESTRA')  # Field name made lowercase.
    dilucion = models.IntegerField(db_column='DILUCION')  # Field name made lowercase.
    lq = models.FloatField(db_column='LQ')  # Field name made lowercase.
    error = models.FloatField(db_column='ERROR')  # Field name made lowercase.
    codigo_reducido_duplicada = models.CharField(db_column='CODIGO_REDUCIDO_DUPLICADA', max_length=30)  # Field name made lowercase.
    concentracion_muestra_primera = models.FloatField(db_column='CONCENTRACION_MUESTRA_PRIMERA')  # Field name made lowercase.
    concentracion_muestra_duplicada = models.FloatField(db_column='CONCENTRACION_MUESTRA_DUPLICADA')  # Field name made lowercase.
    fecha_medida = models.DateTimeField(db_column='FECHA_MEDIDA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_tratamiento_resultado_icp'


class ReportAsistencia(models.Model):
    usuario = models.CharField(db_column='USUARIO', primary_key=True, max_length=30)  # Field name made lowercase.
    semana = models.IntegerField(db_column='SEMANA')  # Field name made lowercase.
    año = models.IntegerField(db_column='AÑO')  # Field name made lowercase.
    horas = models.FloatField(db_column='HORAS', blank=True, null=True)  # Field name made lowercase.
    porcentaje = models.CharField(db_column='PORCENTAJE', max_length=11, blank=True, null=True)  # Field name made lowercase.
    dias_ausencia = models.IntegerField(db_column='DIAS_AUSENCIA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'report_asistencia'
        unique_together = (('usuario', 'semana', 'año'),)


class ReportRealDecretoDit(models.Model):
    radionuclido = models.CharField(db_column='RADIONUCLIDO', primary_key=True, max_length=100)  # Field name made lowercase.
    procedimiento = models.CharField(db_column='PROCEDIMIENTO', max_length=100)  # Field name made lowercase.
    fecha = models.CharField(db_column='FECHA', max_length=30)  # Field name made lowercase.
    actividad = models.CharField(db_column='ACTIVIDAD', max_length=30)  # Field name made lowercase.
    amd = models.CharField(db_column='AMD', max_length=30)  # Field name made lowercase.
    tiempo_medida = models.CharField(db_column='TIEMPO_MEDIDA', max_length=30)  # Field name made lowercase.
    cantidad_muestra = models.CharField(db_column='CANTIDAD_MUESTRA', max_length=30)  # Field name made lowercase.
    rendimiento_quimico = models.CharField(db_column='RENDIMIENTO_QUIMICO', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'report_real_decreto_dit'


class ReportRealDecretoGenerico(models.Model):
    cliente = models.CharField(db_column='CLIENTE', max_length=100)  # Field name made lowercase.
    desc_cliente = models.CharField(db_column='DESC_CLIENTE', max_length=300)  # Field name made lowercase.
    direccion = models.CharField(db_column='DIRECCION', max_length=300)  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=100)  # Field name made lowercase.
    fax = models.CharField(db_column='FAX', max_length=100)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=100)  # Field name made lowercase.
    tipo_muestra = models.CharField(db_column='TIPO_MUESTRA', max_length=100)  # Field name made lowercase.
    id_muestra = models.IntegerField(db_column='ID_MUESTRA', primary_key=True)  # Field name made lowercase.
    procedencia = models.CharField(db_column='PROCEDENCIA', max_length=100)  # Field name made lowercase.
    ref_cliente = models.CharField(db_column='REF_CLIENTE', max_length=100)  # Field name made lowercase.
    fecha_recogida = models.CharField(db_column='FECHA_RECOGIDA', max_length=100)  # Field name made lowercase.
    fecha_recepcion = models.CharField(db_column='FECHA_RECEPCION', max_length=100)  # Field name made lowercase.
    observaciones = models.TextField(db_column='OBSERVACIONES')  # Field name made lowercase.
    informe = models.IntegerField(db_column='INFORME')  # Field name made lowercase.
    dia_informe = models.CharField(db_column='DIA_INFORME', max_length=30)  # Field name made lowercase.
    mes_informe = models.CharField(db_column='MES_INFORME', max_length=30)  # Field name made lowercase.
    anio_informe = models.CharField(db_column='ANIO_INFORME', max_length=30)  # Field name made lowercase.
    dit = models.CharField(db_column='DIT', max_length=3)  # Field name made lowercase.
    titulo_informe = models.CharField(db_column='TITULO_INFORME', max_length=300, blank=True, null=True)  # Field name made lowercase.
    nota_medidas = models.CharField(db_column='NOTA_MEDIDAS', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    modificacion = models.CharField(db_column='MODIFICACION', max_length=255, blank=True, null=True)  # Field name made lowercase.
    anio_informe_db = models.CharField(db_column='ANIO_INFORME_DB', max_length=30, blank=True, null=True)  # Field name made lowercase.
    aspectos_criterio = models.CharField(db_column='ASPECTOS_CRITERIO', max_length=9999, blank=True, null=True)  # Field name made lowercase.
    aspectos_explicativos = models.CharField(db_column='ASPECTOS_EXPLICATIVOS', max_length=9999, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'report_real_decreto_generico'


class ReportRealDecretoMedidas(models.Model):
    indice = models.IntegerField(db_column='INDICE')  # Field name made lowercase.
    radionuclido = models.CharField(db_column='RADIONUCLIDO', max_length=100, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    procedimiento = models.CharField(db_column='PROCEDIMIENTO', max_length=100, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    fecha = models.CharField(db_column='FECHA', max_length=30, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    actividad = models.CharField(db_column='ACTIVIDAD', max_length=30, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    amd = models.CharField(db_column='AMD', max_length=30, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    tiempo_medida = models.CharField(db_column='TIEMPO_MEDIDA', max_length=30, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    cantidad_muestra = models.CharField(db_column='CANTIDAD_MUESTRA', max_length=30, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    rendimiento_quimico = models.CharField(db_column='RENDIMIENTO_QUIMICO', max_length=30, db_collation='latin1_swedish_ci')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'report_real_decreto_medidas'


class ReportSemana(models.Model):
    id_user = models.IntegerField(db_column='ID_USER', primary_key=True)  # Field name made lowercase.
    semana = models.IntegerField(db_column='SEMANA')  # Field name made lowercase.
    año = models.IntegerField(db_column='AÑO')  # Field name made lowercase.
    horas = models.FloatField(db_column='HORAS', blank=True, null=True)  # Field name made lowercase.
    correcto = models.IntegerField(db_column='CORRECTO', blank=True, null=True)  # Field name made lowercase.
    porcentaje = models.FloatField(db_column='PORCENTAJE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'report_semana'
        unique_together = (('id_user', 'semana', 'año'),)


class ResultadosMedidas(models.Model):
    id_alicuota = models.IntegerField()
    id_analisis_medido = models.IntegerField(blank=True, null=True)
    fecha_medida = models.DateTimeField(blank=True, null=True)
    tiempo_medida = models.IntegerField(blank=True, null=True)
    equipo_medida = models.CharField(max_length=20, blank=True, null=True)
    actividad = models.FloatField(blank=True, null=True)
    error = models.FloatField(blank=True, null=True)
    amd = models.FloatField(blank=True, null=True)
    rendimiento = models.FloatField(blank=True, null=True)
    validacion = models.IntegerField(blank=True, null=True)
    unidad = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resultados_medidas'


class SituacionRecepcion(models.Model):
    identificador = models.IntegerField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    coprecipitacion_actual = models.IntegerField(db_column='COPRECIPITACION ACTUAL')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    desecacion_actual = models.IntegerField(db_column='DESECACION ACTUAL')  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'situacion_recepcion'


class Suministradores(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=255)  # Field name made lowercase.
    direccion = models.CharField(db_column='DIRECCION', max_length=150, blank=True, null=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=15, blank=True, null=True)  # Field name made lowercase.
    fax = models.CharField(db_column='FAX', max_length=15, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    persona_contacto = models.CharField(db_column='PERSONA_CONTACTO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nif = models.CharField(db_column='NIF', max_length=15, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'suministradores'


class TipoDeMuestras(models.Model):
    tipo_muestra_id = models.IntegerField(db_column='TIPO_MUESTRA_ID', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=50)  # Field name made lowercase.
    medida_cantidad = models.CharField(db_column='MEDIDA_CANTIDAD', max_length=50, blank=True, null=True)  # Field name made lowercase.
    param_requerido_1 = models.IntegerField(db_column='PARAM_REQUERIDO_1', blank=True, null=True)  # Field name made lowercase.
    param_requerido_2 = models.IntegerField(db_column='PARAM_REQUERIDO_2', blank=True, null=True)  # Field name made lowercase.
    param_requerido_3 = models.IntegerField(db_column='PARAM_REQUERIDO_3', blank=True, null=True)  # Field name made lowercase.
    param_requerido_4 = models.IntegerField(db_column='PARAM_REQUERIDO_4', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_de_muestras'


class Tratamiento(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100)  # Field name made lowercase.
    medida = models.CharField(db_column='MEDIDA', max_length=5)  # Field name made lowercase.
    tiempo_en_lab = models.IntegerField(db_column='TIEMPO_EN_LAB')  # Field name made lowercase.
    alcance = models.FloatField(db_column='ALCANCE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tratamiento'


class Usuarios(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', max_length=10)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=30)  # Field name made lowercase.
    perfil_usuario = models.ForeignKey(PerfilesDeUsuarios, models.DO_NOTHING, db_column='PERFIL_USUARIO')  # Field name made lowercase.
    login = models.CharField(db_column='LOGIN', max_length=256)  # Field name made lowercase.
    activo = models.TextField(db_column='ACTIVO')  # Field name made lowercase. This field type is a guess.
    telegram = models.CharField(db_column='TELEGRAM', max_length=60, blank=True, null=True)  # Field name made lowercase.
    usuario_django = models.IntegerField(db_column='USUARIO_DJANGO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuarios'
        unique_together = (('identificador', 'dni'),)


class UsuariosAsistencia(models.Model):
    id_user = models.IntegerField(db_column='ID_USER', blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=30, blank=True, null=True)  # Field name made lowercase.
    turno = models.CharField(db_column='TURNO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    jornada = models.FloatField(db_column='JORNADA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuarios_asistencia'


class ValoresAnalisisPresupuesto(models.Model):
    analisis = models.CharField(db_column='ANALISIS', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'valores_analisis_presupuesto'
