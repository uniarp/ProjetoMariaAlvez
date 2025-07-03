# MariaAlvezApp/views.py

from django.shortcuts import render
from django.db.models import Q 
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from datetime import timedelta, datetime

# Importar modelos e formulários do próprio MariaAlvezApp
from .models import (
    AgendamentoConsultas, ConsultaClinica, EstoqueMedicamento,
    RegistroVacinacao, RegistroVermifugos,
)
from .forms import (
    FiltroConsultaForm, FiltroEstoqueForm, FiltroVacinacaoForm,
    FiltroVermifugosForm, FiltroRegistroServicoForm 
)

# Importar modelos do app Terceiros
from Terceiros.models import RegistroServico, EmpresaTerceirizada 

# Para PDF
from weasyprint import HTML, CSS
from django.conf import settings 
from django.contrib.staticfiles.storage import staticfiles_storage 


def relatorios_index(request):
    return render(request, 'relatorios/relatorios_index.html')

def relatorio_consultas(request):
    form = FiltroConsultaForm(request.GET)
    consultas = ConsultaClinica.objects.all().order_by('-data_atendimento')

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        tutor = form.cleaned_data.get('tutor')
        animal = form.cleaned_data.get('animal')

        if data_inicio:
            consultas = consultas.filter(data_atendimento__date__gte=data_inicio)
        if data_fim:
            consultas = consultas.filter(data_atendimento__date__lte=data_fim)
        if tutor:
            consultas = consultas.filter(animal__tutor=tutor)
        if animal:
            consultas = consultas.filter(animal=animal)

    context = {'consultas': consultas, 'form': form}
    return render(request, 'relatorios/relatorio_consultas.html', context)

def relatorio_consultas_pdf(request):
    form = FiltroConsultaForm(request.GET)
    consultas = ConsultaClinica.objects.all().order_by('-data_atendimento')

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        tutor = form.cleaned_data.get('tutor')
        animal = form.cleaned_data.get('animal')

        if data_inicio:
            consultas = consultas.filter(data_atendimento__date__gte=data_inicio)
        if data_fim:
            consultas = consultas.filter(data_atendimento__date__lte=data_fim)
        if tutor:
            consultas = consultas.filter(animal__tutor=tutor)
        if animal:
            consultas = consultas.filter(animal=animal)

    template = get_template('relatorios/relatorio_consultas_pdf.html')
    html = template.render({'consultas': consultas, 'total_consultas': consultas.count()})
    
    pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[
            CSS(string='@page { size: A4; margin: 1cm; }'),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/base.css'))),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/forms.css'))),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/changelists.css'))),
        ]
    )

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_consultas.pdf"'
    return response

def relatorio_estoque(request):
    form = FiltroEstoqueForm(request.GET)
    estoque = EstoqueMedicamento.objects.all().order_by('data_validade')
    hoje = timezone.now().date()

    if form.is_valid():
        medicamento = form.cleaned_data.get('medicamento')
        lote = form.cleaned_data.get('lote')
        data_validade_inicio = form.cleaned_data.get('data_validade_inicio')
        data_validade_fim = form.cleaned_data.get('data_validade_fim')
        status_estoque = form.cleaned_data.get('status_estoque')

        if medicamento:
            estoque = estoque.filter(medicamento__icontains=medicamento)
        if lote:
            estoque = estoque.filter(lote__icontains=lote)
        if data_validade_inicio:
            estoque = estoque.filter(data_validade__gte=data_validade_inicio)
        if data_validade_fim:
            estoque = estoque.filter(data_validade__lte=data_validade_fim)

        if status_estoque == 'com_estoque':
            estoque = estoque.filter(quantidade__gt=0)
        elif status_estoque == 'sem_estoque':
            estoque = estoque.filter(quantidade=0)
        elif status_estoque == 'vencidos':
            estoque = estoque.filter(data_validade__lt=hoje)
        elif status_estoque == 'vencendo':
            limite_vencimento = hoje + timedelta(days=30)
            estoque = estoque.filter(data_validade__range=(hoje, limite_vencimento))

    context = {'estoque': estoque, 'form': form, 'hoje': hoje}
    return render(request, 'relatorios/relatorio_estoque.html', context)

def relatorio_estoque_pdf(request):
    form = FiltroEstoqueForm(request.GET)
    estoque = EstoqueMedicamento.objects.all().order_by('data_validade')
    hoje = timezone.now().date()

    if form.is_valid():
        medicamento = form.cleaned_data.get('medicamento')
        lote = form.cleaned_data.get('lote')
        data_validade_inicio = form.cleaned_data.get('data_validade_inicio')
        data_validade_fim = form.cleaned_data.get('data_validade_fim')
        status_estoque = form.cleaned_data.get('status_estoque')

        if medicamento:
            estoque = estoque.filter(medicamento__icontains=medicamento)
        if lote:
            estoque = estoque.filter(lote__icontains=lote)
        if data_validade_inicio:
            estoque = estoque.filter(data_validade__gte=data_validade_inicio)
        if data_validade_fim:
            estoque = estoque.filter(data_validade__lte=data_validade_fim)

        if status_estoque == 'com_estoque':
            estoque = estoque.filter(quantidade__gt=0)
        elif status_estoque == 'sem_estoque':
            estoque = estoque.filter(quantidade=0)
        elif status_estoque == 'vencidos':
            estoque = estoque.filter(data_validade__lt=hoje)
        elif status_estoque == 'vencendo':
            limite_vencimento = hoje + timedelta(days=30)
            estoque = estoque.filter(data_validade__range=(hoje, limite_vencimento))
    
    template = get_template('relatorios/relatorio_estoque_pdf.html')
    html = template.render({'estoque': estoque, 'total_lotes': estoque.count(), 'hoje': hoje})
    pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[
            CSS(string='@page { size: A4; margin: 1cm; }'),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/base.css'))),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/forms.css'))),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/changelists.css'))),
        ]
    )

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_estoque.pdf"'
    return response


def relatorio_vacinacao(request):
    form = FiltroVacinacaoForm(request.GET)
    vacinacoes = RegistroVacinacao.objects.all().order_by('-data_aplicacao')
    hoje = timezone.now().date()

    if form.is_valid():
        animal = form.cleaned_data.get('animal')
        data_aplicacao_inicio = form.cleaned_data.get('data_aplicacao_inicio')
        data_aplicacao_fim = form.cleaned_data.get('data_aplicacao_fim')
        status_revacinacao = form.cleaned_data.get('status_revacinacao')
        medicamento = form.cleaned_data.get('medicamento')

        if animal:
            vacinacoes = vacinacoes.filter(animal=animal)
        if data_aplicacao_inicio:
            vacinacoes = vacinacoes.filter(data_aplicacao__gte=data_aplicacao_inicio)
        if data_aplicacao_fim:
            vacinacoes = vacinacoes.filter(data_aplicacao__lte=data_aplicacao_fim)
        if medicamento:
            vacinacoes = vacinacoes.filter(medicamento_aplicado=medicamento)

        if status_revacinacao:
            if status_revacinacao == 'ok':
                vacinacoes = vacinacoes.filter(Q(data_revacinacao__gte=hoje + timedelta(days=31)) | Q(data_revacinacao__isnull=True))
            elif status_revacinacao == 'vencendo':
                limite_vencimento = hoje + timedelta(days=30)
                vacinacoes = vacinacoes.filter(data_revacinacao__range=(hoje, limite_vencimento))
            elif status_revacinacao == 'atrasada':
                vacinacoes = vacinacoes.filter(data_revacinacao__lt=hoje)
            elif status_revacinacao == 'nao_definida':
                vacinacoes = vacinacoes.filter(data_revacinacao__isnull=True)
    
    for vacina in vacinacoes:
        if vacina.data_revacinacao:
            vacina.days_diff = (vacina.data_revacinacao - hoje).days
        else:
            vacina.days_diff = None

    context = {'vacinacoes': vacinacoes, 'form': form, 'hoje': hoje}
    return render(request, 'relatorios/relatorio_vacinacao.html', context)

def relatorio_vacinacao_pdf(request):
    form = FiltroVacinacaoForm(request.GET)
    vacinacoes = RegistroVacinacao.objects.all().order_by('-data_aplicacao')
    hoje = timezone.now().date()

    if form.is_valid():
        animal = form.cleaned_data.get('animal')
        data_aplicacao_inicio = form.cleaned_data.get('data_aplicacao_inicio')
        data_aplicacao_fim = form.cleaned_data.get('data_aplicacao_fim')
        status_revacinacao = form.cleaned_data.get('status_revacinacao')
        medicamento = form.cleaned_data.get('medicamento')

        if animal:
            vacinacoes = vacinacoes.filter(animal=animal)
        if data_aplicacao_inicio:
            vacinacoes = vacinacoes.filter(data_aplicacao__gte=data_aplicacao_inicio)
        if data_aplicacao_fim:
            vacinacoes = vacinacoes.filter(data_aplicacao__lte=data_aplicacao_fim)
        if medicamento:
            vacinacoes = vacinacoes.filter(medicamento_aplicado=medicamento)

        if status_revacinacao:
            if status_revacinacao == 'ok':
                vacinacoes = vacinacoes.filter(Q(data_revacinacao__gte=hoje + timedelta(days=31)) | Q(data_revacinacao__isnull=True))
            elif status_revacinacao == 'vencendo':
                limite_vencimento = hoje + timedelta(days=30)
                vacinacoes = vacinacoes.filter(data_revacinacao__range=(hoje, limite_vencimento))
            elif status_revacinacao == 'atrasada':
                vacinacoes = vacinacoes.filter(data_revacinacao__lt=hoje)
            elif status_revacinacao == 'nao_definida':
                vacinacoes = vacinacoes.filter(data_revacinacao__isnull=True)

    for vacina in vacinacoes:
        if vacina.data_revacinacao:
            vacina.days_diff = (vacina.data_revacinacao - hoje).days
        else:
            vacina.days_diff = None

    template = get_template('relatorios/relatorio_vacinacao_pdf.html')
    html = template.render({'vacinacoes': vacinacoes, 'total_registros': vacinacoes.count(), 'hoje': hoje})
    
    pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[
            CSS(string='@page { size: A4; margin: 1cm; }'),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/base.css'))),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/forms.css'))),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/changelists.css'))),
        ]
    )

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_vacinacao.pdf"'
    return response


def relatorio_vermifugos(request):
    form = FiltroVermifugosForm(request.GET)
    vermifugos = RegistroVermifugos.objects.all().order_by('-data_administracao')
    hoje = timezone.now().date()

    if form.is_valid():
        animal = form.cleaned_data.get('animal')
        data_administracao_inicio = form.cleaned_data.get('data_administracao_inicio')
        data_administracao_fim = form.cleaned_data.get('data_administracao_fim')
        status_readministracao = form.cleaned_data.get('status_readministracao')
        medicamento = form.cleaned_data.get('medicamento')

        if animal:
            vermifugos = vermifugos.filter(animal=animal)
        if data_administracao_inicio:
            vermifugos = vermifugos.filter(data_administracao__gte=data_administracao_inicio)
        if data_administracao_fim:
            vermifugos = vermifugos.filter(data_administracao__lte=data_administracao_fim)
        if medicamento:
            vermifugos = vermifugos.filter(medicamento_administrado=medicamento)

        if status_readministracao:
            if status_readministracao == 'ok':
                vermifugos = vermifugos.filter(Q(data_readministracao__gte=hoje + timedelta(days=31)) | Q(data_readministracao__isnull=True))
            elif status_readministracao == 'vencendo':
                limite_readministracao = hoje + timedelta(days=30)
                vermifugos = vermifugos.filter(data_readministracao__range=(hoje, limite_readministracao))
            elif status_readministracao == 'atrasada':
                vermifugos = vermifugos.filter(data_readministracao__lt=hoje)
            elif status_readministracao == 'nao_definida':
                vermifugos = vermifugos.filter(data_readministracao__isnull=True)

    for vermifugo in vermifugos:
        if vermifugo.data_readministracao:
            vermifugo.days_diff = (vermifugo.data_readministracao - hoje).days
        else:
            vermifugo.days_diff = None

    context = {'vermifugos': vermifugos, 'form': form, 'hoje': hoje}
    return render(request, 'relatorios/relatorio_vermifugos.html', context)

def relatorio_vermifugos_pdf(request):
    form = FiltroVermifugosForm(request.GET)
    vermifugos = RegistroVermifugos.objects.all().order_by('-data_administracao')
    hoje = timezone.now().date()

    if form.is_valid():
        animal = form.cleaned_data.get('animal')
        data_administracao_inicio = form.cleaned_data.get('data_administracao_inicio')
        data_administracao_fim = form.cleaned_data.get('data_administracao_fim')
        status_readministracao = form.cleaned_data.get('status_readministracao')
        medicamento = form.cleaned_data.get('medicamento')

        if animal:
            vermifugos = vermifugos.filter(animal=animal)
        if data_administracao_inicio:
            vermifugos = vermifugos.filter(data_administracao__gte=data_administracao_inicio)
        if data_administracao_fim:
            vermifugos = vermifugos.filter(data_administracao__lte=data_administracao_fim)
        if medicamento:
            vermifugos = vermifugos.filter(medicamento_administrado=medicamento)

        if status_readministracao:
            if status_readministracao == 'ok':
                vermifugos = vermifugos.filter(Q(data_readministracao__gte=hoje + timedelta(days=31)) | Q(data_readministracao__isnull=True))
            elif status_readministracao == 'vencendo':
                limite_readministracao = hoje + timedelta(days=30)
                vermifugos = vermifugos.filter(data_readministracao__range=(hoje, limite_readministracao))
            elif status_readministracao == 'atrasada':
                vermifugos = vermifugos.filter(data_readministracao__lt=hoje)
            elif status_readministracao == 'nao_definida':
                vermifugos = vermifugos.filter(data_readministracao__isnull=True)

    for vermifugo in vermifugos:
        if vermifugo.data_readministracao:
            vermifugo.days_diff = (vermifugo.data_readministracao - hoje).days
        else:
            vermifugo.days_diff = None

    template = get_template('relatorios/relatorio_vermifugos_pdf.html')
    html = template.render({'vermifugos': vermifugos, 'total_registros': vermifugos.count(), 'hoje': hoje})
    
    pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[
            CSS(string='@page { size: A4; margin: 1cm; }'),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/base.css'))),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/forms.css'))),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/changelists.css'))),
        ]
    )

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_vermifugos.pdf"'
    return response

# --- NOVAS VIEWS PARA RELATÓRIO DE SERVIÇOS ---
def relatorio_servicos(request):
    form = FiltroRegistroServicoForm(request.GET)
    servicos = RegistroServico.objects.all().order_by('-data_hora_procedimento')

    if form.is_valid():
        animal = form.cleaned_data.get('animal')
        empresa = form.cleaned_data.get('empresa')
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        busca_texto = form.cleaned_data.get('busca_texto')

        if animal:
            servicos = servicos.filter(animal=animal)
        if empresa:
            servicos = servicos.filter(empresa=empresa)
        if data_inicio:
            servicos = servicos.filter(data_hora_procedimento__date__gte=data_inicio)
        if data_fim:
            servicos = servicos.filter(data_hora_procedimento__date__lte=data_fim)
        
        if busca_texto:
            servicos = servicos.filter(
                Q(medicamentos_aplicados__icontains=busca_texto) |
                Q(outros_procedimentos__icontains=busca_texto)
            )

    context = {'servicos': servicos, 'form': form}
    return render(request, 'relatorios/relatorio_servicos.html', context)

def relatorio_servicos_pdf(request):
    form = FiltroRegistroServicoForm(request.GET)
    servicos = RegistroServico.objects.all().order_by('-data_hora_procedimento')

    if form.is_valid():
        animal = form.cleaned_data.get('animal')
        empresa = form.cleaned_data.get('empresa')
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        busca_texto = form.cleaned_data.get('busca_texto')

        if animal:
            servicos = servicos.filter(animal=animal)
        if empresa:
            servicos = servicos.filter(empresa=empresa)
        if data_inicio:
            servicos = servicos.filter(data_hora_procedimento__date__gte=data_inicio)
        if data_fim:
            servicos = servicos.filter(data_hora_procedimento__date__lte=data_fim)
        
        if busca_texto:
            servicos = servicos.filter(
                Q(medicamentos_aplicados__icontains=busca_texto) |
                Q(outros_procedimentos__icontains=busca_texto)
            )

    template = get_template('relatorios/relatorio_servicos_pdf.html')
    html = template.render({'servicos': servicos, 'total_registros': servicos.count()})
    
    pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[
            CSS(string='@page { size: A4; margin: 1cm; }'),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/base.css'))),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/forms.css'))),
            CSS(url=request.build_absolute_uri(staticfiles_storage.url('admin/css/changelists.css'))),
        ]
    )

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_servicos.pdf"'
    return response

def painel_gerencial(request):
    hoje = timezone.localdate()
    agendamentos_hoje_qs = AgendamentoConsultas.objects.filter(data_consulta__date=hoje).order_by('data_consulta')
    
    # Medicamentos vencendo em 30 dias ou vencidos
    data_limite_vencimento = hoje + timedelta(days=30)
    medicamentos_criticos_qs = EstoqueMedicamento.objects.filter(data_validade__lte=data_limite_vencimento).exclude(quantidade=0).order_by('data_validade')

    # Vacinações com revacinação hoje ou atrasadas
    vacinacoes_pendentes_qs = RegistroVacinacao.objects.filter(
        data_revacinacao__lte=hoje
    ).exclude(data_revacinacao__isnull=True).order_by('data_revacinacao')

    # Vermifugações com readministração hoje ou atrasadas
    vermifugacoes_pendentes_qs = RegistroVermifugos.objects.filter(
        data_readministracao__lte=hoje
    ).exclude(data_readministracao__isnull=True).order_by('data_readministracao')

    # Lógica para Agendamentos na Semana
    dia_semana_atual = hoje.weekday() # 0 = segunda, 6 = domingo
    inicio_semana = hoje - timedelta(days=dia_semana_atual)
    fim_semana = inicio_semana + timedelta(days=6)
    agendamentos_semana_qs = AgendamentoConsultas.objects.filter(
        data_consulta__date__gte=inicio_semana,
        data_consulta__date__lte=fim_semana
    ).order_by('data_consulta')

    context = {
        'agendamentos_hoje': agendamentos_hoje_qs, # Renomeado para template
        'vacinas_hoje': vacinacoes_pendentes_qs,   # Renomeado para template
        'vermifugos_hoje': vermifugacoes_pendentes_qs, # Renomeado para template
        'medicamentos_vencer': medicamentos_criticos_qs, # Renomeado para template
        'agendamentos_semana': agendamentos_semana_qs, # Adicionado
        'hoje': hoje,
    }
    return render(request, 'admin/painel_gerencial.html', context)