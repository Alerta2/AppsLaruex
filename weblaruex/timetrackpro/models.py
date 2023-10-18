
# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from datetime import timezone
from django.db import models
from django.contrib.contenttypes.models import ContentType 
from django.contrib.auth.models import Permission


class Archivos(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    justificantes_adicionales = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archivos'


class ArchivosLeidos(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    ruta = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archivos_leidos'


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
    content_type = models.ForeignKey(ContentType, models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)




class AuthUser(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
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


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)

class Duraciones(models.Model):
    id = models.IntegerField(primary_key=True)
    unidad = models.CharField(max_length=255, blank=True, null=True)
    categoria = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'duraciones'

class RegistrosJornadaInsertados(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    mes = models.CharField(max_length=15)
    year = models.IntegerField()
    seccion = models.CharField(max_length=15)
    ruta = models.CharField(max_length=300, blank=True, null=True)
    fecha_lectura = models.DateTimeField()
    insertador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='insertador')
    remoto = models.IntegerField(db_column='remoto')

    class Meta:
        managed = False
        db_table = 'registros_jornada_insertados'
        
class Empleados(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    turno = models.CharField(max_length=255, blank=True, null=True)
    horas_maxima_contrato = models.FloatField(blank=True, null=True)
    en_practicas = models.IntegerField(blank=True, null=True)
    maquina_laboratorio = models.IntegerField(blank=True, null=True)
    maquina_alerta2 = models.IntegerField(blank=True, null=True)
    maquina_departamento = models.IntegerField(blank=True, null=True)
    codigo_fichar = models.IntegerField(db_column='codigo_fichar')
    huellas_registradas = models.IntegerField(db_column='huellas_registradas')
    admin_dispositivo = models.IntegerField(db_column='admin_dispositivo')
    fichar_remoto = models.IntegerField(db_column='fichar_remoto')

    class Meta:
        managed = False
        db_table = 'empleados'

class Mensajes(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    mensaje = models.CharField(max_length=1000)
    destinatarios = models.CharField(max_length=1000)
    remitente = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mensajes'


class TipoFestivos(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.
    color = models.CharField(db_column='Color', max_length=50)  # Field name made lowercase.
    color_calendario = models.CharField(db_column='Color_calendario', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_festivos'


class FestivosYVacaciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100)  # Field name made lowercase.
    tipo_festividad = models.ForeignKey('TipoFestivos', models.DO_NOTHING, db_column='Tipo_festividad')  # Field name made lowercase.
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    year = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'festivos_y_vacaciones'

class EstadosSolicitudes(models.Model):
    id = models.AutoField(db_column='id',primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=255)

    class Meta:
        managed = False
        db_table = 'estados_solicitudes'


class MaquinaControlAsistencia(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    localizacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'maquina_control_asistencia'


class PeriodoAntelacion(models.Model):
    id = models.IntegerField(primary_key=True)
    unidad = models.CharField(max_length=255, blank=True, null=True)
    categoria = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'periodo_antelacion'


class Permisos(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    duracion = models.ForeignKey(Duraciones, models.DO_NOTHING, db_column='duracion', blank=True, null=True)
    periodo_antelacion = models.ForeignKey(PeriodoAntelacion, models.DO_NOTHING, db_column='periodo_antelacion', blank=True, null=True)
    acreditar = models.IntegerField(blank=True, null=True)
    doc_necesaria = models.CharField(max_length=255, blank=True, null=True)
    legislacion_aplicable = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permisos'


class RegistroAusenciasAceptadas(models.Model):
    id = models.IntegerField(primary_key=True)
    id_registro_solicitud = models.IntegerField(blank=True, null=True)
    id_empleado = models.IntegerField(blank=True, null=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    id_estado = models.IntegerField(blank=True, null=True)
    archivo_solicitud = models.CharField(max_length=255, blank=True, null=True)
    archivo_justificante = models.CharField(max_length=255, blank=True, null=True)
    funciones_a_cubrir = models.CharField(max_length=255, blank=True, null=True)
    id_empleado_sustituto = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'registro_ausencias_aceptadas'


class Registros(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado', blank=True, null=True)
    nombre_empleado = models.CharField(max_length=255, blank=True, null=True)
    hora = models.DateTimeField()
    maquina = models.ForeignKey(MaquinaControlAsistencia, models.DO_NOTHING, db_column='maquina', blank=True, null=True)
    remoto = models.IntegerField(blank=True, null=True)
    #debe relacionarse con id de la tabla registros_jornada_insertados
    id_archivo_leido = models.ForeignKey('RegistrosJornadaInsertados', models.DO_NOTHING, db_column='id_archivo_leido', blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'registros'


class RegitroSolicitudViajes(models.Model):
    id = models.IntegerField(primary_key=True)
    id_empleado = models.IntegerField(blank=True, null=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    id_estado = models.IntegerField(blank=True, null=True)
    motivo_solicitud_rechazo = models.CharField(max_length=255, blank=True, null=True)
    archivo_solicitud = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'regitro_solicitud_viajes'


class RegitroSolicitudesPermisos(models.Model):
    id = models.IntegerField(primary_key=True)
    id_empleado = models.IntegerField(blank=True, null=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    id_permisos = models.IntegerField(blank=True, null=True)
    id_estado = models.IntegerField(blank=True, null=True)
    motivo_solicitud_rechazo = models.CharField(max_length=255, blank=True, null=True)
    archivo_solicitud = models.CharField(max_length=255, blank=True, null=True)
    funciones_a_cubrir = models.CharField(max_length=255, blank=True, null=True)
    id_empleado_sustituto = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'regitro_solicitudes_permisos'


class RegitroViajesAceptados(models.Model):
    id = models.IntegerField(primary_key=True)
    id_registro_solicitud = models.IntegerField(blank=True, null=True)
    id_empleado = models.IntegerField(blank=True, null=True)
    dieta = models.IntegerField(blank=True, null=True)
    ruta_solicitud = models.CharField(max_length=255, blank=True, null=True)
    ruta_dieta = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'regitro_viajes_aceptados'


class RelEmpleadosUsuarios(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario')
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado')
    id_auth_user = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='id_auth_user', blank=True, null=True)
    id_tarjeta_acceso = models.ForeignKey('TarjetasAcceso', models.DO_NOTHING, db_column='id_tarjeta_acceso', blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'rel_empleados_usuarios'

class RelJornadaEmpleados(models.Model):
    id = models.IntegerField(primary_key=True)
    id_empleado = models.IntegerField(blank=True, null=True)
    fecha_inicio = models.DateTimeField()
    motivo = models.CharField(max_length=255, blank=True, null=True)
    horas_semanales = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rel_jornada_empleados'


class RelJustificantesEmpleados(models.Model):
    id = models.IntegerField(primary_key=True)
    id_ausencia = models.IntegerField(blank=True, null=True)
    id_empleado = models.IntegerField(blank=True, null=True)
    justificante = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rel_justificantes_empleados'


class Usuarios(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    apellidos = models.CharField(db_column='Apellidos', max_length=255, blank=True, null=True)  # Field name made lowercase.
    img = models.CharField(db_column='Img', max_length=30, blank=True, null=True)  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', max_length=10, blank=True, null=True)  # Field name made lowercase.
    fecha_nacimiento = models.DateField(db_column='Fecha_nacimiento', blank=True, null=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='Telefono', max_length=18, blank=True, null=True)  # Field name made lowercase.
    telefono2 = models.CharField(db_column='Telefono2', max_length=18, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=255, blank=True, null=True)  # Field name made lowercase.
    email2 = models.CharField(db_column='Email2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    extension = models.CharField(db_column='Extension', max_length=5, blank=True, null=True)  # Field name made lowercase.
    puesto = models.CharField(db_column='Puesto', max_length=255)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)  # Field name made lowercase.
    info_adicional = models.CharField(db_column='Info_adicional', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_alta_app =  models.DateField(db_column='Fecha_alta_app')  # Field name made lowercase.
    fecha_baja_app =  models.DateField(db_column='Fecha_baja_app', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuarios'

class NavBar(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255, blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='Icono', max_length=255)  # Field name made lowercase.
    url = models.CharField(db_column='URL', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'nav_bar'


class TarjetasAcceso(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    dni = models.CharField(db_column='DNI', max_length=255)  # Field name made lowercase.
    imagen = models.CharField(db_column='imagen', max_length=255, blank=True, null=True)  # Field name made lowercase.
    acceso_laboratorios = models.IntegerField(db_column='acceso_laboratorios')  # Field name made lowercase.
    acceso_cpd = models.IntegerField(db_column='acceso_CPD')  # Field name made lowercase.
    acceso_alerta2 = models.IntegerField(db_column='acceso_alerta2')
    id_tarjeta = models.CharField(db_column='ID_tarjeta', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_alta = models.DateField(db_column='fecha_alta')  # Field name made lowercase.
    fecha_baja = models.DateField(db_column='fecha_baja', blank=True, null=True)  # Field name made lowercase.
    fecha_expiracion = models.DateField(db_column='fecha_expiracion', blank=True, null=True)  # Field name made lowercase.
    activo = models.IntegerField(db_column='activo')

    class Meta:
        managed = False
        db_table = 'tarjetas_acceso'