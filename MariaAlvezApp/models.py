from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _ # Do main
from datetime import datetime, date # Do main
import re # Do main
from django.utils import timezone # Do gabrielDalpiaz
from django.utils.timezone import localtime # Do gabrielDalpiaz


# Classes principais
class Veterinario(models.Model):
    class Meta:
        verbose_name = "Veterinário"
        verbose_name_plural = "Veterinários"

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
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True, validators=[validar_cpf])
    telefone = models.CharField(max_length=15, validators=[validar_telefone])
    data_nascimento = models.DateField()
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    cep = models.CharField(max_length=9)

    def clean(self):
        self.validar_data_nascimento()
        self.aplicar_mascaras()

    def validar_data_nascimento(self):
        hoje = date.today()
        limite_inferior = date(hoje.year - 120, hoje.month, hoje.day)

        if self.data_nascimento > hoje:
            raise ValidationError({'data_nascimento': _('A data de nascimento não pode estar no futuro.')})
        if self.data_nascimento < limite_inferior:
            raise ValidationError({'data_nascimento': _('A data de nascimento é muito antiga. Deve estar nos últimos 120 anos.')})

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

    PESO_UNIDADE_CHOICES = [
        ('kg', 'Quilos'),
        ('g', 'Gramas'),
    ]

    nome = models.CharField(max_length=150, default="Nome")
    especie = models.CharField(max_length=100, default="Especie")

    idade_anos = models.PositiveIntegerField(default=0)
    idade_meses = models.PositiveIntegerField(default=0)
    idade_dias = models.PositiveIntegerField(default=0)

    sexo = models.CharField(max_length=15, choices=SEXO_CHOICES, default="Sexo")

    peso = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=3, # Se você quer 3 casas decimais, mantenha assim
        help_text="Peso em quilogramas" # Adiciona uma dica para o usuário
    )

    def _str_(self):
        return self.nome

    castrado = models.BooleanField(default=False)
    rfid = models.CharField(max_length=128, unique=True,default=0)

    def clean(self):
        # Valida idade
        if self.idade_anos == 0 and self.idade_meses == 0 and self.idade_dias == 0:
            raise ValidationError('O animal deve ter ao menos 1 dia de idade.')

        # Valida peso
        if self.peso <= 0:
            raise ValidationError({'peso': 'O peso deve ser maior que zero.'})

        self.nome = self.nome.strip().capitalize()
        self.especie = self.especie.strip().capitalize()

    def __str__(self):
        return f"{self.nome} ({self.especie}) - {self.get_sexo_display()}"

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"

class ConsultaClinica(models.Model):
        class Meta:
            verbose_name = "Consulta Clínica"
            verbose_name_plural = "Consultas Clínicas"

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
        if self.data_consulta < timezone.now():
            raise ValidationError({'data_consulta': "A data da consulta não pode estar no passado."})
        if AgendamentoConsultas.objects.filter(animal=self.animal, data_consulta=self.data_consulta).exclude(pk=self.pk).exists():
            raise ValidationError({'data_consulta': "Já existe uma consulta agendada para este animal nesse horário."})

    class Meta:
        verbose_name = "Agendamento de Consulta"
        verbose_name_plural = "Agendamentos de Consultas"
        indexes = [models.Index(fields=['data_consulta'])]

    def __str__(self):
        if self.animal and self.tutor and self.data_consulta:
            data_local = localtime(self.data_consulta)
            return f"- {data_local.strftime('%d/%m/%Y %H:%M')}"
        return "Consulta sem dados completos"

    class Meta:
        verbose_name = "Agendamento de Consulta"
        verbose_name_plural = "Agendamentos de Consultas"

# Classes de procedimentos"
class RegistroVacinacao(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, blank=True, null=True)
    medicamento = models.ForeignKey('Medicamentos', on_delete=models.CASCADE,  blank=True, null=True)
    data_aplicacao = models.DateField( blank=True, null=True)
    data_revacinacao = models.DateField(verbose_name="Data Revacinação", blank=True, null=True, )

    class Meta:
        verbose_name = "Registro de Vacinação"
        verbose_name_plural = "Registros de Vacinação"

    def clean(self):
        hoje = timezone.now().date()
        limite = hoje - timedelta(days=15)

        if self.data_aplicacao < limite:
            raise ValidationError({'data_aplicacao': 'A data de aplicação não pode ser anterior a 15 dias.'})

        if self.data_revacinacao and self.data_revacinacao < limite:
            raise ValidationError({'data_revacinacao': 'A data de revacinação não pode ser anterior a 15 dias.'})

    def __str__(self):
        return f" {self.data_aplicacao}"

class RegistroVermifugos(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, blank=True, null=True)
    medicamento = models.ForeignKey('Medicamentos', on_delete=models.CASCADE,  blank=True, null=True)
    data_administracao = models.DateField( blank=True, null=True)
    data_readministracao = models.DateField(verbose_name="Data Readministração", blank=True, null=True, )

    class Meta:
        verbose_name = "Registro de Vermífugo"
        verbose_name_plural = "Registros de Vermífugos"

    def clean(self):
        hoje = timezone.now().date()
        limite = hoje - timedelta(days=15)

        if self.data_administracao < limite:
            raise ValidationError({'data_administracao': 'A data de administração não pode ser anterior a 15 dias.'})

        if self.data_readministracao and self.data_readministracao < limite:
            raise ValidationError({'data_readministracao': 'A data de readministração não pode ser anterior a 15 dias.'})

    def __str__(self):
        return f" {self.data_administracao}"

class Exames(models.Model):
    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"

# Classes de gestão
class Medicamentos(models.Model):
    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"