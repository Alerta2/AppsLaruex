from background_task import background
from datetime import datetime, timedelta, timezone
from .models import *
from django.db.models import Avg, StdDev
from django.http import JsonResponse
import json

#########################################################################
# DJANGO TASKS                                                          #
#########################################################################

# lanzar ejecución: python manage.py process_tasks
# lanzar ejecución eligiendo cola: python manage.py process_tasks --queue cola_prueba

# con queue definimos la cola a la que pertenece el proceso, podemos lanzar el script y que solo realice las tareas de esta cola
@background(queue='cola_prueba')
def pruebaBT():
    print("hola1")

# si llamamos a este método lo ejecutará en 60 segundos
@background(schedule=60)
def pruebaBT1():
    print("hola2")

# pruebaBT1() -- ejecutamos el método
# pruebaBT1(schedule=90) -- ejecutamos el método sobrescribiendo el tiempo de espera
# pruebaBT1.now() -- ejecutamos el método obligandolo a no esperar
# pruebaBT1(repeat=10, repeat_until=datetime.now()) -- ejecutamos el método cada 10 segundos hasta la fecha que digamos en repeat_until, podemos poner None en repeat_until

# pruebaBT(repeat=10, repeat_until=None)
#########################################################################

#########################################################################
# FUNCIONES OPERATIVAS                                                  #
#########################################################################

@background(queue='mantenimientoRarex')
def calcularMediasDiariasDosis():
    estaciones = [1, 2, 3, 4, 5 , 7, 8, 10, 11, 12, 13, 40, 53, 54, 55, 56, 57]
    dias = datetime.now(timezone.utc) - timedelta(days=2)
    fechaInicio = dias.replace(hour=0, minute=0, second=0)
    fechaFin = dias.replace(hour=23, minute=59, second=59)
    while fechaFin < datetime.now(timezone.utc):
        for estacion in estaciones:
            print("consultando " + str(estacion) + "...")
            valor = EstGamYRadioyodos.objects.using('rvra').filter(fecha_hora__gte=fechaInicio, fecha_hora__lte=fechaFin, canales=1, estaciones=estacion, valido=1).aggregate(Avg('valor'))
            if MediasDiarias.objects.using('rvra').filter(id_estacion__id=estacion, id_detector=0, id_canal__id=1, fecha=fechaInicio.date()).exists():
                mediaCalculada = MediasDiarias.objects.using('rvra').filter(id_estacion__id=estacion, id_detector=0, id_canal__id=1, fecha=fechaInicio.date()).get()
                mediaExistente = round(mediaCalculada.valor, 4)
                mediaNueva = round(valor["valor__avg"], 4)
                if mediaExistente == mediaNueva:
                    print("Valor de media para el día "+ str(fechaInicio.date()) +" es " + str(mediaExistente) + " y no varía.")
                else:
                    print("Valor de media para el día "+ str(fechaInicio.date()) +" es " + str(mediaExistente) + ". Mi valor calculado es:" + str(mediaNueva))
            else:
                if valor["valor__avg"] == None:
                    print("No hay valor de media para el día ")
                else:
                    print("No hay valor de media para el día "+ str(fechaInicio.date()) +". Mi valor calculado es:" + str(valor))

        fechaInicio += timedelta(days=1)
        fechaFin += timedelta(days=1)


@background(queue='mantenimientoRarex')
def calcularMediasDiariasEspectrometria():
    listaIsotopos = [0, 6, 15, 19, 20, 36, 38, 50]
    datosMonitorizar = DatosMonitorizablesDetectores.objects.using('rvra').filter(isotopo_id__id__lte=51).exclude(isotopo_id__id__in=listaIsotopos).order_by('can_det_est')
    print("DETECTOR - ISOTOPO - ANOMALOS SUBIDA - ANOMALOS BAJADA - TOTAL VALORES - TOTAL VALORES VALIDOS - MESES MAL - MEDIA(actividad, amd, desviacion)")
    reporte = []
    detectorCreado = []
    for dato in datosMonitorizar:
        valoresAnualesTotales = EstEspecGamma.objects.using('rvra_historico').filter(fecha_hora__year=2021, relacion_detectores_estacion_id=dato.can_det_est.id, isotopos_id=dato.isotopo_id.id)
        valoresAnuales = valoresAnualesTotales.filter(valido=1)
        mediaConsultada = valoresAnuales.aggregate(Avg('actividad'),Avg('amd'),StdDev('amd'))
        meses = consultarMeses(valoresAnuales, mediaConsultada["amd__avg"], mediaConsultada["amd__stddev"])
        anomalosSubida = consultarSubidas(valoresAnuales, mediaConsultada["amd__avg"], mediaConsultada["amd__stddev"])
        anomalosBajada = consultarBajadas(valoresAnuales, mediaConsultada["amd__avg"], mediaConsultada["amd__stddev"])

        if not(dato.can_det_est in detectorCreado):
            detectorCreado.append(dato.can_det_est)
            reporte.append({"Estacion":dato.estacion_id.nombre, "Detector":dato.can_det_est.id, "Meses":meses, "Anulados":[], "Revisables":[]})
        index = detectorCreado.index(dato.can_det_est)

        if anomalosSubida > len(valoresAnuales)*0.01 or anomalosBajada > len(valoresAnuales)*0.01:
            print("DETECTOR("+str(dato.can_det_est)+") ISOTOPO(id:"+str(dato.isotopo_id.id)+" : "+str(dato.isotopo_id.n_iso)+") SUBIDA("+str(anomalosSubida)+") BAJADA("+str(anomalosBajada)+") TOTAL("+str(len(valoresAnualesTotales))+") TOTAL_VALIDOS("+str(len(valoresAnuales))+") MESES("+str(12-meses.count("OK"))+"/12) MEDIA CONSULTADA("+str(round(mediaConsultada["actividad__avg"],2))+","+str(round(mediaConsultada["amd__avg"],2))+","+str(round(mediaConsultada["amd__stddev"],2))+")")
            reporte[index]["Revisables"].append({"Isotopo":dato.isotopo_id.id, "Subida": anomalosSubida, "Total Valores": len(valoresAnualesTotales), "Meses mal": str(12-meses.count("OK"))})
        else:
            valoresAnulados = anularSubidas(valoresAnuales, mediaConsultada["amd__avg"], mediaConsultada["amd__stddev"])
            reporte[index]["Anulados"].append({"Isotopo":dato.isotopo_id.id, "Valores": valoresAnulados})

    json_string = json.dumps({"Estaciones":reporte})
    with open('json_data.json', 'w') as outfile:
        json.dump(json_string, outfile)

def consultarMeses(valores, media, desviacion):
    meses=[]
    for i in range(12):
        valoresMes = valores.filter(fecha_hora__month=i+1).aggregate(Avg('actividad'),Avg('amd'),StdDev('amd'))
        if valoresMes["amd__stddev"] > desviacion:
            meses.append(round((valoresMes["amd__stddev"]/desviacion)*100,2))
        else:
            meses.append("OK")
    return meses

def consultarSubidas(valores, media, desviacion):
    contarValores = 0
    for valor in valores:
        if valor.actividad > media+desviacion*3 or valor.amd > media+desviacion*3:
            contarValores+=1
    return contarValores
    
def anularSubidas(valores, media, desviacion):
    valoresInvalidados = []
    for valor in valores:
        if valor.actividad > media+desviacion*3 or valor.amd > media+desviacion*3:
            #EstEspecGamma.objects.using('rvra_historico').filter(fecha_hora=valor.fecha_hora, relacion_detectores_estacion_id=valor.relacion_detectores_estacion_id, isotopos_id=valor.isotopo_id).update(valido=0)
            print("Se va a anular el valor " + str(valor.fecha_hora))
            valoresInvalidados.append({"fh":str(valor.fecha_hora),"act":valor.actividad,"amd":valor.amd})
    return valoresInvalidados

def consultarBajadas(valores, media, desviacion):
    contarValores = 0
    for valor in valores:
        if valor.amd == 0.0:
            contarValores+=1
    return contarValores


@background(queue='mantenimientoRarex')
def comprobacionMedias():
    listaIsotopos = [0, 6, 15, 19, 20, 36, 38, 50]
    datosMonitorizar = DatosMonitorizables.objects.using('rvra').filter(isotopo_id__id__lte=51).exclude(isotopo_id__id__in=listaIsotopos).order_by('can_det_est')
    for dato in datosMonitorizar:
        valoresAnuales = EstEspecGamma.objects.using('rvra_historico').filter(fecha_hora__year=2021, relacion_detectores_estacion_id=dato.can_det_est, isotopos_id=dato.isotopo_id.id, valido=1)
        mediaConsultada = valoresAnuales.aggregate(Avg('actividad'),Avg('amd'),StdDev('amd'))
        if dato.med_anio_ant == None:
            mediaActividadExistente = None
        else:
            mediaActividadExistente = round(dato.med_anio_ant,4)
        if dato.med_amd_anio_ant == None:
            mediaAmdExistente = None
        else:
            mediaAmdExistente = round(dato.med_amd_anio_ant,4)

        if mediaConsultada["actividad__avg"] != None:
            mediaActividad = round(mediaConsultada["actividad__avg"], 4)
        else:
            mediaActividad = None
        if mediaConsultada["amd__avg"] != None:
            mediaAmd = round(mediaConsultada["amd__avg"], 4)
        else:
            mediaAmd = None
        if mediaActividadExistente == mediaActividad:
            mensajeActividad = "Actividad igual, " + str(mediaActividadExistente) + ", " + str(mediaActividad)
        else:
            mensajeActividad = "Actividad distinta, " + str(mediaActividadExistente) + ", " + str(mediaActividad)
        if mediaAmdExistente == mediaAmd:
            mensajeAMD = "AMD igual, " + str(mediaAmdExistente) + ", " + str(mediaAmd)
        else:
            mensajeAMD = "AMD distinta, " + str(mediaAmdExistente) + ", " + str(mediaAmd)

        if mediaActividad != None:
            DatosMonitorizables.objects.using('rvra').filter(estacion_id=dato.estacion_id, can_det_est=dato.can_det_est, isotopo_id=dato.isotopo_id).update(med_anio_ant=mediaActividad)
        if mediaAmd != None:
            DatosMonitorizables.objects.using('rvra').filter(estacion_id=dato.estacion_id, can_det_est=dato.can_det_est, isotopo_id=dato.isotopo_id).update(med_amd_anio_ant=mediaAmd)
        print("DETECTOR("+str(dato.can_det_est)+") ISOTOPO(id:"+str(dato.isotopo_id.id)+" : "+str(dato.isotopo_id.n_iso)+") - " + mensajeActividad + " - " + mensajeAMD)
        
            
#calcularMediasDiariasDosis(repeat=task.DAILY, repeat_until=None)
calcularMediasDiariasEspectrometria.now()
#comprobacionMedias.now()
#########################################################################
