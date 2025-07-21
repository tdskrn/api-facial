# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Flask Development (New Primary Method)
- **Development mode**: `python3 app.py` or `flask run`
- **Production mode**: `gunicorn --config gunicorn.conf.py app:app`
- **VPS Deploy**: `./deploy-kinghost.sh install` (KingHost VPS deployment)
- **Update code**: `./deploy-kinghost.sh update`
- **Check status**: `./deploy-kinghost.sh status`
- **View logs**: `./deploy-kinghost.sh logs`

### Legacy Docker Commands (Still Available)
- **Development mode**: `./deploy.sh development` (Linux/WSL) or `docker-compose up --build -d facial-api` (Windows)
- **Production mode**: `./deploy.sh production` (Linux/WSL) or `docker-compose up --build -d facial-api nginx` (Windows)
- **Stop services**: `./deploy.sh stop` or `docker-compose down`
- **View logs**: `./deploy.sh logs` or `docker-compose logs -f facial-api`
- **Check status**: `./deploy.sh status` or `docker-compose ps`

### Testing
- **Flask API tests**: `python3 test-flask.py`
- **Legacy tests**: `./test_api.sh` (Linux/WSL) or `.\test-windows.ps1` (PowerShell)
- **Manual health check**: `curl http://localhost:8000/health`

### Environment Setup
- **Flask**: Create `.env` file with BASE_URL, SECRET_KEY
- **Legacy**: Copy `env.example` to `.env` before first run
- **VPS**: Use `./deploy-kinghost.sh install` for complete Ubuntu setup

## Architecture Overview

### Core Components (Flask - Primary)
- **Flask Application** (`app.py`): Main Flask app with CORS, logging, and error handling
- **Facial Recognition Module** (`utils/face_matcher.py`): URL-based facial recognition with face_recognition library
- **Configuration**: Environment variables via `.env` file
- **Production Server**: Gunicorn with Nginx reverse proxy

### Legacy Components (FastAPI - Still Available)
- **FastAPI Application** (`app/main.py`): Main application with middleware, logging, and global exception handling
- **Facial Recognition Service** (`app/services/facial_service.py`): Core business logic for face detection and comparison
- **API Endpoints** (`app/api/facial.py`): REST API routes with validation and error handling
- **Configuration** (`app/config.py`): Settings management using Pydantic Settings
- **Data Models** (`app/models/employee.py`): Pydantic models for API responses

### Storage Structure
- **Flask**: URL-based image storage (fetches from external URLs)
- **Legacy**: Local files in `app/storage/employee_photos/` - Stores JPG photos and JSON encodings
- **Logs**: `logs/` directory with rotating log files (api.log, errors.log)

### Docker Architecture
- **Main service**: `facial-api` (FastAPI app)
- **Reverse proxy**: `nginx` (production only)
- **Optional services**: `redis`, `postgres`, `prometheus`, `grafana` (not used by default)

## Key Technical Details

### Facial Recognition Pipeline
1. Image upload and validation (max 10MB, JPG/PNG/WEBP)
2. Face detection using face_recognition library
3. Encoding generation and storage as JSON
4. Comparison using euclidean distance with configurable tolerance (default 0.6)

### API Flow

#### Flask API (Primary)
- **Validation**: POST `/api/validate` with JSON `{"employee_id": "123", "image_base64": "data:image/jpeg;base64,..."}`
- **Health check**: GET `/health`
- **Root info**: GET `/`

#### Legacy FastAPI (Still Available)
- **Registration**: POST `/api/v1/register-employee/{id}` with image file
- **Verification**: POST `/api/v1/verify-face/{id}` with image file  
- **Status check**: GET `/api/v1/employee/{id}/status`
- **Updates**: PUT `/api/v1/update-employee/{id}` (replaces existing)
- **Deletion**: DELETE `/api/v1/employee/{id}`
- **Service info**: GET `/api/v1/service-info` (shows current mode and capabilities)
- **Health check**: GET `/api/v1/health` (includes service mode status)

### Configuration
- Environment variables loaded from `.env` file
- Key settings: FACE_TOLERANCE, MAX_FILE_SIZE, DEBUG mode
- Storage paths, database URL, and security keys configurable

### Logging
- Structured logging with loguru
- File rotation (daily for general logs, weekly for errors)
- Request/response logging middleware with performance metrics
- Separate error logging with full stack traces

### Platform Support
- **Primary**: Linux VPS deployment (KingHost optimized)
- **Flask**: Direct Python deployment with systemd service
- **Legacy**: Docker deployment (Linux/Windows)
- **Scripts**: 
  - Flask: `deploy-kinghost.sh` (VPS deployment), `test-flask.py` (testing)
  - Legacy: `deploy.sh`, `test_api.sh` (Linux), `test-windows.ps1` (PowerShell)

## Development Notes

### Service Patterns
- Graceful fallback to mock service if face_recognition dependencies unavailable
- Async/await patterns for file operations
- Comprehensive error handling with HTTP status codes
- Middleware for CORS, security headers, and request logging

### File Handling
- Validation of file types, sizes, and content
- Atomic operations for photo updates (delete old, save new)
- Automatic directory creation for storage paths

### Dependencies and Installation

#### Essential (always required)
- `pip install -r requirements.txt` - Core dependencies (FastAPI, uvicorn, loguru, aiofiles)

#### Optional (for full facial recognition)
- `pip install -r requirements-dev.txt` - Includes face_recognition, opencv-python-headless, numpy
- The API gracefully degrades to "limited mode" without these dependencies

#### Development Dependencies
- **Flask version**: `requirements-flask.txt` - Flask + face_recognition + gunicorn
- **Legacy version**: `requirements-dev.txt` - FastAPI + pytest + face_recognition 
- Requirements files: `requirements.txt` (legacy minimal), `requirements-dev.txt` (legacy full), `requirements-flask.txt` (new Flask)

### Database Options
- SQLite (default) - No setup required, database stored in `./data/facial_api.db`
- PostgreSQL (optional) - For production scaling, configured in docker-compose.yml

### Service Modes
- **Real mode**: All CV dependencies available, full facial recognition
- **Limited mode**: Missing CV deps, basic image storage with simulated recognition  
- **Mock mode**: Fallback service for testing (facial_service_mock.py)