from rare.models import *
import pytz
from datetime import datetime, timedelta, timezone
import pandas as pd
from django.db.models import F, Q
from django.contrib.auth.models import User

def consultarAnalista():
    tzInfo = pytz.timezone('Europe/Madrid')
    fecha_hora_actual = datetime.now().astimezone(tzInfo)
    today = fecha_hora_actual.strftime("%Y-%m-%d")
    current_time = fecha_hora_actual.strftime("%H:%M:%S")

    #Obtengo a los analistas que se encuentran de guardia para el area especificada (id_area -> Rarex = 1, Informatica = 2, Spida = 3)
    analistas = CalendarioGuardiasGuardias.objects.using('guardias'
            ).filter(id_turno__id_area=1,
                    valido = 1, 
                    supervisado = 1,
                    fecha_local_start__lte = today,
                    fecha_local_end__gte = today
            ).filter(id_turno__hora_local_comienzo__lte = current_time, 
                    id_turno__hora_local_fin__gte=current_time
            ).annotate(id_user=F('id_user_analista'), 
                    area=F('id_turno__id_area__nombre'), 
                    hora_entrada= F('id_turno__hora_local_comienzo'),
                    hora_salida= F('id_turno__hora_local_fin'),
                    icono = F('id_turno__id_area__icono')
            ).values('id_user','area', 'hora_entrada', 'hora_salida','icono').order_by('-id_guardia')
        
    #Obtengo la informacion del personal que esta activo de guardia en estos momentos
    if analistas.count()>0:
        df_analista = pd.DataFrame(analistas)
        df_analista = df_analista.drop_duplicates(subset = ["area"]) # Me quedo unicamente con el primer analista que debe encontrarse de guardia
        df_analista["nombre"] = df_analista.apply(lambda row : User.objects.get(id=row['id_user']).first_name, axis = 1)
        return df_analista

def consultarInformados():
    analistaGuardia = consultarAnalista().iloc[0].id_user
    return list(CalendarioPersonal.objects.using('guardias').filter(Q(id_usuario=analistaGuardia) | Q(supervisor=1) | Q(superinformado=1)).values_list("id_usuario", flat=True))

def consultarTelefonosInformados():    
        print("informados", consultarInformados()) 
        return list(StructureProfile.objects.filter(user_id__in=consultarInformados()).values_list("telefono", flat=True))