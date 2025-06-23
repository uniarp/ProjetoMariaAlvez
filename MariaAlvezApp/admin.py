# admin.py - VERSÃO ATUALIZADA

from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils import timezone 

from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao, RegistroVermifugos, 
    Exames, EstoqueMedicamento, MovimentoEstoqueMedicamento,
    RelatoriosGerais,
    MedicamentoConsulta 
)

# Registros simples
admin.site.register(Veterinario)
# admin.site.register(Exames) # Agora gerenciado via inline, pode ser comentado/removido
admin.site.register(Tutor)
admin.site.register(Animal)
admin.site.register(AgendamentoConsultas)

@admin.register(RelatoriosGerais)
class RelatoriosGeraisAdmin(admin.ModelAdmin):
    # ... (sem alterações aqui)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        return super().changelist_view(request, extra_context=extra_context)
    change_list_template = "admin/relatorios_geral_changelist.html"
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [path('', self.admin_site.admin_view(self.redirecionar_para_index_relatorios), name='relatorios_gerais_index')]
        return custom_urls + urls
    def redirecionar_para_index_relatorios(self, request):
        return HttpResponseRedirect(reverse('relatorios_index'))

# --- INLINES ---
class MedicamentoConsultaInline(admin.TabularInline):
    model = MedicamentoConsulta
    extra = 1 
    fields = ['medicamento_estoque', 'quantidade_aplicada']

# --- NOVO INLINE PARA EXAMES ---
class ExameInline(admin.TabularInline):
    model = Exames
    extra = 1 # Começa com 1 campo vazio para adicionar um novo exame
    fields = ('nome', 'tipo', 'anexo', 'descricao', 'data_exame') # Campos que aparecerão no inline
    # O campo 'animal' será preenchido automaticamente ou pode ser omitido se desejado
    # O campo 'consulta' é preenchido automaticamente pelo Django

# --- ALTERAÇÃO AQUI ---
@admin.register(ConsultaClinica)
class ConsultaClinicaAdmin(admin.ModelAdmin):
    list_display = ('animal', 'data_atendimento', 'veterinario', 'tipo_atendimento', 'diagnostico', 'get_medicamentos_aplicados_display')
    readonly_fields = [] 
    search_fields = ('animal__nome', 'veterinario__nome', 'diagnostico') 
    
    fieldsets = (
        (None, {
            'fields': (
                'animal', 'veterinario', 'data_atendimento', 
                'tipo_atendimento', 'diagnostico', 'observacoes',
            )
        }),
        ('Detalhes Físicos', {
            'fields': (
                'frequencia_cardiaca', 'frequencia_respiratoria', 'temperatura',
                'peso', 'avaliacao_mucosa', 'tempo_preenchimento_capilar',
                # 'exames_realizados', # <-- CAMPO REMOVIDO DAQUI
            ),
            'classes': ('collapse',),
        }),
    )

    # Adiciona o novo inline à lista
    inlines = [
        MedicamentoConsultaInline,
        ExameInline, # <-- NOVO INLINE ADICIONADO
    ]

    @admin.display(description="Medicamentos na Consulta")
    def get_medicamentos_aplicados_display(self, obj):
        medicamentos_consulta = obj.medicamentoconsulta_set.all() 
        if medicamentos_consulta:
            return format_html("<br>".join([f"{mc.medicamento_estoque.medicamento} ({mc.quantidade_aplicada} un.)" for mc in medicamentos_consulta]))
        return "Nenhum"

# Demais classes Admin (sem alterações)
@admin.register(EstoqueMedicamento)
class EstoqueMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'lote', 'data_validade', 'quantidade', 'destaque_validade_admin_display')
    list_filter = ('data_validade',)
    search_fields = ('medicamento', 'lote')
    readonly_fields = ('data_cadastro',)

    @admin.display(description="Status da Validade", ordering='data_validade')
    def destaque_validade_admin_display(self, obj):
        return obj.destaque_validade()

@admin.register(MovimentoEstoqueMedicamento)
class MovimentoEstoqueMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('estoque_item', 'tipo', 'quantidade', 'data', 'observacao')
    list_filter = ('tipo', 'data')
    search_fields = ('estoque_item__medicamento', 'estoque_item__lote', 'observacao') 
    def has_change_permission(self, request, obj=None): return False 
    def get_readonly_fields(self, request, obj=None):
        if obj is None: return ('data',)
        else: return ('estoque_item', 'tipo', 'quantidade', 'data', 'observacao')

@admin.register(RegistroVacinacao)
class RegistroVacinacaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'medicamento_aplicado_display', 'data_aplicacao', 'data_revacinacao', 'status_revacinacao_display')
    search_fields = ('animal__nome', 'medicamento_aplicado__medicamento', 'medicamento_aplicado__lote') 
    list_filter = ('data_aplicacao', 'data_revacinacao', 'medicamento_aplicado__medicamento') 
    ordering = ('-data_aplicacao',)
    fieldsets = ((None, {'fields': ('animal', 'medicamento_aplicado', 'data_aplicacao', 'data_revacinacao')}),)
    @admin.display(description="Medicamento Aplicado (Lote/Validade)")
    def medicamento_aplicado_display(self, obj):
        if obj.medicamento_aplicado:
            validade = obj.medicamento_aplicado.data_validade.strftime('%d/%m/%Y')
            return format_html(f"{obj.medicamento_aplicado.medicamento} (Lote: {obj.medicamento_aplicado.lote}) Val: {validade})")
        return "N/A"
    @admin.display(description="Status Revacinação", ordering='data_revacinacao')
    def status_revacinacao_display(self, obj):
        if not obj.data_revacinacao: return format_html('<span style="color: gray;">Não definida</span>')
        hoje = timezone.now().date(); dias = (obj.data_revacinacao - hoje).days
        if dias < 0: return format_html('<b style="color: red;">ATRASADA! ({} dias)</b>', abs(dias))
        elif dias <= 30: return format_html('<b style="color: orange;">Vence em {} dias</b>', dias)
        else: return format_html('<span style="color: green;">OK (Em {} dias)</span>', dias)

@admin.register(RegistroVermifugos)
class RegistroVermifugosAdmin(admin.ModelAdmin):
    list_display = ('animal', 'medicamento_administrado_display', 'data_administracao', 'data_readministracao', 'status_readministracao_display')
    search_fields = ('animal__nome', 'medicamento_administrado__medicamento', 'medicamento_administrado__lote') 
    list_filter = ('data_administracao', 'data_readministracao', 'medicamento_administrado__medicamento') 
    ordering = ('-data_administracao',)
    fieldsets = ((None, {'fields': ('animal', 'medicamento_administrado', 'data_administracao', 'data_readministracao')}),)
    @admin.display(description="Vermífugo Administrado (Lote/Validade)")
    def medicamento_administrado_display(self, obj):
        if obj.medicamento_administrado:
            validade = obj.medicamento_administrado.data_validade.strftime('%d/%m/%Y')
            return format_html(f"{obj.medicamento_administrado.medicamento} (Lote: {obj.medicamento_administrado.lote}) Val: {validade})")
        return "N/A"
    @admin.display(description="Status Readministração", ordering='data_readministracao')
    def status_readministracao_display(self, obj):
        if not obj.data_readministracao: return format_html('<span style="color: gray;">Não definida</span>')
        hoje = timezone.now().date(); dias = (obj.data_readministracao - hoje).days
        if dias < 0: return format_html('<b style="color: red;">ATRASADA! ({} dias)</b>', abs(dias))
        elif dias <= 30: return format_html('<b style="color: orange;">Readministrar em {} dias</b>', dias)
        else: return format_html('<span style="color: green;">OK (Em {} dias)</span>', dias)