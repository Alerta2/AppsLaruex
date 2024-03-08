# Generated by Django 3.1.2 on 2022-02-24 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestionmuestras', '0002_relacionalicuotasmedidas_relaciondeterminacionesprogramadas_relacionhistoricoanaliticascompuestas'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedidasPredefinidas',
            fields=[
                ('paquetemedidas', models.CharField(db_column='paqueteMedidas', max_length=30, primary_key=True, serialize=False)),
                ('nombrepaquete', models.CharField(blank=True, db_column='nombrePaquete', max_length=60, null=True)),
                ('analisis', models.CharField(blank=True, max_length=60, null=True)),
            ],
            options={
                'db_table': 'medidas_predefinidas',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RelacionDeterminacionesTratamientos',
            fields=[
                ('id_determinacion', models.OneToOneField(db_column='ID_DETERMINACION', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='gestionmuestras.determinaciones')),
                ('por_defecto', models.IntegerField(db_column='POR_DEFECTO')),
            ],
            options={
                'db_table': 'relacion_determinaciones_tratamientos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RelacionTipoDeterminacionParametros',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('valor_recomendado', models.CharField(blank=True, db_column='VALOR_RECOMENDADO', max_length=30, null=True)),
                ('formula', models.CharField(blank=True, db_column='FORMULA', max_length=30, null=True)),
            ],
            options={
                'db_table': 'relacion_tipo_determinacion_parametros',
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='AlmacenEmailRecepcion',
        ),
        migrations.DeleteModel(
            name='AnalisisTablas',
        ),
        migrations.DeleteModel(
            name='Ausencias',
        ),
        migrations.DeleteModel(
            name='Balanzas',
        ),
        migrations.DeleteModel(
            name='CalibracionQuantulus',
        ),
        migrations.DeleteModel(
            name='CantidadesAgregadasRadioDesecacion',
        ),
        migrations.DeleteModel(
            name='Conductivimetros',
        ),
        migrations.DeleteModel(
            name='DeterminacionElementosEstables',
        ),
        migrations.DeleteModel(
            name='FechasDeterminacionProgramada',
        ),
        migrations.DeleteModel(
            name='HistoricoAlicuotasControles',
        ),
        migrations.DeleteModel(
            name='InfoPrograma',
        ),
        migrations.DeleteModel(
            name='InformacionMemorias',
        ),
        migrations.DeleteModel(
            name='Isotopos',
        ),
        migrations.DeleteModel(
            name='Laboratorios',
        ),
        migrations.DeleteModel(
            name='ParametrosAnaliticas',
        ),
        migrations.DeleteModel(
            name='Phmetros',
        ),
        migrations.DeleteModel(
            name='Presupuestos',
        ),
        migrations.DeleteModel(
            name='RadionucleidosTrazadores',
        ),
        migrations.DeleteModel(
            name='RegistroAsistencia',
        ),
        migrations.RemoveField(
            model_name='relacionanalisisgamma',
            name='id_histo_muestra_analitica',
        ),
        migrations.RemoveField(
            model_name='relacionanalisistablas',
            name='id_analisis',
        ),
        migrations.DeleteModel(
            name='RelacionControlesTratamientos',
        ),
        migrations.DeleteModel(
            name='RelacionDetectoresAlfabeta',
        ),
        migrations.DeleteModel(
            name='RelacionDeterminacionesProgramadas',
        ),
        migrations.DeleteModel(
            name='RelacionHistoricoAnaliticasCompuestas',
        ),
        migrations.DeleteModel(
            name='RelacionIncidencias',
        ),
        migrations.DeleteModel(
            name='RelacionInformesCorreccion',
        ),
        migrations.DeleteModel(
            name='RelacionInformesGenerados',
        ),
        migrations.DeleteModel(
            name='RelacionKBetaBetaresto',
        ),
        migrations.DeleteModel(
            name='RelacionMuestraAsalvo',
        ),
        migrations.DeleteModel(
            name='RelacionMuestraProgramadaFecha',
        ),
        migrations.DeleteModel(
            name='RelacionPresupuestosAnalisis',
        ),
        migrations.DeleteModel(
            name='RelacionResultadosSeleccionados',
        ),
        migrations.DeleteModel(
            name='RelacionResultadosSeleccionadosCorreccion',
        ),
        migrations.DeleteModel(
            name='RelacionSuministradorSuministro',
        ),
        migrations.DeleteModel(
            name='RelacionTipoDeterminacionParamRequer',
        ),
        migrations.DeleteModel(
            name='RelacionTipoMuestraDeterminacionCantidad',
        ),
        migrations.DeleteModel(
            name='RelacionTratamientoAlfabetaResultado',
        ),
        migrations.DeleteModel(
            name='RelacionTratamientoRegistroResultado',
        ),
        migrations.DeleteModel(
            name='RelacionTratamientoResultadoIcp',
        ),
        migrations.DeleteModel(
            name='ReportAsistencia',
        ),
        migrations.DeleteModel(
            name='ReportRealDecretoDit',
        ),
        migrations.DeleteModel(
            name='ReportRealDecretoGenerico',
        ),
        migrations.DeleteModel(
            name='ReportRealDecretoMedidas',
        ),
        migrations.DeleteModel(
            name='ReportSemana',
        ),
        migrations.DeleteModel(
            name='SituacionRecepcion',
        ),
        migrations.DeleteModel(
            name='UsuariosAsistencia',
        ),
        migrations.DeleteModel(
            name='ValoresAnalisisPresupuesto',
        ),
        migrations.DeleteModel(
            name='Analiticas',
        ),
        migrations.DeleteModel(
            name='RelacionAnalisisGamma',
        ),
        migrations.DeleteModel(
            name='RelacionAnalisisTablas',
        ),
    ]
