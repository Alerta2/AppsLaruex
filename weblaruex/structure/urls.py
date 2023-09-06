from django.urls import path
from structure.views import portada, register, UserEditView, PasswordsChangeView, password_success, tickets, configServer
from public.views import areaPrivada
from django.urls import include, path
from django.contrib import admin

app_name = 'structure'

urlpatterns = [
    path('private/servicios/',              areaPrivada,                    name='servicios'),
    path('accounts/',                       include('django.contrib.auth.urls')),


    path('private/',                                areaPrivada,                name='privateHome'),
    path('private/index/',                          areaPrivada),
    path('private/home/',                           areaPrivada),
    path('private/servicios/tickets/',              tickets,                name='serviciosTickets'),

    # Profiles
    path('profile/registration/',                   register,               name='register'),
    path('edit_profile/',                           UserEditView.as_view(), name='edit_profile'),
    path('password/',                               PasswordsChangeView.as_view(template_name='registration/change-password.html')),
    path('password_success/',                       password_success,       name='password_success'),
    path('private/profile/registration/',           register,               name='Register'),

    # Configs
    path('config/',                                configServer,                name='configServer'),

]

