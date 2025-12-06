# Paperwork Generation API

This FastAPI service generates loadsheets and timesheets (Excel + optional PDFs) from JSON payloads by mapping every field to the Excel templates documented in the legacy `sql_host`/`sql-to-docs` projects.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Install `libreoffice` if you need PDF output (or set `PAPERWORK_DISABLE_PDF=true` to skip conversion).
3. Ensure `templates/loadsheet.xlsx`, `templates/timesheet.xlsx`, and the signature folders (`signatures/sig1`, `signatures/sig2`) mirror the legacy structure described in `/home/craigst/Nextcloud/Documents/projects/sql_host/loadsheet.md`, `/home/craigst/Nextcloud/Documents/projects/sql_host/timesheet.md`, and `/home/craigst/Nextcloud/Documents/projects/sql-to-docs/`.
4. Configure optional environment overrides:
   - `PAPERWORK_OUTPUT_DIR` (default: `output/`)
   - `PAPERWORK_TEMPLATES_DIR`
   - `PAPERWORK_SIGNATURES_DIR` (should contain `sig1/` and `sig2/`)
   - `PAPERWORK_DISABLE_PDF` (set to `true` to skip LibreOffice)
   - `HOST`, `PORT`, `DEBUG`

## Running the API

Start the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The key endpoints are:

- `POST /api/loadsheet/generate` – supply `load_date`, `load_number`, `collection_point`, `delivery_point`, `fleet_reg`, `cars`, and optional `sig1`, `sig2`, `load_notes`.
- `POST /api/timesheet/generate` – supply `week_ending`, `driver`, `fleet_reg`, optional `weekly_total_hours`, `start_mileage`, `end_mileage`, and per-day `loads` matching the old `DayModel`/`LoadModel`.
- `GET /api/signatures` – lists images under `signatures/sig1` and `sig2`.

### Output

Files land under `output/<DD-MM-YY>/`. The folder corresponds to the Sunday of the week (`load_date` for loadsheets, `week_ending` for timesheets) as defined in `/home/craigst/Nextcloud/Documents/projects/sql_host/README_LOADSHEET.md`.

## Testing

Install the test runner and execute:

```bash
pip install pytest
pytest
```

The tests generate ephemeral workbooks beneath the configured `PAPERWORK_OUTPUT_DIR` (default `output/`). PDF conversion is skipped during tests via `PAPERWORK_DISABLE_PDF=true`.

## Docker & Deployment

Build the container:

```bash
docker build -t paperworkgen/api:latest .
```

A helper script is provided to build and push:

```bash
./scripts/build_and_push.sh paperworkgen/api:latest
```

Set `SKIP_PUSH=true` to keep the image local.

## Project Planning & References

- Workflows, mapping rules, and data models are captured in `docs/project_plan.md` (read it before extending the API).
- The legacy generators in `/home/craigst/Nextcloud/Documents/projects/sql_host/` and `/home/craigst/Nextcloud/Documents/projects/sql-to-docs/` remain the source of truth for template cells, database schema, and deployment expectations.

Use the documentation in those directories to audit payloads and ensure your JSON maps directly to the cells described in `loadsheet.md`, `timesheet.md`, `loadsheetguide.md`, and `timesheetguide.md`.
