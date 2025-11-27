# main_v1.py
# Titan-X Core API – v1
# Clean production-ready entrypoint

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import ONLY the Titan Core v1 router
from routes.core_v1 import router as core_v1_router
from routes.support_v1 import router as support_v1_router
from routes.marketing_v1 import router as marketing_v1_router


# -----------------------------------------------------
# Create FastAPI app
# -----------------------------------------------------
app = FastAPI(
    title="Titan-X Core API",
    version="1.0.0",
    description="Titan-X Core behavioural engine (HALO v1). Clean, stable v1 API surface.",
)


# -----------------------------------------------------
# CORS (allow all for dev – tighten later)
# -----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------
# Include ONLY the core v1 router
# -----------------------------------------------------
app.include_router(core_v1_router)
app.include_router(support_v1_router)
app.include_router(marketing_v1_router)


# -----------------------------------------------------
# Root endpoint (optional)
# -----------------------------------------------------
@app.get("/", tags=["root"])
async def root():
    return {
        "service": "titan-x-core",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
