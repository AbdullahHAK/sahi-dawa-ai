"""API routes for the deterministic catalogue/matching/pricing layer."""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_catalogue_repository, get_history_repository
from app.models.schemas import (
    NOT_FOUND_MESSAGE,
    AlternativesResponse,
    HistoryResponse,
    MatchStatus,
    MedicineRecord,
    PrescriptionRequest,
    PrescriptionResponse,
)
from app.services.catalogue import CatalogueRepository
from app.services.history import HistoryRepository
from app.services.matching import identify_medicine
from app.services.patterns import detect_patterns, enrich_with_category
from app.services.pricing import compare_prices, get_equivalent_alternatives

router = APIRouter()


@router.post("/prescription", response_model=PrescriptionResponse)
def post_prescription(
    request: PrescriptionRequest,
    repository: CatalogueRepository = Depends(get_catalogue_repository),
    history: HistoryRepository = Depends(get_history_repository),
) -> PrescriptionResponse:
    """Identify the prescribed medicine and return catalogue-backed comparisons.

    Covers the deterministic catalogue layer: identification, the verified
    record, same-medicine (ingredient + strength + dosage form) alternatives,
    price comparison, encounter storage and historical pattern detection.
    RAG explanation is implemented by another layer.
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

        history.save_encounter(
            patient_id=request.patient_id,
            diagnosis=request.diagnosis,
            medicine_id=result.medicine.medicine_id,
            medicine_name=result.medicine.brand_name,
            dosage=request.dosage,
        )
        enriched = enrich_with_category(repository, history.get_encounters(request.patient_id))
        response.pattern_flags = detect_patterns(enriched)

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


@router.get("/history/{patient_id}", response_model=HistoryResponse)
def get_history(
    patient_id: str,
    repository: CatalogueRepository = Depends(get_catalogue_repository),
    history: HistoryRepository = Depends(get_history_repository),
) -> HistoryResponse:
    """Return a patient's stored encounters and any detected discussion flags.

    An unknown/never-seen patient_id simply returns an empty history, not an
    error -- there is nothing exceptional about a first-time patient.
    """
    enriched = enrich_with_category(repository, history.get_encounters(patient_id))
    return HistoryResponse(
        patient_id=patient_id,
        encounters=enriched,
        pattern_flags=detect_patterns(enriched),
    )
