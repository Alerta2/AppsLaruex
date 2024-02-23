from django.http.response import JsonResponse
from docLaruex.models import *

# comprueba si el usuario es administrador
def esAdministrador(id_user):
    return RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo='Administrador').exists()

# comprueba si el usuario es administrador
def esDirector(id_user):
    if RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo='Director Técnico') or RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo='Subdirector Técnico') :
        return True
    else:
        return False
