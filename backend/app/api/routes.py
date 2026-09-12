"""API routes for the deterministic catalogue/matching/pricing layer."""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_catalogue_repository
from app.models.schemas import (
    NOT_FOUND_MESSAGE,
    AlternativesResponse,
    MatchStatus,
    MedicineRecord,
    PrescriptionRequest,
    PrescriptionResponse,
)
from app.services.catalogue import CatalogueRepository
from app.services.matching import identify_medicine
from app.services.pricing import compare_prices, get_equivalent_alternatives

router = APIRouter()


@router.post("/prescription", response_model=PrescriptionResponse)
def post_prescription(
    request: PrescriptionRequest,
    repository: CatalogueRepository = Depends(get_catalogue_repository),
) -> PrescriptionResponse:
    """Identify the prescribed medicine and return catalogue-backed comparisons.

    This covers only the deterministic catalogue layer: identification,
    the verified record, same-medicine (ingredient + strength + dosage form)
    alternatives and price comparison. RAG explanation, encounter storage
    and pattern detection are implemented by other layers.
    """
    result = identify_medicine(repository, request.medicine, request.dosage)

    response = PrescriptionResponse(
        patient_id=request.patient_id,
        diagnosis=request.diagnosis,
        medicine_query=request.medicine,
        dosage_query=request.dosage,
        status=result.status,
        message=result.message,
        candidates=result.candidates,
    )

    if result.status == MatchStatus.FOUND and result.medicine is not None:
        alternatives = get_equivalent_alternatives(repository, result.medicine)
        response.medicine = result.medicine
        response.alternatives = alternatives
        response.price_comparison = compare_prices(result.medicine, alternatives)

    return response


@router.get("/medicine/{medicine_id}", response_model=MedicineRecord)
def get_medicine(
    medicine_id: str,
    repository: CatalogueRepository = Depends(get_catalogue_repository),
) -> MedicineRecord:
    """Return the verified catalogue record for a given medicine_id."""
    record = repository.get_by_id(medicine_id)
    if record is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND_MESSAGE)
    return record


@router.get("/alternatives/{medicine_id}", response_model=AlternativesResponse)
def get_alternatives(
    medicine_id: str,
    repository: CatalogueRepository = Depends(get_catalogue_repository),
) -> AlternativesResponse:
    """Return same-medicine (ingredient + strength + dosage form) catalogue
    records and a price comparison."""
    record = repository.get_by_id(medicine_id)
    if record is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND_MESSAGE)

    alternatives = get_equivalent_alternatives(repository, record)
    price_comparison = compare_prices(record, alternatives)

    return AlternativesResponse(
        medicine_id=record.medicine_id,
        active_ingredient=record.active_ingredient,
        strength=record.strength,
        dosage_form=record.dosage_form,
        alternatives=alternatives,
        price_comparison=price_comparison,
    )
