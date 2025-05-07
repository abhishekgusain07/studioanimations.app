# FastAPI Manim Animation Generator

A FastAPI application that generates Manim animations based on natural language queries.

## Features

- REST API endpoint for generating Manim animations
- Simulated LLM code generation (can be replaced with a real LLM API)
- Asynchronous processing of animation generation
- Automatic file cleanup and management
- Static file serving for generated videos
- **Conversation Tracking**: Keep track of animations in the context of ongoing conversations
- **Iterative Refinement**: Build on previous animations within conversations
- **User-based Storage**: Access your animation history organized by conversation

## Prerequisites

- Python 3.9 or higher
- [FFmpeg](https://ffmpeg.org/download.html) (required by Manim)
- [LaTeX](https://www.latex-project.org/get/) (required by Manim for text rendering)
- PostgreSQL 13 or higher

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

5. **Set up a PostgreSQL database**

Create a PostgreSQL database and update the `.env` file with your database credentials:

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=manim_app
```

6. **Run migrations**

```bash
alembic upgrade head
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
  "quality": "low" | "medium" | "high",
  "conversation_id": "optional-uuid-for-conversation",
  "user_id": "uuid-of-the-user",
  "previous_code": "optional-previous-manim-code"
}
```

**Quality Settings**:
- `low`: Faster rendering with lower resolution (default if not specified)
- `medium`: Balanced rendering time and visual quality
- `high`: Higher resolution and visual quality but longer rendering time

- **Response**:

```json
{
  "id": "uuid-of-the-animation",
  "success": true,
  "video_url": "/manim_videos/123e4567-e89b-12d3-a456-426614174000_GeneratedManimScene.mp4",
  "message": "Animation generated successfully",
  "conversation_id": "uuid-of-the-conversation",
  "user_id": "uuid-of-the-user",
  "version": 1,
  "created_at": "2023-10-30T12:34:56Z"
}
```

### List Conversations

Get all conversations for a user.

- **URL**: `/api/conversations?user_id=uuid-of-the-user`
- **Method**: `GET`
- **Response**:

```json
[
  {
    "id": "uuid-of-the-conversation",
    "user_id": "uuid-of-the-user",
    "title": "Conversation Title",
    "created_at": "2023-10-30T12:34:56Z",
    "updated_at": "2023-10-30T12:34:56Z"
  }
]
```

### Get Conversation with Animations

Get a conversation with all its animations.

- **URL**: `/api/conversations/{conversation_id}?user_id=uuid-of-the-user`
- **Method**: `GET`
- **Response**:

```json
{
  "id": "uuid-of-the-conversation",
  "user_id": "uuid-of-the-user",
  "title": "Conversation Title",
  "created_at": "2023-10-30T12:34:56Z",
  "updated_at": "2023-10-30T12:34:56Z",
  "animations": [
    {
      "id": "uuid-of-the-animation",
      "query": "animate a triangle morphing into a square",
      "video_url": "/manim_videos/123e4567-e89b-12d3-a456-426614174000_GeneratedManimScene.mp4",
      "version": 1,
      "quality": "low",
      "success": true,
      "created_at": "2023-10-30T12:34:56Z"
    }
  ]
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

### Create Conversation

Create a new conversation.

- **URL**: `/api/conversations`
- **Method**: `POST`
- **Request Body**:

```json
{
  "user_id": "uuid-of-the-user",
  "title": "Optional conversation title",
  "initial_prompt": "Optional prompt to generate title from"
}
```

- **Response**:

```json
{
  "id": "uuid-of-the-conversation",
  "user_id": "uuid-of-the-user",
  "title": "Conversation Title",
  "created_at": "2023-10-30T12:34:56Z",
  "updated_at": "2023-10-30T12:34:56Z"
}
```

### Get Conversation Sidebar Data

Get optimized conversation data for the sidebar display, including minimal data such as id, title, last active time, and animation count.

- **URL**: `/api/sidebar?user_id=uuid-of-the-user&skip=0&limit=50`
- **Method**: `GET`
- **Query Parameters**:
  - `user_id`: UUID of the user
  - `skip`: Number of conversations to skip (for pagination, default: 0)
  - `limit`: Maximum number of conversations to return (default: 50, max: 100)
- **Response**:

```json
[
  {
    "id": "uuid-of-the-conversation",
    "title": "Conversation Title",
    "last_active": "2023-10-30T12:34:56Z",
    "preview": "Optional preview of the conversation",
    "animation_count": 3
  }
]
```

The results are automatically sorted by most recent activity first.

### Rename Conversation

Rename an existing conversation.

- **URL**: `/api/conversations/{conversation_id}/rename`
- **Method**: `PATCH`
- **Request Body**:

```json
{
  "user_id": "uuid-of-the-user",
  "new_title": "New Conversation Title"
}
```

- **Response**:

```json
{
  "id": "uuid-of-the-conversation",
  "user_id": "uuid-of-the-user",
  "title": "New Conversation Title",
  "created_at": "2023-10-30T12:34:56Z",
  "updated_at": "2023-10-31T09:45:23Z"
}
```

### Delete Conversation

Delete a conversation and all its animations.

- **URL**: `/api/conversations/{conversation_id}?user_id=uuid-of-the-user`
- **Method**: `DELETE`
- **Query Parameters**:
  - `user_id`: UUID of the user who owns the conversation
- **Response**: No content (204)

## Conversation-based Workflow

The application supports a conversation-based workflow for animation generation:

1. **Start a new conversation**:
   - Send a POST request to `/api/conversations` with:
     ```json
     {
       "user_id": "uuid-of-the-user",
       "initial_prompt": "Optional prompt to generate title from"
     }
     ```
   - Or simply send an animation request without a conversation ID - the system will create a new conversation automatically

2. **Generate an animation in an existing conversation**:
   - Send a request to `/api/generate-animation` with a `conversation_id`
   - The system will add the new animation to the existing conversation

3. **Iterate on an animation**:
   - Include `previous_code` in your request to refine an existing animation
   - The system will track the new animation as part of the same conversation with an incremented version number

4. **View your conversation history**:
   - Use `/api/conversations?user_id=your-user-id` to list all your conversations
   - Use `/api/conversations/{conversation_id}?user_id=your-user-id` to view all animations in a conversation

This approach enables iterative refinement of animations while maintaining context.

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

### Run Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
alembic upgrade head
```
