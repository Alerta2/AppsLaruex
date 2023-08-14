from django.shortcuts import render, redirect
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.views import generic
from django.urls import reverse_lazy
from structure.forms import SignUpForm, EditProfileForm, PasswordChangingForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import user_passes_test

import configparser

config = configparser.RawConfigParser()
config.read('config.ini')

@login_required
def profile(request):
	user=request.user
	if(user.has_perm('auth.muestras')):
		return redirect('HomeMuestras')
	if(user.has_perm('auth.tasa_dosis')):
		return redirect('Mapa')
	if(user.has_perm('auth.pvrain')):
		return redirect('analisis')

def portada(request):
    user = request.user
    return render(
        request,
        "content/portada.html",
        {
            "user":user,
        }
    )

def register(request):
    return render(
        request,
        "registration/register.html",
        {}
    )

def test(request):
    return render(
        request,
        "test.html",
        {}
    )

class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('password_success')

def password_success(request):
    return render(request, 'registration/password_success.html')

class UserRegisterView(generic.CreateView):
    form_class = SignUpForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

class UserEditView(generic.UpdateView):
    form_class = EditProfileForm
    template_name = 'registration/edit_profile.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user

def tickets(request):
    return render(
        request,
        "content/tickets.html",
        {}
    )

@user_passes_test(lambda u: u.is_superuser)
def configServer(request):
    print(config.sections())
    django, emailConfig = None, None
    dbs = []
    for section in config.sections():
        if section == "django":
            django = {"validips":config.get('django', 'validips'),"rutaActiva":config.get('django','rutaactiva')}
        elif "db" in section:
            dbs.append({"database":config.get(section, 'database'),"user":config.get(section,'user'),"password":config.get(section,'password'),"host":config.get(section,'host'),"port":config.get(section,'port')})
        elif section == "email_config":
            emailConfig = {"hostUser":config.get('email_config', 'hostUser'), "hostPassword":config.get('email_config', 'hostPassword'), "gestorCursos":config.get('email_config', 'gestorCursos')}

    return render(
        request,
        "config/config.html",
        {"django":django, "dbs":dbs, "emailConfig":emailConfig}
    )