from fastapi import APIRouter, HTTPException

from backend.schemas import AnalyzeRequest, AnalyzeResponse, ErrorResponse
from backend.services import (
    CompanyNotFoundError,
    ModelLoadError,
    WorkflowError,
    analyze_company,
)

router = APIRouter(tags=["analyze"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        return analyze_company(request.company)
    except CompanyNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ModelLoadError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error
    except WorkflowError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during analysis: {error}",
        ) from error
