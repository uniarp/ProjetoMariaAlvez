from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from reportlab.pdfgen import canvas
from .models import ConsultaClinica, Medicamentos, Animal, RegistroVacinacao, RegistroVermifugos


def gerar_relatorio_consultas(request):
    consultas = ConsultaClinica.objects.select_related('animal', 'vet_responsavel').order_by('-data_atendimento')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_consultas.pdf"'
    pdf = canvas.Canvas(response)
    
    y = 800
    pdf.drawString(20, y + 20, "Relatório de Consultas Clínicas")
    for consulta in consultas:
        linha = f"{consulta.data_atendimento} - {consulta.animal.nome} - {consulta.vet_responsavel.nome}"
        pdf.drawString(20, y, linha)
        y -= 20
        if y <= 40:  # quebra de página se necessário
            pdf.showPage()
            y = 800

    pdf.showPage()
    pdf.save()
    return response


# 2. RELATÓRIO DE ESTOQUE DE MEDICAMENTOS (HTML)
def relatorio_estoque(request):
    medicamentos = Medicamentos.objects.all().order_by('nome')
    hoje = timezone.now().date()
    return render(request, 'relatorio_estoque.html', {
        'medicamentos': medicamentos,
        'hoje': hoje
    })


# 3. FILA DE CASTRAÇÃO (HTML)
def fila_castracao(request):
    fila = Animal.objects.filter(castrado=False).order_by('idade')
    return render(request, 'fila_castracao.html', {'fila': fila})


# 4. RELATÓRIO DE VACINAÇÃO (HTML)
def relatorio_vacinacao(request):
    vacinacoes = RegistroVacinacao.objects.select_related('animal', 'medicamento').order_by('-data_aplicacao')
    return render(request, 'relatorio_vacinacao.html', {'vacinacoes': vacinacoes})


# 5. RELATÓRIO DE VERMÍFUGOS (HTML)
def relatorio_vermifugo(request):
    vermifugos = RegistroVermifugos.objects.select_related('animal', 'medicamento').order_by('-data_administracao')
    return render(request, 'relatorio_vermifugo.html', {'vermifugos': vermifugos})