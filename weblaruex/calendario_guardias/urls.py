from django.urls import path
from calendario_guardias.views import *
from django.contrib.auth.views import LoginView

app_name="calendario_guardias"

urlpatterns = [
    #Templates:
    path("private/operatividad/apps/", VisorOperatividadApps, name="VisorOperatividadApps"),  #Visor Calendario Guardias ALERTA2
    path("private/calendario/guardias/visor/", VisorCalendarioGuardias, name="VisorCalendarioGuardias"),  #Visor Calendario Guardias ALERTA2
    path('private/calendario/guardias/acceso/', LoginView.as_view(template_name='cg_acceso.html'), name="LoginCalendarioGuardias"), #Acceso o Login a la App Guardias
    path('private/calendario/guardias/perfil/', PerfilUsuario, name="PerfilUsuario"), #Configuración de Perfil de Usuario
    path('private/calendario/guardias/personal/', PersonalCalendarioGuardias, name="PersonalCalendarioGuardias"), #Personal adscrito a la app de guardias (analistas, informaticos ...)
    path('private/calendario/guardias/nuevo/', NuevoCalendarioGuardias, name="NuevoCalendarioGuardias"), #Creación de nuevo calendario de guardias 
    path('private/calendario/guardias/tablon/', MiTablonGuardias, name="MiTablonGuardias"), #Mi tablon con sustituciones cambios y mi calendario
    path('private/calendario/guardias/supervision/', SupervisionGuardias, name="SupervisionGuardias"), #Notificaciones
    path('private/calendario/guardias/historico/', HistoricoCambiosGuardia, name="HistoricoCambiosGuardia"), #Notificaciones
    path('confirmacion/aviso/', ConfirmacionTelegram, name="ConfirmacionTelegram"), #Confirmacion mensaje telegram
    path('acceso/analista/', LoginView.as_view(template_name='cg_acceso_confirmacion.html')), #Acceso o Login a la App Guardias

    #Datos:
    #Cargar informacion:
    path('private/calendario/guardias/datos/upd/perfil/', updatePerfilUsuarioGuardias, name="updatePerfilUsuarioGuardias"),
    path('private/calendario/guardias/datos/upd/festivos/', updateFestivos, name="updateFestivos"),
    path('private/calendario/guardias/nuevo/upd/calendario/rotatorio/', updateCalendarioRotatorio, name="updateCalendarioRotatorio"),
    path('private/calendario/guardias/nuevo/upd/calendario/rarex/', updateCalendarioRarex, name="updateCalendarioRarex"),

    #Obtener informacion:
    path('private/calendario/guardias/datos/areas/', getAreas, name="getAreas"), 
    path('private/calendario/guardias/datos/area/turnos/', getTurnosArea, name="getTurnosArea"),
    path('private/calendario/guardias/datos/area/personal/', getPersonalArea, name="getPersonalArea"),
    path('private/calendario/guardias/datos/area/guardias/year', getGuardiasYearArea, name="getGuardiasYearArea"),
    path('private/calendario/guardias/datos/area/analistas/', getAnalistasArea, name="getAnalistasArea"),
    path('private/calendario/guardias/datos/festivos/', getFestivos, name="getFestivos"),
    path('private/calendario/guardias/datos/colores/personal/', getColoresPersonal, name="getColoresPersonal"),
    path('private/calendario/guardias/datos/colores/usuarios/', getColoresUsuarios, name="getColoresUsuarios"),
    path('private/calendario/guardias/datos/colores/turno/', getColoresTurnos, name="getColoresTurnos"),
    path('private/calendario/guardias/datos/users/', getUsers, name="getUsers"), 
    path('private/calendario/guardia/datos/treeview/', getTreeViewAreasPersonal, name="getTreeViewAreasPersonal"),
    path('private/calendario/guardias/datos/guardias/', getGuardias, name="getGuardias"),
    path('private/calendario/guardias/datos/sustituto/', getSustituto, name="getSustituto"),
    path('private/calendario/guardias/datos/guardias/cambios/', getGuardiasCambios, name="getGuardiasCambios"),
    path('private/calendario/guardias/datos/tablon/sustituciones/', getSustituciones, name="getSustituciones"),
    path('private/calendario/guardias/datos/tablon/cambios/', getCambiosGuardias, name="getCambiosGuardias"),
    path('private/calendario/guardias/datos/guardias/personal/', getMisGuardias, name="getMisGuardias"),
    path('private/calendario/guardias/datos/supervision/sustituciones/', getSustitucionesPendientes, name="getSustitucionesPendientes"),
    path('private/calendario/guardias/datos/supervision/cambios/', getCambiosGuardiasPendientes, name="getCambiosGuardiasPendientes"),
    path('private/calendario/guardias/datos/supervision/cambios/historico', getHistoricoCambiosGuardias, name="getHistoricoCambiosGuardias"),
    path('private/estado/aplicaciones/', getEstadoApps, name="getEstadoApps"),
    path('private/calendario/guardias/prueba/', getHistorioContadorGuardias, name="getHistorioContadorGuardias"),



    path('private/calendario/guardias/setdata/sustitucion/', setSustitucion, name="setSustitucion"),
    path('private/calendario/guardias/setdata/sustitucion/supervisor/', setSustitucionSupervisor, name="setSustitucionSupervisor"),
    path('private/calendario/guardias/setdata/sustitucion/eliminar/', setEliminarSustitucion, name="setEliminarSustitucion"),
    path('private/calendario/guardias/setdata/sustitucion/aceptar/', setAceptarSustitucion, name="setAceptarSustitucion"),
    path('private/calendario/guardias/setdata/sustitucion/rechazar/', setRechazarSustitucion, name="setRechazarSustitucion"),
    path('private/calendario/guardias/setdata/cambio/', setCambioGuardia, name="setCambioGuardia"),
    path('private/calendario/guardias/setdata/cambio/directo/', setCambioGuardiaDirecto, name="setCambioGuardiaDirecto"),
    path('private/calendario/guardias/setdata/cambio/eliminar/', setEliminarCambioGuardia, name="setEliminarCambioGuardia"),
    path('private/calendario/guardias/setdata/cambio/aceptar/', setAceptarCambioGuardia, name="setAceptarCambioGuardia"),
    path('private/calendario/guardias/setdata/cambio/rechazar/', setRechazarCambioGuardia, name="setRechazarCambioGuardia"),
    path('private/calendario/guardias/mensaje/', setNuevoMensaje, name="setNuevoMensaje"),
    
    



    #Nuevos Calendarios
    path('private/calendario/guardias/nuevo/create/nueva/guardia/', createGuardia, name="createGuardia"),
    path('private/calendario/guardias/nuevo/create/calendario/rotatorio/', createCalendarRotatorio, name="createCalendarRotatorio"),
    path('private/calendario/guardias/nuevo/create/calendario/rarex/', createCalendarRarex, name="createCalendarRarex"),
    path('private/calendario/guardias/modifi/calendario/rotatorio/', modificarCalendarioRotatorio, name="modificarCalendarioRotatorio"),
    path('private/calendario/guardias/modifi/calendario/rarex/', modificarCalendarioRarex, name="modificarCalendarioRarex"),



    
]