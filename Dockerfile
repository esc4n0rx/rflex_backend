# =============================================================================
# RFlex License Server - Dockerfile para Coolify
# =============================================================================
# Imagem base otimizada para Python com dependências de sistema
FROM python:3.12-slim

# Metadados
LABEL maintainer="RFlex Team"
LABEL description="RFlex License Server - API de Licenciamento"
LABEL version="1.0.0"

# =============================================================================
# ESTÁGIO 1: Variáveis de Ambiente
# =============================================================================
# Desabilita criação de arquivos .pyc (otimização)
ENV PYTHONDONTWRITEBYTECODE=1 \
    # Desabilita buffer de Python (logs em tempo real)
    PYTHONUNBUFFERED=1 \
    # Diretório de trabalho
    WORKDIR=/app \
    # Porta da aplicação
    PORT=8000 \
    # Ambiente
    ENVIRONMENT=production

# =============================================================================
# ESTÁGIO 2: Dependências de Sistema
# =============================================================================
# Instala apenas dependências essenciais e limpa caches em uma única camada
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libmariadb-dev \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# =============================================================================
# ESTÁGIO 3: Usuário Não-Root (Segurança)
# =============================================================================
# Cria usuário dedicado para executar a aplicação
RUN groupadd -r rflex && \
    useradd -r -g rflex -d /app -s /sbin/nologin -c "RFlex User" rflex

# =============================================================================
# ESTÁGIO 4: Setup da Aplicação
# =============================================================================
# Define diretório de trabalho
WORKDIR /app

# Copia apenas requirements.txt primeiro (cache do Docker)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia arquivos da aplicação
COPY app ./app
COPY run.py .
COPY alembic.ini .
COPY alembic ./alembic

# Cria diretório para logs com permissões corretas
RUN mkdir -p /app/logs && \
    chown -R rflex:rflex /app

# =============================================================================
# ESTÁGIO 5: Configuração de Portas e Volumes
# =============================================================================
# Expõe a porta da aplicação
EXPOSE 8000

# Volume para logs (persistência)
VOLUME ["/app/logs"]

# =============================================================================
# ESTÁGIO 6: Health Check
# =============================================================================
# Verifica saúde da aplicação a cada 30s
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# =============================================================================
# ESTÁGIO 7: Startup
# =============================================================================
# Muda para usuário não-root
USER rflex

# Comando de execução em produção
CMD ["python", "run.py", "--production", "--host", "0.0.0.0", "--port", "8000"]
