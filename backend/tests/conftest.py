import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_catalogue_repository
from app.main import app
from app.services.catalogue import CatalogueRepository

SAMPLE_CSV_ROWS = [
    # medicine_id, brand_name, generic_name, active_ingredient, strength, dosage_form,
    # pack_size, manufacturer, price, price_effective_date, registration_number,
    # drap_source_url, last_verified, data_status, medicine_category
    ["TESTX001", "BrandA", "GenericX", "IngredientX", "100mg", "Tablet", "10's", "ManuA",
     "100.0", "01 Jan, 2026", "REG1", "http://example.com", "2026-01-01", "VERIFIED", "Antibiotic"],
    ["TESTX002", "BrandA", "GenericX", "IngredientX", "200mg", "Tablet", "10's", "ManuA",
     "150.0", "01 Jan, 2026", "REG2", "http://example.com", "2026-01-01", "VERIFIED", "Antibiotic"],
    ["TESTX003", "BrandB", "GenericX", "IngredientX", "100mg", "Capsule", "10's", "ManuB",
     "80.0", "01 Jan, 2026", "REG3", "http://example.com", "2026-01-01", "VERIFIED", "Antibiotic"],
    ["TESTX004", "BrandC", "GenericY", "IngredientX", "50mg", "Tablet", "5's", "ManuC",
     "", "", "REG4", "http://example.com", "2026-01-01", "VERIFIED", "Antibiotic"],
    ["TESTZ001", "BrandZ", "GenericZ", "IngredientZ", "10mg", "Tablet", "10's", "ManuZ",
     "50.0", "01 Jan, 2026", "REG5", "http://example.com", "2026-01-01", "VERIFIED", "Non-antibiotic"],
]

SAMPLE_COLUMNS = [
    "medicine_id", "brand_name", "generic_name", "active_ingredient", "strength",
    "dosage_form", "pack_size", "manufacturer", "price", "price_effective_date",
    "registration_number", "drap_source_url", "last_verified", "data_status",
    "medicine_category",
]


@pytest.fixture
def sample_csv_path(tmp_path):
    path = tmp_path / "medicines.csv"
    df = pd.DataFrame(SAMPLE_CSV_ROWS, columns=SAMPLE_COLUMNS)
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def sample_repository(sample_csv_path):
    return CatalogueRepository.from_csv(sample_csv_path)


@pytest.fixture
def sample_dataframe_factory(tmp_path):
    """Lets a test write an arbitrary/malformed CSV and load it."""

    def _make(rows, columns):
        path = tmp_path / "custom.csv"
        pd.DataFrame(rows, columns=columns).to_csv(path, index=False)
        return path

    return _make


@pytest.fixture
def client(sample_repository):
    app.dependency_overrides[get_catalogue_repository] = lambda: sample_repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
