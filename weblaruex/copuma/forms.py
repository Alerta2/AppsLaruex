from django import forms

class UploadFormCopuma(forms.Form):
	docfile = forms.FileField(label='Selecciona un archivo')
