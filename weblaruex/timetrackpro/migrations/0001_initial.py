# Generated by Django 3.2.19 on 2023-08-16 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Archivos',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('justificantes_adicionales', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'archivos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ArchivosLeidos',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('ruta', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'archivos_leidos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
            ],
            options={
                'db_table': 'auth_group',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthGroupPermissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'auth_group_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('codename', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'auth_permission',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.IntegerField()),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.CharField(max_length=254)),
                ('is_staff', models.IntegerField()),
                ('is_active', models.IntegerField()),
                ('date_joined', models.DateTimeField()),
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserGroups',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Duraciones',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('unidad', models.CharField(blank=True, max_length=255, null=True)),
                ('categoria', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'duraciones',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Empleados',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'empleados',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EstadosSolicitudes',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'estados_solicitudes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MaquinaControlAsistencia',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('localizacion', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'maquina_control_asistencia',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PeriodoAntelacion',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('unidad', models.CharField(blank=True, max_length=255, null=True)),
                ('categoria', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'periodo_antelacion',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Permisos',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('acreditar', models.IntegerField(blank=True, null=True)),
                ('doc_necesaria', models.CharField(blank=True, max_length=255, null=True)),
                ('legislacion_aplicable', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'permisos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RegistroAusenciasAceptadas',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('id_registro_solicitud', models.IntegerField(blank=True, null=True)),
                ('id_empleado', models.IntegerField(blank=True, null=True)),
                ('fecha_inicio', models.DateTimeField()),
                ('fecha_fin', models.DateTimeField()),
                ('id_estado', models.IntegerField(blank=True, null=True)),
                ('archivo_solicitud', models.CharField(blank=True, max_length=255, null=True)),
                ('archivo_justificante', models.CharField(blank=True, max_length=255, null=True)),
                ('funciones_a_cubrir', models.CharField(blank=True, max_length=255, null=True)),
                ('id_empleado_sustituto', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'registro_ausencias_aceptadas',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Registros',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre_empleado', models.CharField(blank=True, max_length=255, null=True)),
                ('hora', models.DateTimeField()),
                ('maquina', models.IntegerField(blank=True, null=True)),
                ('remoto', models.IntegerField(blank=True, null=True)),
                ('id_archivo_leido', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'registros',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RegitroSolicitudes',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('id_empleado', models.IntegerField(blank=True, null=True)),
                ('fecha_inicio', models.DateTimeField()),
                ('fecha_fin', models.DateTimeField()),
                ('id_permisos', models.IntegerField(blank=True, null=True)),
                ('id_estado', models.IntegerField(blank=True, null=True)),
                ('motivo_solicitud_rechazo', models.CharField(blank=True, max_length=255, null=True)),
                ('archivo_solicitud', models.CharField(blank=True, max_length=255, null=True)),
                ('funciones_a_cubrir', models.CharField(blank=True, max_length=255, null=True)),
                ('id_empleado_sustituto', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'regitro_solicitudes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RegitroSolicitudViajes',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('id_empleado', models.IntegerField(blank=True, null=True)),
                ('fecha_inicio', models.DateTimeField()),
                ('fecha_fin', models.DateTimeField()),
                ('id_estado', models.IntegerField(blank=True, null=True)),
                ('motivo_solicitud_rechazo', models.CharField(blank=True, max_length=255, null=True)),
                ('archivo_solicitud', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'regitro_solicitud_viajes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RegitroViajesAceptados',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('id_registro_solicitud', models.IntegerField(blank=True, null=True)),
                ('id_empleado', models.IntegerField(blank=True, null=True)),
                ('dieta', models.IntegerField(blank=True, null=True)),
                ('ruta_solicitud', models.CharField(blank=True, max_length=255, null=True)),
                ('ruta_dieta', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'regitro_viajes_aceptados',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RelEmpleadosUsuarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'rel_empleados_usuarios',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RelJornadaEmpleados',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('id_empleado', models.IntegerField(blank=True, null=True)),
                ('fecha_inicio', models.DateTimeField()),
                ('motivo', models.CharField(blank=True, max_length=255, null=True)),
                ('horas_semanales', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'rel_jornada_empleados',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RelJustificantesEmpleados',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('id_ausencia', models.IntegerField(blank=True, null=True)),
                ('id_empleado', models.IntegerField(blank=True, null=True)),
                ('justificante', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'rel_justificantes_empleados',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Usuarios',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'usuarios',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='navBar',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, db_column='Nombre', max_length=255, null=True)),
                ('icono', models.CharField(db_column='Icono', max_length=255)),
                ('url', models.CharField(db_column='URL', max_length=255)),
                ('desplegable', models.IntegerField(blank=True, db_column='Desplegable', null=True)),
                ('padre', models.IntegerField(blank=True, db_column='Padre', null=True)),
            ],
            options={
                'db_table': 'nav_bar',
                'managed': True,
            },
        ),
    ]
