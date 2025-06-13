from django.contrib import admin
from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao,
    RegistroVermifugos, Exames, Medicamentos
)

# Register your models here.
admin.site.register(Veterinario)
admin.site.register(Tutor)
admin.site.register(Animal)
admin.site.register(ConsultaClinica)
admin.site.register(AgendamentoConsultas)
admin.site.register(RegistroVacinacao)
admin.site.register(RegistroVermifugos)
admin.site.register(Medicamentos)

@admin.register(Exames)
class ExamesAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo')
        
