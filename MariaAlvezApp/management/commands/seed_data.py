from django.core.management.base import BaseCommand
from django.utils import timezone
from MariaAlvezApp.models import (
    Veterinario, Tutor, Animal, EstoqueMedicamento, MovimentoEstoqueMedicamento,
    AgendamentoConsultas, ConsultaClinica, MedicamentoConsulta,
    RegistroVacinacao, RegistroVermifugos, Exames,
)
from Terceiros.models import EmpresaTerceirizada, RegistroServico

from faker import Faker
from decimal import Decimal
import random
from datetime import timedelta, date, datetime
from django.core.exceptions import ValidationError


CACADOR_ENDERECOS_STATICOS = [
    {
        'cep': '89500000',
        'logradouro': 'Rua Dr. Ulysses Guimarães',
        'bairro': 'Centro',
        'localidade': 'Caçador',
        'uf': 'SC'
    },
    {
        'cep': '89500000',
        'logradouro': 'Rua Getúlio Vargas',
        'bairro': 'Centro',
        'localidade': 'Caçador',
        'uf': 'SC'
    },
    {
        'cep': '89500000',
        'logradouro': 'Rua XV de Novembro',
        'bairro': 'Centro',
        'localidade': 'Caçador',
        'uf': 'SC'
    },
    {
        'cep': '89505000',
        'logradouro': 'Rua Adelmir Pressanto',
        'bairro': 'Alto Bonito',
        'localidade': 'Caçador',
        'uf': 'SC'
    },
    {
        'cep': '89505000',
        'logradouro': 'Rua Benjamin Constant',
        'bairro': 'Alto Bonito',
        'localidade': 'Caçador',
        'uf': 'SC'
    },
    {
        'cep': '89507000',
        'logradouro': 'Rua Nereu Ramos',
        'bairro': 'Berger',
        'localidade': 'Caçador',
        'uf': 'SC'
    },
    {
        'cep': '89507000',
        'logradouro': 'Rua Santa Catarina',
        'bairro': 'Berger',
        'localidade': 'Caçador',
        'uf': 'SC'
    },
    {
        'cep': '89506538',
        'logradouro': 'Rua José Boiteux',
        'bairro': 'Martello',
        'localidade': 'Caçador',
        'uf': 'SC'
    },
    {
        'cep': '89510000',
        'logradouro': 'Rua Rio do Peixe',
        'bairro': 'Bom Retiro',
        'localidade': 'Caçador',
        'uf': 'SC'
    },
    {
        'cep': '89500000',
        'logradouro': 'Rua Conselheiro Mafra',
        'bairro': 'Centro',
        'localidade': 'Caçador',
        'uf': 'SC'
    },
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo para Veterinario, Tutor, Animal e EstoqueMedicamento.'

    def handle(self, *args, **kwargs):
        fake = Faker('pt_BR')

        self.stdout.write(self.style.SUCCESS('Iniciando população de dados...'))

        # Descomente as linhas abaixo APENAS se você quiser limpar completamente
        # o banco de dados antes de popular, para garantir um estado limpo.
        # É crucial deletar na ordem inversa de dependência para evitar IntegrityError de chaves estrangeiras.
        # self.stdout.write('Deletando dados existentes (OPCIONAL - DESCOMENTE COM CUIDADO)...')
        # RegistroServico.objects.all().delete()
        # MedicamentoConsulta.objects.all().delete()
        # ConsultaClinica.objects.all().delete()
        # AgendamentoConsultas.objects.all().delete()
        # RegistroVacinacao.objects.all().delete()
        # RegistroVermifugos.objects.all().delete()
        # Exames.objects.all().delete()
        # MovimentoEstoqueMedicamento.objects.all().delete()
        # EstoqueMedicamento.objects.all().delete()
        # Animal.objects.all().delete()
        # Tutor.objects.all().delete()
        # Veterinario.objects.all().delete()
        # EmpresaTerceirizada.objects.all().delete()


        self.stdout.write('Populando Veterinarios...')
        veterinarios = []
        for _ in range(3):
            vet = Veterinario(
                nome=fake.name(),
                crmv=f'CRMV/{fake.state_abbr()} {random.randint(1000, 9999)}',
                telefone=fake.msisdn()[:11],
                email=fake.unique.email(),
            )
            try:
                vet.full_clean()
                vet.save()
                veterinarios.append(vet)
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f'Erro de validação ao criar Veterinario: {e.message_dict if hasattr(e, "message_dict") else e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar Veterinario: {e}'))
        self.stdout.write(self.style.SUCCESS(f'{len(veterinarios)} Veterinarios criados.'))

        self.stdout.write('Populando Tutores...')
        tutores = []
        MIN_TUTORS = 10
        attempts = 0
        while len(tutores) < MIN_TUTORS and attempts < (MIN_TUTORS * 5):
            attempts += 1
            if not CACADOR_ENDERECOS_STATICOS:
                self.stdout.write(self.style.ERROR("ERRO: A lista CACADOR_ENDERECOS_STATICOS está vazia. Não é possível criar Tutores."))
                break 

            cpf_num = fake.ssn()
            cpf_formatted = ''.join(filter(str.isdigit, cpf_num))[:11]

            telefone_num = fake.msisdn()
            telefone_formatted = ''.join(filter(str.isdigit, telefone_num))[:11]
            
            hoje = date.today()
            data_nascimento_tutor = fake.date_between(
                start_date=hoje - timedelta(days=120*365), 
                end_date=hoje - timedelta(days=16*365) 
            )

            endereco_escolhido = random.choice(CACADOR_ENDERECOS_STATICOS)
            
            tutor = Tutor(
                nome=fake.name(),
                cpf=cpf_formatted,
                telefone=telefone_formatted,
                data_nascimento=data_nascimento_tutor,
                cep=endereco_escolhido['cep'],
                endereco=f"{endereco_escolhido['logradouro']}, {random.randint(1, 1000)}",
                cidade=endereco_escolhido['localidade'],
                estado=endereco_escolhido['uf'],
            )
            tutor._skip_cep_lookup = True 

            try:
                tutor.full_clean() 
                tutor.save()
                tutores.append(tutor)
            except ValidationError as e:
                pass
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar Tutor: {e}. Abortando criação de tutores.'))
                break 
        self.stdout.write(self.style.SUCCESS(f'{len(tutores)} Tutores criados.'))

        self.stdout.write('Populando Animais...')
        animais = []
        if not tutores:
            self.stdout.write(self.style.WARNING("Não há tutores criados. Pulando a criação de animais."))
        else:
            especies = ['Cachorro', 'Gato', 'Pássaro', 'Roedor', 'Réptil', 'Outros']
            racas_map = { 
                'Cachorro': ['Labrador', 'Poodle', 'Vira-lata', 'Pastor Alemão', 'Golden Retriever', 'Bulldog'],
                'Gato': ['Persa', 'Siamês', 'Vira-lata', 'Maine Coon', 'Ragdoll', 'Sphynx'],
                'Pássaro': ['Calopsita', 'Periquito', 'Canário', 'Agapornis'],
                'Roedor': ['Hamster', 'Porquinho da Índia', 'Gerbil'],
                'Réptil': ['Tartaruga', 'Iguana', 'Cobra'],
                'Outros': ['Não Definida']
            }
            sexo_choices = ['M', 'F'] 

            for tutor in tutores:
                num_animais = random.randint(1, 3)
                for _ in range(num_animais):
                    especie_animal = random.choice(especies)
                    raca_animal_para_obs = random.choice(racas_map.get(especie_animal, ['Raça Indefinida']))
                    data_nascimento_animal = fake.date_between(start_date='-10y', end_date='-6m')
                    
                    rfid_generated = ''.join(random.choices('0123456789', k=15))
                    
                    animal = Animal(
                        nome=fake.first_name_male() if random.random() < 0.5 else fake.first_name_female(),
                        tutor=tutor,
                        especie=especie_animal,
                        sexo=random.choice(sexo_choices),
                        data_nascimento=data_nascimento_animal,
                        peso=Decimal(str(round(random.uniform(0.5, 50.0), 2))),
                        castrado=fake.boolean(chance_of_getting_true=50),
                        rfid=rfid_generated if random.random() < 0.7 else None,
                    )
                    animal.observacoes = fake.text(max_nb_chars=200) if random.random() > 0.3 else ''
                    animal.observacoes += f" Raça: {raca_animal_para_obs}." if animal.observacoes else f"Raça: {raca_animal_para_obs}."

                    try:
                        animal.full_clean()
                        animal.save()
                        animais.append(animal)
                    except ValidationError as e:
                        self.stdout.write(self.style.ERROR(f'Erro de validação ao criar Animal: {e.message_dict if hasattr(e, "message_dict") else e}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar Animal: {e}'))
            self.stdout.write(self.style.SUCCESS(f'{len(animais)} Animais criados.'))

        self.stdout.write('Populando EstoqueMedicamento...')
        medicamentos = []
        tipos_medicamento_choices = [EstoqueMedicamento.VACINA, EstoqueMedicamento.VERMIFUGO, EstoqueMedicamento.MEDICAMENTO]

        garantee_vacinas = 5
        garantee_vermifugos = 5
        total_medicamentos_gerar = 25 
        
        for i in range(garantee_vacinas):
            nome_vacina = fake.unique.word().capitalize() + ' Vacina ' + str(i+1)
            vacina = EstoqueMedicamento(
                medicamento=nome_vacina,
                tipo_medicamento=EstoqueMedicamento.VACINA,
                lote=fake.unique.uuid4()[:8].upper(),
                data_validade=fake.date_between(start_date='today', end_date='+3y'),
                quantidade=random.randint(10, 50),
            )
            try:
                vacina.full_clean()
                vacina.save()
                medicamentos.append(vacina)
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f'Erro de validação ao criar Vacina garantida: {e.message_dict if hasattr(e, "message_dict") else e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar Vacina garantida: {e}'))

        for i in range(garantee_vermifugos):
            nome_vermifugo = fake.unique.word().capitalize() + ' Vermífugo ' + str(i+1)
            vermifugo = EstoqueMedicamento(
                medicamento=nome_vermifugo,
                tipo_medicamento=EstoqueMedicamento.VERMIFUGO,
                lote=fake.unique.uuid4()[:8].upper(),
                data_validade=fake.date_between(start_date='today', end_date='+3y'),
                quantidade=random.randint(10, 50),
            )
            try:
                vermifugo.full_clean()
                vermifugo.save()
                medicamentos.append(vermifugo)
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f'Erro de validação ao criar Vermífugo garantido: {e.message_dict if hasattr(e, "message_dict") else e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar Vermífugo garantido: {e}'))

        for _ in range(total_medicamentos_gerar - len(medicamentos)):
            nome_medicamento = fake.unique.word().capitalize() + ' ' + random.choice(['Creme', 'Comprimido', 'Injetável', 'Gotas', 'Xarope', 'Solução'])
            tipo_med = random.choice(tipos_medicamento_choices)
            
            medicamento = EstoqueMedicamento(
                medicamento=nome_medicamento,
                tipo_medicamento=tipo_med,
                lote=fake.unique.uuid4()[:8].upper(),
                data_validade=fake.date_between(start_date='today', end_date='+3y'),
                quantidade=random.randint(0, 200),
            )
            try:
                medicamento.full_clean()
                medicamento.save()
                medicamentos.append(medicamento)
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f'Erro de validação ao criar EstoqueMedicamento: {e.message_dict if hasattr(e, "message_dict") else e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar EstoqueMedicamento: {e}'))
        self.stdout.write(self.style.SUCCESS(f'{len(medicamentos)} Medicamentos criados (incluindo garantidos).'))
        
        self.stdout.write(self.style.SUCCESS('População inicial de dados (Veterinario, Tutor, Animal, EstoqueMedicamento) concluída!'))

        # --- A partir daqui: Agendamentos, Consultas, Vacinação, Vermifugação, Terceiros ---

        self.stdout.write('Populando Agendamentos e Consultas...')
        agendamentos_criados = []
        consultas_criadas = []
        if not animais or not veterinarios:
            self.stdout.write(self.style.WARNING("Pulando Agendamento/Consulta: Não há animais ou veterinários suficientes."))
        else:
            for _ in range(40):
                animal = random.choice(animais)
                veterinario = random.choice(veterinarios)
                is_castracao = random.random() < 0.15 

                # Gerar data da consulta entre 30 dias atrás e 6 meses no futuro para "agendada"
                # ou entre 15 dias atrás e "agora" para "realizada"
                if random.random() < 0.7: # 70% de chance de ser consulta já realizada
                    # data_atendimento da ConsultaClinica não pode ser mais antiga que 15 dias
                    # Então, para 'realizada', a data deve estar nesse range.
                    start_date_realizada = timezone.now() - timedelta(days=14) # Mínimo 14 dias atrás
                    end_date_realizada = timezone.now()
                    data_consulta_dt = fake.date_time_between(start_date=start_date_realizada, end_date=end_date_realizada, tzinfo=timezone.get_current_timezone())
                    status_agendamento_temp = 'realizada'
                else: # Agendamentos futuros
                    data_consulta_dt = fake.date_time_between(start_date='now', end_date='+6m', tzinfo=timezone.get_current_timezone())
                    status_agendamento_temp = 'agendada'

                agendamento = AgendamentoConsultas(
                    animal=animal,
                    data_consulta=data_consulta_dt,
                    is_castracao=is_castracao,
                )
                try:
                    agendamento.full_clean()
                    agendamento.save() 
                    agendamentos_criados.append(agendamento)

                    consulta = None
                    if status_agendamento_temp == 'realizada':
                        consulta = getattr(agendamento, 'consulta_gerada', None)
                        
                        if consulta:
                            tipo_atendimento_choices = ['CONSULTA_ROTINA', 'EMERGENCIA', 'OUTRO']
                            
                            consulta.veterinario = veterinario
                            consulta.tipo_atendimento = random.choice(tipo_atendimento_choices)
                            consulta.diagnostico = fake.text(max_nb_chars=200)
                            consulta.observacoes = fake.text(max_nb_chars=150) if random.random() > 0.5 else ''
                            
                            peso_min = float(animal.peso) * 0.9
                            peso_max = float(animal.peso) * 1.1
                            consulta.peso = Decimal(str(round(random.uniform(peso_min, peso_max), 2)))

                            consulta.temperatura = Decimal(str(round(random.uniform(37.5, 39.5), 1)))
                            consulta.frequencia_cardiaca = random.randint(60, 180)
                            consulta.frequencia_respiratoria = random.randint(15, 60)
                            consulta.avaliacao_mucosa = random.choice(['Rósea', 'Pálida', 'Ictérica']) if random.random() > 0.3 else None
                            consulta.tempo_preenchimento_capilar = random.choice(['< 2 segundos', '3 segundos', '> 3 segundos']) if random.random() > 0.3 else None
                            
                            consulta.observacoes += f" Prognóstico: {random.choice(['Bom', 'Reservado', 'Ruim'])}." if consulta.observacoes else f"Prognóstico: {random.choice(['Bom', 'Reservado', 'Ruim'])}."

                            try:
                                consulta.full_clean()
                                consulta.save()
                                consultas_criadas.append(consulta) 
                            except ValidationError as e:
                                self.stdout.write(self.style.ERROR(f'Erro de validação ao atualizar/salvar ConsultaClinica (gerada por agendamento): {e.message_dict if hasattr(e, "message_dict") else e}'))
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'Erro inesperado ao atualizar/salvar ConsultaClinica (gerada por agendamento): {e}'))

                            if consulta and consulta.pk:
                                num_medicamentos_consulta = random.randint(0, 3)
                                for _ in range(num_medicamentos_consulta):
                                    if not medicamentos: continue
                                    medicamento_estoque = random.choice(medicamentos)
                                    if medicamento_estoque.quantidade > 0:
                                        quantidade = random.randint(1, min(5, medicamento_estoque.quantidade))
                                        med_consulta = MedicamentoConsulta(
                                            consulta=consulta,
                                            medicamento_estoque=medicamento_estoque,
                                            quantidade_aplicada=quantidade,
                                        )
                                        try:
                                            med_consulta.full_clean()
                                            med_consulta.save()
                                        except ValidationError as e:
                                            self.stdout.write(self.style.ERROR(f'Erro de validação ao criar MedicamentoConsulta: {e.message_dict if hasattr(e, "message_dict") else e}'))
                                        except Exception as e:
                                            self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar MedicamentoConsulta: {e}'))

                                num_exames_consulta = random.randint(0, 2)
                                for _ in range(num_exames_consulta):
                                    nome_exame_choices = ['Hemograma', 'Bioquímico', 'Ultrassom', 'Raio-X', 'Urinálise', 'Coproparasitológico']
                                    tipo_exame_choices = ['Imagem', 'Laboratorial', 'Clínico']
                                    
                                    exame = Exames(
                                        consulta=consulta,
                                        animal=animal,
                                        nome=random.choice(nome_exame_choices),
                                        descricao=fake.text(max_nb_chars=100) if random.random() > 0.3 else '',
                                        tipo=random.choice(tipo_exame_choices),
                                        data_exame=fake.date_between(start_date=consulta.data_atendimento.date(), end_date='now'),
                                    )
                                    try:
                                        exame.full_clean()
                                        exame.save()
                                    except ValidationError as e:
                                        self.stdout.write(self.style.ERROR(f'Erro de validação ao criar Exame: {e.message_dict if hasattr(e, "message_dict") else e}'))
                                    except Exception as e:
                                        self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar Exame: {e}'))

                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f'Erro de validação ao criar AgendamentoConsultas: {e.message_dict if hasattr(e, "message_dict") else e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar AgendamentoConsultas: {e}'))

        self.stdout.write(self.style.SUCCESS(f'{len(agendamentos_criados)} Agendamentos e {len(consultas_criadas)} Consultas criados.'))

        # 6. Popula RegistroVacinacao
        self.stdout.write('Populando Registros de Vacinação...')
        vacinas_disponiveis = [m for m in medicamentos if m.tipo_medicamento == EstoqueMedicamento.VACINA and m.quantidade > 0]
        
        if not animais or not vacinas_disponiveis:
            self.stdout.write(self.style.WARNING("Pulando RegistroVacinacao: Não há animais ou vacinas disponíveis suficientes."))
        else:
            for animal in animais:
                num_vacinas = random.randint(0, 2)
                for _ in range(num_vacinas):
                    medicamento_vacina = random.choice(vacinas_disponiveis)
                    
                    # data_aplicacao: DataField no RegistroVacinacao. Deve ser após o nascimento do animal e dentro dos últimos 15 dias.
                    # Assegura que start_date seja <= end_date.
                    # start_date deve ser no máximo 'hoje - 14 dias' para passar a validação 'não pode ser anterior a 15 dias atrás'
                    start_date_aplicacao_v = max(animal.data_nascimento + timedelta(days=60), date.today() - timedelta(days=14))
                    
                    data_aplicacao = fake.date_between(
                        start_date=start_date_aplicacao_v, 
                        end_date='today'
                    )
                    # data_revacinacao: null=False no modelo. Deve ter um valor.
                    # Garantir que data_revacinacao seja APÓS data_aplicacao.
                    data_revacinacao = data_aplicacao + timedelta(days=365) # Um ano depois da aplicação
                    
                    registro_vacinacao = RegistroVacinacao(
                        animal=animal,
                        medicamento_aplicado=medicamento_vacina,
                        data_aplicacao=data_aplicacao,
                        data_revacinacao=data_revacinacao,
                    )
                    try:
                        registro_vacinacao.full_clean()
                        registro_vacinacao.save()
                    except ValidationError as e:
                        self.stdout.write(self.style.ERROR(f'Erro de validação ao criar RegistroVacinacao: {e.message_dict if hasattr(e, "message_dict") else e}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar RegistroVacinacao: {e}'))
            self.stdout.write(self.style.SUCCESS('Registros de Vacinação criados.'))

        # 7. Popula RegistroVermifugos
        self.stdout.write('Populando Registros de Vermifugação...')
        vermifugos_disponiveis = [m for m in medicamentos if m.tipo_medicamento == EstoqueMedicamento.VERMIFUGO and m.quantidade > 0]
        
        if not animais or not vermifugos_disponiveis:
            self.stdout.write(self.style.WARNING("Pulando RegistroVermifugos: Não há animais ou vermífugos disponíveis suficientes."))
        else:
            for animal in animais:
                num_vermifugos = random.randint(0, 2)
                for _ in range(num_vermifugos):
                    medicamento_vermifugo = random.choice(vermifugos_disponiveis)
                    
                    # data_administracao: DataField no RegistroVermifugos. Deve ser após o nascimento do animal e dentro dos últimos 15 dias.
                    # Assegura que start_date seja <= end_date.
                    # start_date deve ser no máximo 'hoje - 14 dias' para passar a validação 'não pode ser anterior a 15 dias atrás'
                    start_date_admin_v = max(animal.data_nascimento + timedelta(days=30), date.today() - timedelta(days=14))
                    
                    data_administracao = fake.date_between(
                        start_date=start_date_admin_v, 
                        end_date='today'
                    )
                    # data_readministracao: null=False no modelo. Deve ter um valor.
                    # Garantir que data_readministracao seja APÓS data_administracao.
                    data_readministracao = data_administracao + timedelta(days=90) # 90 dias depois da administração
                    
                    registro_vermifugos = RegistroVermifugos(
                        animal=animal,
                        medicamento_administrado=medicamento_vermifugo,
                        data_administracao=data_administracao,
                        data_readministracao=data_readministracao,
                    )
                    try:
                        registro_vermifugos.full_clean()
                        registro_vermifugos.save()
                    except ValidationError as e:
                        self.stdout.write(self.style.ERROR(f'Erro de validação ao criar RegistroVermifugos: {e.message_dict if hasattr(e, "message_dict") else e}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar RegistroVermifugos: {e}'))
            self.stdout.write(self.style.SUCCESS('Registros de Vermifugação criados.'))


        self.stdout.write('Populando Empresas Terceirizadas...')
        empresas_terceirizadas = []
        for _ in range(5):
            empresa = EmpresaTerceirizada(
                razao_social=fake.unique.company(),
                cnpj=fake.cnpj().replace('.', '').replace('/', '').replace('-', ''),
                telefone=fake.msisdn()[:11],
                email=fake.unique.company_email() if random.random() < 0.8 else None
            )
            try:
                empresa.full_clean()
                empresa.save()
                empresas_terceirizadas.append(empresa)
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f'Erro de validação ao criar EmpresaTerceirizada: {e.message_dict if hasattr(e, "message_dict") else e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar EmpresaTerceirizada: {e}'))
        self.stdout.write(self.style.SUCCESS(f'{len(empresas_terceirizadas)} Empresas Terceirizadas criadas.'))

        self.stdout.write('Populando Registros de Serviço...')
        if not animais or not empresas_terceirizadas:
            self.stdout.write(self.style.WARNING("Pulando RegistroServico: Não há animais ou empresas terceirizadas suficientes."))
        else:
            for _ in range(15):
                animal = random.choice(animais)
                empresa = random.choice(empresas_terceirizadas)
                data_hora_procedimento = fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
                valor_servico = Decimal(str(round(random.uniform(50.0, 500.0), 2))) if random.random() < 0.8 else None
                
                registro_servico = RegistroServico(
                    empresa=empresa,
                    animal=animal,
                    data_hora_procedimento=data_hora_procedimento,
                    valor_servico=valor_servico,
                    medicamentos_aplicados=fake.text(max_nb_chars=100) if random.random() < 0.7 else '',
                    outros_procedimentos=fake.text(max_nb_chars=150) if random.random() < 0.7 else ''
                )
                try:
                    registro_servico.full_clean()
                    registro_servico.save()
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f'Erro de validação ao criar RegistroServico: {e.message_dict if hasattr(e, "message_dict") else e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro inesperado ao criar RegistroServico: {e}'))
        self.stdout.write(self.style.SUCCESS('Registros de Serviço criados.'))


        self.stdout.write(self.style.SUCCESS('População de dados concluída com sucesso!'))