# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AsuntosPropios(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    year = models.IntegerField(db_column='Year')  # Field name made lowercase.
    empleado = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='Empleado')  # Field name made lowercase.
    fecha_inicio = models.DateField(db_column='Fecha_inicio')  # Field name made lowercase.
    fecha_fin = models.DateField(db_column='Fecha_fin')  # Field name made lowercase.
    dias_consumidos = models.IntegerField(db_column='Dias_consumidos')  # Field name made lowercase.
    estado = models.ForeignKey('EstadosSolicitudes', models.DO_NOTHING, db_column='Estado')  # Field name made lowercase.
    fecha_solicitud = models.DateTimeField(db_column='Fecha_solicitud')  # Field name made lowercase.
    recuperable = models.IntegerField(db_column='Recuperable')  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    tareas_a_sustituir = models.CharField(db_column='Tareas_a_sustituir', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    sustituto = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='Sustituto', blank=True, null=True)  # Field name made lowercase.
    motivo_estado_solicitud = models.CharField(db_column='Motivo_estado_solicitud', max_length=1000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'asuntos_propios'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
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


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CambiosAsuntosPropios(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    solicitante = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='Solicitante')  # Field name made lowercase.
    id_periodo_cambio = models.ForeignKey(AsuntosPropios, models.DO_NOTHING, db_column='ID_periodo_cambio')  # Field name made lowercase.
    fecha_inicio_actual = models.DateField(db_column='Fecha_inicio_actual')  # Field name made lowercase.
    fecha_fin_actual = models.DateField(db_column='Fecha_fin_actual')  # Field name made lowercase.
    dias_actuales_consumidos = models.IntegerField(db_column='Dias_actuales_consumidos')  # Field name made lowercase.
    fecha_inicio_nueva = models.DateField(db_column='Fecha_inicio_nueva')  # Field name made lowercase.
    fecha_fin_nueva = models.DateField(db_column='Fecha_fin_nueva')  # Field name made lowercase.
    dias_nuevos_consumidos = models.IntegerField(db_column='Dias_nuevos_consumidos')  # Field name made lowercase.
    motivo_solicitud = models.CharField(db_column='Motivo_solicitud', max_length=255)  # Field name made lowercase.
    estado = models.ForeignKey('EstadosSolicitudes', models.DO_NOTHING, db_column='Estado')  # Field name made lowercase.
    motivo_rechazo = models.CharField(db_column='Motivo_rechazo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_solicitud = models.DateTimeField(db_column='Fecha_solicitud')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cambios_asuntos_propios'


class CambiosVacaciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    solicitante = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='Solicitante')  # Field name made lowercase.
    id_periodo_cambio = models.ForeignKey('Vacaciones', models.DO_NOTHING, db_column='ID_periodo_cambio')  # Field name made lowercase.
    fecha_inicio_actual = models.DateField(db_column='Fecha_inicio_actual')  # Field name made lowercase.
    fecha_fin_actual = models.DateField(db_column='Fecha_fin_actual')  # Field name made lowercase.
    dias_actuales_consumidos = models.IntegerField(db_column='Dias_actuales_consumidos')  # Field name made lowercase.
    fecha_inicio_nueva = models.DateField(db_column='Fecha_inicio_nueva')  # Field name made lowercase.
    fecha_fin_nueva = models.DateField(db_column='Fecha_fin_nueva')  # Field name made lowercase.
    dias_nuevos_consumidos = models.IntegerField(db_column='Dias_nuevos_consumidos')  # Field name made lowercase.
    motivo_solicitud = models.CharField(db_column='Motivo_solicitud', max_length=255)  # Field name made lowercase.
    estado = models.ForeignKey('EstadosSolicitudes', models.DO_NOTHING, db_column='Estado')  # Field name made lowercase.
    motivo_rechazo = models.CharField(db_column='Motivo_rechazo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_solicitud = models.DateTimeField(db_column='Fecha_solicitud')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cambios_vacaciones'


class Empleados(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    apellidos = models.CharField(db_column='Apellidos', max_length=255)  # Field name made lowercase.
    img = models.CharField(db_column='Img', max_length=30, blank=True, null=True)  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', max_length=12, blank=True, null=True)  # Field name made lowercase.
    fecha_nacimiento = models.DateField(db_column='Fecha_nacimiento', blank=True, null=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='Telefono', max_length=18, blank=True, null=True)  # Field name made lowercase.
    telefono2 = models.CharField(db_column='Telefono2', max_length=18, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=255, blank=True, null=True)  # Field name made lowercase.
    email2 = models.CharField(db_column='Email2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    extension = models.CharField(db_column='Extension', max_length=5, blank=True, null=True)  # Field name made lowercase.
    puesto = models.CharField(db_column='Puesto', max_length=255)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)  # Field name made lowercase.
    info_adicional = models.CharField(db_column='Info_adicional', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_alta_app = models.DateField(db_column='Fecha_alta_app')  # Field name made lowercase.
    fecha_baja_app = models.DateField(db_column='Fecha_baja_app', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'empleados'


class EmpleadosMaquina(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    turno = models.CharField(max_length=255, blank=True, null=True)
    horas_maxima_contrato = models.FloatField(blank=True, null=True)
    en_practicas = models.IntegerField(blank=True, null=True)
    maquina_laboratorio = models.IntegerField(blank=True, null=True)
    maquina_alerta2 = models.IntegerField(blank=True, null=True)
    maquina_departamento = models.IntegerField(blank=True, null=True)
    codigo_fichar = models.IntegerField()
    huellas_registradas = models.IntegerField()
    admin_dispositivo = models.IntegerField()
    fichar_remoto = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'empleados_maquina'


class ErroresRegistroNotificados(models.Model):
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado')
    hora = models.DateTimeField()
    motivo = models.CharField(max_length=255)
    estado = models.IntegerField()
    motivo_rechazo = models.CharField(max_length=255, blank=True, null=True)
    quien_notifica = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='quien_notifica')
    hora_notificacion = models.DateTimeField()
    hora_modificacion_o_rechazo = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'errores_registro_notificados'


class ErroresRegistroNotificadosCopy(models.Model):
    id_empleado = models.ForeignKey('RelEmpleadosUsuarios', models.DO_NOTHING, db_column='id_empleado')
    hora = models.DateTimeField()
    motivo = models.CharField(max_length=255)
    estado = models.IntegerField()
    motivo_rechazo = models.CharField(max_length=255, blank=True, null=True)
    quien_notifica = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='quien_notifica')
    hora_notificacion = models.DateTimeField()
    hora_modificacion_o_rechazo = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'errores_registro_notificados_copy'


class EstadosSolicitudes(models.Model):
    nombre = models.CharField(max_length=255)
    vacaciones = models.IntegerField()
    solicitudes = models.IntegerField()
    incidencias = models.IntegerField()
    permisos_retribuidos = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'estados_solicitudes'


class Festivos(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100)  # Field name made lowercase.
    tipo_festividad = models.ForeignKey('TipoFestivos', models.DO_NOTHING, db_column='Tipo_festividad')  # Field name made lowercase.
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    year = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'festivos'


class HabilitacionesTimetrackpro(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'habilitaciones_timetrackpro'


class Incidencias(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fecha_solicitud = models.DateTimeField(db_column='Fecha_solicitud')  # Field name made lowercase.
    solicitante = models.IntegerField(db_column='Solicitante')  # Field name made lowercase.
    estado = models.IntegerField(db_column='Estado')  # Field name made lowercase.
    motivo = models.CharField(db_column='Motivo', max_length=255)  # Field name made lowercase.
    seccion = models.IntegerField(db_column='Seccion')  # Field name made lowercase.
    prioridad = models.IntegerField(db_column='Prioridad')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'incidencias'


class MaquinaControlAsistencia(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    localizacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'maquina_control_asistencia'


class Mensajes(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    mensaje = models.CharField(max_length=1000)
    destinatarios = models.CharField(max_length=1000)
    remitente = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mensajes'


class NavBar(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255, blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='Icono', max_length=255)  # Field name made lowercase.
    url = models.CharField(db_column='URL', max_length=255)  # Field name made lowercase.
    seccion = models.CharField(db_column='Seccion', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'nav_bar'


class Permisos(models.Model):
    nombre = models.CharField(max_length=255)
    duracion = models.IntegerField(blank=True, null=True)
    naturales_o_habiles = models.CharField(max_length=255)
    periodo_antelacion = models.CharField(max_length=255, blank=True, null=True)
    fecha_maxima_solicitud = models.DateField(blank=True, null=True)
    acreditar = models.IntegerField()
    doc_necesaria = models.CharField(max_length=255)
    legislacion_aplicable = models.CharField(max_length=255)
    bonificable_por_antiguedad = models.IntegerField()
    bonificacion_por_15_years = models.IntegerField()
    bonificacion_por_20_years = models.IntegerField()
    bonificacion_por_25_years = models.IntegerField()
    bonificacion_por_30_years = models.IntegerField()
    year = models.IntegerField()
    es_permiso_retribuido = models.IntegerField()
    pas = models.IntegerField()
    pdi = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'permisos'


class PermisosRetribuidos(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    cod_uex = models.CharField(max_length=7, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    tipo = models.ForeignKey('TipoPermisosYAusencias', models.DO_NOTHING, db_column='tipo')
    dias = models.IntegerField(blank=True, null=True)
    habiles_o_naturales = models.CharField(max_length=15)
    solicitud_dias_naturales_antelacion = models.IntegerField(blank=True, null=True)
    pas = models.IntegerField(blank=True, null=True)
    pdi = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permisos_retribuidos'


class PermisosYAusenciasSolicitados(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='empleado')
    fecha_solicitud = models.DateTimeField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_solicitados = models.IntegerField()
    codigo_permiso = models.ForeignKey(PermisosRetribuidos, models.DO_NOTHING, db_column='codigo_permiso')
    justificante = models.CharField(max_length=255, blank=True, null=True)
    estado = models.ForeignKey(EstadosSolicitudes, models.DO_NOTHING, db_column='estado')
    year = models.IntegerField()
    motivo_estado_solicitud = models.CharField(db_column='Motivo_estado_solicitud', max_length=1000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'permisos_y_ausencias_solicitados'


class ProblemasDetectados(models.Model):
    usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='usuario')
    fecha_registro = models.DateTimeField()
    estado = models.IntegerField()
    tipo = models.IntegerField()
    fecha_resolucion = models.DateTimeField(blank=True, null=True)
    observaciones = models.CharField(max_length=1000, blank=True, null=True)
    problema_detectado = models.CharField(max_length=1000)

    class Meta:
        managed = False
        db_table = 'problemas_detectados'


class Registros(models.Model):
    id_empleado = models.ForeignKey(EmpleadosMaquina, models.DO_NOTHING, db_column='id_empleado')
    nombre_empleado = models.CharField(max_length=255)
    hora = models.DateTimeField()
    maquina = models.ForeignKey(MaquinaControlAsistencia, models.DO_NOTHING, db_column='maquina', blank=True, null=True)
    remoto = models.IntegerField()
    id_archivo_leido = models.ForeignKey('RegistrosJornadaInsertados', models.DO_NOTHING, db_column='id_archivo_leido', blank=True, null=True)
    modificado = models.IntegerField(blank=True, null=True)
    motivo_modificacion = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'registros'


class RegistrosCopy(models.Model):
    id_empleado = models.ForeignKey(EmpleadosMaquina, models.DO_NOTHING, db_column='id_empleado')
    nombre_empleado = models.CharField(max_length=255)
    hora = models.DateTimeField()
    maquina = models.ForeignKey(MaquinaControlAsistencia, models.DO_NOTHING, db_column='maquina', blank=True, null=True)
    remoto = models.IntegerField()
    id_archivo_leido = models.ForeignKey('RegistrosJornadaInsertados', models.DO_NOTHING, db_column='id_archivo_leido', blank=True, null=True)
    modificado = models.IntegerField(blank=True, null=True)
    motivo_modificacion = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'registros_copy'


class RegistrosEliminados(models.Model):
    id_empleado = models.ForeignKey(EmpleadosMaquina, models.DO_NOTHING, db_column='id_empleado')
    nombre_empleado = models.CharField(max_length=255)
    hora = models.DateTimeField()
    maquina = models.ForeignKey(MaquinaControlAsistencia, models.DO_NOTHING, db_column='maquina', blank=True, null=True)
    remoto = models.IntegerField()
    id_archivo_leido = models.ForeignKey('RegistrosJornadaInsertados', models.DO_NOTHING, db_column='id_archivo_leido', blank=True, null=True)
    fecha_eliminacion = models.DateTimeField()
    motivo = models.CharField(max_length=250)
    eliminado_por = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='eliminado_por')
    id_registro_eliminado = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'registros_eliminados'


class RegistrosJornadaInsertados(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    mes = models.CharField(max_length=15)
    year = models.IntegerField()
    seccion = models.CharField(max_length=15)
    ruta = models.CharField(max_length=300, blank=True, null=True)
    fecha_lectura = models.DateTimeField()
    insertador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='insertador')
    remoto = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'registros_jornada_insertados'


class RegistrosManualesControlHorario(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_rel_emp_users = models.ForeignKey('RelEmpleadosUsuarios', models.DO_NOTHING, db_column='id_rel_emp_users')
    mes = models.IntegerField()
    year = models.IntegerField()
    dia = models.IntegerField()
    hora_1_entrada = models.TimeField()
    hora_1_salida = models.TimeField()
    hora_2_entrada = models.TimeField()
    hora_2_salida = models.TimeField()
    motivo = models.CharField(max_length=255, blank=True, null=True)
    laborable = models.IntegerField()
    registrador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='registrador')

    class Meta:
        managed = False
        db_table = 'registros_manuales_control_horario'


class RegistrosManualesControlHorarioNoInsertados(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_rel_emp_users = models.ForeignKey('RelEmpleadosUsuarios', models.DO_NOTHING, db_column='id_rel_emp_users')
    mes = models.IntegerField()
    year = models.IntegerField()
    dia = models.IntegerField()
    hora_1_entrada = models.TimeField()
    hora_1_salida = models.TimeField()
    hora_2_entrada = models.TimeField()
    hora_2_salida = models.TimeField()
    motivo = models.CharField(max_length=255, blank=True, null=True)
    laborable = models.IntegerField()
    registrador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='registrador')

    class Meta:
        managed = False
        db_table = 'registros_manuales_control_horario_no_insertados'


class RelEmpleadosUsuarios(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_usuario = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_usuario')
    id_empleado = models.ForeignKey(EmpleadosMaquina, models.DO_NOTHING, db_column='id_empleado')
    id_auth_user = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_auth_user', blank=True, null=True)
    id_tarjeta_acceso = models.ForeignKey('TarjetasAcceso', models.DO_NOTHING, db_column='id_tarjeta_acceso', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rel_empleados_usuarios'


class RelHabilitacionesUsuarioTimetrackpro(models.Model):
    id_auth_user = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_auth_user')
    id_habilitacion = models.ForeignKey(HabilitacionesTimetrackpro, models.DO_NOTHING, db_column='id_habilitacion')

    class Meta:
        managed = False
        db_table = 'rel_habilitaciones_usuario_timetrackpro'


class RelJornadaEmpleados(models.Model):
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado')
    horas_semanales = models.FloatField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rel_jornada_empleados'


class Secciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    color = models.CharField(db_column='Color', max_length=10)  # Field name made lowercase.
    tema = models.CharField(db_column='Tema', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'secciones'


class TarjetasAcceso(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    dni = models.CharField(db_column='DNI', max_length=255)  # Field name made lowercase.
    imagen = models.CharField(max_length=255, blank=True, null=True)
    acceso_laboratorios = models.IntegerField()
    acceso_cpd = models.IntegerField(db_column='acceso_CPD')  # Field name made lowercase.
    acceso_alerta2 = models.IntegerField()
    id_tarjeta = models.CharField(db_column='ID_tarjeta', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_alta = models.DateField()
    fecha_baja = models.DateField(blank=True, null=True)
    activo = models.IntegerField()
    fecha_expiracion = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tarjetas_acceso'


class TipoFestivos(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    color = models.CharField(db_column='Color', max_length=50)  # Field name made lowercase.
    color_calendario = models.CharField(db_column='Color_calendario', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_festivos'


class TipoPermisosYAusencias(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_permisos_y_ausencias'


class TipoVacaciones(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    color = models.CharField(db_column='Color', max_length=50)  # Field name made lowercase.
    color_calendario = models.CharField(db_column='Color_calendario', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_vacaciones'


class Vacaciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    tipo_vacaciones = models.ForeignKey(TipoVacaciones, models.DO_NOTHING, db_column='Tipo_vacaciones')  # Field name made lowercase.
    year = models.IntegerField(db_column='Year')  # Field name made lowercase.
    empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Empleado')  # Field name made lowercase.
    fecha_inicio = models.DateField(db_column='Fecha_inicio')  # Field name made lowercase.
    fecha_fin = models.DateField(db_column='Fecha_fin')  # Field name made lowercase.
    dias_consumidos = models.IntegerField(db_column='Dias_consumidos')  # Field name made lowercase.
    estado = models.ForeignKey(EstadosSolicitudes, models.DO_NOTHING, db_column='Estado')  # Field name made lowercase.
    fecha_solicitud = models.DateTimeField(db_column='Fecha_solicitud')  # Field name made lowercase.
    motivo_rechazo = models.CharField(db_column='Motivo_rechazo', max_length=1000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'vacaciones'