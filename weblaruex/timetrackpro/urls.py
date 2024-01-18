
#from timetrackpro.views import *
from django.urls import path, re_path
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
    path('private/timetrackpro/ups', ups ,name='ups'),
    path('private/timetrackpro/ups/<str:mensaje>/', ups ,name='ups'),

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
    path('private/timetrackpro/tarjeta/<slug:id>/', verTarjetaAcceso ,name='ver-tarjeta-acceso'),
    path('private/timetrackpro/editar-tarjeta', editarTarjetaAcceso ,name='editar-tarjeta-acceso'),
    path('private/timetrackpro/info-configuracion-tarjetas', infoConfigTarjetasAcceso ,name='info-configuracion-tarjetas'),
    path('private/timetrackpro/datos-tarjetas-de-acceso-activas', datosTarjetasAccesoActivas ,name='datos-tarjetas-de-acceso-activas'),
    path('private/timetrackpro/datos-tarjetas-de-acceso-inactivas', datosTarjetasAccesoInactivas ,name='datos-tarjetas-de-acceso-inactivas'),

    # registros insertados en la base de datos  
    path('private/timetrackpro/agregar-registro', agregarRegistro , name='agregar-registro'),
    path('private/timetrackpro/registros-insertados', registrosInsertados , name='registros-insertados'),
    path('private/timetrackpro/datos-registros-insertados', datosRegistrosInsertados , name='datos-registros-insertados'),
    path('private/timetrackpro/ver-registro/<slug:id>/', verRegistro , name='ver-registro'),
    path('private/timetrackpro/datos-registro/<slug:id>/', datosRegistro , name='datos-registro'),
    path('private/timetrackpro/ver-linea-registro/<slug:id>/', verLineaRegistro , name='ver-linea-registro'),
    path('private/timetrackpro/editar-linea-registro/<slug:id>/', editarLineaRegistro , name='editar-linea-registro'),
    path('private/timetrackpro/eliminar-linea-registro/<slug:id>/', eliminarLineaRegistro , name='eliminar-linea-registro'),

    # información de los registros por cada empleado Laruex
    path('private/timetrackpro/obtener-registro-empleados/', obtenerRegistroEmpleados , name='obtener-registro-empleados'),
    path('private/timetrackpro/datos-registro-empleados/', datosRegistroEmpleados , name='datos-registro-empleados'),
    path('private/timetrackpro/obtener-registro-semanal-empleados/', obtenerRegistroSemanalEmpleados , name='obtener-registro-empleados'),
    path('private/timetrackpro/datos-registro-semanal-empleados/', datosRegistroSemanalEmpleados , name='datos-registro-empleados'),
    #path('private/timetrackpro/datos-registro-empleados/<str:listEmpleados>/<slug:fechaInicio>/<slug:fechaFin>', datosRegistroUsuario , name='datos-registro-empleados'),

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

    # festivos
    path('private/timetrackpro/datos-festivos-calendario/<slug:year>/', datosFestivosCalendario , name='datos-festivos-calendario'),
    path('private/timetrackpro/datos-festivos-calendario/', datosFestivosCalendario , name='datos-festivos-calendario'),
    
    path('private/timetrackpro/calendario-festivos/<slug:mes>/<slug:year>/', calendarioFestivos , name='calendario-festivos'),
    path('private/timetrackpro/calendario-festivos/<slug:mes>/', calendarioFestivos , name='calendario-festivos'),
    path('private/timetrackpro/calendario-festivos/', calendarioFestivos , name='calendario-festivos'),
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
    path('private/timetrackpro/lista-permisos/', listaPermisos , name='lista-permisos'),
    path('private/timetrackpro/lista-permisos/<slug:year>/', listaPermisos , name='lista-permisos'),
    path('private/timetrackpro/datos-lista-permisos/', datosListaPermisos , name='datos-lista-permisos'),
    path('private/timetrackpro/datos-lista-permisos/<slug:year>/', datosListaPermisos , name='datos-lista-permisos'),
    path('private/timetrackpro/agregar-permiso/', agregarPermiso , name='agregar-permiso'),
    path('private/timetrackpro/ver-permiso/<slug:id>/', verPermiso , name='ver-permiso'),
    path('private/timetrackpro/editar-permiso/', editarPermiso , name='editar-permiso'),
    path('private/timetrackpro/eliminar-permiso/', eliminarPermiso , name='eliminar-permiso'),

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
    path('private/timetrackpro/solicitudes/', solicitudes , name='solicitudes'),
    path('private/timetrackpro/solicitar-vacaciones/', solicitarVacaciones , name='solicitar-vacaciones'),
    path('private/timetrackpro/solicitar-modificar-vacaciones/', solicitarModificarVacaciones , name='solicitar-modificar-vacaciones'),

    #Solicitud de vacaciones
    path('private/timetrackpro/datos-festivos-vacaciones-empleado/', datosFestivosVacacionesEmpleado , name='datos-festivos-vacaciones-empleado'),
    path('private/timetrackpro/vacaciones-solicitadas/', vacacionesSolicitadas , name='vacaciones-solicitadas'),
    path('private/timetrackpro/datos-vacaciones-solicitadas/', datosVacacionesSolicitadas , name='datos-vacaciones-solicitadas'),
    path('private/timetrackpro/datos-cambio-vacaciones-solicitadas/', datosCambioVacacionesSolicitadas , name='datos-cambio-vacaciones-solicitadas'),
    path('private/timetrackpro/datos-cambio-vacaciones-solicitadas/<slug:year>/', datosCambioVacacionesSolicitadas , name='datos-cambio-vacaciones-solicitadas'),
    path('private/timetrackpro/ver-cambio-vacaciones-seleccionadas/<slug:id>/', verCambioVacacionesSeleccionadas , name='ver-cambio-vacaciones-seleccionadas'),
    path('private/timetrackpro/datos-calendario-vacaciones-solicitadas/', datosCalendarioVacacionesSolicitadas , name='datos-calendario-vacaciones-solicitadas'),
    path('private/timetrackpro/ver-vacaciones-seleccionadas/<slug:id>/', verVacacionesSeleccionadas , name='ver-vacaciones-seleccionadas'),
    path('private/timetrackpro/modifcar-vacaciones/<slug:id>/', modificarVacaciones , name='modificar-vacaciones'),
    path('private/timetrackpro/cambiar-estado-vacaciones/<slug:id>/', cambiarEstadoVacaciones , name='cambiar-estado-vacaciones'),
    path('private/timetrackpro/eliminar-vacaciones/', eliminarVacaciones , name='eliminar-vacaciones'),
    path('private/timetrackpro/modifcar-cambio-vacaciones/<slug:id>/', modificarCambioVacaciones , name='modificar-cambio-vacaciones'),
    path('private/timetrackpro/cambiar-estado-cambio-vacaciones/<slug:id>/', cambiarEstadoCambioVacaciones , name='cambiar-estado-cambio-vacaciones'),
    path('private/timetrackpro/eliminar-cambio-vacaciones/', eliminarCambioVacaciones , name='eliminar-cambio-vacaciones'),
    
    #Solicitud de asuntos propios 
    path('private/timetrackpro/solicitar-asuntos-propios/', solicitarAsuntosPropios , name='solicitar-asuntos-propios'),
    path('private/timetrackpro/solicitar-asuntos-propios/<slug:year>/', solicitarAsuntosPropios , name='solicitar-asuntos-propios'),
    path('private/timetrackpro/datos-asuntos-propios/', datosAsuntosPropiosEmpleados , name='datos-asuntos-propios-empleados'),
    path('private/timetrackpro/datos-asuntos-propios/<slug:year>/', datosAsuntosPropiosEmpleados , name='datos-asuntos-propios-empleados'),
    path('private/timetrackpro/datos-asuntos-propios-admin/', datosAsuntosPropiosSolicitados , name='datos-asuntos-propios-solicitados'),
    path('private/timetrackpro/datos-asuntos-propios-admin/<slug:year>/', datosAsuntosPropiosSolicitados , name='datos-asuntos-propios-solicitados'),    
    path('private/timetrackpro/ver-solicitud-asuntos-propios/', verSolicitudAsuntosPropios , name='ver-solicitud-asuntos-propios'),
    path('private/timetrackpro/ver-solicitud-asuntos-propios/<slug:id>/', verSolicitudAsuntosPropios , name='ver-solicitud-asuntos-propios'),
    path('private/timetrackpro/datos-calendario-asuntos-propios/', datosCalendarioAsuntosPropios , name='datos-calendario-asuntos-propios'), 
    path('private/timetrackpro/datos-calendario-asuntos-propios/<slug:year>/', datosCalendarioAsuntosPropios , name='datos-calendario-asuntos-propios'), 
    path('private/timetrackpro/agregar-asuntos-propios-desde-calendario/', agregarAsuntosPropiosCalendario , name='agregar-asuntos-propios-desde-calendario'),
    path('private/timetrackpro/modificar-asuntos-propios/', modificarAsuntosPropios , name='modificar-asuntos-propios'),
    path('private/timetrackpro/solicitar-modificacion-asuntos-propios/', solicitarModificarAsuntosPropios , name='solicitar-modificacion-asuntos-propios'),
    path('private/timetrackpro/cambiar-estado-asuntos-propios/', cambiarEstadoAsuntosPropios , name='cambiar-estado-asuntos-propios'),
    path('private/timetrackpro/cambiar-estado-asuntos-propios/<slug:id>/', cambiarEstadoAsuntosPropios , name='cambiar-estado-asuntos-propios'),
    path('private/timetrackpro/eliminar-asuntos-propios/', eliminarAsuntosPropios , name='eliminar-asuntos-propios'),
    path('private/timetrackpro/eliminar-asuntos-propios/<slug:id>/', eliminarAsuntosPropios , name='eliminar-asuntos-propios'),
    path('private/timetrackpro/solicitar-modificar-asuntos-propios/', solicitarModificarAsuntosPropios , name='solicitar-modificar-asuntos-propios'),

    # permisos retribuidos
    path('private/timetrackpro/lista-permisos-retribuidos/', listaPermisosRetribuidos , name='lista-permisos-retribuidos'),
    path('private/timetrackpro/datos-lista-permisos-retribuidos/', datosListaPermisosRetribuidos , name='datos-lista-permisos-retribuidos'),    
    path('private/timetrackpro/agregar-permiso-retribuido/', agregarPermisoRetribuido , name='agregar-permiso-retribuido'),
    path('private/timetrackpro/ver-permiso-retribuido/<slug:id>/', verPermisoRetribuido , name='ver-permiso-retribuido'),
    path('private/timetrackpro/editar-permiso-retribuido/', editarPermisoRetribuido , name='editar-permiso-retribuido'),
    path('private/timetrackpro/eliminar-permiso-retribuido/', eliminarPermisoRetribuido , name='eliminar-permiso-retribuido'),

    
    #Solicitud de permisos retribuidos 
    path('private/timetrackpro/solicitar-permisos-retribuidos/', solicitarPermisosRetribuidos , name='solicitar-permisos-retribuidos'),
    path('private/timetrackpro/solicitar-permisos-retribuidos/<slug:year>/', solicitarPermisosRetribuidos , name='solicitar-permisos-retribuidos'),
    path('private/timetrackpro/solicitar-permiso-retribuido-desde-calendario/', solicitarPermisoRetribuidoCalendario , name='solicitar-permiso-rertibuido-desde-calendario'),
    path('private/timetrackpro/datos-permisos-retribuidos-empleados/', datosPermisosRetribuidosEmpleados , name='datos-permisos-retribuidos-empleados'),
    path('private/timetrackpro/datos-permisos-retribuidos-empleados/<slug:year>/', datosPermisosRetribuidosEmpleados , name='datos-permisos-retribuidos-empleados'),
    path('private/timetrackpro/datos-permisos-retribuidos-solicitados/', datosPermisosRetribuidosSolicitados , name='datos-permisos-retribuidos-solicitados'),
    path('private/timetrackpro/datos-permisos-retribuidos-solicitados/<slug:year>/', datosPermisosRetribuidosSolicitados , name='datos-permisos-retribuidos-solicitados'),
    path('private/timetrackpro/ver-solicitud-permisos-retribuidos/<slug:id>/', verSolicitudPermisosRetribuidos , name='ver-solicitud-permisos-retribuidos'),
    path('private/timetrackpro/modificar-solicitud-permiso-retribuido/', modificarSolicitudPermisoRetribuido , name='modificar-solicitud-permiso-retribuido'),
    path('private/timetrackpro/cambiar-estado-permisos-retribuidos/', cambiarEstadoSolicitudPermisoRetribuido , name='cambiar-estado-permisos-retribuidos'),
    path('private/timetrackpro/cambiar-estado-permisos-retribuidos/<slug:id>/', cambiarEstadoSolicitudPermisoRetribuido , name='cambiar-estado-permisos-retribuidos'),
    path('private/timetrackpro/eliminar-permisos-retribuidos/', eliminarSolicitudPermisoRetribuido , name='eliminar-permisos-retribuidos'),
    path('private/timetrackpro/eliminar-permisos-retribuidos/<slug:id>/', eliminarSolicitudPermisoRetribuido , name='eliminar-permisos-retribuidos'),
    path('private/timetrackpro/justificar-solicitud-permisos-retribuidos/', justicarSolicitudPermisosRetribuidos , name='justificar-solicitud-permisos-retribuidos'),
    path('private/timetrackpro/justificar-solicitud-permisos-retribuidos/<slug:id>/', justicarSolicitudPermisosRetribuidos , name='justificar-solicitud-permisos-retribuidos'),
    path('private/timetrackpro/descargar-solicitud-permisos-retribuidos/<slug:id>/', descargarSolicitudPermisosRetribuidos , name='descargar-solicitud-permisos-retribuidos'),
    path('private/timetrackpro/actualizar-justificante-solicitud-permisos-retribuidos/<slug:id>/', actualizarJustificanteSolicitudPermisosRetribuidos , name='actualizar-justificante-solicitud-permisos-retribuidos'),  

    #Informar de problemas
    path('private/timetrackpro/notificar-problemas', notificarProblemas , name='notificar-problemas'),  
    path('private/timetrackpro/notificar-datos-erroneos', notificarDatosErroneos , name='notificar-datos-erroneos'),  
    path('private/timetrackpro/notificar-errores-app', notificarErroresApp , name='notificar-errores-app'),   
    path('private/timetrackpro/listado-incidencias', problemasNotificados , name='listado-incidencias'),  
    path('private/timetrackpro/datos-listado-incidencias', datosProblemasNotificados , name='datos-listado-incidencias'), 
    path('private/timetrackpro/datos-listado-incidencias/<slug:tipo>/', datosProblemasNotificados , name='datos-listado-incidencias'),  
    path('private/timetrackpro/datos-listado-incidencias/<slug:estado>/', datosProblemasNotificados , name='datos-listado-incidencias'), 
    path('private/timetrackpro/datos-listado-incidencias/<slug:tipo>/<slug:estado>/', datosProblemasNotificados , name='datos-listado-incidencias'), 
    path('private/timetrackpro/ver-incidencia/<slug:id>/', verIncidencia , name='ver-incidencia'),
    path('private/timetrackpro/cambiar-estado-incidencia/<slug:id>/', cambiarEstadoIncidencia , name='cambiar-estado-incidencia'),
    path('private/timetrackpro/eliminar-incidencia/<slug:id>/', eliminarIncidencia , name='eliminar-incidencia'),

]