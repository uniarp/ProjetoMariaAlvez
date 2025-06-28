FROM python:3.13

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Adicionadas as dependências do sistema necessárias para WeasyPrint
# Essas são bibliotecas de renderização de gráficos e texto
RUN apt-get update && \
    apt-get install -y \
    postgresql-client \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    # FFI é frequentemente necessário para algumas dependências do WeasyPrint
    # (como cffi, que é usado por algumas libs de baixo nível)
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

EXPOSE 8000
