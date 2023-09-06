from django.forms import ModelForm, Form
from django_jsonform.models.fields import JSONField

esquema = {
      "type": "object",
      "required": ["First Name"],
      "properties": {
           "First Name": {
                "type": "string",
                "maxLength": 30                 
           }
      }     
    }

options = {"no_additional_properties": True}

class CustomForm(Form):    
    print("Saco el formulario", esquema)
    formulario = JSONField(schema = esquema)
    
def get_form(esquemaNuevo):
    global esquema
    esquema = esquemaNuevo
    print("Cargo el esquema", esquema)
    return CustomForm()

