#!/bin/bash
set -e

# Verifica se as variáveis de ambiente essenciais estão definidas
: "${POSTGRES_USER:?Erro: variável POSTGRES_USER não definida}"
: "${POSTGRES_DB:?Erro: variável POSTGRES_DB não definida}"
: "${POSTGRES_HOST:?Erro: variável POSTGRES_HOST não definida}"
: "${POSTGRES_PORT:?Erro: variável POSTGRES_PORT não definida}"

# Aguarda o banco de dados estar disponível
until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"; do
  echo "Aguardando o banco de dados (${POSTGRES_HOST}:${POSTGRES_PORT})..."
  sleep 2
done

echo "PostgreSQL está pronto!"

# Configurar variáveis de ambiente do Django
export DJANGO_SETTINGS_MODULE=MariaAlvez.settings


# Rodar as migrações do Django
echo "Executando migrações do Django..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Criar superusuário se não existir
if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_EMAIL}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
  echo "Verificando/criando superusuário Django..."
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
username = '${DJANGO_SUPERUSER_USERNAME}'
email = '${DJANGO_SUPERUSER_EMAIL}'
password = '${DJANGO_SUPERUSER_PASSWORD}'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superusuário criado com sucesso!')
else:
    print('Superusuário já existe.')
"
fi

# Executar o comando passado ou iniciar o servidor
if [ "$#" -gt 0 ]; then
  echo "Executando comando: $@"
  exec "$@"
else
  echo "Iniciando o servidor Django em 127.0.0.1:8000"
  exec python manage.py runserver 0.0.0.0:8000
fi