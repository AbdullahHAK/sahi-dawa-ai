"""Pydantic models for the deterministic catalogue/matching/pricing API."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

NOT_FOUND_MESSAGE = "This medicine is not currently available in our verified catalogue."

AMBIGUOUS_MESSAGE = (
    "Multiple verified catalogue records match this medicine name. "
    "Please specify the exact brand, strength or dosage form."
)

SAME_INGREDIENT_NOTE = (
    "These medicines contain the same active ingredient according to our verified "
    "catalogue. Discuss any substitution with your healthcare professional."
)


class MatchStatus(str, Enum):
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    AMBIGUOUS = "AMBIGUOUS"


class MedicineRecord(BaseModel):
    """A single verified catalogue record, as read from the CSV."""

    medicine_id: str
    brand_name: str
    generic_name: str
    active_ingredient: str
    strength: str
    dosage_form: str
    pack_size: str
    manufacturer: str
    price: Optional[float] = None
    price_effective_date: Optional[str] = None
    registration_number: Optional[str] = None
    drap_source_url: Optional[str] = None
    last_verified: Optional[str] = None
    data_status: str
    medicine_category: str


class CandidateSummary(BaseModel):
    """Minimal fields shown when a query matches more than one catalogue record."""

    medicine_id: str
    brand_name: str
    generic_name: str
    strength: str
    dosage_form: str
    pack_size: str
    manufacturer: str


class AlternativeRecord(BaseModel):
    """A same-active-ingredient catalogue record, for comparison display."""

    medicine_id: str
    brand_name: str
    generic_name: str
    strength: str
    dosage_form: str
    pack_size: str
    manufacturer: str
    price: Optional[float] = None
    price_effective_date: Optional[str] = None
    data_status: str
    last_verified: Optional[str] = None


class PriceComparison(BaseModel):
    """Deterministic price comparison across a medicine and its alternatives."""

    current_price: Optional[float] = None
    current_pack_size: str
    lowest_price: Optional[float] = None
    lowest_price_medicine_id: Optional[str] = None
    lowest_price_pack_size: Optional[str] = None
    price_difference: Optional[float] = None
    note: str = SAME_INGREDIENT_NOTE


class AlternativesResponse(BaseModel):
    """Response for GET /alternatives/{id}."""

    medicine_id: str
    active_ingredient: str
    alternatives: List[AlternativeRecord]
    price_comparison: PriceComparison
    note: str = SAME_INGREDIENT_NOTE


class MedicineLookupResult(BaseModel):
    """Outcome of identifying a medicine name (+ optional dosage) in the catalogue."""

    status: MatchStatus
    message: Optional[str] = None
    medicine: Optional[MedicineRecord] = None
    candidates: List[CandidateSummary] = Field(default_factory=list)


class PrescriptionRequest(BaseModel):
    patient_id: str
    diagnosis: str
    medicine: str
    dosage: Optional[str] = None


class PrescriptionResponse(BaseModel):
    """Response for POST /prescription.

    Covers only the deterministic catalogue/matching/pricing layer. RAG
    explanation, patient history and pattern detection are out of scope here
    and are expected to be layered on by downstream services.
    """

    patient_id: str
    diagnosis: str
    medicine_query: str
    dosage_query: Optional[str] = None
    status: MatchStatus
    message: Optional[str] = None
    medicine: Optional[MedicineRecord] = None
    candidates: List[CandidateSummary] = Field(default_factory=list)
    alternatives: List[AlternativeRecord] = Field(default_factory=list)
    price_comparison: Optional[PriceComparison] = None
