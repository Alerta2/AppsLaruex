
#from timetrackpro.views import *
from django.urls import path
from django.conf.urls import url
from .views import *
from django.conf.urls.static import static
from django.conf.urls import url

app_name = 'timetrackpro'

urlpatterns = [
    path('private/timetrackpro/', home ,name='home'),
    path('private/timetrackpro/documentacion', documentacion ,name='documentacion'),
    path('private/timetrackpro/perfil', perfil ,name='perfil'),
    path('private/timetrackpro/404', noEncontrado ,name='404'),
    path('private/timetrackpro/sin-permiso', sinPermiso ,name='sin-permiso'),

    # permisos de la aplicación
    path('private/timetrackpro/habilitaciones', habilitaciones ,name='habilitaciones'),
    path('private/timetrackpro/agregar-habilitacion', agregarHabilitacion ,name='agregar-habilitacion'),
    path('private/timetrackpro/modificar-habilitacion', modificarHabilitacion ,name='modificar-habilitacion'),
    path('private/timetrackpro/eliminar-habilitacion', eliminarHabilitacion ,name='eliminar-habilitacion'),
    path('private/timetrackpro/asociar-habilitacion', asociarHabilitacion ,name='asociar-habilitacion'),
    path('private/timetrackpro/datos-django-users', datosDjangoUsers ,name='datos-django-users'),

    path('private/timetrackpro/dashboard', dashBoard ,name='dashBoard'),
    path('private/timetrackpro/tablas', tablas ,name='tablas'),
    path('private/timetrackpro/facturacion', facturacion ,name='facturacion'),
    path('private/timetrackpro/realidadVirtual', realidadVirtual ,name='realidadVirtual'),
    path('private/timetrackpro/sign-in', signIn ,name='sign-in'),
    path('private/timetrackpro/sign-up', signUp ,name='sign-up'),

    # registros de las tarjetas de acceso
    path('private/timetrackpro/tarjetas-de-acceso', tarjetasAcceso ,name='tarjetas-de-acceso'),
    path('private/timetrackpro/agregar-tarjeta', agregarTarjetaAcceso ,name='agregar-tarjeta'),
    path('private/timetrackpro/tarjeta/<slug:id>', verTarjetaAcceso ,name='ver-tarjeta-acceso'),
    path('private/timetrackpro/editar-tarjeta', editarTarjetaAcceso ,name='editar-tarjeta-acceso'),
    path('private/timetrackpro/info-configuracion-tarjetas', infoConfigTarjetasAcceso ,name='info-configuracion-tarjetas'),


    # registros insertados en la base de datos  
    path('private/timetrackpro/agregar-registro', agregarRegistro , name='agregar-registro'),
    path('private/timetrackpro/registros-insertados', registrosInsertados , name='registros-insertados'),
    path('private/timetrackpro/datos-registros-insertados', datosRegistrosInsertados , name='registros-insertados'),
    path('private/timetrackpro/ver-registro/<slug:id>/', verRegistro , name='ver-registro'),
    path('private/timetrackpro/datos-registro/<slug:id>/', datosRegistro , name='datos-registro'),
    path('private/timetrackpro/ver-linea-registro/<slug:id>/', verLineaRegistro , name='ver-linea-registro'),
    path('private/timetrackpro/editar-linea-registro/<slug:id>/', editarLineaRegistro , name='editar-linea-registro'),
    path('private/timetrackpro/eliminar-linea-registro/<slug:id>/', eliminarLineaRegistro , name='eliminar-linea-registro'),
    path('private/timetrackpro/obtener-registro/', obtenerRegistro , name='obtener-registro'),
    path('private/timetrackpro/obtener-registro/<slug:year>', obtenerRegistro , name='obtener-registro'),
    path('private/timetrackpro/obtener-registro/<slug:year>/<slug:mes>/', obtenerRegistro , name='obtener-registro'),
    path('private/timetrackpro/obtener-registro/<slug:year>/<slug:mes>/<slug:semana>/', obtenerRegistro , name='obtener-registro'),
    # información de los registros por cada empleado Laruex
    path('private/timetrackpro/obtener-registro-empleados/', obtenerRegistroUsuario , name='obtener-registro-empleados'),
    path('private/timetrackpro/obtener-registro-empleados/<slug:id>/<slug:year>', obtenerRegistroUsuario , name='obtener-registro-empleados'),
    path('private/timetrackpro/obtener-registro-empleados/<slug:id>/<slug:year>/<slug:mes>/', obtenerRegistroUsuario , name='obtener-registro-empleados'),
    path('private/timetrackpro/obtener-registro-empleados/<slug:id>/<slug:year>/<slug:mes>/<slug:semana>/', obtenerRegistroUsuario , name='obtener-registro-empleados'),
    # información de los empleados del Laruex
    path('private/timetrackpro/agregar-usuario', agregarUsuario , name='agregar-usuario'),
    path('private/timetrackpro/datos-empleados/', datosEmpleados , name='datos-empleados'),
    path('private/timetrackpro/empleados/', empleados , name='empleados'),
    path('private/timetrackpro/ver-empleado/<slug:id>/', verEmpleado , name='ver-empleado'),
    path('private/timetrackpro/editar-empleado/<slug:id>/', editarEmpleado , name='editar-empleado'),

    # información de los usuarios del sistema
    path('private/timetrackpro/asociar-usuario/', asociarUsuario , name='asociar-usuario'),
    path('private/timetrackpro/editar-asociar-usuario/<slug:id>/', editarAsociarUsuario , name='editar-asociar-usuario'),

    # información de los usuarios del control de acceso 
    path('private/timetrackpro/agregar-usuario-maquina', agregarUsuarioMaquina , name='agregar-usuario-maquina'),
    path('private/timetrackpro/usuarios-maquina/', usuariosMaquina , name='usuarios-maquina'),
    path('private/timetrackpro/datos-usuarios-maquina/', datosUsuariosMaquina , name='datos-usuarios-maquina'),
    path('private/timetrackpro/ver-usuario-maquina/<slug:id>/', verUsuarioMaquina , name='ver-usuario-maquina'),

    #solicitudes de vacaciones
    path('private/timetrackpro/solicitudes/', solicitudes , name='solicitudes'),

    # festivos
    path('private/timetrackpro/datos-festivos-calendario/<slug:year>/', datosFestivosCalendario , name='datos-festivos-calendario'),
    path('private/timetrackpro/datos-festivos-calendario/', datosFestivosCalendario , name='datos-festivos-calendario'),
    
    path('private/timetrackpro/calendario-festivos/<slug:mes>/<slug:year>/', calendarioFestivos , name='calendario-festivos'),
    path('private/timetrackpro/calendario-festivos/<slug:mes>/', calendarioFestivos , name='calendario-festivos'),
    path('private/timetrackpro/festivos/', festivos , name='festivos'),
    path('private/timetrackpro/festivos/<slug:year>/', festivos , name='festivos-year'),
    path('private/timetrackpro/agregar-festivo/', agregarFestivo , name='agregar-festivo'),
    path('private/timetrackpro/agregar-festivo-desde-calendario/', agregarFestivoCalendario , name='agregar-festivo-desde-calendario'),
    path('private/timetrackpro/agregar-festivo/<slug:id>/', editarFestivo , name='editar-festivo'),
    path('private/timetrackpro/agregar-festivo/<slug:id>/', eliminarFestivo , name='eliminar-festivo'),

    # información relacionada con los empleados
    path('private/timetrackpro/errores-en-registros/<slug:mes>/', erroresRegistro , name='errores-en-registros'),
    path('private/timetrackpro/errores-en-registros/<slug:idEmpleado>/<slug:year>/<slug:mes>/', erroresRegistroEmpleado , name='errores-en-registros-empleado'),

    #Permisos
    path('private/timetrackpro/permisos/', permisos , name='permisos'),
    path('private/timetrackpro/permisos/<slug:year>/', permisos , name='permisos'),
    path('private/timetrackpro/datos-permisos/', datosPermisos , name='datos-permisos'),
    path('private/timetrackpro/datos-permisos/<slug:year>/', datosPermisos , name='datos-permisos'),
    path('private/timetrackpro/agregar-permiso/', agregarPermiso , name='agregar-permiso'),
    path('private/timetrackpro/ver-permiso/<slug:id>/', verPermiso , name='ver-permiso'),
    path('private/timetrackpro/editar-permiso/', editarPermiso , name='editar-permiso'),

    #Registro control horario
    path('private/timetrackpro/insertar-registro-manual-mensual/', insertarRegistroManualMensual , name='insertar-registro-manual-mensual'),
    path('private/timetrackpro/insertar-registro-manual/', insertarRegistroManual , name='insertar-registro-manual'),

    #Registro de errores
    path('private/timetrackpro/notificar-error-fichaje/', notificarErrorEnFichaje , name='notificar-error-fichaje'),
    path('private/timetrackpro/ver-errores-notificados/', verErroresNotificados , name='ver-errores-notificados'),
    path('private/timetrackpro/ver-errores-notificados-pendientes/', verErroresNotificadosPendientes , name='ver-errores-notificados-pendientes'),
    path('private/timetrackpro/datos-errores-notificados-pendientes/', datosErroresNotificadosPendientes , name='datos-errores-notificados-pendientes'),
    path('private/timetrackpro/ver-errores-notificados/<slug:id>/', verErroresNotificados , name='ver-errores-notificados'),
    path('private/timetrackpro/datos-errores-notificados/', datosErroresNotificados , name='datos-errores-notificados'),
    path('private/timetrackpro/datos-errores-notificados/<slug:id>/', datosErroresNotificados , name='datos-errores-notificados'),
    path('private/timetrackpro/ver-error-registro-notificado/<slug:id>/', verErrorRegistroNotificado , name='ver-error-registro-notificado'),
    path('private/timetrackpro/editar-error-registro-notificado/<slug:id>/', editarErrorRegistroNotificado , name='editar-error-registro-notificado'),
    path('private/timetrackpro/modificar-estado-error-registro-notificado/<slug:id>/', modificarEstadoErrorRegistroNotificado , name='modificar-estado-error-registro-notificado'),
    path('private/timetrackpro/eliminar-error-registro-notificado/<slug:id>/', eliminarErrorRegistroNotificado ,  name='eliminar-error-registro-notificado'), 
    path('private/timetrackpro/ver-mis-errores-notificados', verMisErroresNotificados , name='ver-mis-errores-notificados'),
    path('private/timetrackpro/datos-mis-errores-notificados', datosMisErroresNotificados , name='datos-mis-errores-notificados'),


    #Solicitud de vacaciones
    path('private/timetrackpro/solicitar-dias/', accesoDirectoPermisos , name='solicitar-dias'),
    path('private/timetrackpro/solicitar-vacaciones/', solicitarVacaciones , name='solicitar-vacaciones'),
    path('private/timetrackpro/ver-solicitudes-vacaciones/', verSolicitudesVacaciones , name='ver-solicitudes-vacaciones'),
    path('private/timetrackpro/ver-solicitudes-vacaciones/<slug:id>/', verSolicitudesVacaciones , name='ver-solicitudes-vacaciones'),

]
