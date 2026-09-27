from freightguard.models import FindingCode, FreightDocument, Location, Severity
from freightguard.validation import validate_document


def freight_document(**overrides: object) -> FreightDocument:
    values = {
        "carrier_name": "Apex Logistics Solutions LLC",
        "load_number": "LD-994821",
        "pickup_location": Location(city="Dallas", state="TX", zip="75201"),
        "delivery_location": Location(city="Atlanta", state="GA", zip="30303"),
        "total_linehaul_rate": 2200.0,
        "fuel_surcharge": 350.0,
        "total_pay": 2550.0,
        "weight_lbs": 45000,
    }
    values.update(overrides)
    return FreightDocument(**values)


def test_valid_document_has_no_findings() -> None:
    assert validate_document(freight_document()) == []


def test_rate_mismatch_reports_exact_difference() -> None:
    findings = validate_document(freight_document(total_pay=2800.0))
    assert findings[0].code is FindingCode.RATE_MISMATCH
    assert findings[0].severity is Severity.ERROR
    assert "$250.00" in findings[0].message


def test_overweight_load_is_warning() -> None:
    findings = validate_document(freight_document(weight_lbs=46800))
    assert findings[0].code is FindingCode.OVERWEIGHT_LOAD
    assert findings[0].severity is Severity.WARNING
    assert "1,800 lbs" in findings[0].message


def test_blank_location_is_incomplete() -> None:
    pickup = Location(city="", state="TX", zip="75201")
    findings = validate_document(freight_document(pickup_location=pickup))
    assert findings[0].code is FindingCode.INCOMPLETE_DATA
    assert "pickup_location.city" in findings[0].message

