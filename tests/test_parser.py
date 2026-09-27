from types import SimpleNamespace

import pytest

from freightguard.models import FreightDocument, Location
from freightguard.parser import DocumentParsingError, OpenAIFreightParser


class FakeResponses:
    def __init__(self, output: FreightDocument | None) -> None:
        self.output = output

    def parse(self, **_: object) -> SimpleNamespace:
        return SimpleNamespace(output_parsed=self.output)


class FakeClient:
    def __init__(self, output: FreightDocument | None) -> None:
        self.responses = FakeResponses(output)


def extracted_document() -> FreightDocument:
    return FreightDocument(
        carrier_name="Apex Logistics Solutions LLC",
        load_number="LD-994821",
        pickup_location=Location(city="Dallas", state="TX", zip="75201"),
        delivery_location=Location(city="Atlanta", state="GA", zip="30303"),
        total_linehaul_rate=2200.0,
        fuel_surcharge=350.0,
        total_pay=2800.0,
        weight_lbs=46800,
    )


def test_parser_returns_typed_model() -> None:
    expected = extracted_document()
    parser = OpenAIFreightParser(client=FakeClient(expected))  # type: ignore[arg-type]
    assert parser.parse("freight document") == expected


def test_empty_input_never_calls_model() -> None:
    parser = OpenAIFreightParser(client=FakeClient(None))  # type: ignore[arg-type]
    with pytest.raises(DocumentParsingError, match="empty"):
        parser.parse("  ")


def test_missing_structured_output_is_an_error() -> None:
    parser = OpenAIFreightParser(client=FakeClient(None))  # type: ignore[arg-type]
    with pytest.raises(DocumentParsingError, match="no structured"):
        parser.parse("freight document")

