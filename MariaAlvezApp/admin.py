from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils import timezone 
from django.utils.html import format_html
from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao,
    RegistroVermifugos, Exames, EstoqueMedicamento, MovimentoEstoqueMedicamento,
    RelatoriosGerais
)

admin.site.register(Veterinario)
admin.site.register(Exames)
admin.site.register(Tutor)
admin.site.register(Animal)
admin.site.register(AgendamentoConsultas)
admin.site.register(MovimentoEstoqueMedicamento)

@admin.register(RelatoriosGerais)
class RelatoriosGeraisAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        return super().changelist_view(request, extra_context=extra_context)

    change_list_template = "admin/relatorios_geral_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.redirecionar_para_index_relatorios), name='relatorios_gerais_index'),
        ]
        return custom_urls + urls

    def redirecionar_para_index_relatorios(self, request):
        return HttpResponseRedirect(reverse('relatorios_index'))

@admin.register(ConsultaClinica)
class ConsultaClinicaAdmin(admin.ModelAdmin):
    list_display = ('nome_animal', 'data_atendimento', 'nome_vet_responsavel', 'tipo_atendimento', 'diagnostico')
    search_fields = ('nome_animal', 'nome_vet_responsavel', 'diagnostico')

@admin.register(EstoqueMedicamento)
class EstoqueMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'lote', 'data_validade', 'quantidade', 'destaque_validade')
    list_filter = ('data_validade',)
    search_fields = ('medicamento', 'lote')
    readonly_fields = ('data_cadastro',)

@admin.register(RegistroVacinacao)
class RegistroVacinacaoAdmin(admin.ModelAdmin):
    list_display = (
        'animal',
        'medicamento_aplicado_display',
        'data_aplicacao',
        'data_revacinacao',
        'status_revacinacao',
    )
    search_fields = ('animal__nome', 'medicamento_aplicado__medicamento', 'medicamento_aplicado__lote')
    list_filter = ('data_aplicacao', 'data_revacinacao', 'medicamento_aplicado__medicamento')
    ordering = ('-data_aplicacao',)
    fieldsets = (
        (None, {
            'fields': ('animal', 'medicamento_aplicado', 'data_aplicacao', 'data_revacinacao')
        }),
    )

    def medicamento_aplicado_display(self, obj):
        if obj.medicamento_aplicado:
            validade = obj.medicamento_aplicado.data_validade.strftime('%d/%m/%Y')
            return format_html(
                f"{obj.medicamento_aplicado.medicamento} (Lote: {obj.medicamento_aplicado.lote}) Val: {validade})"
            )
        return "N/A"
    medicamento_aplicado_display.short_description = "Medicamento Aplicado (Lote/Validade)"
    medicamento_aplicado_display.admin_order_field = 'medicamento_aplicado__medicamento'

    def status_revacinacao(self, obj):
        if not obj.data_revacinacao:
            return format_html('<span style="color: gray;">Não definida</span>')

        hoje = timezone.now().date()
        dias_para_revacinar = (obj.data_revacinacao - hoje).days

        if dias_para_revacinar < 0:
            dias_atraso = abs(dias_para_revacinar)
            return format_html('<b style="color: red;">ATRASADA! ({} dias)</b>', dias_atraso)
        elif dias_para_revacinar <= 30:
            return format_html('<b style="color: orange;">Vence em {} dias</b>', dias_para_revacinar)
        else:
            return format_html('<span style="color: green;">OK (Em {} dias)</span>', dias_para_revacinar)

    status_revacinacao.short_description = "Status Revacinação"
    status_revacinacao.admin_order_field = 'data_revacinacao'

@admin.register(RegistroVermifugos)
class RegistroVermifugosAdmin(admin.ModelAdmin):
    list_display = (
        'animal',
        'medicamento_administrado_display',
        'data_administracao',
        'data_readministracao',
        'status_readministracao',
    )
    search_fields = ('animal__nome', 'medicamento_administrado__medicamento', 'medicamento_administrado__lote')
    list_filter = ('data_administracao', 'data_readministracao', 'medicamento_administrado__medicamento')
    ordering = ('-data_administracao',)
    fieldsets = (
        (None, {
            'fields': ('animal', 'medicamento_administrado', 'data_administracao', 'data_readministracao')
        }),
    )

    def medicamento_administrado_display(self, obj):
        if obj.medicamento_administrado:
            validade = obj.medicamento_administrado.data_validade.strftime('%d/%m/%Y')
            return format_html(
                f"{obj.medicamento_administrado.medicamento} (Lote: {obj.medicamento_administrado.lote}) Val: {validade})"
            )
        return "N/A"
    medicamento_administrado_display.short_description = "Vermífugo Administrado (Lote/Validade)"
    medicamento_administrado_display.admin_order_field = 'medicamento_administrado__medicamento'

    def status_readministracao(self, obj):
        if not obj.data_readministracao:
            return format_html('<span style="color: gray;">Não definida</span>')

        hoje = timezone.now().date()
        dias_para_readministrar = (obj.data_readministracao - hoje).days

        if dias_para_readministrar < 0:
            dias_atraso = abs(dias_para_readministrar)
            return format_html('<b style="color: red;">ATRASADA! ({} dias)</b>', dias_atraso)
        elif dias_para_readministrar <= 30:
            return format_html('<b style="color: orange;">Readministrar em {} dias</b>', dias_para_readministrar)
        else:
            return format_html('<span style="color: green;">OK (Em {} dias)</span>', dias_para_readministrar)

    status_readministracao.short_description = "Status Readministração"
    status_readministracao.admin_order_field = 'data_readministracao'