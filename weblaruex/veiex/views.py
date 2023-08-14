from django.shortcuts import render
from .models import Estaciones, UltimosValores, ValoresVeiex, UmbralesVle, Flags, IndicesCalidadAire, PromediosVeiex
from django.db.models import F, Max, Func, Value, CharField, Case, When, Q, Count
from django.db.models.functions import Concat
from django.http import JsonResponse
import pandas as pd
import json
from datetime import datetime, timezone, timedelta
from dateutil import tz
import pytz
import numpy as np
import random
from django.conf import settings
from django.http import FileResponse
# Create your views here.

def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

def PerfilVeiex(request):
    '''Pagina de edición del perfil del usuario'''
    user=request.user

    if request.method == 'POST':
        info=request.POST # get info del POST 
        user.first_name=info.get("first_name")
        user.last_name=info.get("last_name")
        user.email=info.get("email")
        user.save()
      
        # Devuelvo un mensaje informativo
        mensaje={}
        mensaje["title"]='El perfil del usuario ha sido actualizado'
        mensaje["text"]=""
        mensaje["icon"]="success"
        mensaje["timer"]=2000

        return render(request,"perfil_veiex.html",{"user": user, "mensaje": mensaje})
    
    else:
        
        return render(request,"perfil_veiex.html",{"user": user})


def MapaVeiex(request):
    '''Visor de datos en tiempo real (Mapa Veiex)'''

    user=request.user

    if user.is_authenticated:
        filters = {
            'visualizar': 1,
        }
    else:
        filters = {
            'visualizar': 1,
        }

    estaciones= Estaciones.objects.using('veiex'
    ).filter(**filters
    ).annotate(
        I=F('id_estacion'),
        Nombre=F('nombre'),
        Foco = F('foco'),
        Lat = F('estacion_lat'),
        Lon = F('estacion_lon')
    ).values('I','Nombre', 'Foco', 'Lat', 'Lon').order_by('Nombre')
    
    return render(request,"mapa_veiex.html",{"user": user, "listaEstaciones": estaciones})


def HomeVeiex(request):
    '''Pagina de inicio (Home Spida)'''
    
    user=request.user
    
    return render(request,"home_veiex.html",{"user": user})



def getInfoEstacion(request):
    '''Obtiene la información de una estacion'''

    user = request.user

    result = {}
    idEstacion=request.GET.get('i',None)

    # Si no obtuve respuesta 
    if idEstacion is None:
        return JsonResponse(result, safe=False)

    # Extraigo la informacion de la estacion
    infoEstacion= Estaciones.objects.using('veiex'
        ).filter(id_estacion= int(idEstacion)
        ).annotate(
            I=F('id_estacion'),
            Nombre=F('nombre'),
            Foco=F('foco'),
            Lat=F('estacion_lat'),
            Lon=F('estacion_lon'),
            Denominacion = F('denominacion'),
            Proceso = F('proceso_asociado')
        ).values('I','Nombre','Foco','Lat','Lon', 'Denominacion', 'Proceso')

    if len(infoEstacion)>0:
        df_infoEstacion = pd.DataFrame(infoEstacion)
        result['info_estacion'] = df_infoEstacion.to_dict('records')[0]

    # Extraigo los flags de validación
    flags =  Flags.objects.using('veiex'
        ).filter(validacion = 1
        ).annotate(
            Flag = F('codificacion'), 
            Descripcion = F('descripcion'),
            Color = F('color')
        ).values('Flag', 'Descripcion', 'Color'
        ).order_by('-Descripcion')
    
    if len(flags)>0:
        df_flags = pd.DataFrame(flags)
        result['flags'] = df_flags.to_dict('records')

    # Extraigo los ICA (Indices de Calidad del Aire)
    ica =  IndicesCalidadAire.objects.using('veiex'
        ).annotate(
            #Min = F('minimo'),
            #Max = F('maximo'),
            Rango = Case(
                        When(Q(minimo__isnull=True) & Q(maximo__isnull=True), then=F('nombre')),
                        When(maximo__isnull=True, then=Concat(Value("Más de "), F('minimo'), output_field=CharField())),
                        default=Concat(Value("De "), F('minimo'), Value(" a "), F('maximo'), output_field=CharField()),
                        output_field=CharField()
                    ), 
            Nombre = F('nombre'),
            Descripcion = F('descripcion'),
            Instruccion = F('instruccion'),
            Color = F('color'),
            Icono = F('icono')
        ).values('Rango', 'Nombre', 'Descripcion', 'Instruccion', 'Color', 'Icono' #,'Min', 'Max' 
        ).order_by('minimo')
    
    if len(ica)>0:
        df_ica = pd.DataFrame(ica)
        result['ica'] = df_ica.to_dict('records')


    # Extraigo los ultimos valores registrados de la estacion (solo los contaminantes)
    ultimosValores= UltimosValores.objects.using('veiex'
        ).filter(
            id_estacion = int(idEstacion), 
            valido = 1
        ).annotate(
            Parametro = F('id_canal__nombre'),
            Acronimo = F('id_canal__acronimo'),
            Unidades = F('id_canal__unidades'),
            UTC = F('fecha_hora_utc'),
            FechaHora = F('fecha_hora_local'),
            Valor = F('valor'),
            Flag = F('codificacion'),
            Estado = F('codificacion__descripcion'),
            C = F('id_canal')
        ).values('Parametro','Acronimo','Unidades','UTC','FechaHora', 'Valor', 'C', 'Flag', 'Estado')


    if len(ultimosValores)>0:
        df_contaminantes = pd.DataFrame(ultimosValores.exclude(id_canal__contaminante=0))
        df_parametros = pd.DataFrame(ultimosValores.exclude(id_canal__contaminante=1))

        vle = UmbralesVle.objects.using('veiex'
            ).filter(id_estacion = int(idEstacion)
            ).annotate(
                C = F('id_canal'),
                VLE = F('vle')
            ).values('C','VLE')
        
        
        if len(vle)>0:
            df_vle = pd.DataFrame(vle)
            
            if len(df_contaminantes)>0:
                df_contaminantes = pd.merge(df_contaminantes, df_vle, on = ['C'], how='left')
                df_contaminantes = df_contaminantes.replace({np.nan: None})
            if len(df_parametros)>0:
                df_parametros = pd.merge(df_parametros, df_vle, on = ['C'], how='left')
                df_parametros = df_parametros.replace({np.nan: None})

        result['contaminantes'] = df_contaminantes.to_dict('records')
        result['parametros'] = df_parametros.to_dict('records')

    
    return JsonResponse(result, safe=False)

def getDatos(request):

    '''Obtiene los valores registrados para una estacion, canal y rango de horas concreta'''

    user = request.user
    
    result={}
    idEstacion=request.GET.get('i',None)
    idCanal=request.GET.get('c',None)
    numHoras=request.GET.get('h',None)
    fechaUTC = request.GET.get('dt', None)

    if idEstacion is not None and idCanal is not None and numHoras is not None:

        if fechaUTC is None:
            filters = {
                'id_estacion' : int(idEstacion),
                'id_canal' : int(idCanal),
                'fecha_hora_utc__gte' : datetime.now(timezone.utc) - timedelta(hours=int(numHoras))
            }
        else:
            filters = {
                'id_estacion' : int(idEstacion),
                'id_canal' : int(idCanal),
                'fecha_hora_utc__gte' : datetime.strptime(fechaUTC,'%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=int(numHoras))
            }
        #print(fechaUTC, datetime.strptime(fechaUTC,'%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=int(numHoras)), (datetime.strptime(fechaUTC,'%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=int(numHoras))).astimezone(tz=pytz.utc))
        valores = ValoresVeiex.objects.using('veiex'
                ).filter(**filters
                ).annotate(
                    LOCAL = F('fecha_hora_local'),
                    Flag = F('codificacion'),
                    Estado = F('codificacion__descripcion'),
                    Color = F('codificacion__color')
                ).values('LOCAL', 'valor', 'Flag', 'Estado', 'Color'
                ).order_by('LOCAL')
        if len(valores)>0:
            df_valores = pd.DataFrame(valores)
            result = df_valores.to_dict('records')
    
    return JsonResponse(result, safe=False)  


def getMaximosDiarios(request):

    '''Obtiene los valores máximos por día'''
    
    result = {}

    year = datetime.now().year

    idEstacion=request.GET.get('i',None)
    idCanal=request.GET.get('c',None)
    fechaUTC = request.GET.get('dt', None)

    #PRUEBA
    year = datetime.strptime(fechaUTC,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).year
    #VALIDO
    #year = datetime.now().year
    result['year'] = year

    if idEstacion is not None and idCanal is not None and fechaUTC is not None:

        valores_maximos = ValoresVeiex.objects.using('veiex'
                        ).filter(
                            id_estacion = int(idEstacion),
                            id_canal = int(idCanal),
                            fecha_hora_local__year = year,
                            codificacion = 'V'
                        ).extra({'Fecha':"date(fecha_hora_local)"}
                        ).values("Fecha").order_by("Fecha").annotate(Valor = Max("valor"))

        if len(valores_maximos)>0:
            df_valores_maximos = pd.DataFrame(valores_maximos)
            df_valores_maximos['Fecha'] =  pd.to_datetime(df_valores_maximos['Fecha'], format='%Y-%m-%d')
            df_valores_maximos['x'] = df_valores_maximos.apply(lambda row :  row["Fecha"].day - 1, axis = 1)
            df_valores_maximos['y'] = df_valores_maximos.apply(lambda row :  row["Fecha"].month - 1, axis = 1)
              
            result['maximos_diarios'] = df_valores_maximos.to_dict('records')
  

    return JsonResponse(result, safe=False)  

def getActividadIndustrial(request):

    '''Calcula los periodos de actividad industrial anual'''

    result = {} 

    idEstacion=request.GET.get('i',None)

    #PRUEBA
    #year = datetime.strptime(fechaUTC,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).year
    #VALIDO
    #year = datetime.now().year
    #result['year'] = year
    dia = 2
    mes = 1
    year = 2022

    print(datetime.now() - timedelta(days=445))

    if idEstacion is not None:

        # Creo un dataframe con todas las fecha/hora del año (dosminutal) desde el 1 de Enero hasta el 31 de Diciembre
        df_aux = pd.DataFrame()
        df_aux['Fecha'] = pd.date_range(datetime(year,1,1), datetime(year,12,31,23,58,0), freq='2min')
        #PRUEBA
        #df_aux = df_aux.loc[df_aux['Fecha'] < datetime.now() - timedelta(days=445)]
        df_aux = df_aux.loc[df_aux['Fecha'] < datetime.now()]
        df_aux['Fecha'] =  pd.to_datetime(df_aux['Fecha']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')


        # Obtengo los valores distintos por fecha/hora (dosminutal) y tipo flag
        valores = ValoresVeiex.objects.using('veiex'
                        ).filter(
                            id_estacion = int(idEstacion),
                            fecha_hora_local__year = year,
                            #fecha_hora_local__day__in = [1,2,3],
                            #fecha_hora_local__month = mes,
                        ).annotate(Flag = F('codificacion'), Fecha = F('fecha_hora_local')
                        ).values("Fecha",'Flag'
                        ).order_by("Fecha"
                        ).distinct()


        if len(valores)>0:
            df_valores = pd.DataFrame(valores)
            df_valores['Fecha'] =  pd.to_datetime(df_valores['Fecha']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')

            # PRUEBA (para saber si no hay datos durante algun periodo de tiempo)
            df_valores = df_valores.drop([df_valores.index[1], df_valores.index[2]])
        
            df = pd.merge(df_aux, df_valores, on = ['Fecha'], how='left')
            df = df.replace({np.nan: None})

            # Obtengo las Fecha/Hora unicas
            arr_dates = df['Fecha'].unique()

            data_aux = []
            for date in arr_dates:
                print("DATE", date)
                
                # Por Fecha/Hora unica obtengo los Flags unicos
                rslt_df = df[df['Fecha'] == date] 
                arr_flags = rslt_df.Flag.unique()

                data_aux.append(
                    {
                        'Fecha': date,
                        'Flags': arr_flags.tolist(),
                        'Propiedades':  tipoActividad(arr_flags)
                    }
                )
            
            if len(data_aux)>0:
                df_actividad = pd.DataFrame(data_aux)

                # Añado una nueva columna para identificar los valores consecutivos distintos
                df_actividad['match'] = df_actividad['Propiedades'].str['Valor'].eq(df_actividad['Propiedades'].str['Valor'].shift())

                # Filtro por los valores distintos para sacar los rangos de actividad, inactividad o sin datos
                df_actividad = df_actividad[df_actividad['match']==False]
                df_actividad['Start'] = df_actividad['Fecha']
                df_actividad['End'] = df_actividad['Fecha'].shift(-1)
                df_actividad = df_actividad.replace({np.nan: None})
                df_actividad = df_actividad.replace({None: datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')})
                df_actividad = df_actividad.drop(['Fecha','match'], axis=1)
                print(df_actividad)

                result['year'] = year
                result['valores'] = df_actividad.to_dict('records')

    return JsonResponse(result, safe=False)  


def getActividadEfectiva(request):

    result = {} 

    idEstacion=request.GET.get('i',None)

    #PRUEBA
    #year = datetime.strptime(fechaUTC,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).year
    #VALIDO
    #year = datetime.now().year
    #result['year'] = year
    year = 2022

    print(datetime.now() - timedelta(days=445))

    if idEstacion is not None:

        # Obtengo los valores distintos por fecha/hora (dosminutal) y tipo flag
        valores = ValoresVeiex.objects.using('veiex'
                        ).filter(
                            id_estacion = int(idEstacion),
                            fecha_hora_local__year = year,
                            id_canal__in=[1,2,3,4]
                        ).exclude(codificacion='I')
        
        actividad_total = len(valores)
        actividad_efectiva = len(valores.filter(codificacion='V'))

        porcentaje_efectivo = round(actividad_efectiva*100/actividad_total,3)
        result["global"] = {'efectivo': porcentaje_efectivo, 'anomalo': round(100-porcentaje_efectivo,3)}

        values_monoxido = valores.filter(id_canal = 1)
        actividad_total = len(values_monoxido)
        actividad_efectiva = len(values_monoxido.filter(codificacion='V'))
        porcentaje_efectivo = round(actividad_efectiva*100/actividad_total,3)

        result["CO"] = {'efectivo': porcentaje_efectivo, 'anomalo': round(100-porcentaje_efectivo,3)}

        values_monoxido = valores.filter(id_canal = 2)
        actividad_total = len(values_monoxido)
        actividad_efectiva = len(values_monoxido.filter(codificacion='V'))
        porcentaje_efectivo = round(actividad_efectiva*100/actividad_total,3)

        result["NOX"] = {'efectivo': porcentaje_efectivo, 'anomalo': round(100-porcentaje_efectivo,3)}

        values_monoxido = valores.filter(id_canal = 3)
        actividad_total = len(values_monoxido)
        actividad_efectiva = len(values_monoxido.filter(codificacion='V'))
        porcentaje_efectivo = round(actividad_efectiva*100/actividad_total,3)

        result["SO2"] = {'efectivo': porcentaje_efectivo, 'anomalo': round(100-porcentaje_efectivo,3)}

        values_monoxido = valores.filter(id_canal = 4)
        actividad_total = len(values_monoxido)
        actividad_efectiva = len(values_monoxido.filter(codificacion='V'))
        porcentaje_efectivo = round(actividad_efectiva*100/actividad_total,3)

        result["PT"] = {'efectivo': porcentaje_efectivo, 'anomalo': round(100-porcentaje_efectivo,3)}
    return JsonResponse(result, safe=False) 


def tipoActividad(arr_flags):

    if len(arr_flags)>0 and None in arr_flags:
        return {
                "Valor": -2,
                "Nombre": "Inoperatividad",
                "Color": 'grey'
                } # Sin datos

    if len(arr_flags)==1 and 'I' in arr_flags:
        return {
                "Valor": -1,
                "Nombre": "Inactividad",
                "Color": 'black'
                } # Inactividad

    if len(arr_flags)>0 and 'I' not in arr_flags:
        return  {
                "Valor": 1,
                "Nombre": "Actividad",
                "Color": 'green'
                } # Actividad

    if len(arr_flags)>1 and 'I' in arr_flags:
        return {
                "Valor": 0,
                "Nombre": "Actividad",
                "Color": 'yellow'
                } # Actividad e Inactividad simultanea
    
    return {
            "Valor": -3,
            "Nombre": "Error",
            "Color": 'red'
            } # Error


def getPromediosValidados(request):

    result = {} 

    idEstacion=request.GET.get('i',None)
    idCanal = request.GET.get('c', None)
    vle = request.GET.get('vle', None)

    if idEstacion is not None and idCanal is not None and vle is not None:

        # Obtengo los valores promedios semihorarios validados del año

        year = 2022

        promedios = PromediosVeiex.objects.using('veiex'
                        ).filter(
                            id_estacion = int(idEstacion),
                            contaminante = int(idCanal),
                            fecha_hora_local__year = year,
                            codificacion = '<'
                        )
        
        if len(promedios)>0:
            result['promedios_SH_totales'] = len(promedios.exclude(id_canal = 10)) # Promedios semihorarios
            
            # Obtengo los valores promedios semihorarios cuyos valores NO superan el 100% del VLE establecido
            promedios_sm_existentes = promedios.exclude(valor__gte = float(vle), id_canal = 10)
            result['promedios_SH_existentes'] = len(promedios_sm_existentes)
            result['promedio_SH_maximo'] = round(promedios.aggregate(Max('valor'))['valor__max'],2)
            result['porcentaje_SH_apto'] = round(len(promedios_sm_existentes)*100/len(promedios_sm_existentes), 2)
            result['cond_valor_125vle'] = True if result['promedio_SH_maximo'] <= float(vle)*1.25 else False
            result['cond_semihorario_100vle'] = True if result['porcentaje_SH_apto'] >= 94 else False
            
            if int(idCanal) == 5: # Excepcion Particulas totales
                # Obtengo el valor promedio diario máximo cuyo valor NO debe superar el 100% del VLE establecido
                promedios_d_existentes = promedios.exclude(id_canal = 9)
                if len(promedios_d_existentes)>0:
                    result['promedio_D_maximo'] = round(promedios_d_existentes.aggregate(Max('valor'))['valor__max'],2)
                    result['cond_diario_100vle'] = True if result['promedio_D_maximo'] <= float(vle) else False

    return JsonResponse(result, safe=False) 
       

       
# import urllib library
from urllib.request import urlopen
import requests
def getJSONActividadIndustrial(request):

    '''Obtiene el json con la actividad industrial anual de una estacion'''

    result = {}

    user=request.user

    idEstacion=request.GET.get('i',None)
    year = request.GET.get('y', None)

    if idEstacion is not None and year is not None:

        url = f"{settings.MEDIA_ROOT}/VEIEX/{(year)}_{(idEstacion)}_global.json"

        with open(url, 'rb') as j:
            result = json.loads(j.read())

    return JsonResponse(result, safe=False) 

def getDatosICA(request):
    
    result = {}

    year = datetime.now().year

    contaminantes=request.GET.get('c',None)
    print("CONTAMINANTES")
    if contaminantes is not None:
        print(contaminantes)

    return JsonResponse(result, safe=False)  