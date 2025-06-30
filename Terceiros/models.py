from django.db import models
from django.utils import timezone
from MariaAlvezApp.models import Animal 


class EmpresaTerceirizada(models.Model):
    razao_social = models.CharField(max_length=200, verbose_name="Razão Social")
    cnpj = models.CharField(max_length=18, unique=True, help_text="Formato: XX.XXX.XXX/XXXX-XX")
    telefone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.razao_social

    class Meta:
        verbose_name = "Empresa Terceirizada"
        verbose_name_plural = "Empresas Terceirizadas"
        ordering = ['razao_social']


class RegistroServico(models.Model):
    empresa = models.ForeignKey(
        EmpresaTerceirizada,
        on_delete=models.PROTECT,
        verbose_name="Empresa Prestadora"
    )

    animal = models.ForeignKey(
        Animal, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Animal Atendido"
    )
    
    data_hora_procedimento = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data e Hora do Procedimento"
    )

    valor_servico = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor do Serviço (R$)",
        help_text="Custo do serviço. Deixe em branco se não aplicável." # ASPAS ADICIONADAS AQUI
    )
    
    medicamentos_aplicados = models.TextField(
        blank=True,
        verbose_name="Medicamentos Aplicados",
        help_text="Liste os medicamentos e dosagens."
    )
    outros_procedimentos = models.TextField(
        blank=True,
        verbose_name="Outros Procedimentos Realizados",
        help_text="Descreva outros procedimentos, como curativos, exames, etc."
    )
    
    def __str__(self):
        nome_animal = self.animal.nome if self.animal else "Animal não informado"
        data_formatada = self.data_hora_procedimento.strftime('%d/%m/%Y às %H:%M')
        return f"Atendimento para {nome_animal} em {data_formatada}"

    class Meta:
        verbose_name = "Registro de Serviço"
        verbose_name_plural = "Registros de Serviços"
        ordering = ['-data_hora_procedimento']