from app.services.pricing import compare_prices, get_same_ingredient_alternatives


def test_same_ingredient_alternatives_excludes_self_and_unrelated_ingredients(sample_repository):
    medicine = sample_repository.get_by_id("TESTX001")
    alternatives = get_same_ingredient_alternatives(sample_repository, medicine)
    ids = {a.medicine_id for a in alternatives}

    assert "TESTX001" not in ids  # excludes itself
    assert ids == {"TESTX002", "TESTX003", "TESTX004"}  # same active ingredient
    assert "TESTZ001" not in ids  # different active ingredient must never appear


def test_price_comparison_finds_lowest_price_and_difference(sample_repository):
    medicine = sample_repository.get_by_id("TESTX001")  # price 100.0
    alternatives = get_same_ingredient_alternatives(sample_repository, medicine)
    comparison = compare_prices(medicine, alternatives)

    assert comparison.current_price == 100.0
    assert comparison.lowest_price == 80.0
    assert comparison.lowest_price_medicine_id == "TESTX003"
    assert comparison.price_difference == 20.0


def test_pack_size_is_preserved_in_comparison(sample_repository):
    medicine = sample_repository.get_by_id("TESTX001")
    alternatives = get_same_ingredient_alternatives(sample_repository, medicine)
    comparison = compare_prices(medicine, alternatives)

    assert comparison.current_pack_size == "10's"
    assert comparison.lowest_price_pack_size == "10's"
    assert all(a.pack_size for a in alternatives)


def test_missing_price_is_excluded_not_treated_as_zero(sample_repository):
    medicine = sample_repository.get_by_id("TESTX004")  # price is None
    alternatives = get_same_ingredient_alternatives(sample_repository, medicine)
    comparison = compare_prices(medicine, alternatives)

    assert comparison.current_price is None
    # lowest price among alternatives (100, 150, 80) must be 80, never 0
    assert comparison.lowest_price == 80.0
    # current price unavailable -> difference cannot be computed
    assert comparison.price_difference is None


def test_medicine_category_comes_from_catalogue_field(sample_repository):
    antibiotic = sample_repository.get_by_id("TESTX001")
    non_antibiotic = sample_repository.get_by_id("TESTZ001")

    assert antibiotic.medicine_category == "Antibiotic"
    assert non_antibiotic.medicine_category == "Non-antibiotic"
