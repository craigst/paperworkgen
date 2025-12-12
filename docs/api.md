# API Documentation

## Common response

Both generation endpoints return `GenerateResponse`:

```json
{
  "excel_path": "output/07-12-25/$S355049_WBAC_Maidstone.xlsx",
  "pdf_path": "output/07-12-25/$S355049_WBAC_Maidstone.pdf",
  "message": "Loadsheet generated successfully",
  "week_folder": "07-12-25"
}
```

`pdf_path` is `null` when PDF conversion was skipped or failed; set `include_pdf` to `false` to skip LibreOffice intentionally.

## POST /api/loadsheet/generate

### Description
Generate a loadsheet workbook (and optional PDF) by mapping each car entry to the cells described in [`docs/cell_mapping.md`](cell_mapping.md).

### Request body

```json
{
  "load_date": "2025-12-01",
  "load_number": "$S355049",
  "collection_point": "WBAC Maidstone",
  "delivery_point": "BTT Yard",
  "fleet_reg": "Y6BTT",
  "load_notes": "Docs on passenger seat",
  "cars": [
    {
      "reg": "AB12CDE",
      "make_model": "Ford Focus",
      "offloaded": "N",
      "docs": "Y",
      "spare_keys": "Y",
      "car_notes": "Clean condition"
    },
    {
      "reg": "XY34ZRT",
      "make_model": "Vauxhall Corsa",
      "offloaded": "Y",
      "docs": "N",
      "spare_keys": "N",
      "car_notes": "Offloaded at depot"
    }
  ]
}
```

### Notes
- `include_pdf` controls whether LibreOffice runs; set to `false` or use `PAPERWORK_DISABLE_PDF=true` if the runtime lacks LibreOffice.
- `sig1`/`sig2` accept `"random"` to pull from `signatures/sig1`/`sig2` or a direct path to an image.
- The repository`s `docs/cell_mapping.md` captures the JSON-to-cell mapping for every field listed above.

## GET /api/settings

Returns non-secret runtime configuration (host, port, directories, PDF toggle).

```json
{
  "host": "::",
  "port": 8000,
  "output_dir": "/app/output",
  "templates_dir": "/app/templates",
  "signatures_dir": "/app/signatures",
  "pdf_enabled": true,
  "api_version": "1.0.0",
  "message": "Current settings"
}
```

## POST /api/settings

Update runtime settings (currently limited to the PDF toggle; host/port changes still require a restart).

```json
{
  "pdf_enabled": false,
  "reset_pdf_override": false
}
```

Set `pdf_enabled` to override the runtime PDF toggle, or send `{"reset_pdf_override": true}` to fall back to the environment value `PAPERWORK_DISABLE_PDF`.

## POST /api/timesheet/generate

### Description
Fill the weekly timesheet template by enumerating every day, loads, hours, and fleet regs sent by n8n.

### Request body

```json
{
  "week_ending": "2025-05-18",
  "driver": "Craig Example",
  "fleet_reg": ["Y6BTT", "ZZ1234"],
  "start_mileage": "12000",
  "end_mileage": "12050",
  "weekly_total_hours": "16.5",
  "days": [
    {
      "day": "Monday",
      "start_time": "07:00",
      "finish_time": "16:00",
      "total_hours": "9",
      "loads": [
        {
          "customer": "WBAC Maidstone",
          "car_count": 2,
          "collection": "WBAC Maidstone",
          "delivery": "BTT Yard",
          "note": "Docs onboard"
        }
      ]
    },
    {
      "day": "Tuesday",
      "start_time": "08:00",
      "finish_time": "14:30",
      "total_hours": "7.5",
      "loads": []
    }
  ]
}
```

### Notes
- Each `day` can include up to three loads; extras spill into rows 29+ in the template (see `docs/cell_mapping.md` for the overflow mapping).
- Use `"message": "SICK"` inside the `loads` array to render a stand-alone message row instead of contractor data.
- `fleet_reg` accepts a string or list (the schema normalizes to uppercase strings internally).
