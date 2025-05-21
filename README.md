# Backend API for Document Management and Q&A

## Overview

This backend service provides a RESTful API for managing users, documents, and interacting with a Question & Answering system. It's built using FastAPI and supports features like user authentication, document upload and retrieval, document ingestion processing, and a placeholder for Q&A functionality.

## Features

*   **User Authentication:** Secure token-based (JWT) authentication.
*   **User Management:**
    *   User registration.
    *   Retrieval of current user details.
    *   Admin-only: Listing users, updating user roles, and deleting users.
*   **Document Management:**
    *   Secure document uploads.
    *   Listing and retrieving documents.
    *   Deleting documents.
    *   Downloading uploaded documents.
*   **Document Ingestion:**
    *   Trigger asynchronous ingestion process for uploaded documents (simulated).
    *   API to check the status of ingestion tasks.
*   **Q&A System:**
    *   Placeholder endpoint for asking questions related to documents.
*   **CORS Enabled:** Allows cross-origin requests (currently configured for all origins).

## Technology Stack

*   **Framework:** FastAPI
*   **Web Server:** Uvicorn
*   **Data Validation & Settings:** Pydantic, Pydantic-Settings
*   **Database ORM:** SQLAlchemy
*   **Database:** PostgreSQL
*   **Authentication:** Python-JOSE (JWT), Passlib (bcrypt for password hashing)
*   **File Handling:** Python-multipart
*   **Containerization:** Docker

## Prerequisites

*   Python 3.12
*   Docker
*   Docker Compose

## Environment Variables

The application uses the following environment variables for configuration. These can be set directly in your environment or by creating a `.env` file in the `backend/` directory.

*   `DATABASE_URL`: The connection string for the PostgreSQL database.
    *   Example: `postgresql://user:password@localhost:5432/mydatabase`
    *   Default for Docker Compose: `postgresql://user:password@db:5432/mydatabase`
*   `SECRET_KEY`: A secret key used for signing JWT tokens. **This must be changed for production environments.**
    *   Example: `your-very-secure-and-random-secret-key`
*   `ALGORITHM`: The algorithm used for JWT signing.
    *   Default: `HS256`
*   `ACCESS_TOKEN_EXPIRE_MINUTES`: The duration (in minutes) for which access tokens are valid.
    *   Default: `30`
*   `DOCUMENTS_UPLOAD_PATH`: The directory where uploaded documents will be stored relative to the application's working directory.
    *   Default: `uploaded_documents`

## Setup and Running Locally (Docker Compose)

The recommended way to run the backend locally for development is using Docker Compose, which also sets up the PostgreSQL database.

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Navigate to Project Root:**
    Ensure you are in the main project directory where `docker-compose.yml` is located.

3.  **Environment File (Optional but Recommended):**
    While `docker-compose.yml` sets some defaults, you can create a `.env` file inside the `backend/` directory to override or manage sensitive values like `SECRET_KEY` or a different `DATABASE_URL` if not using the Docker Compose defaults for the database service.
    Example `backend/.env` file:
    ```env
    DATABASE_URL=postgresql://user:password@db:5432/mydatabase
    SECRET_KEY=a_very_strong_and_unique_secret_key_here
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60
    DOCUMENTS_UPLOAD_PATH=uploaded_documents
    ```

4.  **Build and Run with Docker Compose:**
    From the project root directory (containing `docker-compose.yml`):
    ```bash
    docker compose up --build
    ```
    This command will:
    *   Build the Docker image for the backend service (if not already built or if changes are detected).
    *   Start the backend service and the PostgreSQL database service.
    *   The backend API will be accessible at `http://localhost:8000`.

5.  **Stopping the Services:**
    Press `Ctrl+C` in the terminal where Docker Compose is running, then you can run:
    ```bash
    docker compose down
    ```
    To remove volumes (like database data and uploaded files), use:
    ```bash
    docker compose down -v
    ```

## API Documentation

Once the application is running, interactive API documentation (Swagger UI) is available at:
`http://localhost:8000/docs`

Alternative API documentation (ReDoc) is available at:
`http://localhost:8000/redoc`

## Database

*   The application uses SQLAlchemy as its ORM.
*   Database tables are automatically created based on the models defined in `src/models.py` when the application starts, using `Base.metadata.create_all(bind=database.engine)`.
*   **Note:** This setup does not include a formal database migration system (like Alembic). For schema changes in a production environment or more complex development, integrating a migration tool would be necessary.

## File Uploads

*   Uploaded documents are stored in the directory specified by the `DOCUMENTS_UPLOAD_PATH` environment variable (defaults to `uploaded_documents` inside the application container).
*   When using Docker Compose, the `uploaded_documents` named volume is mounted to this path, ensuring persistence of uploaded files across container restarts.

## Testing

(Information on how to run tests should be added here. A `tests/test_backend.py` file exists, suggesting tests can be run, likely with `pytest`.)

To run tests (assuming `pytest` is installed and configured):
```bash
# Navigate to the backend directory
cd backend
# Ensure your environment (e.g., virtualenv) has test dependencies if any
# pytest
```
(Further details on test setup and specific commands might be needed).