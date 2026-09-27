"""Typed contracts shared by extraction, validation, and workflow code."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Location(StrictModel):
    city: str = Field(description="City exactly as supported by the document")
    state: str = Field(description="Two-letter US state abbreviation")
    zip: str = Field(description="Five-digit ZIP code, retained as text")


class FreightDocument(StrictModel):
    carrier_name: str
    load_number: str
    pickup_location: Location
    delivery_location: Location
    total_linehaul_rate: float = Field(ge=0)
    fuel_surcharge: float = Field(ge=0)
    total_pay: float = Field(ge=0)
    weight_lbs: int = Field(ge=0)


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


class FindingCode(str, Enum):
    RATE_MISMATCH = "RATE_MISMATCH"
    OVERWEIGHT_LOAD = "OVERWEIGHT_LOAD"
    INCOMPLETE_DATA = "INCOMPLETE_DATA"


class ValidationFinding(StrictModel):
    code: FindingCode
    severity: Severity
    message: str


class DecisionStatus(str, Enum):
    APPROVED = "APPROVED"
    FLAGGED_FOR_HUMAN_REVIEW = "FLAGGED_FOR_HUMAN_REVIEW"


class ProcessingResult(StrictModel):
    status: DecisionStatus
    summary: str
    findings: list[ValidationFinding]
    document: FreightDocument

