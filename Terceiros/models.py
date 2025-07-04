# Terceiros/models.py

from django.db import models
from django.utils import timezone
from MariaAlvezApp.models import Animal
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator # Mantenha se quiser usar em outros campos
import re

# --- Função de Validação de CNPJ (Mantenha esta) ---
def validar_cnpj(cnpj):
    # ... (sua implementação de validar_cnpj aqui) ...
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) != 14:
        raise ValidationError('CNPJ deve conter 14 dígitos numéricos.')
    if cnpj == cnpj[0] * 14:
        raise ValidationError('CNPJ inválido (todos os dígitos são iguais).')
    def calcular_digito(base, pesos):
        soma = 0
        for i in range(len(base)):
            soma += int(base[i]) * pesos[i]
        digito = 11 - (soma % 11)
        return digito if digito <= 9 else 0
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    cnpj_base = cnpj[:12]
    primeiro_digito = calcular_digito(cnpj_base, pesos1)
    if primeiro_digito != int(cnpj[12]):
        raise ValidationError('CNPJ inválido (primeiro dígito verificador incorreto).')
    cnpj_base_com_dv1 = cnpj[:13]
    segundo_digito = calcular_digito(cnpj_base_com_dv1, pesos2)
    if segundo_digito != int(cnpj[13]):
        raise ValidationError('CNPJ inválido (segundo dígito verificador incorreto).')
    return cnpj

# --- NOVA FUNÇÃO validar_telefone ---
def validar_telefone(telefone):
    # Remove caracteres não numéricos para validação
    telefone_numeros = re.sub(r'\D', '', telefone)
    
    # Verifica se tem exatamente 11 dígitos
    if not re.fullmatch(r'\d{11}', telefone_numeros):
        raise ValidationError('Telefone inválido. Deve conter exatamente 11 dígitos (DDD + 9 dígitos), sem máscara. Ex: 49998086201.')


class EmpresaTerceirizada(models.Model):
    razao_social = models.CharField(
        max_length=200, 
        verbose_name="Razão Social",
        unique=True,
        help_text="Nome completo da empresa."
    )
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name="CNPJ",
        validators=[validar_cnpj],
        help_text="Número de Cadastro Nacional de Pessoa Jurídica (14 dígitos)."
    )
    telefone = models.CharField(
        max_length=15, # Max_length deve ser capaz de guardar o formato mascarado
        verbose_name="Telefone",
        blank=True,
        null=True,
        validators=[validar_telefone], # <--- Usando a nova função
        help_text="Telefone do tutor com DDD. Ex: 49998086201 (apenas números, a máscara será aplicada automaticamente)."
    )
    email = models.EmailField(
        verbose_name="E-mail",
        unique=True,
        blank=True,
        null=True,
        help_text="Endereço de e-mail da empresa."
    )
    
    class Meta:
        verbose_name = "Empresa Terceirizada"
        verbose_name_plural = "Empresas Terceirizadas"
        ordering = ['razao_social']
    
    def clean(self):
        super().clean()
        
        # Limpa e formata o CNPJ
        if self.cnpj:
            self.cnpj = re.sub(r'\D', '', self.cnpj)
            # A validação validar_cnpj já garante 14 dígitos.
            # Aqui, apenas aplicamos a máscara se for um CNPJ válido.
            if len(self.cnpj) == 14:
                self.cnpj = f"{self.cnpj[:2]}.{self.cnpj[2:5]}.{self.cnpj[5:8]}/{self.cnpj[8:12]}-{self.cnpj[12:]}"

        # Limpa e formata o telefone
        if self.telefone:
            tel_numeros = re.sub(r'\D', '', self.telefone)
            # A validação validar_telefone já garante 11 dígitos.
            # Aqui, apenas aplicamos a máscara.
            if len(tel_numeros) == 11:
                self.telefone = f"({tel_numeros[:2]}) {tel_numeros[2:7]}-{tel_numeros[7:]}"
            # Se não tiver 11 dígitos, a validação já impediu o clean de ser chamado ou um erro já ocorreu antes.

    def __str__(self):
        return self.razao_social


class RegistroServico(models.Model):
    empresa = models.ForeignKey(
        EmpresaTerceirizada,
        on_delete=models.PROTECT,
        verbose_name="Empresa Prestadora"
    )

    animal = models.ForeignKey(
        Animal, 
        on_delete=models.SET_NULL,
        blank=False,
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
        help_text="Custo do serviço. Deixe em branco se não aplicável."
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
    
    def clean(self): # <--- ADICIONE ESTE MÉTODO OU ATUALIZE-O
        super().clean()

        # Validação para valor_servico (opcional, mas se preenchido, > 0)
        # self.valor_servico pode ser None ou Decimal('0.00')
        if self.valor_servico is not None and self.valor_servico <= 0:
            raise ValidationError({
                'valor_servico': 'O valor do serviço deve ser maior que zero, se preenchido.'
            })
        
        # Validação para data_hora_procedimento (não pode ser no futuro)
        if self.data_hora_procedimento and self.data_hora_procedimento > timezone.now():
            raise ValidationError({
                'data_hora_procedimento': 'A data e hora do procedimento não pode estar no futuro.'
            })

    def __str__(self):
        nome_animal = self.animal.nome if self.animal else "Animal não informado"
        data_formatada = self.data_hora_procedimento.strftime('%d/%m/%Y às %H:%M')
        return f"Atendimento para {nome_animal} em {data_formatada}"

    class Meta:
        verbose_name = "Registro de Serviço"
        verbose_name_plural = "Registros de Serviços"
        ordering = ['-data_hora_procedimento']