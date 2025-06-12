from django.contrib import admin
from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao,
    RegistroVermifugos, Exames, Medicamentos
)

class AgendamentoConsultasAdmin(admin.ModelAdmin):
    list_display = ('id_agendamento', 'animal', 'tutor', 'data_consulta')
    list_filter = ('data_consulta',)
    search_fields = ('animal__nome', 'tutor')
    ordering = ('-data_consulta',)

# Register your models here.
admin.site.register(Veterinario)
admin.site.register(Tutor)
admin.site.register(Animal)
admin.site.register(ConsultaClinica)
admin.site.register(AgendamentoConsultas)
admin.site.register(RegistroVacinacao)
admin.site.register(RegistroVermifugos)
admin.site.register(Exames)
admin.site.register(Medicamentos)
