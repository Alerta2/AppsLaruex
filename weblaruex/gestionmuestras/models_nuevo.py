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
        
class AnalisisMedido(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    analisis = models.CharField(db_column='ANALISIS', max_length=10, blank=True, null=True)  # Field name made lowercase.
    isotopo = models.CharField(db_column='ISOTOPO', max_length=10, blank=True, null=True)  # Field name made lowercase.
    masa = models.IntegerField(db_column='MASA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'analisis_medido'

class BotonesEdicion(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=255, blank=True, null=True)  # Field name made lowercase.
    url = models.CharField(db_column='URL', max_length=255, blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='ICONO', max_length=255, blank=True, null=True)  # Field name made lowercase.
    grupo = models.IntegerField(db_column='GRUPO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'botones_edicion'

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

class EstadoMuestras(models.Model):
    identificador_estado = models.IntegerField(db_column='IDENTIFICADOR_ESTADO', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'estado_muestras'


class EventosMuestras(models.Model):
    identificador = models.IntegerField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    muestra = models.IntegerField(db_column='MUESTRA', blank=True, null=True)  # Field name made lowercase.
    evento = models.CharField(db_column='EVENTO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    fecha_evento = models.DateTimeField(db_column='FECHA_EVENTO', blank=True, null=True)  # Field name made lowercase.
    comentario = models.CharField(db_column='COMENTARIO', max_length=255, blank=True, null=True)  # Field name made lowercase.
    usuario = models.IntegerField(db_column='USUARIO', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'eventos_muestras'

class FrasesPredefinidas(models.Model):
    identificador = models.IntegerField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    texto = models.CharField(db_column='TEXTO', max_length=255, blank=True, null=True)  # Field name made lowercase.
    destino = models.CharField(db_column='DESTINO', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'frases_predefinidas'

class FrecuenciaRecogida(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'frecuencia_recogida'

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


class ParametrosMuestra(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=50)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.
    muestra = models.IntegerField(db_column='MUESTRA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'parametros_muestra_nuevo'
        
class Procedencias(models.Model):
    codigo = models.IntegerField(db_column='CODIGO', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'procedencias'

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

class PerfilesDeUsuarios(models.Model):
    identificador = models.IntegerField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'perfiles_de_usuarios'

class Usuarios(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', max_length=10)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=30)  # Field name made lowercase.
    perfil_usuario = models.ForeignKey(PerfilesDeUsuarios, models.DO_NOTHING, db_column='PERFIL_USUARIO')  # Field name made lowercase.
    login = models.CharField(db_column='LOGIN', max_length=256)  # Field name made lowercase.
    activo = models.TextField(db_column='ACTIVO')  # Field name made lowercase. This field type is a guess.
    telegram = models.CharField(db_column='TELEGRAM', max_length=60, blank=True, null=True)  # Field name made lowercase.
    usuario_django = models.IntegerField(db_column='USUARIO_DJANGO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuarios'
        unique_together = (('identificador', 'dni'),)

class Determinaciones(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'determinaciones'


class Tratamiento(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100)  # Field name made lowercase.
    medida = models.CharField(db_column='MEDIDA', max_length=5)  # Field name made lowercase.
    tiempo_en_lab = models.IntegerField(db_column='TIEMPO_EN_LAB')  # Field name made lowercase.
    alcance = models.FloatField(db_column='ALCANCE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tratamiento'

class MuestraActualCodigo(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
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


class CodMuestras(models.Model):
    codigo = models.CharField(db_column='CODIGO', max_length=3, primary_key=True) # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    tipo = models.ForeignKey(TipoDeMuestras, models.DO_NOTHING, db_column='TIPO')  # Field name made lowercase.
    etiquetas = models.IntegerField(db_column='ETIQUETAS')  # Field name made lowercase.
    nombre_pt = models.CharField(db_column='NOMBRE_PT', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cod_muestras'


class RecogidaGeneral(models.Model):
    identificador = models.AutoField(primary_key=True)  # Field name made lowercase.
    codigo_csn = models.ForeignKey(CodMuestras, models.DO_NOTHING, db_column='CODIGO_CSN')  # Field name made lowercase.
    codigo_procedencia = models.ForeignKey(Procedencias, models.DO_NOTHING, db_column='CODIGO_PROCEDENCIA')  # Field name made lowercase.
    codigo_memoria = models.ForeignKey(Memorias, models.DO_NOTHING, db_column='CODIGO_MEMORIA')  # Field name made lowercase.
    observaciones = models.CharField(db_column='OBSERVACIONES', max_length=150, blank=True, null=True)  # Field name made lowercase.
    frecuencia_de_recogida = models.ForeignKey(FrecuenciaRecogida, models.DO_NOTHING, db_column='FRECUENCIA_DE_RECOGIDA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'recogida_general'


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

class HistoricoRecogida(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    codigo_recogida = models.ForeignKey(RecogidaGeneral, models.DO_NOTHING, db_column='CODIGO_RECOGIDA')  # Field name made lowercase.
    codigo_barras = models.CharField(db_column='CODIGO_BARRAS', max_length=50, blank=True, null=True)  # Field name made lowercase.
    recepcionado_por = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='RECEPCIONADO_POR', blank=True, null=True)  # Field name made lowercase.
    cliente = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='CLIENTE')  # Field name made lowercase.
    suministrador = models.ForeignKey(Suministradores, models.DO_NOTHING, db_column='SUMINISTRADOR')  # Field name made lowercase.
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
        unique_together = (('identificador', 'codigo_recogida', 'suministrador', 'fecha_hora_recogida'),)


class DeterminacionesProgramadas(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    muestra_prog_id = models.IntegerField(db_column='MUESTRA_PROG_ID')  # Field name made lowercase.
    determinacion = models.IntegerField(db_column='DETERMINACION')  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'determinaciones_programadas'



class RelacionHistoricoMuestraAnaliticas(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_historico_recogida = models.ForeignKey(HistoricoRecogida, models.DO_NOTHING, db_column='ID_HISTORICO_RECOGIDA')  # Field name made lowercase.
    codigo_barras = models.CharField(db_column='CODIGO_BARRAS', max_length=50, blank=True, null=True)  # Field name made lowercase.
    id_analiticas = models.ForeignKey(Determinaciones, models.DO_NOTHING, db_column='ID_ANALITICAS')  # Field name made lowercase.
    fecha_hora_entrega = models.DateTimeField(db_column='FECHA_HORA_ENTREGA', blank=True, null=True)  # Field name made lowercase.
    analista_tecnico = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='ANALISTA_TECNICO')  # Field name made lowercase.
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

class RelacionAnaliticasTratamiento(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_muestra_analitica = models.ForeignKey(RelacionHistoricoMuestraAnaliticas, models.DO_NOTHING, db_column='ID_MUESTRA_ANALITICA')  # Field name made lowercase.
    tratamiento = models.ForeignKey(Tratamiento, models.DO_NOTHING, db_column='TRATAMIENTO', blank=True, null=True)  # Field name made lowercase.
    cod_reducido = models.CharField(db_column='COD_REDUCIDO', max_length=30)  # Field name made lowercase.
    fecha_inicio = models.DateTimeField(db_column='FECHA_INICIO')  # Field name made lowercase.
    fecha_fin = models.DateTimeField(db_column='FECHA_FIN', blank=True, null=True)  # Field name made lowercase.
    analista = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='ANALISTA')  # Field name made lowercase.
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

class RelacionDeterminacionesTratamientos(models.Model):
    id_determinacion = models.OneToOneField(Determinaciones, models.DO_NOTHING, db_column='ID_DETERMINACION', primary_key=True)  # Field name made lowercase.
    id_tratamiento = models.ForeignKey('Tratamiento', models.DO_NOTHING, db_column='ID_TRATAMIENTO')  # Field name made lowercase.
    por_defecto = models.IntegerField(db_column="POR_DEFECTO")
    
    class Meta:
        managed = False
        db_table = 'relacion_determinaciones_tratamientos'
        unique_together = (('id_determinacion', 'id_tratamiento'),)


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

class RelacionParametrosAnalitica(models.Model):
    identificador = models.AutoField(db_column='IDENTIFICADOR', primary_key=True)  # Field name made lowercase.
    id_analitica = models.ForeignKey(RelacionHistoricoMuestraAnaliticas, models.DO_NOTHING, db_column='ID_ANALITICA')  # Field name made lowercase.
    id_parametro_analitica = models.ForeignKey(ParametrosMuestra, models.DO_NOTHING, db_column='ID_PARAMETRO_ANALITICA')  # Field name made lowercase.
    valor = models.CharField(db_column='VALOR', max_length=50)  # Field name made lowercase.
    comentarios = models.CharField(db_column='COMENTARIOS', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_parametros_analitica'

class RelacionProcedenciasGestionVraex(models.Model):
    id_gestion_muestras = models.IntegerField(db_column='ID_GESTION_MUESTRAS', primary_key=True)  # Field name made lowercase.
    id_vraex = models.IntegerField(db_column='ID_VRAEX', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_procedencias_gestion_vraex'

class RelacionProcedimientosResponsables(models.Model):
    procedimiento = models.OneToOneField(Tratamiento, models.DO_NOTHING, db_column='PROCEDIMIENTO', primary_key=True)  # Field name made lowercase.
    responsable = models.CharField(db_column='RESPONSABLE', max_length=30)  # Field name made lowercase.
    sustituto_1 = models.CharField(db_column='SUSTITUTO_1', max_length=30)  # Field name made lowercase.
    sustituto_2 = models.CharField(db_column='SUSTITUTO_2', max_length=30, blank=True, null=True)  # Field name made lowercase.
    sustituto_3 = models.CharField(db_column='SUSTITUTO_3', max_length=30, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=300, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_procedimientos_responsables_nueva'


class RelacionTipoDeterminacionParametros(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    tipo = models.ForeignKey(TipoDeMuestras, models.DO_NOTHING, db_column='TIPO', blank=True, null=True)  # Field name made lowercase.
    determinacion = models.ForeignKey(Determinaciones, models.DO_NOTHING, db_column='DETERMINACION', blank=True, null=True)  # Field name made lowercase.
    parametro = models.ForeignKey(ParametrosMuestra, models.DO_NOTHING, db_column='PARAMETRO', blank=True, null=True)  # Field name made lowercase.
    valor_recomendado = models.CharField(db_column='VALOR_RECOMENDADO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    formula = models.CharField(db_column='FORMULA', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_tipo_determinacion_parametros'


class RelacionInformesMuestra(models.Model):
    identificador = models.IntegerField(db_column='IDENTIFICADOR')  # Field name made lowercase.
    codigo_muestra_asociada = models.CharField(db_column='CODIGO_MUESTRA_ASOCIADA', max_length=50, primary_key=True)  # Field name made lowercase.
    anio = models.IntegerField(db_column='ANIO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_informes_muestra'
        unique_together = (('codigo_muestra_asociada', 'anio'),)


# PARA MEDIDAS
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


class ResultadosMedidas(models.Model):
    id_alicuota = models.ForeignKey('RelacionHistoricoMuestraAnaliticas', models.DO_NOTHING, db_column='id_alicuota')
    id_analisis_medido = models.ForeignKey('AnalisisMedido', models.DO_NOTHING, db_column='id_analisis_medido')
    fecha_medida = models.DateTimeField(blank=True, null=True)
    tiempo_medida = models.IntegerField(blank=True, null=True)
    equipo_medida = models.CharField(blank=True, max_length=20, null=True)
    actividad = models.FloatField(blank=True, null=True)
    error = models.FloatField(blank=True, null=True)
    amd = models.FloatField(blank=True, null=True)
    rendimiento = models.FloatField(blank=True, null=True)
    validacion = models.IntegerField(blank=True, null=True)
    unidad = models.CharField(db_column='unidad', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'resultados_medidas'


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

class RelacionTratamientosMuestraCodigo(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_muestra_codigo = models.ForeignKey(MuestraActualCodigo, models.DO_NOTHING, db_column='ID_MUESTRA_CODIGO')  # Field name made lowercase.
    id_tratamiento = models.ForeignKey(Tratamiento, models.DO_NOTHING, db_column='ID_TRATAMIENTO')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_tratamientos_muestra_codigo'

class GestmuesRecogida(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    numero = models.IntegerField(db_column='NUMERO', blank=True, null=True)  # Field name made lowercase.
    csn = models.ForeignKey(CodMuestras, db_column='CSN', max_length=30, on_delete=models.PROTECT)  # Field name made lowercase.
    procedencia = models.ForeignKey(Procedencias, db_column='PROCEDENCIA', on_delete=models.PROTECT)  # Field name made lowercase.
    memoria = models.ForeignKey(Memorias, db_column='MEMORIA', max_length=10, on_delete=models.PROTECT)  # Field name made lowercase.
    suministra = models.CharField(db_column='SUMINISTRA', max_length=255, blank=True, null=True)  # Field name made lowercase.
    observaciones = models.CharField(db_column='OBSERVACIONES', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'gestmues_recogida'

class GestmuesColeccion(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    n_recogida = models.ForeignKey(GestmuesRecogida, models.DO_NOTHING, db_column='N_RECOGIDA', blank=True, null=True)  # Field name made lowercase.
    csn = models.ForeignKey(CodMuestras, db_column='CSN', blank=True, null=True, on_delete=models.PROTECT)  # Field name made lowercase.
    recoge = models.CharField(db_column='RECOGE', max_length=255, blank=True, null=True)  # Field name made lowercase.
    suministra = models.CharField(db_column='SUMINISTRA', max_length=255, blank=True, null=True)  # Field name made lowercase.
    observaciones = models.CharField(db_column='OBSERVACIONES', max_length=255, blank=True, null=True)  # Field name made lowercase.
    recogido = models.IntegerField(db_column='RECOGIDO', blank=True, null=True)  # Field name made lowercase.
    fecha_recogida_inicial = models.DateTimeField(db_column='FECHA_RECOGIDA_INICIAL', blank=True, null=True)  # Field name made lowercase.
    fecha_recogida_final = models.DateTimeField(db_column='FECHA_RECOGIDA_FINAL', blank=True, null=True)  # Field name made lowercase.
    fecha_recepcion = models.DateTimeField(db_column='FECHA RECEPCION', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    conservacion = models.CharField(db_column='CONSERVACION', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nfiltro = models.IntegerField(db_column='NFILTRO', blank=True, null=True)  # Field name made lowercase.
    ibomba = models.CharField(db_column='IBOMBA', max_length=30, blank=True, null=True)  # Field name made lowercase.
    mes = models.CharField(db_column='MES', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'gestmues_coleccion'

class GestmuesRelacionRecogidaDeterminacion(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_muestra_recogida = models.ForeignKey(GestmuesColeccion, models.DO_NOTHING, db_column='ID_MUESTRA_RECOGIDA', blank=True, null=True)  # Field name made lowercase.
    id_determinacion = models.ForeignKey(Determinaciones, models.DO_NOTHING, db_column='ID_DETERMINACION', blank=True, null=True)  # Field name made lowercase.
    mes = models.CharField(db_column='MES', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'gestmues_relacion_recogida_determinacion'

class MensajesTelegram(models.Model):
    id_mensaje = models.AutoField(db_column='ID_MENSAJE', primary_key=True)  # Field name made lowercase.
    id_area = models.IntegerField(db_column='ID_AREA', blank=True, null=True)  # Field name made lowercase.
    id_estacion = models.IntegerField(db_column='ID_ESTACION', blank=True, null=True)  # Field name made lowercase.
    id_canal = models.IntegerField(db_column='ID_CANAL', blank=True, null=True)  # Field name made lowercase.
    fecha_hora_utc = models.DateTimeField(db_column='FECHA_HORA_UTC')  # Field name made lowercase.
    mensaje = models.CharField(db_column='MENSAJE', max_length=200)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=9000, blank=True, null=True)  # Field name made lowercase.
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


class MonitorizaMensajesTipo(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    mensaje = models.CharField(db_column='MENSAJE', max_length=200)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=500, blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='ICONO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    confirmar = models.IntegerField(db_column='CONFIRMAR')  # Field name made lowercase.
    silenciar = models.IntegerField(db_column='SILENCIAR')  # Field name made lowercase.
    estado = models.IntegerField(db_column='ESTADO')  # Field name made lowercase.
    id_area = models.IntegerField(db_column='ID_AREA')  # Field name made lowercase.
    usuarios_sms = models.CharField(db_column='USUARIOS_SMS', max_length=500, blank=True, null=True)  # Field name made lowercase.
    tipo_mensaje_enviado = models.CharField(db_column='TIPO_MENSAJE_ENVIADO', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'monitoriza_mensajes_tipo'

