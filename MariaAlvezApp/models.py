from django.core.exceptions import ValidationError
from django.utils.html import format_html
from datetime import timedelta, datetime, date
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
import re
from django.utils import timezone
from django.utils.timezone import localtime


# Classes principais
class Veterinario(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome do Veterinário", default="Nome do Veterinário")
    crmv = models.CharField(max_length=50, unique=True, verbose_name="CRMV", default="00000-UF")
    telefone = models.CharField(max_length=15, verbose_name="Telefone", blank=True, null=True)
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)

    class Meta:
        verbose_name = "Veterinário"
        verbose_name_plural = "Veterinários"

    def __str__(self):
        return f"{self.nome} (CRMV: {self.crmv})"

def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError(_('CPF inválido.'))

    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            raise ValidationError(_('CPF inválido.'))

def validar_telefone(telefone):
    telefone_numeros = re.sub(r'\D', '', telefone)
    if not re.fullmatch(r'\d{10,11}', telefone_numeros):
        raise ValidationError(_('Telefone inválido. Deve conter 10 ou 11 dígitos.'))

class Tutor(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    cpf = models.CharField(max_length=14, unique=True, validators=[validar_cpf], verbose_name="CPF")
    telefone = models.CharField(max_length=15, validators=[validar_telefone], verbose_name="Telefone")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    endereco = models.CharField(max_length=255, verbose_name="Endereço")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=50, verbose_name="Estado")
    cep = models.CharField(max_length=9, verbose_name="CEP")

    def clean(self):
        self.validar_data_nascimento()
        self.aplicar_mascaras()
        super().clean() # Chame o clean do pai por último

    def validar_data_nascimento(self):
        hoje = date.today()
        limite_inferior = date(hoje.year - 120, hoje.month, hoje.day)
        idade_minima = hoje.replace(year=hoje.year - 16)

        if self.data_nascimento > hoje:
            raise ValidationError({'data_nascimento': _('A data de nascimento não pode estar no futuro.')})

        if self.data_nascimento < limite_inferior:
            raise ValidationError({'data_nascimento': _('A data de nascimento é muito antiga. Deve estar nos últimos 120 anos.')})

        if self.data_nascimento > idade_minima:
            raise ValidationError({'data_nascimento': _('O tutor precisa ter no mínimo 16 anos para cadastro.')})

    def aplicar_mascaras(self):
        # CPF
        cpf = re.sub(r'\D', '', self.cpf)
        if len(cpf) == 11:
            self.cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        
        # Telefone
        tel = re.sub(r'\D', '', self.telefone)
        if len(tel) == 11:
            self.telefone = f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
        elif len(tel) == 10:
            self.telefone = f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
        
        # CEP
        cep = re.sub(r'\D', '', self.cep)
        if len(cep) == 8:
            self.cep = f"{cep[:5]}-{cep[5:]}"

    def __str__(self):
        return f"{self.nome} ({self.cpf})"
    
class Animal(models.Model):
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
    ]

    nome = models.CharField(max_length=150, default="Nome", verbose_name="Nome")
    especie = models.CharField(max_length=100, default="Especie", verbose_name="Espécie")

    idade_anos = models.PositiveIntegerField(default=0, verbose_name="Anos")
    idade_meses = models.PositiveIntegerField(default=0, verbose_name="Meses")
    idade_dias = models.PositiveIntegerField(default=0, verbose_name="Dias")

    sexo = models.CharField(max_length=15, choices=SEXO_CHOICES, default="Sexo", verbose_name="Sexo")

    peso = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=3,
        help_text="Peso em quilogramas",
        verbose_name="Peso (kg)"
    )

    castrado = models.BooleanField(default=False, verbose_name="Castrado(a)")
    rfid = models.CharField(max_length=128, unique=True, default="0", verbose_name="RFID") # Default como string para evitar int conversion issues

    def clean(self):
        super().clean() # Chame o clean do pai primeiro
        # Valida idade
        if self.idade_anos == 0 and self.idade_meses == 0 and self.idade_dias == 0:
            raise ValidationError('O animal deve ter ao menos 1 dia de idade.')

        # Valida peso
        if self.peso <= 0:
            raise ValidationError({'peso': 'O peso deve ser maior que zero.'})

        self.nome = self.nome.strip().capitalize()
        self.especie = self.especie.strip().capitalize()

    def __str__(self): # Corrigido de _str_ para __str__
        return f"{self.nome} ({self.especie}) - {self.get_sexo_display()}"

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"

class ConsultaClinica(models.Model):
    # Adicione campos para ConsultaClinica conforme necessário
    # Por exemplo:
    # animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    # data_consulta = models.DateTimeField()
    # diagnostico = models.TextField(blank=True, null=True)
    # tratamento = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Consulta Clínica"
        verbose_name_plural = "Consultas Clínicas"
    
    def __str__(self):
        # Adapte este retorno conforme os campos que você adicionar em ConsultaClinica
        return "Consulta Clínica (sem detalhes)"


class AgendamentoConsultas(models.Model):
    data_consulta = models.DateTimeField(
        verbose_name="Data da Consulta",
        default=timezone.now,
        blank=True,
        null=True,
    )
    tutor = models.ForeignKey(
        'Tutor',
        on_delete=models.CASCADE,
        related_name='agendamentos',
        verbose_name="Tutor",
        blank=False,
        null=False,
    )
    animal = models.ForeignKey(
        'Animal',
        on_delete=models.CASCADE,
        related_name='agendamentos_consultas',
        verbose_name="Animal",
        blank=False,
        null=False,
    )
    def clean(self):
        super().clean()
        if self.data_consulta and self.data_consulta < timezone.now(): # Verifique se data_consulta não é None
            raise ValidationError({'data_consulta': "A data da consulta não pode estar no passado."})
        if self.animal and self.data_consulta and \
           AgendamentoConsultas.objects.filter(animal=self.animal, data_consulta=self.data_consulta).exclude(pk=self.pk).exists():
            raise ValidationError({'data_consulta': "Já existe uma consulta agendada para este animal nesse horário."})

    class Meta:
        verbose_name = "Agendamento de Consulta"
        verbose_name_plural = "Agendamentos de Consultas"
        indexes = [models.Index(fields=['data_consulta'])]

    def __str__(self):
        if self.animal and self.tutor and self.data_consulta:
            data_local = localtime(self.data_consulta)
            return f"Consulta de {self.animal.nome} ({self.tutor.nome}) - {data_local.strftime('%d/%m/%Y %H:%M')}"
        return "Agendamento sem dados completos"


# Classes de gestão
class EstoqueMedicamento(models.Model):
    medicamento = models.CharField("Medicamento", max_length=255)
    lote = models.CharField("Lote", max_length=100, unique=True)
    data_validade = models.DateField("Data de Validade")
    quantidade = models.PositiveIntegerField("Quantidade em Estoque", default=0, editable=False)
    data_cadastro = models.DateField("Data de Entrada", default=timezone.now, editable=False)

    class Meta:
        verbose_name = 'Lote de Medicamento'
        verbose_name_plural = 'Estoque de Medicamentos'

    def __str__(self):
        validade = self.data_validade.strftime('%d/%m/%Y')
        return f"{self.medicamento} - Lote: {self.lote} (Val: {validade}) | {self.quantidade} un."

    def destaque_validade(self):
        """
        Retorna uma tag HTML com uma cor indicando o status da data de validade.
        Útil para visualização rápida no painel de administração.
        """
        if not self.data_validade:
            return format_html('<span style="color: gray;">Sem validade</span>')

        dias_para_vencer = (self.data_validade - timezone.now().date()).days

        if dias_para_vencer < 0:
            return format_html('<b style="color: red;">VENCIDO</b>')
        elif dias_para_vencer <= 30:
            return format_html('<b style="color: orange;">Vence em {} dias</b>', dias_para_vencer)
        else:
            return format_html('<span style="color: green;">OK</span>')

    destaque_validade.short_description = "Status da Validade"


class MovimentoEstoqueMedicamento(models.Model):
    ENTRADA = 'entrada'
    SAIDA = 'saida'
    TIPOS_MOVIMENTO = [
        (ENTRADA, 'Entrada'),
        (SAIDA, 'Saída'),
    ]

    medicamento = models.CharField("Medicamento", max_length=255)
    lote = models.CharField("Código do Lote", max_length=100)
    data_validade = models.DateField("Data de Validade")
    tipo = models.CharField("Tipo de Movimento", max_length=10, choices=TIPOS_MOVIMENTO)
    quantidade = models.PositiveIntegerField("Quantidade Movimentada")
    data = models.DateTimeField("Data do Movimento", auto_now_add=True)
    observacao = models.TextField("Observação", blank=True, null=True)

    class Meta:
        verbose_name = "Movimento de Estoque"
        verbose_name_plural = "Movimentos de Estoque"

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.quantidade} un. de {self.medicamento} (Lote: {self.lote})"

    def clean(self):
        super().clean()

        if self.quantidade is not None and self.quantidade <= 0:
            raise ValidationError({'quantidade': "A quantidade movimentada deve ser maior que zero."})

        if self.tipo == self.SAIDA:
            if self.medicamento and self.lote:
                try:
                    estoque = EstoqueMedicamento.objects.get(
                        medicamento=self.medicamento,
                        lote=self.lote
                    )
                except EstoqueMedicamento.DoesNotExist:
                    raise ValidationError("Não é possível dar saída de um lote que não existe no estoque.")

                if self.quantidade is not None and estoque.quantidade < self.quantidade:
                    raise ValidationError(
                        f"Saldo insuficiente para este lote. Disponível: {estoque.quantidade}, Saída: {self.quantidade}."
                    )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.tipo == self.ENTRADA:
                estoque, created = EstoqueMedicamento.objects.get_or_create(
                    medicamento=self.medicamento,
                    lote=self.lote,
                    defaults={'data_validade': self.data_validade, 'quantidade': self.quantidade}
                )
                if not created:
                    estoque.quantidade += self.quantidade
                    estoque.data_validade = self.data_validade
                    estoque.save()

            elif self.tipo == self.SAIDA:
                estoque = EstoqueMedicamento.objects.get(medicamento=self.medicamento, lote=self.lote)
                estoque.quantidade -= self.quantidade
                estoque.save()

            super().save(*args, **kwargs)


# Classes de procedimentos
class RegistroVacinacao(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Animal")
    medicamento_aplicado = models.ForeignKey(
        'EstoqueMedicamento',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Medicamento/Lote Aplicado"
    )
    data_aplicacao = models.DateField(verbose_name="Data de Aplicação", blank=True, null=True)
    data_revacinacao = models.DateField(verbose_name="Data Revacinação", blank=True, null=True)

    class Meta:
        verbose_name = "Registro de Vacinação"
        verbose_name_plural = "Registros de Vacinação"

    def clean(self):
        super().clean()
        hoje = timezone.now().date()
        limite = hoje - timedelta(days=15)

        if self.data_aplicacao and self.data_aplicacao < limite:
            raise ValidationError({'data_aplicacao': 'A data de aplicação não pode ser anterior a 15 dias.'})

        if self.data_revacinacao and self.data_revacinacao < limite:
            raise ValidationError({'data_revacinacao': 'A data de revacinação não pode ser anterior a 15 dias.'})

        if self.medicamento_aplicado:
            if self.medicamento_aplicado.quantidade < 1:
                raise ValidationError(
                    {'medicamento_aplicado': 'Não há estoque suficiente do medicamento/lote selecionado para esta vacinação.'}
                )

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        original_medicamento_aplicado = None

        if not is_new:
            try:
                original_registro = RegistroVacinacao.objects.get(pk=self.pk)
                original_medicamento_aplicado = original_registro.medicamento_aplicado
            except RegistroVacinacao.DoesNotExist:
                pass

        with transaction.atomic():
            super().save(*args, **kwargs)

            if self.medicamento_aplicado:
                if not is_new and original_medicamento_aplicado and original_medicamento_aplicado != self.medicamento_aplicado:
                    MovimentoEstoqueMedicamento.objects.create(
                        medicamento=original_medicamento_aplicado.medicamento,
                        lote=original_medicamento_aplicado.lote,
                        data_validade=original_medicamento_aplicado.data_validade,
                        tipo=MovimentoEstoqueMedicamento.ENTRADA,
                        quantidade=1,
                        observacao=f"Estorno de saída devido a alteração no registro de vacinação #{self.pk}"
                    )

                if is_new or (not is_new and original_medicamento_aplicado != self.medicamento_aplicado):
                    MovimentoEstoqueMedicamento.objects.create(
                        medicamento=self.medicamento_aplicado.medicamento,
                        lote=self.medicamento_aplicado.lote,
                        data_validade=self.medicamento_aplicado.data_validade,
                        tipo=MovimentoEstoqueMedicamento.SAIDA,
                        quantidade=1,
                        observacao=f"Aplicação em vacinação do animal {self.animal} (Registro #{self.pk})"
                    )

    def __str__(self):
        return f"Vacinação de {self.animal} em {self.data_aplicacao}"


class RegistroVermifugos(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Animal")
    medicamento_administrado = models.ForeignKey(
        'EstoqueMedicamento',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Vermífugo/Lote Administrado"
    )
    data_administracao = models.DateField(verbose_name="Data de Administração", blank=True, null=True)
    data_readministracao = models.DateField(verbose_name="Data Readministração", blank=True, null=True)

    class Meta:
        verbose_name = "Registro de Vermífugo"
        verbose_name_plural = "Registros de Vermífugos"

    def clean(self):
        super().clean()
        hoje = timezone.now().date()
        limite = hoje - timedelta(days=15)

        if self.data_administracao and self.data_administracao < limite:
            raise ValidationError({'data_administracao': 'A data de administração não pode ser anterior a 15 dias.'})

        if self.data_readministracao and self.data_readministracao < limite:
            raise ValidationError({'data_readministracao': 'A data de readministração não pode ser anterior a 15 dias.'})

        if self.medicamento_administrado:
            if self.medicamento_administrado.quantidade < 1:
                raise ValidationError(
                    {'medicamento_administrado': 'Não há estoque suficiente do vermífugo/lote selecionado.'}
                )

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        original_medicamento_administrado = None

        if not is_new:
            try:
                original_registro = RegistroVermifugos.objects.get(pk=self.pk)
                original_medicamento_administrado = original_registro.medicamento_administrado
            except RegistroVermifugos.DoesNotExist:
                pass

        with transaction.atomic():
            super().save(*args, **kwargs)

            if self.medicamento_administrado:
                if not is_new and original_medicamento_administrado and \
                   original_medicamento_administrado != self.medicamento_administrado:
                    MovimentoEstoqueMedicamento.objects.create(
                        medicamento=original_medicamento_administrado.medicamento,
                        lote=original_medicamento_administrado.lote,
                        data_validade=original_medicamento_administrado.data_validade,
                        tipo=MovimentoEstoqueMedicamento.ENTRADA,
                        quantidade=1,
                        observacao=f"Estorno de saída devido a alteração no registro de vermifugo #{self.pk}"
                    )

                if is_new or (not is_new and original_medicamento_administrado != self.medicamento_administrado):
                    MovimentoEstoqueMedicamento.objects.create(
                        medicamento=self.medicamento_administrado.medicamento,
                        lote=self.medicamento_administrado.lote,
                        data_validade=self.medicamento_administrado.data_validade,
                        tipo=MovimentoEstoqueMedicamento.SAIDA,
                        quantidade=1,
                        observacao=f"Administração de vermífugo em {self.animal} (Registro #{self.pk})"
                    )

    def __str__(self):
        return f"Vermífugo em {self.animal} em {self.data_administracao}"


class Exames(models.Model):
    # Campos de exemplo para Exames. Remova ou adapte conforme sua necessidade real.
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name="Animal", blank=True, null=True)
    tipo_exame = models.CharField(max_length=100, verbose_name="Tipo de Exame", blank=True, null=True)
    data_exame = models.DateField(verbose_name="Data do Exame", blank=True, null=True)
    resultado = models.TextField(verbose_name="Resultado", blank=True, null=True)

    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"

    def __str__(self):
        if self.animal and self.tipo_exame and self.data_exame:
            return f"Exame de {self.tipo_exame} em {self.animal.nome} ({self.data_exame.strftime('%d/%m/%Y')})"
        return "Exame (sem dados)"