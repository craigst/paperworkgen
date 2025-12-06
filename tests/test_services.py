import datetime
from pathlib import Path

import pytest

from app.config import settings
from app.schemas import (
    CarModel,
    DayModel,
    LoadModel,
    LoadsheetRequest,
    TimesheetRequest,
)
from app.services.loadsheet import generate_loadsheet
from app.services.timesheet import generate_timesheet


@pytest.fixture(autouse=True)
def disable_pdf(monkeypatch):
    monkeypatch.setenv("PAPERWORK_DISABLE_PDF", "true")


@pytest.fixture
def use_temp_output(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "output_dir", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_generate_loadsheet_creates_workbook(use_temp_output):
    request = LoadsheetRequest(
        load_date="2025-05-17",
        load_number="$S123456",
        collection_point="WBAC Maidstone",
        delivery_point="BTT Yard",
        fleet_reg="Y6BTT",
        load_notes="Sample manifest",
        cars=[
            CarModel(
                reg="AB12CDE",
                make_model="Ford Focus",
                offloaded="N",
                docs="Y",
                spare_keys="Y",
                car_notes="Clean"
            ),
            CarModel(
                reg="XY34ZRT",
                make_model="Vauxhall Corsa",
                offloaded="Y",
                docs="N",
                spare_keys="N",
                car_notes="Offloaded at depot"
            ),
        ],
    )

    result = generate_loadsheet(request)
    excel_path = Path(result.excel_path)
    assert excel_path.exists(), "Expected Excel file to exist"
    assert result.pdf_path is None
    assert result.week_folder == datetime.datetime(2025, 5, 18).strftime("%d-%m-%y")


def test_generate_timesheet_writes_days(use_temp_output):
    request = TimesheetRequest(
        week_ending="2025-05-18",
        driver="Craig Example",
        fleet_reg=["Y6BTT", "ZZ1234"],
        start_mileage="12000",
        end_mileage="12050",
        weekly_total_hours="16.5",
        days=[
            DayModel(
                day="Monday",
                start_time="07:00",
                finish_time="16:00",
                total_hours="9",
                loads=[
                    LoadModel(
                        customer="WBAC Maidstone",
                        car_count=2,
                        collection="WBAC Maidstone",
                        delivery="BTT Yard",
                        note="Docs onboard",
                    )
                ],
            ),
            DayModel(
                day="Tuesday",
                start_time="08:00",
                finish_time="14:30",
                total_hours="7.5",
                loads=[],
            ),
        ],
    )

    result = generate_timesheet(request)
    excel_path = Path(result.excel_path)
    assert excel_path.exists()
    assert result.pdf_path is None
    assert result.week_folder == datetime.datetime(2025, 5, 18).strftime("%d-%m-%y")
