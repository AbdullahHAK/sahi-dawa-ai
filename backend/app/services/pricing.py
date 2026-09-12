"""Same-active-ingredient matching and deterministic price comparison.

All calculations are plain Python over catalogue values. No estimation, no
LLM involvement, no ranking beyond factual lowest-price computation.
"""

from typing import List, Optional, Tuple

from app.models.schemas import (
    AlternativeRecord,
    MedicineRecord,
    PriceComparison,
)
from app.services.catalogue import CatalogueRepository


def get_same_ingredient_alternatives(
    repository: CatalogueRepository, medicine: MedicineRecord
) -> List[AlternativeRecord]:
    """Other catalogue records sharing the matched medicine's active ingredient."""
    matches = repository.find_by_active_ingredient(
        medicine.active_ingredient, exclude_medicine_id=medicine.medicine_id
    )
    return [CatalogueRepository.to_alternative_record(row) for _, row in matches.iterrows()]


def compare_prices(
    medicine: MedicineRecord, alternatives: List[AlternativeRecord]
) -> PriceComparison:
    """Compute the lowest available price across the medicine and its alternatives.

    Missing prices are never treated as zero and never estimated -- they are
    simply excluded from the lowest-price calculation.
    """
    priced_candidates: List[Tuple[str, float, str]] = []

    if medicine.price is not None:
        priced_candidates.append((medicine.medicine_id, medicine.price, medicine.pack_size))

    for alt in alternatives:
        if alt.price is not None:
            priced_candidates.append((alt.medicine_id, alt.price, alt.pack_size))

    lowest_id: Optional[str] = None
    lowest_price: Optional[float] = None
    lowest_pack_size: Optional[str] = None
    if priced_candidates:
        lowest_id, lowest_price, lowest_pack_size = min(priced_candidates, key=lambda item: item[1])

    price_difference: Optional[float] = None
    if medicine.price is not None and lowest_price is not None:
        price_difference = round(medicine.price - lowest_price, 2)

    return PriceComparison(
        current_price=medicine.price,
        current_pack_size=medicine.pack_size,
        lowest_price=lowest_price,
        lowest_price_medicine_id=lowest_id,
        lowest_price_pack_size=lowest_pack_size,
        price_difference=price_difference,
    )
