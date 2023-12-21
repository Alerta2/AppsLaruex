# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


''' ----------------- MODELOS DE LA BASE DE DATOS -----------------
'''

# Importación de la tabla AuthUser con todos sus campos
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

# Importación de la tabla AuthUser con todos sus campos
class PropietariosDocumentos(models.Model):
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

# Importación de la tabla Habilitaciones con todos sus campos
class Estado(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'estado'

# Importación de la tabla Habilitaciones con todos sus campos
class Habilitaciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    titulo = models.CharField(db_column='Titulo', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'habilitaciones'


# DUPLICADO de la tabla Objeto RENOMBRADA por ObjetoRelacionado conservando su campos
class ObjetoPadre(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    padre = models.ForeignKey('self', models.DO_NOTHING, db_column='Padre', blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    fecha_subida = models.DateTimeField(db_column='Fecha_subida')  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=255)  # Field name made lowercase.
    ruta_editable = models.CharField(db_column='Ruta_editable', max_length=255)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255)  # Field name made lowercase.
    creador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Creador')  # Field name made lowercase.
    visible = models.IntegerField(db_column='Visible', blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='Icono', max_length=255)  # Field name made lowercase.
    id_estado = models.ForeignKey(Estado, models.DO_NOTHING, db_column='ID_estado', blank=True, null=True)  # Field name made lowercase.
    id_habilitacion = models.ForeignKey(Habilitaciones, models.DO_NOTHING, db_column='ID_habilitacion')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'objeto'

# Importación de la tabla Objeto con todos sus campos
class Objeto(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    padre = models.ForeignKey(ObjetoPadre, models.DO_NOTHING, db_column='Padre', blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=10000)  # Field name made lowercase.
    fecha_subida = models.DateTimeField(db_column='Fecha_subida')  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ruta_editable = models.CharField(db_column='Ruta_editable', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255)  # Field name made lowercase.
    creador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Creador')  # Field name made lowercase.
    visible = models.IntegerField(db_column='Visible', blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='Icono', max_length=255)  # Field name made lowercase.
    id_estado = models.ForeignKey(Estado, models.DO_NOTHING, db_column='ID_estado', blank=True, null=True)  # Field name made lowercase.
    id_habilitacion = models.ForeignKey(Habilitaciones, models.DO_NOTHING, db_column='ID_habilitacion')  # Field name made lowercase.
    propietario = models.ForeignKey(PropietariosDocumentos, models.DO_NOTHING, db_column='Propietario')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'objeto'


# DUPLICADO de la tabla Objeto RENOMBRADA por ObjetoRelacionado conservando su campos
class ObjetoRelacionado(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    padre = models.ForeignKey('self', models.DO_NOTHING, db_column='Padre', blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    fecha_subida = models.DateTimeField(db_column='Fecha_subida')  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=255)  # Field name made lowercase.
    ruta_editable = models.CharField(db_column='Ruta_editable', max_length=255)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255)  # Field name made lowercase.
    creador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Creador')  # Field name made lowercase.
    visible = models.IntegerField(db_column='Visible', blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='Icono', max_length=255)  # Field name made lowercase.
    id_estado = models.ForeignKey(Estado, models.DO_NOTHING, db_column='ID_estado', blank=True, null=True)  # Field name made lowercase.
    id_habilitacion = models.ForeignKey(Habilitaciones, models.DO_NOTHING, db_column='ID_habilitacion')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'objeto'

# DUPLICADO de la tabla AuthUser RENOMBRADA por Responsables conservando su campos
class Responsables(models.Model):
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

# DUPLICADO de la tabla AuthUser RENOMBRADA por Revisores conservando su campos
class Revisores(models.Model):
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

# DUPLICADO de la tabla AuthUser RENOMBRADA como Editores conservando su campos
class Editores(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase
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

class Entidades(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    imagen = models.CharField(db_column='Imagen', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'entidades'

class EntidadesFinanciadoras(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    imagen = models.CharField(db_column='Imagen', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'entidades'


class Propietarios(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    imagen = models.CharField(db_column='Imagen', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'entidades'

# DUPLICADO de la tabla AuthUser RENOMBRADA por Miembros conservando su campos
class UserCurriculum(models.Model):
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

class Curriculum(models.Model):
    id = models.OneToOneField(Objeto, models.DO_NOTHING, db_column='ID', primary_key=True)  # Field name made lowercase.
    id_usuario = models.ForeignKey(UserCurriculum, models.DO_NOTHING, db_column='ID_usuario')  # Field name made lowercase.
    id_contacto = models.ForeignKey('Contacto', models.DO_NOTHING, db_column='ID_contacto')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'curriculum'


class CurriculumCopyDelete(models.Model):
    id_doc = models.OneToOneField('Objeto', models.DO_NOTHING, db_column='ID_doc', primary_key=True)  # Field name made lowercase.
    cv_actual = models.CharField(db_column='CV_actual', max_length=255)  # Field name made lowercase.
    contrato_vigente = models.CharField(db_column='Contrato_vigente', max_length=255)  # Field name made lowercase.
    formacion_y_titulacion = models.CharField(db_column='Formacion_y_titulacion', max_length=255)  # Field name made lowercase.
    acreditacion = models.CharField(db_column='Acreditacion', max_length=255)  # Field name made lowercase.
    acuerdo_confidencialidad = models.IntegerField(db_column='Acuerdo_confidencialidad')  # Field name made lowercase.
    propietario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Propietario')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'curriculum_copy_delete'


class FormacionCurriculum(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_curriculum = models.ForeignKey(Curriculum, models.DO_NOTHING, db_column='ID_curriculum')  # Field name made lowercase.
    titulo = models.CharField(db_column='Titulo', max_length=255)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=10000, blank=True, null=True)  # Field name made lowercase.
    horas = models.FloatField(db_column='Horas', blank=True, null=True)  # Field name made lowercase.
    ruta = models.CharField(db_column='Ruta', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_inicio = models.DateTimeField(db_column='Fecha_inicio')  # Field name made lowercase.
    fecha_fin = models.DateTimeField(db_column='Fecha_fin')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'formacion_curriculum'

# Importación de la tabla Documento con todos sus campos
class Documento(models.Model):
    id_doc = models.OneToOneField(Objeto, models.DO_NOTHING, db_column='ID_doc', primary_key=True)
    editable = models.IntegerField(db_column='Editable', blank=True, null=True)  # Field name made lowercase.
    fecha_actualizacion = models.DateTimeField(db_column='Fecha_actualizacion')  # Field name made lowercase.
    num_modificaciones = models.IntegerField(db_column='Num_modificaciones')  # Field name made lowercase.
    tipo_documento = models.ForeignKey('TipoDocumentos', models.DO_NOTHING, db_column='Tipo_documento', blank=True, null=True)  # Field name made lowercase.
    version = models.IntegerField(db_column='Version', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = True
        db_table = 'documento'

# Importación de la tabla Procedimiento con todos sus campos
class Procedimiento(models.Model):
    id_doc = models.OneToOneField(Objeto, models.DO_NOTHING, db_column='ID_doc', primary_key=True)  # Field name made lowercase.
    titulo = models.CharField(db_column='Titulo', max_length=255)  # Field name made lowercase.
    version = models.IntegerField(db_column='Version')  # Field name made lowercase.
    fecha_verificacion = models.DateTimeField(db_column='Fecha_verificacion')  # Field name made lowercase.
    responsable = models.ForeignKey(Responsables, models.DO_NOTHING, db_column='Responsable')  # Field name made lowercase.
    revisor = models.ForeignKey(Revisores, models.DO_NOTHING, db_column='Revisor')  # Field name made lowercase.
    modificaciones = models.TextField(db_column='Modificaciones')  # Field name made lowercase.
    
    class Meta:
        managed = True
        db_table = 'procedimiento'


# Importación de la tabla Formatos con todos sus campos
class Formatos(models.Model):
    id_doc = models.OneToOneField(Objeto, models.DO_NOTHING, db_column='ID_doc', primary_key=True)  # Field name made lowercase.
    titulo = models.CharField(db_column='Titulo', max_length=255)  # Field name made lowercase.
    version = models.IntegerField(db_column='Version')  # Field name made lowercase.
    plantilla = models.IntegerField(db_column='Plantilla')  # Field name made lowercase.
    editor = models.ForeignKey(Editores, models.DO_NOTHING, db_column='Editor')  # Field name made lowercase.
    fecha_edicion = models.DateTimeField(db_column='Fecha_edicion')  # Field name made lowercase.
    procedimiento = models.CharField(db_column='Procedimiento', max_length=255)  # Field name made lowercase.
    editable = models.IntegerField(db_column='Editable', blank=True, null=True)  # Field name made lowercase.
    info_adicional = models.CharField(db_column='Info_adicional', max_length=255, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = True
        db_table = 'formatos'

class GrupoEquipos(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'grupo_equipos'

class Llave(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    imagen = models.CharField(db_column='Imagen', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ubicacion = models.ForeignKey('Ubicaciones', models.DO_NOTHING, db_column='Ubicacion', blank=True, null=True)  # Field name made lowercase.
    responsable = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Responsable')  # Field name made lowercase.
    color = models.CharField(db_column='Color', max_length=255)  # Field name made lowercase.
    id_habilitacion = models.ForeignKey(Habilitaciones, models.DO_NOTHING, db_column='ID_habilitacion')  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'llave'

class RelLlavesUbicaciones(models.Model):
    id = models.BigAutoField(primary_key=True)
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.
    id_llave = models.ForeignKey(Llave, models.DO_NOTHING, db_column='ID_llave')  # Field name made lowercase.
    id_ubicacion = models.ForeignKey('Ubicaciones', models.DO_NOTHING, db_column='ID_ubicacion')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rel_llaves_ubicaciones'

# Importación de la tabla MenuBar con todos sus campos
class MenuBar(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255, blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='Icono', max_length=255)  # Field name made lowercase.
    url = models.CharField(db_column='URL', max_length=255)  # Field name made lowercase.
    imagen = models.CharField(db_column='Imagen', max_length=255, blank=True, null=True)  # Field name made lowercase.
    desplegable = models.IntegerField(db_column='Desplegable', blank=True, null=True)  # Field name made lowercase.
    padre = models.IntegerField(db_column='Padre', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'menu_bar'

# Importación de la tabla NotificacionRevisiones con todos sus campos
class NotificacionRevisiones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_doc = models.IntegerField(db_column='ID_doc')  # Field name made lowercase.
    solicitante = models.IntegerField(db_column='Solicitante')  # Field name made lowercase.
    revisor = models.IntegerField(db_column='Revisor')  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.
    comentario = models.CharField(db_column='Comentario', max_length=255)  # Field name made lowercase.
    respuesta = models.CharField(db_column='Respuesta', max_length=255)  # Field name made lowercase.
    id_estado = models.ForeignKey(Estado, models.DO_NOTHING, db_column='ID_Estado')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'notificacion_revisiones'

# Importación de la tabla RelUsuarioHabilitaciones con todos sus campos
class RelUsuarioHabilitaciones(models.Model):
    id_usuario = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='ID_usuario')  # Field name made lowercase.
    id_habilitacion = models.ForeignKey(Habilitaciones, models.DO_NOTHING,db_column='ID_habilitacion')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=255)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'rel_usuario_habilitaciones'
        unique_together = (('id_usuario', 'id_habilitacion'),)

# Importación de la tabla RelacionDocumentaciones con todos sus campos
class RelacionDocumentaciones(models.Model):
    id_doc = models.OneToOneField(Objeto, models.DO_NOTHING, db_column='ID_doc')  # Field name made lowercase.
    id_relacionado = models.OneToOneField(ObjetoRelacionado, models.DO_NOTHING, db_column='ID_relacionado')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'relacion_documentaciones'
        unique_together = (('id_doc', 'id_relacionado'),)

# DUPLICADO de la tabla RelacionDocumentaciones RENOMBRADA como RelacionDocumentacionesInverso conservando su campos
class RelacionDocumentacionesInverso(models.Model):
    id_relacionado = models.OneToOneField(Objeto, models.DO_NOTHING, db_column='ID_doc')  # Field name made lowercase.
    id_doc = models.OneToOneField(ObjetoRelacionado, models.DO_NOTHING, db_column='ID_relacionado')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relacion_documentaciones'
        unique_together = (('id_doc', 'id_relacionado'),)


class Equipo(models.Model):
    id = models.OneToOneField('Objeto', models.DO_NOTHING, db_column='ID', primary_key=True)  # Field name made lowercase.
    cod_laruex = models.IntegerField(db_column='COD_Laruex')  # Field name made lowercase.
    cod_uex = models.IntegerField(db_column='COD_Uex', blank=True, null=True)  # Field name made lowercase.
    tipo_equipo = models.ForeignKey('TipoEquipo', models.DO_NOTHING, db_column='Tipo_equipo')  # Field name made lowercase.
    fabricante = models.ForeignKey('Fabricante', models.DO_NOTHING, db_column='Fabricante')  # Field name made lowercase.
    num_serie = models.CharField(db_column='NUM_serie', max_length=255)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=10000, blank=True, null=True)  # Field name made lowercase.
    fecha_alta = models.DateField(db_column='Fecha_alta')  # Field name made lowercase.
    fecha_baja = models.DateField(db_column='Fecha_baja', blank=True, null=True)  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio', blank=True, null=True)  # Field name made lowercase.
    modelo = models.CharField(db_column='Modelo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    motivo_baja = models.CharField(db_column='Motivo_baja', max_length=255, blank=True, null=True)  # Field name made lowercase.
    proyecto = models.ForeignKey('Proyecto', models.DO_NOTHING, db_column='Proyecto', blank=True, null=True)  # Field name made lowercase.
    cod_spida = models.IntegerField(db_column='COD_Spida', blank=True, null=True)  # Field name made lowercase.
    propietario = models.ForeignKey(Entidades, models.DO_NOTHING, db_column='Propietario', blank=True, null=True)  # Field name made lowercase.
    proveedor = models.ForeignKey('Proveedor', models.DO_NOTHING, db_column='Proveedor', blank=True, null=True)  # Field name made lowercase.
    ubicacion_actual = models.ForeignKey('Ubicaciones', models.DO_NOTHING, db_column='Ubicacion_actual', blank=True, null=True)  # Field name made lowercase.
    grupo = models.ForeignKey('GrupoEquipos', models.DO_NOTHING, db_column='Grupo', blank=True, null=True)  # Field name made lowercase.
    alta_uex = models.IntegerField(db_column='Alta_Uex')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'equipo'

class Proyecto(models.Model):
    id = models.OneToOneField(Objeto, models.DO_NOTHING, db_column='ID', primary_key=True)  # Field name made lowercase.
    codigo = models.CharField(db_column='Codigo', max_length=255)  # Field name made lowercase.
    fecha_inicio = models.DateField(db_column='Fecha_inicio')  # Field name made lowercase.
    fecha_fin = models.DateField(db_column='Fecha_fin')  # Field name made lowercase.
    presupuesto = models.FloatField(db_column='Presupuesto', blank=True, null=True)  # Field name made lowercase.
    objetivo = models.CharField(db_column='Objetivo', max_length=10000, blank=True, null=True)  # Field name made lowercase.
    expediente = models.CharField(db_column='Expediente', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'proyecto'

class Fabricante(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fijo = models.CharField(db_column='Fijo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    movil = models.CharField(db_column='Movil', max_length=20, blank=True, null=True)  # Field name made lowercase.
    correo = models.CharField(db_column='Correo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    comentarios = models.CharField(db_column='Comentarios', max_length=255, blank=True, null=True)  # Field name made lowercase.
    web = models.CharField(db_column='Web', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'fabricante'

class Proveedor(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    cif = models.CharField(db_column='CIF', max_length=15, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='Telefono', max_length=20, blank=True, null=True)  # Field name made lowercase.
    telefono_2 = models.CharField(db_column='Telefono_2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fax = models.CharField(db_column='Fax', max_length=20, blank=True, null=True)  # Field name made lowercase.
    correo = models.CharField(db_column='Correo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    correo_2 = models.CharField(db_column='Correo_2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    web = models.CharField(db_column='Web', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comentarios = models.CharField(db_column='Comentarios', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'proveedor'

class TipoDocumentos(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tipo_documentos'

class TipoEquipo(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tipo_equipo'


class TipoUbicacion(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tipo_ubicacion'


class Ubicaciones(models.Model):
    id = models.OneToOneField(Objeto, models.DO_NOTHING, db_column='ID', primary_key=True)  # Field name made lowercase.
    latitud = models.CharField(db_column='Latitud', max_length=255)  # Field name made lowercase.
    longitud = models.CharField(db_column='Longitud', max_length=255)  # Field name made lowercase.
    tipo_ubicacion = models.ForeignKey(TipoUbicacion, models.DO_NOTHING, db_column='Tipo_ubicacion')  # Field name made lowercase.
    alias = models.CharField(db_column='Alias', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'ubicaciones'

class RelUbicacionesEquipos(models.Model):
    id_equipo = models.ForeignKey(Equipo, models.DO_NOTHING, db_column='ID_equipo')  # Field name made lowercase.
    id_ubicacion = models.ForeignKey('Ubicaciones', models.DO_NOTHING, db_column='ID_ubicacion')  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'rel_ubicaciones_equipos'
        unique_together = (('id_equipo', 'id_ubicacion'),)

class HistoricoFormatosEditable(models.Model):
    id_formato = models.ForeignKey(Formatos, models.DO_NOTHING, db_column='ID_formato')  # Field name made lowercase.
    creador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Creador')  # Field name made lowercase.
    fecha_edicion = models.DateTimeField(db_column='Fecha_edicion')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'historico_formatos_editable'

class ReservasProcedimiento(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    procedimiento_reservado = models.CharField(db_column='Procedimiento_reservado', max_length=100)  # Field name made lowercase.
    titulo = models.CharField(db_column='Titulo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha = models.DateField(db_column='Fecha')  # Field name made lowercase.
    responsable = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Responsable')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'reservas_procedimiento'

class ContenidoCurso(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre_ponencia = models.CharField(db_column='Nombre_ponencia', max_length=255)  # Field name made lowercase.
    fecha_ponencia = models.DateTimeField(db_column='Fecha_ponencia')  # Field name made lowercase.
    archivo = models.CharField(db_column='Archivo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    ponente = models.ForeignKey('Contacto', models.DO_NOTHING, db_column='Ponente')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'contenido_curso'

class Cursos(models.Model):
    id = models.OneToOneField('Objeto', models.DO_NOTHING, db_column='ID', primary_key=True)  # Field name made lowercase.
    fecha_inicio = models.DateField(db_column='Fecha_inicio')  # Field name made lowercase.
    fecha_fin = models.DateField(db_column='Fecha_fin', blank=True, null=True)  # Field name made lowercase.
    resumen = models.CharField(db_column='Resumen', max_length=255)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=10000, blank=True, null=True)  # Field name made lowercase.
    imagen = models.CharField(db_column='Imagen', max_length=255, blank=True, null=True)  # Field name made lowercase.
    patrocinadores = models.ForeignKey('Entidades', models.DO_NOTHING, db_column='Patrocinadores')  # Field name made lowercase.
    tipo_curso = models.ForeignKey('TipoCurso', models.DO_NOTHING, db_column='Tipo_curso')  # Field name made lowercase.
    horas = models.FloatField(db_column='Horas')  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'cursos'




class TipoCurso(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_curso'

class RelCursoAsistentes(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_curso = models.ForeignKey(Cursos, models.DO_NOTHING, db_column='ID_curso')  # Field name made lowercase.
    id_asistente = models.ForeignKey('Contacto', models.DO_NOTHING, db_column='ID_asistente')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=9)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rel_curso_asistentes'


class RelCursoContenido(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    id_curso = models.ForeignKey(Cursos, models.DO_NOTHING, db_column='ID_curso')  # Field name made lowercase.
    id_contenido = models.ForeignKey(ContenidoCurso, models.DO_NOTHING, db_column='ID_contenido')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rel_curso_contenido'
   

class EstadosNotificaciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'estados_notificaciones'

class Notificacion(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_doc = models.ForeignKey('Objeto', models.DO_NOTHING, db_column='ID_doc')  # Field name made lowercase.
    titulo = models.CharField(db_column='Titulo', max_length=255)  # Field name made lowercase.
    resumen = models.CharField(db_column='Resumen', max_length=10000)  # Field name made lowercase.
    creador = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Creador')  # Field name made lowercase.
    estado_notificacion = models.ForeignKey(EstadosNotificaciones, models.DO_NOTHING, db_column='Estado_notificacion')  # Field name made lowercase.
    fecha = models.DateField(db_column='Fecha') # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'notificacion'

class RelProyectoColaboradores(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_proyecto = models.ForeignKey(Proyecto, models.DO_NOTHING, db_column='ID_proyecto', blank=True, null=True)  # Field name made lowercase.
    id_colaborador = models.ForeignKey(Entidades, models.DO_NOTHING, db_column='ID_colaborador', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rel_proyecto_colaboradores'


class RelProyectoFinanciadores(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_proyecto = models.ForeignKey(Proyecto, models.DO_NOTHING, db_column='id_proyecto')
    id_financiador = models.ForeignKey(EntidadesFinanciadoras, models.DO_NOTHING, db_column='id_financiador')

    class Meta:
        managed = False
        db_table = 'rel_proyecto_financiadores'

class Contacto(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    telefono = models.CharField(db_column='Telefono', max_length=18, blank=True, null=True)  # Field name made lowercase.
    telefono_fijo = models.CharField(db_column='Telefono_fijo', max_length=18, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=255, blank=True, null=True)  # Field name made lowercase.
    info_adicional = models.CharField(db_column='Info_adicional', max_length=255, blank=True, null=True)  # Field name made lowercase.
    id_habilitacion = models.ForeignKey('Habilitaciones', models.DO_NOTHING, db_column='ID_habilitacion')  # Field name made lowercase.
    puesto = models.CharField(db_column='Puesto', max_length=255)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=255)  # Field name made lowercase.
    empresa = models.CharField(db_column='Empresa', max_length=255, blank=True, null=True)  # Field name made lowercase.
    extension = models.CharField(db_column='Extension', max_length=5, blank=True, null=True)  # Field name made lowercase.
    img = models.CharField(db_column='Img', max_length=10, blank=True, null=True)  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', max_length=10, blank=True, null=True)  # Field name made lowercase.
    fecha_nacimiento = models.DateField(db_column='Fecha_nacimiento', blank=True, null=True)  # Field name made lowercase.
    tipo_contacto = models.CharField(db_column='Tipo_contacto', max_length=9)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'contacto'


# DUPLICADO de la tabla AuthUser RENOMBRADA por Miembros conservando su campos
class Miembros(models.Model):
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

# DUPLICADO de la tabla AuthUser RENOMBRADA por Miembros conservando su campos
class Convocantes(models.Model):
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

# DUPLICADO de la tabla AuthUser RENOMBRADA por Secretario conservando su campos
class Secretarios(models.Model):
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

class Acta(models.Model):
    id = models.OneToOneField(Objeto, models.DO_NOTHING, db_column='ID', primary_key=True)   # Field name made lowercase.
    fecha_inicio = models.DateTimeField(db_column='Fecha_inicio')  # Field name made lowercase.
    fecha_cierre = models.DateTimeField(db_column='Fecha_cierre', blank=True, null=True)  # Field name made lowercase.
    convocante = models.ForeignKey('Convocantes', models.DO_NOTHING, db_column='Convocante')  # Field name made lowercase.
    ubicacion = models.CharField(db_column='Ubicacion', max_length=100)  # Field name made lowercase.
    secretario = models.ForeignKey('Secretarios', models.DO_NOTHING, db_column='Secretario')  # Field name made lowercase.
    sesion = models.IntegerField(db_column='Sesion')  # Field name made lowercase.
    consejo = models.CharField(db_column='Consejo', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'acta'

class PuntosYAcuerdos(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    orden = models.IntegerField(db_column='Orden')  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=10)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=10000)  # Field name made lowercase.
    acta_relacionada = models.ForeignKey(Acta, models.DO_NOTHING, db_column='Acta_relacionada')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'puntos_y_acuerdos'

class RelActaMiembros(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_acta = models.ForeignKey(Acta, models.DO_NOTHING, db_column='ID_acta')  # Field name made lowercase.
    id_miembro = models.ForeignKey(Miembros, models.DO_NOTHING, db_column='ID_miembro')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rel_acta_miembros'

''' 
    ---------------------------------------------------------------
        Gestión de stock (fungibles, papelería, reactivos, etc)
    ---------------------------------------------------------------
'''

class UnidadesStock(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'unidades_stock'

class CategoriasStock(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    categoria = models.CharField(db_column='Categoria', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'categorias_stock'       

class Stock(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    item = models.CharField(db_column='Item', max_length=100)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=255, blank=True, null=True)  # Field name made lowercase.
    num_estanteria = models.CharField(db_column='NUM_estanteria', max_length=100, blank=True, null=True)  # Field name made lowercase.
    num_contenedor = models.CharField(db_column='NUM_Contenedor', max_length=100, blank=True, null=True)  # Field name made lowercase.
    id_ubicacion = models.ForeignKey('Ubicaciones', models.DO_NOTHING, db_column='ID_Ubicacion')  # Field name made lowercase.
    unidad = models.ForeignKey('UnidadesStock', models.DO_NOTHING, db_column='Unidad')  # Field name made lowercase.
    cantidad = models.FloatField(db_column='Cantidad')  # Field name made lowercase.
    min_cantidad = models.FloatField(db_column='MIN_Cantidad')  # Field name made lowercase.
    categoria = models.ForeignKey(CategoriasStock, models.DO_NOTHING, db_column='Categoria')  # Field name made lowercase.
    avisado = models.IntegerField(db_column='Avisado', blank=True, null=True)  # Field name made lowercase.
    urgente = models.IntegerField(db_column='Urgente')  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'stock'

class RegistroRetiradaStock(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    item = models.ForeignKey('Stock', models.DO_NOTHING, db_column='Item')  # Field name made lowercase.
    cantidad = models.FloatField(db_column='Cantidad')  # Field name made lowercase.
    fecha = models.DateField(db_column='Fecha')  # Field name made lowercase.
    empleado = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Empleado')  # Field name made lowercase.
    ubicacion = models.ForeignKey('Ubicaciones', models.DO_NOTHING, db_column='Ubicacion')  # Field name made lowercase.
    error = models.IntegerField(db_column='Error', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'registro_retirada_stock'


class RelStockProveedores(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fecha = models.DateField(db_column='Fecha', blank=True, null=True)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste', blank=True, null=True)  # Field name made lowercase.
    proveedor = models.ForeignKey(Proveedor, models.DO_NOTHING, db_column='Proveedor')  # Field name made lowercase.
    item = models.ForeignKey('Stock', models.DO_NOTHING, db_column='Item')  # Field name made lowercase.  
    unidad = models.ForeignKey('UnidadesStock', models.DO_NOTHING, db_column='Unidad')  # Field name made lowercase.
    cantidad = models.FloatField(db_column='Cantidad')  # Field name made lowercase.
    coste_unitario= models.FloatField(db_column='Coste_unitario', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rel_stock_proveedores'

class TiposEventos(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=20)  # Field name made lowercase.
    color = models.CharField(db_column='Color', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipos_eventos'
        
class TipoPeriodicidad(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    periodicidad = models.CharField(db_column='Periodicidad', max_length=12)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_periodicidad'
        
class TareasProgramadas(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_evento = models.ForeignKey('Eventos', models.DO_NOTHING, db_column='ID_evento')  # Field name made lowercase.
    id_objeto = models.ForeignKey(Objeto, models.DO_NOTHING, db_column='ID_objeto')  # Field name made lowercase.
    fecha_inicial = models.DateTimeField(db_column='Fecha_inicial')  # Field name made lowercase.
    fecha_ultimo_mantenimiento = models.DateTimeField(db_column='Fecha_ultimo_mantenimiento', blank=True, null=True)  # Field name made lowercase.
    fecha_proximo_mantenimiento = models.DateTimeField(db_column='Fecha_proximo_mantenimiento', blank=True, null=True)  # Field name made lowercase.
    observaciones = models.CharField(db_column='Observaciones', max_length=1000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tareas_programadas'

class EstadoTareas(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=25)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'estado_tareas'

class RegistroTareaProgramada(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    empleado = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='Empleado', blank=True, null=True)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha', blank=True, null=True)  # Field name made lowercase.
    fecha_programada = models.DateTimeField(db_column='Fecha_programada')  # Field name made lowercase.
    conforme = models.IntegerField(db_column='Conforme', blank=True, null=True)  # Field name made lowercase.
    datos = models.CharField(db_column='Datos', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    observaciones = models.CharField(db_column='Observaciones', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    estado = models.ForeignKey(EstadoTareas, models.DO_NOTHING, db_column='Estado')  # Field name made lowercase.
    id_tarea_programada = models.ForeignKey('TareasProgramadas', models.DO_NOTHING, db_column='ID_tarea_programada')  # Field name made lowercase.
    id_formato = models.ForeignKey(Formatos, models.DO_NOTHING, db_column='ID_formato', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'registro_tarea_programada'



class Periodicidad(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    cantidad = models.IntegerField(db_column='Cantidad')  # Field name made lowercase.
    unidad = models.CharField(db_column='Unidad', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'periodicidad'


class Eventos(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    tipo_periodicidad = models.ForeignKey('TipoPeriodicidad', models.DO_NOTHING, db_column='Tipo_periodicidad')  # Field name made lowercase.
    tipo_evento = models.ForeignKey('TiposEventos', models.DO_NOTHING, db_column='Tipo_evento')  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=255)  # Field name made lowercase.
    procedimiento_asociado = models.ForeignKey('Procedimiento', models.DO_NOTHING, db_column='Procedimiento_asociado', blank=True, null=True)  # Field name made lowercase.
    datos = models.CharField(db_column='Datos', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    periodicidad = models.ForeignKey('Periodicidad', models.DO_NOTHING, db_column='Periodicidad')  # Field name made lowercase.
    estado = models.ForeignKey(Estado, models.DO_NOTHING, db_column='Estado')  # Field name made lowercase.
    formato_asociado = models.ForeignKey('Formatos', models.DO_NOTHING, db_column='Formato_asociado', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'eventos'