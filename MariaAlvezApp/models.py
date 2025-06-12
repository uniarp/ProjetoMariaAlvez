from django.db import models
from django.core.exceptions import ValidationError

# Classes principais
class Veterinario(models.Model):
    class Meta:
        verbose_name = "Veterinário"
        verbose_name_plural = "Veterinários"

class Tutor(models.Model):
    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutores"

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
    class Meta:
        verbose_name = "Agendamento de Consulta"
        verbose_name_plural = "Agendamentos de Consultas"

# Classes de procedimentos"
class RegistroVacinacao(models.Model):
    class Meta:
        verbose_name = "Registro de Vacinacão"
        verbose_name_plural = "Registros de Vacinações"

class RegistroVermifugos(models.Model):
    class Meta:
        verbose_name = "Registro de Vermífugo"
        verbose_name_plural = "Registros de Vermífugos"

class Exames(models.Model):
    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"

# Classes de gestão
class Medicamentos(models.Model):
    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"