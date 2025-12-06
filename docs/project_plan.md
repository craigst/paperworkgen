# Project Plan

## 1. High-level plan
1. Catalog the existing Excel templates and JSON contracts documented under `/home/craigst/Nextcloud/Documents/projects/sql_host/` and `/home/craigst/Nextcloud/Documents/projects/sql-to-docs/`. Those notes describe the cell mappings, load/time payloads, signature handling, and output folder strategy.
2. Strengthen the FastAPI service so it mirrors those contracts exactly, populates every template cell from the incoming JSON, safely handles signatures, and exposes deterministic outputs (Excel + optional PDF) alongside health endpoints.
3. Add reproducible tooling (tests, Dockerfile, build script, plan doc) so analysts, admins, and future AI agents can continue iterating using the referenced documentation.

## 2. Implementation tasks
- Describe the JSON-to-cell mappings alongside the plan document so developers can confirm whether `LoadsheetRequest`/`TimesheetRequest` require new fields (e.g., `load_notes`, `weekly_total_hours`) or additional validation.
- Ensure every load/time field maps to the Excel coordinates described in `loadsheet.md`, `timesheet.md`, `loadsheetguide.md`, and `timesheetguide.md`, then lock that mapping inside the helper/service layer.
- Wire in a flexible configuration layer that respects `PAPERWORK_OUTPUT_DIR`, `PAPERWORK_SIGNATURES_DIR`, and the `PAPERWORK_DISABLE_PDF` toggle, so deployments can disable LibreOffice or redirect outputs without code changes.
- Add regression tests that exercise the sample payloads (from the guides) and confirm both Excel and optional PDF metadata are returned.
- Dockerize the API with a minimal `Dockerfile` and a `scripts/build_and_push.sh` helper so the service can be rebuilt/pushed from the git-controlled workspace.
- Capture this workflow in `README.md` and this `docs/project_plan.md`, linking back to the SQL/Docs repositories for reference.

## 3. Data analyst plan
1. Use `sql_host/timesheet.md`, `sql_host/loadsheet.md`, and `sql_host/README_LOADSHEET.md` to understand how raw `DWJJOB`/`DWVVEH` rows become the JSON contracts accepted by the API and to verify any alias fields (`dwjtype`, `dwjload`, `day`, `loads`) required by controllers.
2. Refer to `sql-to-docs/data_model_guide.md` to confirm the relationships between `DWJJOB` and `DWVVEH`, their join keys (`dwvLoad`, `dwjLoad`, `dwjAdrCod`, `dwvColCod`, `dwvDelCod`), and the fields that need preservation in overrides.
3. Provide clean, ready-to-return JSON (mirroring the `loadsheetguide.md` + `timesheetguide.md` examples) so the HTTP API receives exactly what the templates expect—no transformations, no derived counts, just the data collected from dispatch tables.
4. If additional fields are required (e.g., vehicle notes or per-day messages), document them in this plan so the API validations can keep up with the dataset.

## 4. Server admin plan
1. Build the Docker image defined in `Dockerfile` and use `scripts/build_and_push.sh` to tag/push it; keep the image tagged with the git commit when deploying to production.
2. Mount the recommended folders (`templates/`, `signatures/`, `output/`) into the container/host and ensure `/home/craigst/Nextcloud/Documents/projects/sql_host/` assets remain in sync with the generation templates.
3. Install LibreOffice (or set `PAPERWORK_DISABLE_PDF=true`) within the runtime environment referenced by `n8n-install.md`/`adh-host.md` so PDF conversion works when enabled.
4. Keep an eye on `/mnt/paperwork/app/output/<DD-MM-YY>/` from the n8n workflows; the endpoints assume the same week-ending foldering strategy described in `README_LOADSHEET.md`.
5. Monitor logs for failed PDF rendering and ensure the `PAPERWORK_DISABLE_PDF` toggle is used when LibreOffice is unavailable.

## 5. Test agent plan
1. Run `pytest` against `tests/test_services.py` after any change to the helpers or schema to confirm Excel files are created and metadata in `GenerateResponse` matches expectations.
2. When PDF conversion is enabled, manually verify that `libreoffice` is callable and that the generated PDF sits alongside the Excel workbook in the `<DD-MM-YY>` folder.
3. Validate the HTTP surface manually (or with an API test suite) by sending the sample payloads from the guides to `/api/loadsheet/generate` and `/api/timesheet/generate`, ensuring the JSON-to-cell mapping behaves identically to the legacy scripts.
4. Use the `GET /api/signatures` endpoint to confirm new signature images land in `signatures/sig1` and `sig2`, and that the API can switch between random/default files.
5. Re-run `scripts/build_and_push.sh` with a dry-run tag to ensure Docker rebuild/push still works before deploying.

## 6. AI prompt
```
You are onboarding a Paperwork Generation API that mirrors the legacy load/timesheet Excel tooling described in the SQL host and sql-to-docs repositories. Follow these rules:
- Work from JSON payloads that already include every field mentioned in loadsheet.md, timesheet.md, loadsheetguide.md, and timesheetguide.md—do not invent derived values such as total hours or vehicle counts unless the payload omits them and the templates expect them.
- Place every value in the cell described by those guides, keep signature handling optional/random via `signatures/sig1`/`sig2`, and store outputs under `output/<DD-MM-YY>/` where `<DD-MM-YY>` is the Sunday of the provided week date.
- Respect the environment flags (`PAPERWORK_OUTPUT_DIR`, `PAPERWORK_SIGNATURES_DIR`, `PAPERWORK_DISABLE_PDF`) and add coverage in tests/docs whenever you extend the schema or helpers.
- Review `docs/project_plan.md` before proposing large structural changes, and always reference the SQL docs for data expectations.
```
