from freightguard.models import DecisionStatus, FreightDocument, Location
from freightguard.workflow import process_document


def document(*, total_pay: float = 2550.0, weight_lbs: int = 45000) -> FreightDocument:
    return FreightDocument(
        carrier_name="Apex Logistics Solutions LLC",
        load_number="LD-994821",
        pickup_location=Location(city="Dallas", state="TX", zip="75201"),
        delivery_location=Location(city="Atlanta", state="GA", zip="30303"),
        total_linehaul_rate=2200.0,
        fuel_surcharge=350.0,
        total_pay=total_pay,
        weight_lbs=weight_lbs,
    )


def test_clean_document_is_approved() -> None:
    result = process_document(document())
    assert result.status is DecisionStatus.APPROVED
    assert result.findings == []


def test_source_document_is_sent_to_review() -> None:
    result = process_document(document(total_pay=2800.0, weight_lbs=46800))
    assert result.status is DecisionStatus.FLAGGED_FOR_HUMAN_REVIEW
    assert [finding.code.value for finding in result.findings] == [
        "RATE_MISMATCH",
        "OVERWEIGHT_LOAD",
    ]

