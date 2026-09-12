from app.models.schemas import NOT_FOUND_MESSAGE


def test_post_prescription_found(client):
    resp = client.post(
        "/prescription",
        json={
            "patient_id": "P001",
            "diagnosis": "Bacterial infection",
            "medicine": "BrandA",
            "dosage": "100mg",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "FOUND"
    assert body["medicine"]["medicine_id"] == "TESTX001"

    alt_ids = {a["medicine_id"] for a in body["alternatives"]}
    assert alt_ids == {"TESTX005", "TESTX006", "TESTX007"}

    comparison = body["price_comparison"]
    assert comparison["comparison_basis"] == "UNIT_PRICE"
    assert comparison["lowest_unit_price"] == 7.5
    assert comparison["lowest_unit_price_medicine_id"] == "TESTX005"
    assert comparison["lowest_pack_price"] == 90.0
    assert comparison["lowest_pack_price_medicine_id"] == "TESTX006"


def test_post_prescription_not_found(client):
    resp = client.post(
        "/prescription",
        json={
            "patient_id": "P001",
            "diagnosis": "Bacterial infection",
            "medicine": "TotallyUnknownMedicine",
            "dosage": "500mg",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "NOT_FOUND"
    assert body["message"] == NOT_FOUND_MESSAGE
    assert body["medicine"] is None
    assert body["alternatives"] == []
    assert body["price_comparison"] is None


def test_post_prescription_ambiguous(client):
    resp = client.post(
        "/prescription",
        json={
            "patient_id": "P001",
            "diagnosis": "Bacterial infection",
            "medicine": "BrandA",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "AMBIGUOUS"
    assert body["medicine"] is None
    assert len(body["candidates"]) == 2


def test_get_medicine_success(client):
    resp = client.get("/medicine/TESTX001")
    assert resp.status_code == 200
    body = resp.json()
    assert body["brand_name"] == "BrandA"
    assert body["medicine_category"] == "Antibiotic"


def test_get_medicine_not_found(client):
    resp = client.get("/medicine/DOES_NOT_EXIST")
    assert resp.status_code == 404
    assert resp.json()["detail"] == NOT_FOUND_MESSAGE


def test_get_alternatives_success(client):
    resp = client.get("/alternatives/TESTX001")
    assert resp.status_code == 200
    body = resp.json()
    assert body["active_ingredient"] == "IngredientX"
    assert body["strength"] == "100mg"
    assert body["dosage_form"] == "Tablet"
    ids = {a["medicine_id"] for a in body["alternatives"]}
    assert ids == {"TESTX005", "TESTX006", "TESTX007"}
    assert body["price_comparison"]["lowest_unit_price"] == 7.5


def test_get_alternatives_not_found(client):
    resp = client.get("/alternatives/DOES_NOT_EXIST")
    assert resp.status_code == 404
    assert resp.json()["detail"] == NOT_FOUND_MESSAGE
