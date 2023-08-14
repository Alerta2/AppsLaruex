from django import forms
from django.core.validators import FileExtensionValidator


class subidaInforme(forms.Form):
    title = forms.CharField(max_length=50, required=False)
    fecha = forms.IntegerField(required=False)
    file = forms.FileField(required=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])], widget=forms.FileInput(attrs={'class':'btn btn-info'}))


class FormFechaIniFinEvento(forms.Form):
    idEvento = forms.IntegerField(initial=-1)
    titulo = forms.CharField(max_length=100, label='')
    tipoFecha = forms.CharField(max_length=50, initial='Your type of date')
    fecha = forms.DateTimeField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        }),
        required=True
    )


'''class FileFieldForm(forms.Form):
    #file_field = forms.FileField(widget=forms.FileInput(attrs={'multiple':"true"}))
    docuspida = forms.FileField(readonly=True, widget=forms.FileInput( attrs={'multiple':"true"}))'''