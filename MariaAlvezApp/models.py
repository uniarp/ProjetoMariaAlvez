# models.py - VERSÃO ATUALIZADA

from django.core.exceptions import ValidationError
from django.utils.html import format_html
from datetime import timedelta, datetime, date
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
import re
from django.utils import timezone
from django.utils.timezone import localtime


# Classes principais (Sem alterações aqui)
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
        super().clean() 

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
        cpf = re.sub(r'\D', '', self.cpf)
        if len(cpf) == 11:
            self.cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        
        tel = re.sub(r'\D', '', self.telefone)
        if len(tel) == 11:
            self.telefone = f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
        elif len(tel) == 10:
            self.telefone = f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
        
        cep = re.sub(r'\D', '', self.cep)
        if len(cep) == 8:
            self.cep = f"{cep[:5]}-{cep[5:]}"

    def __str__(self):
        return f"{self.nome} ({self.cpf})"
    
    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutores" 
    
class Animal(models.Model):
    SEXO_CHOICES = [('M', 'Macho'), ('F', 'Fêmea')]
    nome = models.CharField(max_length=150, default="Nome", verbose_name="Nome")
    especie = models.CharField(max_length=100, default="Especie", verbose_name="Espécie")
    idade_anos = models.PositiveIntegerField(default=0, verbose_name="Anos")
    idade_meses = models.PositiveIntegerField(default=0, verbose_name="Meses")
    idade_dias = models.PositiveIntegerField(default=0, verbose_name="Dias")
    sexo = models.CharField(max_length=15, choices=SEXO_CHOICES, default="Sexo", verbose_name="Sexo")
    peso = models.DecimalField(default=0, max_digits=10, decimal_places=3, help_text="Peso em quilogramas", verbose_name="Peso (kg)")
    castrado = models.BooleanField(default=False, verbose_name="Castrado(a)")
    rfid = models.CharField(max_length=128, unique=True, default="0", verbose_name="RFID") 
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='animais_tutor', verbose_name="Tutor do Animal", blank=True, null=True, help_text="Selecione o tutor responsável por este animal.")

    def clean(self):
        super().clean() 
        if self.idade_anos == 0 and self.idade_meses == 0 and self.idade_dias == 0:
            raise ValidationError('O animal deve ter ao menos 1 dia de idade.')
        if self.peso <= 0:
            raise ValidationError({'peso': 'O peso deve ser maior que zero.'})
        self.nome = self.nome.strip().capitalize()
        self.especie = self.especie.strip().capitalize()

    def __str__(self):
        tutor_nome = self.tutor.nome if self.tutor else "Tutor não atribuído"
        return f"{self.nome} ({self.especie}) - {self.get_sexo_display()} | Tutor: {tutor_nome}"

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"

# Classes de gestão (Sem alterações aqui)
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
    ENTRADA = 'entrada'; SAIDA = 'saida'
    TIPOS_MOVIMENTO = [(ENTRADA, 'Entrada'),(SAIDA, 'Saída')]
    estoque_item = models.ForeignKey(EstoqueMedicamento, on_delete=models.RESTRICT, blank=True, null=True, verbose_name="Lote de Medicamento", help_text="Selecione o lote de medicamento ao qual o movimento se refere.")
    tipo = models.CharField("Tipo de Movimento", max_length=10, choices=TIPOS_MOVIMENTO)
    quantidade = models.PositiveIntegerField("Quantidade Movimentada")
    data = models.DateTimeField("Data do Movimento", auto_now_add=True)
    observacao = models.TextField("Observação", blank=True, null=True)

    class Meta:
        verbose_name = "Movimento de Estoque"
        verbose_name_plural = "Movimentos de Estoque"

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.quantidade} un. de {self.estoque_item.medicamento} (Lote: {self.estoque_item.lote})"

    def clean(self):
        super().clean()
        if self.quantidade <= 0:
            raise ValidationError({'quantidade': "A quantidade movimentada deve ser maior que zero."})
        if self.tipo == self.SAIDA:
            if self.quantidade > self.estoque_item.quantidade:
                raise ValidationError(f"Saldo insuficiente para este lote. Disponível: {self.estoque_item.quantidade}, Saída: {self.quantidade}.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs) 
            if self.tipo == self.ENTRADA: self.estoque_item.quantidade += self.quantidade
            elif self.tipo == self.SAIDA: self.estoque_item.quantidade -= self.quantidade
            self.estoque_item.save()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if self.tipo == self.ENTRADA: self.estoque_item.quantidade -= self.quantidade
            elif self.tipo == self.SAIDA: self.estoque_item.quantidade += self.quantidade
            self.estoque_item.save()
            super().delete(*args, **kwargs)

# --- ALTERAÇÃO AQUI ---
class ConsultaClinica(models.Model):
    data_atendimento = models.DateTimeField(default=timezone.now, help_text="Data e hora da consulta")
    tipo_atendimento = models.CharField(max_length=100, blank=True, null=True, help_text="Tipo de atendimento (ex: Rotina, Emergência)")
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, related_name='consultas_realizadas', verbose_name="Veterinário Responsável", blank=True, null=True, help_text="Selecione o veterinário responsável pela consulta")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='historico_consultas', verbose_name="Animal Atendido", blank=True, null=True, help_text="Selecione o animal atendido na consulta")
    medicamentos_aplicados = models.ManyToManyField(EstoqueMedicamento, through='MedicamentoConsulta', related_name='consultas_onde_aplicado', verbose_name="Medicamentos Aplicados na Consulta", blank=True)
    diagnostico = models.TextField(blank=True, null=True, help_text="Diagnóstico da consulta")
    observacoes = models.TextField(blank=True, null=True, help_text="Observações adicionais da consulta")
    frequencia_cardiaca = models.IntegerField(blank=True, null=True, help_text="Frequência cardíaca em batimentos por minuto (BPM)")
    frequencia_respiratoria = models.IntegerField(blank=True, null=True, help_text="Frequência respiratoria em respirações por minuto (RPM)")
    temperatura = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Temperatura corporal em graus Celsius (°C)")
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Peso do animal em quilogramas (Kg) ") 
    avaliacao_mucosa = models.CharField(max_length=100, blank=True, null=True, help_text="Avaliação da mucosa (ex: Rósea, Pálida, Ictérica)")
    # exames_realizados = models.TextField(blank=True, null=True, help_text="Nomes ou IDs dos exames realizados (separados por vírgula)") # <-- CAMPO REMOVIDO
    tempo_preenchimento_capilar = models.CharField(max_length=50, blank=True, null=True, help_text="Tempo de preenchimento capilar (ex: < 2 segundos, 3 segundos)")

    class Meta:
        verbose_name = "Consulta Clínica"
        verbose_name_plural = "Consultas Clínicas"
        ordering = ['-data_atendimento']

    def __str__(self):
        animal_info = self.animal.nome if self.animal else 'N/A'
        vet_info = self.veterinario.nome if self.veterinario else 'N/A'
        tutor_info = self.animal.tutor.nome if self.animal and self.animal.tutor else 'N/A' 
        return f"Consulta de {animal_info} (Tutor: {tutor_info}) por {vet_info} em {self.data_atendimento.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        super().clean() 
        if not self.diagnostico:
            raise ValidationError({'diagnostico': 'O campo Diagnóstico não pode ser vazio.'})
        hoje = timezone.localdate()
        data_limite = hoje - timedelta(days=15)
        if self.data_atendimento and self.data_atendimento.date() < data_limite:
            raise ValidationError({'data_atendimento': 'A data da consulta não pode ser mais antiga que 15 dias.'})

# Classes intermediárias e de agendamento (Sem alterações aqui)
class MedicamentoConsulta(models.Model):
    consulta = models.ForeignKey(ConsultaClinica, on_delete=models.CASCADE, verbose_name="Consulta Clínica")
    medicamento_estoque = models.ForeignKey(EstoqueMedicamento, on_delete=models.RESTRICT, verbose_name="Medicamento (Lote)")
    quantidade_aplicada = models.PositiveIntegerField(verbose_name="Quantidade Aplicada")

    class Meta:
        verbose_name = "Medicamento na Consulta"
        verbose_name_plural = "Medicamentos na Consulta"
        unique_together = ('consulta', 'medicamento_estoque')

    def __str__(self):
        return f"{self.quantidade_aplicada} de {self.medicamento_estoque.medicamento} (Lote: {self.medicamento_estoque.lote})"

    def clean(self):
        super().clean()
        if self.quantidade_aplicada <= 0: raise ValidationError({'quantidade_aplicada': "A quantidade aplicada deve ser maior que zero."})
        if self.medicamento_estoque.quantidade < self.quantidade_aplicada: raise ValidationError({'quantidade_aplicada': f"Estoque insuficiente. Disponível: {self.medicamento_estoque.quantidade}."})
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding 
        old_quantidade_aplicada = 0
        if not is_new:
            try:
                old_mc = MedicamentoConsulta.objects.get(pk=self.pk)
                old_quantidade_aplicada = old_mc.quantidade_aplicada
            except MedicamentoConsulta.DoesNotExist: pass 
        with transaction.atomic():
            super().save(*args, **kwargs)
            if is_new:
                MovimentoEstoqueMedicamento.objects.create(estoque_item=self.medicamento_estoque, tipo=MovimentoEstoqueMedicamento.SAIDA, quantidade=self.quantidade_aplicada, observacao=f"Saída em Consulta Clínica #{self.consulta.pk}.")
            elif self.quantidade_aplicada != old_quantidade_aplicada:
                delta = self.quantidade_aplicada - old_quantidade_aplicada
                tipo_mov = MovimentoEstoqueMedicamento.SAIDA if delta > 0 else MovimentoEstoqueMedicamento.ENTRADA
                obs = "Aumento" if delta > 0 else "Redução"
                MovimentoEstoqueMedicamento.objects.create(estoque_item=self.medicamento_estoque, tipo=tipo_mov, quantidade=abs(delta), observacao=f"Ajuste de saída ({obs}) em Consulta Clínica #{self.consulta.pk}.")

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            MovimentoEstoqueMedicamento.objects.create(estoque_item=self.medicamento_estoque, tipo=MovimentoEstoqueMedicamento.ENTRADA, quantidade=self.quantidade_aplicada, observacao=f"Estorno de saída devido à remoção de medicamento da Consulta Clínica #{self.consulta.pk}.")
            super().delete(*args, **kwargs)

class AgendamentoConsultas(models.Model):
    data_consulta = models.DateTimeField(verbose_name="Data da Consulta", default=timezone.now, blank=True, null=True)
    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='agendamentos', verbose_name="Tutor")
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE, related_name='agendamentos_consultas', verbose_name="Animal")
    
    def clean(self):
        super().clean()
        if self.data_consulta and self.data_consulta < timezone.now():
            raise ValidationError({'data_consulta': "A data da consulta não pode estar no passado."})
        if self.animal and self.data_consulta and AgendamentoConsultas.objects.filter(animal=self.animal, data_consulta=self.data_consulta).exclude(pk=self.pk).exists():
            raise ValidationError({'data_consulta': "Já existe uma consulta agendada para este animal nesse horário."})

    class Meta:
        verbose_name = "Agendamento de Consulta"; verbose_name_plural = "Agendamentos de Consultas"
        indexes = [models.Index(fields=['data_consulta'])]

    def __str__(self):
        if self.animal and self.tutor and self.data_consulta:
            return f"Consulta de {self.animal.nome} ({self.tutor.nome}) - {localtime(self.data_consulta).strftime('%d/%m/%Y %H:%M')}"
        return "Agendamento sem dados completos"

# Registros (Com os métodos delete já adicionados)
class RegistroVacinacao(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Animal")
    medicamento_aplicado = models.ForeignKey('EstoqueMedicamento', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Medicamento/Lote Aplicado")
    data_aplicacao = models.DateField(verbose_name="Data de Aplicação", blank=True, null=True)
    data_revacinacao = models.DateField(verbose_name="Data Revacinação", blank=True, null=True)
    
    class Meta: verbose_name = "Registro de Vacinação"; verbose_name_plural = "Registros de Vacinação"
    def clean(self):
        super().clean()
        hoje = timezone.now().date(); limite = hoje - timedelta(days=15)
        if self.data_aplicacao and self.data_aplicacao < limite: raise ValidationError({'data_aplicacao': 'A data de aplicação não pode ser anterior a 15 dias.'})
        if self.data_revacinacao and self.data_revacinacao < limite: raise ValidationError({'data_revacinacao': 'A data de revacinação não pode ser anterior a 15 dias.'})
    def save(self, *args, **kwargs):
        is_new = self._state.adding; original_medicamento_aplicado = None
        if not is_new:
            try: original_registro = RegistroVacinacao.objects.get(pk=self.pk); original_medicamento_aplicado = original_registro.medicamento_aplicado
            except RegistroVacinacao.DoesNotExist: pass
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.medicamento_aplicado:
                if is_new or (not is_new and original_medicamento_aplicado != self.medicamento_aplicado):
                    if not is_new and original_medicamento_aplicado:
                        MovimentoEstoqueMedicamento.objects.create(estoque_item=original_medicamento_aplicado, tipo=MovimentoEstoqueMedicamento.ENTRADA, quantidade=1, observacao=f"Estorno de saída (vacinação) devido a alteração do registro #{self.pk}.")
                    MovimentoEstoqueMedicamento.objects.create(estoque_item=self.medicamento_aplicado, tipo=MovimentoEstoqueMedicamento.SAIDA, quantidade=1, observacao=f"Aplicação em vacinação do animal {self.animal.nome if self.animal else 'N/A'} (Registro #{self.pk})")
            elif not is_new and original_medicamento_aplicado:
                MovimentoEstoqueMedicamento.objects.create(estoque_item=original_medicamento_aplicado, tipo=MovimentoEstoqueMedicamento.ENTRADA, quantidade=1, observacao=f"Estorno de saída (vacinação) devido à remoção do medicamento do registro #{self.pk}")
    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if self.medicamento_aplicado:
                MovimentoEstoqueMedicamento.objects.create(estoque_item=self.medicamento_aplicado, tipo=MovimentoEstoqueMedicamento.ENTRADA, quantidade=1, observacao=f"Estorno por exclusão do Registro de Vacinação #{self.pk} para o animal {self.animal.nome if self.animal else 'N/A'}.")
            super().delete(*args, **kwargs)
    def __str__(self):
        animal_name = self.animal.nome if self.animal else "Animal Não Informado"; data_app = self.data_aplicacao.strftime('%d/%m/%Y') if self.data_aplicacao else "Data Não Informada"
        return f"Vacinação de {animal_name} em {data_app}"

class RegistroVermifugos(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Animal")
    medicamento_administrado = models.ForeignKey('EstoqueMedicamento', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Vermífugo/Lote Administrado")
    data_administracao = models.DateField(verbose_name="Data de Administração", blank=True, null=True)
    data_readministracao = models.DateField(verbose_name="Data Readministração", blank=True, null=True)
    
    class Meta: verbose_name = "Registro de Vermífugo"; verbose_name_plural = "Registros de Vermífugos"
    def clean(self):
        super().clean(); hoje = timezone.now().date(); limite = hoje - timedelta(days=15)
        if self.data_administracao and self.data_administracao < limite: raise ValidationError({'data_administracao': 'A data de administração não pode ser anterior a 15 dias.'})
        if self.data_readministracao and self.data_readministracao < limite: raise ValidationError({'data_readministracao': 'A data de readministração não pode ser anterior a 15 dias.'})
    def save(self, *args, **kwargs):
        is_new = self._state.adding; original_medicamento_administrado = None
        if not is_new:
            try: original_registro = RegistroVermifugos.objects.get(pk=self.pk); original_medicamento_administrado = original_registro.medicamento_administrado
            except RegistroVermifugos.DoesNotExist: pass
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.medicamento_administrado:
                if is_new or (not is_new and original_medicamento_administrado != self.medicamento_administrado):
                    if not is_new and original_medicamento_administrado:
                        MovimentoEstoqueMedicamento.objects.create(estoque_item=original_medicamento_administrado, tipo=MovimentoEstoqueMedicamento.ENTRADA, quantidade=1, observacao=f"Estorno de saída (vermífugo) devido a alteração do registro #{self.pk}.")
                    MovimentoEstoqueMedicamento.objects.create(estoque_item=self.medicamento_administrado, tipo=MovimentoEstoqueMedicamento.SAIDA, quantidade=1, observacao=f"Administração de vermífugo em {self.animal.nome if self.animal else 'N/A'} (Registro #{self.pk})")
            elif not is_new and original_medicamento_administrado:
                MovimentoEstoqueMedicamento.objects.create(estoque_item=original_medicamento_administrado, tipo=MovimentoEstoqueMedicamento.ENTRADA, quantidade=1, observacao=f"Estorno de saída (vermífugo) devido à remoção do medicamento do registro #{self.pk}")
    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if self.medicamento_administrado:
                MovimentoEstoqueMedicamento.objects.create(estoque_item=self.medicamento_administrado, tipo=MovimentoEstoqueMedicamento.ENTRADA, quantidade=1, observacao=f"Estorno por exclusão do Registro de Vermífugo #{self.pk} para o animal {self.animal.nome if self.animal else 'N/A'}.")
            super().delete(*args, **kwargs)
    def __str__(self):
        animal_name = self.animal.nome if self.animal else "Animal Não Informado"; data_adm = self.data_administracao.strftime('%d/%m/%Y') if self.data_administracao else "Data Não Informada"
        return f"Vermífugo em {animal_name} em {data_adm}"

# --- ALTERAÇÃO AQUI ---
class Exames(models.Model):
    id_exame = models.BigAutoField(primary_key=True)
    
    # --- CAMPO NOVO ---
    consulta = models.ForeignKey(
        ConsultaClinica, 
        on_delete=models.CASCADE, 
        related_name='exames', 
        verbose_name="Consulta Associada",
        blank=True,
        null=True # Permite que exames existam sem uma consulta (opcional)
    )

    # --- CAMPO ALTERADO ---
    animal = models.ForeignKey(
        'Animal',
        on_delete=models.CASCADE,
        verbose_name="Animal",
        blank=True, # Agora pode ser opcional, se o exame estiver ligado a uma consulta
        null=True
    )

    nome = models.CharField(max_length=100, verbose_name="Nome do Exame")
    descricao = models.TextField(verbose_name="Descrição do Exame", blank=True, null=True) # Permitir em branco
    tipo = models.CharField(max_length=50, choices=[('Imagem', 'Imagem'), ('Laboratorial', 'Laboratorial'), ('Clínico', 'Clínico')], verbose_name="Tipo de Exame")
    anexo = models.FileField(upload_to='exames/', blank=True, null=True, verbose_name="Anexo do Exame")
    data_exame = models.DateField(verbose_name="Data de Realização do Exame", default=timezone.now)

    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"
        ordering = ['-data_exame', 'animal__nome']

    def __str__(self):
        animal_info = "N/A"
        if self.animal:
            animal_info = self.animal.nome
        elif self.consulta and self.consulta.animal:
            animal_info = self.consulta.animal.nome

        if self.tipo and self.data_exame:
            return f"Exame de {self.tipo} em {animal_info} ({self.data_exame.strftime('%d/%m/%Y')})"
        return "Exame (sem dados completos)"

# Relatórios (Sem alterações)
class RelatoriosGerais(models.Model):
    class Meta:
        managed = False
        verbose_name = "Relatório Geral"
        verbose_name_plural = "Relatórios Gerais"
        permissions = [("can_view_reports", "Can view general reports")]