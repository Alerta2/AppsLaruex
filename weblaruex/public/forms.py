from django import forms
from django.conf import settings
from ckeditor.widgets import CKEditorWidget
from captcha.fields import ReCaptchaField

class formularioNoticia(forms.Form):
    resumenNoticia = forms.CharField(widget=CKEditorWidget(config_name='default'))
    contenidoNoticia = forms.CharField(widget=CKEditorWidget(config_name='default'))

class formularioInvestigacion(forms.Form):
    resumenInvestigacion = forms.CharField(widget=CKEditorWidget(config_name='default'))


class formularioMedida(forms.Form):
    descripcionMedida = forms.CharField(widget=CKEditorWidget(config_name='default'))




class formularioCaptcha(forms.Form):
    publicKey = settings.RECAPTCHA_SITE_KEY
    privateKey = settings.RECAPTCHA_SECRET_KEY
    # Agrega el campo de reCAPTCHA
    captcha = ReCaptchaField(public_key= publicKey,private_key=privateKey)


class consultaInforme(forms.Form):
    informe = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

class InformeForm(forms.Form):
    informe_numero = forms.CharField(label='Informe número', max_length=100)
    informe_password = forms.CharField(label='Informe password', max_length=100)