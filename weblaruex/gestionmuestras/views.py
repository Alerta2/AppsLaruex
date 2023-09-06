from django.shortcuts import render
from gestionmuestras.models_nuevo import *
from gestionmuestras.modelChurros import *
from django.http import JsonResponse
from django.contrib.auth.decorators import permission_required
from django.conf import settings

import os

from gestionmuestras.funciones_procesado import *

@permission_required('auth.gestion_muestras')
def opcionesGestionMuestras(request):
    return render(
        request,
        "gestionmuestras/gmuestras.html",
        {
        }
    )

@permission_required('auth.visualizacion_muestras')
def listadoMuestras(request):
    return render(request, "gestionmuestras/listadoMuestras.html", {})


@permission_required('auth.visualizacion_muestras')
def listadoMuestrasDatos(request):
    muestras = HistoricoRecogida.objects.using('gestion_muestras').order_by('-identificador').values('identificador', 'codigo_recogida__codigo_csn__nombre','cliente__nombre','codigo_recogida__codigo_procedencia__nombre', 'codigo_recogida__codigo_memoria__memoria', 'recepcionado_por__nombre', 'fecha_hora_recogida', 'fecha_hora_recepcion', 'estado_de_muestra__descripcion', 'referencia_cliente')

    return JsonResponse(list(muestras), safe=False)


@permission_required('auth.visualizacion_muestras')
def getInfoMuestra(request, id_muestra):
    informe = None
    if 'auth.informes_muestra_lectura' in request.user.get_all_permissions():
        if RelacionInformesMuestra.objects.using('gestion_muestras').filter(codigo_muestra_asociada=id_muestra).exists():
            informe = RelacionInformesMuestra.objects.using('gestion_muestras').filter(codigo_muestra_asociada=id_muestra)[0]
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=id_muestra)[0]
    print(muestra, informe)
    return render(
        request,
        "gestionmuestras/informacionMuestra.html",
        {
            "muestra":muestra,
            "informe":informe
        }
    )

@permission_required('auth.visualizacion_muestras')
def getInfoMuestraForm(request):
    return getInfoMuestra(request, request.POST.get('id_muestra'))

@permission_required('auth.visualizacion_muestras')
def getAlicuotasMuestra(request, id_muestra):
    alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=id_muestra).values('identificador', 'id_analiticas__nombre', 'fecha_hora_entrega', 'analista_tecnico__nombre', 'cantidad_muestra_analizada', 'estado_alicuota__descripcion')
    return JsonResponse(list(alicuotas), safe=False)

@permission_required('auth.insercion_muestras')
def insertarMuestra(request):
    if request.method == "POST":
        print("Crear muestra con todos los parámetros y obtener ID", request.POST)

        if RecogidaGeneral.objects.using('gestion_muestras').filter(codigo_csn__nombre=request.POST.get('codigoCSN').split("_")[1], codigo_procedencia__nombre=request.POST.get('localizacion'), codigo_memoria__memoria=request.POST.get('memoria')).exists():
            print("existe en recogida")
            recogida = RecogidaGeneral.objects.using('gestion_muestras').filter(codigo_csn__nombre=request.POST.get('codigoCSN').split("_")[1], codigo_procedencia__nombre=request.POST.get('localizacion'), codigo_memoria__memoria=request.POST.get('memoria'))[0]
            if request.POST.get('inputComentarioParticular') != '':
                recogida.observaciones = recogida.observaciones + '\n' + request.POST.get('inputComentarioParticular')
                recogida.save(using='gestion_muestras')
        else:
            print("no existe")
            print("muestra", request.POST.get('codigoCSN').split("_")[1])
            recogida = RecogidaGeneral(
                codigo_csn = CodMuestras.objects.using('gestion_muestras').filter(nombre=request.POST.get('codigoCSN').split("_")[1])[0], 
                codigo_procedencia= Procedencias.objects.using('gestion_muestras').filter(nombre=request.POST.get('localizacion'))[0], 
                codigo_memoria = Memorias.objects.using('gestion_muestras').filter(memoria=request.POST.get('memoria'))[0] , 
                observaciones = request.POST.get('inputComentarioParticular'), 
                frecuencia_de_recogida = FrecuenciaRecogida.objects.using('gestion_muestras').filter(nombre=request.POST.get('frecuencia'))[0]
                )
            recogida.save(using='gestion_muestras')
        
        rutaFoto = ""
        if(request.POST.get('foto_webcam') != ''):
            print("guardar foto y calcular ruta") 
            rutaFoto = "/gestionMuestras/fotosMuestras/"+str(recogida.identificador)+"_"+request.POST.get('fechaRecepcion')+"_"+request.POST.get('horaRecepcion')+".jpg"
            f = open(settings.MEDIA_ROOT+rutaFoto, "w")
            f.write(request.POST.get('foto_webcam'))
            f.close()
        
        fechaRecogidaInicio = request.POST.get('fechaRecogidaInicio') + " " + request.POST.get('horaRecogidaInicio')

        historico = HistoricoRecogida(
            codigo_recogida = recogida,
            codigo_barras = "0000000000000",
            recepcionado_por = Usuarios.objects.using('gestion_muestras').filter(usuario_django=request.user.id)[0],
            cliente = Clientes.objects.using('gestion_muestras').filter(nombre=request.POST.get('cliente'))[0],
            suministrador = Suministradores.objects.using('gestion_muestras').filter(nombre=request.POST.get('suministrador'))[0],
            fecha_hora_recogida = request.POST.get('fechaRecogidaInicio') + " " + request.POST.get('horaRecogidaInicio')+"+01:00",
            fecha_hora_recogida_2 = request.POST.get('fechaRecogidaFin') + " " + request.POST.get('horaRecogidaFin')+"+01:00",
            fecha_hora_recogida_ref = request.POST.get('fechaRecogidaReferencia') + " " + request.POST.get('horaRecogidaReferencia')+"+01:00",
            fecha_hora_recepcion = request.POST.get('fechaRecepcion') + " " + request.POST.get('horaRecepcion')+"+01:00",
            estado_de_muestra = EstadoMuestras.objects.using('gestion_muestras').filter(identificador_estado=1)[0],
            referencia_cliente = request.POST.get('referencia'),
            comentarios = request.POST.get('inputComentarioParticular'),
            foto = rutaFoto
        )
        
        historico.save(using='gestion_muestras')
        id_muestra = historico.identificador
        codigoBarras = generarCodigoBarras(id_muestra, None)
        historico.codigo_barras = codigoBarras
        historico.save(using='gestion_muestras')

        determinaciones = Determinaciones.objects.using('gestion_muestras').values()
        predefinidas = MedidasPredefinidas.objects.using('gestion_muestras').values()

        return render(request, "gestionmuestras/insertarAlicuotas.html", {
            "id_muestra":id_muestra,
            "determinaciones":determinaciones,
            "predefinidas":predefinidas
        })
    else:
        memorias = Memorias.objects.using('gestion_muestras').order_by('descripcion').values()
        codMuestras = CodMuestras.objects.using('gestion_muestras').order_by('nombre').values()
        frecuencias = FrecuenciaRecogida.objects.using('gestion_muestras').order_by('-identificador').values()
        suministradores = Suministradores.objects.using('gestion_muestras').order_by('nombre').values()
        clientes = Clientes.objects.using('gestion_muestras').order_by('nombre').values()
        localizaciones = Procedencias.objects.using('gestion_muestras').order_by('nombre').values()
        parametros = ParametrosMuestra.objects.using('gestion_muestras').values()
        return render(
            request,
            "gestionmuestras/insertarMuestra.html",
            {
                "memorias":memorias,
                "codMuestras":codMuestras,
                "frecuencias":frecuencias,
                "suministradores":suministradores,
                "clientes":clientes,
                "localizaciones":localizaciones,
                "parametros":parametros,
            }
        )

@permission_required('auth.insercion_muestras')
def consultarParametrosTipo(request, tipo):
    parametros = RelacionTipoDeterminacionParametros.objects.using('gestion_muestras').filter(tipo=tipo,determinacion__isnull=True).values("parametro__nombre","parametro__descripcion","valor_recomendado")
    return JsonResponse({"parametros":list(parametros)}, safe=False)
        
@permission_required('auth.insercion_muestras')
def insertarDeterminaciones(request):
    determinacionesInsertadas = []
    relacionDeterminacion = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras')
    for key in request.POST:
        if request.POST.get(key) == "on":
            tratamientos = relacionDeterminacion.filter(id_determinacion=key).values("id_determinacion__identificador", "id_determinacion__nombre", "id_tratamiento__identificador", "id_tratamiento__descripcion", "por_defecto")
            determinacionesInsertadas.append({"determinacion":key, "determinacion_nombre":tratamientos[0]["id_determinacion__nombre"], "tratamientos":tratamientos})

    return render(request, "gestionmuestras/asignacionTratamiento.html", {
        "id_muestra": request.POST.get("id_muestra"),
        "determinacionesInsertadas": determinacionesInsertadas,
    })
    

@permission_required('auth.insercion_muestras')
def insertarTratamientos(request):
    tratamientos = []
    return render(request, "gestionmuestras/tareasPostInsercion.html", {
        "id_muestra": request.POST.get("id_muestra"),
        "tratamientos": tratamientos,
    })

def generarCodigoBarras(idMuestra, idAlicuota):
    print(idMuestra, idAlicuota)
    if idAlicuota is None:
        return "1"+("%06d" % idMuestra)+("%06d" % 0)
    else:      
        return "2"+("%06d" % idMuestra)+("%06d" % idAlicuota)


@permission_required('auth.visualizacion_muestras')
def muestrasInforme(request):
    return render(request, "gestionmuestras/muestrasInformes.html", {})


@permission_required('auth.visualizacion_muestras')
def muestrasInformeDatos(request):
    muestras = HistoricoRecogida.objects.using('gestion_muestras').filter(estado_de_muestra=4).order_by('-identificador').values('identificador', 'codigo_recogida__codigo_csn__nombre','cliente__nombre','codigo_recogida__codigo_procedencia__nombre', 'codigo_recogida__codigo_memoria__memoria', 'recepcionado_por__nombre', 'fecha_hora_recogida', 'fecha_hora_recepcion', 'estado_de_muestra__descripcion', 'referencia_cliente')

    return JsonResponse(list(muestras), safe=False)

@permission_required('auth.visualizacion_muestras')
def consultorMedidas(request):
    if request.method == "POST":
        print(request.POST)
        memorias, clientes, determinaciones, estados, tipos = [], [], [], [], []
        for k, v in request.POST.items():
            if k.startswith("memoria_") and v == "on":
                memorias.append(k.replace("memoria_",""))
            if k.startswith("cliente_") and v == "on":
                clientes.append(int(k.replace("cliente_","")))
            if k.startswith("determinacion_") and v == "on":
                determinaciones.append(int(k.replace("determinacion_","")))
            if k.startswith("estado_") and v == "on":
                estados.append(int(k.replace("estado_","")))
            if k.startswith("tipo_") and v == "on":
                tipos.append(k.replace("tipo_",""))
        print(memorias, clientes, determinaciones, estados)
        muestras = ResultadosMedidas.objects.using('gestion_muestras').filter(id_alicuota__id_historico_recogida__fecha_hora_recogida__gte=request.POST.get('fechaInicio'), id_alicuota__id_historico_recogida__fecha_hora_recogida__lte=request.POST.get('fechaFin'))
        if len(memorias) > 0:
            muestras = muestras.filter(id_alicuota__id_historico_recogida__codigo_recogida__codigo_memoria__codigo_memoria__in=memorias)
        if len(clientes) > 0:
            muestras = muestras.filter(id_alicuota__id_historico_recogida__cliente__identificador__in=clientes)
        if len(determinaciones) > 0:
            muestras = muestras.filter(id_alicuota__id_analiticas__identificador__in=determinaciones)
        if len(estados) > 0:
            muestras = muestras.filter(id_alicuota__id_historico_recogida__estado_de_muestra__identificador_estado__in=estados)
        if len(tipos) > 0:
            muestras = muestras.filter(id_alicuota__id_historico_recogida__codigo_recogida__codigo_csn__codigo__in=tipos)
        print("MUESTRAS LEIDAS: ", muestras.count())
        return render(request, "gestionmuestras/consultorMedidasResultados.html", {"muestras":muestras})
    else:
        memorias = Memorias.objects.using('gestion_muestras').order_by('descripcion')
        tiposMuestras = CodMuestras.objects.using('gestion_muestras').order_by('nombre')
        determinaciones = Determinaciones.objects.using('gestion_muestras')
        clientes = Clientes.objects.using('gestion_muestras').order_by('nombre')
        estados = EstadoMuestras.objects.using('gestion_muestras').order_by('descripcion')
        return render(request, "gestionmuestras/consultorMedidas.html", {"memorias":memorias, "tiposMuestras":tiposMuestras, "determinaciones":determinaciones, "clientes":clientes, "estados":estados})

@permission_required('auth.visualizacion_muestras')
def listadoChurros(request):
    return render(request, "gestionmuestras/listadoChurros.html", {})


@permission_required('auth.visualizacion_muestras')
def listadoChurrosDatos(request):
    muestras = Churros.objects.using('geslabChurros').order_by('-f_analisis').values('memoria__memoria', 'muestra__nombre', 'analisis__descripcion', 'isotopo__descripcion', 'f_rec_ini', 'f_rec_fin', 'dias', 'f_analisis', 'muestra_compartida', 'actividad', 'error', 'lid', 'submuestras', 'tiempo_medida', 'cantidad_muestra_recogida', 'cantidad_muestra_analizada', 'rendimiento')

    return JsonResponse(list(muestras), safe=False)

@permission_required('auth.visualizacion_muestras')
def capturarInformeAlfa(request):
    print(request.POST)
    if request.method == "POST":
        fichero = request.FILES['inputFile']
        datos = procesarInformeAlfa(fichero)
        return render(request, "gestionmuestras/capturarInformeAlfa.html", {"datos":datos})
    else:
        return render(request, "gestionmuestras/capturarInformeAlfa.html", {})

@permission_required('auth.visualizacion_muestras')
def capturarDBFgestmues(request):
    print(request.POST)
    if request.method == "POST":
        fichero = request.FILES['inputFile']

        with open("recogida.dbf", "wb+") as f:
            for chunk in fichero.chunks():
                f.write(chunk)
        
        datos = procesarDBFgestmues("recogida.dbf")
        if "recogida.dbf":
            os.remove("recogida.dbf")
        return render(request, "gestionmuestras/cargarDBFgestmues.html", {"datos":datos})
    else:
        return render(request, "gestionmuestras/cargarDBFgestmues.html", {})
    
@permission_required('auth.visualizacion_muestras')
def capturarExcelCopuma(request):
    print(request.POST)
    if request.method == "POST":
        fichero = request.FILES['inputFile']
        with open("excel.xlsx", "wb+") as f:
            for chunk in fichero.chunks():
                f.write(chunk)
        
        datos = procesarExcelCopuma("excel.xlsx")
        return render(request, "gestionmuestras/capturarExcelCopuma.html", {"datos":datos})
    else:
        return render(request, "gestionmuestras/capturarExcelCopuma.html", {})
    
@permission_required('auth.visualizacion_muestras')
def infoAlicuota(request, id_alicuota):
    tratamientos = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=id_alicuota).values('identificador','cod_reducido','tratamiento__descripcion','fecha_inicio','fecha_fin','analista__nombre','paso_actual')
    return JsonResponse(list(tratamientos), safe=False)


@permission_required('auth.visualizacion_muestras')
def verificarMuestra(request):
    '''
    from django.contrib.auth.models import Group
    users_in_group = Group.objects.get(name="group name").user_set.all()
    
    if user in users_in_group:
        # do something
    '''
    print("RECIBO:", request.POST)
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=request.POST.get('id_muestra')).get()

        
    return JsonResponse({}, safe=False)

@permission_required('auth.visualizacion_muestras')
def consultaDuplicados(request):
    if request.method == "POST":
        print(request.POST)
        muestrasConDuplicados = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(cod_reducido__contains="DU", id_muestra_analitica__id_historico_recogida__fecha_hora_recogida__range=(request.POST.get('fechaInicio'),request.POST.get('fechaFin'))).filter(cod_reducido__contains=request.POST.get('procedimiento')).values_list("id_muestra_analitica__id_historico_recogida")

        muestras = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(cod_reducido__contains=request.POST.get('procedimiento'), id_muestra_analitica__id_historico_recogida__in=list(muestrasConDuplicados), tratamiento__identificador=3).order_by('id_muestra_analitica__id_historico_recogida')

        resultados = []
        resultado = None
        labels, data1, data2 = [], [], []

        for muestra in muestras:
            duplicada = muestra.cod_reducido.endswith("DU")
            if resultado is None:
                resultado = {}
                resultado["muestra"] = muestra.id_muestra_analitica.id_historico_recogida.identificador
            if resultado["muestra"] != muestra.id_muestra_analitica.id_historico_recogida.identificador:
                if resultado["muestra"] is not None and ("actividad_original" in resultado and resultado["actividad_original"] is not None) and ("actividad_duplicada" in resultado and resultado["actividad_duplicada"] is not None):
                    labels.append(resultado["muestra"])
                    data1.append([round(resultado["actividad_original"]+resultado["error_original"], 3), round(resultado["actividad_original"], 3), round(resultado["actividad_original"]-resultado["error_original"], 3)])
                    data2.append([round(resultado["actividad_duplicada"]+resultado["error_duplicada"], 3), round(resultado["actividad_duplicada"], 3), round(resultado["actividad_duplicada"]-resultado["error_duplicada"], 3)])
                    resultado = calcularControles(resultado, request.POST.get('procedimiento'), request.POST.get('medida'))
                resultados.append(resultado)
                resultado = {}
                resultado["muestra"] = muestra.id_muestra_analitica.id_historico_recogida.identificador

            if duplicada:
                resultado["duplicada"] = muestra.cod_reducido
            else:
                resultado["original"] = muestra.cod_reducido
            try:
                registroAB = RelacionTratamientoAlfabetaResultado.objects.using('gestion_muestras').filter(cod_reducido=muestra.cod_reducido, parametro=request.POST.get('medida')).get()
                if duplicada:
                    resultado["actividad_duplicada"] = registroAB.actividad
                    resultado["error_duplicada"] = registroAB.incertidumbre
                    resultado["amd_duplicada"] = registroAB.amd
                else:
                    resultado["actividad_original"] = registroAB.actividad
                    resultado["error_original"] = registroAB.incertidumbre
                    resultado["amd_original"] = registroAB.amd
                    
            except:
                if duplicada:
                    resultado["actividad_duplicada"] = None
                    resultado["error_duplicada"] = None
                    resultado["amd_duplicada"] = None
                else:
                    resultado["actividad_original"] = None
                    resultado["error_original"] = None
                    resultado["amd_original"] = None
        
        if resultado and resultado["muestra"] is not None and resultado["actividad_original"] is not None and resultado["actividad_duplicada"] is not None:
            labels.append(resultado["muestra"])
            data1.append([round(resultado["actividad_original"]+resultado["error_original"], 3), round(resultado["actividad_original"], 3), round(resultado["actividad_original"]-resultado["error_original"], 3)])
            data2.append([round(resultado["actividad_duplicada"]+resultado["error_duplicada"], 3), round(resultado["actividad_duplicada"], 3), round(resultado["actividad_duplicada"]-resultado["error_duplicada"], 3)])
            resultado = calcularControles(resultado, request.POST.get('procedimiento'), request.POST.get('medida'))
        resultados.append(resultado)

        return render(request, "gestionmuestras/consultaDuplicados.html", {"resultados":resultados, "labels": labels, "data1": data1, "data2": data2})
    else:
        return render(request, "gestionmuestras/consultaDuplicados.html", {})
    
def calcularControles(resultado, procedimiento, medida):
    if resultado["actividad_original"] < resultado["amd_original"] or resultado["actividad_duplicada"] < resultado["amd_duplicada"]:
        resultado["control"] = "OK"
        resultado["descripcion"] = "Valor inferior al AMD"
        resultado["factor"] = 1
        resultado["factor2"] = "OK"
        return resultado
    else:
        if resultado["actividad_original"] > resultado["actividad_duplicada"]:
            return verificarResultado(resultado, resultado["actividad_original"], resultado["error_original"], resultado["actividad_duplicada"], resultado["error_duplicada"], obtenerFactor(procedimiento, medida))
        else:
            return verificarResultado(resultado, resultado["actividad_duplicada"], resultado["error_duplicada"], resultado["actividad_original"], resultado["error_original"], obtenerFactor(procedimiento, medida))

def verificarResultado(resultado, mayor, errorAbajoMayor, menor, errorArribaMenor, factorCorrecto):
    factor = round(mayor / menor,2)
    if factor > factorCorrecto:
        resultado["control"] = "ERROR"
        resultado["descripcion"] = "Valor fuera de rango"
        resultado["factor"] = factor
    else:
        resultado["control"] = "OK"
        resultado["descripcion"] = "Valor dentro de rango"
        resultado["factor"] = factor

    rango1Max = mayor + errorAbajoMayor
    rango1Min = mayor - errorAbajoMayor
    rango2Max = menor + errorArribaMenor
    rango2Min = menor - errorArribaMenor

    # comprobar si coinciden valores entre los rangos
    if (rango1Max > rango2Max and rango1Min < rango2Max) or (rango1Max > rango2Min and rango1Min < rango2Min) or (rango1Max > rango2Max and rango1Min < rango2Min) or (rango1Max < rango2Max and rango1Min > rango2Min):
        resultado["factor2"] = "OK"
    else:
        resultado["factor2"] = "ERROR"
    return resultado

def obtenerFactor(procedimiento, medida):
    if procedimiento == "AB" and medida == "ALFA":
        return 1.3
    if procedimiento == "AB" and medida == "BETA":
        return 1.1
    if procedimiento == "CP" and medida == "ALFA":
        return 1.4
    return 1