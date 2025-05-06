from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.api.v1.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando la aplicación Convertix...")
    yield
    logger.info("Cerrando la aplicación Convertix...")

app = FastAPI(
    title="Convertix API",
    description="API para conversión de imágenes",
    version="0.1.0",
    docs_url="/docs", 
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configurar los CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Incluir routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Manejador de excepciones global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Se produjo un error interno en el servidor."},
    )

# Ruta de verificación de salud
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )