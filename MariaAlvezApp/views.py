from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta, date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML, CSS

from .models import (
    ConsultaClinica, EstoqueMedicamento, RegistroVacinacao,
    RegistroVermifugos, Tutor, Animal
)
from .forms import (
    FiltroConsultaForm, FiltroEstoqueForm,
    FiltroVacinacaoForm, FiltroVermifugosForm
)

@login_required
@user_passes_test(lambda u: u.is_staff)
def relatorios_index(request):
    return render(request, 'relatorios/relatorios_index.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def relatorio_consultas(request):
    form = FiltroConsultaForm(request.GET or None)
    consultas = ConsultaClinica.objects.all().order_by('-data_atendimento')

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        tutor_selecionado = form.cleaned_data.get('tutor')
        animal_selecionado = form.cleaned_data.get('animal')

        if data_inicio:
            consultas = consultas.filter(data_atendimento__date__gte=data_inicio)
        if data_fim:
            consultas = consultas.filter(data_atendimento__date__lte=data_fim)
        if animal_selecionado:
            consultas = consultas.filter(animal=animal_selecionado)
        elif tutor_selecionado:
            consultas = consultas.filter(animal__tutor=tutor_selecionado)

    return render(request, 'relatorios/relatorio_consultas.html', {
        'form': form,
        'consultas': consultas,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def relatorio_estoque(request):
    form = FiltroEstoqueForm(request.GET or None)
    estoque = EstoqueMedicamento.objects.all().order_by('data_validade', 'medicamento')

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

        hoje = timezone.now().date()
        if status_estoque == 'com_estoque':
            estoque = estoque.filter(quantidade__gt=0)
        elif status_estoque == 'sem_estoque':
            estoque = estoque.filter(quantidade=0)
        elif status_estoque == 'vencidos':
            estoque = estoque.filter(data_validade__lt=hoje)
        elif status_estoque == 'vencendo':
            data_limite_vencendo = hoje + timedelta(days=30)
            estoque = estoque.filter(data_validade__range=(hoje, data_limite_vencendo))

    return render(request, 'relatorios/relatorio_estoque.html', {
        'form': form,
        'estoque': estoque,
        'hoje': timezone.now().date()
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def relatorio_vacinacao(request):
    form = FiltroVacinacaoForm(request.GET or None)
    vacinacoes = RegistroVacinacao.objects.all().order_by('-data_aplicacao')

    if form.is_valid():
        animal_selecionado = form.cleaned_data.get('animal')
        data_aplicacao_inicio = form.cleaned_data.get('data_aplicacao_inicio')
        data_aplicacao_fim = form.cleaned_data.get('data_aplicacao_fim')
        status_revacacao = form.cleaned_data.get('status_revacinacao')
        medicamento_selecionado = form.cleaned_data.get('medicamento')

        if animal_selecionado:
            vacinacoes = vacinacoes.filter(animal=animal_selecionado)
        if data_aplicacao_inicio:
            vacinacoes = vacinacoes.filter(data_aplicacao__gte=data_aplicacao_inicio)
        if data_aplicacao_fim:
            vacinacoes = vacinacoes.filter(data_aplicacao__lte=data_aplicacao_fim)
        if medicamento_selecionado:
            vacinacoes = vacinacoes.filter(medicamento_aplicado=medicamento_selecionado)

        hoje = timezone.now().date()
        if status_revacacao:
            q_objects = Q()
            if status_revacacao == 'ok':
                q_objects &= Q(data_revacinacao__gte=hoje)
            elif status_revacacao == 'vencendo':
                data_limite_vencendo = hoje + timedelta(days=30)
                q_objects &= Q(data_revacinacao__range=(hoje, data_limite_vencendo))
            elif status_revacacao == 'atrasada':
                q_objects &= Q(data_revacinacao__lt=hoje)
            elif status_revacacao == 'nao_definida':
                q_objects &= Q(data_revacinacao__isnull=True)
            vacinacoes = vacinacoes.filter(q_objects)


    hoje = timezone.now().date() 
    for vacina in vacinacoes:
        if vacina.data_revacinacao:
            delta = vacina.data_revacinacao - hoje
            vacina.days_diff = delta.days
        else:
            vacina.days_diff = None 

    return render(request, 'relatorios/relatorio_vacinacao.html', {
        'form': form,
        'vacinacoes': vacinacoes,
        'hoje': hoje 
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def relatorio_vermifugos(request):
    form = FiltroVermifugosForm(request.GET or None)
    vermifugos = RegistroVermifugos.objects.all().order_by('-data_administracao')

    if form.is_valid():
        animal_selecionado = form.cleaned_data.get('animal')
        data_administracao_inicio = form.cleaned_data.get('data_administracao_inicio')
        data_administracao_fim = form.cleaned_data.get('data_administracao_fim')
        status_readmin = form.cleaned_data.get('status_readministracao')
        medicamento_selecionado = form.cleaned_data.get('medicamento')

        if animal_selecionado:
            vermifugos = vermifugos.filter(animal=animal_selecionado)
        if data_administracao_inicio:
            vermifugos = vermifugos.filter(data_administracao__gte=data_administracao_inicio)
        if data_administracao_fim:
            vermifugos = vermifugos.filter(data_administracao__lte=data_administracao_fim)
        if medicamento_selecionado:
            vermifugos = vermifugos.filter(medicamento_administrado=medicamento_selecionado)

        hoje = timezone.now().date()
        if status_readmin:
            q_objects = Q()
            if status_readmin == 'ok':
                q_objects &= Q(data_readministracao__gte=hoje)
            elif status_readmin == 'vencendo':
                data_limite_vencendo = hoje + timedelta(days=30)
                q_objects &= Q(data_readministracao__range=(hoje, data_limite_vencendo))
            elif status_readmin == 'atrasada':
                q_objects &= Q(data_readministracao__lt=hoje)
            elif status_readmin == 'nao_definida':
                q_objects &= Q(data_readministracao__isnull=True)
            vermifugos = vermifugos.filter(q_objects)

    hoje = timezone.now().date()
    for vermifugo in vermifugos:
        if vermifugo.data_readministracao:
            delta = vermifugo.data_readministracao - hoje
            vermifugo.days_diff = delta.days
        else:
            vermifugo.days_diff = None

    return render(request, 'relatorios/relatorio_vermifugos.html', {
        'form': form,
        'vermifugos': vermifugos,
        'hoje': hoje
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def relatorio_consultas_pdf(request):
    form = FiltroConsultaForm(request.GET or None)
    consultas = ConsultaClinica.objects.all().order_by('-data_atendimento')

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        tutor_selecionado = form.cleaned_data.get('tutor')
        animal_selecionado = form.cleaned_data.get('animal')

        if data_inicio:
            consultas = consultas.filter(data_atendimento__date__gte=data_inicio)
        if data_fim:
            consultas = consultas.filter(data_atendimento__date__lte=data_fim)
        if animal_selecionado:
            consultas = consultas.filter(animal=animal_selecionado)
        elif tutor_selecionado:
            consultas = consultas.filter(animal__tutor=tutor_selecionado)

    template = get_template('relatorios/relatorio_consultas_pdf.html')
    context = {
        'form': form,
        'consultas': consultas,
        'total_consultas': consultas.count(),
        'request': request,
    }
    html_string = template.render(context)

    try:
        pdf_html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = pdf_html.write_pdf()

    except Exception as e:
        print(f"Erro ao gerar o PDF: {e}")
        return HttpResponse(f"Erro ao gerar o PDF: {e}", status=500)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_consultas.pdf"'
    return response

@login_required
@user_passes_test(lambda u: u.is_staff)
def relatorio_estoque_pdf(request):
    form = FiltroEstoqueForm(request.GET or None)
    estoque = EstoqueMedicamento.objects.all().order_by('data_validade', 'medicamento')

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

        hoje = timezone.now().date()
        if status_estoque == 'com_estoque':
            estoque = estoque.filter(quantidade__gt=0)
        elif status_estoque == 'sem_estoque':
            estoque = estoque.filter(quantidade=0)
        elif status_estoque == 'vencidos':
            estoque = estoque.filter(data_validade__lt=hoje)
        elif status_estoque == 'vencendo':
            data_limite_vencendo = hoje + timedelta(days=30)
            estoque = estoque.filter(data_validade__range=(hoje, data_limite_vencendo))

    template = get_template('relatorios/relatorio_estoque_pdf.html')
    context = {
        'form': form,
        'estoque': estoque,
        'hoje': timezone.now().date(),
        'total_lotes': estoque.count(),
        'request': request,
    }
    html_string = template.render(context)

    try:
        pdf_html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = pdf_html.write_pdf()

    except Exception as e:
        print(f"Erro ao gerar o PDF de Estoque: {e}")
        return HttpResponse(f"Erro ao gerar o PDF de Estoque: {e}", status=500)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_estoque.pdf"'
    return response


@login_required
@user_passes_test(lambda u: u.is_staff)
def relatorio_vacinacao_pdf(request):
    form = FiltroVacinacaoForm(request.GET or None)
    vacinacoes = RegistroVacinacao.objects.all().order_by('-data_aplicacao')

    if form.is_valid():
        animal_selecionado = form.cleaned_data.get('animal')
        data_aplicacao_inicio = form.cleaned_data.get('data_aplicacao_inicio')
        data_aplicacao_fim = form.cleaned_data.get('data_aplicacao_fim')
        status_revacacao = form.cleaned_data.get('status_revacinacao')
        medicamento_selecionado = form.cleaned_data.get('medicamento')

        if animal_selecionado:
            vacinacoes = vacinacoes.filter(animal=animal_selecionado)
        if data_aplicacao_inicio:
            vacinacoes = vacinacoes.filter(data_aplicacao__gte=data_aplicacao_inicio)
        if data_aplicacao_fim:
            vacinacoes = vacinacoes.filter(data_aplicacao__lte=data_aplicacao_fim)
        if medicamento_selecionado:
            vacinacoes = vacinacoes.filter(medicamento_aplicado=medicamento_selecionado)

        hoje = timezone.now().date()
        if status_revacacao:
            q_objects = Q()
            if status_revacacao == 'ok':
                q_objects &= Q(data_revacinacao__gte=hoje)
            elif status_revacacao == 'vencendo':
                data_limite_vencendo = hoje + timedelta(days=30)
                q_objects &= Q(data_revacinacao__range=(hoje, data_limite_vencendo))
            elif status_revacacao == 'atrasada':
                q_objects &= Q(data_revacinacao__lt=hoje)
            elif status_revacacao == 'nao_definida':
                q_objects &= Q(data_revacinacao__isnull=True)
            vacinacoes = vacinacoes.filter(q_objects)

    hoje = timezone.now().date()
    for vacina in vacinacoes:
        if vacina.data_revacinacao:
            delta = vacina.data_revacinacao - hoje
            vacina.days_diff = delta.days
        else:
            vacina.days_diff = None

    template = get_template('relatorios/relatorio_vacinacao_pdf.html')
    context = {
        'form': form,
        'vacinacoes': vacinacoes,
        'hoje': hoje,
        'total_registros': vacinacoes.count(),
        'request': request,
    }
    html_string = template.render(context)

    try:
        pdf_html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = pdf_html.write_pdf()

    except Exception as e:
        print(f"Erro ao gerar o PDF de Vacinação: {e}")
        return HttpResponse(f"Erro ao gerar o PDF de Vacinação: {e}", status=500)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_vacinacao.pdf"'
    return response


@login_required
@user_passes_test(lambda u: u.is_staff)
def relatorio_vermifugos_pdf(request):
    form = FiltroVermifugosForm(request.GET or None)
    vermifugos = RegistroVermifugos.objects.all().order_by('-data_administracao')

    if form.is_valid():
        animal_selecionado = form.cleaned_data.get('animal')
        data_administracao_inicio = form.cleaned_data.get('data_administracao_inicio')
        data_administracao_fim = form.cleaned_data.get('data_administracao_fim')
        status_readmin = form.cleaned_data.get('status_readministracao')
        medicamento_selecionado = form.cleaned_data.get('medicamento')

        if animal_selecionado:
            vermifugos = vermifugos.filter(animal=animal_selecionado)
        if data_administracao_inicio:
            vermifugos = vermifugos.filter(data_administracao__gte=data_administracao_inicio)
        if data_administracao_fim:
            vermifugos = vermifugos.filter(data_administracao__lte=data_administracao_fim)
        if medicamento_selecionado:
            vermifugos = vermifugos.filter(medicamento_administrado=medicamento_selecionado)

        hoje = timezone.now().date()
        if status_readmin:
            q_objects = Q()
            if status_readmin == 'ok':
                q_objects &= Q(data_readministracao__gte=hoje)
            elif status_readmin == 'vencendo':
                data_limite_vencendo = hoje + timedelta(days=30)
                q_objects &= Q(data_readministracao__range=(hoje, data_limite_vencendo))
            elif status_readmin == 'atrasada':
                q_objects &= Q(data_readministracao__lt=hoje)
            elif status_readmin == 'nao_definida':
                q_objects &= Q(data_readministracao__isnull=True)
            vermifugos = vermifugos.filter(q_objects)

    hoje = timezone.now().date()
    for vermifugo in vermifugos:
        if vermifugo.data_readministracao:
            delta = vermifugo.data_readministracao - hoje
            vermifugo.days_diff = delta.days
        else:
            vermifugo.days_diff = None

    template = get_template('relatorios/relatorio_vermifugos_pdf.html')
    context = {
        'form': form,
        'vermifugos': vermifugos,
        'hoje': hoje,
        'total_registros': vermifugos.count(),
        'request': request,
    }
    html_string = template.render(context)

    try:
        pdf_html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = pdf_html.write_pdf()

    except Exception as e:
        print(f"Erro ao gerar o PDF de Vermífugos: {e}")
        return HttpResponse(f"Erro ao gerar o PDF de Vermífugos: {e}", status=500)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_vermifugos.pdf"'
    return response
