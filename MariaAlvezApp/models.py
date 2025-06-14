from django.db import models

class Veterinario(models.Model):
    nome = models.CharField(max_length=100, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        verbose_name = "Veterinário"
        verbose_name_plural = "Veterinários"

    def __str__(self):
        return self.nome


class Tutor(models.Model):
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    nome = models.CharField(max_length=100, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    cep = models.CharField(max_length=9, null=True, blank=True)
    endereco = models.CharField(max_length=200, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cidade = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutores"

    def __str__(self):
        return self.nome


class Animal(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100, null=True, blank=True)
    especie = models.CharField(max_length=50, null=True, blank=True)
    idade = models.CharField(max_length=20, null=True, blank=True)
    sexo = models.CharField(max_length=10, null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    castrado = models.BooleanField(default=False)
    rfid = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"

    def __str__(self):
        return self.nome


class ConsultaClinica(models.Model):
    data_atendimento = models.DateField(null=True, blank=True)
    tipo_atendimento = models.CharField(max_length=100, null=True, blank=True)
    vet_responsavel = models.ForeignKey(Veterinario, on_delete=models.CASCADE, null=True, blank=True)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, null=True, blank=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, null=True, blank=True)
    diagnostico = models.TextField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    frequencia_cardiaca = models.IntegerField(null=True, blank=True)
    frequencia_respiratoria = models.IntegerField(null=True, blank=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    avaliacao_mucosa = models.CharField(max_length=100, null=True, blank=True)
    exame = models.ForeignKey('Exames', on_delete=models.SET_NULL, null=True, blank=True)
    tcp = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Consulta Clínica"
        verbose_name_plural = "Consultas Clínicas"

    def __str__(self):
        return f"{self.animal.nome if self.animal else 'Sem nome'} - {self.data_atendimento}"


class AgendamentoConsultas(models.Model):
    data_consulta = models.DateField(null=True, blank=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, null=True, blank=True)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Agendamento de Consulta"
        verbose_name_plural = "Agendamentos de Consultas"

    def __str__(self):
        return f"{self.animal.nome if self.animal else 'Sem animal'} - {self.data_consulta}"


class RegistroVacinacao(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, null=True, blank=True)
    medicamento = models.ForeignKey('Medicamentos', on_delete=models.CASCADE, null=True, blank=True)
    data_aplicacao = models.DateField(null=True, blank=True)
    data_revacinacao = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Registro de Vacinação"
        verbose_name_plural = "Registros de Vacinações"


class RegistroVermifugos(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, null=True, blank=True)
    medicamento = models.ForeignKey('Medicamentos', on_delete=models.CASCADE, null=True, blank=True)
    data_administracao = models.DateField(null=True, blank=True)
    data_readministracao = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Registro de Vermífugo"
        verbose_name_plural = "Registros de Vermífugos"


class Exames(models.Model):
    nome = models.CharField(max_length=100, null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    tipo_exame = models.CharField(max_length=50, null=True, blank=True)
    arquivo = models.FileField(upload_to='exames/', null=True, blank=True)

    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"

    def __str__(self):
        return self.nome


class Medicamentos(models.Model):
    nome = models.CharField(max_length=100, null=True, blank=True)
    quantidade = models.IntegerField(null=True, blank=True)
    data_da_entrada = models.DateField(auto_now_add=True, null=True, blank=True)
    validade = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"

    def __str__(self):
        return self.nome
