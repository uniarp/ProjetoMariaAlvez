from django.contrib import admin
from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao,
    RegistroVermifugos, Exames, Medicamentos
)

# Register your models here.
admin.site.register(Veterinario)
admin.site.register(Tutor)
# admin.site.register(Animal)

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie')
    fields = (
        'nome', 'especie',
        'idade_anos', 'idade_meses', 'idade_dias',
        'sexo',
        'peso',
        'rfid'      
    )

admin.site.register(ConsultaClinica)
admin.site.register(AgendamentoConsultas)
admin.site.register(RegistroVacinacao)
admin.site.register(RegistroVermifugos)
admin.site.register(Exames)
admin.site.register(Medicamentos)

