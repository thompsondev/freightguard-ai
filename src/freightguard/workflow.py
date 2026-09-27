"""Turn extracted data and rule findings into an operational decision."""

from freightguard.models import DecisionStatus, FreightDocument, ProcessingResult
from freightguard.validation import validate_document


def process_document(document: FreightDocument) -> ProcessingResult:
    findings = validate_document(document)
    if not findings:
        return ProcessingResult(
            status=DecisionStatus.APPROVED,
            summary="All required data is present and every business rule passed.",
            findings=[],
            document=document,
        )

    codes = ", ".join(finding.code.value for finding in findings)
    return ProcessingResult(
        status=DecisionStatus.FLAGGED_FOR_HUMAN_REVIEW,
        summary=f"Human review required: {codes}.",
        findings=findings,
        document=document,
    )

