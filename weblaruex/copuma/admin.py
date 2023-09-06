from django.contrib import admin
from copuma.models import ProduccionAlmaraz


class ProduccionAlmarazAdmin(admin.ModelAdmin):
    list_display = ("fecha_consumo", "modulo_1", "modulo_2")
    search_fields = ("fecha_consumo",)

admin.site.register(ProduccionAlmaraz, ProduccionAlmarazAdmin)
