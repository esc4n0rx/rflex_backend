"""
Aplicação principal FastAPI - RFlex License Server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.routes import (
    auth,
    companies,
    plans,
    licenses,
    devices,
    public,
    dashboard
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.

    Startup: Inicializa conexões e recursos.
    Shutdown: Limpa recursos.
    """
    # Startup
    print("[*] Iniciando RFlex License Server...")
    print(f"[+] Ambiente: {settings.environment}")
    print(f"[+] Database: {settings.db_host}:{settings.db_port}/{settings.db_name}")

    # Inicializa banco de dados (apenas em desenvolvimento)
    if settings.environment == "development":
        init_db()
        print("[+] Banco de dados inicializado")

    yield

    # Shutdown
    print("[*] Desligando RFlex License Server...")


# Cria aplicação FastAPI
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="""
    API oficial de licenciamento do RFlex Client.

    ## Autenticação

    As rotas administrativas requerem token JWT obtido via `/api/v1/auth/login`.

    ## Rotas Públicas

    As rotas em `/api/v1/public` são usadas pelo app RFlex Client (coletores)
    e não requer autenticação de administrador.

    ## Estrutura

    - **Empresas**: Gerencia clientes (empresas)
    - **Planos**: Gerencia planos de licenciamento
    - **Licenças**: Gerencia licenças de uso
    - **Dispositivos**: Gerencia coletores ativados
    - **Dashboard**: Métricas e estatísticas
    """,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "message": "RFlex License Server",
        "status": "running",
        "version": settings.api_version,
        "environment": settings.environment
    }


@app.get("/health", tags=["Health"])
def health():
    """Health check detalhado."""
    return {
        "status": "healthy",
        "database": "connected"  # TODO: verificar conexão real
    }


# Registra rotas
api_prefix = "/api/v1"

app.include_router(auth.router, prefix=api_prefix)
app.include_router(companies.router, prefix=api_prefix)
app.include_router(plans.router, prefix=api_prefix)
app.include_router(licenses.router, prefix=api_prefix)
app.include_router(devices.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(public.router, prefix=api_prefix)


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handler para ValueError."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


# Run com: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
