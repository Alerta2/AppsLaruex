from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth.models import Permission
from django.conf import settings
from django.db import connections
from django.http import JsonResponse
import simplejson

from .procesar_texto import procesar_texto_copuma_volatil, guardar_muestra

from copuma.forms import UploadFormCopuma
from copuma.models import *

def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


######################### VRAEX #########################
######################### VRAEX PUBLICO #########################

def getPortadaJuntaex(request):
    user = request.user
    return render(
        request,
        "portadaJuntaex.html",
        {
            "user":user,
        }
    )


def getPortadaVraex(request):
    user = request.user
    return render(
        request,
        "portadaCopuma.html",
        {
            "user":user,
        }
    )

# MAPA PUBLICO VRAEX
def GetHomeMuestrasPublic(request):
    user=request.user
    return render(
        request,
        "muestrasmapapublico.html",
        {'user':user}
    )

#CONSULTA MUESTRAS MAPA PUBLICO VRAEX
def GetMuestrasPublic(request,cod_muestra, cod_analisis, cod_procedencia):
    muestras=""
    salida = ""
    if(cod_muestra!="-1"):
        valores = cod_muestra.split("_")
        muestras=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(muestra_codmuestra__in=valores).filter(csn=0)
    if len(muestras)!=0:
        codigos_procedencia=muestras.values_list('estacion_codprocedencia', flat=True).distinct()
        codigos_procedencia=Procedencia.objects.using('gestion_memoria').filter(codprocedencia__in=codigos_procedencia)

        for ind4 in codigos_procedencia:
            print ("Busco procedencia" + " " + str(ind4.codprocedencia) + " " + str(ind4.name) + " " + str(ind4.map_lat)  + " " + str(ind4.map_lon))
            if len(salida)>0:
                salida = salida + "##" + str(ind4.name) + "@" + str(ind4.map_lat) + "@" + str(ind4.map_lon) + "@" + str(ind4.codprocedencia)
            else:
                salida = salida + str(ind4.name) + "@" + str(ind4.map_lat) + "@" + str(ind4.map_lon) + "@" + str(ind4.codprocedencia)

            for m in valores:
                auxmuestra = muestras.filter(estacion_codprocedencia=ind4.codprocedencia).filter(muestra_codmuestra=m)
                codigos_muestras=auxmuestra.values_list('muestra_codmuestra', flat=True).distinct()
                codigos_muestras=Muestra.objects.using('gestion_memoria').filter(codmuestra__in=codigos_muestras)
                for codmuestra in codigos_muestras:
                    salida = salida + "#" + str(codmuestra.name) + "*" + str(codmuestra.codmuestra) +"@"
                    codigos_analisis=auxmuestra.values_list('isotopo_analisis_codanalisis', flat=True).distinct()
                    codigos_analisis=Analisis.objects.using('gestion_memoria').filter(codanalisis__in=codigos_analisis)
                    for analisis in codigos_analisis:
                        salida = salida + str(analisis.name) + "%" + str(analisis.codanalisis) + "*"
    else:
        error=1
    print("DATOS#####", salida)
    return render(request, 'data/plantilla_mapa_plana.html', {'datos':salida})

#CONSULTA MUESTRAS MAPA PUBLICO VRAEX MODIFICANDO PARA HACERLO CORRECTAMENTE
def GetMuestrasPublicNew(request,cod_muestra):
    procedencias = []
    valores = cod_muestra.split("_")
    muestras=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(muestra_codmuestra__in=valores).filter(csn=0)
    if len(muestras)!=0:
        codigos_procedencia=muestras.values_list('estacion_codprocedencia', flat=True).distinct()
        for procedencia in codigos_procedencia:
            estacion = Procedencia.objects.using('gestion_memoria').filter(codprocedencia=procedencia)[0]
            codigos_analisis = ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=procedencia).values_list('isotopo_analisis_codanalisis', flat=True).distinct()
            analisis_encontrados=Analisis.objects.using('gestion_memoria').filter(codanalisis__in=codigos_analisis).values()
            procedencias.append({"Procedencia":  simplejson.dumps(estacion), "Muestras": list(analisis_encontrados)})
    print(procedencias)
    jsonValores = simplejson.dumps(procedencias)
    return JsonResponse(jsonValores, safe=False)



#CONSULTA GRAFICA PUBLICO VRAEX
def GetGraficaPublic(request, cod_muestra, cod_analisis, cod_procedencia):
    enac = 1
    perm_noverif = 1

    if cod_muestra=="I" and cod_analisis=="IG":
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(csn=0).filter(isotopo_codisotopo='I').order_by('fecha_recogida_inicial','isotopo_codisotopo','masa')
    elif cod_analisis=="IG":
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(csn=0).exclude(isotopo_codisotopo='Ba').exclude(isotopo_codisotopo='Cr').exclude(isotopo_codisotopo='I').exclude(isotopo_codisotopo='La').exclude(isotopo_codisotopo='Nb').exclude(isotopo_codisotopo='Ru').exclude(isotopo_codisotopo='Zr').order_by('fecha_recogida_inicial','isotopo_codisotopo','masa')
    else:
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(csn=0).order_by('fecha_recogida_inicial','isotopo_codisotopo','masa')

    primera_fecha = None
    for val in valores:
        f=val.fecha_recogida_inicial
        if (primera_fecha is None):
            primera_fecha = f.strftime("%Y")+"-"+f.strftime("%m")+"-"+f.strftime("%d")

    if cod_muestra=="I" and cod_analisis=="IG":
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(isotopo_codisotopo='I').filter(fecha_recogida_inicial__gte=primera_fecha).order_by('fecha_recogida_inicial','csn','isotopo_codisotopo','masa')
        isotopos=list(ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(fecha_recogida_inicial__gte=primera_fecha).filter(isotopo_codisotopo='I').order_by('isotopo_codisotopo','masa').values_list('isotopo_codisotopo','masa').distinct())
    elif cod_analisis=="IG":
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(fecha_recogida_inicial__gte=primera_fecha).exclude(isotopo_codisotopo='Ba').exclude(isotopo_codisotopo='Cr').exclude(isotopo_codisotopo='I').exclude(isotopo_codisotopo='La').exclude(isotopo_codisotopo='Nb').exclude(isotopo_codisotopo='Ru').exclude(isotopo_codisotopo='Zr').exclude(masa=210).order_by('fecha_recogida_inicial','csn','isotopo_codisotopo','masa')
        isotopos=list(ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(fecha_recogida_inicial__gte=primera_fecha).exclude(isotopo_codisotopo='Ba').exclude(isotopo_codisotopo='Cr').exclude(isotopo_codisotopo='I').exclude(isotopo_codisotopo='La').exclude(isotopo_codisotopo='Nb').exclude(isotopo_codisotopo='Ru').exclude(isotopo_codisotopo='Zr').exclude(masa=210).order_by('isotopo_codisotopo','masa').values_list('isotopo_codisotopo','masa').distinct())
    else:
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(fecha_recogida_inicial__gte=primera_fecha).order_by('fecha_recogida_inicial','csn','isotopo_codisotopo','masa')
        isotopos=list(ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(muestra_codmuestra=cod_muestra).filter(fecha_recogida_inicial__gte=primera_fecha).filter(isotopo_analisis_codanalisis=cod_analisis).order_by('isotopo_codisotopo','masa').values_list('isotopo_codisotopo','masa').distinct())

    #DATOS LARUEX

    aux=""
    isotopo=""
    #Calculamos el numero de isotopo que tiene esta muestra
    isotopo_inicial=valores[0].isotopo_codisotopo

    isotopo_inicial_masa=valores[0].masa

    isotopo_final=valores[len(valores)-1].isotopo_codisotopo

    isotopo_final_masa=valores[len(valores)-1].masa


    primera_fecha = None
    ultima_fecha = None
    valores_csn = 0

    for val in valores:
        if cod_analisis=="AT" or cod_analisis=="BT" or cod_analisis=="UT" or cod_analisis=="TD":
            limite=Limites.objects.using('gestion_memoria').filter(codmuestra=val.muestra_codmuestra).filter(analisis_codanalisis=cod_analisis).filter(masa=val.masa)
        else:
            limite=Limites.objects.using('gestion_memoria').filter(codmuestra=val.muestra_codmuestra).filter(codisotopo=val.isotopo_codisotopo).filter(masa=val.masa)
        if len(limite) == 0:
            limite_maximo = 100000
            unidades = "N/U"
        else:
            limite_maximo = limite[0].limite_maximo
            unidades = limite[0].unidad



        if val.isotopo_codisotopo.replace(" ", "")==isotopo_inicial.replace(" ", "") and val.masa==isotopo_inicial_masa:
            f=val.fecha_recogida_inicial
            aux+=f.strftime("%Y")+","+f.strftime("%m")+","+f.strftime("%d")+","+f.strftime("%H")+","+f.strftime("%M")
            if (primera_fecha is None):
                primera_fecha = f.strftime("%Y")+"-"+f.strftime("%m")+"-"+f.strftime("%d")
            ultima_fecha = f.strftime("%Y")+"-"+f.strftime("%m")+"-"+f.strftime("%d")

        if(val.actividad_medida==-1):
            val.actividad_medida=0
        if(val.lid_medida==-1):
            val.lid_medida=0
        if(val.error_actividad_medida==-1):
            val.error_actividad_medida=0
        if(val.csn == 1):
            valores_csn = 1

        aux+="%" +str(val.actividad_medida)+"%" +str(val.lid_medida)+"%"+str(val.error_actividad_medida)+"%"+str(limite_maximo)+"%"+str(val.csn)
        if val.isotopo_codisotopo.replace(" ", "")==isotopo_final.replace(" ", "") and val.masa==isotopo_final_masa:
            aux+="@"
    aux=aux [:-1]


    #ISOTOPOS

    isos=""

    for iso in isotopos:
        if str(cod_analisis) == "H" and str(cod_muestra) == "PP":
            enac = 0
        if iso[1]==-1:
            if str(cod_analisis)=="AT":
                isos+="Alfa Total$"
            elif str(cod_analisis)=="BT":
                isos+="Beta Total$"
            elif str(cod_analisis)=="UT":
                isos+="Uranio Total$"
            elif str(cod_analisis)=="TD":
                isos+="Tasa de Dosis$"

        else:
            isos+=str(iso[0])+str(iso[1])+"$"
    isos=isos [:-1]

    prod_cna = ""

    producciones=ProduccionAlmaraz.objects.using('gestion_memoria').filter(fecha_consumo__lte=ultima_fecha).filter(fecha_consumo__gte=primera_fecha)

    for p in producciones:
        prod_cna = prod_cna + "@" +  str(p.fecha_consumo) + "%" + str(p.modulo_1) + "%" + str(p.modulo_2)

    prod_cna = prod_cna[1:]

    aux = aux + "##" + prod_cna + '##' + str(valores_csn)

    #print ("DATOS::::::::::::::::::::::::"+aux)
    #print ("PRODUCCION::::::::::::::::::::::::"+prod_cna)
    #print ("PROCEDENCIA::::::::::::::::::::::::"+cod_procedencia)
    return render(request, 'data/isotopos.html', {'unidad': unidades, 'valores': aux,'isotopos':isos, 'logo_enac': enac, 'procedencia': cod_procedencia})

#CONSULTA GRAFICA DOSIS PUBLICO VRAEX
def GetGraficaPublicDose(request, cod_muestra, cod_analisis, cod_procedencia):
    valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(csn=0).order_by('fecha_recogida_inicial')
    valEstacion = []
    limite = LimitesDosis.objects.using('gestion_memoria').filter(codprocedencia=cod_procedencia)[0]
    nombre = Procedencia.objects.using('gestion_memoria').filter(codprocedencia=cod_procedencia)[0].name
    unidad = "mSv/a"
    for val in valores:
        estacion = {}
        # f.strftime("%Y")+","+f.strftime("%m")+","+f.strftime("%d")+","+f.strftime("%H")+","+f.strftime("%M")
        estacion["fecha"] = val.fecha_recogida_inicial.strftime("%Y")+"@"+val.fecha_recogida_inicial.strftime("%m")+"@"+val.fecha_recogida_inicial.strftime("%d")+"@"+val.fecha_recogida_inicial.strftime("%H")+"@"+val.fecha_recogida_inicial.strftime("%M")
        estacion["actividad"] = str(val.actividad_medida)
        estacion["fondo"] = str(limite.dosismedia)
        estacion["maximo"] = str(limite.dosismaxima)
        valEstacion.append(estacion)
    valoresEstaciones = ""
    for valor in valEstacion:
        valoresEstaciones = valoresEstaciones + str(valor) + "%"

    return render(request, 'data/data_dose.html', {'estacion': nombre, 'valores':valoresEstaciones[:-1], 'unidad': unidad})


######################### VRAEX PRIVADO #########################

# CONSULTA MAPA VRAEX PRIVADO
@permission_required('auth.muestras_vraex')
def GetHomeMuestras(request):
    user=request.user
    return render(
        request,
        "muestrasmapa.html",
        {'user':user}
    )

# CONSULTA MUESTRAS VRAEX PRIVADO
@permission_required('auth.muestras_vraex')
def GetMuestras(request,cod_muestra,cod_analisis,cod_procedencia):
    user=request.user
    muestras=""
    error=0
    salida = ""

    if(cod_muestra!="-1"):
        valores = cod_muestra.split("_")
        muestras=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(muestra_codmuestra__in=valores).filter(csn=0)

    print ("LONGITUD MUESTRAS: "+ str(len(muestras)))

    if len(muestras)!=0:
        codigos_procedencia=muestras.values_list('estacion_codprocedencia', flat=True).distinct()
        codigos_procedencia=Procedencia.objects.using('gestion_memoria').filter(codprocedencia__in=codigos_procedencia)

        for ind4 in codigos_procedencia:
            print ("Busco procedencia" + " " + str(ind4.codprocedencia) + " " + str(ind4.name) + " " + str(ind4.map_lat)  + " " + str(ind4.map_lon))
            if len(salida)>0:
                salida = salida + "##" + str(ind4.name) + "@" + str(ind4.map_lat) + "@" + str(ind4.map_lon) + "@" + str(ind4.codprocedencia)
            else:
                salida = salida + str(ind4.name) + "@" + str(ind4.map_lat) + "@" + str(ind4.map_lon) + "@" + str(ind4.codprocedencia)

            for m in valores:
                auxmuestra = muestras.filter(estacion_codprocedencia=ind4.codprocedencia).filter(muestra_codmuestra=m)
                codigos_muestras=auxmuestra.values_list('muestra_codmuestra', flat=True).distinct()
                codigos_muestras=Muestra.objects.using('gestion_memoria').filter(codmuestra__in=codigos_muestras)
                for codmuestra in codigos_muestras:
                    salida = salida + "#" + str(codmuestra.name) + "*" + str(codmuestra.codmuestra) +"@"
                    codigos_analisis=auxmuestra.values_list('isotopo_analisis_codanalisis', flat=True).distinct()
                    codigos_analisis=Analisis.objects.using('gestion_memoria').filter(codanalisis__in=codigos_analisis)
                    for analisis in codigos_analisis:
                        salida = salida + str(analisis.name) + "%" + str(analisis.codanalisis) + "*"

    else:
        error=1

    return render(request, 'data/plantilla_mapa_plana.html', {'datos':salida})

# CONSULTA GRAFICA VRAEX PRIVADO
@permission_required('auth.muestras_vraex')
def GetGrafica(request, cod_muestra, cod_analisis, cod_procedencia):
    enac = 1

    perm_noverif = 0

    if cod_muestra=="I" and cod_analisis=="IG":
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(csn=0).filter(isotopo_codisotopo='I').order_by('fecha_recogida_inicial','isotopo_codisotopo','masa')
    elif cod_analisis=="IG":
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(csn=0).exclude(isotopo_codisotopo='Ba').exclude(isotopo_codisotopo='Cr').exclude(isotopo_codisotopo='I').exclude(isotopo_codisotopo='La').exclude(isotopo_codisotopo='Nb').exclude(isotopo_codisotopo='Ru').exclude(isotopo_codisotopo='Zr').order_by('fecha_recogida_inicial','isotopo_codisotopo','masa')
    else:
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(csn=0).order_by('fecha_recogida_inicial','isotopo_codisotopo','masa')


    primera_fecha = None
    for val in valores:
        f=val.fecha_recogida_inicial
        if (primera_fecha is None):
            primera_fecha = f.strftime("%Y")+"-"+f.strftime("%m")+"-"+f.strftime("%d")

    if cod_muestra=="I" and cod_analisis=="IG":
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(isotopo_codisotopo='I').filter(fecha_recogida_inicial__gte=primera_fecha).order_by('fecha_recogida_inicial','csn','isotopo_codisotopo','masa')
        isotopos=list(ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(fecha_recogida_inicial__gte=primera_fecha).filter(isotopo_codisotopo='I').order_by('isotopo_codisotopo','masa').values_list('isotopo_codisotopo','masa').distinct())
    elif cod_analisis=="IG":
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(fecha_recogida_inicial__gte=primera_fecha).exclude(isotopo_codisotopo='Ba').exclude(isotopo_codisotopo='Cr').exclude(isotopo_codisotopo='I').exclude(isotopo_codisotopo='La').exclude(isotopo_codisotopo='Nb').exclude(isotopo_codisotopo='Ru').exclude(isotopo_codisotopo='Zr').order_by('fecha_recogida_inicial','csn','isotopo_codisotopo','masa')
        isotopos=list(ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(fecha_recogida_inicial__gte=primera_fecha).exclude(isotopo_codisotopo='Ba').exclude(isotopo_codisotopo='Cr').exclude(isotopo_codisotopo='I').exclude(isotopo_codisotopo='La').exclude(isotopo_codisotopo='Nb').exclude(isotopo_codisotopo='Ru').exclude(isotopo_codisotopo='Zr').order_by('isotopo_codisotopo','masa').values_list('isotopo_codisotopo','masa').distinct())
    else:
        valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(verificado__gte=perm_noverif).filter(muestra_codmuestra=cod_muestra).filter(isotopo_analisis_codanalisis=cod_analisis).filter(fecha_recogida_inicial__gte=primera_fecha).order_by('fecha_recogida_inicial','csn','isotopo_codisotopo','masa')
        isotopos=list(ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(estacion_codprocedencia=cod_procedencia).filter(muestra_codmuestra=cod_muestra).filter(fecha_recogida_inicial__gte=primera_fecha).filter(isotopo_analisis_codanalisis=cod_analisis).order_by('isotopo_codisotopo','masa').values_list('isotopo_codisotopo','masa').distinct())

    #DATOS LARUEX

    aux=""
    isotopo=""
    #Calculamos el numero de isotopo que tiene esta muestra
    isotopo_inicial=valores[0].isotopo_codisotopo

    isotopo_inicial_masa=valores[0].masa

    isotopo_final=valores[len(valores)-1].isotopo_codisotopo

    isotopo_final_masa=valores[len(valores)-1].masa

    primera_fecha = None
    ultima_fecha = None
    valores_csn = 0
    print("cod_isotopo", valores[0].isotopo_codisotopo, "cod_analisis", valores[0].isotopo_analisis_codanalisis, "masa", valores[0].masa)

    for val in valores:
        if cod_analisis=="AT" or cod_analisis=="BT" or cod_analisis=="UT" or cod_analisis=="TD":
            limite=Limites.objects.using('gestion_memoria').filter(codmuestra=val.muestra_codmuestra).filter(analisis_codanalisis=cod_analisis).filter(masa=val.masa)
        else:
            limite=Limites.objects.using('gestion_memoria').filter(codmuestra=val.muestra_codmuestra).filter(codisotopo=val.isotopo_codisotopo).filter(masa=val.masa)
        if len(limite) == 0:
            limite_maximo = 100000
            unidades = "N/U"
        else:
            limite_maximo = limite[0].limite_maximo
            unidades = limite[0].unidad



        if val.isotopo_codisotopo.replace(" ", "")==isotopo_inicial.replace(" ", "") and val.masa==isotopo_inicial_masa:
            f=val.fecha_recogida_inicial
            aux+=f.strftime("%Y")+","+f.strftime("%m")+","+f.strftime("%d")+","+f.strftime("%H")+","+f.strftime("%M")
            if (primera_fecha is None):
                primera_fecha = f.strftime("%Y")+"-"+f.strftime("%m")+"-"+f.strftime("%d")
            ultima_fecha = f.strftime("%Y")+"-"+f.strftime("%m")+"-"+f.strftime("%d")

        if(val.actividad_medida==-1):
            val.actividad_medida=0
        if(val.lid_medida==-1):
            val.lid_medida=0
        if(val.error_actividad_medida==-1):
            val.error_actividad_medida=0
        if(val.csn == 1):
            valores_csn = 1

        aux+="%" +str(val.actividad_medida)+"%" +str(val.lid_medida)+"%"+str(val.error_actividad_medida)+"%"+str(limite_maximo)+"%"+str(val.csn)
        if val.isotopo_codisotopo.replace(" ", "")==isotopo_final.replace(" ", "") and val.masa==isotopo_final_masa:
            aux+="@"
    aux=aux [:-1]


    #ISOTOPOS

    isos=""

    for iso in isotopos:
        if str(cod_analisis) == "H" and str(cod_muestra) == "PP":
            enac = 0
        if iso[1]==-1:
            if str(cod_analisis)=="AT":
                isos+="Alfa Total$"
            elif str(cod_analisis)=="BT":
                isos+="Beta Total$"
            elif str(cod_analisis)=="UT":
                isos+="Uranio Total$"
            elif str(cod_analisis)=="TD":
                isos+="Tasa de Dosis$"

        else:
            isos+=str(iso[0])+str(iso[1])+"$"
    isos=isos [:-1]

    prod_cna = ""

    producciones=ProduccionAlmaraz.objects.using('gestion_memoria').filter(fecha_consumo__lte=ultima_fecha).filter(fecha_consumo__gte=primera_fecha)

    for p in producciones:
        prod_cna = prod_cna + "@" +  str(p.fecha_consumo) + "%" + str(p.modulo_1) + "%" + str(p.modulo_2)

    prod_cna = prod_cna[1:]

    aux = aux + "##" + prod_cna + '##' + str(valores_csn)

    estacion = "estacion"
    estaciones=Procedencia.objects.using('gestion_memoria').filter(codprocedencia=cod_procedencia)
    for e in estaciones:
        estacion = e.name
    aux = aux + "##" + estacion
    return render(request, 'data/isotopos.html', {'unidad': unidades, 'valores': aux,'isotopos':isos, 'logo_enac': enac, 'procedencia': cod_procedencia })

# Metodo llamado desde verificar. Consulta de valores a verificar para tabla de consulta
def CalcularVerificar():
    valores=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(verificado=0).filter(csn=0).order_by('estacion_codprocedencia','muestra_codmuestra','isotopo_codisotopo').values('muestra_codmuestra','isotopo_analisis_codanalisis','estacion_codprocedencia','fecha_recogida_inicial','fecha_analisis','fecha_subida_fichero').distinct()

    datos = []
    for val in valores:
        codmuestra = ""
        codanalisis = ""
        codprocedencia = ""
        fechainicial = ""
        fechaanalisis = ""
        fechasubida = ""
        for key, value in val.items():
            if key == "muestra_codmuestra":
                codmuestra = value.replace(" ", "")
            if key == "isotopo_analisis_codanalisis":
                codanalisis = value
            if key == "estacion_codprocedencia":
                codprocedencia = value
            if key == "fecha_recogida_inicial":
                fechainicial = value
            if key == "fecha_analisis":
                fechaanalisis = value
            if key == "fecha_subida_fichero":
                fechasubida = value
        print("codmuestra",codmuestra,"codanalisis",codanalisis,"codprocedencia",codprocedencia,"fecharecogida",fechainicial,"fechaanalisis",fechaanalisis,"fechasubida",fechasubida)
        datos.append({"codmuestra":codmuestra,"codanalisis":codanalisis,"codprocedencia":codprocedencia,"fecharecogida":fechainicial,"fechaanalisis":fechaanalisis,"fechasubida":fechasubida})
    datos_result = []
    for i in range(len(datos)):
        if datos[i] not in datos[i + 1:]:
            datos_result.append(datos[i])
    return datos_result

# Consulta de los datos a verificar VRAEX
@permission_required('auth.vision_no_verificado')
def Verificar(request):
    user = request.user
    datos_result = CalcularVerificar()
    return render(
        request,
        "verificacion.html",
        {
            "user":user,
            "datos":datos_result
        }
    )

# Verificacion de una muestra de VRAEX
@permission_required('auth.verificacion_vraex')
def Verificada(request,cod_muestra,cod_analisis,cod_procedencia):
    ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(muestra_codmuestra=cod_muestra,isotopo_analisis_codanalisis=cod_analisis,estacion_codprocedencia=cod_procedencia,csn=0,verificado=0).update(verificado=1)
    user = request.user
    datos_result = CalcularVerificar()
    return render(
        request,
        "verificacion.html",
        {
            "user":user,
            "datos":datos_result
        }
    )

# SUBIDA DE NUEVOS DATOS VRAEX
@permission_required('auth.subida_vraex')
def UploadCopuma(request):
    user = request.user
    if request.method == 'POST':
        form = UploadFormCopuma(request.POST, request.FILES)
        mensaje_correcto=""
        mensaje_error=""
        if form.is_valid():
            nombre_fichero=str(request.FILES['docfile']).split(".")[0]
            #Creamos el documentao que hemos subido
            document=GestionMemoriaDocumentcopuma.objects.using('gestion_memoria').filter(filename=nombre_fichero)
            if(len(document)==0 or 1==1):
                newdoc = GestionMemoriaDocumentcopuma(filename = nombre_fichero,docfile = request.FILES['docfile'])
                newdoc.save(form,using='gestion_memoria')
                #Leemos el fichero subido
                infile = open(settings.MEDIA_ROOT+str(newdoc.docfile), 'r')
                mensaje_error,mensaje_correcto,mensaje_resumen=procesar_texto_copuma_volatil(infile,str(newdoc.docfile))
                infile.close()
            else:
                return render(
                    request,
                    "subida_copuma.html",
                    {
                        'form': form,
                        'mensaje_error':"Ya existe un fichero con el mismo nombre"
                    }
                )
            return render(
                request,
                "subida_copuma.html",
                {
                    'form': form,
                    'mensaje_correcto':mensaje_correcto,
                    'mensaje_error':mensaje_error,
                    'mensaje_resumen':mensaje_resumen
                }
            )
    else:
        form = UploadFormCopuma()
    return render(
        request,
        "subida_copuma.html",
        {
            'form': form,
            'user':user
        }
    )

# CARGA DE UNA MUESTRA DE VRAEX
@permission_required('auth.subida_vraex')
def EnviarMuestra(request,motivo_muestreo_codmuestreo,fecha_recogida_inicial,fecha_recogida_final,fecha_analisis,instalacion_codinstalacion,laboratorio_codlaboratorio,muestra_codmuestra,isotopo_codisotopo,isotopo_analisis_codanalisis,estacion_codprocedencia,masa,metaestable,actividad_medida,error_actividad_medida,lid_medida):
    salida=guardar_muestra(motivo_muestreo_codmuestreo,fecha_recogida_inicial,fecha_recogida_final,fecha_analisis,instalacion_codinstalacion,laboratorio_codlaboratorio,muestra_codmuestra,isotopo_codisotopo,isotopo_analisis_codanalisis,estacion_codprocedencia,masa,metaestable,float(actividad_medida.replace("-",".")),float(error_actividad_medida.replace("-",".")),float(lid_medida.replace("-",".")))
    return render(
        request,
        "dosisEstacion.html",
        {
            "valores": salida
        }
    )

# NORMALIZACION DE LA BASE DE DATOS VRAEX
@permission_required('auth.subida_vraex')
def ActualizarDB(request):
    user=request.user
    form = UploadFormCopuma()
    cur = connections["gestion_memoria"].cursor()
    cur.callproc("proc_updateDatabase")
    res = cur.fetchall()
    cur.close()
    return render(
        request,
        "subida_copuma.html",
        {
            'form': form,
            'user':user
        }
    )

# CARGA DE UN NUEVO VALOR DE PRODUCCION
@permission_required('auth.subida_vraex')
def InsertarProduccion(request,fecha_consumo,modulo_1,modulo_2):
    user=request.user
    form = UploadFormCopuma()
    p = ProduccionAlmaraz(fecha_consumo=fecha_consumo,modulo_1=modulo_1,modulo_2=modulo_2)
    p.save(using='gestion_memoria')
    return render(
        request,
        "subida_copuma.html",
        {
            'form': form,
            'user':user
        }
    )

# CONSULTA DE LOS LIMITES DE VRAEX
@permission_required('auth.verificacion_vraex')
def MostrarLimites(request):
    user=request.user

    valores = LimitesMaximos.objects.using('gestion_memoria').exclude(masa=0)
    return render(
        request,
        "valores_limites.html",
        {
            'user':user,
            'datos':valores
        }
    )

# CONSULTA DE LOS LIMITES DE VRAEX
@permission_required('auth.verificacion_vraex')
def MostrarSinLimites(request):
    user=request.user

    valores = LimitesMaximos.objects.using('gestion_memoria').filter(limite_maximo=99).exclude(masa=0)
    return render(
        request,
        "sin_valor_limite.html",
        {
            'user':user,
            'datos':valores
        }
    )

