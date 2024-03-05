from django.http.response import JsonResponse
from timetrackpro.models import *

# comprueba si el usuario es administrador
def esAdministrador(id_user):
    return RelHabilitacionesUsuarioTimeTrackPro.objects.using("timetrackpro").filter(id_auth_user=id_user,id_habilitacion__nombre='Administrador').exists()

# comprueba si el usuario es administrador
def esDirector(id_user):
    if RelHabilitacionesUsuarioTimeTrackPro.objects.using("timetrackpro").filter(id_auth_user=id_user,id_habilitacion__nombre='Direccón') or RelHabilitacionesUsuarioTimeTrackPro.objects.using("timetrackpro").filter(id_auth_user=id_user,id_habilitacion__nombre='Subdirección / Secretaría') :
        return True
    else:
        return False
