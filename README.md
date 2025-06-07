
# 🐾 Projeto Maria Alvez

Sistema web desenvolvido para o **Centro de Bem-Estar Animal de Caçador/SC**, com o objetivo de auxiliar na gestão de atendimentos, cadastros de animais, tutores, vacinas, medicamentos e outros serviços voltados ao bem-estar animal.

Projeto acadêmico desenvolvido pela **turma de Análise e Desenvolvimento de Sistemas (ADS)** da **Universidade Alto Vale do Rio do Peixe (UNIARP)**.

---

## 🎯 Objetivo

Criar uma aplicação moderna, eficiente e acessível para apoiar a administração do centro de bem-estar animal, promovendo um controle mais eficaz e transparente dos serviços prestados.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.13**
- **Django**
- **Docker + Docker Compose**
- **PostgreSQL**

---

## 🗂️ Estrutura do Projeto

```
PROJETOMARIAALVEZ/
├── MariaAlvez/              # Configurações principais do Django
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── MariaAlvezApp/           # App principal
│   ├── models.py            # Modelos como Tutor, Animal, etc.
│   ├── views.py
│   └── ...
├── .env                     # Variáveis de ambiente
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh            # Script de inicialização do container
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos

- Docker e Docker Compose instalados

### Instruções

1. Clone o repositório:
   ```bash
   git clone https://github.com/uniarp/ProjetoMariaAlvez.git
   cd ProjetoMariaAlvez
   ```

2. Crie o arquivo `.env` com suas variáveis de ambiente (exemplo abaixo):
   ```
   DEBUG=1
   SECRET_KEY=sua_chave_secreta
   DB_NAME=mariaalvezdb
   DB_USER=postgres
   DB_PASSWORD=senha
   DB_HOST=db
   DB_PORT=5432
   ```

3. Suba o ambiente com Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. Acesse no navegador:
   ```
   http://localhost:8000
   ```

---

## ✅ Funcionalidades (em desenvolvimento)

### 👤 Gestão de Pessoas
- [ ] Cadastro de Veterinários
- [ ] Cadastro de Tutores
- [ ] Cadastro de Animais

### 🩺 Atendimento Clínico
- [ ] Agendamento de Consultas
- [ ] Agendamento de Castração
- [ ] Registro de Consultas Clínicas

### 💉 Procedimentos
- [ ] Registro de Vacinações
- [ ] Registro de Vermífugos
- [ ] Registro de Exames
- [ ] Registro e controle de Castrações

### 💊 Gestão de Estoque
- [ ] Cadastro e controle de Medicamentos

### 📊 Relatórios
- [ ] Relatório de Consultas
- [ ] Relatório de Estoque
- [ ] Gestão da Fila de Castração

### 🔐 Autenticação e Acesso
- [ ] Login e gerenciamento de usuários (administração e colaboradores)

---

## 👥 Equipe

Desenvolvido pela turma de **Análise e Desenvolvimento de Sistemas (ADS)** da **UNIARP — Universidade Alto Vale do Rio do Peixe**.