from django import forms

#class EditProfileUserForm(UserChangeForm):
#    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
#    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
#    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
#    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

#    class Meta:
#        model = User
#        fields = ('username', 'first_name', 'last_name', 'email')

class FormCrearEvento(forms.Form):
    tituloNewEvento = forms.CharField(min_length=4, max_length=100, label='', required=True)
    fechaInicial = forms.DateTimeField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            #'data-target': '#datetimepicker1'
        }),
        required=True
    )

class FormCerrarEvento(forms.Form):
    idEventoInundacion = forms.IntegerField(initial=-1)
    tituloFinalEvento = forms.CharField(min_length=4, max_length=100, label='', required=True)
    fechaFinal = forms.DateTimeField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            #'data-target': '#datetimepicker1'
        }),
        required=True
    )