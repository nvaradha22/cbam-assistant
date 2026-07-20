from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import hs_codes, calculator, emission_factors, suppliers, validation, reports

app = FastAPI(
    title="CBAM Assistant API",
    description="Open-source EU CBAM compliance tool for GCC exporters",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hs_codes.router)
app.include_router(calculator.router)
app.include_router(emission_factors.router)
app.include_router(suppliers.router)
app.include_router(validation.router)
app.include_router(reports.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "cbam-assistant"}


@app.get("/")
async def root() -> dict:
    return {"message": "CBAM Assistant API", "docs": "/docs"}
