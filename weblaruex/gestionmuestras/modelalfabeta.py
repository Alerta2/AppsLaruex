# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Actividadeficienciaalfa(models.Model):
    medida = models.OneToOneField('Medida', models.DO_NOTHING, db_column='Medida_ID', primary_key=True)  # Field name made lowercase.
    actividad = models.FloatField(db_column='Actividad')  # Field name made lowercase.
    errorrecuento = models.FloatField(db_column='ErrorRecuento')  # Field name made lowercase.
    actividadminimadetectable = models.FloatField(db_column='ActividadMinimaDetectable')  # Field name made lowercase.
    incertidumbrecombinada = models.FloatField(db_column='IncertidumbreCombinada')  # Field name made lowercase.
    ef0 = models.FloatField(db_column='Ef0')  # Field name made lowercase.
    c = models.FloatField(db_column='C', blank=True, null=True)  # Field name made lowercase.
    x = models.FloatField(db_column='X', blank=True, null=True)  # Field name made lowercase.
    origenx = models.CharField(db_column='OrigenX', max_length=22, blank=True, null=True)  # Field name made lowercase.
    efm = models.FloatField(db_column='Efm')  # Field name made lowercase.
    nalfablanco = models.FloatField(db_column='NAlfaBlanco')  # Field name made lowercase.
    tblanco = models.IntegerField(db_column='tBlanco')  # Field name made lowercase.
    f = models.FloatField(blank=True, null=True)
    fechamuestra = models.DateTimeField(db_column='FechaMuestra', blank=True, null=True)  # Field name made lowercase.
    t12 = models.CharField(db_column='T12', max_length=45, blank=True, null=True)  # Field name made lowercase.
    t12tipo = models.CharField(db_column='T12Tipo', max_length=38, blank=True, null=True)  # Field name made lowercase.
    v = models.FloatField(db_column='V')  # Field name made lowercase.
    rq = models.FloatField(db_column='Rq')  # Field name made lowercase.
    erroref0 = models.FloatField(db_column='ErrorEf0')  # Field name made lowercase.
    errorv = models.FloatField(db_column='ErrorV')  # Field name made lowercase.
    uc = models.FloatField()
    s = models.FloatField()
    k1 = models.FloatField()
    k2 = models.FloatField()

    class Meta:
        managed = False
        db_table = 'actividadeficienciaalfa'


class Actividadeficienciabeta(models.Model):
    medida = models.CharField(db_column='Medida_ID', max_length=60, primary_key=True)  # Field name made lowercase.
    actividad = models.FloatField(db_column='Actividad')  # Field name made lowercase.
    errorrecuento = models.FloatField(db_column='ErrorRecuento')  # Field name made lowercase.
    actividadminimadetectable = models.FloatField(db_column='ActividadMinimaDetectable')  # Field name made lowercase.
    incertidumbrecombinada = models.FloatField(db_column='IncertidumbreCombinada')  # Field name made lowercase.
    ef0 = models.FloatField(db_column='Ef0')  # Field name made lowercase.
    c = models.FloatField(db_column='C', blank=True, null=True)  # Field name made lowercase.
    x = models.FloatField(db_column='X', blank=True, null=True)  # Field name made lowercase.
    origenx = models.CharField(db_column='OrigenX', max_length=22, blank=True, null=True)  # Field name made lowercase.
    efm = models.FloatField(db_column='Efm')  # Field name made lowercase.
    nalfablanco = models.FloatField(db_column='NAlfaBlanco')  # Field name made lowercase.
    nbetablanco = models.FloatField(db_column='NBetaBlanco')  # Field name made lowercase.
    tblanco = models.IntegerField(db_column='tBlanco')  # Field name made lowercase.
    f = models.FloatField(blank=True, null=True)
    fechamuestra = models.DateTimeField(db_column='FechaMuestra', blank=True, null=True)  # Field name made lowercase.
    t12 = models.CharField(db_column='T12', max_length=45, blank=True, null=True)  # Field name made lowercase.
    t12tipo = models.CharField(db_column='T12Tipo', max_length=38, blank=True, null=True)  # Field name made lowercase.
    v = models.FloatField(db_column='V')  # Field name made lowercase.
    rq = models.FloatField(db_column='Rq')  # Field name made lowercase.
    erroref0 = models.FloatField(db_column='ErrorEf0')  # Field name made lowercase.
    errorv = models.FloatField(db_column='ErrorV')  # Field name made lowercase.
    uc = models.FloatField()
    s = models.FloatField()
    k1 = models.FloatField()
    k2 = models.FloatField()
    crosstalk = models.FloatField(db_column='Crosstalk')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'actividadeficienciabeta'


class Alicuota(models.Model):
    codigoreducido = models.CharField(db_column='CodigoReducido', primary_key=True, max_length=45)  # Field name made lowercase.
    muestra_clave = models.ForeignKey('Muestra', models.DO_NOTHING, db_column='Muestra_Clave', blank=True, null=True)  # Field name made lowercase.
    tipoanalitica = models.ForeignKey('Tipoanalitica', models.DO_NOTHING, db_column='TipoAnalitica_ID', blank=True, null=True)  # Field name made lowercase.
    fraccion = models.CharField(db_column='Fraccion', max_length=7, blank=True, null=True)  # Field name made lowercase.
    volumenoptimo = models.FloatField(db_column='VolumenOptimo', blank=True, null=True)  # Field name made lowercase.
    volumen = models.FloatField(db_column='Volumen', blank=True, null=True)  # Field name made lowercase.
    volumenerror = models.FloatField(db_column='VolumenError', blank=True, null=True)  # Field name made lowercase.
    deposito = models.FloatField(db_column='Deposito', blank=True, null=True)  # Field name made lowercase.
    espesormasico = models.FloatField(db_column='EspesorMasico', blank=True, null=True)  # Field name made lowercase.
    rendimientoquimico = models.FloatField(db_column='RendimientoQuimico', blank=True, null=True)  # Field name made lowercase.
    muestraaceptada = models.CharField(db_column='MuestraAceptada', max_length=5, blank=True, null=True)  # Field name made lowercase.
    fechafinpreparacion = models.DateField(db_column='FechaFinPreparacion', blank=True, null=True)  # Field name made lowercase.
    tipoblanco = models.ForeignKey('Tipoblanco', models.DO_NOTHING, db_column='TipoBlanco_ID', blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=31)  # Field name made lowercase.
    actividad = models.FloatField(db_column='Actividad', blank=True, null=True)  # Field name made lowercase.
    radionucleido = models.ForeignKey('Radionucleido', models.DO_NOTHING, db_column='Radionucleido_ID', blank=True, null=True)  # Field name made lowercase.
    factoreficiencia = models.FloatField(db_column='FactorEficiencia', blank=True, null=True)  # Field name made lowercase.
    analista = models.ForeignKey('Analista', models.DO_NOTHING, db_column='Analista_ID', blank=True, null=True)  # Field name made lowercase.
    fechaseparacionradioquimica = models.DateField(db_column='FechaSeparacionRadioquimica', blank=True, null=True)  # Field name made lowercase.
    id = models.CharField(db_column='ID', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'alicuota'


class Analista(models.Model):
    nombre = models.CharField(db_column='Nombre', primary_key=True, max_length=45)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=45)  # Field name made lowercase.
    administrador = models.CharField(db_column='Administrador', max_length=5)  # Field name made lowercase.
    acceso = models.CharField(db_column='Acceso', max_length=5, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'analista'

class AnalistaIDSalvado(models.Model):
    nombre = models.CharField(db_column='Nombre', primary_key=True, max_length=45)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=45)  # Field name made lowercase.
    administrador = models.CharField(db_column='Administrador', max_length=5)  # Field name made lowercase.
    acceso = models.CharField(db_column='Acceso', max_length=5, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'analista'


class Analiticaprogramada(models.Model):
    tipoanalitica = models.ForeignKey('Tipoanalitica', models.DO_NOTHING, db_column='TipoAnalitica_ID')  # Field name made lowercase.
    muestra_clave = models.ForeignKey('Muestra', models.DO_NOTHING, db_column='Muestra_Clave')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'analiticaprogramada'


class Ciclo(models.Model):
    nciclo = models.IntegerField(db_column='NCiclo', primary_key=True)  # Field name made lowercase.
    medida = models.ForeignKey('Medida', models.DO_NOTHING, db_column='Medida_ID')  # Field name made lowercase.
    alfa = models.FloatField(db_column='Alfa', blank=True, null=True)  # Field name made lowercase.
    beta = models.FloatField(db_column='Beta', blank=True, null=True)  # Field name made lowercase.
    tiempo = models.IntegerField(db_column='Tiempo', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ciclo'
        unique_together = (('nciclo', 'medida'),)


class Configuracion(models.Model):
    parametro = models.CharField(db_column='Parametro', primary_key=True, max_length=45)  # Field name made lowercase.
    valor = models.FloatField(db_column='Valor')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'configuracion'


class Configuracionexpresiones(models.Model):
    parametro = models.CharField(db_column='Parametro', primary_key=True, max_length=10)  # Field name made lowercase.
    valor = models.FloatField(db_column='Valor')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'configuracionexpresiones'


class Configuracionmoduloestroncio(models.Model):
    parametro = models.CharField(db_column='Parametro', primary_key=True, max_length=45)  # Field name made lowercase.
    valor = models.CharField(db_column='Valor', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'configuracionmoduloestroncio'


class Configuracionmodulopotasio(models.Model):
    parametro = models.CharField(db_column='Parametro', primary_key=True, max_length=45)  # Field name made lowercase.
    valor = models.CharField(db_column='Valor', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'configuracionmodulopotasio'


class Configuracionmoduloradio(models.Model):
    parametro = models.CharField(db_column='Parametro', primary_key=True, max_length=45)  # Field name made lowercase.
    valor = models.CharField(db_column='Valor', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'configuracionmoduloradio'


class Contador(models.Model):
    nombre = models.CharField(db_column='Nombre', primary_key=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'contador'


class Curva(models.Model):
    nombre = models.CharField(db_column='Nombre', primary_key=True, max_length=45)  # Field name made lowercase.
    factorcorrecciont12 = models.FloatField(db_column='FactorCorreccionT12', blank=True, null=True)  # Field name made lowercase.
    factorcorrecciont12tipo = models.CharField(db_column='FactorCorreccionT12Tipo', max_length=38, blank=True, null=True)  # Field name made lowercase.
    parametrox = models.CharField(db_column='ParametroX', max_length=22, blank=True, null=True)  # Field name made lowercase.
    crosstalkradionucleido = models.ForeignKey('Radionucleido', models.DO_NOTHING, db_column='CrosstalkRadionucleido', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'curva'


class Maquina(models.Model):
    nombre = models.CharField(db_column='Nombre', primary_key=True, max_length=45)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=8)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'maquina'


class Maquinaberthold(models.Model):
    maquina_nombre = models.OneToOneField(Maquina, models.DO_NOTHING, db_column='Maquina_Nombre', primary_key=True)  # Field name made lowercase.
    contador1 = models.CharField(db_column='Contador1', max_length=4)  # Field name made lowercase.
    contador2 = models.CharField(db_column='Contador2', max_length=4)  # Field name made lowercase.
    contador3 = models.CharField(db_column='Contador3', max_length=4)  # Field name made lowercase.
    contador4 = models.CharField(db_column='Contador4', max_length=4)  # Field name made lowercase.
    contador5 = models.CharField(db_column='Contador5', max_length=4)  # Field name made lowercase.
    contador6 = models.CharField(db_column='Contador6', max_length=4)  # Field name made lowercase.
    contador7 = models.CharField(db_column='Contador7', max_length=4)  # Field name made lowercase.
    contador8 = models.CharField(db_column='Contador8', max_length=4)  # Field name made lowercase.
    contador9 = models.CharField(db_column='Contador9', max_length=4)  # Field name made lowercase.
    contador10 = models.CharField(db_column='Contador10', max_length=4)  # Field name made lowercase.
    puerto = models.IntegerField(db_column='Puerto')  # Field name made lowercase.
    baudrate = models.IntegerField(db_column='BaudRate')  # Field name made lowercase.
    databits = models.CharField(db_column='DataBits', max_length=7)  # Field name made lowercase.
    stopbits = models.CharField(db_column='StopBits', max_length=7)  # Field name made lowercase.
    parity = models.CharField(db_column='Parity', max_length=24)  # Field name made lowercase.
    flowcontrol = models.CharField(db_column='FlowControl', max_length=22)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'maquinaberthold'


class Medida(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=200)  # Field name made lowercase.
    contador = models.ForeignKey(Contador, models.DO_NOTHING, db_column='Contador_ID')  # Field name made lowercase.
    alicuota_codigoreducido = models.ForeignKey(Alicuota, models.DO_NOTHING, db_column='Alicuota_CodigoReducido')  # Field name made lowercase.
    fecha = models.DateTimeField(db_column='Fecha', blank=True, null=True)  # Field name made lowercase.
    alfa = models.FloatField(db_column='Alfa', blank=True, null=True)  # Field name made lowercase.
    alfa_desv = models.FloatField(db_column='Alfa_Desv', blank=True, null=True)  # Field name made lowercase.
    beta = models.FloatField(db_column='Beta', blank=True, null=True)  # Field name made lowercase.
    beta_desv = models.FloatField(db_column='Beta_Desv', blank=True, null=True)  # Field name made lowercase.
    tiempo = models.IntegerField(db_column='Tiempo', blank=True, null=True)  # Field name made lowercase.
    eficiencia = models.FloatField(db_column='Eficiencia', blank=True, null=True)  # Field name made lowercase.
    crosstalk = models.FloatField(db_column='Crosstalk', blank=True, null=True)  # Field name made lowercase.
    analista = models.ForeignKey(Analista, models.DO_NOTHING, db_column='Analista_ID', blank=True, null=True)  # Field name made lowercase.
    analista_id_salvado = models.ForeignKey(AnalistaIDSalvado, models.DO_NOTHING, db_column='Analista_ID_Salvado', blank=True, null=True)  # Field name made lowercase.
    valida = models.CharField(db_column='Valida', max_length=5, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'medida'


class Medidaestroncio(models.Model):
    medida = models.OneToOneField(Medida, models.DO_NOTHING, db_column='Medida_ID', primary_key=True)  # Field name made lowercase.
    alfa = models.FloatField(db_column='Alfa')  # Field name made lowercase.
    alfa_desv = models.FloatField(db_column='Alfa_Desv')  # Field name made lowercase.
    beta = models.FloatField(db_column='Beta')  # Field name made lowercase.
    beta_desv = models.FloatField(db_column='Beta_Desv')  # Field name made lowercase.
    recuentobetan90 = models.FloatField(db_column='RecuentoBetaN90')  # Field name made lowercase.
    recuentobetan90error = models.FloatField(db_column='RecuentoBetaN90Error')  # Field name made lowercase.
    recuentobetan89 = models.FloatField(db_column='RecuentoBetaN89')  # Field name made lowercase.
    recuentobetan89error = models.FloatField(db_column='RecuentoBetaN89Error')  # Field name made lowercase.
    chi2 = models.FloatField(db_column='Chi2')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'medidaestroncio'


class Medidaestroncioactividadeficienciaalfa(models.Model):
    medidaestroncio_medida = models.OneToOneField(Medidaestroncio, models.DO_NOTHING, db_column='MedidaEstroncio_Medida_ID', primary_key=True)  # Field name made lowercase.
    actividad = models.FloatField(db_column='Actividad')  # Field name made lowercase.
    errorrecuento = models.FloatField(db_column='ErrorRecuento')  # Field name made lowercase.
    actividadminimadetectable = models.FloatField(db_column='ActividadMinimaDetectable')  # Field name made lowercase.
    incertidumbrecombinada = models.FloatField(db_column='IncertidumbreCombinada')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'medidaestroncioactividadeficienciaalfa'


class Medidaestroncioactividadeficienciabeta(models.Model):
    medidaestroncio_medida = models.OneToOneField(Medidaestroncio, models.DO_NOTHING, db_column='MedidaEstroncio_Medida_ID', primary_key=True)  # Field name made lowercase.
    actividad = models.FloatField(db_column='Actividad')  # Field name made lowercase.
    errorrecuento = models.FloatField(db_column='ErrorRecuento')  # Field name made lowercase.
    actividadminimadetectable = models.FloatField(db_column='ActividadMinimaDetectable')  # Field name made lowercase.
    incertidumbrecombinada = models.FloatField(db_column='IncertidumbreCombinada')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'medidaestroncioactividadeficienciabeta'


class Medidapotasio(models.Model):
    medida = models.OneToOneField(Medida, models.DO_NOTHING, db_column='Medida_ID', primary_key=True)  # Field name made lowercase.
    k = models.FloatField(db_column='K')  # Field name made lowercase.
    k_error = models.FloatField(db_column='K_Error')  # Field name made lowercase.
    ek_esr90 = models.FloatField(db_column='EK_ESr90')  # Field name made lowercase.
    ak40 = models.FloatField(db_column='AK40')  # Field name made lowercase.
    ak40_error = models.FloatField(db_column='AK40_Error', blank=True, null=True)  # Field name made lowercase.
    abetaresto = models.FloatField(db_column='ABetaResto')  # Field name made lowercase.
    eabetaresto = models.FloatField(db_column='EABetaResto')  # Field name made lowercase.
    uc = models.FloatField(db_column='Uc')  # Field name made lowercase.
    abeta = models.FloatField(db_column='ABeta')  # Field name made lowercase.
    fechamedidaabsorcionatomica = models.DateField(db_column='FechaMedidaAbsorcionAtomica', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'medidapotasio'


class Medidaradio(models.Model):
    medida_id1 = models.CharField(db_column='Medida_ID1', max_length=30, primary_key=True)  # Field name made lowercase.
    medida_id2 = models.CharField(db_column='Medida_ID2', max_length=30)  # Field name made lowercase.
    t1 = models.FloatField()
    t2 = models.FloatField()
    c1 = models.FloatField(db_column='C1')  # Field name made lowercase.
    c2 = models.FloatField(db_column='C2')  # Field name made lowercase.
    e_c1 = models.FloatField(db_column='E_C1')  # Field name made lowercase.
    e_c2 = models.FloatField(db_column='E_C2')  # Field name made lowercase.
    f4_m1 = models.FloatField()
    f4_m2 = models.FloatField()
    f6_m1 = models.FloatField()
    f6_m2 = models.FloatField()
    ara224 = models.FloatField(db_column='ARa224')  # Field name made lowercase.
    ara226 = models.FloatField(db_column='ARa226')  # Field name made lowercase.
    e_ara224 = models.FloatField(db_column='E_ARa224')  # Field name made lowercase.
    e_ara226 = models.FloatField(db_column='E_ARa226')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'medidaradio'
        unique_together = (('medida_id1', 'medida_id2'),)


class Muestra(models.Model):
    clave = models.CharField(db_column='Clave', primary_key=True, max_length=18)  # Field name made lowercase.
    origen = models.ForeignKey('Origen', models.DO_NOTHING, db_column='Origen_ID', blank=True, null=True)  # Field name made lowercase.
    tipomuestra = models.ForeignKey('Tipomuestra', models.DO_NOTHING, db_column='TipoMuestra_ID', blank=True, null=True)  # Field name made lowercase.
    fecharecogida = models.DateTimeField(db_column='FechaRecogida', blank=True, null=True)  # Field name made lowercase.
    fechafinrecogida = models.DateTimeField(db_column='FechaFinRecogida', blank=True, null=True)  # Field name made lowercase.
    fecharecepcion = models.DateTimeField(db_column='FechaRecepcion', blank=True, null=True)  # Field name made lowercase.
    cantidad = models.FloatField(db_column='Cantidad', blank=True, null=True)  # Field name made lowercase.
    tipocantidad = models.CharField(db_column='TipoCantidad', max_length=18, blank=True, null=True)  # Field name made lowercase.
    conductividad = models.FloatField(db_column='Conductividad', blank=True, null=True)  # Field name made lowercase.
    tipoconservacion = models.CharField(db_column='TipoConservacion', max_length=35, blank=True, null=True)  # Field name made lowercase.
    observaciones = models.CharField(db_column='Observaciones', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'muestra'


class Notificacion(models.Model):
    mensaje = models.CharField(db_column='Mensaje', max_length=500)  # Field name made lowercase.
    alicuota_codigoreducido = models.ForeignKey(Alicuota, models.DO_NOTHING, db_column='Alicuota_CodigoReducido')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'notificacion'


class Notificacionanalitica(models.Model):
    mensaje = models.CharField(db_column='Mensaje', primary_key=True, max_length=500)  # Field name made lowercase.
    medida = models.ForeignKey(Medida, models.DO_NOTHING, db_column='Medida_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'notificacionanalitica'
        unique_together = (('mensaje', 'medida'),)

class Origen(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'origen'


class Patroncontador(models.Model):
    alicuota_codigoreducido = models.OneToOneField(Alicuota, models.DO_NOTHING, db_column='Alicuota_CodigoReducido', primary_key=True)  # Field name made lowercase.
    contador = models.ForeignKey(Contador, models.DO_NOTHING, db_column='Contador_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patroncontador'
        unique_together = (('alicuota_codigoreducido', 'contador'),)


class Radionucleido(models.Model):
    nombre = models.CharField(db_column='Nombre', primary_key=True, max_length=45)  # Field name made lowercase.
    periodosemidesintegracion = models.FloatField(db_column='PeriodoSemidesintegracion')  # Field name made lowercase.
    tipoperiodosemidesintegracion = models.CharField(db_column='TipoPeriodoSemidesintegracion', max_length=38)  # Field name made lowercase.
    tipoemision = models.CharField(db_column='TipoEmision', max_length=9)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'radionucleido'


class Tipoanalitica(models.Model):
    nombre = models.CharField(db_column='Nombre', primary_key=True, max_length=45)  # Field name made lowercase.
    prefijo = models.CharField(db_column='Prefijo', max_length=5)  # Field name made lowercase.
    rangodepositomin = models.IntegerField(db_column='RangoDepositoMin', blank=True, null=True)  # Field name made lowercase.
    rangodepositomax = models.IntegerField(db_column='RangoDepositoMax', blank=True, null=True)  # Field name made lowercase.
    diassininformemax = models.IntegerField(db_column='DiasSinInformeMax', blank=True, null=True)  # Field name made lowercase.
    controlvolumen = models.IntegerField(db_column='ControlVolumen', blank=True, null=True)  # Field name made lowercase.
    controlerrorvolumen = models.IntegerField(db_column='ControlErrorVolumen', blank=True, null=True)  # Field name made lowercase.
    curvaalfa = models.CharField(db_column='CurvaAlfa', max_length=45, blank=True, null=True)  # Field name made lowercase.
    curvabeta = models.CharField(db_column='CurvaBeta', max_length=45, blank=True, null=True)  # Field name made lowercase.
    blanconmedpromedio = models.IntegerField(db_column='BlancoNMedPromedio', blank=True, null=True)  # Field name made lowercase.
    tipoblanco = models.ForeignKey('Tipoblanco', models.DO_NOTHING, db_column='TipoBlanco', blank=True, null=True)  # Field name made lowercase.
    incadicional_curvaalfa = models.FloatField(db_column='IncAdicional_CurvaAlfa', blank=True, null=True)  # Field name made lowercase.
    factoranalitica_curvaalfa = models.FloatField(db_column='FactorAnalitica_CurvaAlfa', blank=True, null=True)  # Field name made lowercase.
    incadicional_curvabeta = models.FloatField(db_column='IncAdicional_CurvaBeta', blank=True, null=True)  # Field name made lowercase.
    factoranalitica_curvabeta = models.FloatField(db_column='FactorAnalitica_CurvaBeta', blank=True, null=True)  # Field name made lowercase.
    limitenalfa = models.FloatField(db_column='LimiteNAlfa', blank=True, null=True)  # Field name made lowercase.
    limitenbeta = models.FloatField(db_column='LimiteNBeta', blank=True, null=True)  # Field name made lowercase.
    rangoactalfamin = models.FloatField(db_column='RangoActAlfaMin', blank=True, null=True)  # Field name made lowercase.
    rangoactalfamax = models.FloatField(db_column='RangoActAlfaMax', blank=True, null=True)  # Field name made lowercase.
    rangoactbetamin = models.FloatField(db_column='RangoActBetaMin', blank=True, null=True)  # Field name made lowercase.
    rangoactbetamax = models.FloatField(db_column='RangoActBetaMax', blank=True, null=True)  # Field name made lowercase.
    diasseparacionradioquimica = models.IntegerField(db_column='DiasSeparacionRadioquimica', blank=True, null=True)  # Field name made lowercase.
    limiterendimientoquimico = models.FloatField(db_column='LimiteRendimientoQuimico', blank=True, null=True)  # Field name made lowercase.
    calcularactividad = models.CharField(db_column='CalcularActividad', max_length=5, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipoanalitica'


class Tipoblanco(models.Model):
    nombre = models.CharField(db_column='Nombre', primary_key=True, max_length=45)  # Field name made lowercase.
    prefijo = models.CharField(db_column='Prefijo', max_length=5)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipoblanco'


class Tipomuestra(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=4)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipomuestra'


class Verificacioncurva(models.Model):
    contador = models.OneToOneField(Contador, models.DO_NOTHING, db_column='Contador_ID', primary_key=True)  # Field name made lowercase.
    curva = models.ForeignKey(Curva, models.DO_NOTHING, db_column='Curva_ID')  # Field name made lowercase.
    ef0 = models.FloatField(db_column='Ef0')  # Field name made lowercase.
    c = models.FloatField(db_column='C')  # Field name made lowercase.
    f = models.FloatField()
    anio = models.IntegerField(db_column='Año')  # Field name made lowercase.
    ef0_error = models.FloatField(db_column='Ef0_Error')  # Field name made lowercase.
    c_error = models.FloatField(db_column='C_Error')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'verificacioncurva'
        unique_together = (('contador', 'curva'),)


class Verificacionpatron(models.Model):
    alicuota_codigoreducido = models.OneToOneField(Alicuota, models.DO_NOTHING, db_column='Alicuota_CodigoReducido', primary_key=True)  # Field name made lowercase.
    curva = models.ForeignKey(Curva, models.DO_NOTHING, db_column='Curva_ID')  # Field name made lowercase.
    contador = models.ForeignKey(Contador, models.DO_NOTHING, db_column='Contador_ID')  # Field name made lowercase.
    nmedidaspromedio = models.IntegerField(db_column='NMedidasPromedio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'verificacionpatron'
        unique_together = (('alicuota_codigoreducido', 'curva', 'contador'),)
