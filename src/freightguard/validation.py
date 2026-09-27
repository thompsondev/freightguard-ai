"""Deterministic freight rules. No model calls belong in this module."""

from decimal import Decimal

from freightguard.models import (
    FindingCode,
    FreightDocument,
    Severity,
    ValidationFinding,
)

CENT = Decimal("0.01")
MAX_WEIGHT_LBS = 45_000
AMBIGUOUS_VALUES = {"", "unknown", "unclear", "ambiguous", "n/a", "not provided", "missing"}


def _money(value: float) -> Decimal:
    # Convert through str so binary floating-point noise cannot create a false mismatch.
    return Decimal(str(value)).quantize(CENT)


def _is_missing(value: str) -> bool:
    return value.strip().casefold() in AMBIGUOUS_VALUES


def validate_document(document: FreightDocument) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []

    expected_total = _money(document.total_linehaul_rate) + _money(document.fuel_surcharge)
    reported_total = _money(document.total_pay)
    if expected_total != reported_total:
        difference = reported_total - expected_total
        findings.append(
            ValidationFinding(
                code=FindingCode.RATE_MISMATCH,
                severity=Severity.ERROR,
                message=(
                    f"Linehaul plus fuel is ${expected_total:,.2f}, but total pay is "
                    f"${reported_total:,.2f} (difference: ${difference:,.2f})."
                ),
            )
        )

    if document.weight_lbs > MAX_WEIGHT_LBS:
        excess = document.weight_lbs - MAX_WEIGHT_LBS
        findings.append(
            ValidationFinding(
                code=FindingCode.OVERWEIGHT_LOAD,
                severity=Severity.WARNING,
                message=(
                    f"Load weight is {document.weight_lbs:,} lbs, which is {excess:,} lbs "
                    f"over the {MAX_WEIGHT_LBS:,} lb review threshold."
                ),
            )
        )

    # Structured Outputs guarantees these keys exist, but an unsupported or ambiguous
    # value is deliberately represented as an empty string and still needs review.
    required_text = {
        "carrier_name": document.carrier_name,
        "load_number": document.load_number,
        "pickup_location.city": document.pickup_location.city,
        "pickup_location.state": document.pickup_location.state,
        "pickup_location.zip": document.pickup_location.zip,
        "delivery_location.city": document.delivery_location.city,
        "delivery_location.state": document.delivery_location.state,
        "delivery_location.zip": document.delivery_location.zip,
    }
    missing = [name for name, value in required_text.items() if _is_missing(value)]
    if missing:
        findings.append(
            ValidationFinding(
                code=FindingCode.INCOMPLETE_DATA,
                severity=Severity.ERROR,
                message=f"Required data is missing or ambiguous: {', '.join(missing)}.",
            )
        )

    return findings
