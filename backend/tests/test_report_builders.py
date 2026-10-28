from app.routers.reports import _make_csv, _make_pdf


def sample_payload():
    return {
        "report_info": {"generated_at": "2026-01-01T00:00:00+00:00", "report_scope": "Metadata only"},
        "case": {"case_id": "sample", "case_name": "Test <case>", "imaging_modality": "CCTA", "anatomical_region": "Coronary arteries", "scan_date": None, "notes": "=1+1", "case_status": "Pending", "created_at": None, "updated_at": None},
        "images": [], "analysis_results": [], "history": [],
    }


def test_csv_sanitizes_spreadsheet_formula_prefix():
    content = _make_csv(sample_payload()).decode("utf-8-sig")
    assert "'=1+1" in content
    assert "No diagnostic findings" in content


def test_pdf_is_non_empty_and_contains_pdf_signature():
    content = _make_pdf(sample_payload())
    assert content.startswith(b"%PDF-")
    assert len(content) > 1000
