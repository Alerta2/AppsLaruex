from django import forms

class FechasInforme(forms.Form):
    date_inicio = forms.DateField( )
    date_fin = forms.DateField( )
