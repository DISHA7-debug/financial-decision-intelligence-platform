from fastapi import APIRouter, HTTPException

from backend.schemas import CompareRequest, CompareResponse, ErrorResponse
from backend.services import (
    CompanyNotFoundError,
    WorkflowError,
    compare_companies_api,
)

router = APIRouter(tags=["compare"])


@router.post(
    "/compare",
    response_model=CompareResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def compare(request: CompareRequest) -> CompareResponse:
    try:
        return compare_companies_api(request.companies)
    except CompanyNotFoundError as error:
        raise HTTPException(
            status_code=404,
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
            detail=f"Unexpected error during comparison: {error}",
        ) from error
