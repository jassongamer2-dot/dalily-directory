from app.services.phone_validation import validate_phone

def test_valid_mobile():
    result = validate_phone("0100 123 4567")
    assert result == {"number": "01001234567", "type": "mobile", "valid": True}

def test_invalid_short_number_flagged_not_dropped():
    result = validate_phone("012345")
    assert result["valid"] is False

def test_landline_with_area_code():
    result = validate_phone("02 2735 1234")
    assert result["type"] == "landline" and result["valid"] is True