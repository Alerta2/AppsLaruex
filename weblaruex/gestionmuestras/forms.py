from django.forms import ModelForm, Form
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
# import reverse
from django.urls import reverse

from gestionmuestras.models_nuevo import *

# form for cod_muestras
# parametros codigo, nombre, tipo, etiquetas, nombre_pt
class CodMuestrasForm(forms.Form):
    codigo = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'XX'}))
    nombre = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'nombre'}))
    tipo = forms.ChoiceField(choices = [])
    #etiquetas en un input numérico
    etiquetas = forms.IntegerField(widget=forms.NumberInput())
    nombre_pt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'nombre portugués'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].choices = [(x.tipo_muestra_id, x.descripcion) for x in TipoDeMuestras.objects.using('gestion_muestras').all()]
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionCodigosMuestrasNuevo')
        self.helper.layout = Layout(
            Row(
                Column('codigo', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                Column('nombre_pt', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('tipo', css_class='form-group col-md-6 mb-0'),
                Column('etiquetas', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )   

class CodMuestrasEditarForm(forms.Form):
    codigo = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    nombre = forms.CharField(widget=forms.TextInput())
    tipo = forms.ChoiceField(choices = [])
    #etiquetas en un input numérico
    etiquetas = forms.IntegerField(widget=forms.NumberInput())
    nombre_pt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'nombre portugués'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].choices = [(x.tipo_muestra_id, x.descripcion) for x in TipoDeMuestras.objects.using('gestion_muestras').all()]
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionCodigosMuestrasEditar')
        self.helper.layout = Layout(
            Row(
                Column('codigo', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                Column('nombre_pt', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('tipo', css_class='form-group col-md-6 mb-0'),
                Column('etiquetas', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )   

'''
forms para clientes
clase con los siguientes campos:
    identificador, nombre, descripcion, direccion, telefono, fax, email, persona_contacto, nif, idioma, password, informar 
'''
class ClientesForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'nombre'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'descripcion'}))
    direccion = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'direccion'}))
    telefono = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'telefono'}))
    fax = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'fax'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'email'}))
    persona_contacto = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'persona contacto'}))
    nif = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'nif'}))
    idioma = forms.ChoiceField(choices = (("ES",'ES'), ("EN",'EN'), ("PT",'PT')))
    password = forms.CharField(widget=forms.PasswordInput())
    informar = forms.BooleanField(required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionClientesNuevo')
        self.helper.layout = Layout(
            Row(
                Column('nombre', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('descripcion', css_class='form-group col-md-12 mb-0'),
                Column('direccion', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('telefono', css_class='form-group col-md-6 mb-0'),
                Column('fax', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                Column('persona_contacto', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('nif', css_class='form-group col-md-6 mb-0'),
                Column('idioma', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password', css_class='form-group col-md-6 mb-0'),
                Column('informar', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )
        
class ClientesEditarForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    nombre = forms.CharField(widget=forms.TextInput())
    descripcion = forms.CharField(widget=forms.Textarea())
    direccion = forms.CharField(widget=forms.TextInput())
    telefono = forms.CharField(widget=forms.TextInput())
    fax = forms.CharField(widget=forms.TextInput())
    email = forms.EmailField(widget=forms.EmailInput())
    persona_contacto = forms.CharField(widget=forms.TextInput())
    nif = forms.CharField(widget=forms.TextInput())
    idioma = forms.ChoiceField(choices = (("ES",'ES'), ("EN",'EN'), ("PT",'PT')))
    password = forms.CharField(widget=forms.PasswordInput())
    informar = forms.BooleanField(required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionClientesEditar')
        self.helper.layout = Layout(
            Row(
                Column('identificador', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('descripcion', css_class='form-group col-md-12 mb-0'),
                Column('direccion', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('telefono', css_class='form-group col-md-6 mb-0'),
                Column('fax', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                Column('persona_contacto', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('nif', css_class='form-group col-md-6 mb-0'),
                Column('idioma', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password', css_class='form-group col-md-6 mb-0'),
                Column('informar', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

'''
forms para memorias
clase con los siguientes campos:
    codigo_memoria, memoria, base_datos_geslab, descripcion, ajuste_semana
'''
class MemoriasForm(forms.Form):
    codigo_memoria = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'XX'}))
    memoria = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'memoria'}))
    base_datos_geslab = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'base de datos'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'descripcion'}))
    ajuste_semana = forms.IntegerField(widget=forms.NumberInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionMemoriasNuevo')
        self.helper.layout = Layout(
            Row(
                Column('codigo_memoria', css_class='form-group col-md-6 mb-0'),
                Column('memoria', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('base_datos_geslab', css_class='form-group col-md-6 mb-0'),
                Column('descripcion', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('ajuste_semana', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class MemoriasEditarForm(forms.Form):
    codigo_memoria = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    memoria = forms.CharField(widget=forms.TextInput())
    base_datos_geslab = forms.CharField(widget=forms.TextInput())
    descripcion = forms.CharField(widget=forms.Textarea())
    ajuste_semana = forms.IntegerField(widget=forms.NumberInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionMemoriasEditar')
        self.helper.layout = Layout(
            Row(
                Column('codigo_memoria', css_class='form-group col-md-6 mb-0'),
                Column('memoria', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('base_datos_geslab', css_class='form-group col-md-6 mb-0'),
                Column('descripcion', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('ajuste_semana', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

'''
form para muestra actual codigo
clase con los siguientes campos:
    codigo, posicion, duplicada, duplicada_pos, control, control_pos, blanco, blanco_pos, tiempo_en_lab
'''
class MuestraActualCodigoForm(forms.Form):
    codigo = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'codigo'}))
    posicion = forms.IntegerField(widget=forms.NumberInput())
    duplicada = forms.IntegerField(widget=forms.NumberInput())
    duplicada_pos = forms.IntegerField(widget=forms.NumberInput())
    control = forms.IntegerField(widget=forms.NumberInput())
    control_pos = forms.IntegerField(widget=forms.NumberInput())
    blanco = forms.IntegerField(widget=forms.NumberInput())
    blanco_pos = forms.IntegerField(widget=forms.NumberInput())
    tiempo_en_lab = forms.IntegerField(widget=forms.NumberInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionMuestraActualCodigoNuevo')
        self.helper.layout = Layout(
            Row(
                Column('codigo', css_class='form-group col-md-6 mb-0'),
                Column('posicion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('duplicada', css_class='form-group col-md-6 mb-0'),
                Column('duplicada_pos', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('control', css_class='form-group col-md-6 mb-0'),
                Column('control_pos', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('blanco', css_class='form-group col-md-6 mb-0'),
                Column('blanco_pos', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('tiempo_en_lab', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class MuestraActualCodigoEditarForm(forms.Form):
    codigo = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    posicion = forms.IntegerField(widget=forms.NumberInput())
    duplicada = forms.IntegerField(widget=forms.NumberInput())
    duplicada_pos = forms.IntegerField(widget=forms.NumberInput())
    control = forms.IntegerField(widget=forms.NumberInput())
    control_pos = forms.IntegerField(widget=forms.NumberInput())
    blanco = forms.IntegerField(widget=forms.NumberInput())
    blanco_pos = forms.IntegerField(widget=forms.NumberInput())
    tiempo_en_lab = forms.IntegerField(widget=forms.NumberInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionMuestraActualCodigoEditar')
        self.helper.layout = Layout(
            Row(
                Column('codigo', css_class='form-group col-md-6 mb-0'),
                Column('posicion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('duplicada', css_class='form-group col-md-6 mb-0'),
                Column('duplicada_pos', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('control', css_class='form-group col-md-6 mb-0'),
                Column('control_pos', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('blanco', css_class='form-group col-md-6 mb-0'),
                Column('blanco_pos', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('tiempo_en_lab', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )
        

# form para gestion de parámetros de muestra
# parametros identificador, nombre, descripcion, muestra

class ParametrosMuestraForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'XX'}))
    nombre = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'nombre'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'descripcion'}))
    muestra = forms.IntegerField(widget=forms.NumberInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionParametrosNuevo')
        self.helper.layout = Layout(
            Row(
                Column('identificador', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('descripcion', css_class='form-group col-md-12 mb-0'),
                Column('muestra', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class ParametrosMuestraEditarForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    nombre = forms.CharField(widget=forms.TextInput())
    descripcion = forms.CharField(widget=forms.Textarea())
    muestra = forms.IntegerField(widget=forms.NumberInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionParametrosEditar')
        self.helper.layout = Layout(
            Row(
                Column('identificador', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('descripcion', css_class='form-group col-md-12 mb-0'),
                Column('muestra', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

# form para gestion de las procedencias
# parametros: codigo, nombre
class ProcedenciasForm(forms.Form):
    codigo = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'XX'}))
    nombre = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'nombre'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('codigo', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class ProcedenciasEditarForm(forms.Form):
    codigo = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    nombre = forms.CharField(widget=forms.TextInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('codigo', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

# form para gestion de relacion de control con tratamiento
# parametros: identificador, tipo_control, codigo, id_muestra_historico
class RelacionControlTratamientoForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'XX'}))
    tipo_control = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'BL o CTR'}))
    codigo = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'codigo'}))
    id_muestra_historico = forms.IntegerField(widget=forms.NumberInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionRelacionControlTratamientoNuevo')
        self.helper.layout = Layout(
            Row(
                Column('identificador', css_class='form-group col-md-6 mb-0'),
                Column('tipo_control', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('codigo', css_class='form-group col-md-6 mb-0'),
                Column('id_muestra_historico', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class RelacionControlTratamientoEditarForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    tipo_control = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'BL o CTR'}))
    codigo = forms.CharField(widget=forms.TextInput())
    id_muestra_historico = forms.IntegerField(widget=forms.NumberInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionRelacionControlTratamientoEditar')
        self.helper.layout = Layout(
            Row(
                Column('identificador', css_class='form-group col-md-6 mb-0'),
                Column('tipo_control', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('codigo', css_class='form-group col-md-6 mb-0'),
                Column('id_muestra_historico', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

# form para la gestion de la relacion determinacion con tratamientos
# parametros: id_determinacion, id_tratamiento, por_defecto

class RelacionDeterminacionTratamientoForm(forms.Form):
    id_determinacion = forms.IntegerField(widget=forms.NumberInput())
    id_tratamiento = forms.IntegerField(widget=forms.NumberInput())
    por_defecto = forms.BooleanField(required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionRelacionDeterminacionTratamientoNuevo')
        self.helper.layout = Layout(
            Row(
                Column('id_determinacion', css_class='form-group col-md-6 mb-0'),
                Column('id_tratamiento', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('por_defecto', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class RelacionDeterminacionTratamientoEditarForm(forms.Form):
    id_determinacion = forms.IntegerField(widget=forms.NumberInput())
    id_tratamiento = forms.IntegerField(widget=forms.NumberInput())
    por_defecto = forms.BooleanField(required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionRelacionDeterminacionTratamientoEditar')
        self.helper.layout = Layout(
            Row(
                Column('id_determinacion', css_class='form-group col-md-6 mb-0'),
                Column('id_tratamiento', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('por_defecto', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

# form para la gestion de frases predefinidas
# parametros: identificador, texto, destino

class FrasesPredefinidasForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'XX'}))
    texto = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'texto'}))
    destino = forms.ChoiceField(choices = (("recepcion",'recepcion'), ("informe",'informe'), ("informe_portugues",'informe_portugues')))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionFrasePredefinidaNuevo')
        self.helper.layout = Layout(
            Row(
                Column('texto', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('destino', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class FrasesPredefinidasEditarForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    texto = forms.CharField(widget=forms.Textarea())
    destino = forms.ChoiceField(choices = (("recepcion",'recepcion'), ("informe",'informe'), ("informe_portugues",'informe_portugues')))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionFrasePredefinidaEditar')
        self.helper.layout = Layout(
            Row(
                Column('texto', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('destino', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

# form para la gestion de las determinaciones
# parametros: identificador, nombre
class DeterminacionesForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'XX'}))
    nombre = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'nombre'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionDeterminacionNuevo')
        self.helper.layout = Layout(
            Row(
                Column('identificador', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class DeterminacionesEditarForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    nombre = forms.CharField(widget=forms.TextInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionDeterminacionEditar')
        self.helper.layout = Layout(
            Row(
                Column('identificador', css_class='form-group col-md-6 mb-0'),
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

# form para la gestion de los tratamientos
# parametros: identificador, descripcion, medida, tiempo_en_lab, alcance
class TratamientoForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'XX'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'descripcion'}))
    medida = forms.ChoiceField(choices=(("SI",'SI'), ("NO",'NO')))
    tiempo_en_lab = forms.IntegerField(widget=forms.NumberInput())
    alcance = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'alcance'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionTratamientoNuevo')
        self.helper.layout = Layout(
            Row(
                Column('identificador', css_class='form-group col-md-6 mb-0'),
                Column('descripcion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('medida', css_class='form-group col-md-6 mb-0'),
                Column('tiempo_en_lab', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('alcance', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class TratamientoEditarForm(forms.Form):
    identificador = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    descripcion = forms.CharField(widget=forms.Textarea())
    medida = forms.ChoiceField(choices=(("SI",'SI'), ("NO",'NO')))
    tiempo_en_lab = forms.IntegerField(widget=forms.NumberInput())
    alcance = forms.CharField(widget=forms.TextInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionTratamientoEditar')
        self.helper.layout = Layout(
            Row(
                Column('identificador', css_class='form-group col-md-6 mb-0'),
                Column('descripcion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('medida', css_class='form-group col-md-6 mb-0'),
                Column('tiempo_en_lab', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('alcance', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

# form para la gestion de la relacion de tratamiento con responsables
# parametros: procedimiento, responsable, sustituto_1, sustituto_2, sustituto_3, descripcion
        
class RelacionTratamientoResponsableForm(forms.Form):
    procedimiento = forms.ChoiceField(choices = [])
    responsable = forms.ChoiceField(choices = [])
    sustituto_1 = forms.ChoiceField(choices = [])
    sustituto_2 = forms.ChoiceField(choices = [])
    sustituto_3 = forms.ChoiceField(choices = [])
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'descripcion'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['procedimiento'].choices = [(x.identificador, x.descripcion) for x in Tratamiento.objects.using('gestion_muestras').all()]
        self.fields['responsable'].choices = [(x.nombre, x.nombre) for x in Usuarios.objects.using('gestion_muestras').all()]
        self.fields['sustituto_1'].choices = [(x.nombre, x.nombre) for x in Usuarios.objects.using('gestion_muestras').all()]
        self.fields['sustituto_2'].choices = [(x.nombre, x.nombre) for x in Usuarios.objects.using('gestion_muestras').all()]
        self.fields['sustituto_3'].choices = [(x.nombre, x.nombre) for x in Usuarios.objects.using('gestion_muestras').all()]
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionRelacionTratamientoResponsableNuevo')
        self.helper.layout = Layout(
            Row(
                Column('procedimiento', css_class='form-group col-md-6 mb-0'),
                Column('responsable', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('sustituto_1', css_class='form-group col-md-6 mb-0'),
                Column('sustituto_2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('sustituto_3', css_class='form-group col-md-6 mb-0'),
                Column('descripcion', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class RelacionTratamientoResponsableEditarForm(forms.Form):
    procedimiento = forms.ChoiceField(choices = [])
    responsable = forms.ChoiceField(choices = [])
    sustituto_1 = forms.ChoiceField(choices = [])
    sustituto_2 = forms.ChoiceField(choices = [])
    sustituto_3 = forms.ChoiceField(choices = [])
    descripcion = forms.CharField(widget=forms.Textarea())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['procedimiento'].choices = [(x.identificador, x.descripcion) for x in Tratamiento.objects.using('gestion_muestras').all()]
        self.fields['responsable'].choices = [(x.nombre, x.nombre) for x in Usuarios.objects.using('gestion_muestras').all()]
        self.fields['sustituto_1'].choices = [(x.nombre, x.nombre) for x in Usuarios.objects.using('gestion_muestras').all()]
        self.fields['sustituto_2'].choices = [(x.nombre, x.nombre) for x in Usuarios.objects.using('gestion_muestras').all()]
        self.fields['sustituto_3'].choices = [(x.nombre, x.nombre) for x in Usuarios.objects.using('gestion_muestras').all()]
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionRelacionTratamientoResponsableEditar')
        self.helper.layout = Layout(
            Row(
                Column('procedimiento', css_class='form-group col-md-6 mb-0'),
                Column('responsable', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('sustituto_1', css_class='form-group col-md-6 mb-0'),
                Column('sustituto_2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('sustituto_3', css_class='form-group col-md-6 mb-0'),
                Column('descripcion', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

# form para la gestion de tratamientos muestras codigo
# parametros: id, id_muestra_codigo, id_tratamiento

class TratamientosMuestrasCodigoForm(forms.Form):
    id_muestra_codigo = forms.IntegerField(widget=forms.NumberInput())
    id_tratamiento = forms.IntegerField(widget=forms.NumberInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionTratamientosMuestrasCodigoNuevo')
        self.helper.layout = Layout(
            Row(
                Column('id_muestra_codigo', css_class='form-group col-md-6 mb-0'),
                Column('id_tratamiento', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )

class TratamientosMuestrasCodigoEditarForm(forms.Form):
    id = forms.IntegerField(widget=forms.NumberInput())
    id_muestra_codigo = forms.IntegerField(widget=forms.NumberInput())
    id_tratamiento = forms.IntegerField(widget=forms.NumberInput())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('gestionmuestras:gestmuesGestionTratamientosMuestrasCodigoEditar')
        self.helper.layout = Layout(
            Row(
                Column('id', css_class='form-group col-md-6 mb-0'),
                Column('id_muestra_codigo', css_class='form-group col-md-6 mb-0'),
                Column('id_tratamiento', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enviar')
        )
        