# Paperwork Generation API - Project Status & Tasks

> **Last Updated**: 2025-12-12 01:43:40 UTC  
> **Status**: ✅ Core Implementation Complete - IPv6 binding updated (retest pending)

---

## 🤖 AI Agent Instructions

**READ THIS FIRST**: This file tracks the current state of the Paperwork Generation API project. 

### For AI Agents Working on This Project:

1. **Read this entire file** before starting any work
2. **Update this file** after completing tasks, fixing bugs, or identifying issues
3. **Mark tasks as complete** by changing `- [ ]` to `- [x]`
4. **Add new issues** to the "Known Issues" section as you discover them
5. **Update the "Last Updated" timestamp** at the top
6. **Document all commands** you use in the relevant sections

---

## 📋 Project Overview

**Name**: Paperwork Generation HTTP API  
**Purpose**: FastAPI service that generates Excel and PDF loadsheets/timesheets from JSON input  
**Repository**: https://github.com/craigst/paperworkgen  
**Docker Image**: `ghcr.io/craigst/paperworkgen:latest`  
**Remote Server**: craigst@10.10.254.81

### Architecture
- **Backend**: FastAPI (Python 3.12)
- **Excel Processing**: openpyxl
- **PDF Generation**: LibreOffice (headless)
- **Containerization**: Docker/Podman
- **CI/CD**: GitHub Actions

---

## ✅ Completed Tasks

- [x] Set up project structure with FastAPI
- [x] Create Pydantic schemas for loadsheet and timesheet
- [x] Implement loadsheet generation service
- [x] Implement timesheet service
- [x] Create Excel template cell mapping
- [x] Add signature handling (random selection or custom path)
- [x] Set up Dockerfile with LibreOffice
- [x] Configure GitHub Actions for Docker builds
- [x] Create API endpoints (/api/loadsheet/generate, /api/timesheet/generate, /api/health)
- [x] Copy Excel templates from reference projects
- [x] Copy signature images from reference projects
- [x] Initialize Git repository
- [x] Test Docker build locally
- [x] Verify container starts successfully
- [x] Confirm API responds (via IPv4)

---

## 🔄 Current Tasks

### High Priority
- [x] Fix IPv6 networking issue in container (uvicorn now binds to `::` by default)
- [x] Test loadsheet generation with sample JSON data (service-layer pytest inside Docker; PDF disabled)
- [x] Test timesheet generation with sample JSON data (service-layer pytest inside Docker; PDF disabled)
- [ ] Verify PDF generation works correctly
- [x] Deploy fixed container to remote server (10.10.254.81)

### Medium Priority
- [ ] Create comprehensive API tests
- [ ] Add error handling for missing templates
- [ ] Implement logging for PDF conversion failures
- [ ] Create docker-compose.yml for easy local development
- [ ] Write API usage examples in documentation
- [x] Add runtime settings endpoints (GET current config: host/port/output/templates/signatures/pdf_enabled; POST toggle PDF and reset to env)

### Low Priority
- [ ] Add support for more than 8 cars in loadsheet
- [ ] Implement batch processing endpoint
- [ ] Add webhook notifications for completed paperwork
- [ ] Create web UI for manual testing

---

## ⚠️ Known Issues

### 1. IPv6 Networking Problem (HIGH PRIORITY)
**Status**: Fix implemented—uvicorn now binds to `::` by default in Docker; redeploy and retest IPv6  
**Symptom**: Previous container builds reset IPv6 (::1) connections  
**Workaround**: Use IPv4 explicitly with `curl -4` until the new image is deployed  
**Impact**: Prevented normal API access without forcing IPv4 (should be resolved after redeploy)

**Next Steps**:
- Rebuild/push the image with the updated Dockerfile and deploy to 10.10.254.81
- After deploy, retest IPv6 endpoints; set `HOST=0.0.0.0` only if the runtime lacks IPv6 support

### 2. Remote Server Container Not Running
**Status**: Container stopped/removed  
**Location**: 10.10.254.81  
**Last Known State**: Crash loop due to ModuleNotFoundError (now fixed in latest build)

### 3. Local Python 3.13 environment dependency failure
**Status**: New  
**Symptom**: `pip install -r requirements.txt` fails while building `pydantic-core` on Python 3.13  
**Workaround**: Use Python 3.12 (matches Docker base image) or run tests via `docker build --target test .`  
**Impact**: Local virtualenvs on Python 3.13 cannot install dependencies without an alternate runtime

### 4. Docker healthcheck script failing on remote deployment
**Status**: Update staged (pending redeploy)  
**Symptom**: Healthcheck failing in swarm because `curl` not present in image; prior version also hit `SyntaxError` on Python heredoc  
**Fix**: Healthcheck now uses built-in Python: `python -c "import sys,urllib.request; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/api/health',timeout=5).status==200 else sys.exit(1)"` in `docker-compose.yml`  
**Action**: Manual `docker run` deployed on 10.10.254.81 with HOST=0.0.0.0; compose/swarm not available on host. Health OK via curl after redeploy.  
**Impact**: Compose file not applied; host needs docker-compose plugin or swarm init to use the compose healthcheck in future.

---

## 🧪 Testing Checklist

### Docker Build & Run
- [x] Build image locally: `podman build -t paperworkgen:test .`
- [x] Run container: `podman run -d -p 8000:8000 paperworkgen:test`
- [x] Container starts without errors
- [x] Uvicorn starts successfully
- [x] Logs show clean startup

### API Endpoints
- [x] Root endpoint: `curl -4 http://localhost:8000/`
- [x] Health endpoint: `curl -4 http://localhost:8000/api/health`
- [x] Settings endpoint: `curl -4 http://localhost:8000/api/settings`
- [x] Remote health endpoint: `curl http://10.10.254.81:8000/api/health`
- [ ] Loadsheet generation: `curl -4 -X POST http://localhost:8000/api/loadsheet/generate -H "Content-Type: application/json" -d @test_loadsheet.json`
- [ ] Timesheet generation: `curl -4 -X POST http://localhost:8000/api/timesheet/generate -H "Content-Type: application/json" -d @test_timesheet.json`
- [ ] Signatures list: `curl -4 http://localhost:8000/api/signatures`
- [ ] API documentation: `curl -4 http://localhost:8000/docs`

### PDF Generation
- [ ] Verify LibreOffice is installed in container
- [ ] Test Excel to PDF conversion
- [ ] Confirm PDF output is readable
- [ ] Check PDF file size is reasonable

### File Generation
- [x] Verify Excel files are created in output directory (pytest in Docker test stage)
- [x] Confirm correct week folder structure (DD-MM-YY) (validated in pytest for loadsheet/timesheet)
- [ ] Check Excel files open correctly
- [ ] Validate cell mapping is accurate
- [ ] Confirm signatures are embedded correctly

---

## 🧾 Commands Run This Update

- `source .venv/bin/activate && pytest` (failed: missing dependencies for `app` imports)
- `source .venv/bin/activate && PYTHONPATH=. pytest` (failed: `pydantic` unavailable on local Python 3.13)
- `source .venv/bin/activate && pip install -r requirements.txt` (failed building `pydantic-core` on Python 3.13)
- `docker build --target test .` (passes pytest inside Python 3.12 container; PDF disabled)
- `ssh craigst@10.10.254.81 "mkdir -p ~/paperworkgen/output ~/paperworkgen/templates ~/paperworkgen/signatures/sig1 ~/paperworkgen/signatures/sig2"` (create bind mount targets)
- `ssh craigst@10.10.254.81 "docker ps"` (verify container health)
- `ssh craigst@10.10.254.81 "curl -s -o /dev/null -w '%{http_code}\\n' http://localhost:8000/api/health"` (API responding 200 despite failing healthcheck)
- `date -u +"%Y-%m-%d %H:%M:%S UTC"` (timestamp updates)
- `docker build --target test .` (passes pytest inside Python 3.12 container; includes new settings endpoint tests)
- `docker build -t ghcr.io/craigst/paperworkgen:latest .` (build runtime image with settings endpoints)
- `docker save ghcr.io/craigst/paperworkgen:latest | ssh craigst@10.10.254.81 "docker load"` (load new image on remote)
- `scp docker-compose.yml craigst@10.10.254.81:/home/craigst/paperworkgen/` (sync compose file)
- `ssh craigst@10.10.254.81 "docker stop btt-paperwork-paperworkgen-1 && docker rm btt-paperwork-paperworkgen-1"` (remove old container)
- `ssh craigst@10.10.254.81 "docker run -d --name paperworkgen-app --restart unless-stopped -p 8000:8000 -e HOST='0.0.0.0' -e PORT=8000 -e PAPERWORK_OUTPUT_DIR=/app/output -e PAPERWORK_TEMPLATES_DIR=/app/templates -e PAPERWORK_SIGNATURES_DIR=/app/signatures -v /home/craigst/paperworkgen/output:/app/output -v /home/craigst/paperworkgen/templates:/app/templates -v /home/craigst/paperworkgen/signatures:/app/signatures ghcr.io/craigst/paperworkgen:latest"` (deploy new image manually; host lacks compose/swarm)
- `ssh craigst@10.10.254.81 "curl -s -o /dev/null -w '%{http_code}\\n' http://localhost:8000/api/health"` and `curl -f http://10.10.254.81:8000/api/health` (verify health 200)

---

## 🚀 Deployment Commands

### Local Development

```bash
# Build Docker image
cd paperworkgen
podman build -t paperworkgen:test .

# Run container
podman run -d --name paperworkgen-test -p 8000:8000 localhost/paperworkgen:test

# View logs
podman logs paperworkgen-test

# Stop container
podman stop paperworkgen-test

# Remove container
podman rm paperworkgen-test

# Clean up
podman rmi localhost/paperworkgen:test
```

### GitHub Actions (Automatic)

GitHub Actions automatically builds and pushes to `ghcr.io/craigst/paperworkgen:latest` on push to master branch.

**Workflow file**: `.github/workflows/docker-publish.yml`

```bash
# Trigger build by pushing to master
git add .
git commit -m "Your commit message"
git push origin master

# Monitor build at: https://github.com/craigst/paperworkgen/actions
```

### Manual Docker Registry Push

```bash
# Build for multiple architectures
podman build --platform linux/amd64,linux/arm64 -t ghcr.io/craigst/paperworkgen:latest .

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | podman login ghcr.io -u craigst --password-stdin

# Push image
podman push ghcr.io/craigst/paperworkgen:latest
```

### Remote Server Deployment

```bash
# SSH to remote server
ssh craigst@10.10.254.81

# Pull latest image
docker pull ghcr.io/craigst/paperworkgen:latest

# Stop old container (if exists)
docker stop btt-paperwork-paperwork-1
docker rm btt-paperwork-paperwork-1

# Run new container
docker run -d \
  --name paperwork-api \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /path/to/output:/app/output \
  -v /path/to/templates:/app/templates \
  -v /path/to/signatures:/app/signatures \
  ghcr.io/craigst/paperworkgen:latest

# Check logs
docker logs paperwork-api

# Check status
docker ps | grep paperwork
```

### Testing Remote Deployment

```bash
# From local machine
ssh craigst@10.10.254.81 "curl -4 http://localhost:8000/api/health"

# Or via public IP (if exposed)
curl -4 http://10.10.254.81:8000/api/health
```

---

## 📝 API Usage Examples

### Test Loadsheet Generation

Create `test_loadsheet.json`:
```json
{
  "load_date": "2025-12-12",
  "load_number": "$S123456",
  "collection_point": "WBAC Maidstone",
  "delivery_point": "BTT Yard",
  "fleet_reg": "Y6BTT",
  "sig1": "random",
  "sig2": "random",
  "cars": [
    {
      "reg": "AB12CDE",
      "make_model": "Ford Focus",
      "offloaded": "N",
      "docs": "Y",
      "spare_keys": "Y",
      "car_notes": "Clean vehicle"
    },
    {
      "reg": "CD34EFG",
      "make_model": "Vauxhall Astra",
      "offloaded": "N",
      "docs": "N",
      "spare_keys": "Y",
      "car_notes": "Docs with office"
    }
  ]
}
```

Test:
```bash
curl -4 -X POST http://localhost:8000/api/loadsheet/generate \
  -H "Content-Type: application/json" \
  -d @test_loadsheet.json | jq .
```

### Test Timesheet Generation

Create `test_timesheet.json`:
```json
{
  "week_ending": "2025-12-14",
  "driver": "CRAIG",
  "fleet_reg": "Y6BTT",
  "start_mileage": "12500",
  "end_mileage": "12820",
  "sig1": "random",
  "sig2": "random",
  "days": [
    {
      "day": "Monday",
      "start_time": "07:30",
      "finish_time": "16:15",
      "total_hours": "8.75",
      "loads": [
        {
          "customer": "WBAC",
          "car_count": 2,
          "collection": "Didcot",
          "delivery": "BTT Yard"
        }
      ]
    },
    {
      "day": "Tuesday",
      "start_time": "07:00",
      "finish_time": "15:30",
      "total_hours": "8.5",
      "loads": [
        {
          "customer": "WBAC",
          "car_count": 3,
          "collection": "Crawley",
          "delivery": "BTT Yard"
        }
      ]
    }
  ]
}
```

Test:
```bash
curl -4 -X POST http://localhost:8000/api/timesheet/generate \
  -H "Content-Type: application/json" \
  -d @test_timesheet.json | jq .
```

---

## 📚 Reference Documentation

- **API Documentation**: `/docs` endpoint (Swagger UI)
- **Cell Mapping**: `docs/cell_mapping.md`
- **Project Plan**: `docs/project_plan.md`
- **API Reference**: `docs/api.md`

### Original Reference Projects
- `/home/craigst/Nextcloud/Documents/projects/sql_host/`
- `/home/craigst/Nextcloud/Documents/projects/sql-to-docs/`

---

## 🔧 Troubleshooting

### Container Won't Start
```bash
# Check logs
podman logs paperworkgen-test

# Common issues:
# 1. Port already in use - change port mapping
# 2. Missing templates - check volume mounts
# 3. Permission issues - check file ownership
```

### API Not Responding
```bash
# Force IPv4
curl -4 http://localhost:8000/api/health

# Check if container is running
podman ps | grep paperwork

# Check port mapping
podman port paperworkgen-test
```

### PDF Generation Fails
```bash
# Verify LibreOffice is installed
podman exec paperworkgen-test which libreoffice

# Check LibreOffice version
podman exec paperworkgen-test libreoffice --version

# Test manual conversion
podman exec paperworkgen-test libreoffice --headless --convert-to pdf test.xlsx
```

---

## 🎯 Success Criteria

The project is considered complete when:

- [ ] IPv6 networking issue is resolved
- [ ] API responds without requiring `-4` flag
- [ ] Loadsheet generation works end-to-end (JSON → Excel → PDF)
- [ ] Timesheet generation works end-to-end (JSON → Excel → PDF)
- [ ] Container runs successfully on remote server (10.10.254.81)
- [ ] All API endpoints return appropriate responses
- [ ] Error handling is comprehensive
- [ ] Documentation is complete and accurate
- [ ] CI/CD pipeline successfully builds and deploys

---

## 📞 Key Information

**Git Repository**: `/home/craigst/Nextcloud/Documents/projects/paperworkgen/paperworkgen`  
**Docker Registry**: `ghcr.io/craigst/paperworkgen`  
**Remote Server**: `craigst@10.10.254.81`  
**Container Port**: `8000`  
**Template Location**: `/app/templates/`  
**Output Location**: `/app/output/`  
**Signature Location**: `/app/signatures/`

---

## 🤖 AI Agent Update Protocol

When updating this file:

1. Update the "Last Updated" timestamp at the top
2. Mark completed tasks with `[x]`
3. Add new issues to "Known Issues" with detailed descriptions
4. Document any new commands you used
5. Update testing checklists with results
6. Add troubleshooting steps for any errors encountered
7. Commit the changes with a descriptive message

**Example commit**:
```bash
git add PROJECT_STATUS.md
git commit -m "Update PROJECT_STATUS: Fixed IPv6 issue, completed API tests"
git push origin master
```

---

*This document is a living file - keep it updated as the project evolves.*
