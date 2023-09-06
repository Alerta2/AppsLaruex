# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from ckeditor.fields import RichTextField, RichTextFormField
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField, RichTextFormField


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


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'

class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class WeblaruexContacto(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=100)  # Field name made lowercase.
    asunto = models.CharField(db_column='ASUNTO', max_length=100)  # Field name made lowercase.
    mensaje = models.CharField(db_column='MENSAJE', max_length=500)  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='FECHA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_contacto'

class WeblaruexEmpleados(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    imagen = models.CharField(db_column='IMAGEN', max_length=100)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    grupo = models.CharField(db_column='GRUPO', max_length=50)  # Field name made lowercase.
    puesto = models.CharField(db_column='PUESTO', max_length=70)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_empleados'


class WeblaruexInvestigaciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    imagen = models.CharField(db_column='Imagen', max_length=100, blank=True, null=True)  # Field name made lowercase.
    fecha = models.CharField(db_column='Fecha', max_length=30)  # Field name made lowercase.
    revista = models.CharField(db_column='Revista', max_length=100, blank=True, null=True)  # Field name made lowercase.
    autor = models.CharField(db_column='Autor', max_length=100, blank=True, null=True)  # Field name made lowercase.
    entidad_financiadora = models.CharField(db_column='Entidad financiadora', max_length=200, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    titulo = models.CharField(db_column='Titulo', max_length=300, blank=True, null=True)  # Field name made lowercase.
    resumen = models.CharField(db_column='Resumen', max_length=9999)  # Field name made lowercase.
    informacion = models.CharField(db_column='Informacion', max_length=9999)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=100, blank=True, null=True)  # Field name made lowercase.
    fecha_final = models.CharField(db_column='Fecha final', max_length=30, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    localizacion = models.CharField(db_column='Localizacion', max_length=200, blank=True, null=True)  # Field name made lowercase.
    seccion = models.CharField(db_column='Seccion', max_length=30, blank=True, null=True)  # Field name made lowercase.
    enlace = models.CharField(db_column='Enlace', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_investigaciones'


class WeblaruexContenidocurso(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_curso = models.CharField(db_column='ID Curso', max_length=20)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    fecha_contenido = models.DateTimeField(db_column='Fecha Contenido')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    nombre = models.CharField(db_column='Nombre', max_length=300)  # Field name made lowercase.
    ponente = models.CharField(db_column='Ponente', max_length=300) 
    descripcion = models.CharField(db_column='Descripcion', max_length=9999)  # Field name made lowercase.
    url = models.CharField(db_column='URL', max_length=100)  # Field name made lowercase.
    codigo = models.CharField(db_column='Codigo', max_length=40)  # Field name made lowercase.
    visible = models.IntegerField(db_column='Visible')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_contenidocurso'


class WeblaruexCursos(models.Model):
    id = models.CharField(db_column='ID', max_length=20, primary_key=True)  # Field name made lowercase.
    fecha_inicio = models.DateField(db_column='Fecha Inicio')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    fecha_fin = models.DateField(db_column='Fecha Fin')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    titulo = models.CharField(db_column='Titulo', max_length=100)  # Field name made lowercase.
    resumen = models.CharField(db_column='Resumen', max_length=300)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=9999)  # Field name made lowercase.
    triptico = models.CharField(db_column='Triptico', max_length=100)  # Field name made lowercase.
    imagen = models.CharField(db_column='Imagen', max_length=100)  # Field name made lowercase.
    inscripciones = models.CharField(db_column='Inscripciones', max_length=1)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=60)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=20)  # Field name made lowercase.
    mapa = models.CharField(db_column='Mapa', max_length=500)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_cursos'

class WeblaruexStreaming(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_curso = models.CharField(db_column='ID Curso', max_length=20)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    fecha = models.DateTimeField(db_column='Fecha')  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=300)  # Field name made lowercase.
    url = models.CharField(db_column='URL', max_length=100)  # Field name made lowercase.
    visible = models.IntegerField(db_column='Visible')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_streaming'


class CategoriasNoticias(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    categoria = models.CharField(db_column='Categoria', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'categorias_noticias'

class WeblaruexNoticias(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    img_portada = models.CharField(db_column='IMG_PORTADA', max_length=90)  # Field name made lowercase.
    n_comentarios = models.IntegerField(db_column='N_COMENTARIOS')  # Field name made lowercase.
    fecha = models.DateField(db_column='FECHA')  # Field name made lowercase.
    titulo = models.CharField(db_column='TITULO', max_length=200)  # Field name made lowercase.
    resumen = RichTextField(db_column='RESUMEN', max_length=9999)  # Field name made lowercase.
    noticia = RichTextField(db_column='NOTICIA', max_length=9999)  # Field name made lowercase.
    categoria = models.CharField(db_column='CATEGORIA', max_length=90)  # Field name made lowercase.
    categoria_noticia = models.ForeignKey(CategoriasNoticias, models.DO_NOTHING, db_column='CATEGORIA_NOTICIA', blank=True, null=True)  # Field name made lowercase.
    meta_descripcion = models.CharField(db_column='META_DESCRIPTION', max_length=150)  # Field name made lowercase.
    meta_keywords = models.CharField(db_column='META_KEYWORDS', max_length=200)  # Field name made lowercase.
    visible = models.IntegerField(db_column='VISIBLE', max_length=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_noticias'


class WeblaruexPatrocinadorescurso(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_curso = models.CharField(db_column='ID Curso', max_length=20)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    imagen = models.CharField(db_column='Imagen', max_length=300)  # Field name made lowercase.
    alt = models.CharField(db_column='Alt', max_length=300)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_patrocinadorescurso'


class WeblaruexResponsables(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    imagen = models.CharField(db_column='IMAGEN', max_length=100)  # Field name made lowercase.
    frase = models.CharField(db_column='FRASE', max_length=150, blank=True, null=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=20)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=100)  # Field name made lowercase.
    cargo = models.CharField(db_column='CARGO', max_length=200)  # Field name made lowercase.
    apartado = models.CharField(db_column='APARTADO', max_length=200)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_responsables'

class WeblaruexServicios(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=200)  # Field name made lowercase.
    imagen = models.CharField(db_column='IMAGEN', max_length=200)  # Field name made lowercase.
    grupo = models.CharField(db_column='GRUPO', max_length=100)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=200)  # Field name made lowercase.
    enlace = models.CharField(db_column='ENLACE', max_length=200)  # Field name made lowercase.
    categoria = models.CharField(db_column='CATEGORIA', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_servicios'


class WeblaruexSliders(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    pagina = models.CharField(db_column='PAGINA', max_length=30)  # Field name made lowercase.
    titulo = models.CharField(db_column='TITULO', max_length=100)  # Field name made lowercase.
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=600, blank=True, null=True)  # Field name made lowercase.
    enlace = models.CharField(db_column='ENLACE', max_length=300, blank=True, null=True)  # Field name made lowercase.
    imagen_slider = models.CharField(db_column='IMAGEN_SLIDER', max_length=300)  # Field name made lowercase.
    slider_principal = models.IntegerField(db_column='SLIDER_PRINCIPAL')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_sliders'




class WeblaruexFormularioCursos(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_curso = models.CharField(db_column='ID CURSO', max_length=30)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=300)  # Field name made lowercase.
    apellidos = models.CharField(db_column='APELLIDOS', max_length=300)  # Field name made lowercase.
    dni = models.CharField(db_column='DNI', max_length=20)  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=20)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=50)  # Field name made lowercase.
    grupo_investigacion = models.CharField(db_column='GRUPO INVESTIGACION', max_length=300)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    curriculum = models.CharField(db_column='CURRICULUM', max_length=900)  # Field name made lowercase.
    fecha = models.DateField(db_column='FECHA')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_formulario_cursos'

class WeblaruexAcreditaciones(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=100)  # Field name made lowercase.
    archivo = models.CharField(db_column='Archivo', max_length=100)  # Field name made lowercase.
    seccion = models.CharField(db_column='Seccion', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_acreditaciones'


class WeblaruexMedidas(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=20)  # Field name made lowercase.
    resumen_tarjeta = models.CharField(db_column='RESUMEN_TARJETA', max_length=100)  # Field name made lowercase.
    imagen = models.CharField(db_column='IMAGEN', max_length=20)  # Field name made lowercase.
    resumen_medida = models.CharField(db_column='RESUMEN_MEDIDA', max_length=200)  # Field name made lowercase.
    descripcion_medida = models.CharField(db_column='DESCRIPCION_MEDIDA', max_length=9999)  # Field name made lowercase.
    meta_descripcion = models.CharField(db_column='META_DESCRIPCION', max_length=150)  # Field name made lowercase.
    meta_keywords = models.CharField(db_column='META_KEYWORDS', max_length=200)  # Field name made lowercase.
    norma = models.CharField(db_column='NORMA', max_length=200)  # Field name made lowercase.
    url = models.CharField(db_column='URL', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'weblaruex_medidas'

