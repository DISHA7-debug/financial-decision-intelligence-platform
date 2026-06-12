from fastapi import APIRouter, HTTPException

from backend.schemas import (
    CommitteeReportResponse,
    ErrorResponse,
    ReportResponse,
)
from backend.services import (
    CompanyNotFoundError,
    ModelLoadError,
    ReportNotFoundError,
    WorkflowError,
    get_committee_report,
    get_company_report,
)

router = APIRouter(tags=["reports"])


@router.get(
    "/report/{company}",
    response_model=ReportResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def company_report(company: str) -> ReportResponse:
    try:
        return get_company_report(company)
    except CompanyNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ReportNotFoundError as error:
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
            detail=f"Unexpected error loading report: {error}",
        ) from error


@router.get(
    "/committee-report",
    response_model=CommitteeReportResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def committee_report() -> CommitteeReportResponse:
    try:
        return get_committee_report()
    except ReportNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error loading committee report: {error}",
        ) from error
