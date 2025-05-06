# FastAPI Manim Animation Generator

A FastAPI application that generates Manim animations based on natural language queries.

## Features

- REST API endpoint for generating Manim animations
- Simulated LLM code generation (can be replaced with a real LLM API)
- Asynchronous processing of animation generation
- Automatic file cleanup and management
- Static file serving for generated videos

## Prerequisites

- Python 3.9 or higher
- [FFmpeg](https://ffmpeg.org/download.html) (required by Manim)
- [LaTeX](https://www.latex-project.org/get/) (required by Manim for text rendering)

## Installation

1. **Clone the repository**

2. **Create and activate a virtual environment**

```bash
cd fastapi_manim_app
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
uv pip install -e ".[dev]"
```

4. **Copy the example environment file**

```bash
cp .env.example .env
```

## Running the Application

Start the application with hot reload:

```bash
uvicorn app.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).

## API Documentation

API documentation is available at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### Generate Animation

Generate a Manim animation based on a natural language query.

- **URL**: `/api/generate-animation`
- **Method**: `POST`
- **Request Body**:

```json
{
  "query": "animate a triangle morphing into a square",
  "quality": "low" | "medium" | "high"
}
```

**Quality Settings**:
- `low`: Faster rendering with lower resolution (default if not specified)
- `medium`: Balanced rendering time and visual quality
- `high`: Higher resolution and visual quality but longer rendering time

- **Response**:

```json
{
  "success": true,
  "video_url": "/manim_videos/123e4567-e89b-12d3-a456-426614174000_GeneratedManimScene.mp4",
  "message": "Animation generated successfully"
}
```

### Health Check

Check the health of the application.

- **URL**: `/api/health`
- **Method**: `GET`
- **Response**:

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Development

### Running Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=app tests/
```

### Format Code

```bash
black .
isort .
```

### Run Linting

```bash
ruff .
```

### Run Type Checking

```bash
mypy .
```
