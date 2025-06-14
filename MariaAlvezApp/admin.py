from django.contrib import admin
from django import forms
from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao,
    RegistroVermifugos, Exames, EstoqueMedicamento, MovimentoEstoqueMedicamento
)

# Register your models here.
admin.site.register(Veterinario)
admin.site.register(Tutor)
admin.site.register(Animal)
admin.site.register(ConsultaClinica)
admin.site.register(AgendamentoConsultas)
admin.site.register(RegistroVacinacao)
admin.site.register(RegistroVermifugos)
admin.site.register(Exames)

@admin.register(EstoqueMedicamento)
class EstoqueMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'lote', 'quantidade', 'data_validade', 'destaque_validade')
    search_fields = ('medicamento', 'lote')
    list_filter = ('data_validade',)
    ordering = ['medicamento']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.quantidade == 0:
                return ['medicamento', 'lote', 'quantidade', 'data_cadastro', 'destaque_validade']
            else:
                return ['medicamento', 'lote', 'quantidade', 'data_validade', 'data_cadastro', 'destaque_validade']
        return ['medicamento', 'lote', 'quantidade', 'data_validade', 'data_cadastro', 'destaque_validade']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class MovimentoEstoqueMedicamentoForm(forms.ModelForm):
    saldo_lote = forms.CharField(
        label="Status do Lote",
        required=False,
        disabled=True,
        initial="Informe o código do lote para verificar."
    )

    class Meta:
        model = MovimentoEstoqueMedicamento
        fields = '__all__'


@admin.register(MovimentoEstoqueMedicamento)
class MovimentoEstoqueMedicamentoAdmin(admin.ModelAdmin):
    form = MovimentoEstoqueMedicamentoForm
    list_display = ('data', 'tipo', 'medicamento', 'lote', 'quantidade')
    search_fields = ('medicamento', 'lote')
    list_filter = ('tipo', 'data')
    list_per_page = 25


    fieldsets = (
        (None, {
            'fields': (
                'lote',
                'medicamento',
                'data_validade',
                'tipo', 
                'quantidade',
                'observacao',
            )
        }),
    )

    def has_change_permission(self, request, obj=None):
        # Impede a alteração de um movimento já registrado para manter o histórico fiel.
        return False

    def has_delete_permission(self, request, obj=None):
        # Impede a exclusão de um movimento já registrado.
        return False