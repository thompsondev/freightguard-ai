import json
from pathlib import Path

from freightguard.cli import main
from freightguard.io import read_document


def test_read_text_document(tmp_path: Path) -> None:
    source = tmp_path / "load.txt"
    source.write_text("Ref: LD-1", encoding="utf-8")
    assert read_document(source) == "Ref: LD-1"


def test_missing_document_has_clear_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    try:
        read_document(missing)
    except FileNotFoundError as exc:
        assert str(missing) in str(exc)
    else:
        raise AssertionError("read_document should reject a missing file")


def test_validate_command_prints_decision(tmp_path: Path, capsys: object) -> None:
    payload = {
        "carrier_name": "Apex Logistics Solutions LLC",
        "load_number": "LD-994821",
        "pickup_location": {"city": "Dallas", "state": "TX", "zip": "75201"},
        "delivery_location": {"city": "Atlanta", "state": "GA", "zip": "30303"},
        "total_linehaul_rate": 2200.0,
        "fuel_surcharge": 350.0,
        "total_pay": 2800.0,
        "weight_lbs": 46800,
    }
    source = tmp_path / "extracted.json"
    source.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["validate", str(source)]) == 0
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert '"status": "FLAGGED_FOR_HUMAN_REVIEW"' in output
    assert '"code": "RATE_MISMATCH"' in output


def test_validate_command_rejects_bad_json(tmp_path: Path, capsys: object) -> None:
    source = tmp_path / "bad.json"
    source.write_text("not json", encoding="utf-8")

    assert main(["validate", str(source)]) == 1
    assert "error:" in capsys.readouterr().err  # type: ignore[attr-defined]
