from django.urls import path
from veiex.views import *
from django.contrib.auth.views import LoginView

app_name = 'veiex'


urlpatterns = [
    path('private/veiex/login/', LoginView.as_view(template_name='login_veiex.html'), name="LoginVeiex"),
    path('private/veiex/perfil/', PerfilVeiex, name="PerfilVeiex"),

    path('private/veiex/home/', HomeVeiex,name='HomeVeiex'),
    path('private/veiex/visor/', MapaVeiex,name='MapaVeiex'),

    path('private/veiex/datos/infoestacion/', getInfoEstacion, name="getInfoEstacion"), 
    path('private/veiex/datos/', getDatos, name="getDatos"), 
    path('private/veiex/datos/maximos/diarios/', getMaximosDiarios, name="getMaximosDiarios"), 
    path('private/veiex/datos/ica/', getDatosICA, name="getDatosICA"), 
    path('private/veiex/datos/actividad/industrial/', getActividadIndustrial, name="getActividadIndustrial"), 
    path('private/veiex/datos/actividad/industrial/json/', getJSONActividadIndustrial, name="getJSONActividadIndustrial"), 
    path('private/veiex/datos/actividad/efectiva/', getActividadEfectiva, name="getActividadEfectiva"), 
    path('private/veiex/datos/promedios/semihorarios/', getPromediosValidados, name="getPromediosValidados"), 
]

handler404 = "spd.views.page_not_found_view"
handler500 = "spd.views.custom_error_view"

