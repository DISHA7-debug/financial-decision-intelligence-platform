from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import analyze, compare, reports
from backend.schemas import HealthResponse

app = FastAPI(
    title="Financial Decision Intelligence API",
    description=(
        "Production API for SEC-based due diligence, risk analysis, "
        "and investment recommendations."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(compare.router)
app.include_router(reports.router)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
)
def health() -> HealthResponse:
    return HealthResponse(status="healthy")
