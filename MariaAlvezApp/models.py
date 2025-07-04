from django.core.exceptions import ValidationError
from django.utils.html import format_html
from datetime import timedelta, datetime, date
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
import re
from django.utils import timezone
from django.utils.timezone import localtime
import requests
from django.core.validators import RegexValidator

class Veterinario(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome do Veterinário", help_text="Nome Completo do veterinario")
    crmv = models.CharField(max_length=50, unique=True, verbose_name="CRMV", help_text="CRMV do Veterinario Ex: (65485-SC)")
    telefone = models.CharField(max_length=15, verbose_name="Telefone", help_text="Telefone Veterinario")
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True, help_text="Email do veterinario")

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
    
def validar_estado(estado):
    ufs_validas = {
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT",
        "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO",
        "RR", "SC", "SP", "SE", "TO"
    }
    if estado.upper() not in ufs_validas:
        raise ValidationError(_('Estado inválido. Informe uma sigla de UF válida.'))
    
def validar_cep(cep):
    cep_numeros = re.sub(r'\D', '', cep)
    if not re.fullmatch(r'\d{8}', cep_numeros):
        raise ValidationError(_('CEP inválido. Deve conter 8 dígitos numéricos.'))
    
validador_cep = RegexValidator(
    regex=r'^\d{8}$',
    message='CEP inválido. Digite apenas 8 números, sem traços ou espaços.'
)
    
def buscar_endereco_por_cep(cep):
    cep = re.sub(r'\D', '', cep)
    if len(cep) != 8:
        raise ValidationError({'cep': _('CEP inválido. Deve conter 8 dígitos.')})

    url = f'https://viacep.com.br/ws/{cep}/json/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'erro' in data:
            raise ValidationError({'cep': _('CEP não encontrado.')})
        return data
    except requests.RequestException:
        raise ValidationError({'cep': _('Erro ao buscar o endereço. Verifique sua conexão.')})
    

class Tutor(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome", help_text="Nome Completo do tutor!")
    cpf = models.CharField(max_length=14, unique=True, validators=[validar_cpf], verbose_name="CPF", help_text="CPF do Tutor")
    telefone = models.CharField(max_length=15, validators=[validar_telefone], verbose_name="Telefone", help_text="Telefone do tutor com DDD. Ex:(49998086201)")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento", help_text="Data de Nascimento do Tutor. Ex: 19/09/2000")
    cep = models.CharField(max_length=9, verbose_name="CEP", help_text="Clique para buscar o CEP preenchido.")
    endereco = models.CharField(max_length=255, verbose_name="Endereço", help_text="Lembre de Preencher com o numero da casa. Ex:(Rua Exemplo, 999)")
    cidade = models.CharField(max_length=100, verbose_name="Cidade", help_text="Cidade do Tutor")
    estado = models.CharField(max_length=2, verbose_name="Estado", help_text="Estado do Tutor")

    def clean(self):
        if self.data_nascimento:
            self.validar_data_nascimento()
        self.aplicar_mascaras()
        self.validar_estado()
        self.buscar_e_preencher_endereco()
        super().clean()

    def validar_data_nascimento(self):
        hoje = date.today()
        if not self.data_nascimento:
            raise ValidationError({'data_nascimento': _('Data de nascimento inválida.')})

        limite_inferior = date(hoje.year - 120, hoje.month, hoje.day)
        idade_minima = hoje.replace(year=hoje.year - 16)

        if self.data_nascimento > hoje:
            raise ValidationError({'data_nascimento': _('A data de nascimento não pode estar no futuro.')})
        if self.data_nascimento < limite_inferior:
            raise ValidationError({'data_nascimento': _('A data de nascimento é muito antiga.')})
        if self.data_nascimento > idade_minima:
            raise ValidationError({'data_nascimento': _('O tutor deve ter no mínimo 16 anos.')})

    def aplicar_mascaras(self):
        self.cpf = re.sub(r'\D', '', self.cpf)
        if len(self.cpf) == 11:
            self.cpf = f"{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}"
        
        tel = re.sub(r'\D', '', self.telefone)
        if len(tel) == 11:
            self.telefone = f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
        elif len(tel) == 10:
            self.telefone = f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
        
        cep = re.sub(r'\D', '', self.cep)
        if len(cep) == 8:
            self.cep = f"{cep[:5]}-{cep[5:]}"

    def validar_estado(self):
        if not re.fullmatch(r'[A-Z]{2}', self.estado.upper()):
            raise ValidationError({'estado': _('Estado inválido. Use a sigla com 2 letras, ex: SC.')})
        self.estado = self.estado.upper()

    def buscar_e_preencher_endereco(self):
        dados = buscar_endereco_por_cep(self.cep)
        self.endereco = f"{dados.get('logradouro', '')}, {dados.get('bairro', '')}".strip(', ')
        self.cidade = dados.get('localidade', '')
        self.estado = dados.get('uf', '')

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutores"
    
class Animal(models.Model):
    SEXO_CHOICES = [('M', 'Macho'), ('F', 'Fêmea')]
    nome = models.CharField(max_length=150, default="Nome", help_text="Nome do Animal", verbose_name="Nome")
    especie = models.CharField(max_length=100, default="Especie", help_text="Espécie do Animal. Ex:(Cachorro, Gato, Passaro, etc)", verbose_name="Espécie")
    
    # --- CAMPOS DE IDADE (serão preenchidos automaticamente se a data de nascimento for dada) ---
    idade_anos = models.PositiveIntegerField(default=0, verbose_name="Anos", help_text="Quantos anos o animal tem (será preenchido automaticamente pela data de nascimento)")
    idade_meses = models.PositiveIntegerField(default=0, verbose_name="Meses", help_text="Quantos meses o animal tem (será preenchido automaticamente pela data de nascimento)")
    idade_dias = models.PositiveIntegerField(default=0, verbose_name="Dias", help_text="Quantos dias o animal tem (será preenchido automaticamente pela data de nascimento)")
    
    # --- NOVO CAMPO: DATA DE NASCIMENTO (este será o campo principal para idade) ---
    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento",
        blank=True,    # Permite deixar em branco no formulário
        null=True,     # Permite valor NULL no banco de dados
        help_text="Data de nascimento exata do animal. Se vazia, será calculada com base na idade fornecida."
    )

    sexo = models.CharField(max_length=15, choices=SEXO_CHOICES, default="Sexo", verbose_name="Sexo", help_text="Escolha o sexo do animal")
    peso = models.DecimalField(default=0, max_digits=10, decimal_places=3, help_text="Peso em quilogramas", verbose_name="Peso (kg)")
    castrado = models.BooleanField(default=False, verbose_name="Castrado(a)", help_text="Marque se o animal for castrado")
    rfid = models.CharField(max_length=128, unique=True, null=True, blank=True, default="", verbose_name="RFID", help_text="RFID segue padrão ISO 11784/11785 EXEMPLOS: 985 112003456789") 
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='animais_tutor', verbose_name="Tutor do Animal", help_text="Selecione o tutor responsável por este animal.")

    def clean(self):
        super().clean()
        
        hoje = date.today()

        # Verifica se pelo menos um dos campos de idade OU a data de nascimento foi preenchido
        idade_fornecida = (self.idade_anos is not None and self.idade_anos > 0) or \
                          (self.idade_meses is not None and self.idade_meses > 0) or \
                          (self.idade_dias is not None and self.idade_dias > 0)

        if not self.data_nascimento and not idade_fornecida:
            raise ValidationError('É necessário informar a idade (anos, meses, dias) ou a data de nascimento do animal.')

        # CENÁRIO PRINCIPAL: data_nascimento é a fonte da verdade
        if self.data_nascimento:
            if self.data_nascimento > hoje:
                raise ValidationError({'data_nascimento': 'A data de nascimento não pode estar no futuro.'})
            
            # Calcula a idade (anos, meses, dias) a partir da data de nascimento
            # de forma mais precisa, considerando meses e dias do ano.
            anos = hoje.year - self.data_nascimento.year
            meses = hoje.month - self.data_nascimento.month
            dias = hoje.day - self.data_nascimento.day

            if dias < 0:
                meses -= 1
                # Calcula os dias no mês anterior à data atual
                # Ex: se hoje é 05/julho e nasc é 10/junho, pega dias de junho (30) + 5 dias de julho - 10 dias de junho = 25 dias
                dias += (hoje - timedelta(days=hoje.day)).day # Dias do mês anterior

            if meses < 0:
                anos -= 1
                meses += 12
            
            self.idade_anos = anos
            self.idade_meses = meses
            self.idade_dias = dias

        # CENÁRIO SECUNDÁRIO: data_nascimento NÃO foi preenchida, mas a idade foi
        elif idade_fornecida:
            # Calcula a data de nascimento retroativamente a partir da idade fornecida
            # Isso é uma estimativa, pois anos/meses são aproximados.
            total_dias_estimado = (self.idade_anos * 365) + (self.idade_meses * 30) + self.idade_dias
            
            if total_dias_estimado < 1: # Garante que a idade não é zero
                raise ValidationError('O animal deve ter ao menos 1 dia de idade.')
            
            self.data_nascimento = hoje - timedelta(days=total_dias_estimado)
        
        # --- Suas validações existentes (manter) ---
        if self.peso is not None and self.peso <= 0: # Adicione 'is not None' para campos nulos
            raise ValidationError({'peso': 'O peso deve ser maior que zero.'})
        
        self.nome = self.nome.strip().capitalize()
        self.especie = self.especie.strip().capitalize()
        
        # Validação do RFID, considerando que pode ser null ou blank
        if self.rfid: # Só valida se o campo RFID não estiver vazio
            rfid_numeros = self.rfid.replace(" ", "")
            if not re.fullmatch(r"\d{15}", rfid_numeros):
                raise ValidationError({'rfid': 'O RFID deve conter exatamente 15 dígitos numéricos, seguindo o padrão ISO 11784/11785.'})
        # Se rfid for null ou "", a validação acima não será acionada, o que está de acordo com blank=True, null=True.

    def __str__(self):
        tutor_nome = self.tutor.nome if self.tutor else "Tutor não atribuído"
        return f"{self.nome} ({self.especie}) - {self.get_sexo_display()} | Tutor: {tutor_nome}"

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"
        # Adicione ordering se ainda não tiver, ex: ordering = ['nome']

class EstoqueMedicamento(models.Model):
    VACINA = 'vacina'
    VERMIFUGO = 'vermifugo'
    MEDICAMENTO = 'medicamento'

    TIPOS_MEDICAMENTO = [
        (VACINA, 'Vacina'),
        (VERMIFUGO, 'Vermífugo'),
        (MEDICAMENTO, 'Medicamento'),
    ]

    medicamento = models.CharField("Medicamento", max_length=255, unique=True)
    tipo_medicamento = models.CharField(
        "Tipo de Medicamento",
        max_length=20,
        choices=TIPOS_MEDICAMENTO,
        default=MEDICAMENTO,
        help_text="Classifique o tipo do medicamento"
    )
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

    def clean(self):
        super().clean()

        if self.data_validade and self.data_validade < timezone.now().date():
            raise ValidationError({
                'data_validade': "Não é possível cadastrar um medicamento com data de validade vencida."
            })
        if EstoqueMedicamento.objects.filter(
            medicamento=self.medicamento
        ).exclude(pk=self.pk).exists():
            raise ValidationError({
                'medicamento': "Já existe um medicamento cadastrado com esse nome."
            })

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
    ENTRADA = 'entrada'
    SAIDA = 'saida'
    TIPOS_MOVIMENTO = [(ENTRADA, 'Entrada'), (SAIDA, 'Saída')]
    estoque_item = models.ForeignKey(EstoqueMedicamento, on_delete=models.RESTRICT, blank=True, null=True, verbose_name="Lote de Medicamento", help_text="Selecione o medicamento ao qual o movimento se refere.")
    tipo = models.CharField("Tipo de Movimento", max_length=10, choices=TIPOS_MOVIMENTO, help_text="Escolha o tipo de movimento: ENTRADA ou SAIDA")
    quantidade = models.PositiveIntegerField("Quantidade Movimentada", help_text="Escolha a quantidade movimentada")
    data = models.DateTimeField("Data do Movimento", auto_now_add=True, help_text="Data de Hoje")
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
            if self.estoque_item and self.quantidade > self.estoque_item.quantidade:
                raise ValidationError(f"Saldo insuficiente para este lote. Disponível: {self.estoque_item.quantidade}, Saída: {self.quantidade}.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.tipo == self.ENTRADA:
                self.estoque_item.quantidade += self.quantidade
            elif self.tipo == self.SAIDA:
                self.estoque_item.quantidade -= self.quantidade
            self.estoque_item.save()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if self.tipo == self.ENTRADA:
                self.estoque_item.quantidade -= self.quantidade
            elif self.tipo == self.SAIDA:
                self.estoque_item.quantidade += self.quantidade
            self.estoque_item.save()
            super().delete(*args, **kwargs)

class AgendamentoConsultas(models.Model):
    data_consulta = models.DateTimeField(verbose_name="Data da Consulta", default=timezone.now, blank=True, null=True, help_text="Escolha a data da consulta!")
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE, related_name='agendamentos_consultas', verbose_name="Animal", help_text="Selecione o Animal para agendamento!")
    is_castracao = models.BooleanField(default=False, verbose_name="Agendamento para Castração?", help_text="Marque se este agendamento for para um procedimento de castração.") 

    def clean(self): 
        super().clean()
        pass 

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            if not hasattr(self, 'consulta_gerada') or self.consulta_gerada is None:
                ConsultaClinica.objects.create(
                    animal=self.animal,
                    data_atendimento=self.data_consulta,
                    agendamento_origem=self
                )

    def delete(self, *args, **kwargs):
        if hasattr(self, 'consulta_gerada') and self.consulta_gerada is not None:
            self.consulta_gerada.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Agendamento de Consulta"
        verbose_name_plural = "Agendamentos de Consultas"
        indexes = [models.Index(fields=['data_consulta'])]

    def __str__(self):
        tutor_nome = self.animal.tutor.nome if self.animal and self.animal.tutor else 'N/A'
        tipo_agendamento = "Castração" if self.is_castracao else "Consulta"
        if self.animal and self.data_consulta:
            return f"{tipo_agendamento} para {self.animal.nome} (Tutor: {tutor_nome}) - {localtime(self.data_consulta).strftime('%d/%m/%Y %H:%M')}"
        return "Agendamento sem dados completos"
    

class ConsultaClinica(models.Model):
    data_atendimento = models.DateTimeField(default=timezone.now, help_text="Data e hora da consulta")
    
    # Definir as opções para o tipo de atendimento
    TIPO_ATENDIMENTO_CHOICES = [
        ('CONSULTA_ROTINA', 'Consulta de Rotina'),
        ('EMERGENCIA', 'Emergência'),
        ('OUTRO', 'Outro'),
    ]
    
    # --- CAMPO tipo_atendimento: ADICIONE 'choices' e 'verbose_name' e 'help_text' ---
    tipo_atendimento = models.CharField(
        max_length=50, # Defina um max_length que comporte a chave mais longa ('CONSULTA_ROTINA')
        choices=TIPO_ATENDIMENTO_CHOICES,
        default='CONSULTA_ROTINA', # Defina um valor padrão, se desejar
        verbose_name="Tipo de Atendimento",
        help_text="Selecione o tipo de atendimento realizado."
    )

    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, related_name='consultas_realizadas', verbose_name="Veterinário Responsável", blank=True, null=True, help_text="Selecione o veterinário responsável pela consulta")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='historico_consultas', verbose_name="Animal Atendido", blank=True, null=True, help_text="Selecione o animal atendido na consulta")
    medicamentos_aplicados = models.ManyToManyField(EstoqueMedicamento, through='MedicamentoConsulta', related_name='consultas_onde_aplicado', verbose_name="Medicamentos Aplicados na Consulta", blank=True)
    diagnostico = models.TextField(blank=True, null=True, help_text="Diagnóstico da consulta", verbose_name="Diagnóstico")
    observacoes = models.TextField(blank=True, null=True, help_text="Observações adicionais da consulta", verbose_name="Observações")
    frequencia_cardiaca = models.IntegerField(blank=True, null=True, help_text="Frequência cardíaca em batimentos por minuto (BPM)")
    frequencia_respiratoria = models.IntegerField(blank=True, null=True, help_text="Frequência respiratoria em respirações por minuto (RPM)")
    temperatura = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Temperatura corporal em graus Celsius (°C)")
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Peso do animal em quilogramas (Kg) ") 
    avaliacao_mucosa = models.CharField(max_length=100, blank=True, null=True, help_text="Avaliação da mucosa (ex: Rósea, Pálida, Ictérica)")
    tempo_preenchimento_capilar = models.CharField(max_length=50, blank=True, null=True, help_text="Tempo de preenchimento capilar (ex: < 2 segundos, 3 segundos)")
    agendamento_origem = models.OneToOneField(
        'AgendamentoConsultas',
        on_delete=models.SET_NULL,
        related_name='consulta_gerada',
        verbose_name="Agendamento de Origem",
        blank=True,
        null=True,
        help_text="Agendamento que originou esta consulta (se houver)."
    )

    class Meta:
        verbose_name = "Consulta Clínica"
        verbose_name_plural = "Consultas Clínicas"
        ordering = ['-data_atendimento']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.animal and self.peso is not None:
            try:
                animal_para_atualizar = Animal.objects.get(pk=self.animal.pk)
            except Animal.DoesNotExist:
                return 

            if animal_para_atualizar.peso != self.peso:
                animal_para_atualizar.peso = self.peso
                animal_para_atualizar.save(update_fields=['peso'])

    def __str__(self):
        animal_info = self.animal.nome if self.animal else 'N/A'
        vet_info = self.veterinario.nome if self.veterinario else 'N/A'
        tutor_info = self.animal.tutor.nome if self.animal and self.animal.tutor else 'N/A' 
        
        # Para exibir o tipo de atendimento de forma legível
        tipo_display = self.get_tipo_atendimento_display()
        
        return f"Consulta de {animal_info} (Tutor: {tutor_info}) por {vet_info} em {self.data_atendimento.strftime('%d/%m/%Y %H:%M')} ({tipo_display})"

    def clean(self):
        super().clean() 
        hoje = timezone.localdate()
        data_limite = hoje - timedelta(days=15)
        if self.data_atendimento and self.data_atendimento.date() < data_limite:
            raise ValidationError({'data_atendimento': 'A data da consulta não pode ser mais antiga que 15 dias.'})
        if self.peso is None or self.peso <= 0:
            raise ValidationError({'peso': 'O peso do animal na consulta deve ser maior que zero.'})

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
        if self.quantidade_aplicada <= 0:
            raise ValidationError({'quantidade_aplicada': "A quantidade aplicada deve ser maior que zero."})
        if self.medicamento_estoque and self.medicamento_estoque.quantidade < self.quantidade_aplicada:
            raise ValidationError({'quantidade_aplicada': f"Estoque insuficiente. Disponível: {self.medicamento_estoque.quantidade}."})
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding 
        old_quantidade_aplicada = 0
        if not is_new:
            try:
                old_mc = MedicamentoConsulta.objects.get(pk=self.pk)
                old_quantidade_aplicada = old_mc.quantidade_aplicada
            except MedicamentoConsulta.DoesNotExist:
                pass 
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.medicamento_estoque:
                if is_new:
                    MovimentoEstoqueMedicamento.objects.create(estoque_item=self.medicamento_estoque, tipo=MovimentoEstoqueMedicamento.SAIDA, quantidade=self.quantidade_aplicada, observacao=f"Saída em Consulta Clínica #{self.consulta.pk}.")
                elif self.quantidade_aplicada != old_quantidade_aplicada:
                    delta = self.quantidade_aplicada - old_quantidade_aplicada
                    tipo_mov = MovimentoEstoqueMedicamento.SAIDA if delta > 0 else MovimentoEstoqueMedicamento.ENTRADA
                    obs = "Aumento" if delta > 0 else "Redução"
                    MovimentoEstoqueMedicamento.objects.create(estoque_item=self.medicamento_estoque, tipo=tipo_mov, quantidade=abs(delta), observacao=f"Ajuste de saída ({obs}) em Consulta Clínica #{self.consulta.pk}.")

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if self.medicamento_estoque:
                MovimentoEstoqueMedicamento.objects.create(estoque_item=self.medicamento_estoque, tipo=MovimentoEstoqueMedicamento.ENTRADA, quantidade=self.quantidade_aplicada, observacao=f"Estorno de saída devido à remoção de medicamento da Consulta Clínica #{self.consulta.pk}.")
            super().delete(*args, **kwargs)

class RegistroVacinacao(models.Model):
    animal = models.ForeignKey(
        Animal, 
        on_delete=models.CASCADE, 
        verbose_name="Animal",
        help_text="Selecione o animal vacinado." # Adicionei help_text para clareza
    )
    medicamento_aplicado = models.ForeignKey(
        'EstoqueMedicamento',
        on_delete=models.SET_NULL, # SET_NULL é mantido, mas o campo se torna obrigatório a nível de formulário/modelo
        blank=False, null=True,
        verbose_name="Vacina/Lote Aplicado",
        limit_choices_to={'tipo_medicamento': EstoqueMedicamento.VACINA},
        help_text="Selecione a vacina (lote) aplicada. Apenas vacinas serão listadas." # Adicionei help_text
    )
    data_aplicacao = models.DateField(
        verbose_name="Data de Aplicação", 
        blank=False, 
        null=False,  
        help_text="Informe a data em que a vacina foi aplicada." # Adicionei help_text
    )
    data_revacinacao = models.DateField(
        verbose_name="Data Revacinação", 
        blank=False, 
        null=False, 
        help_text="Informe a data da próxima revacinação." # Adicionei help_text
    )
    
    class Meta:
        verbose_name = "Registro de Vacinação"
        verbose_name_plural = "Registros de Vacinação"

    
    def clean(self):
        super().clean()
        hoje = timezone.now().date()
        limite_passado = hoje - timedelta(days=15) # Validação para não ser muito antigo

        # Validação para data_aplicacao
        if self.data_aplicacao:
            if self.data_aplicacao > hoje:
                raise ValidationError({'data_aplicacao': 'A data de aplicação não pode estar no futuro.'})
            if self.data_aplicacao < limite_passado:
                raise ValidationError({'data_aplicacao': 'A data de aplicação não pode ser anterior a 15 dias atrás.'})
        else:
            # Se data_aplicacao é None, levanta erro se o campo for obrigatório
            raise ValidationError({'data_aplicacao': 'Este campo é obrigatório.'})

        # Validação para data_revacinacao
        if self.data_revacinacao:
            if self.data_revacinacao < hoje:
                raise ValidationError({'data_revacinacao': 'A data de revacinação não pode estar no passado.'})
            
            # --- NOVA VALIDAÇÃO LÓGICA: data_revacinacao DEVE SER DEPOIS DE data_aplicacao ---
            if self.data_aplicacao and self.data_revacinacao < self.data_aplicacao:
                raise ValidationError({'data_revacinacao': 'A data de revacinação deve ser posterior à data de aplicação.'})
        else:
            # Se data_revacinacao é None, levanta erro se o campo for obrigatório
            raise ValidationError({'data_revacinacao': 'Este campo é obrigatório.'})
        if not self.animal: # Validação explícita para ForeignKey
             raise ValidationError({'animal': 'O animal vacinado é obrigatório.'})
        if not self.medicamento_aplicado: # Validação explícita para ForeignKey
             raise ValidationError({'medicamento_aplicado': 'O medicamento aplicado é obrigatório.'})
    
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
        animal_name = self.animal.nome if self.animal else "Animal Não Informado"
        data_app = self.data_aplicacao.strftime('%d/%m/%Y') if self.data_aplicacao else "Data Não Informada"
        return f"Vacinação de {animal_name} em {data_app}"

class RegistroVermifugos(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, blank=False, null=True, verbose_name="Animal")
    medicamento_administrado = models.ForeignKey(
        'EstoqueMedicamento',
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name="Vermífugo/Lote Administrado",
        limit_choices_to={'tipo_medicamento': EstoqueMedicamento.VERMIFUGO}
    )
    data_administracao = models.DateField(verbose_name="Data de Administração", blank=False, null=True)
    data_readministracao = models.DateField(verbose_name="Data Readministração", blank=False, null=True)
    
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
        animal_name = self.animal.nome if self.animal else "Animal Não Informado"
        data_adm = self.data_administracao.strftime('%d/%m/%Y') if self.data_administracao else "Data Não Informada"
        return f"Vermífugo em {animal_name} em {data_adm}"

class Exames(models.Model):
    id_exame = models.BigAutoField(primary_key=True)
    
    consulta = models.ForeignKey(
        ConsultaClinica, 
        on_delete=models.CASCADE, 
        related_name='exames', 
        verbose_name="Consulta Associada",
        blank=True,
        null=True
    )

    animal = models.ForeignKey(
        'Animal',
        on_delete=models.CASCADE,
        verbose_name="Animal",
        blank=True,
        null=True
    )

    nome = models.CharField(max_length=100, verbose_name="Nome do Exame", blank=True, null=True)
    descricao = models.TextField(verbose_name="Descrição do Exame", blank=True, null=True)
    tipo = models.CharField(max_length=50, choices=[('Imagem', 'Imagem'), ('Laboratorial', 'Laboratorial'), ('Clínico', 'Clínico')], verbose_name="Tipo de Exame", blank=True, null=True)
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

class RelatoriosGerais(models.Model):
    class Meta:
        managed = False
        verbose_name = "Relatório Geral"
        verbose_name_plural = "Relatórios Gerais"
        permissions = [("can_view_reports", "Can view general reports")]