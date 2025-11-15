# Dockerfile — FT9 Intelligence Backend (Python 3.11)
FROM python:3.11-slim

# Evitar interações
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências do sistema (necessárias para psycopg2 e pgvector)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar código do backend
COPY . .

# Rodar usando uvicorn — Railway usa este comando
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
